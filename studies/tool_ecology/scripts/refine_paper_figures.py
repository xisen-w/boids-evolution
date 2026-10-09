"""Compact manuscript figures from archived CSVs; no tools or graders execute."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from scripts.plot_frozen_analysis import ARMS, COLOR, FAMILIES, INK, LABEL, MARKERS, SEEDS, read_csv, style

BLUE, PALE, LINE = "#002FA7", "#EEF2FC", "#CCD6EE"


def link(ax, start, end, color=BLUE, style="-|>", **kwargs):
    ax.add_patch(
        FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=8, color=color, lw=0.9, **kwargs)
    )


def card(ax, x, y, w, h, title, body, number=None, filled=False):
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=.012,rounding_size=.025",
            fc=BLUE if filled else "white",
            ec=BLUE if filled else LINE,
            lw=0.8,
        )
    )
    color = "white" if filled else INK
    if number:
        ax.text(x + 0.1, y + h - 0.14, number, color="white" if filled else BLUE, fontsize=7.5, weight="bold")
    ax.text(
        x + w / 2, y + h - 0.17, title, ha="center", va="center", fontsize=7.6, color=color, weight="bold"
    )
    ax.text(x + w / 2, y + 0.20, body, ha="center", va="center", fontsize=6.8, color=color, linespacing=1.4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("choose a fresh figure output directory")
    args.output.mkdir(parents=True)
    style()
    cells = read_csv(args.analysis / "societies.csv")
    rounds = read_csv(args.analysis / "rounds.csv")
    pubs = read_csv(args.analysis / "publications.csv")
    authors = read_csv(args.analysis / "authors.csv")
    links = read_csv(args.analysis / "author-links.csv")
    services = read_csv(args.analysis / "services.csv")
    contracts = []

    def save(fig, name, sources, claim, caveat):
        for ext in ("pdf", "svg", "png"):
            path = args.output / f"{name}.{ext}"
            fig.savefig(path, bbox_inches="tight", pad_inches=0.045, dpi=300)
            if ext == "svg":
                path.write_text("\n".join(s.rstrip() for s in path.read_text().splitlines()) + "\n")
        plt.close(fig)
        contracts.append(dict(name=name, sources=sources, claim=claim, caveat=caveat))

    fig, ax = plt.subplots(figsize=(7.25, 2.3))
    ax.set(xlim=(0, 10), ylim=(0, 3.0))
    ax.axis("off")
    ax.text(0.02, 2.87, "a  Tool-mediated communication", fontsize=9, weight="bold", color=BLUE)
    stages = [
        ("Observe", "Own history + local tools"),
        ("Build / revise", "Native package + adapters"),
        ("Publish + check", "Immutable version + DEV"),
        ("Adopt next round", "Tool + declared closure"),
    ]
    for i, (title, body) in enumerate(stages):
        x = 0.04 + i * 2.52
        card(ax, x, 1.97, 2.35, 0.65, title, body, str(i + 1), filled=i == 2)
        if i < 3:
            link(ax, (x + 2.37, 2.28), (x + 2.49, 2.28))
    ax.text(
        0.05,
        1.75,
        "Round boundary: fixed views  /  no same-round access  /  feedback visible next round",
        fontsize=6.8,
        color=INK,
    )
    ax.text(0.02, 1.45, "b  Four distinct evidential questions", fontsize=9, weight="bold", color=BLUE)
    levels = [
        ("Visibility", "Can another agent\naccess it?"),
        ("Correct adoption", "Does foreign code\nserve a correct request?"),
        ("Functional effect", "Can changing a return\nbreak correctness?"),
        ("Collective increment", "Does coverage exceed\none author's own history?"),
    ]
    for i, (title, body) in enumerate(levels):
        x = 0.04 + i * 2.52
        ax.add_patch(Rectangle((x, 0.53), 2.35, 0.65, fc=PALE, ec="none"))
        ax.text(x + 0.10, 1.0, title, fontsize=7.6, weight="bold", color=BLUE)
        ax.text(x + 0.10, 0.68, body, fontsize=6.65, color=INK)
    ax.text(
        0.05,
        0.18,
        "Limits to distinguish: unused imports  /  wrong outputs  /  available substitutes  /  redundant broad libraries",
        fontsize=6.8,
        color="#65758A",
    )
    save(
        fig,
        "fig01-tool-communication",
        [],
        "Separate the implemented exchange pipeline from four evidential questions.",
        "Schematic; the four observations are not equivalent and failure points are not all observed.",
    )

    fig, ax = plt.subplots(figsize=(7.25, 2.15))
    ax.set(xlim=(0, 10), ylim=(0, 3))
    ax.axis("off")
    for x, title in [(0.04, "LOCAL RULE"), (2.35, "TRANSLATION TO TOOLS"), (6.22, "READOUT / BOUNDARY")]:
        ax.text(x, 2.81, title, fontsize=7, weight="bold", color=BLUE)
    mapping = [
        (
            "S",
            "Separation",
            "Avoid redundant construction",
            "when a useful neighbor capability exists",
            "Breadth, duplication, sustained niches",
            "A hint cannot enforce complementarity",
        ),
        (
            "A",
            "Alignment",
            "Reuse verified useful interfaces",
            "when available from a neighbor",
            "Correct adoption and functional witnesses",
            "A passing dependency can have substitutes",
        ),
        (
            "C",
            "Cohesion",
            "Fit recurring needs and capabilities",
            "using the same local pre-round view",
            "Common-panel coverage and persistence",
            "The shared demand is externally specified",
        ),
    ]
    for i, (initial, title, t1, t2, r1, r2) in enumerate(mapping):
        y = 2.02 - i * 0.78
        ax.add_patch(
            FancyBboxPatch(
                (0.04, y), 1.92, 0.59, boxstyle="round,pad=.012,rounding_size=.025", fc=BLUE, ec="none"
            )
        )
        ax.text(0.24, y + 0.3, initial, fontsize=12, weight="bold", color="white", va="center")
        ax.text(0.65, y + 0.3, title, fontsize=8, weight="bold", color="white", va="center")
        for x, w in [(2.32, 3.5), (6.2, 3.72)]:
            ax.add_patch(Rectangle((x, y), w, 0.59, fc=PALE, ec="none"))
        ax.text(2.44, y + 0.38, t1, fontsize=7.5, weight="bold", color=INK)
        ax.text(2.44, y + 0.13, t2, fontsize=6.8, color=INK)
        ax.text(6.32, y + 0.38, r1, fontsize=7.1, weight="bold", color=BLUE)
        ax.text(6.32, y + 0.13, r2, fontsize=6.7, color=INK)
        link(ax, (2.02, y + 0.30), (2.27, y + 0.30))
        link(ax, (5.88, y + 0.30), (6.15, y + 0.30))
    ax.text(
        0.05,
        0.10,
        "Bundled prompt guidance: no physical steering equations, adaptive neighborhoods or separately identified rule effects.",
        fontsize=6.8,
        color="#65758A",
    )
    save(
        fig,
        "fig02-boids-mapping",
        [],
        "Map the three local concepts to implemented guidance and finite observable tests.",
        "Klein blue identifies conceptual diagrams, not a treatment condition.",
    )

    for ext in ("pdf", "svg", "png"):
        shutil.copy2(
            args.analysis / "figures" / f"fig03-main-results.{ext}", args.output / f"fig03-main-results.{ext}"
        )
    contracts.append(
        dict(
            name="fig03-main-results",
            sources=["societies.csv"],
            claim="All nine endpoints are retained unchanged.",
            caveat="Exact previous export; three societies per condition, no case-based intervals.",
        )
    )

    fig, axes = plt.subplots(2, 3, figsize=(7.25, 2.65))
    fig.subplots_adjust(left=0.075, right=0.995, bottom=0.15, top=0.86, wspace=0.19, hspace=0.28)
    for j, seed in enumerate(SEEDS):
        for arm in ARMS:
            rr = [r for r in rounds if r["seed"] == seed and r["condition"] == arm]
            for i, key in enumerate(["adoption_publications", "fresh_history_self_contained_six_authors"]):
                axes[i, j].plot(
                    [r["round"] for r in rr],
                    [r[key] for r in rr],
                    color=COLOR[arm],
                    marker="o",
                    ms=2.4,
                    lw=1.2,
                )
        for i in range(2):
            ax = axes[i, j]
            ax.set(xticks=range(1, 7), yticks=[0, 4, 8], ylim=(-0.35, 8.5))
            ax.grid(axis="y", alpha=0.13)
            ax.tick_params(labelsize=6.5, length=2)
            if j:
                ax.set_yticklabels([])
            if i == 0:
                ax.set_xticklabels([])
                ax.set_title(f"Seed {seed}", fontsize=8, pad=3)
            else:
                ax.set_xlabel("Round", fontsize=7, labelpad=2)
    axes[0, 0].set_ylabel("Adopting pubs\n(of 8)", fontsize=7, labelpad=3)
    axes[1, 0].set_ylabel("Own-six authors\n(of 8)", fontsize=7, labelpad=3)
    fig.legend(
        [Line2D([], [], color=COLOR[a], lw=2) for a in ARMS],
        [LABEL[a] for a in ARMS],
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.52, 1.03),
        fontsize=7,
    )
    save(
        fig,
        "fig04-dynamics",
        ["rounds.csv"],
        "Show all seed trajectories using the original separate score panels.",
        "Upper row original DEV; lower row archived common fresh panel. No rescoring.",
    )

    fig = plt.figure(figsize=(7.25, 3.8))
    outer = fig.add_gridspec(3, 3, left=0.025, right=0.995, top=0.92, bottom=0.075, wspace=0.16, hspace=0.24)
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 8, endpoint=False)
    positions = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    for i, seed in enumerate(SEEDS):
        for j, arm in enumerate(ARMS):
            inner = outer[i, j].subgridspec(1, 2, width_ratios=[0.9, 1.4], wspace=0.05)
            graph = fig.add_subplot(inner[0, 0])
            mat = fig.add_subplot(inner[0, 1])
            graph.set(xlim=(-1.4, 1.4), ylim=(-1.35, 1.35))
            graph.axis("off")
            ee = [r for r in links if r["seed"] == seed and r["condition"] == arm]
            for r in ee:
                a, b = int(r["provider"][1:]), int(r["caller"][1:])
                link(
                    graph,
                    positions[a],
                    positions[b],
                    color=COLOR[arm],
                    connectionstyle="arc3,rad=.12",
                    shrinkA=5,
                    shrinkB=5,
                    alpha=0.68,
                )
            for k, pos in enumerate(positions):
                graph.scatter(*pos, s=62, fc="white", ec=COLOR[arm], lw=0.65, zorder=3)
                graph.text(*pos, str(k), ha="center", va="center", fontsize=5.9, zorder=4)
            graph.text(
                0.5,
                -0.06,
                f"{len(ee)} pairs",
                transform=graph.transAxes,
                ha="center",
                fontsize=6.1,
                color=COLOR[arm],
            )
            matrix = np.full((8, 8), np.nan)
            rr = [r for r in pubs if r["seed"] == seed and r["condition"] == arm]
            for r in rr:
                matrix[int(r["author"][1:]), r["round"] - 1] = r["original_passing_families"]
            for r in authors:
                if r["seed"] == seed and r["condition"] == arm:
                    k = int(r["author"][1:])
                    matrix[k, 6:] = [
                        r["fresh_self_contained_history_families"],
                        r["fresh_served_history_families"],
                    ]
            cmap = LinearSegmentedColormap.from_list(arm, ["white", COLOR[arm]])
            mat.imshow(matrix, cmap=cmap, vmin=0, vmax=6, aspect="auto")
            for y in range(8):
                for x in range(8):
                    v = matrix[y, x]
                    mat.text(
                        x,
                        y,
                        "×" if np.isnan(v) else str(int(v)),
                        ha="center",
                        va="center",
                        fontsize=5.8,
                        color=INK if np.isnan(v) or v < 4 else "white",
                    )
            for r in rr:
                if r["declared_families"] == 1:
                    mat.add_patch(
                        Rectangle(
                            (r["round"] - 1.5, int(r["author"][1:]) - 0.5), 1, 1, fill=False, ec=INK, lw=0.8
                        )
                    )
            mat.axvline(5.5, color="white", lw=2)
            mat.set(
                xticks=range(8),
                xticklabels=[1, 2, 3, 4, 5, 6, "O", "S"],
                yticks=range(8),
                yticklabels=range(8),
            )
            mat.tick_params(length=0, labelsize=5.8, pad=1)
            for spine in mat.spines.values():
                spine.set_visible(False)
            if i == 0:
                mat.set_title(LABEL[arm], color=COLOR[arm], fontsize=7.5, pad=6)
            graph.text(
                -0.14,
                0.5,
                str(seed),
                transform=graph.transAxes,
                rotation=90,
                va="center",
                fontsize=6.6,
                weight="bold",
            )
    fig.text(
        0.5,
        0.005,
        "Rows: authors 0–7  /  Columns: rounds 1–6, O = own history, S = served history  /  × = no admitted package",
        ha="center",
        fontsize=6.6,
        color=INK,
    )
    save(
        fig,
        "fig05-society-atlas",
        ["publications.csv", "authors.csv", "author-links.csv"],
        "Retain all nine networks, all 432 opportunities and all 72 ownership profiles in one atlas.",
        "Round cells use original DEV; O/S use common fresh DEV. Author projections can be cyclic; fixed positions, unweighted edges; narrow declarations outlined.",
    )

    fig = plt.figure(figsize=(7.25, 3.15))
    gs = fig.add_gridspec(2, 3, left=0.065, right=0.98, bottom=0.15, top=0.91, hspace=0.78, wspace=0.43)
    for j, (key, title, scale) in enumerate(
        [
            ("root_ast_median", "a  Root AST median", 1),
            ("input_tokens", "b  Input (millions)", 1e-6),
            ("output_tokens", "c  Output (thousands)", 0.001),
        ]
    ):
        ax = fig.add_subplot(gs[0, j])
        for seed, mark, off in zip(SEEDS, MARKERS, [-0.1, 0, 0.1]):
            for x, arm in enumerate(ARMS):
                c = next(c for c in cells if c["seed"] == seed and c["condition"] == arm)
                ax.scatter(x + off, c[key] * scale, s=22, color=COLOR[arm], marker=mark)
        ax.set(xticks=range(3), xticklabels=["Neutral", "Boids", "Indep."])
        ax.tick_params(labelsize=6.3, length=2)
        ax.set_title(title, loc="left", fontsize=7.5, pad=3)
        ax.grid(axis="y", alpha=0.13)
        if j == 0:
            ax.set_yscale("log")
            ax.set_ylim(30, 1500)
        elif j == 1:
            ax.set_ylim(0, 1.3)
        else:
            ax.set_ylim(0, 85)
    ax = fig.add_subplot(gs[1, :2])
    w = 0.23
    for j, arm in enumerate(ARMS):
        rates = []
        for family in FAMILIES:
            rr = [r for r in services if r["condition"] == arm and r["family"] == family]
            rates.append(100 * (sum(r["cases"] - r["passed"] for r in rr)) / sum(r["cases"] for r in rr))
        ax.bar(np.arange(6) + (j - 1) * w, rates, width=w, color=COLOR[arm])
    ax.set(xticks=range(6), xticklabels=FAMILIES, ylim=(0, 24), ylabel="Failed cases (%)")
    ax.tick_params(labelsize=6.3, length=2)
    ax.set_title("d  Declared-service failures", loc="left", fontsize=7.5, pad=3)
    ax.grid(axis="y", alpha=0.13)
    ax = fig.add_subplot(gs[1, 2])
    fields = json.loads((args.analysis / "summary.json").read_text())["failed_field_sets"]
    counts = [fields[k] for k in ["region", "revenue_cents", "region + units", "units"]]
    ax.barh(range(4), counts, color=INK, height=0.6)
    ax.set(yticks=range(4), yticklabels=["region", "revenue", "region + units", "units"], xlim=(0, 1000))
    ax.invert_yaxis()
    ax.tick_params(labelsize=6.3, length=2)
    for y, v in enumerate(counts):
        ax.text(v + 10, y, str(v), va="center", fontsize=6.6)
    ax.set_title("e  Mismatched fields", loc="left", fontsize=7.5, pad=3)
    save(
        fig,
        "fig06-cost-reliability",
        ["societies.csv", "services.csv", "summary.json"],
        "Separate code size, model tokens and conditional output reliability.",
        "Root code excludes dependencies; input includes cache; field mismatch is not a universal cause. Seed shapes match endpoint figure.",
    )

    fig, ax = plt.subplots(figsize=(7.25, 1.05))
    ax.set(xlim=(0, 6), ylim=(0, 1))
    ax.axis("off")
    labels = [
        ("Own broad", "5 families pass"),
        ("Foreign lookup", "6/6 cases"),
        ("Own wrapper", "Foreign closure · 6/6"),
        ("Own lookup", "1/6 cases"),
        ("Foreign broad", "All six pass"),
        ("Foreign broad", "All six pass"),
    ]
    for i, (title, body) in enumerate(labels):
        color = "#B44B50" if i == 3 else COLOR["local-boids"]
        ax.add_patch(
            FancyBboxPatch(
                (i + 0.03, 0.28),
                0.88,
                0.58,
                boxstyle="round,pad=.009,rounding_size=.025",
                fc="#FBF0E6" if i in (1, 2, 3) else "#F3F5F7",
                ec=color,
                lw=0.75,
            )
        )
        ax.text(i + 0.47, 0.65, title, ha="center", fontsize=6.9, weight="bold", color=color)
        ax.text(i + 0.47, 0.43, body, ha="center", fontsize=6.1, color=INK)
        ax.text(i + 0.47, 0.09, f"Round {i + 1}", ha="center", fontsize=6.4)
        if i < 5:
            link(ax, (i + 0.93, 0.57), (i + 1.01, 0.57), color=INK)
    save(
        fig,
        "fig07-narrow-trajectory",
        ["publications.csv"],
        "Show the original six-round narrowing and re-expansion trajectory.",
        "Seed2026 Boids a00; existing isolated diagnostic is described in caption, never counted as an observed repaired role.",
    )
    used = {
        p: hashlib.sha256((args.analysis / p).read_bytes()).hexdigest()
        for p in [
            "societies.csv",
            "rounds.csv",
            "publications.csv",
            "authors.csv",
            "author-links.csv",
            "services.csv",
            "summary.json",
        ]
    }
    (args.output / "figure-contracts.json").write_text(
        json.dumps(
            dict(
                diagram_color=BLUE,
                condition_colors=COLOR,
                source_hashes=used,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                figures=contracts,
                experimental_model_calls=0,
                grader_calls=0,
                generated_tool_executions=0,
            ),
            indent=2,
        )
        + "\n"
    )
    print("Seven manuscript figures; all archived measurements unchanged")


if __name__ == "__main__":
    main()
