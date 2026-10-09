"""Compare served and self-contained author history on the common fresh panel."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ARMS = ("local-neutral", "local-boids", "independent")
LABELS = ("Local neutral", "Local Boids", "Independent")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("summary", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier provenance figures")
    rows = json.loads(args.summary.read_text())
    cells = {(r["seed"], r["condition"]): r for r in rows}
    if len(rows) != 9 or set(cells) != {(s, a) for s in (71, 108, 2026) for a in ARMS}:
        raise ValueError("need the complete nine-cell common panel")
    args.output.mkdir(parents=True)
    plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "svg.fonttype": "none"})
    fig, axes = plt.subplots(3, 3, figsize=(11.4, 5.9), layout="constrained")
    authors = [f"a{i:02d}" for i in range(8)]
    for i, seed in enumerate((71, 108, 2026)):
        for j, arm in enumerate(ARMS):
            r = cells[(seed, arm)]
            matrix = [
                [len(r["self_contained_author_profiles"][a]) for a in authors],
                [len(r["author_profiles"][a]) for a in authors],
            ]
            ax = axes[i, j]
            image = ax.imshow(matrix, vmin=0, vmax=6, cmap="viridis", aspect="auto")
            ax.set_title(
                f"{LABELS[j]} · seed {seed} · self-contained six: {matrix[0].count(6)}/8", fontsize=9
            )
            ax.set_xticks(range(8), authors, fontsize=8)
            ax.set_yticks([0, 1], ["Self-contained\nhistory", "Served with\ndependencies"], fontsize=8)
            for y, values in enumerate(matrix):
                for x, value in enumerate(values):
                    ax.text(
                        x,
                        y,
                        str(value),
                        ha="center",
                        va="center",
                        fontsize=9,
                        color="white" if value < 3 else "#17252B",
                    )
    fig.colorbar(
        image, ax=axes.ravel().tolist(), label="Passing service families (0–6)", ticks=range(7), shrink=0.8
    )
    fig.suptitle("Common fresh DEV panel: served breadth and self-contained author history", fontsize=11)
    fig.supxlabel(
        "Author; self-contained means the entire declared closure belongs to this author", fontsize=9
    )
    for ext in ("png", "svg", "pdf"):
        fig.savefig(args.output / f"author-dependency-provenance.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)
    (args.output / "figure-manifest.json").write_text(
        json.dumps(
            dict(
                classification="descriptive_common_panel_dependency_provenance",
                summary_sha256=hashlib.sha256(args.summary.read_bytes()).hexdigest(),
                analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                caveat="Profiles are unions over published history, not current-package breadth, original authorship, independent understanding or assigned roles.",
                model_calls=0,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
