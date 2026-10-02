"""ENGINEERING SMOKE TEST, protocol v0.3.10 §8 (a logged pre-freeze deviation).

    python -m boidsnet.runner.smoke --out smoke/                                    # stub, free
    python -m boidsnet.runner.smoke --out smoke/ --model <deployment> --key-env <VAR> \
        --azure-endpoint <url> --azure-api-version <v> --allow-spend      # real model

Fixed by the protocol, so NOT configurable here: seed 9001; arms E, L0, R0,
IM (one society each); N=8, T=3; --token-budget 300000 per society;
--param-mode auto for the societies (to DISCOVER accepted parameters);
a hard cap of 300000 solver tokens per arm on the dev diagnostic (it stops
before the next task once reached; overshoot <= 1 call).  Worst-case spend is
therefore about 4 x (300k + 1 call) society tokens + 4 x (300k + 1 call)
solver tokens, i.e. ~2.5M tokens in total.
Societies are written as ENG_<arm>_s9001 with `engineering: true` in the
manifest; they can never be scored on the test split (utility refuses) and
batch refuses --engineering.

Blinding (msg #96.1): dev split only, --unseal is never passed.  U_dev is
reported POOLED across arms only and nothing per-arm that reveals
correctness is written.  The solver runs in strict mode with the EFFECTIVE
sampling block the societies recorded (after any auto adaptation), and the
four societies must agree on it.

Coverage (msg #96.2) is asserted, not assumed: exactly the four arm dirs,
each with the protocol's seed/N/T/budget/param mode, the engineering flag, no
FAILED.json, and N*T records unless the budget truncated the society (which
is reported).  smoke_report.json has PASS=False if any assertion or gate
fails, including a skipped dev diagnostic.
"""
import argparse
import json
import os
import sys

from .pilot import arm_row, score_dev, smoke_gates
from .run import main as run_main, DEFAULT_ENV

SMOKE = {"seed": 9001, "arms": ("E", "L0", "R0", "IM"), "n_agents": 8, "n_rounds": 3,
         "token_budget": 300000, "param_mode": "auto",
         "solver_token_budget_per_arm": 300000}   # hard cap on the dev-diagnostic solver (msg #130 cost cap)
PROTOCOL_REF = "protocol v0.3.10 (sha256 f5e1fbfebd53fda539645f5738c374a131f8d5fa7b19e334e222f39ec2e1235e) §8"


def society_dir(out, arm):
    return os.path.join(out, f"ENG_{arm}_s{SMOKE['seed']:02d}")


def check_coverage(out, real_model):
    """Every protocol-specified property of the smoke societies, as a list of
    problems (empty = covered)."""
    problems, effective = [], {}
    expected = {os.path.basename(society_dir(out, a)) for a in SMOKE["arms"]}
    present = {d for d in os.listdir(out) if os.path.isdir(os.path.join(out, d))}
    if present != expected:
        problems.append(f"society dirs {sorted(present)} != {sorted(expected)}")
    for arm in SMOKE["arms"]:
        d = society_dir(out, arm)
        if not os.path.isdir(d):
            continue
        if os.path.exists(os.path.join(d, "FAILED.json")):
            problems.append(f"{arm}: FAILED.json present")
            continue
        man = json.load(open(os.path.join(d, "run_manifest.json")))
        for key, want in (("arm", arm), ("seed", SMOKE["seed"]), ("n_agents", SMOKE["n_agents"]),
                          ("n_rounds", SMOKE["n_rounds"]), ("token_budget", SMOKE["token_budget"]),
                          ("engineering", True)):
            if man.get(key) != want:
                problems.append(f"{arm}: manifest {key}={man.get(key)!r}, protocol says {want!r}")
        if real_model and man.get("param_mode") != SMOKE["param_mode"]:
            problems.append(f"{arm}: param_mode {man.get('param_mode')!r} != auto")
        summ = json.load(open(os.path.join(d, "summary.json")))
        if summ["records"] != SMOKE["n_agents"] * SMOKE["n_rounds"] and not summ["truncated"]:
            problems.append(f"{arm}: {summ['records']} records, expected N*T={SMOKE['n_agents'] * SMOKE['n_rounds']}")
        for sub in os.listdir(d):
            if sub.startswith("utility") and sub != "utility_dev":
                problems.append(f"{arm}: non-dev utility dir {sub}")
        samp = man.get("sampling") or {}
        effective[arm] = (samp.get("temperature_sent"), samp.get("token_param"), man.get("model"))
    if len(set(effective.values())) > 1:
        problems.append(f"societies disagree on the effective sampling block: {effective}")
    return problems, (next(iter(effective.values())) if effective else None)


