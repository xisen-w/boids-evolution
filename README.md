# boids-evolution

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
docs/                 RUNNER.md (decision log D1-D20), REPO_LAYOUT.md
legacy/               pre-2026 system (src/, experiments/, scripts) - do not edit
```

## Quick start (stub model, free)

```bash
python -m unittest discover -s tests -t .                 # 76 tests
python -m boidsnet.runner.run --arm L0 --seed 3 --out runs/
python -m boidsnet.runner.smoke --out smoke/              # protocol §8 engineering smoke
```

## Real-model runs

- `pip install -r requirements.txt`.
- Keys are read from environment variables only. They never go in files, logs or chat.
- Every real-model run requires `--allow-spend`.
- Tool code runs in OS namespaces as uid 65534, so it cannot read the key. A run refuses to
  start if the host cannot provide that isolation (Linux `unshare` + `setpriv`).
- Confirmatory runs need a joint freeze (`FROZEN.json`). None exists yet; see `docs/REPO_LAYOUT.md`.
