"""Publication figures from existing sanitized tables only. No execution studies."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ARMS = ("local-neutral", "local-boids", "independent")
LABEL = {"local-neutral": "Local neutral", "local-boids": "Local Boids", "independent": "Independent"}
COLOR = {"local-neutral": "#2878B5", "local-boids": "#D97932", "independent": "#737C86"}
INK, LIGHT, ERROR = "#243544", "#F3F5F7", "#B44B50"
SEEDS, MARKERS = (71, 108, 2026), ("o", "s", "^")
FAMILIES = ("clean", "revenue", "group", "monthly", "lookup", "window")


def read_csv(path):
    rows = list(csv.DictReader(path.open()))
    for row in rows:
        for key, value in row.items():
            if value in ("True", "False"):
                row[key] = value == "True"
            else:
                try:
                    row[key] = float(value) if "." in value else int(value)
                except ValueError:
                    pass
    return rows


def style():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )


def panel(ax, letter, title):
    ax.set_title(title, loc="left", pad=10)
    ax.text(-0.13, 1.075, letter, transform=ax.transAxes, weight="bold", fontsize=11)


def legend(fig, y=1.02):
    fig.legend(
        [Line2D([], [], color=COLOR[a], lw=2.5) for a in ARMS],
        [LABEL[a] for a in ARMS],
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, y),
    )


def box(ax, xy, width, height, text, color=INK, face=LIGHT, size=8):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=.025",
        edgecolor=color,
        facecolor=face,
        lw=0.8,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color=color,
        linespacing=1.5,
    )


def arrow(ax, start, end, color=INK, rad=0, lw=1):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=9,
            connectionstyle=f"arc3,rad={rad}",
            color=color,
            lw=lw,
        )
    )


def main():
    p = argparse.ArgumentParser()
    p.add_argument("analysis", type=Path)
    p.add_argument("--collection", type=Path, required=True)
    args = p.parse_args()
    dest = args.analysis / "figures"
    if dest.exists():
        raise ValueError("preserve existing figures")
    dest.mkdir()
    style()
    cells = read_csv(args.analysis / "societies.csv")
    rounds = read_csv(args.analysis / "rounds.csv")
    pubs = read_csv(args.analysis / "publications.csv")
    authors = read_csv(args.analysis / "authors.csv")
    services = read_csv(args.analysis / "services.csv")
    links = read_csv(args.analysis / "author-links.csv")
    manifests = []

    def save(fig, name, claim, tables, caveat):
        for ext in ("svg", "pdf", "png"):
            path = dest / f"{name}.{ext}"
            fig.savefig(path, dpi=280, bbox_inches="tight", pad_inches=0.08)
            if ext == "svg":
                path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
        plt.close(fig)
        manifests.append(
            dict(
                name=name,
                claim=claim,
                source_tables=tables,
                caveat=caveat,
                replicate_unit="society; three per condition",
                model_calls=0,
                grader_calls=0,
            )
        )

    # Figure 1: implementation and evidence; node colors keep method identities fixed.
    fig, ax = plt.subplots(figsize=(7.25, 3.9))
    ax.set(xlim=(0, 10), ylim=(0, 5))
    ax.axis("off")
    ax.text(0.05, 4.7, "a  Communication through immutable executable tools", fontsize=11, weight="bold")
    titles = [
        "Local pre-round view\nOwn history + neighbors",
        "Agent builds / repairs\nNative Python package",
        "Publish + verify\nVersion + DEV feedback",
        "Next-round adoption\nCode + declared closure",
    ]
    for i, title in enumerate(titles):
        box(ax, (0.1 + 2.5 * i, 3.25), 2.2, 0.92, title)
        if i < 3:
            arrow(ax, (2.33 + 2.5 * i, 3.7), (2.56 + 2.5 * i, 3.7))
    ax.text(
        0.1,
        2.95,
        "All views fixed before a round; no same-round access; feedback arrives next round.",
        fontsize=8,
    )
    ax.text(0.05, 2.52, "b  What each observation establishes", fontsize=11, weight="bold")
    for i, (title, desc) in enumerate(
        [
            ("Visible", "Artifact available\nNo execution evidence"),
            ("Executed correctly", "Foreign code reached\nPassing case"),
            ("Functional witness", "Return changed\nCorrect case fails"),
            ("Collective advantage", "Group adds capability\nBeyond own history"),
        ]
    ):
        box(ax, (0.1 + 2.5 * i, 1.16), 2.2, 1.04, title + "\n\n" + desc, size=7)
    ax.text(
        0.1,
        0.78,
        "Failure points to distinguish: output mismatch · unused imports · transient narrowing · redundant full libraries",
        fontsize=8,
    )
    ax.text(
        0.1,
        0.3,
        "Current study measures the stages separately; successful reuse does not by itself establish complementary division of labour.",
        fontsize=8,
    )
    save(
        fig,
        "fig01-tool-communication",
        "Tools separate visibility, execution, functional contribution and collective coverage.",
        [],
        "Schematic of the implemented protocol, not additional observations.",
    )

    fig, ax = plt.subplots(figsize=(7.25, 3.8))
    ax.set(xlim=(0, 10), ylim=(0, 4.7))
    ax.axis("off")
    ax.text(
        0.1,
        4.42,
        "Boids supplies local policy concepts; their cognitive consequences must be measured",
        fontsize=10,
        weight="bold",
    )
    headers = ["Physical concept", "Implemented guidance", "Observed quantity / limitation"]
    for x, text in zip([0.25, 3.05, 6.4], headers):
        ax.text(x, 3.98, text, weight="bold", fontsize=8)
    rows = [
        (
            "S · Separation",
            "Avoid redundant construction\nwhen a useful neighbor exists",
            "Breadth, duplication, sustained niches\nGuidance cannot enforce complementarity",
        ),
        (
            "A · Alignment",
            "Reuse verified useful\nneighbor interfaces",
            "Correct adoption + return interventions\nA passing tool need not be indispensable",
        ),
        (
            "C · Cohesion",
            "Fit recurring service needs\nand recent neighbor capabilities",
            "Common-panel coverage and persistence\nShared demand is externally specified",
        ),
    ]
    for i, texts in enumerate(rows):
        y = 2.95 - i * 1.1
        for x, w, text in zip([0.1, 2.9, 6.1], [2.5, 2.9, 3.8], texts):
            box(ax, (x, y), w, 0.85, text, COLOR["local-boids"], "#FBF0E6", 7.5)
        arrow(ax, (2.65, y + 0.43), (2.87, y + 0.43), COLOR["local-boids"])
        arrow(ax, (5.85, y + 0.43), (6.07, y + 0.43), COLOR["local-boids"])
    ax.text(
        0.1,
        0.18,
        "Three rules are bundled in one prompt condition. No force equations, adaptive neighborhoods or individual-rule effects are identified.",
        fontsize=7.5,
    )
    save(
        fig,
        "fig02-boids-mapping",
        "The implemented triad is prompt guidance, with distinct measurable targets and limits.",
        [],
        "This figure describes v0.3.1; it does not show the earlier global-catalogue TF-IDF pilot.",
    )

    # Main endpoint comparison: every society shown, no interval from case counts.
    fig, axes = plt.subplots(1, 3, figsize=(7.25, 2.7), layout="constrained")
    specs = [
        (
            "post_round_one_adoption_rate",
            100,
            "Correct adoption",
            "% of admitted publications, rounds 2–6",
            (-2, 65),
        ),
        (
            "self_contained_six_authors",
            1,
            "Own-author capability",
            "Authors covering all six (of 8)",
            (0, 8.6),
        ),
        (
            "history_coverage_gap",
            1,
            "Final collective increment",
            "Families beyond best own-author history",
            (-0.2, 1.1),
        ),
    ]
    for j, (key, scale, title, ylabel, ylim) in enumerate(specs):
        ax = axes[j]
        panel(ax, "abc"[j], title)
        for s, marker, offset in zip(SEEDS, MARKERS, [-0.11, 0, 0.11]):
            yy = [
                next(r[key] for r in cells if r["seed"] == s and r["condition"] == arm) * scale
                for arm in ARMS
            ]
            ax.plot([0 + offset, 1 + offset], yy[:2], color="#CAD0D6", lw=0.8, zorder=1)
            for x, arm, y in zip(range(3), ARMS, yy):
                ax.scatter(
                    x + offset, y, color=COLOR[arm], marker=marker, s=36, edgecolors="white", lw=0.5, zorder=3
                )
        ax.set(xticks=range(3), xticklabels=["Neutral", "Boids", "Independent"], ylabel=ylabel, ylim=ylim)
        ax.grid(axis="y", alpha=0.16)
        if j == 1:
            ax.set_yticks([0, 2, 4, 6, 8])
        if j == 2:
            ax.set_yticks([0, 1])
    fig.legend(
        [Line2D([], [], marker=m, color=INK, lw=0, markersize=5) for m in MARKERS],
        [f"Seed {s}" for s in SEEDS],
        ncol=3,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.12),
    )
    save(
        fig,
        "fig03-main-results",
        "More publications adopt foreign tools, while final additional family coverage is zero.",
        ["societies.csv"],
        "Points are societies, not cases. Three seeds per condition; lines join workload/topology seed matches. History is a union of versions.",
    )

    fig, axes = plt.subplots(2, 3, figsize=(7.25, 4.6), layout="constrained")
    for j, seed in enumerate(SEEDS):
        for arm in ARMS:
            rows = [r for r in rounds if r["seed"] == seed and r["condition"] == arm]
            axes[0, j].plot(
                [r["round"] for r in rows],
                [r["adoption_publications"] for r in rows],
                color=COLOR[arm],
                marker="o",
                ms=3,
                lw=1.6,
            )
            axes[1, j].plot(
                [r["round"] for r in rows],
                [r["fresh_history_self_contained_six_authors"] for r in rows],
                color=COLOR[arm],
                marker="o",
                ms=3,
                lw=1.6,
            )
        for i in range(2):
            axes[i, j].set(xticks=range(1, 7), ylim=(-0.3, 8.4), yticks=[0, 2, 4, 6, 8], xlabel="Round")
            axes[i, j].grid(axis="y", alpha=0.16)
            panel(axes[i, j], "abcdef"[i * 3 + j], f"Seed {seed}")
    axes[0, 0].set_ylabel("Adopting publications this round (of 8)")
    axes[1, 0].set_ylabel("Self-contained six-family authors (of 8)")
    legend(fig, 1.09)
    save(
        fig,
        "fig04-dynamics",
        "Adoption and self-contained histories develop differently in the three seed matches.",
        ["rounds.csv"],
        "Top row uses original round-specific DEV checks; bottom uses already archived common fresh panel. No averages hide seed trajectories.",
    )

    fig, axes = plt.subplots(3, 3, figsize=(7.25, 4.4), layout="constrained")
    for i, seed in enumerate(SEEDS):
        for j, arm in enumerate(ARMS):
            ax = axes[i, j]
            rows = [r for r in authors if r["seed"] == seed and r["condition"] == arm]
            values = np.array(
                [
                    [r["fresh_self_contained_history_families"] for r in rows],
                    [r["fresh_served_history_families"] for r in rows],
                ]
            )
            cmap = LinearSegmentedColormap.from_list(arm, ["#FFFFFF", COLOR[arm]])
            ax.imshow(values, cmap=cmap, vmin=0, vmax=6, aspect="auto")
            for y in range(2):
                for x in range(8):
                    ax.text(
                        x,
                        y,
                        str(values[y, x]),
                        ha="center",
                        va="center",
                        fontsize=7,
                        color="white" if values[y, x] >= 4 else INK,
                    )
            ax.set(
                xticks=range(8),
                xticklabels=[str(x) for x in range(8)],
                yticks=[0, 1],
                yticklabels=["Own history", "With deps"],
                xlabel="Author index",
            )
            ax.tick_params(length=0)
            ax.set_title(f"{LABEL[arm]} · {seed}", color=COLOR[arm], fontsize=8)
    fig.text(
        0.5,
        1.025,
        "Common fresh panel · passing families per author (0–6); equal numbers use equal saturation",
        ha="center",
        fontsize=8,
    )
    save(
        fig,
        "fig05-author-provenance",
        "Dependence supplements some author histories without adding collective categories.",
        ["authors.csv"],
        "Own history requires an entirely same-author declared closure. It is not a measure of originality or understanding.",
    )

    fig, axes = plt.subplots(1, 3, figsize=(7.25, 2.7), layout="constrained")
    for j, (key, title, ylabel, scale) in enumerate(
        [
            ("root_ast_median", "Published root code", "Median AST nodes per society", 1),
            ("input_tokens", "Context consumption", "Input tokens per society (millions)", 1e-6),
            ("output_tokens", "Generated tokens", "Output tokens per society (thousands)", 0.001),
        ]
    ):
        ax = axes[j]
        panel(ax, "abc"[j], title)
        for seed, marker, offset in zip(SEEDS, MARKERS, [-0.1, 0, 0.1]):
            for x, arm in enumerate(ARMS):
                value = next(r[key] for r in cells if r["seed"] == seed and r["condition"] == arm) * scale
                ax.scatter(x + offset, value, s=33, color=COLOR[arm], marker=marker)
        ax.set(xticks=range(3), xticklabels=["Neutral", "Boids", "Independent"], ylabel=ylabel)
        if j == 0:
            ax.set_yscale("log")
            ax.set_ylim(30, 1500)
        elif j == 1:
            ax.set_ylim(0, 1.3)
        else:
            ax.set_ylim(0, 85)
        ax.grid(axis="y", alpha=0.16)
    save(
        fig,
        "fig06-code-and-budget",
        "Short root packages do not imply proportionally lower total context or token use.",
        ["societies.csv"],
        "AST size is static root size, excludes dependencies and is not effort or computational complexity. Input includes cached tokens; money is unverified.",
    )

    fig, axes = plt.subplots(
        1, 2, figsize=(7.25, 2.8), gridspec_kw={"width_ratios": [1.35, 1]}, layout="constrained"
    )
    panel(axes[0], "a", "Failures among declared service cases")
    width = 0.23
    for j, arm in enumerate(ARMS):
        yy = []
        for family in FAMILIES:
            rows = [r for r in services if r["condition"] == arm and r["family"] == family]
            total, passed = sum(r["cases"] for r in rows), sum(r["passed"] for r in rows)
            yy.append(100 * (total - passed) / total)
        axes[0].bar(np.arange(6) + (j - 1) * width, yy, width=width, color=COLOR[arm], label=LABEL[arm])
    axes[0].set(xticks=range(6), xticklabels=FAMILIES, ylabel="Failed cases (%)", ylim=(0, 24))
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].grid(axis="y", alpha=0.16)
    axes[0].legend(fontsize=6.5)
    panel(axes[1], "b", "Where failed outputs differ")
    fields = json.loads((args.analysis / "summary.json").read_text())["failed_field_sets"]
    labels = ["region only", "revenue only", "region + units", "units only"]
    counts = [fields["region"], fields["revenue_cents"], fields["region + units"], fields["units"]]
    axes[1].barh(range(4), counts, color=[INK, "#92A3AF", "#B2BEC7", "#CBD3D9"], height=0.6)
    for y, value in enumerate(counts):
        axes[1].text(value + 10, y, str(value), va="center", fontsize=8)
    axes[1].set(yticks=range(4), yticklabels=labels, xlabel="Failed declared cases", xlim=(0, 960))
    axes[1].invert_yaxis()
    save(
        fig,
        "fig07-reliability",
        "Observed failures concentrate in output contracts rather than providing a single cause for rule effects.",
        ["services.csv", "summary.json"],
        "Cases are correlated, declaration-conditioned and not independent replicates. A mismatched field is not automatically a common code cause.",
    )

    fig, ax = plt.subplots(figsize=(7.25, 2.85))
    ax.set(xlim=(0.3, 6.7), ylim=(0, 3.4))
    ax.axis("off")
    ax.text(
        0.45,
        3.08,
        "Seed 2026 · Local Boids · a00: a narrow interface did appear, but did not persist reliably",
        weight="bold",
        fontsize=9,
    )
    labels = [
        "Six services\nOwn code\n5 families pass",
        "Lookup only\nForeign provider\n6/6 cases",
        "Lookup only\nOwn wrapper,\nforeign closure\n6/6 cases",
        "Lookup only\nOwn rewrite\n1/6 cases",
        "Six services\nForeign exports\nAll six pass",
        "Six services\nForeign exports\nAll six pass",
    ]
    for i, text in enumerate(labels):
        x = i + 0.55
        narrow = i in [1, 2, 3]
        color = ERROR if i == 3 else COLOR["local-boids"]
        box(ax, (x, 1.38), 0.84, 1.24, text, color, "#FBF0E6" if narrow else LIGHT, 7)
        ax.text(x + 0.42, 1.15, f"Round {i + 1}", ha="center", fontsize=7)
        if i < 5:
            arrow(ax, (x + 0.87, 2), (x + 0.99, 2))
    ax.text(
        0.5,
        0.68,
        "Existing isolated diagnosis: normalized region was computed but not written back to the output row.",
        fontsize=8,
    )
    ax.text(
        0.5,
        0.28,
        "The archived one-line diagnostic changed 1/6 to 6/6; it never changes original scores or counts as a sustained original role.",
        fontsize=7.5,
    )
    save(
        fig,
        "fig08-narrowing",
        "Transient narrow declarations must be separated from sustained independent expertise.",
        ["publications.csv"],
        "Selected because this is the only three-round same-author narrow declaration sequence; existing repair evidence only, no new execution.",
    )

    fig, axes = plt.subplots(3, 3, figsize=(7.25, 6.2), layout="constrained")
    angles = np.linspace(np.pi / 2, np.pi / 2 + 2 * np.pi, 8, endpoint=False)
    positions = np.stack([np.cos(angles), np.sin(angles)], axis=1)
    for i, seed in enumerate(SEEDS):
        for j, arm in enumerate(ARMS):
            ax = axes[i, j]
            ax.set(xlim=(-1.43, 1.43), ylim=(-1.37, 1.37))
            ax.axis("off")
            edge_rows = [r for r in links if r["seed"] == seed and r["condition"] == arm]
            for row in edge_rows:
                a, b = int(row["provider"][1:]), int(row["caller"][1:])
                patch = FancyArrowPatch(
                    positions[a],
                    positions[b],
                    arrowstyle="-|>",
                    mutation_scale=7,
                    color=COLOR[arm],
                    alpha=0.65,
                    linewidth=0.9,
                    connectionstyle="arc3,rad=.1",
                    shrinkA=12,
                    shrinkB=12,
                )
                ax.add_patch(patch)
            for k, pos in enumerate(positions):
                ax.scatter(*pos, s=200, color="white", edgecolors=COLOR[arm], lw=1.2, zorder=3)
                ax.text(*pos, f"{k:02d}", ha="center", va="center", fontsize=7, zorder=4)
            ax.set_title(
                f"{LABEL[arm]} · {seed}\n{len(edge_rows)} observed author pairs", color=COLOR[arm], fontsize=8
            )
    fig.text(
        0.5,
        1.01,
        "All nine societies · provider → caller; fixed author positions and unweighted unique directed pairs",
        ha="center",
        fontsize=8,
    )
    save(
        fig,
        "fig09-author-networks",
        "The dependency structure involves more authors in Boids societies, with all seed graphs disclosed.",
        ["author-links.csv"],
        "Edges collapse versioned correct-execution pairs. This author projection may contain cycles although the version graph is acyclic; not the social ring.",
    )

    fig, axes = plt.subplots(3, 3, figsize=(7.25, 6.0), layout="constrained")
    for i, seed in enumerate(SEEDS):
        for j, arm in enumerate(ARMS):
            ax = axes[i, j]
            matrix = np.full((8, 6), np.nan)
            rows = [r for r in pubs if r["seed"] == seed and r["condition"] == arm]
            for r in rows:
                matrix[int(r["author"][1:]), r["round"] - 1] = r["original_passing_families"]
            cmap = LinearSegmentedColormap.from_list(arm, ["#FFFFFF", COLOR[arm]])
            ax.imshow(matrix, cmap=cmap, vmin=0, vmax=6, aspect="auto")
            for y in range(8):
                for x in range(6):
                    value = matrix[y, x]
                    ax.text(
                        x,
                        y,
                        "×" if np.isnan(value) else str(int(value)),
                        ha="center",
                        va="center",
                        fontsize=6.5,
                        color=INK if np.isnan(value) or value < 4 else "white",
                    )
            for r in rows:
                if r["declared_families"] == 1:
                    ax.add_patch(
                        Rectangle(
                            (r["round"] - 1.5, int(r["author"][1:]) - 0.5),
                            1,
                            1,
                            fill=False,
                            edgecolor=INK,
                            lw=1.1,
                        )
                    )
            ax.set(
                xticks=range(6),
                xticklabels=range(1, 7),
                yticks=range(8),
                yticklabels=range(8),
                xlabel="Round",
                ylabel="Author",
            )
            ax.tick_params(length=0)
            ax.set_title(f"{LABEL[arm]} · {seed}", color=COLOR[arm], fontsize=8)
    fig.text(
        0.5,
        1.01,
        "Original per-round DEV · passing declared families (0–6); × = no admitted publication; outline = lookup-only",
        ha="center",
        fontsize=8,
    )
    save(
        fig,
        "fig10-publication-breadth",
        "Broad service offerings dominate every condition; four narrow declarations remain visible.",
        ["publications.csv"],
        "Zero denotes an admitted publication with no fully passing family. A cross denotes skip or contract rejection; neither is missing data.",
    )

    (dest / "figure-contracts.json").write_text(
        json.dumps(
            dict(
                palette=COLOR,
                font="Arial with Helvetica/DejaVu Sans fallbacks",
                width_inches=7.25,
                formats=["editable SVG", "TrueType PDF", "280 dpi PNG preview"],
                error_bars="none; all three society replicates or their descriptive aggregates are shown",
                figures=manifests,
                plotting_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                model_calls=0,
                grader_calls=0,
            ),
            indent=2,
        )
        + "\n"
    )
    print(f"Wrote {len(manifests)} figures in PNG/SVG/PDF")


if __name__ == "__main__":
    main()
