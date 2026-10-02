"""Sandbox isolation tests (sandbox.py docstring)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.sandbox import run_tool, SandboxedTool, is_error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "boidsnet", "env", "mechenv.py")
CALL = [{"args": [[{"units": 1.0}], []], "kwargs": {}}]


def make_lib(tools, acl):
    lib = tempfile.mkdtemp()
    os.makedirs(os.path.join(lib, "tools"))
    open(os.path.join(lib, "tools", "__init__.py"), "w").close()
    for name, src in tools.items():
        with open(os.path.join(lib, "tools", name + ".py"), "w") as f:
            f.write(src)
    with open(os.path.join(lib, "acl.json"), "w") as f:
        json.dump(acl, f)
    with open(os.path.join(lib, "index.json"), "w") as f:
        json.dump({"secret": "hidden verdicts"}, f)
    return lib


IDENT = "def execute(table, lookup, **params):\n    return table\n"


CANARIES = {"AZURE_AI_KEY": "CANARY_azure_ai_key", "AZURE_OPENAI_ENDPOINT": "CANARY_endpoint",
            "SOME_TOKEN": "CANARY_token", "DB_SECRET": "CANARY_secret", "OPENAI_API_KEY": "CANARY_openai"}


class CredentialIsolationTests(unittest.TestCase):
    """msg #91 (Qi-side review): no parent env var of ANY name may reach tool code."""

    def setUp(self):
        self._old = {k: os.environ.get(k) for k in CANARIES}
        os.environ.update(CANARIES)

    def tearDown(self):
        for k, v in self._old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_os_environ_has_no_canary(self):
        src = ("import os\n"
               "def execute(table, lookup, **params):\n"
               "    return [{'k': k, 'v': v} for k, v in os.environ.items()]\n")
        lib = make_lib({"a00_r01": src}, {"a00_r01": []})
        y = run_tool(lib, "a00_r01", CALL)[0]
        self.assertFalse(is_error(y), y)
        dump = json.dumps(y)
        for v in CANARIES.values():
            self.assertNotIn(v, dump)
        self.assertLessEqual({r["k"] for r in y}, {"PYTHONHASHSEED"})

    def test_proc_environ_blocked_or_clean(self):
        for target in ("/proc/self/environ", "/proc/%d/environ" % os.getpid()):
            src = ("import os\n"
                   "def execute(table, lookup, **params):\n"
                   f"    return [{{'raw': open({target!r}, 'rb').read().decode('latin-1')}}]\n")
            lib = make_lib({"a00_r01": src}, {"a00_r01": []})
            y = run_tool(lib, "a00_r01", CALL)[0]
            dump = json.dumps(y)
            for v in CANARIES.values():
                self.assertNotIn(v, dump, target)
            self.assertTrue(is_error(y), (target, y))

    def test_child_env_is_allowlist(self):
        from boidsnet.runner.sandbox import child_env
        self.assertLessEqual(set(child_env()), {"PATH", "LANG", "LC_ALL", "PYTHONHASHSEED"})


TAMPER = "import __main__, os, sys\n"


def _tamper_tool(body):
    return TAMPER + "def execute(table, lookup, **params):\n" + "".join("    " + l + "\n" for l in body)


