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
PROTOCOL_REF = "protocol v0.3.12 (sha256 d9569a07322e168284e4b3fbde37b9d9f02bbe249a0fec3ce451e17ef3bf6555) §8"


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


def backend_args(passthrough):
    """msg #134: parse the model/backend options STRUCTURALLY (so --model=x and
    --model x behave the same) and accept ONLY these; anything else is refused."""
    q = argparse.ArgumentParser(prog="runner.smoke", add_help=False)
    q.add_argument("--model", default="stub")
    q.add_argument("--key-env", default="OPENAI_API_KEY")
    q.add_argument("--base-url", default=None)
    q.add_argument("--azure-endpoint", default=None)
    q.add_argument("--azure-api-version", default=None)
    q.add_argument("--allow-spend", action="store_true")
    q.add_argument("--no-temperature", action="store_true")
    q.add_argument("--token-param", default="max_tokens", choices=("max_tokens", "max_completion_tokens"))
    b, unknown = q.parse_known_args(passthrough)
    if unknown:
        sys.exit(f"runner.smoke accepts only the backend options; refusing {unknown} "
                 "(seed, arms, N, T, budgets, param mode, env and dev seed are fixed by the protocol)")
    argv = ["--model", b.model, "--key-env", b.key_env, "--token-param", b.token_param]
    for flag, val in (("--base-url", b.base_url), ("--azure-endpoint", b.azure_endpoint),
                      ("--azure-api-version", b.azure_api_version)):
        if val:
            argv += [flag, val]
    argv += ["--allow-spend"] * b.allow_spend + ["--no-temperature"] * b.no_temperature
    return b, argv


def build_solver(b, effective):
    from .utility import StubSolver
    if b.model == "stub":
        return StubSolver()
    from .model import OpenAICompatModel
    temp_sent, token_param, model_name = effective
    return OpenAICompatModel(model_name, b.key_env, b.allow_spend, b.base_url, b.azure_endpoint,
                             b.azure_api_version, send_temperature=bool(temp_sent),
                             token_param=token_param, param_mode="strict")


def backend_receipt(out, b, solver):
    """What actually ran, read back from the manifests, plus the solver object."""
    builders = {}
    for arm in SMOKE["arms"]:
        mp = os.path.join(society_dir(out, arm), "run_manifest.json")
        if os.path.exists(mp):
            m = json.load(open(mp))
            builders[arm] = {"model": m.get("model"), "backend": m.get("backend"),
                             "client": m.get("model_client"), "api_version": m.get("azure_api_version"),
                             "transport": m.get("transport"), "sandbox": m.get("sandbox_isolation")}
    solv = None if solver is None else {"client": type(solver).__name__, "model": getattr(solver, "name", "stub"),
                                        "transport": solver.transport_policy() if hasattr(solver, "transport_policy") else None}
    problems = []
    for arm, r in builders.items():
        if r["model"] != b.model:
            problems.append(f"{arm}: builder model {r['model']!r} != requested {b.model!r}")
        if (r["client"] == "StubModel") != (b.model == "stub"):
            problems.append(f"{arm}: builder client {r['client']} inconsistent with --model {b.model!r}")
    if solv is not None:
        if (solv["client"] == "StubSolver") != (b.model == "stub"):
            problems.append(f"solver client {solv['client']} inconsistent with --model {b.model!r}")
        if b.model != "stub" and solv["model"] != b.model:
            problems.append(f"solver deployment {solv['model']!r} != builder {b.model!r}")
    return {"builders": builders, "solver": solv}, problems


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    a, passthrough = p.parse_known_args(argv)
    b, backend_argv = backend_args(passthrough)
    if os.path.exists(a.out) and os.listdir(a.out):
        sys.exit(f"refusing: {a.out} is not empty")
    os.makedirs(a.out, exist_ok=True)
    real_model = b.model != "stub"
    for arm in SMOKE["arms"]:
        try:
            run_main(["--arm", arm, "--seed", str(SMOKE["seed"]), "--out", a.out, "--engineering",
                      "--n-agents", str(SMOKE["n_agents"]), "--n-rounds", str(SMOKE["n_rounds"]),
                      "--token-budget", str(SMOKE["token_budget"]),
                      "--param-mode", SMOKE["param_mode"]] + backend_argv)
        except SystemExit as e:
            if e.code not in (None, 0):
                print(json.dumps({"arm": arm, "status": "FAILED", "exit": e.code}))
    problems, effective = check_coverage(a.out, real_model)
    rows = {arm: arm_row(society_dir(a.out, arm)) for arm in SMOKE["arms"]
            if os.path.exists(os.path.join(society_dir(a.out, arm), "rounds.jsonl"))}
    dev, solver = None, None
    if not problems:
        from .env_adapter import MechEnv
        env = MechEnv(DEFAULT_ENV)
        solver = build_solver(b, effective)
        dev = score_dev({arm: society_dir(a.out, arm) for arm in SMOKE["arms"]}, solver, env,
                        token_budget_per_arm=SMOKE["solver_token_budget_per_arm"])
        if set(dev["per_arm"]) != set(SMOKE["arms"]):
            problems.append(f"dev diagnostic covers {sorted(dev['per_arm'])}")
    receipt, rproblems = backend_receipt(a.out, b, solver)
    problems += rproblems
    gates = smoke_gates(rows, dev) if rows else {"PASS": False}
    rep = {"protocol": PROTOCOL_REF, "deviation": "pre-freeze ENGINEERING smoke; not a pilot or confirmatory run",
           "setup": SMOKE, "effective_sampling": effective, "backend_receipt": receipt,
           "coverage_problems": problems, "per_arm": rows, "dev_diagnostic": dev, "smoke_gates": gates,
           "PASS": not problems and gates["PASS"]}
    with open(os.path.join(a.out, "smoke_report.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps({k: rep[k] for k in ("coverage_problems", "smoke_gates", "PASS")}, indent=1))
    return rep


if __name__ == "__main__":
    main()
