# Repository layout (Oct 2026 refactor)

The repo now holds two systems. They share no code.

| Path | What it is | Status |
|---|---|---|
| `boidsnet/` | New code for the pre-registered AAMAS 2027 study (protocol v0.3.8). Stdlib only. | Active, draft, not frozen |
| `boidsnet/env/mechenv.py` | Mechanism environment: typed table transforms with reference implementations, sealed test split, probe sets. | v0.2.1 |
| `tests_boidsnet/` | Env tests; offline. | |
| `src/`, `experiments/`, `legacy/`, root `*.py` and `*.sh` scripts | The earlier Boids tool-evolution system and its run corpus, as audited in the paper. | **Frozen. Do not edit.** Audit findings cite these paths. |

The society runner (`boids_runner`) is owned by another agent in the project room. Use v0.8.1 or later
(v0.7 had a sandbox hole). It vendors mechenv, which must be v0.2.1. It has the only model
backend (`runner/model.py`, OpenAI/Azure), so the frozen tree has a single model code path.

## Running

```bash
python -m unittest discover -s tests_boidsnet -t .     # offline
python boidsnet/env/mechenv.py                              # env self-checks, prints the test seal
```

Paid runs go through the runner only. They need `AZURE_AI_ENDPOINT` and `AZURE_AI_KEY` in the
environment (never in files or chat), `--allow-spend`, and a freeze manifest.

## Invariants the protocol relies on

- The sealed TEST split hash is `25634f7783fffbac3c2e1f74c545c2f647806218173b1af2dd3e2f1393c82371`
  for `tasks(0, "test")`, independent of `PYTHONHASHSEED`. This is tested.
- Builders only ever see the dev split. The test split is for the frozen-library solver.

## Change log

- v0.2.1 env: `make_task` drew terminal primitives from `list(TERMINAL)`, which iterates a set.
  The dev and test task lists therefore depended on `PYTHONHASHSEED` (seed 5 produced a different
  sealed split). The fix is `sorted(TERMINAL)`. It reproduces the published seal under every hash
  seed, so no confirmatory artefact changes.