class HookTamperTests(unittest.TestCase):
    """msg #102 (i_alx4y9xgu1): the audit hook's policy is mutable from tool
    code, so the boundary must be the OS.  Each test FIRST rewrites the hook's
    state, then attempts the leak."""

    @classmethod
    def setUpClass(cls):
        from boidsnet.runner.sandbox import isolation_level
        if not isolation_level().startswith("os-"):
            raise unittest.SkipTest("no OS isolation on this host; real-model runs are refused here")

    def test_parent_initial_environ_not_reachable_after_tamper(self):
        # the canary must be in the PARENT'S INITIAL environ, so run the runner in a fresh process
        import subprocess
        lib = make_lib({"a00_r01": _tamper_tool([
            "out = []",
            "for pid in [os.getppid()] + [int(p) for p in os.listdir('/proc') if p.isdigit()]:",
            "    p = '/proc/%d/environ' % pid",
            "    __main__.OK_FILES.add(p)",
            "    try: out.append(open(p, 'rb').read().decode('latin-1'))",
            "    except Exception as e: out.append(type(e).__name__)",
            "return [{'x': '|'.join(out)}]"])}, {"a00_r01": []})
        code = ("import json, sys; sys.path.insert(0, %r)\n"
                "from boidsnet.runner.sandbox import run_tool\n"
                "print(json.dumps(run_tool(%r, 'a00_r01', [{'args': [[], []], 'kwargs': {}}])))") % (ROOT, lib)
        env = {"PATH": "/usr/bin:/bin", "AZURE_AI_KEY": "CANARY_PARENT_INITIAL_ENV"}
        r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=60)
        self.assertNotIn("CANARY_PARENT_INITIAL_ENV", r.stdout + r.stderr)
        self.assertTrue(r.stdout.strip(), r.stderr)

    def test_reference_impl_index_and_acl_after_tamper(self):
        vendor = os.path.join(ROOT, "boidsnet", "env", "mechenv.py")
        lib = make_lib({"a00_r01": IDENT, "a01_r02": _tamper_tool([
            "__main__.STDLIB = ('/',); __main__.SITE = ()",
            "__main__.OK_FILES.update([%r, os.path.join(__main__.LIB, 'index.json')])" % vendor,
            "__main__.acl['a01_r02'] = ['a00_r01']",
            "res = []",
            "for f in (%r, 'index.json', os.path.join(__main__.LIB, 'index.json')):" % vendor,
            "    try: res.append(open(f).read()[:40])",
            "    except Exception as e: res.append('ERR ' + type(e).__name__)",
            "try:",
            "    import importlib; importlib.import_module('tools.a00_r01'); res.append('IMPORTED')",
            "except Exception as e: res.append('ERR ' + type(e).__name__)",
            "return [{'r': res}]"])}, {"a00_r01": [], "a01_r02": []})
        y = run_tool(lib, "a01_r02", CALL)[0]
        self.assertFalse(is_error(y), y)
        self.assertTrue(all(x.startswith("ERR") for x in y[0]["r"]), y)       # nothing readable or importable

    def test_network_after_tamper(self):
        lib = make_lib({"a00_r01": _tamper_tool([
            "__main__.BLOCK_PREFIX = ('nothing.',)",
            "import socket",
            "try:",
            "    socket.create_connection(('1.1.1.1', 443), timeout=2); r = 'CONNECTED'",
            "except Exception as e: r = 'ERR ' + type(e).__name__",
            "return [{'r': r}]"])}, {"a00_r01": []})
        y = run_tool(lib, "a00_r01", CALL)[0]
        self.assertTrue(is_error(y) or y[0]["r"].startswith("ERR"), y)

    def test_planted_host_canaries_invisible(self):
        """msg #105.3b: allowlist root, so files planted anywhere on the host
        (/etc, /opt, /var, the repo) do not exist for the tool."""
        planted, made = [], []
        if not os.path.isdir("/usr/local/etc"):
            try:
                os.makedirs("/usr/local/etc")
                made.append("/usr/local/etc")
            except OSError:
                pass
        for d in ("/etc", "/opt", "/var/lib", "/usr/local/etc", "/usr/share", ROOT):   # msg #107: /usr too
            p = os.path.join(d, "boids_canary_%d.txt" % os.getpid())
            try:
                with open(p, "w") as f:
                    f.write("CANARY_HOST_FILE")
                planted.append(p)
            except OSError:
                pass
        if not planted:
            self.skipTest("cannot plant canaries on this host")
        try:
            body = ["__main__.STDLIB = ('/',); __main__.SITE = ()", "res = []",
                    "for p in %r:" % planted,
                    "    __main__.OK_FILES.add(p)",
                    "    try: res.append(open(p).read())",
                    "    except Exception as e: res.append('ERR ' + type(e).__name__)",
                    "return [{'r': res, 'root': sorted(os.listdir('/')), 'usr': sorted(os.listdir('/usr'))}]"]
            lib = make_lib({"a00_r01": _tamper_tool(body)}, {"a00_r01": []})
            y = run_tool(lib, "a00_r01", CALL)[0]
            self.assertNotIn("CANARY_HOST_FILE", json.dumps(y))
            self.assertLessEqual(set(y[0]["root"]), {"bin", "sbin", "lib", "lib32", "lib64", "libx32",
                                                     "usr", "etc", "dev", "proc", "sandbox", ".old"})
            self.assertFalse({"local", "share"} & set(y[0]["usr"]), y[0]["usr"])
        finally:
            for p in planted:
                os.remove(p)
            for d in made:
                os.rmdir(d)

    def test_mount_escape_fails(self):
        """msg #105.3a: tamper the hook, unshare a new user+mount namespace with
        ctypes, try to mount/umount; the host is still unreachable."""
        flag = "/etc/boids_escape_canary_%d" % os.getpid()
        try:
            with open(flag, "w") as f:
                f.write("CANARY_ESCAPE")
        except OSError:
            self.skipTest("cannot plant canary")
        try:
            body = ["__main__.BLOCK_PREFIX = ('nothing.',); __main__.STDLIB = ('/',); __main__.SITE = ()",
                    "import ctypes, ctypes.util",
                    "libc = ctypes.CDLL(ctypes.util.find_library('c') or 'libc.so.6', use_errno=True)",
                    "res = {'unshare': libc.unshare(0x10000000 | 0x00020000)}",
                    "res['umount_root'] = libc.umount2(b'/', 2)",
                    "res['mount_tmpfs'] = libc.mount(b'none', b'/usr', b'tmpfs', 0, None)",
                    "try: res['read'] = open(%r).read()" % flag,
                    "except Exception as e: res['read'] = 'ERR ' + type(e).__name__",
                    "res['root'] = sorted(os.listdir('/'))",
                    "return [res]"]
            lib = make_lib({"a00_r01": _tamper_tool(body)}, {"a00_r01": []})
            y = run_tool(lib, "a00_r01", CALL)[0]
            self.assertNotIn("CANARY_ESCAPE", json.dumps(y))
        finally:
            os.remove(flag)

    def test_loopback_to_parent_unreachable(self):
        """msg #105.3d: the tool's netns has no route to a listener in the runner's netns."""
        import socket
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        try:
            body = ["__main__.BLOCK_PREFIX = ('nothing.',)", "import socket",
                    "try:",
                    "    socket.create_connection(('127.0.0.1', %d), timeout=2); r = 'CONNECTED'" % port,
                    "except Exception as e: r = 'ERR ' + type(e).__name__",
                    "return [{'r': r}]"]
            lib = make_lib({"a00_r01": _tamper_tool(body)}, {"a00_r01": []})
            y = run_tool(lib, "a00_r01", CALL)[0]
            self.assertTrue(is_error(y) or y[0]["r"].startswith("ERR"), y)
        finally:
            srv.close()

    def test_non_runner_tool_ids_refused(self):
        from boidsnet.runner.sandbox import _ns_cmd
        with self.assertRaises(ValueError):
            _ns_cmd("root", "/x", ["a00_r01", "--"], ["true"])
        with self.assertRaises(ValueError):
            _ns_cmd("root", "/x", ["../../etc/passwd"], ["true"])

    def test_runs_as_nobody_without_caps(self):
        from boidsnet.runner.sandbox import isolation_level
        if isolation_level() != "os-root":
            self.skipTest("uid drop only in os-root mode")
        lib = make_lib({"a00_r01": _tamper_tool([
            "__main__.STDLIB = ('/',)",
            "st = dict(l.split(':', 1) for l in open('/proc/self/status') if ':' in l)",
            "return [{'u': os.getuid(), 'g': os.getgid(), 'cap': st['CapEff'].strip(), 'nnp': st['NoNewPrivs'].strip()}]"])},
            {"a00_r01": []})
        y = run_tool(lib, "a00_r01", CALL)[0]
        self.assertEqual((y[0]["u"], y[0]["g"]), (65534, 65534))
        self.assertEqual(int(y[0]["cap"], 16), 0)                         # msg #105.3c
        self.assertEqual(y[0]["nnp"], "1")


