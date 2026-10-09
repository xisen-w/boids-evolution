"""Versioned cross-author execution graphs; no inference or security claims."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def cross_request_pairs(details):
    pairs = defaultdict(Counter)
    for case in details:
        if not case["correct"]:
            continue
        hit = set()
        for edge in case["executed_edges"]:
            match = re.fullmatch(r"published\.(a\d{2}_r\d+)(?:\.[^.]+)*->published\.(a\d{2}_r\d+)\..+", edge)
            if match and match[1].split("_")[0] != match[2].split("_")[0]:
                hit.add((match[1], match[2]))
        for pair in hit:
            pairs[pair][case["family"]] += 1
    return {pair: dict(counts) for pair, counts in pairs.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replay-root", type=Path)
    parser.add_argument("--note", default="Exploratory role-free tool ecology")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("preserve earlier graph output")
    if not (args.run / "COMPLETE.json").exists():
        raise ValueError("only completed batches are plotted")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    args.output.mkdir(parents=True)
    plt.rcParams.update({"font.size": 9, "pdf.fonttype": 42, "svg.fonttype": "none"})
    for root in sorted(args.run.glob("seed-*/*")):
        if not (root / "records.json").exists():
            continue
        records = json.loads((root / "records.json").read_text())
        cfg = json.loads((root / "config.json").read_text())
        pair_counts = defaultdict(Counter)
        for row in records:
            if row["publication_status"] != "published":
                continue
            if args.replay_root:
                file = (
                    args.replay_root / root.relative_to(args.run) / "raw-grades" / row["id"] / "result.json"
                )
            else:
                file = root / "builders" / row["author"] / f"round-{row['round']:02d}" / "service/result.json"
            for pair, counts in cross_request_pairs(json.loads(file.read_text())["details"]).items():
                pair_counts[pair].update(counts)
        dest = args.output / root.parent.name / root.name
        dest.mkdir(parents=True)
        (dest / "graph.json").write_text(
            json.dumps(
                dict(
                    classification="observational_correct_request_execution_pairs",
                    orientation="executed provider -> actual caller or requested service-entry publication",
                    caveat="Weights count repeated service cases, not independent adoptions or causal effects. Nodes show served breadth including dependencies.",
                    edges=[
                        dict(caller=a, provider=b, correct_request_family_counts=dict(counts))
                        for (a, b), counts in sorted(pair_counts.items())
                    ],
                ),
                indent=2,
            )
        )
        fig, ax = plt.subplots(figsize=(9, 4.6), layout="constrained")
        for caller, provider in pair_counts:

            def position(identity):
                author, rnd = identity.split("_r")
                return int(rnd), int(author[1:])

            arrow = FancyArrowPatch(
                position(provider),
                position(caller),
                arrowstyle="-|>",
                mutation_scale=8,
                linewidth=0.8,
                alpha=0.4,
                color="#C35829",
                connectionstyle="arc3,rad=0.10",
                shrinkA=10,
                shrinkB=10,
            )
            ax.add_patch(arrow)
        published = [r for r in records if r["publication_status"] == "published"]
        points = ax.scatter(
            [r["round"] for r in published],
            [int(r["author"][1:]) for r in published],
            c=[len(r["verified_families"]) for r in published],
            cmap="viridis",
            vmin=0,
            vmax=6,
            s=170,
            edgecolor="white",
            linewidth=0.7,
            zorder=3,
        )
        for row in records:
            x, y = row["round"], int(row["author"][1:])
            if row["publication_status"] != "published":
                ax.scatter([x], [y], marker="x", color="#777777", s=90, zorder=4)
            else:
                breadth = len(row["verified_families"])
                ax.text(
                    x,
                    y,
                    str(breadth),
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if breadth < 3 else "#13242C",
                    zorder=4,
                )
        ax.set(
            xlim=(0.6, cfg["rounds"] + 0.4),
            ylim=(cfg["agents"] - 0.5, -0.5),
            xticks=range(1, cfg["rounds"] + 1),
            yticks=range(cfg["agents"]),
            yticklabels=[f"a{i:02d}" for i in range(cfg["agents"])],
            xlabel="Publication round",
            ylabel="Publication author",
        )
        ax.set_title(f"{args.note}\n{root.name} · {root.parent.name} · provider → adopter execution edges")
        ax.grid(alpha=0.1)
        fig.colorbar(
            points,
            ax=ax,
            label="Passing service families (includes dependencies)",
            ticks=range(7),
            shrink=0.8,
        )
        fig.text(
            0.5,
            -0.06,
            "Arrows require a correct executed request; repeated paths are collapsed. × = skip or rejected publication.",
            ha="center",
            fontsize=8,
        )
        for ext in ("png", "svg", "pdf"):
            fig.savefig(dest / f"execution-graph.{ext}", dpi=220, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
