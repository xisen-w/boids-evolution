"""Run the confirmatory design: every arm x every pre-listed seed.

    python -m boidsnet.runner.batch --out runs/ --seeds 1001-1010 --jobs 6          # stub
    python -m boidsnet.runner.batch --out runs/ --seeds 1001-1010 --jobs 6 \
        --model <m> --key-env OPENAI_API_KEY --allow-spend --frozen FROZEN.json

Each society is a separate `python -m boidsnet.runner.run` process, so every society
uses exactly the code path the pilot tested.  The batch is resume-safe:
- a society whose directory holds summary.json is skipped;
- a society that FAILED (API outage, crash) is moved aside to
  <dir>.failed<k> (never deleted) and rerun ONCE with the same seed; a second
  failure is left for a human and reported;
- batch_status.json records every attempt, so reruns are visible in the
  paper's provenance.
Seeds are pre-listed on the command line and logged; the pilot seeds must not
overlap them.
"""
import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time

from .config import PROTOCOL_ARMS


def parse_seeds(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def society_dir(out, arm, seed):
    return os.path.join(out, f"{arm}_s{seed:02d}")


def run_one(out, arm, seed, passthrough, max_attempts=2):
    d = society_dir(out, arm, seed)
    attempts = []
    for k in range(1, max_attempts + 1):
        if os.path.exists(os.path.join(d, "summary.json")):
            return {"arm": arm, "seed": seed, "status": "OK", "attempts": attempts or ["skipped_existing"]}
        if os.path.exists(d):                       # partial or FAILED dir: keep it, move aside
            n = 1
            while os.path.exists(f"{d}.failed{n}"):
                n += 1
            os.rename(d, f"{d}.failed{n}")
            attempts.append(f"moved_aside:{os.path.basename(d)}.failed{n}")
        t0 = time.time()
        env = dict(os.environ, PYTHONHASHSEED="0")   # belt and braces; the run is hash-seed independent
        proc = subprocess.run([sys.executable, "-m", "boidsnet.runner.run", "--arm", arm, "--seed", str(seed),
                               "--out", out] + passthrough, capture_output=True, text=True, env=env,
                              cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        attempts.append({"attempt": k, "returncode": proc.returncode, "wall_s": round(time.time() - t0, 1),
                         "stderr_tail": proc.stderr.strip().splitlines()[-1:] if proc.returncode else []})
        if proc.returncode == 0 and os.path.exists(os.path.join(d, "summary.json")):
            return {"arm": arm, "seed": seed, "status": "OK", "attempts": attempts}
    return {"arm": arm, "seed": seed, "status": "FAILED", "attempts": attempts}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--seeds", required=True, help="pre-listed seeds, e.g. 1001-1010")
    p.add_argument("--arms", default=",".join(PROTOCOL_ARMS))
    p.add_argument("--jobs", type=int, default=4)
    a, passthrough = p.parse_known_args(argv)
    if "--engineering" in passthrough:
        sys.exit("batch runs confirmatory societies only; --engineering is for boidsnet.runner.smoke")
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    arms, seeds = a.arms.split(","), parse_seeds(a.seeds)
    jobs = [(arm, s) for s in seeds for arm in arms]     # interleave arms: no arm finishes first
    results = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run_one, out, arm, s, passthrough): (arm, s) for arm, s in jobs}
        for f in cf.as_completed(futs):
            results.append(f.result())
    results.sort(key=lambda r: (r["arm"], r["seed"]))
    status = {"arms": arms, "seeds": seeds, "passthrough": passthrough,
              "ok": sum(r["status"] == "OK" for r in results),
              "failed": [f'{r["arm"]}_s{r["seed"]}' for r in results if r["status"] != "OK"],
              "results": results}
    with open(os.path.join(out, "batch_status.json"), "w") as f:
        json.dump(status, f, indent=1)
    print(json.dumps({k: status[k] for k in ("ok", "failed")}, indent=1))
    sys.exit(0 if not status["failed"] else 4)


if __name__ == "__main__":
    main()
