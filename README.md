# boids-evolution

## Repeated-demand native tool ecology (2026-10-09)

The latest authorized exploratory experiment uses GPT-6-Luna through mini-SWE-agent, persistent private workspaces, native Python package sharing, and independently verified recurring service requests. It is a separately versioned mechanism study. A direct-function re-export attribution bug invalidated v0.3 feedback comparisons; all attempts are preserved. Corrected v0.3.1 is running a fresh fixed nine-society batch. See [live Chinese results](docs/tool-ecology/RESULTS_ZH.md), [corrected protocol](docs/tool-ecology/EXPERIMENT_V031.md), [original design](docs/tool-ecology/EXPERIMENT_2026-10-09.md) and [implementation](studies/tool_ecology/README.md). The earlier LDB engineering pilot and its limitations remain in [the historical report](studies/tool_ecology/REPORT_ZH.md).

## Current review draft: original Boids guidance controls

The new four-arm S/A/C implementation is documented in [SAC_CONTROLS](docs/SAC_CONTROLS.md).
It remains an unfrozen research design; offline DEV contracts and Linux CI
verify engineering behavior without establishing experimental efficacy. The existing behavioral study
below is preserved as a versioned legacy/optional design, not silently renamed.

## Earlier behavioral study

Boids for LLM tool-building societies. **Does behaviour-based *local repulsion*
between agents preserve the functional coverage that attraction-only coupling
(sharing, imitation) homogenises away?**

- `boidsnet/`: the new, pre-registered study (AAMAS 2027). Standard library only.
- `legacy/`: the earlier system and its run corpus, frozen and audited in the paper.

```
boidsnet/
  env/mechenv.py      mechanism env v0.2.1: typed table transforms, sealed test split, probe sets
  runner/             agent societies, sandbox, scoring, smoke/pilot/batch, freeze
tests/                offline tests (no API calls)
docs/                 RUNNER.md (decision log D1-D24), REPO_LAYOUT.md
legacy/               pre-2026 system (src/, experiments/, scripts) - do not edit
```

## Quick start (stub model, free)

```bash
python -m unittest discover -s tests -t .                 # 89 tests
python -m boidsnet.runner.run --arm L0 --seed 3 --out runs/
python -m boidsnet.runner.smoke --out smoke/              # protocol §8 engineering smoke
```

## Real-model runs

- `pip install -r requirements.txt`.
- Keys are read from environment variables only. They never go in files, logs or chat.
- Every real-model run requires `--allow-spend`.
- Tool code runs as uid 65534 in OS namespaces, inside a minimal root (interpreter, stdlib and
  libraries read-only, plus its own tools), so it cannot read the key or the host. A run refuses to start if the host cannot
  provide that (Linux `unshare`, `pivot_root`, `setpriv`).
- Confirmatory runs need a joint freeze (`FROZEN.json`). None exists yet; see `docs/REPO_LAYOUT.md`.
