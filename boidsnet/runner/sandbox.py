"""Execute a library tool on a batch of calls in a subprocess.

Tools are plain modules in <library>/tools/<tool_id>.py exposing execute(...).
They may import other tools with `from tools import <tool_id>`.  Each call is
{"args": [...], "kwargs": {...}} and crosses the process boundary as JSON.
Tool exceptions and per-probe timeouts become {"__error__": "..."}. Driver
launch/transport failures abort scoring with SandboxInfrastructureError.

Isolation (pre-register; tested in tests/test_sandbox.py):
- the driver runs with `python -s -S`, an explicit safe search path and an ALLOWLISTED env
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
# -I ignores PYTHONHASHSEED. Use -s -S with a clean environment and remove the
# current directory BEFORE importing anything other than the built-in sys.
import sys
sys.path = [p for p in sys.path if p and p != sys.argv[1]]
import json, os, select, signal, time, types
LIB, TOP = sys.argv[1:3]
payload = json.load(sys.stdin)
outputs = []
for call in payload["calls"]:
    rd, wr = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(rd)
        # stdout/stderr are diagnostics, never the structured result channel.
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, 1); os.dup2(null, 2); os.close(null)
        try:
            worker_module = types.ModuleType("__main__")
            sys.modules["__main__"] = worker_module
            worker_module.RESULT_FD = wr
            worker_module.PAYLOAD = {"calls": [call], "acl": payload["acl"]}
            exec(payload["worker"], worker_module.__dict__)
        finally:
            os._exit(0)
    os.close(wr)
    data = bytearray()
    deadline = time.monotonic() + payload["timeout_s"]
    timed_out = oversized = False
    try:
        while True:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([rd], [], [], max(0, left))[0]:
                timed_out = True
                break
            chunk = os.read(rd, 65536)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > 8 * 1024 * 1024:
                oversized = True
                break
    finally:
        # Even a tool that closes its result fd and hangs must not block waitpid.
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        _, status = os.waitpid(pid, 0)
        os.close(rd)
    if not data.startswith(b"READY\n"):
        raise RuntimeError("worker failed before readiness")
    if timed_out or oversized:
        outputs.append({"__error__": "timeout" if timed_out else "output size limit"})
    else:
        # The trusted worker announces readiness BEFORE importing tool code.
        # No handshake means initialization/transport failed. After readiness,
        # an abnormal exit or missing result is a generated-tool failure, not
        # evidence that the sandbox could not start.
        body = data[len(b"READY\n"):]
        if not body:
            code = os.waitstatus_to_exitcode(status)
            message = ("PermissionError: forbidden cross-tool call" if code == 77
                       else "tool terminated without a result (exit %s)" % code)
            outputs.append({"__error__": message})
            continue
        try:
            result = json.loads(body)
            if not isinstance(result, list) or len(result) != 1:
                raise ValueError("invalid worker envelope")
        except (ValueError, TypeError):
            outputs.append({"__error__": "tool corrupted its result channel"})
            continue
        outputs.append(result[0])
json.dump({"protocol": 1, "outputs": outputs}, sys.stdout)
'''

_WORKER = r'''
import json, os, sys, sysconfig, random
sys.dont_write_bytecode = True
LIB = os.path.realpath(sys.argv[1])
TOP = sys.argv[2]
payload = PAYLOAD
calls, acl = payload["calls"], payload["acl"]

# Tools reachable from TOP through the authors' ACLs.
reach, todo = {TOP}, [TOP]
while todo:
    for d in acl.get(todo.pop(), []):
        if d not in reach:
            reach.add(d); todo.append(d)
TOOLS = os.path.join(LIB, "tools")
OK_FILES = {os.path.join(TOOLS, "__init__.py")} | {os.path.join(TOOLS, t + ".py") for t in reach}
_tool_paths = {os.path.join(TOOLS, t + ".py"): t for t in reach}
_module_owners = {}
paths = sysconfig.get_paths()
STDLIB = tuple(os.path.realpath(paths[k]) + os.sep for k in ("stdlib", "platstdlib"))
SITE = tuple(os.path.realpath(paths[k]) for k in ("purelib", "platlib"))
BLOCK_PREFIX = ("socket.", "subprocess.", "os.exec", "os.spawn", "os.posix_spawn",
                "os.fork", "os.kill", "os.system", "os.remove", "os.rename", "os.rmdir",
                "os.mkdir", "os.chmod", "os.truncate", "shutil.", "ctypes.", "pty.")

def _frame_tool(frame, _owners=_module_owners, _paths=_tool_paths):
    # Module-level execution is profiled before generated code runs. Register
    # the namespace by its loader path once; __name__ is tool-writable and is
    # not a trustworthy identity. Hold namespaces to prevent object-id reuse.
    key = id(frame.f_globals)
    if key in _owners:
        return _owners[key][0]
    owner = _paths.get(frame.f_code.co_filename)
    if owner is not None:
        _owners[key] = (owner, frame.f_globals)
    return owner

def _importer():
    f = sys._getframe(2)
    while f is not None:
        owner = _frame_tool(f)
        if owner is not None:
            return owner
        f = f.f_back
    return None

def _file_ok(p):
    try:
        rp = os.path.realpath(p if isinstance(p, str) else os.fsdecode(p))
    except Exception:
        return False
    if rp in OK_FILES:
        target, src = _tool_paths.get(rp), _importer()
        return target is None or target == src or target in (_policy.get(src, ()) if src else (TOP,))
    if rp == TOOLS:
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
        path, mode, flags = args
        write_flags = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND
        if (mode and any(c in str(mode) for c in "wax+")) or flags & write_flags:
            raise PermissionError("file writes are not allowed")
        if isinstance(path, int):
            return
        if not _file_ok(path):
            raise PermissionError("file access outside the sandbox: %s" % path)
    elif event in ("os.listdir", "os.scandir"):
        p = args[0] if args and args[0] is not None else "."
        if not isinstance(p, int) and not _file_ok(p):
            raise PermissionError("directory listing outside the sandbox")
    elif event.startswith(BLOCK_PREFIX):
        raise PermissionError("%s is not allowed" % event)
    elif event in ("sys.setprofile", "sys.settrace"):
        raise PermissionError("execution policy hooks cannot be replaced")

sys.path.insert(0, LIB)
import importlib, importlib.util, builtins
# The audit import event is skipped for sys.modules hits. Check every import
# entry point as well, including `from tools import cached_module`.
_original_import = builtins.__import__
_original_import_module = importlib.import_module
_policy = {k: frozenset(v) for k, v in acl.items()}

def _permit(target, src):
    if target != src and target not in (_policy.get(src, ()) if src else (TOP,)):
        raise PermissionError("tool %s may not import/call %s" % (src, target))

def _checked_import(name, globals=None, locals=None, fromlist=(), level=0):
    src = _importer()
    absolute = name
    if level:
        package = (globals or {}).get("__package__", "")
        absolute = importlib.util.resolve_name("." * level + name, package)
    if absolute.startswith("tools."):
        _permit(absolute.split(".")[1], src)
    elif absolute == "tools":
        for target in fromlist or ():
            _permit(target, src)
    return _original_import(name, globals, locals, fromlist, level)

def _checked_import_module(name, package=None):
    absolute = importlib.util.resolve_name(name, package) if name.startswith(".") else name
    if absolute.startswith("tools."):
        _permit(absolute.split(".")[1], _importer())
    return _original_import_module(name, package)

def _check_call(frame, event, arg, _exit=os._exit, _acl=_policy):
    try:
        if event == "call":
            target = _frame_tool(frame)
            if target is not None:
                caller = frame.f_back
                while caller is not None:
                    src = _frame_tool(caller)
                    if src is not None:
                        if target != src and target not in _acl.get(src, ()):
                            _exit(77)
                        break
                    caller = caller.f_back
    except BaseException:
        # Never raise out of a profiler: CPython disables it on exceptions.
        # Denials AND unexpected policy errors terminate the current probe.
        _exit(77)

builtins.__import__ = _checked_import
importlib.import_module = _checked_import_module
sys.setprofile(_check_call)
for _k in list(os.environ):
    if _k != "PYTHONHASHSEED":
        del os.environ[_k]
sys.addaudithook(_hook)
# Initialization above is trusted. Everything after this marker may execute
# generated code, including module-level imports and JSON serialization hooks.
os.write(RESULT_FD, b"READY\n")
out = []
for c in calls:
    try:
        # A fresh generated-module state for each probe, not stateful batching.
        for name in list(sys.modules):
            if name == "tools" or name.startswith("tools."):
                del sys.modules[name]
        random.seed(0)
        fn = getattr(importlib.import_module("tools." + TOP), "execute")
        y = fn(*c.get("args", []), **c.get("kwargs", {}))
        json.dumps(y)
        out.append(y)
    except BaseException as e:
        out.append({"__error__": type(e).__name__ + ": " + str(e)[:200]})
encoded = json.dumps(out).encode()
while encoded:
    encoded = encoded[os.write(RESULT_FD, encoded):]
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
# inherited from the parent environment; the hash seed is always fixed at 0.
# The old denylist (strip *_API_KEY) let AZURE_AI_KEY / *_TOKEN / *_SECRET etc.
# reach untrusted model-generated code.
def child_env():
    return {"PATH": os.defpath, "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "PYTHONHASHSEED": "0"}


# --------------------------------------------------------------------------
# OS-level isolation (msgs #102, #105, i_alx4y9xgu1).  The audit hook above is
# NOT a security boundary: its policy lives in the child's own memory and a
# tool can rewrite it (`import __main__; __main__.OK_FILES.add(...)`).  The
# boundary is the OS.  Each tool child runs in fresh mount, PID and network
# namespaces and is pivot_root'ed into an ALLOWLIST root (a fresh tmpfs) that
# contains only:
#   * a read-only copy of ONLY: the real interpreter, the few binaries the
#     script runs after pivot_root, their ELF dependency closure (ldd, incl.
#     every lib-dynload extension) and /etc/ld.so.cache, plus the host's
#     /bin /sbin /lib /lib64 symlinks (root_spec(), built once by _sysroot());
#   * a read-only bind of the stdlib directory;
#   * /dev/null, /dev/urandom;
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
LIB="$1"; MODE="$2"; SYSROOT="$3"; STDLIB="$4"; shift 4
R=/mnt
mount --bind "$SYSROOT" "$R"                    # prebuilt minimal root (see _sysroot), read-only below
mount -t tmpfs -o size=64m,mode=755 none "$R/sandbox"
mkdir -p "$R$SANDBOX_LIB/tools"
: > "$R$SANDBOX_LIB/tools/__init__.py"
while [ "$1" != "--" ]; do cp "$LIB/tools/$1.py" "$R$SANDBOX_LIB/tools/"; shift; done; shift
chmod -R a+rX,a-w "$R/sandbox"
mount -o remount,ro "$R/sandbox"                # child tmpfs is NOT covered by remounting /
mount --rbind "$STDLIB" "$R$STDLIB"; mount -o remount,bind,ro "$R$STDLIB"
for d in null urandom; do mount --bind "/dev/$d" "$R/dev/$d"; done
cd "$R"
pivot_root . .old
cd /
mount -t proc proc /proc
umount -l /.old
mount -o remount,bind,ro /
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


_SPEC = None


def root_spec():
    """(dirs, files, links) of the allowlist root (msg #107: do not bind /usr
    wholesale).  dirs = the stdlib only; files = the real interpreter, the
    binaries the namespace script runs after pivot_root, and the ELF
    dependency closure (ldd) of all of them plus every lib-dynload extension;
    links = the host's top-level /bin /sbin /lib /lib64 symlinks so loader
    paths resolve.  Nothing else of /usr (no /usr/local, /usr/share,
    dist-packages) exists in the sandbox."""
    global _SPEC
    if _SPEC is not None:
        return _SPEC
    import glob
    import shutil
    import sysconfig
    links = [(n, os.readlink(n)) for n in ("/bin", "/sbin", "/lib", "/lib32", "/lib64", "/libx32")
             if os.path.islink(n)]
    # Always the BASE interpreter's stdlib: inside a venv, sysconfig's platstdlib points at the
    # venv (site-packages, not stdlib).  Tools are stdlib-only, so the sandbox never needs the venv.
    base = {"base": sys.base_prefix, "platbase": sys.base_exec_prefix,
            "installed_base": sys.base_prefix, "installed_platbase": sys.base_exec_prefix}
    stdlib = sorted({os.path.realpath(sysconfig.get_path(k, vars=base)) for k in ("stdlib", "platstdlib")})
    bins = [os.path.realpath(sys.executable)]
    for b in ("mount", "umount", "rmdir", "setpriv"):
        w = shutil.which(b, path="/usr/sbin:/usr/bin:/sbin:/bin")
        if not w:
            raise RuntimeError(f"{b} not found")
        bins.append(w)
    objs = bins + [f for d in stdlib for f in glob.glob(os.path.join(d, "lib-dynload", "*.so"))]
    libs = set()
    for o in objs:
        out = subprocess.run(["ldd", o], capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            m = re.search(r"(/\S+)", line.split("=>")[-1])
            if m:
                libs.add(m.group(1))
    files = sorted(set(bins) | libs | ({"/etc/ld.so.cache"} if os.path.exists("/etc/ld.so.cache") else set()))
    _SPEC = (stdlib, files, links)
    return _SPEC


_SYSROOT = None


def _sysroot():
    """Build, once per process, a minimal root directory: the files of
    root_spec() COPIED to their loader paths, the host's top-level symlinks,
    and empty mount points (stdlib, /dev nodes, /proc, /sandbox, /.old).
    Each tool call then binds this one directory instead of dozens of files
    (one bind per file cost ~0.2 s per call).  Returns (path, stdlib)."""
    global _SYSROOT
    if _SYSROOT is not None:
        return _SYSROOT
    import atexit
    import shutil
    import tempfile
    stdlibs, files, links = root_spec()
    if len(stdlibs) != 1:
        raise RuntimeError(f"expected one stdlib dir, got {stdlibs}")
    root = tempfile.mkdtemp(prefix="boids_sysroot_")
    atexit.register(shutil.rmtree, root, True)
    link_map = dict(links)

    def inside(path):              # resolve a top-level symlink the way the sandbox will
        parts = path.lstrip("/").split("/", 1)
        top = "/" + parts[0]
        if top in link_map:
            tgt = link_map[top]
            base = tgt if tgt.startswith("/") else "/" + tgt
            path = base + ("/" + parts[1] if len(parts) > 1 else "")
        return os.path.join(root, path.lstrip("/"))

    for name, tgt in links:
        os.makedirs(inside(name), exist_ok=True)
        os.symlink(tgt, os.path.join(root, name.lstrip("/")))
    for f in files:
        dst = inside(f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.realpath(f), dst)
    os.makedirs(inside(stdlibs[0]), exist_ok=True)
    for d in ("dev", "proc", "sandbox", ".old"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    for n in ("null", "urandom"):
        open(os.path.join(root, "dev", n), "w").close()
    for dp, dn, fn in os.walk(root):
        os.chmod(dp, 0o755)
    os.chmod(root, 0o755)
    _SYSROOT = (root, stdlibs[0])
    return _SYSROOT


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
    sysroot, stdlib = _sysroot()
    return (_ns_prefix(mode) + ["sh", "-c", _NS_SCRIPT, "sh", library_dir, mode, sysroot, stdlib]
            + list(tool_ids) + ["--"] + argv)


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
    if os.environ.get("BOIDS_SANDBOX") == "docker":
        from .docker_sandbox import probe
        try:
            receipt = probe()
        except Exception as exc:
            _LEVEL = "hook-only"
            PROBE_REPORT.update(level=_LEVEL, docker_probe_error=type(exc).__name__)
        else:
            _LEVEL = "os-docker"
            PROBE_REPORT.update(level=_LEVEL, probe=receipt)
        return _LEVEL
    probe = ("import json, os, sys\n"
             "st = dict(l.split(':', 1) for l in open('/proc/self/status') if ':' in l)\n"
             "print(json.dumps({'parent_visible': os.path.exists('/proc/%d' % int(sys.argv[1])),\n"
             "  'host_paths_visible': [p for p in sys.argv[2:] if os.path.exists(p)],\n"
             "  'uid': os.getuid(), 'cap_eff': st['CapEff'].strip(), 'root_entries': sorted(os.listdir('/'))}))\n")
    import tempfile
    import shutil
    lib = tempfile.mkdtemp()
    canaries = ["/etc/hostname", "/etc/passwd", "/home", "/root", "/tmp", "/opt", "/var", "/run", lib,
                "/usr/local", "/usr/share", "/usr/lib/python3/dist-packages"]
    try:
        os.makedirs(os.path.join(lib, "tools"))
        for mode in (("root",) if os.geteuid() == 0 else ()) + ("userns",):
            try:
                cmd = _ns_cmd(mode, lib, [], [os.path.realpath(sys.executable), "-I", "-c", probe, str(os.getpid())]
                              + canaries)
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=_ns_env())
                rep = json.loads(r.stdout)
            except Exception:  # noqa: BLE001 - any failure (incl. no ldd) means this mode is unavailable
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


class SandboxInfrastructureError(RuntimeError):
    """A launch/transport failure: the experiment must stop, not score zero."""
    infrastructure_failure = True


def run_tool(library_dir, tool_id, calls, timeout_s=5.0, acl=None):
    """One clean fork per probe; timeout_s is the per-probe execution limit."""
    try:
        return _run_tool(library_dir, tool_id, calls, timeout_s, acl)
    except SandboxInfrastructureError:
        raise
    except Exception as exc:
        # Includes ACL loading, namespace command construction and JSON input
        # serialization: none of these is a generated tool's task verdict.
        raise SandboxInfrastructureError("sandbox preparation failed") from exc


def _run_tool(library_dir, tool_id, calls, timeout_s, acl):
    if not calls:
        return []
    library_dir = os.path.abspath(library_dir)
    if acl is None:
        acl = load_acl(library_dir)
    level = isolation_level()
    if level == "os-docker":
        from .docker_sandbox import run
        proc = run(library_dir, tool_id, calls, acl, timeout_s)
    elif level == "hook-only":
        cmd, cwd, env = [sys.executable, "-s", "-S", "-c", _CHILD, library_dir, tool_id], library_dir, child_env()
    else:
        files = [t for t in _reachable(acl, tool_id)
                 if os.path.exists(os.path.join(library_dir, "tools", t + ".py"))]
        cmd = _ns_cmd(level[3:], library_dir, files,
                      [os.path.realpath(sys.executable), "-s", "-S", "-c", _CHILD, SANDBOX_LIB, tool_id])
        cwd, env = "/", _ns_env()
    if level != "os-docker":
        try:
            proc = subprocess.run(
                cmd, input=json.dumps({"calls": calls, "acl": acl, "worker": _WORKER, "timeout_s": timeout_s}),
                capture_output=True, text=True,
                timeout=timeout_s * len(calls) + 10, env=env, cwd=cwd,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            raise SandboxInfrastructureError("sandbox driver launch/timeout failure") from exc
    if proc.returncode != 0:
        raise SandboxInfrastructureError(f"sandbox driver exited with status {proc.returncode}")
    try:
        envelope = json.loads(proc.stdout)
        out = envelope["outputs"]
        if envelope.get("protocol") != 1 or not isinstance(out, list) or len(out) != len(calls):
            raise ValueError("length mismatch")
        return out
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        raise SandboxInfrastructureError("sandbox driver returned an invalid envelope") from exc


class SandboxedTool:
    """Callable handed to the env's harness: tool(*args, **kwargs).

    Results are cached per call. .prefetch(calls) uses one isolated driver and
    a clean fork of that driver per probe, before any generated code is loaded.
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
