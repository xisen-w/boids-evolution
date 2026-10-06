"""Neighbourhoods, exemplar selection and length-matched framing.

Content is held fixed across arms: E, L0 and L1 run the SAME selection rule
over the SAME local pool and differ only in framing text; G0 runs the same
rule over the society-wide pool.  IM gets no exemplar block.

Selection rule (pre-register): from the pool of other agents' tools built in
earlier rounds, take the m tools whose behaviour on P_signal is most similar
to the agent's own most recent tool (behavioural near-duplicates).  Ties and
the cold start (agent has no tool yet) are broken by a seeded RNG.
"""
import ast
import random

# Framing texts are written to equal length (checked in tests, +-3 chars).
FRAMING = {
    "neutral": ("[NEIGHBOUR TOOLS] Here are some tools that other agents in your society\n"
                "have built. They are shown for information only. Do as you see fit"),
    "avoid":   ("[NEIGHBOUR TOOLS] These tools by other agents behave much like yours.\n"
                "Avoid duplicating these behaviours: build something that differs.  "),
    "emulate": ("[NEIGHBOUR TOOLS] These tools by other agents behave much like yours.\n"
                "Emulate these designs: build in the same spirit and conventions.   "),
}


def ring_neighbours(agent, n_agents, k):
    half = k // 2
    out = []
    for d in range(1, half + 1):
        out += [(agent - d) % n_agents, (agent + d) % n_agents]
    return sorted(set(out) - {agent})


def select_exemplars(agent, pool, own_latest, m, rng, similarity):
    """pool: list of library entries (other agents, earlier rounds).
    Returns (chosen entries, similarities, mode)."""
    if not pool:
        return [], [], "empty_pool"
    order = list(pool)
    rng.shuffle(order)                      # seeded tie-break
    if own_latest is None or own_latest.get("signature_signal") is None:
        chosen = order[:m]
        return chosen, [None] * len(chosen), "random_cold_start"
    ref = own_latest["signature_signal"]
    scored = [(similarity(ref, e.get("signature_signal")), i, e)
              for i, e in enumerate(order)]
    scored.sort(key=lambda t: (-t[0], t[1]))
    chosen = scored[:m]
    # If the agent's own latest tool crashed on every probe, all similarities
    # are 0 and the order is just the seeded shuffle: label it so the
    # manipulation check does not count it as a behavioural selection.
    mode = ("own_tool_crashed" if all(str(x).startswith("ERR") for x in ref)
            else "behavioural")
    return [e for _, _, e in chosen], [s for s, _, _ in chosen], mode


def select_matched(ring_pool, other_pool, own_latest, m, rng, similarity):
    """G0m selection (pre-registered):
    - targets = similarities the L0 rule would pick from this agent's own ring
      pool, computed in this society, this round;
    - round 1 / empty ring pool -> no exemplars ("empty_pool"), same as L0;
    - cold start (no own tool yet) -> seeded random draw of up to m from the
      non-neighbour pool, same as L0's cold start;
    - otherwise each target, highest first, takes the unused non-neighbour
      tool with the smallest |sim - target| (seeded tie-break);
    - if the non-neighbour pool runs out, fewer exemplars are shown and the
      shortfall is logged ("matched_short").
    Returns (chosen, sims, mode, match) where match holds targets/diffs."""
    if not ring_pool:
        return [], [], "empty_pool", None
    if own_latest is None or own_latest.get("signature_signal") is None:
        order = list(other_pool)
        rng.shuffle(order)
        k = min(m, len(ring_pool))          # L0 would show at most len(ring_pool)
        chosen = order[:k]
        return chosen, [None] * len(chosen), "random_cold_start", {"targets": None, "shortfall": k - len(chosen)}
    _, targets, _ = select_exemplars(None, ring_pool, own_latest, m, random.Random(0), similarity)
    ref = own_latest["signature_signal"]
    order = list(other_pool)
    rng.shuffle(order)
    cand = [(similarity(ref, e.get("signature_signal")), i, e) for i, e in enumerate(order)]
    chosen, sims, diffs = [], [], []
    for t in targets:
        if not cand:
            break
        j = min(range(len(cand)), key=lambda q: (abs(cand[q][0] - t), cand[q][1]))
        sv, _, e = cand.pop(j)
        chosen.append(e); sims.append(sv); diffs.append(round(abs(sv - t), 6))
    mode = "matched" if len(chosen) == len(targets) else "matched_short"
    return chosen, sims, mode, {"targets": targets, "abs_diff": diffs,
                                "shortfall": len(targets) - len(chosen)}


EXEMPLAR_CHARS = 400


def summarise(entry, source, prose_limit=None):
    """Keep interface metadata intact; cap only the descriptive prose.
    Same format for every arm, so content is fixed (msg #30, E3)."""
    sig, doc = "execute(?)", ""
    try:
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.FunctionDef) and node.name == "execute":
                sig = "execute(" + ast.unparse(node.args) + ")"
                doc = (ast.get_docstring(node) or "").strip()
                break
    except SyntaxError:
        pass
    impl = ", ".join(entry.get("implements") or []) or "none"
    mandatory = (f"--- {entry['id']} (by agent {entry['author']:02d})\n"
                 f"    {sig} | implements: {impl}")
    prose = "\n    " + entry.get("description", "")
    if doc:
        prose += f" | doc: {' '.join(doc.split())}"
    room = max(0, EXEMPLAR_CHARS - len(mandatory))
    if prose_limit is not None:
        room = min(room, prose_limit)
    if len(prose) > room:
        prose = prose[:room - 3] + "..." if room >= 3 else ""
    # An unusually long signature can exceed the soft exemplar budget. The
    # overall prompt hard cap is enforced separately, never by corrupting it.
    return mandatory + prose


def render_block(framing, exemplars, source_of):
    if framing is None or not exemplars:
        return ""
    return "\n".join([FRAMING[framing]] + [summarise(e, source_of(e["id"])) for e in exemplars])
