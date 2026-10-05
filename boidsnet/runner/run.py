"""CLI: run one society.

    python -m boidsnet.runner.run --arm L0 --seed 3 --out runs/          # dry run, stub model
    python -m boidsnet.runner.run --arm L0 --seed 3 --out runs/ \
        --model gpt-4o-mini --key-env OPENAI_API_KEY --allow-spend --frozen FROZEN.json

A paid run requires --allow-spend AND a freeze file whose code hash matches the
current source tree; otherwise it refuses.  The key is read from the named
environment variable and is never written anywhere.
"""
import argparse
import json
import os
import sys

DEFAULT_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "env", "mechenv.py")

from .config import RunConfig, ARMS, SAC_ARMS
from .env_adapter import MechEnv
from .freeze import code_hash
from .model import StubModel, OpenAICompatModel
from .society import Society


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--arm", required=True, choices=ARMS)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="stub")
    p.add_argument("--key-env", default="OPENAI_API_KEY")
    p.add_argument("--base-url", default=None)
    p.add_argument("--azure-endpoint", default=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                   help="Azure resource endpoint; --model is then the deployment name")
    p.add_argument("--azure-api-version", default=os.environ.get("AZURE_OPENAI_API_VERSION"))
    p.add_argument("--no-temperature", action="store_true",
                   help="do not send temperature (reasoning deployments)")
    p.add_argument("--token-param", default="max_tokens", choices=("max_tokens", "max_completion_tokens"))
    p.add_argument("--param-mode", default="strict", choices=("strict", "auto"),
                   help="strict: refuse if the deployment rejects a parameter; auto: adapt once and record it")
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--allow-spend", action="store_true")
    p.add_argument("--frozen", default=None, help="freeze manifest (required for paid runs)")
    p.add_argument("--engineering", action="store_true",
                   help="pre-freeze ENGINEERING smoke (protocol v0.3.10 §8, a logged deviation): "
                        "real model without --frozen; run dir ENG_<arm>_s<seed>; dev split only")
    p.add_argument("--n-agents", type=int, default=8)
    p.add_argument("--n-rounds", type=int, default=10)
    p.add_argument("--token-budget", type=int, default=None)
    p.add_argument("--env-path", default=DEFAULT_ENV)
    p.add_argument("--dev-seed", type=int, default=0)
    a = p.parse_args(argv)
    if a.arm in SAC_ARMS and a.model != "stub":
        sys.exit("paid SAC runs must use boidsnet.runner.sac_pilot with a reviewed approval file")

    dry = a.model == "stub"
    env = MechEnv(a.env_path, a.dev_seed)
    chash = code_hash(a.env_path)
    protocol_sha = ""
    if a.engineering and a.frozen:
        sys.exit("--engineering and --frozen are mutually exclusive")
    if not dry and not a.engineering:
        if not a.frozen:
            sys.exit("refusing paid run: no --frozen manifest")
        with open(a.frozen) as f:
            frozen = json.load(f)
        if frozen["code_sha256"] != chash:
            sys.exit("refusing paid run: runner code differs from frozen hash")
        protocol_sha = frozen["protocol_sha256"]

    from .sandbox import isolation_level, PROBE_REPORT
    iso = isolation_level()
    if not dry and not iso.startswith("os-"):
        sys.exit(f"refusing real-model run: sandbox isolation is {iso!r}; generated tool code could reach "
                 "the model key (msg #102). Needs Linux namespaces (unshare) + setpriv.")
    cfg = RunConfig(arm=a.arm, seed=a.seed, n_agents=a.n_agents, n_rounds=a.n_rounds,
                    model=a.model, token_budget=a.token_budget, dry_run=dry,
                    temperature=(None if a.no_temperature else a.temperature),
                    code_sha256=chash, protocol_sha256=protocol_sha)
    out = os.path.join(a.out, ("ENG_" if a.engineering else "") + f"{cfg.arm}_s{cfg.seed:02d}")
    if os.path.exists(out):
        sys.exit(f"refusing to overwrite existing run dir {out}")
    os.makedirs(out)
    model = (StubModel(cfg.seed, env) if dry else
             OpenAICompatModel(a.model, a.key_env, a.allow_spend, a.base_url,
                               a.azure_endpoint, a.azure_api_version,
                               send_temperature=not a.no_temperature, token_param=a.token_param,
                               param_mode=a.param_mode))
    manifest = cfg.to_dict() | {"backend": ("azure" if (not dry and a.azure_endpoint) else
                                            "openai_compat" if not dry else "stub"),
                                "azure_api_version": a.azure_api_version if a.azure_endpoint else None,
                                "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
                                "env": env.name, "env_sha256": env.file_sha256,
                                "dev_seed": a.dev_seed, "model_client": type(model).__name__,
                                "engineering": bool(a.engineering),
                                "deviation": ("pre-freeze engineering smoke, protocol v0.3.10 §8; "
                                              "not a confirmatory or pilot society") if a.engineering else None,
                                "param_mode": a.param_mode, "sandbox_isolation": iso,
                                "sandbox_probe": PROBE_REPORT,
                                "transport": model.transport_policy() if hasattr(model, "transport_policy") else None}
    with open(os.path.join(out, "run_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    try:
        summary = Society(cfg, env, model, out).run()
    except Exception as e:  # noqa: BLE001 - any crash marks the society FAILED
        with open(os.path.join(out, "FAILED.json"), "w") as f:
            json.dump({"error_type": type(e).__name__, "error": str(e)[:300]}, f, indent=1)
        print(json.dumps({"out": out, "status": "FAILED", "error_type": type(e).__name__}))
        sys.exit(3)
    adaptations = getattr(model, "param_adaptations", [])
    manifest["sampling"] = {"temperature_sent": getattr(model, "send_temperature", None),
                            "token_param": getattr(model, "token_param", None),
                            "param_adaptations": adaptations}
    with open(os.path.join(out, "run_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(json.dumps({"out": out, "status": "OK", **summary}, indent=1))


if __name__ == "__main__":
    main()
