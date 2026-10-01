"""Execute a library tool on a batch of calls in a subprocess.

Tools are plain modules in <library>/tools/<tool_id>.py exposing execute(...).
They may import other tools with `from tools import <tool_id>`.  Each call is
{"args": [...], "kwargs": {...}} and crosses the process boundary as JSON.
Any exception or timeout becomes the sentinel {"__error__": "..."}, so a crash
is a distinct behaviour, not a missing value.

Isolation (pre-register; tested in tests/test_sandbox.py):
- the child runs with `python -I` and cwd = the library, with an ALLOWLISTED env
  (PATH/LANG/PYTHONHASHSEED only; nothing else is inherited, so no credential of any
  name reaches tool code; os.environ is also cleared before the tool is imported);
- an audit hook, installed before the tool is imported, enforces
  * imports of `tools.<id>` only if <id> is in the importing tool's ACL, i.e.
    the catalogue its author could see when it was built (society-wide in
    E/L0/L1/R0/G0m, self-only in IM);
  * file reads only inside the Python standard library and of the .py files
    of tools reachable through those ACLs.  No reading the env, the runner,
    index.json (hidden verdicts), other runs, or site-packages;
  * no file writes, sockets, subprocesses, exec/spawn/fork or signals.
A blocked action raises PermissionError inside the tool, which therefore
records a crash like any other error.

v0.13 (msg #102): the hook is only a second layer.  See isolation_level():
OS namespaces + uid 65534 are the actual boundary, and real-model runs refuse
to start without them.
"""
import json
import os
import re
import subprocess
import sys

_CHILD = r'''
import json, os, sys, sysconfig
sys.dont_write_bytecode = True
LIB = os.path.realpath(sys.argv[1])
TOP = sys.argv[2]
payload = json.load(sys.stdin)
calls, acl = payload["calls"], payload["acl"]

# Tools reachable from TOP through the authors' ACLs.
reach, todo = {TOP}, [TOP]
while todo:
    for d in acl.get(todo.pop(), []):
        if d not in reach:
            reach.add(d); todo.append(d)
TOOLS = os.path.join(LIB, "tools")
OK_FILES = {os.path.join(TOOLS, "__init__.py")} | {os.path.join(TOOLS, t + ".py") for t in reach}
paths = sysconfig.get_paths()
STDLIB = tuple(os.path.realpath(paths[k]) + os.sep for k in ("stdlib", "platstdlib"))
SITE = tuple(os.path.realpath(paths[k]) for k in ("purelib", "platlib"))
BLOCK_PREFIX = ("socket.", "subprocess.", "os.exec", "os.spawn", "os.posix_spawn",
                "os.fork", "os.kill", "os.system", "os.remove", "os.rename", "os.rmdir",
                "os.mkdir", "os.chmod", "os.truncate", "shutil.", "ctypes.", "pty.")

def _importer():
    f = sys._getframe(2)
    while f is not None:
        n = f.f_globals.get("__name__", "")
        if n.startswith("tools.") and n != "tools":
            return n[6:]
        f = f.f_back
    return None

def _file_ok(p):
    try:
        rp = os.path.realpath(p if isinstance(p, str) else os.fsdecode(p))
    except Exception:
        return False
    if rp in OK_FILES or rp == TOOLS:
        return True
    if rp.startswith(SITE):
        return False
    return rp.startswith(STDLIB) or rp + os.sep in STDLIB

def _hook(event, args):
    if event == "import":
        mod = args[0] or ""
        if mod.startswith("tools."):
            target = mod[6:].split(".")[0]
            src = _importer()
            if src is None:
                if target != TOP:
                    raise PermissionError("import of tool %s not allowed" % target)
            elif target not in acl.get(src, []):
                raise PermissionError("tool %s may not import %s" % (src, target))
    elif event == "open":
        path, mode = args[0], args[1]
        if isinstance(path, int):
            return
        if mode and any(c in str(mode) for c in "wax+"):
            raise PermissionError("file writes are not allowed")
        if not _file_ok(path):
            raise PermissionError("file access outside the sandbox: %s" % path)
    elif event in ("os.listdir", "os.scandir"):
        p = args[0] if args and args[0] is not None else "."
        if not isinstance(p, int) and not _file_ok(p):
            raise PermissionError("directory listing outside the sandbox")
    elif event.startswith(BLOCK_PREFIX):
        raise PermissionError("%s is not allowed" % event)

sys.path.insert(0, LIB)
import importlib
for _k in list(os.environ):
    if _k != "PYTHONHASHSEED":
        del os.environ[_k]
sys.addaudithook(_hook)
try:
    fn = getattr(importlib.import_module("tools." + TOP), "execute")
except BaseException as e:
    json.dump([{"__error__": "import: " + type(e).__name__ + ": " + str(e)[:200]}] * len(calls), sys.stdout)
    sys.exit(0)
out = []
for c in calls:
    try:
        y = fn(*c.get("args", []), **c.get("kwargs", {}))
        json.dumps(y)
        out.append(y)
    except BaseException as e:
        out.append({"__error__": type(e).__name__ + ": " + str(e)[:200]})
json.dump(out, sys.stdout)
'''


