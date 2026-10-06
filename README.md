# boids-evolution

Boids for LLM tool-building societies. Does local separation improve the
usefulness of a shared tool library, beyond alignment and cohesion?

- `boidsnet/`: draft research runner. Four-arm real-model engineering smoke completed;
  this is **not a confirmatory experiment or evidence of a separation benefit**.
- `legacy/`: the earlier system and its run corpus, frozen and audited in the paper.

## Current small-pilot preparation (7 Oct 2026)

The supplemented runner passed a new **96-request, four-arm real smoke**, including
integrated mechanism analysis and independent replay. See the
[two-pass review and revalidation report](docs/SMOKE_REVALIDATION_2026-10-07.md).
This establishes engineering execution, not the paper's mechanism claims; Stage B
has not been run. No credentials or raw research runs are published here.

Use [the Stage B preparation guide](docs/STAGE_B_AND_ANALYSIS.md) and
[Mac/AgentPort instructions](docs/MAC_AGENTPORT_SMOKE.md), not the historical
official-DeepSeek or L0/E recipes below. The `000 / 100 / 011 / 111` path implements the
PDF-aligned instruction-only ablation: all arms share the same information
selectors and global library access. The old behavioral arms remain separate.

```bash
# PREPARE ONLY. No model client, API key or generated tool execution.
python -m boidsnet.runner.sac_pilot --config configs/agentport_flash_stage_b.json \
  --out review/stage-b --run-out runs/stage-b-approved
```

The proposed next-stage config is 8 agents × 12 rounds × 4 arms, one paired seed,
plus six development tasks × two solver attempts per arm: **432 nominal calls**.
Its CNY 60 local reservation ceiling is a proposal, not an approved budget or
provider invoice. Existing 4-agent × 3-round smoke configs remain separate.
Execution is blocked until the user approves that exact config/source and
single-use run ID/output directory. See [bug-fix verification](docs/BUGFIX_AUDIT.md).
Model route: AgentPort `azure:DeepSeek-V4-Flash`, requested thinking disabled.
The runner and Docker Desktop can run on the same Mac. Generated tools execute
inside the pinned stdlib-only Linux container. No new paid pilot has been launched
by preparation. Independent mechanism analysis reuses saved tools with no model calls.

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
- Tool code runs as uid 65534 in a pinned Docker container or OS namespaces, inside a minimal root (interpreter, stdlib and
  libraries read-only, plus its own tools), so it cannot read the key or the host. A run refuses to start if the host cannot
  provide verified isolation (Docker Desktop on Mac, or Linux `unshare`, `pivot_root`, `setpriv`).
- Confirmatory runs need a joint freeze (`FROZEN.json`). None exists yet; see `docs/REPO_LAYOUT.md`.
