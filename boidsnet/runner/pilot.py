"""Pilot: one society per arm (two for L0, protocol §8), then a cost / health report.

    python -m boidsnet.runner.pilot --out pilot/ --seed 900                     # stub, free
    python -m boidsnet.runner.pilot --out pilot/ --seed 900 --model <m> \
        --key-env OPENAI_API_KEY --allow-spend --frozen FROZEN.json    # paid

Pilot seeds must not overlap the pre-listed confirmatory seeds.  Each arm is
a separate run.py invocation, so the pilot uses exactly the confirmatory
code path.  The report projects total tokens for the confirmatory design
(n societies per arm) from the measured per-society mean.
"""
import argparse
import json
import os
import sys

from .config import PROTOCOL_ARMS as ARMS
from .run import main as run_main


def arm_row(d):
    """Per-society health metrics from rounds.jsonl (no outcome data)."""
    with open(os.path.join(d, "rounds.jsonl")) as fh:
        recs = [json.loads(l) for l in fh]
    n = len(recs) or 1
    return {
        "calls": len(recs),
        "tokens": max((r["tokens_cum"] for r in recs), default=0),
        "parse_rate": sum(r["parse_ok"] for r in recs) / n,
        "pass_rate": sum(1 for r in recs if (r.get("harness") or {}).get("passed")) / n,
        "rule_fire_rate": sum(r["rule_fired"] for r in recs) / n,
        "rule_fire_rate_after_r2": (sum(r["rule_fired"] for r in recs if r["round"] > 2)
                                    / max(1, sum(1 for r in recs if r["round"] > 2))),
        "cross_agent_import_rate": sum(bool(r.get("cross_agent_imports")) for r in recs) / n,
        "target_unknown_rate": sum(1 for r in recs
                                   if (r.get("harness") or {}).get("reason") == "no_or_unknown_target") / n,
        # smoke-test diagnostics (msgs #79/#80): why tools crash, and how many are parametric
        "missing_module_rate": sum("ModuleNotFoundError" in (r.get("exec_feedback") or "") for r in recs) / n,
        "sandbox_block_rate": sum("PermissionError" in (r.get("exec_feedback") or "") for r in recs) / n,
        "all_crash_on_signal_rate": sum(bool(r.get("signature_signal")) and
                                        all(str(x).startswith("ERR") for x in r["signature_signal"])
                                        for r in recs) / n,
        "parametric_candidate_rate": sum(bool(r.get("implements")) and bool(r.get("signature_signal")) and
                                         all(str(x).startswith("ERR") for x in r["signature_signal"])
                                         for r in recs) / n,
        "own_tool_crashed_rate": sum(r.get("selection_mode") == "own_tool_crashed" for r in recs) / n,
        "api_retries": sum(r.get("api_retries", 0) for r in recs),
    }


def report(out, seed, n_per_arm, dev=None, n_test_tasks=60, solver_attempts=3, n_confirm_arms=6,
           l0_seed2=None):
    rows = {arm: arm_row(os.path.join(out, f"{arm}_s{seed:02d}")) for arm in ARMS}
    extra = None
    if l0_seed2 is not None:                 # protocol §8: 2 L0 societies, crude between-society spread
        r2 = arm_row(os.path.join(out, f"L0_s{l0_seed2:02d}"))
        extra = {"L0_second_society": r2,
                 "L0_pair_abs_diff": {k: abs(rows["L0"][k] - r2[k]) for k in
                                      ("tokens", "parse_rate", "pass_rate", "rule_fire_rate_after_r2")}}
    mean_tokens = sum(r["tokens"] for r in rows.values()) / len(rows)
    return {"per_arm": rows, "l0_replicate": extra, "mean_tokens_per_society": mean_tokens,
            "projected_tokens_all_arms": mean_tokens * n_per_arm * len(ARMS),
            "criteria": criteria(rows),
            "dev_diagnostic": dev,
            "smoke_gates": smoke_gates(rows, dev),
            # S1: projected solver cost for the confirmatory U (calls x measured tokens/call)
            "projected_solver_calls": n_per_arm * n_confirm_arms * n_test_tasks * solver_attempts,
            "projected_solver_tokens": (dev["solver_tokens_per_call"] * n_per_arm * n_confirm_arms
                                        * n_test_tasks * solver_attempts) if dev else None,
            "g0m_matching_gate": matching_gate(out, seed)}


