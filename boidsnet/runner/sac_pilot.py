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
from decimal import Decimal
from pathlib import Path

from .config import RunConfig, SAC_ARMS
from .env_adapter import MechEnv
from .freeze import code_hash
from .mechanisms import canonical
from .run import DEFAULT_ENV
from .agentport_config import is_agentport, validate as validate_agentport, blockers, EXTRA_KEYS, USD_KEYS

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
    gateway = is_agentport(config)
    if set(config) != ((KEYS - USD_KEYS) | EXTRA_KEYS if gateway else KEYS):
        raise ValueError("config has missing or unknown fields")
    fixed = {"thinking": "disabled", "key_env": "BOIDS_PARTNER_API_KEY"}
    if gateway:
        validate_agentport(config)
    else:
        fixed.update(version="sac-dev-pilot-v1", model="deepseek-flash", base_url="https://api.deepseek.com")
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
    numeric = [("temperature", 0.7, 0.7), ("tool_timeout_s", 5.0, 5.0), ("separation_threshold", 0.3, 0.3)]
    if not gateway:
        numeric += [("max_reserved_usd", 0.01, 2.0), ("input_usd_per_million", 0.30, 0.30),
                    ("output_usd_per_million", 1.20, 1.20)]
    for k, lo, hi in numeric:
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
            "spend_blockers": blockers(config) if gateway else [],
            "run_scope": scope, "sandbox_hash_seed": 0, "probe_state": "clean_fork_per_probe",
            "study_status": "engineering_diagnostic_not_scientific_evidence",
            "builder_dev_tasks": len(dev), "dev_task_seal": env.m.seal_hash([t["obj"] for t in dev]),
            "eval_task_ids": [t["id"] for t in selected],
            "builder_calls": build, "solver_calls": solve, "nominal_model_calls": build + solve,
            "code_sha256": code_hash(DEFAULT_ENV),
            "requirements_sha256": hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()}


def approval_template(resolved):
    return {"status": "PENDING_HUMAN_REVIEW", "approved": False, "reviewed_by": "",
            "credential_owner": "user_provided" if is_agentport(resolved["config"]) else "collaborator", "review_sha256": digest(resolved),
            "note": "Change only after the user explicitly approves this exact config and source. No credentials here."}


def verify_approval(resolved, approval, allow_spend, out=None):
    if not allow_spend:
        raise PermissionError("execution needs explicit --allow-spend and human approval")
    if resolved.get("spend_blockers") or (is_agentport(resolved["config"]) and blockers(resolved["config"])):
        raise PermissionError("unresolved pricing, provider cap, model IDs or sandbox; no request permitted")
    owner = "user_provided" if is_agentport(resolved["config"]) else "collaborator"
    if (approval.get("approved") is not True or approval.get("status") != "APPROVED"
            or not approval.get("reviewed_by") or approval.get("credential_owner") != owner):
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
        self.currency = "CNY" if is_agentport(config) else "USD"
        if is_agentport(config) and blockers(config):
            raise PermissionError("unverified AgentPort pricing/limit/route cannot create a spend ledger")
        self.requests, self._reserved, self._reported = 0, Decimal(0), Decimal(0)
        self.reported_responses = 0
        self._stopped = False
        self._last_response_request = 0
        self._last_limits = None

    @property
    def reserved(self):
        return float(self._reserved)

    @property
    def reported_usd(self):
        # Legacy API compatibility; new reports use explicit currency fields.
        return float(self._reported)

    def rates(self):
        unit = self.currency.lower()
        return tuple(Decimal(str(self.config[k])) for k in (
            "input_" + unit + "_per_million", "output_" + unit + "_per_million", "max_reserved_" + unit))

    def receipt(self):
        return {"currency": self.currency, "cost_reserved": self.reserved,
                "cost_reported_at_uncached_rate": float(self._reported),
                "http_requests": self.requests, "reported_responses": self.reported_responses,
                "unreported_requests": self.requests - self.reported_responses}

    def append(self, row):
        # Preserve the existing v1 USD ledger schema; never put CNY amounts in
        # USD-named fields in the new gateway contract.
        row = dict(row)
        if self.currency == "USD" and row.get("event") == "request_reserved":
            row["reserved_usd_cumulative"] = row["reserved_cost_cumulative"]
        elif self.currency == "USD" and row.get("event") == "response_usage":
            row["usage_cost_at_uncached_rate_usd"] = row["usage_cost_at_uncached_rate"]
        with self.ledger.open("a") as f:
            f.write(canonical(row) + "\n")

    def before(self, system, user, max_tokens, attempt):
        cfg = self.config
        if self._stopped:
            raise PermissionError("accounting anomaly: review required before further requests")
        if type(max_tokens) is not int or max_tokens <= 0:
            raise ValueError("output cap must be a positive integer")
        size = len((system + user).encode("utf-8"))
        if size > cfg["max_input_bytes"]:
            raise ValueError("input exceeds the reviewed byte cap; do not silently truncate")
        rate_in, rate_out, limit = self.rates()
        estimate = ((size + 512) * rate_in + max_tokens * rate_out) / Decimal(1000000)
        if self.requests >= cfg["max_http_requests"] or self._reserved + estimate > limit:
            self._stopped = True
            raise PermissionError("reviewed request/cost budget exhausted; no further request sent")
        self.requests += 1
        self._reserved += estimate
        self._last_limits = (size + 512, max_tokens)
        self.append({"event": "request_reserved", "request": self.requests, "retry_index": attempt,
                     "input_bytes": size, "output_token_cap": max_tokens,
                     "currency": self.currency, "reserved_cost_cumulative": self.reserved,
                     "reserved_cost_exact": str(self._reserved)})

    def after(self, tin, tout, cached, metadata):
        from .model import validate_usage
        try:
            validate_usage(tin, tout, cached)
            if self.requests <= self._last_response_request:
                raise RuntimeError("usage without an unreported reserved request")
        except RuntimeError:
            self._stopped = True
            raise
        # Report conservative uncached-rate cost; do not assume cache hits are free.
        rate_in, rate_out, limit = self.rates()
        cost = (tin * rate_in + tout * rate_out) / Decimal(1000000)
        self._reported += cost
        self.reported_responses += 1
        self._last_response_request = self.requests
        self.append({"event": "response_usage", "request": self.requests, "tokens_in": tin,
                     "tokens_out": tout, "cached_tokens": cached, "metadata": metadata,
                     "currency": self.currency, "usage_cost_at_uncached_rate": float(cost),
                     "usage_cost_exact": str(cost)})
        if (self._reported > limit
                or tin > self._last_limits[0] or tout > self._last_limits[1]):
            self._stopped = True
            raise PermissionError("reported provider usage exceeded reserve assumptions; stop for review")


