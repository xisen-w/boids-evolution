"""Opt-in, same-Mac Docker tool boundary. No key, repo or Docker socket mounts.

The trusted runner stays on the host. Each container receives only a readonly
copy of reachable tool sources and a JSON probe payload on stdin. The image is
stdlib-only, pinned by image ID, and never pulled implicitly during a run.
"""
import atexit
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

DEFAULT_IMAGE = 'boids-tool-sandbox:v1'
_IMAGE = None
_CONFIG = None


def client():
    global _CONFIG
    binary = shutil.which('docker') or '/usr/local/bin/docker'
    endpoint = os.environ.get('BOIDS_DOCKER_SOCKET') or (
        str(Path.home() / '.docker/run/docker.sock') if sys.platform == 'darwin' else '/var/run/docker.sock')
    if not os.path.isabs(endpoint) or not Path(endpoint).is_socket():
        raise RuntimeError('local Docker socket unavailable')
    if _CONFIG is None:
        _CONFIG = tempfile.mkdtemp(prefix='boids_docker_client_')
        atexit.register(shutil.rmtree, _CONFIG, True)
    return [binary, '--config', _CONFIG, '--host', 'unix://' + endpoint]


def cli(args, **kwargs):
    from .sandbox import child_env
    return subprocess.run(client() + args, env=child_env(), capture_output=True,
                          text=True, **kwargs)


def image_id():
    global _IMAGE
    if _IMAGE is None:
        ref = os.environ.get('BOIDS_DOCKER_IMAGE', DEFAULT_IMAGE)
        result = cli(['image', 'inspect', ref], timeout=15)
        if result.returncode:
            raise RuntimeError('sandbox image unavailable; build it before review')
        info = json.loads(result.stdout)[0]
        if (info.get('Config', {}).get('Labels') or {}).get('org.boids.sandbox') != 'stdlib-only-v1':
            raise RuntimeError('not a Boids stdlib-only sandbox image')
        _IMAGE = info['Id']
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', _IMAGE):
            raise RuntimeError('invalid sandbox image ID')
    return _IMAGE


def options(name):
    return ['run', '--rm', '--interactive', '--pull=never', '--name', name,
            '--network=none', '--read-only', '--cap-drop=ALL',
            '--security-opt=no-new-privileges', '--user=65534:65534',
            '--pids-limit=64', '--memory=256m', '--memory-swap=256m', '--cpus=1',
            '--log-driver=none', '--env=PYTHONHASHSEED=0']


def invoke(args, payload=None, timeout=30):
    name = 'boids-tool-' + uuid.uuid4().hex
    try:
        return cli(options(name) + args, input=payload, timeout=timeout)
    finally:
        # Killing a docker CLI alone does NOT kill its container. Target only
        # this generated name; never stop any unrelated container or daemon.
        result = cli(['rm', '--force', name], timeout=15)
        if result.returncode and 'No such container' not in result.stderr:
            raise RuntimeError('sandbox container cleanup unverified; stop')


def probe():
    source = """
import json, os, socket, sys
st = dict(line.split(':', 1) for line in open('/proc/self/status') if ':' in line)
try:
    open('/sandbox/boids_write_probe', 'w').close()
    readonly = False
except OSError:
    readonly = True
print(json.dumps({'uid': os.getuid(), 'gid': os.getgid(),
 'cap_eff': st['CapEff'].strip(), 'no_new_privs': st['NoNewPrivs'].strip(),
 'readonly': readonly, 'interfaces': [{'name': n,
   'up': bool(int(open('/sys/class/net/' + n + '/flags').read(), 16) & 1)}
   for _, n in socket.if_nameindex()],
 'ipv4_routes': open('/proc/net/route').read().splitlines()[1:],
 'python_version': sys.version.split()[0], 'image_files': sorted(os.listdir('/')),
 'forbidden_paths': [p for p in ('/Users', '/home', '/root', '/var/run/docker.sock',
  '/usr/local', '/usr/share', '/repo') if os.path.exists(p)]}))
"""
    result = invoke([image_id(), '-c', source])
    if result.returncode:
        raise RuntimeError('Docker isolation probe failed')
    row = json.loads(result.stdout)
    if not (row['uid'] == row['gid'] == 65534 and int(row['cap_eff'], 16) == 0
            and row['no_new_privs'] == '1' and row['readonly']
            and not row['forbidden_paths'] and not row['ipv4_routes']
            and all(n['name'] == 'lo' or not n['up'] for n in row['interfaces'])):
        raise RuntimeError('Docker isolation probe violated required policy')
    return dict(row, image_id=image_id(), backend='docker-stdlib-only-v1')


def run(library_dir, tool_id, calls, acl, timeout_s, *, worker_source=None):
    from .sandbox import _CHILD, _WORKER, _reachable, TOOL_ID
    ids = _reachable(acl, tool_id)
    if any(not TOOL_ID.fullmatch(tid) for tid in ids):
        raise ValueError('invalid tool ID')
    # This directory is the ONLY host bind mount, and contains source copies
    # only. Never mount the library itself (index/ACL/verdicts) or the repo.
    with tempfile.TemporaryDirectory(prefix='boids_tool_sources_') as tmp:
        stage = Path(tmp)
        stage.chmod(0o755)
        (stage / 'tools').mkdir(mode=0o755)
        (stage / 'tools/__init__.py').touch(mode=0o444)
        for tid in ids:
            original = Path(library_dir) / 'tools' / (tid + '.py')
            if original.is_symlink():
                raise ValueError('tool sources cannot be symlinks')
            if original.exists():
                dest = stage / 'tools' / (tid + '.py')
                shutil.copyfile(original, dest)
                dest.chmod(0o444)
        payload = json.dumps({'calls': calls, 'acl': acl, 'worker': worker_source or _WORKER, 'timeout_s': timeout_s})
        return invoke(['--mount', 'type=bind,source=' + str(stage) + ',target=/sandbox/lib,readonly',
                       image_id(), '-c', _CHILD, '/sandbox/lib', tool_id],
                      payload, timeout_s * len(calls) + 20)
