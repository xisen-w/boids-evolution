"""Mechanism environment for the Boids study (v0.2.2, DRAFT, not frozen).

v0.2.1: draw terminal primitives from sorted(TERMINAL), not list(set), so the task
lists no longer depend on PYTHONHASHSEED. The sealed TEST hash is unchanged.

A grammar of typed table transforms. Every task is a pipeline of primitives whose
reference implementation is known, so harness verdicts never depend on agent-written
tests. No model calls anywhere in this module.

Data model: a Table is a list of dict rows; every column is either "num" (float or
None) or "str" (str or None). Tables are generated deterministically from a seed.

Interface for the runner (agreed in room msg #27):
    tasks(seed, split) -> list[Task]
    harness(tool_fn, task, probe="coverage") -> Verdict
    verify_primitive(tool_fn, primitive, probe="coverage") -> Verdict   # for M6/M7
"""
from __future__ import annotations

import hashlib
import zlib
import json
import math
import random
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Tuple

Table = List[Dict[str, Any]]

# ---------------------------------------------------------------------------
# Seed ranges. Disjoint by construction; the TEST range is never passed to builders.
# ---------------------------------------------------------------------------
SEED_RANGES = {
    "dev": (0, 10_000),            # task specs visible to building agents
    "test": (10_000, 20_000),      # sealed: only the frozen-library solver sees these
    "signal": (20_000, 30_000),    # freeze probes; SAC separation is text-only
    "coverage": (30_000, 40_000),  # P_coverage: M6/M7 and load-bearing ablation
    "diversity": (40_000, 50_000), # P_diversity: M5 behavioural clustering
    "test_coverage": (50_000, 60_000), # v0.2.2: held-out solver input tables
}
PROBES_PER_SET = 8

# ---------------------------------------------------------------------------
# Table generation
# ---------------------------------------------------------------------------
REGIONS = ["north", "south", "east", "west"]
PRODUCTS = ["alpha", "beta", "gamma", "delta", "eps"]


def gen_table(seed: int, n_rows: Optional[int] = None) -> Table:
    """Sales-like table with missing values, duplicates, unit quirks and dates."""
    rng = random.Random(seed)
    n = n_rows or rng.randint(12, 30)
    rows = []
    for i in range(n):
        month = rng.randint(1, 12)
        row = {
            "id": float(rng.randint(1, max(3, n - 3))),  # deliberate duplicate ids
            "region": rng.choice(REGIONS) if rng.random() > 0.2 else rng.choice([" North", "SOUTH ", "East", " west "]),
            "product": rng.choice(PRODUCTS),
            "date": f"2025-{month:02d}-{rng.randint(1, 28):02d}",
            "units": float(rng.randint(0, 50)),
            "price_cents": float(rng.randint(100, 5000)),
            "cost_cents": float(rng.randint(50, 4000)),
        }
        for col in ("units", "price_cents", "region"):
            if rng.random() < 0.12:
                row[col] = None
        rows.append(row)
    return rows


def gen_lookup(seed: int) -> Table:
    """Second table for joins: region -> target, manager."""
    rng = random.Random(seed + 7)
    return [{"region": r, "target": float(rng.randint(100, 900)),
             "manager": rng.choice(["ann", "bo", "cy", "di"])} for r in REGIONS]


# ---------------------------------------------------------------------------
# Primitives: name -> (reference fn, parameter sampler, description)
# Each ref fn: (table, lookup, **params) -> Table.  Pure; never mutates input.
# ---------------------------------------------------------------------------
NUM_COLS = ["units", "price_cents", "cost_cents"]


def _copy(t: Table) -> Table:
    return [dict(r) for r in t]


def p_filter(t, lk, col, op, value):
    ops = {">": lambda a: a is not None and a > value,
           "<": lambda a: a is not None and a < value,
           "==": lambda a: a == value}
    return [dict(r) for r in t if ops[op](r.get(col))]