def is_error(y):
    return isinstance(y, dict) and "__error__" in y


def load_acl(library_dir):
    """tool_id -> ids its author could import (written by Library.add)."""
    p = os.path.join(library_dir, "acl.json")
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


# Explicit ALLOWLIST for the tool child (Qi-side review, msg #91): nothing is
# inherited from the parent environment except the hash seed (determinism).
# The old denylist (strip *_API_KEY) let AZURE_AI_KEY / *_TOKEN / *_SECRET etc.
# reach untrusted model-generated code.
def child_env():
    env = {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8"}
    hs = os.environ.get("PYTHONHASHSEED")
    if hs is not None and hs.isdigit():
        env["PYTHONHASHSEED"] = hs
    return env


# --------------------------------------------------------------------------
# OS-level isolation (msgs #102, #105, i_alx4y9xgu1).  The audit hook above is
# NOT a security boundary: its policy lives in the child's own memory and a
# tool can rewrite it (`import __main__; __main__.OK_FILES.add(...)`).  The
# boundary is the OS.  Each tool child runs in fresh mount, PID and network
# namespaces and is pivot_root'ed into an ALLOWLIST root (a fresh tmpfs) that
# contains only:
#   * read-only binds of the interpreter's tree (/usr on merged-usr hosts, plus
#     sys.prefix / base_prefix / the executable's dir if outside it),
#     /etc/ld.so.cache, and symlinks /bin /sbin /lib /lib64 as on the host;
#   * /dev/null, /dev/zero, /dev/urandom;
#   * a fresh /proc of its own PID namespace (the runner, which may hold the
#     model key in its initial environ, does not exist there);
#   * /sandbox/lib/tools with ONLY the tools reachable through the ACLs.
# No other host path exists for it: no /etc, /home, /root, /tmp, /opt, /run,
# /var, repo, run tree.  No network.  In os-root mode it then drops to
# uid/gid 65534 with no capabilities and no_new_privs.  The hook stays as a
# second layer.  Real-model runs REFUSE to start unless the level is os-*.
# --------------------------------------------------------------------------
NOBODY = "65534"
SANDBOX_LIB = "/sandbox/lib"
TOOL_ID = re.compile(r"^(a\d{2}_r\d{2}|solver_t\d{3}_k\d+)$")   # runner-assigned ids only

_NS_SCRIPT = r"""
set -eu
LIB="$1"; MODE="$2"; shift 2
R=/mnt
mount -t tmpfs -o size=64m,mode=755 none "$R"
mkdir -p "$R$SANDBOX_LIB/tools" "$R/proc" "$R/dev" "$R/.old"
: > "$R$SANDBOX_LIB/tools/__init__.py"
while [ "$1" != "--" ]; do cp "$LIB/tools/$1.py" "$R$SANDBOX_LIB/tools/"; shift; done; shift
while [ "$1" != "--" ]; do                      # read-only directory binds
  mkdir -p "$R$1"; mount --rbind "$1" "$R$1"; mount -o remount,bind,ro "$R$1"; shift
done; shift
while [ "$1" != "--" ]; do                      # read-only file binds
  mkdir -p "$(dirname "$R$1")"; : > "$R$1"; mount --bind "$1" "$R$1"; mount -o remount,bind,ro "$R$1"; shift
done; shift
while [ "$1" != "--" ]; do ln -s "$2" "$R$1"; shift 2; done; shift   # symlinks NAME TARGET
for d in null zero urandom; do : > "$R/dev/$d"; mount --bind "/dev/$d" "$R/dev/$d"; done
chmod -R a+rX "$R$SANDBOX_LIB"
cd "$R"
pivot_root . .old
cd /
mount -t proc proc /proc
umount -l /.old
rmdir /.old
mount -o remount,ro /
cd "$SANDBOX_LIB"
if [ "$MODE" = root ]; then
  exec setpriv --reuid=65534 --regid=65534 --clear-groups --no-new-privs --inh-caps=-all --bounding-set=-all "$@"
else
  exec setpriv --no-new-privs --inh-caps=-all --bounding-set=-all "$@"
fi
"""


def _reachable(acl, top):
    reach, todo = {top}, [top]
    while todo:
        for d in acl.get(todo.pop(), []):
            if d not in reach:
                reach.add(d)
                todo.append(d)
    return sorted(reach)


def root_spec():
    """(dirs, files, links) that make up the allowlist root."""
    links, dirs = [], ["/usr"]
    for name in ("/bin", "/sbin", "/lib", "/lib32", "/lib64", "/libx32"):
        if os.path.islink(name):
            links.append((name, os.readlink(name)))
        elif os.path.isdir(name):
            dirs.append(name)
    for p in (sys.prefix, sys.base_prefix, os.path.dirname(os.path.dirname(os.path.realpath(sys.executable))),
              os.path.dirname(os.path.abspath(sys.executable))):
        p = os.path.realpath(p)
        if p != "/" and not any(p == d or p.startswith(d + os.sep) for d in dirs):
            dirs.append(p)
    files = [f for f in ("/etc/ld.so.cache",) if os.path.exists(f)]
    return dirs, files, links


def _ns_prefix(mode):
    base = ["unshare", "--mount", "--pid", "--fork", "--kill-child", "--mount-proc", "--net"]
    if mode == "userns":
        base.insert(1, "--user")
        base.insert(2, "--map-root-user")
    return base


def _ns_cmd(mode, library_dir, tool_ids, argv):
    bad = [t for t in tool_ids if not TOOL_ID.match(t)]
    if bad:
        raise ValueError(f"refusing non-runner tool ids {bad}")
    dirs, files, links = root_spec()
    return (_ns_prefix(mode) + ["sh", "-c", _NS_SCRIPT, "sh", library_dir, mode] + list(tool_ids) + ["--"]
            + dirs + ["--"] + files + ["--"] + [x for l in links for x in l] + ["--"] + argv)


_LEVEL = None
PROBE_REPORT = {}


def isolation_level():
    """'os-root' (allowlist root + uid 65534), 'os-userns' (allowlist root in an
    unprivileged user namespace), or 'hook-only'.  Probed once by actually
    running the isolation; PROBE_REPORT holds what the probe saw, for the
    manifest."""
    global _LEVEL
    if _LEVEL is not None:
        return _LEVEL
    if os.environ.get("BOIDS_SANDBOX") == "hook-only":
        _LEVEL = "hook-only"
        PROBE_REPORT.update(level=_LEVEL, forced=True)
        return _LEVEL
    probe = ("import json, os, sys\n"
             "st = dict(l.split(':', 1) for l in open('/proc/self/status') if ':' in l)\n"
             "print(json.dumps({'parent_visible': os.path.exists('/proc/%d' % int(sys.argv[1])),\n"
             "  'host_paths_visible': [p for p in sys.argv[2:] if os.path.exists(p)],\n"
             "  'uid': os.getuid(), 'cap_eff': st['CapEff'].strip(), 'root_entries': sorted(os.listdir('/'))}))\n")
    import tempfile
    import shutil
    lib = tempfile.mkdtemp()
    canaries = ["/etc/hostname", "/etc/passwd", "/home", "/root", "/tmp", "/opt", "/var", "/run", lib]
    try:
        os.makedirs(os.path.join(lib, "tools"))
        for mode in (("root",) if os.geteuid() == 0 else ()) + ("userns",):
            cmd = _ns_cmd(mode, lib, [], [sys.executable, "-I", "-c", probe, str(os.getpid())] + canaries)
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=_ns_env())
                rep = json.loads(r.stdout)
            except Exception:  # noqa: BLE001 - any failure means this mode is unavailable
                continue
            ok = (not rep["parent_visible"] and not rep["host_paths_visible"]
                  and int(rep["cap_eff"], 16) == 0 and (mode != "root" or str(rep["uid"]) == NOBODY))
            if ok:
                _LEVEL = "os-" + mode
                PROBE_REPORT.update(level=_LEVEL, probe=rep, root_spec=root_spec())
                return _LEVEL
    finally:
        shutil.rmtree(lib, ignore_errors=True)
    _LEVEL = "hook-only"
    PROBE_REPORT.update(level=_LEVEL)
    return _LEVEL