def build_solver(real_model, effective, passthrough):
    from .utility import StubSolver
    if not real_model:
        return StubSolver()
    q = argparse.ArgumentParser()
    for f in ("--model", "--key-env", "--azure-endpoint", "--azure-api-version", "--base-url"):
        q.add_argument(f, default=None)
    q.add_argument("--allow-spend", action="store_true")
    b, _ = q.parse_known_args(passthrough)
    from .model import OpenAICompatModel
    temp_sent, token_param, model_name = effective
    return OpenAICompatModel(model_name, b.key_env or "OPENAI_API_KEY", b.allow_spend, b.base_url,
                             b.azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT"),
                             b.azure_api_version or os.environ.get("AZURE_OPENAI_API_VERSION"),
                             send_temperature=bool(temp_sent), token_param=token_param,
                             param_mode="strict")


FORBIDDEN = ("--unseal", "--frozen", "--seed", "--arm", "--n-agents", "--n-rounds",
             "--token-budget", "--param-mode", "--engineering", "--out")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a, passthrough = p.parse_known_args(argv)
    bad = [f for f in passthrough if f.split("=")[0] in FORBIDDEN]
    if bad:
        sys.exit(f"the smoke setup is fixed by the protocol; do not pass {bad}")
    if os.path.exists(a.out) and os.listdir(a.out):
        sys.exit(f"refusing: {a.out} is not empty")
    os.makedirs(a.out, exist_ok=True)
    real_model = "--model" in passthrough and passthrough[passthrough.index("--model") + 1] != "stub"
    for arm in SMOKE["arms"]:
        try:
            run_main(["--arm", arm, "--seed", str(SMOKE["seed"]), "--out", a.out, "--engineering",
                      "--n-agents", str(SMOKE["n_agents"]), "--n-rounds", str(SMOKE["n_rounds"]),
                      "--token-budget", str(SMOKE["token_budget"]),
                      "--param-mode", SMOKE["param_mode"]] + passthrough)
        except SystemExit as e:
            if e.code not in (None, 0):
                print(json.dumps({"arm": arm, "status": "FAILED", "exit": e.code}))
    problems, effective = check_coverage(a.out, real_model)
    rows = {arm: arm_row(society_dir(a.out, arm)) for arm in SMOKE["arms"]
            if os.path.exists(os.path.join(society_dir(a.out, arm), "rounds.jsonl"))}
    dev = None
    if not problems:
        from .env_adapter import MechEnv
        env = MechEnv(DEFAULT_ENV)
        dev = score_dev({arm: society_dir(a.out, arm) for arm in SMOKE["arms"]},
                        build_solver(real_model, effective, passthrough), env,
                        token_budget_per_arm=SMOKE["solver_token_budget_per_arm"])
        if set(dev["per_arm"]) != set(SMOKE["arms"]):
            problems.append(f"dev diagnostic covers {sorted(dev['per_arm'])}")
    gates = smoke_gates(rows, dev) if rows else {"PASS": False}
    rep = {"protocol": PROTOCOL_REF, "deviation": "pre-freeze ENGINEERING smoke; not a pilot or confirmatory run",
           "setup": SMOKE, "effective_sampling": effective, "coverage_problems": problems,
           "per_arm": rows, "dev_diagnostic": dev, "smoke_gates": gates,
           "PASS": not problems and gates["PASS"]}
    with open(os.path.join(a.out, "smoke_report.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps({k: rep[k] for k in ("coverage_problems", "smoke_gates", "PASS")}, indent=1))
    return rep


if __name__ == "__main__":
    main()
