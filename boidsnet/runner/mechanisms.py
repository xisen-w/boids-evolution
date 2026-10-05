"""S/A/C v1: select shared evidence first, then render instruction-only toggles.

No behavioral hashes or held-out data enter these selectors. TCI is a static
complexity heuristic, NOT correctness; adoption counts static importers, NOT
successful reuse. Both caveats are represented in the evidence.
"""
import ast
import hashlib
import json
from collections import Counter

from .config import SAC_ARMS
from .exposure import ring_neighbours

GUIDANCE = {
    "S": (
        "These selected neighbour tools and their similarity metadata are provided for reference. Decide what tool to build.",
        "YOUR GOAL: Ensure your tool offers a DISTINCT function. Do not rebuild a tool that performs these core tasks. Find a new, complementary niche."),
    "A": (
        "These recent neighbour exemplars and their recorded metadata are provided for reference. Decide what tool to build.",
        "Consider these recent neighbour exemplars. Reuse useful design principles such as modularity, composition, and robustness in your own tool. If an exemplar is marked as a fallback that has not passed its declared target, do not assume it is reliable."),
    "C": (
        "These counts describe the previous round's declared activity. They are provided for reference. Decide what tool to build.",
        "YOUR GOAL: Contribute to this emerging trend. How can your tool serve this broader goal?"),
}

# Frozen legacy TCI-Lite v4 list, not dependent on the host Python version.
STDLIB = set("os sys json math re datetime time random collections itertools functools pathlib typing ast inspect importlib statistics argparse logging urllib http email html xml csv configparser tempfile shutil glob fnmatch linecache pickle copy pprint textwrap string io contextlib".split())


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def evidence_hash(evidence):
    return hashlib.sha256(canonical(evidence).encode()).hexdigest()


def tci_score(source, static_imports, visible_ids):
    """Legacy 3+2+5 scale with the documented `tools.<id>` namespace port."""
    loc = sum(bool(s.strip()) and not s.lstrip().startswith("#") for s in source.splitlines())
    external = 0
    for line in source.splitlines():
        words = line.strip().split()
        if len(words) >= 2 and words[0] in ("from", "import"):
            module = words[1].split(".")[0].rstrip(",")
            external += not words[1].startswith(".") and module not in STDLIB and module != "tools"
    iface, valid = 0.0, False
    try:
        tree = ast.parse(source)
        fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "execute"), None)
        if fn is not None:
            valid = True
            returns = []
            for n in ast.walk(fn):
                if isinstance(n, ast.Return) and n.value is not None:
                    v = n.value
                    returns.append(min(len(v.keys) / 5, 1) if isinstance(v, ast.Dict) else
                                   min(len(v.elts) / 10, 1) if isinstance(v, (ast.List, ast.Tuple)) else
                                   0.5 if isinstance(v, ast.Call) else 0.3)
            iface = min(len(fn.args.args) / 5, 1) + max(returns, default=0)
    except SyntaxError:
        pass
    comp = min(0.5 * len(set(static_imports) & set(visible_ids)), 4) + min(0.1 * external, 1)
    return round((3 * min(loc / 300, 1) + iface + comp) * (1 if valid else 0.6), 3)


def text_pairs(entries):
    """(cosine, id1, id2), descending similarity with deterministic tie-breaks."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    entries = sorted(entries, key=lambda e: e["id"])
    if len(entries) < 2:
        return [], "fewer_than_two_tools"
    texts = [(e.get("label") or "") + " " + (e.get("description") or "") for e in entries]
    try:
        x = TfidfVectorizer(stop_words="english").fit_transform(texts)
    except ValueError as exc:
        if "empty vocabulary" not in str(exc):
            raise
        return [], "empty_vocabulary"
    cos = (x @ x.T).toarray()  # TF-IDF defaults to unit L2 norm
    pairs = [(float(cos[i, j]), entries[i]["id"], entries[j]["id"])
             for i in range(len(entries)) for j in range(i + 1, len(entries))]
    return sorted(pairs, key=lambda p: (-p[0], p[1], p[2])), "ok"


def build_evidence(snapshot, agent, rnd, cfg, source_of, known_tasks, primitives):
    history = [e for e in snapshot if e["round"] < rnd]
    neighbours = ring_neighbours(agent, cfg.n_agents, cfg.k)
    pool = [e for e in history if e["author"] in neighbours]
    by_id = {e["id"]: e for e in history}
    adoption = Counter(d for e in history for d in set(e.get("static_imports", [])))

    def pack(e, role):
        return {"tool_id": e["id"], "author": e["author"], "round": e["round"],
                "label": e.get("label"), "description": e.get("description"),
                "target": e.get("target"), "implements": e.get("implements", []),
                "dev_pass": bool((e.get("harness") or {}).get("passed")),
                "tci": e["tci"], "adoption": adoption[e["id"]], "role": role,
                "code_excerpt": "\n".join(s[:200] for s in source_of(e["id"]).splitlines()[:20])}

    pairs, reason = text_pairs(pool)
    qualifying = [p for p in pairs if p[0] >= cfg.separation_threshold]
    s = None
    if qualifying:
        sim, left, right = qualifying[0]  # cap of 2 unique tools -> first pair
        s = {"pair_similarity": sim, "tools": [pack(by_id[t], "similar_neighbour") for t in (left, right)]}
    elif reason == "ok":
        reason = "below_threshold"
    recent = [e for e in pool if rnd - cfg.alignment_window <= e["round"]]
    a = None
    if recent:
        passing = [e for e in recent if (e.get("harness") or {}).get("passed")]
        best = min(passing or recent, key=lambda e: (-e["tci"], e["round"], e["id"]))
        tools = [pack(best, "quality_exemplar")]
        adopted = [e for e in recent if adoption[e["id"]] > 0]
        if adopted:
            most = min(adopted, key=lambda e: (-adoption[e["id"]], e["round"], e["id"]))
            if most["id"] != best["id"]:
                tools.append(pack(most, "adoption_exemplar"))
        a = {"fallback": not bool(passing), "tools": tools,
             "metadata_note": "TCI is complexity, not correctness; adoption counts distinct static importers."}
    prev = [e for e in history if e["round"] == rnd - 1]
    c = None
    if prev:
        targets = Counter(e["target"] for e in prev if e.get("target") in known_tasks)
        prims = Counter(p for e in prev for p in set(e.get("implements", [])) if p in primitives)
        c = {"round": rnd - 1, "target_counts": dict(sorted(targets.items())),
             "primitive_counts": dict(sorted(prims.items())), "n_parsed_tools": len(prev),
             "no_target": sum(not e.get("target") for e in prev),
             "unknown_target": sum(bool(e.get("target")) and e["target"] not in known_tasks for e in prev),
             "unknown_primitive_declarations": sum(p not in primitives for e in prev for p in set(e.get("implements", [])))}
    return {"S": s, "A": a, "C": c}, {"S_selection": reason, "neighbours": neighbours, "pool_size": len(pool)}


def render_evidence(evidence, arm):
    if arm not in SAC_ARMS:
        raise ValueError(arm)
    sections, fired = [], {}
    for name, bit in zip("SAC", arm):
        value = evidence[name]
        lines = [f"[{name} evidence]", canonical(value)]
        if value is not None:
            lines.append(GUIDANCE[name][int(bit)])
        sections.append("\n".join(lines))
        fired[name] = value is not None and bit == "1"
    return "\n\n".join(sections), fired
