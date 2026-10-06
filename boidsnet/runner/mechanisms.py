"""Snapshot-derived, toggle-independent evidence for the original Boids S/A/C rules.

The selectors adapt ``legacy/src/boids_rules.py``: S uses the exact sklearn
English-stop-word TF-IDF/cosine rule (threshold .3, two unique tools); A uses
the preceding three rounds' tested TCI leader, falling back to the TCI
leader, plus a positive-adoption leader. Stable tool-id order breaks ties.
All arms receive the same selected metadata and first-20-line source
excerpts. Only ``render_evidence`` consults guidance toggles.
The .3 threshold is the original helper default; historical run_experiment.py
used a .45 default. This adaptation explicitly chooses the helper default.
The shared pass signal is this runner's dev-target coverage-probe verdict,
not sealed-test performance; it is exposed even when A guidance is disabled.

TCI-Lite v4 preserves the original LOC, execute-parameter, return-AST,
external-import-line, and quality-gate rules. The intentional adaptation is
that known tool imports are supplied as static IDs instead of rediscovered
from bare-module imports on disk. Callers should exclude unresolved/self
imports. No tool source is imported or executed. As in the original, the
small fixed stdlib allowlist is used; tool import lines also contribute to
the non-stdlib import score, positional-only/keyword-only/variadic parameters
are not counted, and nested return nodes remain included.

C is an explicit adaptation, ``descriptive_counts_v1``, rather than a
purported reproduction of the original model-written observer summary. It
counts only preceding-round declared targets and IMPLEMENTS values, uses no
free-form descriptions, and has zero observer model calls, tokens, or cost.
Its shared summary is descriptive; trend-following guidance exists only in
the active C framing.
"""

import ast
from collections import Counter
import hashlib
import json


EVIDENCE_VERSION = "original_boids_sac_evidence_v1"
COMPLEXITY_VERSION = "tci_lite_v4_static_v1"
COHESION_VERSION = "descriptive_counts_v1"
SEPARATION_THRESHOLD = 0.3
SEPARATION_TOP_N = 2
ALIGNMENT_ROUNDS = 3
EXCERPT_LINES = 20

