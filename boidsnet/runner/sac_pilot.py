"""Review-gated, development-only small SAC pilot. Default action is PREPARE.

No .env loading, local credential fallback, test unsealing, resumption,
auto-approval or automatic scale-up. A fresh approval binds both config and
source. This launcher deliberately cannot serve a full confirmatory batch.
"""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import uuid
from pathlib import Path

from .config import RunConfig, SAC_ARMS
from .env_adapter import MechEnv
from .freeze import code_hash
from .mechanisms import canonical
from .run import DEFAULT_ENV

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "configs" / "deepseek_flash_small.json"
KEYS = {"version", "arms", "seeds", "n_agents", "n_rounds", "k", "menu_size", "dev_seed",
        "eval_tasks_per_depth", "solver_attempts", "model", "base_url", "thinking", "temperature",
        "builder_max_tokens", "solver_max_tokens", "max_input_bytes", "max_http_attempts_per_call",
        "max_http_requests", "max_reserved_usd", "input_usd_per_million", "output_usd_per_million",
        "tool_timeout_s", "separation_threshold", "alignment_window", "key_env"}


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(path, value):
    with open(path, "w") as f:
        json.dump(value, f, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def resolve(config, run_out=None, run_id=None):
    """Read-only planning: dev metadata only, no sandbox/model/key access."""
    if set(config) != KEYS:
        raise ValueError("config has missing or unknown fields")
    fixed = {"version": "sac-dev-pilot-v1", "model": "deepseek-flash", "thinking": "disabled",
             "base_url": "https://api.deepseek.com", "key_env": "BOIDS_PARTNER_API_KEY"}
    for k, value in fixed.items():
        if config[k] != value:
            raise ValueError(f"{k} must be {value!r}")
    if config["arms"] != list(SAC_ARMS) or config["seeds"] != [1001]:
        raise ValueError("small launcher requires the four SAC arms and one paired seed [1001]")
    for k, lo, hi in (("n_agents", 3, 8), ("n_rounds", 2, 3), ("k", 2, 2),
                      ("menu_size", 8, 8), ("dev_seed", 0, 0), ("eval_tasks_per_depth", 1, 2),
                      ("solver_attempts", 1, 2), ("builder_max_tokens", 256, 4000),
                      ("solver_max_tokens", 256, 1500), ("max_input_bytes", 2000, 16000),
                      ("max_http_attempts_per_call", 1, 2), ("max_http_requests", 1, 180),
                      ("alignment_window", 3, 3)):
        if type(config[k]) is not int or not lo <= config[k] <= hi:
            raise ValueError(f"{k} must be an integer in [{lo}, {hi}]")
    for k, lo, hi in (("temperature", 0.7, 0.7), ("max_reserved_usd", 0.01, 2.0),
                      ("input_usd_per_million", 0.30, 0.30), ("output_usd_per_million", 1.20, 1.20),
                      ("tool_timeout_s", 5.0, 5.0), ("separation_threshold", 0.3, 0.3)):
        if type(config[k]) not in (int, float) or not lo <= config[k] <= hi:
            raise ValueError(f"{k} outside this reviewed pilot's range")
    RunConfig(arm="000", seed=1001, n_agents=config["n_agents"], n_rounds=config["n_rounds"], k=config["k"])
    env = MechEnv(DEFAULT_ENV, config["dev_seed"])
    dev = env.dev_tasks()
    selected = [t for d in (1, 2, 3) for t in [t for t in dev if t["depth"] == d][:config["eval_tasks_per_depth"]]]
    build = 4 * config["n_agents"] * config["n_rounds"]
    solve = 4 * len(selected) * config["solver_attempts"]
    if config["max_http_requests"] < build + solve:
        raise ValueError("HTTP cap is smaller than the nominal build+solver calls")
    scope = None
    if run_out is not None:
        run_id = str(uuid.UUID(run_id)) if run_id else str(uuid.uuid4())
        scope = {"run_id": run_id, "output_dir": str(Path(run_out).resolve())}
    return {"config": json.loads(json.dumps(config)), "split": "dev", "test_unsealed": False,
            "run_scope": scope, "sandbox_hash_seed": 0, "probe_state": "clean_fork_per_probe",
            "study_status": "engineering_diagnostic_not_scientific_evidence",
            "builder_dev_tasks": len(dev), "dev_task_seal": env.m.seal_hash([t["obj"] for t in dev]),
            "eval_task_ids": [t["id"] for t in selected],
            "builder_calls": build, "solver_calls": solve, "nominal_model_calls": build + solve,
            "code_sha256": code_hash(DEFAULT_ENV),
            "requirements_sha256": hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()}


def approval_template(resolved):
    return {"status": "PENDING_HUMAN_REVIEW", "approved": False, "reviewed_by": "",
            "credential_owner": "collaborator", "review_sha256": digest(resolved),
            "note": "Change only after the user explicitly approves this exact config and source. No credentials here."}


def verify_approval(resolved, approval, allow_spend, out=None):
    if not allow_spend:
        raise PermissionError("execution needs explicit --allow-spend and human approval")
    if (approval.get("approved") is not True or approval.get("status") != "APPROVED"
            or not approval.get("reviewed_by") or approval.get("credential_owner") != "collaborator"):
        raise PermissionError("pending human review; no model client or key was loaded")
    if approval.get("review_sha256") != digest(resolved):
        raise PermissionError("config/source changed since approval; request a new review")
    if out is not None:
        scope = resolved.get("run_scope") or {}
        if not scope.get("run_id") or scope.get("output_dir") != str(Path(out).resolve()):
            raise PermissionError("approval is bound to one run id and exact output directory")
        current = resolve(resolved["config"], out, scope["run_id"])
        if current != resolved:
            raise PermissionError("live source/dependencies differ from the reviewed configuration")


class Budget:
    """Reserve pessimistic cost before EVERY HTTP request, including retries.

The reserve is not refunded; unobservable timed-out usage is not called zero.
Input UTF-8 bytes + 512 framing tokens is a conservative token estimate, not
a provider billing guarantee. Request count is a hard local cap.
"""
    def __init__(self, config, ledger):
        self.config, self.ledger = config, Path(ledger)
        self.requests, self.reserved, self.reported_usd = 0, 0.0, 0.0
        self.reported_responses = 0

    def append(self, row):
        with self.ledger.open("a") as f:
            f.write(canonical(row) + "\n")

    def before(self, system, user, max_tokens, attempt):
        cfg = self.config
        size = len((system + user).encode("utf-8"))
        if size > cfg["max_input_bytes"]:
            raise ValueError("input exceeds the reviewed byte cap; do not silently truncate")
        estimate = ((size + 512) * cfg["input_usd_per_million"] + max_tokens * cfg["output_usd_per_million"]) / 1e6
        if self.requests >= cfg["max_http_requests"] or self.reserved + estimate > cfg["max_reserved_usd"]:
            raise PermissionError("reviewed request/cost budget exhausted; no further request sent")
        self.requests += 1
        self.reserved += estimate
        self.append({"event": "request_reserved", "request": self.requests, "retry_index": attempt,
                     "input_bytes": size, "output_token_cap": max_tokens,
                     "reserved_usd_cumulative": self.reserved})

    def after(self, tin, tout, cached, metadata):
        # Report conservative uncached-rate cost; do not assume cache hits are free.
        usd = (tin * self.config["input_usd_per_million"] + tout * self.config["output_usd_per_million"]) / 1e6
        self.reported_usd += usd
        self.reported_responses += 1
        self.append({"event": "response_usage", "request": self.requests, "tokens_in": tin,
                     "tokens_out": tout, "cached_tokens": cached, "metadata": metadata,
                     "usage_cost_at_uncached_rate_usd": usd})
        if self.reported_usd > self.config["max_reserved_usd"]:
            raise PermissionError("reported provider usage exceeded reserve assumptions; stop for review")


def execute(resolved, approval, out, allow_spend):
    verify_approval(resolved, approval, allow_spend, out)
    from .sandbox import isolation_level
    iso = isolation_level()
    if not iso.startswith("os-"):
        raise PermissionError("real generated tools need Linux OS isolation; do not disable the sandbox")
    deps = {name: importlib.metadata.version(name) for name in ("scikit-learn", "openai", "httpx", "numpy", "scipy")}
    if deps != {"scikit-learn": "1.5.2", "openai": "1.51.0", "httpx": "0.27.2",
                "numpy": "2.0.2", "scipy": "1.13.1"}:
        raise ValueError("install the pinned requirements before execution")
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    # Atomic and persistent even if a failed run directory is later removed.
    # No credentials or model client exist before this single-use claim.
    claim = out.parent / ("." + out.name + "." + resolved["run_scope"]["run_id"] + ".consumed")
    with claim.open("x") as f:
        f.write(digest(resolved) + "\n")
    out.mkdir(exist_ok=False)
    c = resolved["config"]
    budget = Budget(c, out / "request_ledger.jsonl")
    write_json(out / "reviewed_config.json", resolved)
    write_json(out / "approval.json", {k: approval[k] for k in ("status", "approved", "reviewed_by", "credential_owner", "review_sha256")})
    from .model import OpenAICompatModel
    from .society import Society
    from .utility import score_society
    results, pooled = [], []
    try:
        model = OpenAICompatModel(c["model"], c["key_env"], True, base_url=c["base_url"],
                                  thinking=c["thinking"], max_attempts=c["max_http_attempts_per_call"],
                                  before_request=budget.before, after_response=budget.after)
        env = MechEnv(DEFAULT_ENV, c["dev_seed"])
        # Fixed balanced alternating order, not sorted by hypothesized benefit.
        for arm in ("000", "111", "100", "011"):
            cfg = RunConfig(arm=arm, seed=1001, n_agents=c["n_agents"], n_rounds=c["n_rounds"],
                            k=c["k"], menu_size=c["menu_size"], model=c["model"], temperature=c["temperature"],
                            max_tokens_per_call=c["builder_max_tokens"], dry_run=False,
                            separation_threshold=c["separation_threshold"], alignment_window=c["alignment_window"],
                            tool_timeout_s=c["tool_timeout_s"], code_sha256=resolved["code_sha256"],
                            extra={"max_input_bytes": c["max_input_bytes"]})
            soc = out / f"ENG_{arm}_s1001"
            soc.mkdir()
            manifest = cfg.to_dict() | {"engineering": True, "protocol": "sac-dev-pilot-v1",
                                       "env_sha256": env.file_sha256, "dev_seed": c["dev_seed"],
                                       "sampling": model.sampling(), "transport": model.transport_policy(),
                                       "sandbox_isolation": iso, "dependencies": deps,
                                       "sandbox_hash_seed": 0, "probe_state": "clean_fork_per_probe",
                                       "python_version": platform.python_version(), "platform": platform.platform(),
                                       "review_sha256": digest(resolved)}
            write_json(soc / "run_manifest.json", manifest)
            summary = Society(cfg, env, model, str(soc)).run()
            if summary["truncated"] or summary["records"] != c["n_agents"] * c["n_rounds"]:
                raise RuntimeError("incomplete society: stop, do not score as a full run")
            scored = score_society(str(soc), env, model, attempts=c["solver_attempts"], split="dev",
                                   task_ids=resolved["eval_task_ids"], max_tokens=c["solver_max_tokens"])
            pooled.extend(scored.pop("_dev_task_scores"))
            results.append({"arm": arm, "build": summary, "solver": scored})
        report = {"status": "COMPLETE_DEV_DIAGNOSTIC", "results": results,
                  "pooled_U_dev_diagnostic": sum(pooled) / len(pooled),
                  "http_requests": budget.requests, "reported_responses": budget.reported_responses,
                  "cost_reserved_usd": budget.reserved, "cost_reported_at_uncached_rate_usd": budget.reported_usd,
                  "test_unsealed": False, "inference": "One society per arm cannot support a reliable generalizable effect or significance claim."}
        write_json(out / "pilot_summary.json", report)
        return report
    except (Exception, SystemExit, KeyboardInterrupt) as exc:
        # Never persist str(exc): SDK/proxy errors may contain credentials.
        write_json(out / "FAILED.json", {"status": "INCOMPLETE_NOT_SCORED_AS_ZERO",
                    "error_type": type(exc).__name__, "http_status": getattr(exc, "status_code", None),
                    "http_requests": budget.requests, "reserved_usd": budget.reserved,
                    "completed_arms": [r["arm"] for r in results]})
        raise RuntimeError(f"pilot stopped ({type(exc).__name__}); inspect sanitized FAILED.json") from None


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default=str(DEFAULT_CONFIG))
    p.add_argument("--out", required=True, help="fresh review directory (default) or fresh run directory (--execute)")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--approval")
    p.add_argument("--run-out", help="prepare: exact future run directory bound to this single-use approval")
    p.add_argument("--review", help="execute: prepared resolved_config.json; rechecked against live source")
    p.add_argument("--allow-spend", action="store_true")
    a = p.parse_args(argv)
    if not a.execute:
        if a.allow_spend or a.approval or a.review or not a.run_out:
            p.error("prepare requires --run-out; never accepts --allow-spend, --approval or --review")
        resolved = resolve(read_json(a.config), a.run_out)
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=False)
        write_json(out / "resolved_config.json", resolved)
        write_json(out / "approval.template.json", approval_template(resolved))
        print(f"PREPARED ONLY: {resolved['nominal_model_calls']} nominal model calls; pending human review; zero requests sent.")
        return
    if not a.approval or not a.review or a.run_out:
        p.error("--execute needs --review and --approval, and does not accept --run-out")
    resolved = read_json(a.review)
    if resolved["config"] != read_json(a.config):
        p.error("--config differs from reviewed config")
    report = execute(resolved, read_json(a.approval), a.out, a.allow_spend)
    print(json.dumps({"status": report["status"], "http_requests": report["http_requests"], "out": a.out}))


if __name__ == "__main__":
    main()