def matching_gate(out, seed):
    """v0.3.8: G0m (exploratory) matching quality on REAL-model pilot data.
    mean |mean sim(L0 exemplars) - mean sim(G0m exemplars)| <= 0.05 and
    shortfall rate <= 10% of G0m exemplar slots; otherwise G0m is reported
    as 'not tested at matched similarity'."""
    def load(arm):
        with open(os.path.join(out, f"{arm}_s{seed:02d}", "rounds.jsonl")) as fh:
            return [json.loads(l) for l in fh]
    sims = {}
    for arm in ("L0", "G0m"):
        v = [x for r in load(arm) for x in r["exemplar_similarity"] if x is not None]
        sims[arm] = sum(v) / len(v) if v else None
    g = load("G0m")
    slots = sum(len((r.get("exemplar_match") or {}).get("targets") or []) for r in g)
    short = sum((r.get("exemplar_match") or {}).get("shortfall", 0) for r in g)
    gap = None if None in sims.values() else abs(sims["L0"] - sims["G0m"])
    rate = short / slots if slots else 0.0
    return {"mean_sim_L0": sims["L0"], "mean_sim_G0m": sims["G0m"], "gap": gap,
            "shortfall_rate": rate,
            "PASS": gap is not None and gap <= 0.05 and rate <= 0.10}


def smoke_gates(rows, dev):
    """v0.3.10 smoke gates (msgs #81/#82).  gate_fail <= 0.20 and
    missing_module <= 0.10 in every arm; D3-P (parametric_candidate > 0.25 in
    any arm) is a trigger for mechenv v0.3, not a pass/fail.  If the dev
    diagnostic was not run, the gate_fail gate is None and PASS is False
    (msg #96.2: never pass silently on a skipped check)."""
    g = {"missing_module<=0.10_all_arms": all(r["missing_module_rate"] <= 0.10 for r in rows.values()),
         "D3P_triggered(parametric_candidate>0.25_any_arm)":
             any(r["parametric_candidate_rate"] > 0.25 for r in rows.values()),
         "gate_fail<=0.20_all_arms": (None if dev is None else
                                      all(d["gate_fail_rate"] <= 0.20 for d in dev["per_arm"].values()))}
    g["PASS"] = bool(g["missing_module<=0.10_all_arms"] and g["gate_fail<=0.20_all_arms"])
    return g


def score_dev(dirs, solver, env, token_budget_per_arm=None):
    """Dev-split U diagnostic (msg #82 B', #96.1).  dirs: arm -> society dir.
    Per arm: gate_fail_rate, reason tallies, solver cost.  U_dev is computed
    in memory and reported POOLED across arms only; nothing per-arm that
    reveals correctness is written (utility.score_society split='dev')."""
    from .utility import score_society
    per_arm, pooled = {}, []
    for arm, d in dirs.items():
        r = score_society(d, env, solver, attempts=1, split="dev", token_budget=token_budget_per_arm)
        pooled += r.pop("_dev_task_scores")
        per_arm[arm] = {k: r[k] for k in ("gate_fail_rate", "gate_fail_reasons", "solver_calls",
                                          "solver_tokens", "solver_tokens_per_call", "solver_cached_tokens",
                                          "parametric_share", "n_tasks_scored", "solver_truncated_by_budget")}
        per_arm[arm]["n_kept"] = len(r["library"]["kept"])      # S1: extrapolate tokens/call by library size
    calls = sum(d["solver_calls"] for d in per_arm.values())
    tok = sum(d["solver_tokens"] for d in per_arm.values())
    return {"per_arm": per_arm, "U_dev_POOLED_DIAGNOSTIC": sum(pooled) / len(pooled) if pooled else None,
            "solver_tokens_per_call": tok / calls if calls else 0.0,
            "solver_cached_share": (sum(d["solver_cached_tokens"] for d in per_arm.values()) / tok) if tok else 0.0}