# Deliberately the original list, not the running interpreter's stdlib list.
_STDLIB_MODULES = frozenset({
    "os", "sys", "json", "math", "re", "datetime", "time", "random",
    "collections", "itertools", "functools", "pathlib", "typing",
    "ast", "inspect", "importlib", "statistics", "argparse", "logging",
    "urllib", "http", "email", "html", "xml", "csv", "configparser",
    "tempfile", "shutil", "glob", "fnmatch", "linecache", "pickle",
    "copy", "pprint", "textwrap", "string", "io", "contextlib",
})


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json(value):
    """Escape free-form field values, including embedded newlines."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True)


def compute_complexity(source, static_imports):
    """Return static TCI-Lite v4 metrics; never execute ``source``.

    ``static_imports`` contains resolved, non-self tool IDs. Unlike the
    original regex, this input supports the runner's ``tools.<id>`` imports.
    An invalid AST or absent execute function receives the original .6
    quality gate; this gate is not a harness/test result.
    """
    lines = source.splitlines()
    loc = sum(bool(line.strip()) and not line.strip().startswith("#")
              for line in lines)
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        tree = None
    execute = next((node for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef) and node.name == "execute"),
                   None) if tree is not None else None
    param_count = len(execute.args.args) if execute is not None else 0
    return_score = 0.0
    if execute is not None:
        for node in ast.walk(execute):
            if not isinstance(node, ast.Return) or node.value is None:
                continue
            ret = node.value
            if isinstance(ret, ast.Dict):
                value = min(1.0, len(ret.keys) / 5.0)
            elif isinstance(ret, (ast.List, ast.Tuple)):
                value = min(1.0, len(ret.elts) / 10.0)
            elif isinstance(ret, ast.Call):
                value = 0.5
            else:
                value = 0.3
            return_score = max(return_score, value)

    external_imports = 0
    for line in lines:
        line = line.strip()
        if line.startswith(("import ", "from ")):
            parts = line.split()
            module = parts[1].split(".")[0].strip() if len(parts) > 1 else ""
            if module and module not in _STDLIB_MODULES:
                external_imports += 1
    tool_calls = len(set(static_imports or ()))
    code_score = 3.0 * min(1.0, loc / 300.0)
    iface_score = min(1.0, param_count / 5.0) + return_score
    comp_score = min(4.0, tool_calls * 0.5) + min(1.0, external_imports * 0.1)
    quality_gate = 1.0 if execute is not None else 0.6
    raw = code_score + iface_score + comp_score
    return {
        "analysis_version": COMPLEXITY_VERSION,
        "tci_score": round(quality_gate * raw, 3),
        "tci_raw": round(raw, 3),
        "code_complexity": round(code_score, 3),
        "interface_complexity": round(iface_score, 3),
        "compositional_complexity": round(comp_score, 3),
        "quality_gate": quality_gate,
        "lines_of_code": loc,
        "param_count": param_count,
        "tool_calls": tool_calls,
        "external_imports": external_imports,
    }


def _separation(pool, tool_evidence):
    result = {
        "selector": "original_tfidf_pair_cosine_v1",
        "threshold": SEPARATION_THRESHOLD,
        "top_n": SEPARATION_TOP_N,
        "vectorizer": {"class": "sklearn.feature_extraction.text.TfidfVectorizer",
                       "stop_words": "english", "other_parameters": "sklearn defaults"},
        "text_fields": ["label", "description"],
        "tie_break": "ascending tool ID; stable pair order",
        "pool_ids": [entry["id"] for entry in pool],
        "pairs": [],
        "selected": [],
        "reason": "fewer_than_two_neighbour_tools",
    }
    if len(pool) < 2:
        return result
    # Keep historical runner arms importable without installing sklearn.
    # There is intentionally no substitute vectorizer or similarity metric.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import sklearn
    except ImportError as exc:
        raise RuntimeError(
            "Original Boids separation evidence requires scikit-learn; install "
            "the project's declared scikit-learn dependency. No alternate "
            "similarity implementation is used, including for S=0 controls."
        ) from exc
    result["sklearn_version"] = sklearn.__version__
    documents = [f"{entry.get('label') or ''} {entry.get('description') or ''}"
                 for entry in pool]
    result["text_provenance"] = [
        {"id": entry["id"], "text": text, "sha256": _sha(text)}
        for entry, text in zip(pool, documents)
    ]
    try:
        tfidf = TfidfVectorizer(stop_words="english").fit_transform(documents)
        similarities = cosine_similarity(tfidf)
    except ValueError as exc:
        # The original rule returns no evidence for an empty vocabulary.
        # Keep its failure observable instead of inventing a fallback score.
        result["reason"] = "tfidf_value_error"
        result["error"] = str(exc)
        return result
    pairs = [(float(similarities[i, j]), i, j)
             for i in range(len(pool)) for j in range(i + 1, len(pool))]
    pairs.sort(key=lambda value: -value[0])
    result["pairs"] = [
        {"ids": [pool[i]["id"], pool[j]["id"]], "similarity": score}
        for score, i, j in pairs
    ]
    selected, seen = [], set()
    for score, i, j in pairs:
        if score < SEPARATION_THRESHOLD:
            break
        for index in (i, j):
            tool_id = pool[index]["id"]
            if tool_id not in seen:
                item = dict(tool_evidence(pool[index]))
                item["similarity"] = score
                item["similarity_partner_id"] = pool[j if index == i else i]["id"]
                selected.append(item)
                seen.add(tool_id)
        if len(selected) >= SEPARATION_TOP_N:
            break
    result["selected"] = selected[:SEPARATION_TOP_N]
    result["reason"] = "selected" if selected else "no_pair_at_threshold"
    return result


def _alignment(pool, round_num, tool_evidence):
    recent = [entry for entry in pool
              if round_num - ALIGNMENT_ROUNDS <= entry["round"] < round_num]
    candidates = [tool_evidence(entry) for entry in recent]
    tested = [entry for entry in candidates if entry["test_passed"]]
    quality_pool = tested or candidates
    quality = max(quality_pool, key=lambda entry: entry["tci_score"], default=None)
    adoption = max((entry for entry in candidates if entry["adoption_count"] > 0),
                   key=lambda entry: entry["adoption_count"], default=None)
    selected = []
    for entry in (quality, adoption):
        if entry is not None and all(entry["id"] != item["id"] for item in selected):
            selected.append(entry)
    return {
        "selector": "original_recent_tci_and_adoption_v1",
        "rounds_window": ALIGNMENT_ROUNDS,
        "round_min_inclusive": round_num - ALIGNMENT_ROUNDS,
        "round_max_exclusive": round_num,
        "tie_break": "ascending tool ID",
        "candidate_ids": [entry["id"] for entry in candidates],
        "candidate_scores": [
            {key: entry[key] for key in ("id", "author", "round", "age", "tci_score",
                                        "test_passed", "adoption_count")}
            for entry in candidates
        ],
        "quality": quality,
        "adoption": adoption,
        "selected": selected,
        "selection_mode": ("passed_tci_leader" if tested else
                           "fallback_tci_leader" if candidates else "no_recent_tools"),
        "adoption_definition": "distinct later snapshot tools statically importing this tool with build-time ACL permission",
        "adoption_scope": "entire preceding-round snapshot; no future or runtime imports",
    }


def _cohesion(snapshot, round_num):
    previous = [entry for entry in snapshot if entry["round"] == round_num - 1]
    targets = Counter(str(entry.get("target") or "NONE") for entry in previous)
    primitives = Counter()
    for entry in previous:
        # A declaration counts at most once per tool, even if repeated.
        primitives.update(set(str(value) for value in entry.get("implements") or ()))
    target_counts = dict(sorted(targets.items()))
    implements_counts = dict(sorted(primitives.items()))
    authors = sorted({entry["author"] for entry in previous})
    summary = (
        f"Preceding round {round_num - 1}: {len(previous)} tools from {len(authors)} agents. "
        f"Declared target counts: {_json(target_counts)}. "
        f"Declared IMPLEMENTS counts (each primitive once per tool): {_json(implements_counts)}."
    ) if previous else ""
    return {
        "version": COHESION_VERSION,
        "source_round": round_num - 1,
        "source_ids": [entry["id"] for entry in previous],
        "source_authors": [entry["author"] for entry in previous],
        "source_ages": [round_num - entry["round"] for entry in previous],
        "source_fields": ["round", "target", "implements"],
        "tool_count": len(previous),
        "agent_count": len(authors),
        "target_counts": target_counts,
        "implements_counts": implements_counts,
        "summary": summary,
        "summary_sha256": _sha(summary),
        "model_calls": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "cost_usd": 0.0,
        "accounting_scope": "observer generation only; builder context is counted by the runner",
        "adaptation": "deterministic descriptive declaration counts; no model-written observer",
    }


def build_evidence(snapshot, neighbours, round_num, source_loader):
    """Build a JSON-serializable common bundle without consulting toggles.

    ``snapshot`` is the society-wide library at the end of the preceding
    round. ``neighbours`` is the collection of neighbouring author IDs, and
    ``source_loader(tool_id)`` returns source text. Future/current-round
    entries are excluded defensively. ``fired`` records evidence eligibility,
    not whether a treatment's active guidance was enabled.
    """
    if round_num < 1:
        raise ValueError("round_num must be at least one")
    frozen = sorted((entry for entry in snapshot if entry["round"] < round_num),
                    key=lambda entry: entry["id"])
    known_ids = {entry["id"] for entry in frozen}
    if len(known_ids) != len(frozen):
        raise ValueError("snapshot contains duplicate tool IDs")
    neighbour_ids = set(neighbours or ())
    pool = [entry for entry in frozen if entry["author"] in neighbour_ids]
    entries = {entry["id"]: entry for entry in frozen}

    def permitted_imports(entry):
        # Missing provenance is not evidence of build-time permission.
        return sorted(imported for imported in set(entry.get("static_imports") or ())
                      if imported in entries
                      and imported in entry.get("build_acl", ())
                      and entries[imported]["round"] < entry["round"])

    adopted_by = {tool_id: [] for tool_id in known_ids}
    for entry in frozen:
        for imported in permitted_imports(entry):
            if imported in known_ids and imported != entry["id"]:
                adopted_by[imported].append(entry["id"])
    source_cache, evidence_cache = {}, {}

    def source_evidence(tool_id):
        if tool_id not in source_cache:
            try:
                source = source_loader(tool_id)
                if not isinstance(source, str):
                    raise TypeError("source_loader must return source text")
                excerpt = "".join(source.splitlines(keepends=True)[:EXCERPT_LINES])
                provenance = {
                    "status": "available", "tool_id": tool_id,
                    "path": f"tools/{tool_id}.py", "source_sha256": _sha(source),
                    "excerpt_sha256": _sha(excerpt), "line_start": 1,
                    "line_end": min(EXCERPT_LINES, len(source.splitlines())),
                    "line_limit": EXCERPT_LINES,
                    "truncated": len(source.splitlines()) > EXCERPT_LINES,
                }
            except (OSError, UnicodeError, KeyError) as exc:
                source, excerpt = None, "# Code not available"
                provenance = {
                    "status": "unavailable", "tool_id": tool_id,
                    "path": f"tools/{tool_id}.py", "error_type": type(exc).__name__,
                    "source_sha256": None, "excerpt_sha256": _sha(excerpt),
                    "line_start": None, "line_end": None, "line_limit": EXCERPT_LINES,
                    "truncated": False,
                }
            source_cache[tool_id] = (source, excerpt, provenance)
        return source_cache[tool_id]

    def tool_evidence(entry):
        tool_id = entry["id"]
        if tool_id not in evidence_cache:
            source, excerpt, provenance = source_evidence(tool_id)
            complexity = entry.get("complexity")
            if complexity is not None and "tci_score" in complexity:
                complexity = dict(complexity)
                complexity_origin = "snapshot.complexity"
            elif source is not None:
                imports = permitted_imports(entry)
                complexity = compute_complexity(source, imports)
                complexity_origin = "static_source_analysis"
            else:
                complexity = {"analysis_version": COMPLEXITY_VERSION,
                              "tci_score": 0.0, "error": "source_unavailable"}
                complexity_origin = "source_unavailable"
            harness = entry.get("harness")
            passed = ((harness or {}).get("passed") is True if "harness" in entry
                      else entry.get("test_passed") is True)
            evidence_cache[tool_id] = {
                "id": tool_id, "author": entry["author"], "round": entry["round"],
                "age": round_num - entry["round"],
                "label": entry.get("label") or "", "description": entry.get("description") or "",
                "test_passed": passed,
                "harness_scope": "dev_target_coverage_probes_not_sealed_test",
                "test_provenance": "snapshot.harness.passed" if "harness" in entry else "snapshot.test_passed",
                "complexity": complexity, "tci_score": float(complexity["tci_score"]),
                "complexity_provenance": complexity_origin,
                "adoption_count": len(adopted_by[tool_id]), "adopted_by": adopted_by[tool_id],
                "excerpt": excerpt, "excerpt_provenance": provenance,
            }
        return evidence_cache[tool_id]

    separation = _separation(pool, tool_evidence)
    alignment = _alignment(pool, round_num, tool_evidence)
    cohesion = _cohesion(frozen, round_num)
    return {
        "version": EVIDENCE_VERSION,
        "round": round_num,
        "neighbours": sorted(neighbour_ids),
        "snapshot_ids": [entry["id"] for entry in frozen],
        "neighbour_ids": [entry["id"] for entry in pool],
        "fired": {"S": bool(separation["selected"]),
                  "A": bool(alignment["selected"]), "C": bool(cohesion["summary"])},
        "fired_definition": "evidence available, before applying guidance toggles",
        "S": separation, "A": alignment, "C": cohesion,
    }


def _render_tool(tool):
    """Shared descriptive content, identical in active and neutral arms."""
    return [
        f"Tool {_json(tool['id'])}; author {_json(tool['author'])}; "
        f"created round {tool['round']}; age {tool['age']} rounds.",
        f"Label: {_json(tool['label'])}",
        f"Description: {_json(tool['description'])}",
        f"TCI-Lite score: {tool['tci_score']:.3f}; "
        f"dev-target coverage-probe pass: {_json(tool['test_passed'])}; "
        f"adoption count: {tool['adoption_count']}.",
        f"Source excerpt (first {EXCERPT_LINES} lines; "
        f"status {tool['excerpt_provenance']['status']}):",
        "```python\n" + tool["excerpt"].rstrip("\n") + "\n```",
    ]


def render_evidence(bundle, toggles):
    """Render shared evidence plus only the enabled S/A/C instructions.

    Neutral blocks contain observations and excerpts without mechanism
    directives. ``toggles`` maps ``S``, ``A``, and ``C`` to booleans/0/1.
    This function never changes the evidence bundle or selects new evidence.
    """
    lines = []
    separation, alignment, cohesion = bundle["S"], bundle["A"], bundle["C"]
    if bundle["fired"]["S"]:
        lines.append("[SEPARATION EVIDENCE]")
        for tool in separation["selected"]:
            lines.append(f"Neighbour-pair TF-IDF cosine similarity: {tool['similarity']:.6f}; "
                         f"paired with {_json(tool['similarity_partner_id'])}.")
            lines.extend(_render_tool(tool))
        if toggles.get("S", False):
            lines.append("SEPARATION GUIDANCE: Ensure your tool offers a DISTINCT function. "
                         "Do not rebuild a tool that performs these core tasks. "
                         "Find a new, complementary niche.")
    if bundle["fired"]["A"]:
        lines.append("[ALIGNMENT EVIDENCE]")
        for role in ("quality", "adoption"):
            tool = alignment[role]
            if tool is None:
                continue
            lines.append("Quality exemplar:" if role == "quality" else "Adoption leader:")
            lines.extend(_render_tool(tool))
        if toggles.get("A", False):
            lines.append("ALIGNMENT GUIDANCE: Learn from these recent successful neighbours. "
                         "Analyze their code for composition, depth, robust error handling, "
                         "and clear functionality.")
            if alignment["adoption"] is not None:
                lines.append("Analyze the adoption leader's simple API and focused functionality "
                             "to understand why it is used by other tools.")
            lines.append("Do not just copy their code. Adopt their successful DESIGN PRINCIPLES "
                         "like modularity, composition, and robustness in your own unique tool.")
    if bundle["fired"]["C"]:
        lines.extend(["[COHESION EVIDENCE]", cohesion["summary"]])
        if toggles.get("C", False):
            lines.append("COHESION GUIDANCE: Contribute to this emerging society-wide trend. "
                         "How can your tool serve this broader goal?")
    return "\n".join(lines)


# Explicit aliases for callers that name the toggle-independent stage.
build_shared_evidence = build_evidence
shared_evidence = build_evidence