def p_fill_missing(t, lk, col, strategy):
    vals = [r[col] for r in t if r.get(col) is not None]
    if strategy == "zero":
        fill = 0.0
    elif strategy == "mean":
        fill = sum(vals) / len(vals) if vals else 0.0
    else:  # median
        s = sorted(vals)
        fill = (s[len(s) // 2] if len(s) % 2 else (s[len(s) // 2 - 1] + s[len(s) // 2]) / 2) if s else 0.0
    out = _copy(t)
    for r in out:
        if r.get(col) is None:
            r[col] = fill
    return out


def p_drop_missing(t, lk, col):
    return [dict(r) for r in t if r.get(col) is not None]


def p_dedupe(t, lk, key):
    seen, out = set(), []
    for r in t:
        if r.get(key) not in seen:
            seen.add(r.get(key))
            out.append(dict(r))
    return out


def p_derive(t, lk, new, a, op, b):
    f = {"*": lambda x, y: x * y, "-": lambda x, y: x - y, "+": lambda x, y: x + y}[op]
    out = _copy(t)
    for r in out:
        r[new] = None if r.get(a) is None or r.get(b) is None else f(r[a], r[b])
    return out


def p_unit_convert(t, lk, col, factor):
    out = _copy(t)
    for r in out:
        if r.get(col) is not None:
            r[col] = r[col] * factor
    return out


def p_month_bucket(t, lk, col):
    out = _copy(t)
    for r in out:
        r["month"] = r[col][:7] if r.get(col) else None
    return out


def p_group_agg(t, lk, key, col, agg):
    groups: Dict[Any, List[float]] = {}
    for r in t:
        if r.get(key) is None:
            continue
        groups.setdefault(r[key], [])
        if r.get(col) is not None:
            groups[r[key]].append(r[col])
    fn = {"sum": sum, "count": len, "max": lambda v: max(v) if v else None,
          "mean": lambda v: sum(v) / len(v) if v else None}[agg]
    return [{key: k, f"{agg}_{col}": fn(v)} for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))]


def p_sort(t, lk, col, desc):
    present = [r for r in t if r.get(col) is not None]
    missing = [r for r in t if r.get(col) is None]
    return [dict(r) for r in sorted(present, key=lambda r: r[col], reverse=desc)] + [dict(r) for r in missing]


def p_top_k(t, lk, col, k):
    return p_sort(t, lk, col, True)[:k]


def p_zscore(t, lk, col):
    vals = [r[col] for r in t if r.get(col) is not None]
    mu = sum(vals) / len(vals) if vals else 0.0
    sd = math.sqrt(sum((v - mu) ** 2 for v in vals) / len(vals)) if vals else 0.0
    out = _copy(t)
    for r in out:
        if r.get(col) is not None:
            r[col] = 0.0 if sd == 0 else (r[col] - mu) / sd
    return out


def p_clip(t, lk, col, lo, hi):
    out = _copy(t)
    for r in out:
        if r.get(col) is not None:
            r[col] = min(max(r[col], lo), hi)
    return out


def p_join_lookup(t, lk, key):
    idx = {r[key]: r for r in lk}
    out = []
    for r in t:
        m = idx.get(r.get(key))
        nr = dict(r)
        for c, v in (m or {c: None for c in lk[0] if c != key}).items():
            if c != key:
                nr[c] = v
        out.append(nr)
    return out


def p_rank(t, lk, col):
    ordered = p_sort(t, lk, col, True)
    for i, r in enumerate(ordered):
        r[f"rank_{col}"] = float(i + 1) if r.get(col) is not None else None
    return ordered


def p_normalize_str(t, lk, col):
    out = _copy(t)
    for r in out:
        if isinstance(r.get(col), str):
            r[col] = r[col].strip().lower()
    return out


def p_cumsum(t, lk, col):
    out, acc = _copy(t), 0.0
    for r in out:
        if r.get(col) is not None:
            acc += r[col]
        r[f"cumsum_{col}"] = acc
    return out


def p_diff(t, lk, col):
    out, prev = _copy(t), None
    for r in out:
        cur = r.get(col)
        r[f"diff_{col}"] = None if cur is None or prev is None else cur - prev
        if cur is not None:
            prev = cur
    return out


def p_pct_of_total(t, lk, col):
    tot = sum(r[col] for r in t if r.get(col) is not None)
    out = _copy(t)
    for r in out:
        r[f"pct_{col}"] = None if r.get(col) is None or tot == 0 else 100.0 * r[col] / tot
    return out


def p_bin(t, lk, col, edges):
    out = _copy(t)
    for r in out:
        v = r.get(col)
        r[f"bin_{col}"] = None if v is None else float(sum(1 for e in edges if v >= e))
    return out


def p_rolling_mean(t, lk, col, window):
    out = _copy(t)
    for i, r in enumerate(out):
        vals = [x[col] for x in t[max(0, i - window + 1): i + 1] if x.get(col) is not None]
        r[f"roll_{col}"] = sum(vals) / len(vals) if vals else None
    return out