def _ns_env():
    env = child_env()
    env["SANDBOX_LIB"] = SANDBOX_LIB
    env["PATH"] = "/usr/sbin:/usr/bin:/sbin:/bin"
    return env


def run_tool(library_dir, tool_id, calls, timeout_s=5.0, acl=None):
    """Return one output per call (errors as sentinels)."""
    if not calls:
        return []
    library_dir = os.path.abspath(library_dir)
    if acl is None:
        acl = load_acl(library_dir)
    level = isolation_level()
    if level == "hook-only":
        cmd, cwd, env = [sys.executable, "-I", "-c", _CHILD, library_dir, tool_id], library_dir, child_env()
    else:
        files = [t for t in _reachable(acl, tool_id)
                 if os.path.exists(os.path.join(library_dir, "tools", t + ".py"))]
        cmd = _ns_cmd(level[3:], library_dir, files, [sys.executable, "-I", "-c", _CHILD, SANDBOX_LIB, tool_id])
        cwd, env = "/", _ns_env()
    try:
        proc = subprocess.run(
            cmd, input=json.dumps({"calls": calls, "acl": acl}), capture_output=True, text=True,
            timeout=timeout_s + (0 if level == "hook-only" else 5), env=env, cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return [{"__error__": "timeout"}] * len(calls)
    try:
        out = json.loads(proc.stdout)
        if len(out) != len(calls):
            raise ValueError("length mismatch")
        return out
    except Exception:
        msg = (proc.stderr or "no output").strip().splitlines()[-1:] or ["?"]
        return [{"__error__": "child: " + msg[0][:200]}] * len(calls)


class SandboxedTool:
    """Callable handed to the env's harness: tool(*args, **kwargs).

    Results are cached per call, and .prefetch(calls) runs a whole batch in one
    subprocess so the harness's one-call-at-a-time loop does not spawn a
    process per probe.
    """

    def __init__(self, library_dir, tool_id, timeout_s=5.0):
        self.library_dir, self.tool_id, self.timeout_s = library_dir, tool_id, timeout_s
        self._cache = {}

    @staticmethod
    def _key(call):
        return json.dumps(call, sort_keys=True)

    def prefetch(self, calls):
        todo = [c for c in calls if self._key(c) not in self._cache]
        if todo:
            for c, y in zip(todo, run_tool(self.library_dir, self.tool_id, todo, self.timeout_s)):
                self._cache[self._key(c)] = y
        return [self._cache[self._key(c)] for c in calls]

    def __call__(self, *args, **kwargs):
        y = self.prefetch([{"args": list(args), "kwargs": kwargs}])[0]
        if is_error(y):
            raise RuntimeError(y["__error__"])
        return y
