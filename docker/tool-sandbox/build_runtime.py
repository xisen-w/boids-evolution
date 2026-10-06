"""Build a credential-free stdlib-only root; never copy the repository."""
import glob
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig

root = Path('/runtime')
stdlib = Path(sysconfig.get_path('stdlib'))
python = Path(sys.executable).resolve()
shutil.copytree(stdlib, root / str(stdlib).lstrip('/'),
                ignore=shutil.ignore_patterns('__pycache__', 'site-packages', 'dist-packages'))
objects = [str(python)] + glob.glob(str(stdlib / 'lib-dynload' / '*.so'))
files = {str(python)}
for obj in objects:
    output = subprocess.check_output(['ldd', obj], text=True)
    for line in output.splitlines():
        match = re.search(r'(/\S+)', line.split('=>')[-1])
        if match:
            files.add(match.group(1))
for filename in sorted(files):
    dest = root / filename.lstrip('/')
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(os.path.realpath(filename), dest)
link = root / 'usr/bin/python3'
if link != root / str(python).lstrip('/'):
    link.symlink_to(python.name)
for dirname in ('dev', 'proc', 'etc', 'sandbox/lib/tools'):
    (root / dirname).mkdir(parents=True, exist_ok=True)
for directory, _, _ in os.walk(root):
    os.chmod(directory, 0o755)