def p_multi_group_agg(t, lk, keys, col, agg):
    groups: Dict[Any, List[float]] = {}
    for r in t:
        k = tuple(r.get(x) for x in keys)
        if any(v is None for v in k):
            continue
        groups.setdefault(k, [])
        if r.get(col) is not None:
            groups[k].append(r[col])
    fn = {"sum": sum, "count": len, "mean": lambda v: sum(v) / len(v) if v else None}[agg]
    return [dict(zip(keys, k), **{f"{agg}_{col}": fn(v)}) for k, v in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0])))]


def p_lookup_ratio(t, lk, col):
    """revenue-to-target style ratio: requires region normalised to match the lookup."""
    idx = {r["region"]: r["target"] for r in lk}
    out = _copy(t)
    for r in out:
        tgt = idx.get(r.get("region"))
        r[f"{col}_per_target"] = None if tgt in (None, 0) or r.get(col) is None else r[col] / tgt
    return out


def _num_col(rng, t_cols=NUM_COLS):
    return rng.choice(t_cols)


PRIMITIVES: Dict[str, Tuple[Callable, Callable[[random.Random], dict], str]] = {
    "filter": (p_filter, lambda g: {"col": _num_col(g), "op": g.choice([">", "<"]), "value": float(g.randint(5, 2000))},
               "keep rows where numeric column compares to a threshold; missing values are dropped"),
    "fill_missing": (p_fill_missing, lambda g: {"col": _num_col(g), "strategy": g.choice(["zero", "mean", "median"])},
                     "replace missing values of a numeric column by zero/mean/median of present values"),
    "drop_missing": (p_drop_missing, lambda g: {"col": g.choice(NUM_COLS + ["region"])},
                     "drop rows whose column is missing"),
    "dedupe": (p_dedupe, lambda g: {"key": "id"}, "keep the first row for each key value, preserving order"),
    "derive": (p_derive, lambda g: g.choice([{"new": "revenue_cents", "a": "units", "op": "*", "b": "price_cents"},
                                              {"new": "margin_cents", "a": "price_cents", "op": "-", "b": "cost_cents"}]),
               "add a column computed from two columns; missing if either input is missing"),
    "unit_convert": (p_unit_convert, lambda g: {"col": g.choice(["price_cents", "cost_cents"]), "factor": 0.01},
                     "multiply a numeric column by a factor (e.g. cents to dollars)"),
    "month_bucket": (p_month_bucket, lambda g: {"col": "date"}, "add a 'month' column YYYY-MM from an ISO date column"),
    "group_agg": (p_group_agg, lambda g: {"key": g.choice(["region", "product"]), "col": _num_col(g),
                                          "agg": g.choice(["sum", "mean", "count", "max"])},
                  "group by key (dropping missing keys) and aggregate a column; output sorted by key"),
    "sort": (p_sort, lambda g: {"col": _num_col(g), "desc": g.choice([True, False])},
             "stable sort by a numeric column; rows with missing values go last"),
    "top_k": (p_top_k, lambda g: {"col": _num_col(g), "k": g.randint(3, 6)}, "k rows with the largest values"),
    "zscore": (p_zscore, lambda g: {"col": _num_col(g)}, "standardise a column using population sd; missing stays missing"),
    "clip": (p_clip, lambda g: {"col": _num_col(g), "lo": 10.0, "hi": 3000.0}, "clip a numeric column to [lo, hi]"),
    "join_lookup": (p_join_lookup, lambda g: {"key": "region"},
                    "left-join the region lookup table (target, manager); unmatched rows get missing"),
    "rank": (p_rank, lambda g: {"col": _num_col(g)}, "sort descending and add rank_<col> (1 = largest)"),
    "normalize_str": (p_normalize_str, lambda g: {"col": "region"}, "strip whitespace and lowercase a string column; non-strings unchanged"),
    "cumsum": (p_cumsum, lambda g: {"col": _num_col(g)}, "add cumsum_<col>: running sum in row order, missing counts as 0"),
    "diff": (p_diff, lambda g: {"col": _num_col(g)}, "add diff_<col>: value minus the previous NON-missing value; first/missing -> missing"),
    "pct_of_total": (p_pct_of_total, lambda g: {"col": _num_col(g)}, "add pct_<col>: 100*value/sum of present values"),
    "bin": (p_bin, lambda g: {"col": _num_col(g), "edges": sorted(g.sample([10.0, 25.0, 500.0, 1000.0, 2500.0], 2))},
            "add bin_<col>: number of edges <= value (as float); missing stays missing"),
    "rolling_mean": (p_rolling_mean, lambda g: {"col": _num_col(g), "window": g.choice([2, 3])},
                     "add roll_<col>: mean of present values in the trailing window of rows (including current)"),
    "multi_group_agg": (p_multi_group_agg, lambda g: {"keys": ["region", "product"], "col": _num_col(g), "agg": g.choice(["sum", "count", "mean"])},
                        "group by several keys (dropping rows with any missing key), aggregate; sorted by keys"),
    "lookup_ratio": (p_lookup_ratio, lambda g: {"col": _num_col(g)},
                     "add <col>_per_target = value / region target from lookup; exact region match only"),
}