def execute(resolved, approval, out, allow_spend):
    verify_approval(resolved, approval, allow_spend, out)
    from .sandbox import isolation_level, PROBE_REPORT
    iso = isolation_level()
    if not iso.startswith("os-"):
        raise PermissionError("real generated tools need Linux OS isolation; do not disable the sandbox")
    gateway = is_agentport(resolved["config"])
    if gateway and (iso != "os-docker" or PROBE_REPORT.get("probe", {}).get("image_id") != resolved["config"]["sandbox_image_id"]):
        raise PermissionError("AgentPort smoke requires the reviewed Docker image and verified isolation")
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
        strict = {"accepted_response_models": c["accepted_response_models"],
                  "request_timeout_s": c["request_timeout_s"]} if gateway else {}
        model = OpenAICompatModel(c["model"], c["key_env"], True, base_url=c["base_url"],
                                  thinking=c["thinking"], max_attempts=c["max_http_attempts_per_call"],
                                  before_request=budget.before, after_response=budget.after, **strict)
        env = MechEnv(DEFAULT_ENV, c["dev_seed"])
        # Fixed balanced alternating order, not sorted by hypothesized benefit.
        for arm in ("000", "111", "100", "011"):
            cfg = RunConfig(arm=arm, seed=1001, n_agents=c["n_agents"], n_rounds=c["n_rounds"],
                            k=c["k"], menu_size=c["menu_size"], model=c["model"], temperature=c["temperature"],
                            max_tokens_per_call=c["builder_max_tokens"], dry_run=False,
                            separation_threshold=c["separation_threshold"], alignment_window=c["alignment_window"],
                            tool_timeout_s=c["tool_timeout_s"], code_sha256=resolved["code_sha256"],
                            extra={"max_input_bytes": c["max_input_bytes"], "stop_on_smoke_anomaly": gateway})
            soc = out / f"ENG_{arm}_s1001"
            soc.mkdir()
            manifest = cfg.to_dict() | {"engineering": True, "protocol": c["version"],
                                       "env_sha256": env.file_sha256, "dev_seed": c["dev_seed"],
                                       "sampling": model.sampling(), "transport": model.transport_policy(),
                                       "sandbox_isolation": iso, "dependencies": deps,
                                       "sandbox_receipt": PROBE_REPORT,
                                       "sandbox_hash_seed": 0, "probe_state": "clean_fork_per_probe",
                                       "python_version": platform.python_version(), "platform": platform.platform(),
                                       "review_sha256": digest(resolved)}
            write_json(soc / "run_manifest.json", manifest)
            summary = Society(cfg, env, model, str(soc)).run()
            if summary["truncated"] or summary["records"] != c["n_agents"] * c["n_rounds"]:
                raise RuntimeError("incomplete society: stop, do not score as a full run")
            scored = score_society(str(soc), env, model, attempts=c["solver_attempts"], split="dev",
                                   task_ids=resolved["eval_task_ids"], max_tokens=c["solver_max_tokens"],
                                   stop_on_smoke_anomaly=gateway)
            pooled.extend(scored.pop("_dev_task_scores"))
            results.append({"arm": arm, "build": summary, "solver": scored})
        report = {"status": "COMPLETE_DEV_DIAGNOSTIC", "results": results,
                  "pooled_U_dev_diagnostic": sum(pooled) / len(pooled),
                  "http_requests": budget.requests, "reported_responses": budget.reported_responses,
                  "budget": budget.receipt(),
                  "test_unsealed": False, "inference": "One society per arm cannot support a reliable generalizable effect or significance claim."}
        if not gateway:
            report.update(cost_reserved_usd=budget.reserved,
                          cost_reported_at_uncached_rate_usd=budget.reported_usd)
        write_json(out / "pilot_summary.json", report)
        return report
    except (Exception, SystemExit, KeyboardInterrupt) as exc:
        # Never persist str(exc): SDK/proxy errors may contain credentials.
        failure = {"status": "INCOMPLETE_NOT_SCORED_AS_ZERO",
                    "error_type": type(exc).__name__, "http_status": getattr(exc, "status_code", None),
                    "stop_reason": getattr(exc, "reason", None), "budget": budget.receipt(),
                    "http_requests": budget.requests, "completed_arms": [r["arm"] for r in results]}
        if not gateway:
            failure["reserved_usd"] = budget.reserved
        write_json(out / "FAILED.json", failure)
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
        if resolved["spend_blockers"]:
            print("SPENDING BLOCKED: " + "; ".join(resolved["spend_blockers"]))
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
