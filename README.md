# boids-evolution

Boids for LLM tool-building societies. Does local separation improve the
usefulness of a shared tool library, beyond alignment and cohesion?

- `boidsnet/`: draft research runner; the new SAC path is **not jointly frozen or experimentally validated**.
- `legacy/`: the earlier system and its run corpus, frozen and audited in the paper.

## Current small-pilot preparation (6 Oct 2026)

Use [the SAC/DeepSeek audit and review card](docs/SAC_DEEPSEEK_REVIEW.md), not the
older L0/E smoke recipes below. The `000 / 100 / 011 / 111` path implements the
PDF-aligned instruction-only ablation: all arms share the same information
selectors and global library access. The old behavioral arms remain separate.

```bash
# PREPARE ONLY. No model client, API key or generated tool execution.
python -m boidsnet.runner.sac_pilot --out review/deepseek-small \
  --run-out runs/deepseek-small-approved
```

The proposed config is 4 agents × 3 rounds × 4 arms, one paired seed, plus six
development tasks × two solver attempts per arm: **96 nominal model calls**.
Execution is blocked until the user approves that exact config/source and
single-use run ID/output directory. See [bug-fix verification](docs/BUGFIX_AUDIT.md).
Model:
`deepseek-flash`, thinking explicitly disabled; collaborator credentials only.
Preparation works on macOS; real execution still requires Linux OS isolation.

```
boidsnet/
  env/mechenv.py      mechanism env v0.2.2: isolated dev/test coverage tables
  runner/             agent societies, sandbox, scoring, smoke/pilot/batch, freeze
tests/                offline tests (no API calls)
docs/                 RUNNER.md (decision log D1-D24), REPO_LAYOUT.md
legacy/               pre-2026 system (src/, experiments/, scripts) - do not edit
```

## Older behavioral protocol (not the SAC experiment)

```bash
python -m unittest discover -s tests -t .                 # offline software tests
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
