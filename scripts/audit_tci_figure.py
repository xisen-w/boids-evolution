"""Section 2.1 audit figure: published cumulative TCI vs per-round mean TCI of new tools.

Input is a per-tool extract of the archived legacy corpus (the 33 run directories are not in
this repo). One CSV row per tool per run:

    domain,arm,run_id,dup_group,round,is_seed,tci

- domain: "data_science" or "literature"
- arm: condition label as in the published tables (e.g. baseline_4.1, alignment_4.1)
- run_id: run directory, relative to the corpus root
- dup_group: empty, or a label shared by byte-identical run directories (each group is drawn once)
- round: round the tool was counted in (1-15); seed tools use the round they first enter the mean
- is_seed: 1 for system seed tools, 0 for agent-created tools
- tci: the TCI value stored for the tool (0-10)

The published series is the cumulative mean TCI over every counted tool (seeds included), which
reproduces the legacy headline figure. The corrected series is the mean TCI of tools created in that
round, seeds excluded. No CIs and no tests: the figure is descriptive.

Usage: python scripts/audit_tci_figure.py extract.csv out.png
Deterministic: same CSV -> same PNG bytes (fixed metadata, Agg backend).
"""
import csv
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DOMAINS = [("data_science", "Data science"), ("literature", "Literature")]
ROUNDS = range(1, 16)


def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "domain": r["domain"], "arm": r["arm"], "run_id": r["run_id"],
                "dup_group": r.get("dup_group") or "", "round": int(r["round"]),
                "is_seed": r["is_seed"].strip() in ("1", "true", "True"),
                "tci": float(r["tci"]),
            })
    return rows


def dedupe(rows):
    """Keep one run per dup_group (lexicographically first run_id). Returns rows, n_dirs, n_groups."""
    runs = sorted({(r["dup_group"], r["run_id"]) for r in rows})
    keep, seen = set(), set()
    for g, run in runs:
        if g and g in seen:
            continue
        seen.add(g)
        keep.add(run)
    n_dirs = len({r["run_id"] for r in rows})
    n_groups = len({r["dup_group"] for r in rows if r["dup_group"]})
    return [r for r in rows if r["run_id"] in keep], n_dirs, n_groups


def series(run_rows):
    """(published cumulative mean incl. seeds, per-round mean of new non-seed tools) per round."""
    by_round = defaultdict(list)
    for r in run_rows:
        by_round[r["round"]].append(r)
    pub, new, cum = [], [], []
    for t in ROUNDS:
        cum += [r["tci"] for r in by_round[t]]
        pub.append(sum(cum) / len(cum) if cum else float("nan"))
        fresh = [r["tci"] for r in by_round[t] if not r["is_seed"]]
        new.append(sum(fresh) / len(fresh) if fresh else float("nan"))
    return pub, new


def nanmean(cols):
    out = []
    for vals in zip(*cols):
        v = [x for x in vals if x == x]
        out.append(sum(v) / len(v) if v else float("nan"))
    return out


def plot(rows, out):
    rows, n_dirs, n_groups = dedupe(rows)
    arms = sorted({r["arm"] for r in rows})
    colors = {a: plt.get_cmap("tab10")(i) for i, a in enumerate(arms)}
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
    xs = list(ROUNDS)
    for ax, (dom, title) in zip(axes, DOMAINS):
        for arm in arms:
            runs = sorted({r["run_id"] for r in rows if r["domain"] == dom and r["arm"] == arm})
            if not runs:
                continue
            pubs, news = [], []
            for run in runs:
                p, n = series([r for r in rows if r["run_id"] == run])
                pubs.append(p)
                news.append(n)
                ax.plot(xs, n, color=colors[arm], lw=0.4, alpha=0.35)
            ax.plot(xs, nanmean(pubs), color=colors[arm], lw=1.4, ls="--")
            ax.plot(xs, nanmean(news), color=colors[arm], lw=1.4, label=f"{arm} (n={len(runs)})")
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Round", fontsize=8)
        ax.set_xticks([1, 5, 10, 15])
        ax.tick_params(labelsize=7)
        ax.legend(fontsize=6, frameon=False)
    axes[0].set_ylabel("TCI (0-10)", fontsize=8)
    fig.text(0.5, -0.02, f"Dashed: published cumulative mean (seeds included). Solid: mean of tools "
             f"created that round (seeds excluded); thin lines are runs. {n_dirs} run dirs, "
             f"{n_groups} duplicate groups shown once.", ha="center", fontsize=6)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight", metadata={"Software": None})


if __name__ == "__main__":
    plot(load(sys.argv[1]), sys.argv[2])