class VenvTests(unittest.TestCase):
    """Found by the clean-env receipt for msg #130: inside a venv, sysconfig's platstdlib is the
    venv dir, and root_spec() refused to build the sandbox.  Run a tool from a fresh venv."""

    def test_sandbox_works_from_a_venv(self):
        import subprocess
        venv = tempfile.mkdtemp()
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", venv], check=True)
        lib = make_lib({"a00_r01": IDENT}, {"a00_r01": []})
        code = ("import json, sys; sys.path.insert(0, %r)\n"
                "from boidsnet.runner.sandbox import run_tool, isolation_level\n"
                "print(json.dumps([isolation_level(), run_tool(%r, 'a00_r01', %r)]))") % (ROOT, lib, CALL)
        r = subprocess.run([os.path.join(venv, "bin", "python"), "-c", code], capture_output=True, text=True,
                           timeout=120, env={"PATH": "/usr/bin:/bin", "HOME": venv})
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        level, out = json.loads(r.stdout)
        self.assertEqual(out, [CALL[0]["args"][0]], (level, out))


class SandboxTests(unittest.TestCase):
    def err(self, lib, tool):
        y = run_tool(lib, tool, CALL)[0]
        self.assertTrue(is_error(y), y)
        return y["__error__"]

    def test_plain_tool_runs(self):
        lib = make_lib({"a00_r01": IDENT}, {"a00_r01": []})
        self.assertEqual(run_tool(lib, "a00_r01", CALL), [[{"units": 1.0}]])

    def test_reference_impl_cannot_be_loaded(self):
        env = MechEnv(VENDOR)
        task = env.dev_tasks()[25]
        src = ("import importlib.util, sys\n"
               f"spec = importlib.util.spec_from_file_location('m', {VENDOR!r})\n"
               "m = importlib.util.module_from_spec(spec); sys.modules['m'] = m\n"
               "spec.loader.exec_module(m)\n"
               f"T = [t for t in m.tasks(0, 'dev') if t.id == {task['id']!r}][0]\n"
               "def execute(table, lookup, **params):\n    return T.reference(table, lookup)\n")
        lib = make_lib({"a00_r01": src}, {"a00_r01": []})
        verdict = env.harness(SandboxedTool(lib, "a00_r01"), task)
        self.assertFalse(verdict["passed"])
        self.assertIn("PermissionError", self.err(lib, "a00_r01"))

    def test_hidden_index_unreadable(self):
        src = ("import os\ndef execute(table, lookup, **params):\n"
               "    return [{'x': open(os.path.join('..', 'index.json')).read()}]\n")
        lib = make_lib({"a00_r01": src}, {"a00_r01": []})
        self.assertIn("PermissionError", self.err(lib, "a00_r01"))

    def test_import_outside_acl_blocked(self):
        # IM-style: a01_r02 may only import its own tools.
        lib = make_lib({"a00_r01": IDENT,
                        "a01_r02": "from tools import a00_r01\n" + IDENT},
                       {"a00_r01": [], "a01_r02": []})
        self.assertIn("may not import", self.err(lib, "a01_r02"))

    def test_dynamic_import_outside_acl_blocked(self):
        lib = make_lib({"a00_r01": IDENT,
                        "a01_r02": "import importlib\n"
                                   "def execute(table, lookup, **params):\n"
                                   "    return importlib.import_module('tools.a00_r01').execute(table, lookup)\n"},
                       {"a00_r01": [], "a01_r02": []})
        # blocked by the import ACL / file layer (hook-only), or simply absent from
        # the OS-isolated view, which contains only ACL-reachable tools
        e = self.err(lib, "a01_r02")
        self.assertTrue("PermissionError" in e or "ModuleNotFoundError" in e, e)

    def test_reading_unlisted_tool_source_blocked(self):
        lib = make_lib({"a00_r01": IDENT,
                        "a01_r02": "import os\ndef execute(table, lookup, **params):\n"
                                   "    return [{'s': open(os.path.join('tools', 'a00_r01.py')).read()}]\n"},
                       {"a00_r01": [], "a01_r02": []})
        self.assertIn("PermissionError", self.err(lib, "a01_r02"))

    def test_allowed_and_transitive_imports_work(self):
        lib = make_lib({"a00_r01": IDENT,
                        "a01_r02": "from tools import a00_r01\n"
                                   "def execute(table, lookup, **params):\n"
                                   "    return a00_r01.execute(table, lookup)\n",
                        "a02_r03": "from tools import a01_r02\n"
                                   "def execute(table, lookup, **params):\n"
                                   "    return a01_r02.execute(table, lookup)\n"},
                       {"a00_r01": [], "a01_r02": ["a00_r01"], "a02_r03": ["a00_r01", "a01_r02"]})
        self.assertEqual(run_tool(lib, "a02_r03", CALL), [[{"units": 1.0}]])

    def test_network_subprocess_and_writes_blocked(self):
        for body in ("import socket\n    socket.create_connection(('example.com', 80))",
                     "import subprocess\n    subprocess.run(['true'])",
                     "import os\n    os.system('true')",
                     "open('x.txt', 'w').write('hi')"):
            src = "def execute(table, lookup, **params):\n    " + body + "\n    return table\n"
            lib = make_lib({"a00_r01": src}, {"a00_r01": []})
            self.assertIn("PermissionError", self.err(lib, "a00_r01"), body)

    def test_stdlib_still_usable(self):
        src = ("import math, statistics, re, json, datetime, collections, itertools\n"
               "def execute(table, lookup, **params):\n"
               "    return [{'m': statistics.mean([1.0, 3.0]), 'd': datetime.date(2025, 1, 2).isoformat()}]\n")
        lib = make_lib({"a00_r01": src}, {"a00_r01": []})
        self.assertEqual(run_tool(lib, "a00_r01", CALL), [[{"m": 2.0, "d": "2025-01-02"}]])


if __name__ == "__main__":
    unittest.main()
