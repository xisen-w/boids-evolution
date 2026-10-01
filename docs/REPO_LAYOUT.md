# Repository layout (Oct 2026 refactor)

The repo holds two systems. They share no code.

| Path | What it is | Status |
|---|---|---|
| `boidsnet/env/mechenv.py` | Mechanism environment: typed table transforms with reference implementations, sealed test split, probe sets. | v0.2.1 |
| `boidsnet/runner/` | Society runner, sandbox, U harness, smoke/pilot/batch orchestration, freeze. The only model backend (`model.py`, OpenAI/Azure). | Draft, not frozen |
| `tests/` | Offline tests for env and runner. | |
| `docs/RUNNER.md` | Runner guarantees and the decision log D1-D21. | |
| `legacy/` | The earlier Boids tool-evolution system and its run corpus, as audited in the paper. Moved here unchanged with `git mv`. | **Frozen. Do not edit.** |

Audit findings cite legacy files at commit `524dc76`, the last commit before the move. That
commit has the original root paths (`src/...`, `experiments/...`, `run_experiment.py`, ...).
In this tree the same files are under `legacy/`, and `git log --follow` traces them.

## Running

```bash
python -m unittest discover -s tests -t .      # offline, 81 tests
python boidsnet/env/mechenv.py                 # env self-checks, prints the test seal
```

There is one mechenv copy: the runner loads `boidsnet/env/mechenv.py`. The code hash
(`python -c "from boidsnet.runner.freeze import code_hash; print(code_hash())"`) covers
`boidsnet/runner/*.py` plus that file.

## Status (1 Oct 2026)

- The protocol is draft v0.3.11. The canonical text is in the project room (sha256 `094adcdc...`).
- There is **no joint freeze**: the Qi-side cutoff passed without approval, and stop rule §8 applies.
- No real-model run has been made with this code.

## Invariants the protocol relies on

- The sealed TEST split hash is `25634f7783fffbac3c2e1f74c545c2f647806218173b1af2dd3e2f1393c82371`
  for `tasks(0, "test")`, independent of `PYTHONHASHSEED` (tested).
- Builders only ever see the dev split. The test split opens only via `--unseal` in
  `boidsnet.runner.utility`, which smoke, pilot and batch never pass.
- Tool code is untrusted. It runs in mount, PID and network namespaces as uid 65534,
  pivot_root'ed into an allowlist root: read-only /usr, /dev/{null,zero,urandom}, its own /proc,
  and only its ACL-reachable tools. No other host path exists for it (docs/RUNNER.md D20-D21).

## Change log

- v0.2.1 env: `make_task` drew terminal primitives from `list(TERMINAL)`, which iterates a set,
  so the dev and test task lists depended on `PYTHONHASHSEED`. The fix is `sorted(TERMINAL)`,
  which reproduces the published seal under every hash seed.
- Runner v0.13 moved into `boidsnet/runner/`. `vendor/mechenv.py` was dropped in favour of the
  single in-repo copy (identical logic, comments differ), so the code hash changed.