# group_agg changes the schema, so it may only appear last in a pipeline.
TERMINAL = {"group_agg", "multi_group_agg"}


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
@dataclass
class Task:
    id: str
    split: str
    depth: int
    steps: List[Tuple[str, dict]]
    spec: str
    primitive_set: List[str]
    probe_seeds: Dict[str, List[int]] = field(default_factory=dict)

    def reference(self, table: Table, lookup: Table) -> Table:
        out = table
        for name, params in self.steps:
            out = PRIMITIVES[name][0](out, lookup, **params)
        return out


def _spec(steps) -> str:
    parts = []
    for i, (name, params) in enumerate(steps, 1):
        parts.append(f"{i}. {name}({json.dumps(params, sort_keys=True)}): {PRIMITIVES[name][2]}")
    return "Transform the input table (and region lookup table) by applying in order:\n" + "\n".join(parts)


def _probe_seeds(task_seed: int, split: str = "dev") -> Dict[str, List[int]]:
    out = {}
    for name in ("signal", "coverage", "diversity"):
        lo, hi = SEED_RANGES["test_coverage" if name == "coverage" and split == "test" else name]
        rng = random.Random(task_seed * 31 + zlib.crc32(name.encode()) % 997)
        out[name] = [rng.randrange(lo, hi) for _ in range(PROBES_PER_SET)]
    return out


def make_task(task_seed: int, split: str, depth: int) -> Task:
    rng = random.Random(task_seed)
    names = [n for n in PRIMITIVES if n not in TERMINAL]
    steps = []
    for i in range(depth):
        pool = names + (sorted(TERMINAL) if i == depth - 1 else [])
        name = rng.choice(pool)
        steps.append((name, PRIMITIVES[name][1](rng)))
    return Task(id=f"{split}-{task_seed}-d{depth}", split=split, depth=depth, steps=steps,
                spec=_spec(steps), primitive_set=sorted({s[0] for s in steps}),
                probe_seeds=_probe_seeds(task_seed, split))


def tasks(seed: int, split: str, n_per_depth: int = 20, depths=(1, 2, 3)) -> List[Task]:
    if split not in ("dev", "test"):
        raise ValueError("tasks() serves only dev and test splits")
    lo, hi = SEED_RANGES[split]
    rng = random.Random(seed)
    out = []
    for d in depths:
        for _ in range(n_per_depth):
            out.append(make_task(rng.randrange(lo, hi), split, d))
    return out


