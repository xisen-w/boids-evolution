# Engineering smoke: exact recipe (runner v0.17)

Status: **not run**. It needs Xisen's go-ahead, a key and the deployment details below. It is a
logged pre-freeze deviation (protocol v0.3.11 §8). It never opens the sealed test split and
never produces an outcome.

## Fixed by the code (cannot be overridden on the command line)

| Setting | Value |
|---|---|
| Arms | E, L0, R0, IM (one society each) |
| Seed | 9001 |
| N agents / T rounds / k / m / dev tasks shown | 8 / 3 / 2 / 4 / 8 |
| Society token budget | 300,000 per society; stops before the next call once reached |
| Agent call `max_tokens` | 4,000 |
| Society sampling | `--param-mode auto`, to discover which parameters the deployment accepts. Recorded in the manifest as the *effective* block |
| Temperature | 0.7, unless the deployment rejects it (auto mode records the adaptation) |
| Dev diagnostic | 60 dev tasks × 1 attempt per arm. Solver uses the society's effective sampling in strict mode. Hard cap 300,000 solver tokens per arm |
| Outputs | per-arm parse / crash / fire / parametric / missing-module / sandbox-block rates, solver tokens per call, per-arm gate-fail rate and reasons, `U_dev` pooled across arms only |
| Run dirs | `ENG_<arm>_s9001`, with `engineering: true` in the manifest. They can never be scored on the test split |

Passing any of `--seed --arm --n-agents --n-rounds --token-budget --param-mode --engineering
--unseal --frozen` to `runner.smoke` exits with an error.

## Choices still open (Xisen)

| Item | Status |
|---|---|
| Provider | Azure OpenAI, on Xisen's own deployment. No Qi-side credentials, ever |
| Deployment (`--model`) | `gpt-6-luna` proposed (msg #72). **Needs confirmation** |
| API version (`--azure-api-version`) | **Not provided yet** |
| Key | Environment variable only, named by `--key-env`. A dedicated low-quota key, rotated afterwards |

## Worst-case cost (hard caps)

- Societies: 4 × (300k + one call of overshoot, at most ~12k) ≈ **1.24M tokens**.
- Solver: 4 × (300k + one call of overshoot) ≈ **1.24M tokens**.
- **Total ≤ ~2.5M tokens.** Multiply by the deployment's input/output prices for the money cap.
- Expected spend is below the cap. The stub measures ~140k prompt tokens per society at T=10, so
  T=3 should be well under 300k.

## Command

```bash
git clone --branch claude/codebase-setup-201ak0 https://github.com/xisen-w/boids-evolution.git
cd boids-evolution
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export AZURE_AI_KEY=...          # set in the environment settings, never in a file or chat
.venv/bin/python -m boidsnet.runner.smoke --out smoke/ \
    --model <deployment> --key-env AZURE_AI_KEY \
    --azure-endpoint <https://...openai.azure.com> --azure-api-version <version> --allow-spend
```

The run refuses to start unless the OS sandbox is available. It records `sandbox_isolation` and
`sandbox_probe` in every manifest. Read `smoke/smoke_report.json`: `PASS` is false on any
coverage problem or failed gate.

## Executor

Any Linux host with `unshare`, `pivot_root` and `setpriv` (util-linux), with root or unprivileged
user namespaces, that holds **no Qi credentials**. Xisen's cloud container satisfies this: os-root
was verified. The key has to be added to its environment settings and a new session started.

## Independent validation (no key, no network calls)

```bash
git clone --branch claude/codebase-setup-201ak0 https://github.com/xisen-w/boids-evolution.git v && cd v
python3 -m venv /tmp/bv && /tmp/bv/bin/pip install -r requirements.txt
env -i PATH=/tmp/bv/bin:/usr/bin:/bin HOME=$(mktemp -d) PYTHONHASHSEED=0 \
    python -c "from boidsnet.runner.freeze import code_hash; from boidsnet.runner.sandbox import isolation_level; print(code_hash(), isolation_level())"
env -i PATH=/tmp/bv/bin:/usr/bin:/bin HOME=$(mktemp -d) PYTHONHASHSEED=0 \
    python -m unittest discover -s tests -t .        # expect: Ran 84 tests ... OK
env -i PATH=/tmp/bv/bin:/usr/bin:/bin HOME=$(mktemp -d) PYTHONHASHSEED=0 \
    python -m boidsnet.runner.smoke --out /tmp/smoke_stub   # stub smoke, free; expect PASS: true
```

`env -i` gives a clean child environment: no inherited credentials or user site-packages.
Without unshare/pivot_root/setpriv the isolation level is `hook-only`. The tamper-first sandbox
tests are then skipped, and real-model runs refuse to start.
