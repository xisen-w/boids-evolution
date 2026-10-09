"""Scientific diagnostic figures from a completed, archived exploratory batch."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORS = {"local-neutral": "#2878B5", "local-boids": "#E07A2D", "independent": "#656565"}
LABELS = {"local-neutral": "Local neutral", "local-boids": "Local Boids", "independent": "Independent"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    societies = []
    for root in sorted(args.evidence.glob("seed-*/*")):
        if (root / "records.json").exists():
            societies.append(
                (
                    root,
                    json.loads((root / "config.json").read_text()),
                    json.loads((root / "records.json").read_text()),
                    json.loads((root / "round-metrics.json").read_text()),
                )
            )
    if not societies:
        raise ValueError("no archived societies")
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.1), layout="constrained")
    series = defaultdict(list)
    for root, cfg, records, rounds in societies:
        xs = [r["round"] for r in rounds]
        ys = [
            [len(r["verified_family_coverage"]) for r in rounds],
            [r["mean_author_profile_jaccard"] or 0 for r in rounds],
            [sum(r.get("correct_cross_author_requests", 0) for r in records if r["round"] == i) for i in xs],
        ]
        for ax, y in zip(axes, ys):
            ax.plot(xs, y, color=COLORS[root.name], alpha=0.28, lw=1)
        for j, y in enumerate(ys):
            series[(root.name, j)].append(y)
    for (arm, j), rows in series.items():
        mean = np.mean(rows, axis=0)
        axes[j].plot(range(1, len(mean) + 1), mean, color=COLORS[arm], lw=2.1, label=LABELS[arm])
    for ax, title, ylabel in zip(
        axes,
        [
            "Verified ecosystem coverage",
            "Cumulative capability overlap",
            "Correct cross-author service calls",
        ],
        ["Families covered (of 6)", "Mean author-profile Jaccard", "Correct requests this round"],
    ):
        ax.set_title(title)
        ax.set_xlabel("Round")
        ax.set_ylabel(ylabel)
        ax.set_xticks(xs)
        ax.grid(axis="y", alpha=0.15)
    axes[0].set_ylim(-0.15, 6.3)
    axes[1].set_ylim(-0.03, 1.05)
    axes[2].set_ylim(bottom=-0.5)
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle(
        "Role-free tool ecology: thin lines are societies; thick lines are condition means", fontsize=10
    )
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.output / f"ecology-trajectories.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)
    seeds = sorted({cfg["seed"] for _, cfg, _, _ in societies})
    arms = [a for a in COLORS if any(root.name == a for root, _, _, _ in societies)]
    fig, axes = plt.subplots(
        len(seeds),
        len(arms),
        figsize=(3.3 * len(arms), 2.2 * len(seeds)),
        squeeze=False,
        layout="constrained",
    )
    image = None
    for root, cfg, records, _ in societies:
        ax = axes[seeds.index(cfg["seed"]), arms.index(root.name)]
        matrix = np.full((cfg["agents"], cfg["rounds"]), np.nan)
        for row in records:
            matrix[int(row["author"][1:]), row["round"] - 1] = len(row["verified_families"])
        image = ax.imshow(matrix, vmin=0, vmax=6, cmap="viridis", aspect="auto")
        ax.set_title(f'{LABELS[root.name]} · seed {cfg["seed"]}', fontsize=9)
        ax.set_xticks(range(cfg["rounds"]), range(1, cfg["rounds"] + 1))
        ax.set_xlabel("Round")
        ax.set_yticks(range(cfg["agents"]), [f"a{i:02d}" for i in range(cfg["agents"])])
        ax.set_ylabel("Author")
        for i in range(cfg["agents"]):
            for j in range(cfg["rounds"]):
                if not np.isnan(matrix[i, j]):
                    ax.text(
                        j,
                        i,
                        str(int(matrix[i, j])),
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white" if matrix[i, j] < 3 else "#18252B",
                    )
    fig.colorbar(
        image,
        ax=axes.ravel().tolist(),
        label="Passing families (0–6)",
        shrink=0.7,
        ticks=range(7),
    )
    fig.suptitle(
        "Narrow contributions and generalists: published capability breadth over rounds", fontsize=10
    )
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.output / f"author-round-capabilities.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
