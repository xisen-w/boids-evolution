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
# OS-level isolation (msg #102, i_alx4y9xgu1).  The audit hook above is NOT a
# security boundary: its policy lives in the child's own memory, and a tool
# can rewrite it (`import __main__; __main__.OK_FILES.add(...)`).  So the
# child is additionally run, when the host allows it, inside fresh mount,
# PID and network namespaces, as uid/gid 65534 with no capabilities and
# no_new_privs, and it sees:
#   * /proc of its own PID namespace only (the runner, which may hold the
#     model key in its initial environ, is not visible);
#   * no network;
#   * a tmpfs VIEW containing ONLY the tools reachable through the ACLs
#     (no index.json, no other agents' unlisted tools);
#   * empty tmpfs over /tmp, /var/tmp, /home, /root, /srv, the runner tree
#     (mechenv reference implementations) and the run-output tree.
# The hook stays as a second layer.  Real-model runs REFUSE to start unless
# isolation_level() is an OS level (run.py).
# --------------------------------------------------------------------------
VIEW = "/mnt"
NOBODY = "65534"
RUNNER_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root

_NS_SCRIPT = r'''
set -eu
LIB="$1"; MODE="$2"; shift 2
mount -t tmpfs -o size=64m,mode=755 none /mnt
mkdir -p /mnt/lib/tools
: > /mnt/lib/tools/__init__.py
while [ "$1" != "--" ]; do cp "$LIB/tools/$1.py" /mnt/lib/tools/; shift; done
shift
NHIDE="$1"; shift
chmod -R a+rX /mnt/lib
i=0
while [ "$i" -lt "$NHIDE" ]; do mount -t tmpfs -o size=4k,mode=000 none "$1"; shift; i=$((i+1)); done
cd /mnt/lib
if [ "$MODE" = root ]; then
  exec setpriv --reuid=65534 --regid=65534 --clear-groups --no-new-privs --inh-caps=-all --bounding-set=-all "$@"
else
  exec setpriv --no-new-privs --inh-caps=-all --bounding-set=-all "$@"
fi
'''


def _reachable(acl, top):
    reach, todo = {top}, [top]
    while todo:
        for d in acl.get(todo.pop(), []):
            if d not in reach:
                reach.add(d)
                todo.append(d)
    return sorted(reach)


def _needed_paths():
    import sysconfig
    paths = sysconfig.get_paths()
    return [os.path.realpath(p) for p in (sys.executable, sys.prefix, paths["stdlib"], paths["platstdlib"])] + \
        [os.path.abspath(sys.executable)]


def _hide_list(library_dir):
    """Directories to cover with an empty tmpfs; never an ancestor of the
    interpreter or stdlib, never nested inside another hidden dir."""
    d2 = os.path.dirname(os.path.dirname(library_dir))
    cands = ["/tmp", "/var/tmp", "/home", "/root", "/srv", RUNNER_ROOT, d2, os.path.dirname(d2)]
    need = _needed_paths()
    out = []
    for c in cands:
        c = os.path.realpath(c)
        if c in ("/", VIEW) or not os.path.isdir(c):
            continue
        if any(n == c or n.startswith(c + os.sep) for n in need):
            continue
        out.append(c)
    out = sorted(set(out), key=len)
    return [c for i, c in enumerate(out) if not any(c.startswith(o + os.sep) for o in out[:i])]


def _ns_prefix(mode):
    base = ["unshare", "--mount", "--pid", "--fork", "--kill-child", "--mount-proc", "--net"]
    if mode == "userns":
        base.insert(1, "--user")
        base.insert(2, "--map-root-user")
    return base


_LEVEL = None


def isolation_level():
    """'os-root' (namespaces + uid 65534), 'os-userns' (unprivileged
    namespaces), or 'hook-only'.  Probed once by actually running the
    isolation and checking that the parent is invisible."""
    global _LEVEL
    if _LEVEL is not None:
        return _LEVEL
    forced = os.environ.get("BOIDS_SANDBOX")
    if forced == "hook-only":
        _LEVEL = "hook-only"
        return _LEVEL
    probe = ("import os,sys\n"
             "ok = not os.path.exists('/proc/%d' % int(sys.argv[1]))\n"
             "print('ISOLATED' if ok and os.getppid() != int(sys.argv[1]) else 'VISIBLE', os.getuid())\n")
    lib = None
    try:
        import tempfile
        lib = tempfile.mkdtemp()
        os.makedirs(os.path.join(lib, "tools"))
        for mode in (("root",) if os.geteuid() == 0 else ()) + ("userns",):
            cmd = _ns_prefix(mode) + ["sh", "-c", _NS_SCRIPT, "sh", lib, mode, "--", "0",
                                      sys.executable, "-I", "-c", probe, str(os.getpid())]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=10, env=child_env())
            except (OSError, subprocess.TimeoutExpired):
                continue
            words = r.stdout.split()
            if words[:1] == ["ISOLATED"] and (mode != "root" or words[1:2] == [NOBODY]):
                _LEVEL = "os-" + mode
                return _LEVEL
    finally:
        if lib:
            import shutil
            shutil.rmtree(lib, ignore_errors=True)
    _LEVEL = "hook-only"
    return _LEVEL


def run_tool(library_dir, tool_id, calls, timeout_s=5.0, acl=None):
    """Return one output per call (errors as sentinels)."""
    if not calls:
        return []
    library_dir = os.path.abspath(library_dir)
    if acl is None:
        acl = load_acl(library_dir)
    env = child_env()
    level = isolation_level()
    if level == "hook-only":
        cmd, cwd = [sys.executable, "-I", "-c", _CHILD, library_dir, tool_id], library_dir
    else:
        mode = level[3:]
        hide = _hide_list(library_dir)
        files = [t for t in _reachable(acl, tool_id)
                 if os.path.exists(os.path.join(library_dir, "tools", t + ".py"))]
        cmd = (_ns_prefix(mode) + ["sh", "-c", _NS_SCRIPT, "sh", library_dir, mode] + files
               + ["--", str(len(hide))] + hide + [sys.executable, "-I", "-c", _CHILD, VIEW + "/lib", tool_id])
        cwd = "/"
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
