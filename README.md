# boids-evolution

## Completed-study analysis and manuscript

The new analysis uses **existing frozen evidence only: zero additional model or
grader calls**. See the [AAMAS-format full paper](paper/tool-ecology/main.pdf),
[Chinese in-depth analysis](docs/tool-ecology/DEEP_ANALYSIS_ZH.pdf), and
[source data plus ten coordinated figures](studies/tool_ecology/evidence/v031/analysis-02/README.md).
Post-initial correct adoption occurs in Boids57/115 versus neutral26/116 admitted
publications, while final collective family coverage adds zero beyond the best
self-contained author history in every society. The analysis separates adoption,
maintenance location, persistence, reliability, root code size and token budgets.
All seeds, unsuccessful narrowing and recovery/cost provenance remain visible.
The user has ended further experiments; paid work and experiment automation stay stopped.

## Repeated-demand native tool ecology (2026-10-09)

The latest authorized exploratory experiment is complete: nine GPT-6-Luna/mini-SWE-agent societies, 420 immutable native-tool publications, identical plain/instrumented replay scores, and 71 of 72 preselected return interventions with noncrashing correctness-loss witnesses (69 of70 unique edges within societies). Local Boids guidance corresponds to more tool adoption and different dependency profiles, while every society's common-panel coverage equals its best self-contained author history; no complementary coverage gain was observed. Four narrow lookup publications occurred, with one isolated program defect diagnosed without changing original scores. All 2,121 corrected-study attempts, including a 69-call transport-failed partial cell, are accounted for. This is a recovered exploratory collection with per-cell revisions and 55/180-second transport disclosure. Paid work has ended. See [final Chinese results, tables and figures](docs/tool-ecology/FINAL_RESULTS_ZH.md), [historical live record](docs/tool-ecology/RESULTS_ZH.md), [recovery protocol](docs/tool-ecology/RECOVERY_V031.md), and [implementation](studies/tool_ecology/README.md). The earlier LDB pilot remains in [the historical report](studies/tool_ecology/REPORT_ZH.md).

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
