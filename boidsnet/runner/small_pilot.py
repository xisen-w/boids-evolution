"""Small four-arm pilot: defaults to PREPARING only, never spends implicitly.

python -m boidsnet.runner.small_pilot prepare --out review/pilot-v2 --run-out runs/pilot-v2
Execution uses the reviewed config copy and separately approved document.
"""
import sys

from .sac_pilot import ROOT
from .mac_smoke import main as mac_main


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        args = ['--help']
    if not any(a == '--config' or a.startswith('--config=') for a in args):
        args.extend(['--config', str(ROOT / 'configs/agentport_flash_stage_b_v2.json')])
    return mac_main(args)


if __name__ == '__main__':
    main()