def criteria(rows):
    """Pre-registered pilot gates (msg #33). Any failure: fix and re-pilot."""
    import statistics
    parse_ok = all(r["parse_rate"] >= 0.80 for r in rows.values())
    fire_ok = all(rows[a]["rule_fire_rate_after_r2"] >= 0.50 for a in ("L0", "R0", "L1", "G0m"))
    med = statistics.median(r["pass_rate"] for r in rows.values())
    pass_ok = 0.05 <= med <= 0.80
    return {"parse_rate>=0.80_all_arms": parse_ok,
            "rule_fire>=0.50_after_round2_L0_R0_L1_G0m": fire_ok,
            "median_pass_rate_in_[0.05,0.80]": pass_ok, "median_pass_rate": med,
            "PASS": parse_ok and fire_ok and pass_ok}


def solver_from(passthrough):
    """Build the solver from the same flags the societies ran with."""
    from .env_adapter import MechEnv
    from .run import DEFAULT_ENV
    from .utility import StubSolver
    q = argparse.ArgumentParser()
    for f in ("--model", "--key-env", "--azure-endpoint", "--azure-api-version", "--token-param", "--env-path"):
        q.add_argument(f, default=None)
    q.add_argument("--dev-seed", type=int, default=0)
    q.add_argument("--allow-spend", action="store_true")
    q.add_argument("--no-temperature", action="store_true")
    b, _ = q.parse_known_args(passthrough)
    env = MechEnv(b.env_path or DEFAULT_ENV, b.dev_seed)
    if b.model in (None, "stub"):
        return StubSolver(), env
    from .model import OpenAICompatModel
    return OpenAICompatModel(b.model, b.key_env or "OPENAI_API_KEY", b.allow_spend,
                             azure_endpoint=b.azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT"),
                             api_version=b.azure_api_version or os.environ.get("AZURE_OPENAI_API_VERSION"),
                             send_temperature=not b.no_temperature,
                             token_param=b.token_param or "max_tokens", param_mode="strict"), env


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--n-per-arm", type=int, default=10)
    p.add_argument("--l0-seed2", type=int, default=None,
                   help="seed of the 2nd L0 society (protocol §8); default seed+1")
    p.add_argument("--score-dev", action="store_true",
                   help="also run the dev-split U diagnostic (solver = same deployment/sampling)")
    a, passthrough = p.parse_known_args(argv)
    if "--engineering" in passthrough:
        sys.exit("the pilot is a frozen run; the pre-freeze engineering smoke is boidsnet.runner.smoke")
    l0_seed2 = a.seed + 1 if a.l0_seed2 is None else a.l0_seed2
    if l0_seed2 == a.seed:
        sys.exit("--l0-seed2 must differ from --seed")
    for arm in ARMS:
        run_main(["--arm", arm, "--seed", str(a.seed), "--out", a.out] + passthrough)
    run_main(["--arm", "L0", "--seed", str(l0_seed2), "--out", a.out] + passthrough)
    dev = None
    if a.score_dev:
        dirs = {arm: os.path.join(a.out, f"{arm}_s{a.seed:02d}") for arm in ARMS}
        dev = score_dev(dirs, *solver_from(passthrough))
    rep = report(a.out, a.seed, a.n_per_arm, dev, l0_seed2=l0_seed2)
    with open(os.path.join(a.out, "pilot_report.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
