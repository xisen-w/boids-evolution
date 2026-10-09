# Native tool ecology in the core Boids repository

Imported from the separately delivered c447544 implementation on 2026-10-09. Its earlier v0.2 LDB pilot is preserved below and in REPORT_ZH.md. The repeated-demand v0.3 mechanism study is described in ../../docs/tool-ecology/EXPERIMENT_2026-10-09.md. Original boidsnet/ and legacy/ source are preserved.

From the **core repository root**, using the pinned host runtime and existing pinned Docker image:

```bash
PYTHONPATH=studies/tool_ecology python -m pytest studies/tool_ecology/tests -q
PYTHONPATH=studies/tool_ecology python -m ecology.dynamics --phase engineering --agents 4 --rounds 3 --seeds 9001 --arms local-neutral,local-boids --output studies/tool_ecology/runs/demand-engineering-01
PYTHONPATH=studies/tool_ecology python -m ecology.dynamics --phase exploratory --output studies/tool_ecology/runs/demand-batch-01
```

Both model launchers require a clean committed source tree and a fresh output directory. No keys enter model mounts; default key file is host-only /tmp/boids-agentport.key. No API retry or silent fallback. Maximum requests for the fixed nine-society batch: 2,592; max_output_tokens=3,000 per physical request. This is a request/token ceiling, not a verified dollar-price cap. Four concurrent agents, synchronous pre-round snapshots, per-round role-free self-selection. Service feedback is independently verified DEV feedback and is explicitly **not** sealed TEST performance or an external validated benchmark.

The original v0.2 command/path examples below refer to its separate delivered checkout, not this core-repo integration.

---

# Boids tool ecology — engineering implementation

Latest delivery: [Chinese report and pilot table](REPORT_ZH.md), [machine-readable results](evidence/pilot-07/results.csv). Valid Luna run: smoke-07 at c7e22a6; current source adds robust local image-ID resolution and archived analysis scripts.

This implements the three authorized steps: audit Python library tasks; construct local societies with a mature coding agent; freeze and evaluate on withheld downstream tasks. It adapts LibraryDesignBench and is not an official leaderboard submission.

- Task audit: `evidence/task-audit.json` (pyda, python_validation, uglypie).
- Design and deviations: `docs/DESIGN.md`, `docs/LEDGER.md`.
- Native runtime: mini-SWE-agent 2.4.6 DefaultAgent, pinned transport and real GPT-6-Luna Responses API. Each outer turn is a bounded edit/test/debug loop, not one model call.
- Default smoke: 4 agents × 3 rounds, two local arms, two withheld problems per arm, two no-library consumers. Builders and downstream consumers have separate Docker filesystems.
- Source repositories are ignored under `external/`; commit pins are in the design and task audit. No credentials are committed. API key is read from a chmod-600 file outside the repo.

## Commands

Host runtime installed at `/Users/wangxiang/.local/share/boids-ecology-runtime` using uv copy mode to avoid dataless cached hardlinks. The execution checkout is `/Users/wangxiang/.local/share/boids-ecology-workspace`; a pinned sparse task checkout is `/Users/wangxiang/.local/share/boids-ecology-sources/ldb-tasks`. Both are outside iCloud. Set `PY` to the runtime `bin/python` and run commands from the execution checkout. A fresh machine may install requirements-host.lock.txt into its own local venv.

```bash
PY=/Users/wangxiang/.local/share/boids-ecology-runtime/bin/python
TASKS=/Users/wangxiang/.local/share/boids-ecology-sources/ldb-tasks
export PYTHONPYCACHEPREFIX=/tmp/boids-local-bytecode
docker build -t boids-pyda:20261008 docker
$PY -m pytest -q
$PY -m ecology.cli audit --tasks "$TASKS" --output runs/new-audit
$PY -m ecology.cli references --tasks "$TASKS" --output runs/new-reference-check
$PY -m ecology.cli smoke --tasks "$TASKS" --output runs/new-smoke --key-file /path/to/key
```

Run directories cannot be overwritten/resumed silently. Paid smoke requires a clean committed source tree; every physical request is reserved and saved before dispatch; no automatic transport retries or model fallbacks. The 240-request/700k-output-token reservation cap is a technical limit, not a verified currency cap. Provider charges are not inferred from missing prices.

## What is guaranteed and what is measured

The host assigns immutable publication IDs, rejects symlinks/special files, checks received static imports, uses pre-round snapshots, records all dependency-bundle receipts, and verifies frozen bytes. Docker builders have no network, credentials, shared registry, hidden tests, or Docker socket. Original task verifiers are introduced in a different container after consumers finish. All score files and positive test counts are required; a failing verifier cannot be accepted as strict success.

Publication means syntax/admission checks, not semantic correctness. Author labels and import declarations do not prove division of labor or functional reuse. Module-level Python function traces and optional return interventions support diagnosis; class/native/reflection coverage is incomplete. A short engineering smoke is not evidence that Boids outperforms neutral collaboration.

## Preserved evidence

Smoke-03 used an incorrect login-shell PATH and is invalid for arm comparisons. Smoke-04/05/06 are zero-model-request preflight failures (iCloud files and Docker tag lookup). Full attempts are retained; smoke-07 has no transport errors. Source, manifest, requests, responses, trajectories, frozen packages, original grades, all-cell uninstrumented replays, and explicitly separate posthoc diagnostics are preserved in runs/luna-smoke-07. Curated records are committed under evidence/pilot-07.

Analysis scripts are in scripts/. Run summarize_run.py from this project root; the other scripts refuse existing diagnostic output directories. The cross-author probe is a host-written diagnostic on actual Luna packages, not an autonomous consumer result. Never replace the scored frozen submissions with the diagnosed/modified copy.