def seal_hash(task_list: List[Task]) -> str:
    """Hash published before any run so the sealed test set cannot be changed later."""
    blob = json.dumps([asdict(t) for t in task_list], sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------
@dataclass
class Verdict:
    passed: bool
    n_pass: int
    n_total: int
    crashed: int
    details: List[str]


def _canon(v):
    if isinstance(v, float):
        return None if math.isnan(v) else round(v, 6)
    return v


def tables_equal(a: Any, b: Table) -> bool:
    if not isinstance(a, list) or len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if not isinstance(ra, dict) or set(ra) != set(rb):
            return False
        if any(_canon(ra[k]) != _canon(rb[k]) for k in rb):
            return False
    return True


def _run_on_probes(fn: Callable[[Table, Table], Table], ref: Callable[[Table, Table], Table], seeds: List[int]) -> Verdict:
    ok, crashed, details = 0, 0, []
    for s in seeds:
        t, lk = gen_table(s), gen_lookup(s)
        expected = ref(_copy(t), lk)
        try:
            got = fn(_copy(t), [dict(r) for r in lk])
        except Exception as e:  # noqa: BLE001 - any tool failure is a verdict, not a harness error
            if getattr(e, "infrastructure_failure", False):
                raise
            crashed += 1
            details.append(f"seed {s}: crash {type(e).__name__}: {e}"[:200])
            continue
        if tables_equal(got, expected):
            ok += 1
        else:
            details.append(f"seed {s}: output mismatch")
    return Verdict(ok == len(seeds), ok, len(seeds), crashed, details)


def harness(tool_fn: Callable[[Table, Table], Table], task: Task, probe: str = "coverage") -> Verdict:
    """tool_fn(table, lookup) -> table must reproduce the task's reference on every probe."""
    return _run_on_probes(tool_fn, task.reference, task.probe_seeds[probe])


def verify_primitive(tool_fn: Callable[..., Table], primitive: str, probe: str = "coverage", n_param_draws: int = 3) -> Verdict:
    """A tool that declares implements=[primitive] must match the reference for sampled params.
    Declared-and-verified coverage (M6) and per-primitive reliability (M7) use this."""
    ref_fn, sampler, _ = PRIMITIVES[primitive]
    lo, hi = SEED_RANGES[probe]
    rng = random.Random(zlib.crc32(primitive.encode()) % 10_007 + lo)
    total = Verdict(True, 0, 0, 0, [])
    for _ in range(n_param_draws):
        params = sampler(rng)
        seeds = [rng.randrange(lo, hi) for _ in range(PROBES_PER_SET // 2)]
        v = _run_on_probes(lambda t, lk: tool_fn(t, lk, **params), lambda t, lk: ref_fn(t, lk, **params), seeds)
        total = Verdict(total.passed and v.passed, total.n_pass + v.n_pass, total.n_total + v.n_total,
                        total.crashed + v.crashed, total.details + v.details)
    return total


def behaviour_vector(tool_fn: Callable[[Table, Table], Table], probe: str, seeds: Optional[List[int]] = None) -> List[str]:
    """Per-probe output hashes (msg #29 E1). Similarity = fraction of equal entries."""
    lo, hi = SEED_RANGES[probe]
    seeds = seeds or list(range(lo, lo + PROBES_PER_SET))
    vec = []
    for s in seeds:
        try:
            got = tool_fn(gen_table(s), gen_lookup(s))
            vec.append(hashlib.sha256(json.dumps(got, sort_keys=True, default=str).encode()).hexdigest()[:16])
        except Exception as e:  # noqa: BLE001
            if getattr(e, "infrastructure_failure", False):
                raise
            vec.append(f"ERR:{type(e).__name__}")
    return vec


def behaviour_similarity(a: List[str], b: List[str]) -> float:
    """Crashes never count as agreement, so two broken tools are not 'similar'."""
    return sum(1 for x, y in zip(a, b) if x == y and not x.startswith("ERR:")) / max(1, len(a))


def behaviour_signature(tool_fn: Callable[[Table, Table], Table], probe: str, seeds: Optional[List[int]] = None) -> str:
    """Output fingerprint on a probe set: used for the repulsion signal (probe='signal')
    and for M5 clustering (probe='diversity'). Never mix the two sets."""
    lo, hi = SEED_RANGES[probe]
    seeds = seeds or list(range(lo, lo + PROBES_PER_SET))
    outs = []
    for s in seeds:
        try:
            got = tool_fn(gen_table(s), gen_lookup(s))
            outs.append(json.dumps(got, sort_keys=True, default=str)[:4000])
        except Exception as e:  # noqa: BLE001
            if getattr(e, "infrastructure_failure", False):
                raise
            outs.append(f"ERR:{type(e).__name__}")
    return hashlib.sha256("|".join(outs).encode()).hexdigest()


if __name__ == "__main__":
    dev = tasks(0, "dev")
    test = tasks(0, "test")
    print(f"dev tasks: {len(dev)}  test tasks: {len(test)}")
    print("test seal:", seal_hash(test))
    t = dev[25]
    print(t.id, t.primitive_set)
    print(t.spec)
    # Reference must pass its own harness; a wrong tool must fail.
    assert harness(lambda tb, lk: t.reference(tb, lk), t).passed
    assert not harness(lambda tb, lk: tb, t).passed or t.steps == []
    for name, (fn, _, _) in PRIMITIVES.items():
        assert verify_primitive(fn, name).passed, name
    print("self-checks passed")
