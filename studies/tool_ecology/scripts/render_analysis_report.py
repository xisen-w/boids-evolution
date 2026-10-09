"""Render the authored Chinese Markdown analysis as a portable TeX document."""

import argparse
import re
from pathlib import Path


def escape(text):
    mapping = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(mapping.get(c, c) for c in text)


def inline(text, root, source):
    parts = re.split(r"(\*\*.*?\*\*|\[[^\]]+\]\([^)]+\))", text)
    output = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            output.append(r"\textbf{" + escape(part[2:-2]) + "}")
        elif re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part):
            match = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
            label, target = match.groups()
            if not target.startswith("https://"):
                relative = (source.parent / target).resolve().relative_to(root.resolve())
                target = "https://github.com/xisen-w/boids-evolution/blob/codex/tool-ecology-dynamics/" + str(
                    relative
                )
            output.append(r"\href{" + target + "}{" + escape(label) + "}")
        else:
            output.append(escape(part))
    return "".join(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    lines = args.source.read_text().splitlines()
    body = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# "):
            title = escape(line[2:])
        elif line.startswith("## "):
            heading = re.sub(r"^\d+\.\s*", "", line[3:])
            if any(s.startswith("|") for s in lines[i + 1 : i + 5]):
                body.append(r"\Needspace{18\baselineskip}")
            body.append(r"\section{" + escape(heading) + "}")
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            alt, target = match.groups()
            target = str(Path(target).with_suffix(".pdf"))
            body.append(
                r"\begin{figure}[H]\centering\includegraphics[width=\textwidth]{"
                + target
                + r"}\caption{"
                + escape(alt)
                + r"}\end{figure}"
            )
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[-:| ]+\|$", lines[i]):
                    rows.append([s.strip() for s in lines[i].strip("|").split("|")])
                i += 1
            i -= 1
            tab = [
                r"\begin{center}\small\resizebox{\textwidth}{!}{\begin{tabular}{"
                + "l" * len(rows[0])
                + r"}\toprule"
            ]
            for j, row in enumerate(rows):
                colors = {"局部中性": "NeutralBlue", "局部 Boids": "BoidsOrange", "独立": "IndependentGray"}
                values = [
                    r"\textcolor{" + colors[v] + "}{" + escape(v) + "}" if v in colors else escape(v)
                    for v in row
                ]
                tab.append(" & ".join(values) + r" \\")
                if j == 0:
                    tab.append(r"\midrule")
            tab.append(r"\bottomrule\end{tabular}}\end{center}")
            body.extend(tab)
        elif line:
            body.append(inline(line, args.repo, args.source) + "\n")
        i += 1
    preamble = r"""\documentclass[UTF8,fontset=none,11pt]{ctexart}
\usepackage[a4paper,margin=22mm]{geometry}
\usepackage{fontspec,graphicx,booktabs,xcolor,hyperref,fancyhdr,float,needspace}
\setCJKmainfont{Songti SC}\setCJKsansfont{Heiti SC}\setCJKmonofont{Heiti SC}
\setmainfont{Times New Roman}\setsansfont{Arial}\setmonofont{Menlo}
\definecolor{NeutralBlue}{HTML}{2878B5}\definecolor{BoidsOrange}{HTML}{D97932}
\definecolor{IndependentGray}{HTML}{737C86}\definecolor{TextInk}{HTML}{243544}
\hypersetup{colorlinks=true,linkcolor=NeutralBlue,urlcolor=NeutralBlue}
\ctexset{section={format=\Large\sffamily\bfseries\color{TextInk}}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Boids 工具生态：冻结数据分析}\fancyhead[R]{\small 2026-10-09}\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}\setlength{\parskip}{5pt}\linespread{1.18}
\setcounter{topnumber}{3}\renewcommand{\topfraction}{.9}\renewcommand{\textfraction}{.08}
\begin{document}
"""
    args.output.write_text(
        preamble
        + r"\title{"
        + title
        + r"}\author{现有数据分析工作稿}\date{2026年10月9日}\maketitle"
        + "\n"
        + "\n".join(body)
        + "\n\\end{document}\n"
    )
    print(args.output)


if __name__ == "__main__":
    main()
