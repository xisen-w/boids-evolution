"""U = frozen-library utility on the SEALED test split (protocol primary).

    python -m boidsnet.runner.utility --society runs/L0_s1001 --unseal [--attempts 3] [model flags]

Pre-registered rules (msgs #73 B1/B3, #76.1/#76.3):
- Freeze L_T the SAME way in every arm: take every tool the society built;
  drop tools whose P_signal vector crashed on every probe; group the rest by
  identical P_signal vector; keep per group the earliest (round, id) tool that
  passed its dev target, else the earliest tool.  The frozen directory also
  holds the transitive import dependencies of kept tools (so they run), but
  only kept tools are listed to the solver and importable by its glue.
- Solver: sees ONE test task spec (never probe tables) plus the catalogue
  (id, description, execute signature, IMPLEMENTS), and must answer with
  `from tools import ...` lines and one `def execute(table, lookup, **params)`
  whose body has only assignments of names, `return`, and calls of
  `<tool>.execute(...)` with names/constants as arguments.  No other
  statements, no loops/comprehensions/conditionals/arithmetic/subscripts,
  no builtins, getattr/__import__/importlib/eval/open, and every name must be
  bound by a from-tools-import line, by execute's parameters, or by an
  earlier assignment.  At most 15 non-blank lines.  A gate failure scores 0
  for that attempt and is logged with its reason.
- Scoring: mechenv.harness(glue, task, probe='coverage') on tasks(0,'test')
  whose seal must equal the published one.  Each task gets R attempts; task
  score = MEAN pass over attempts (not max); U = mean over test tasks.
- The test split is opened only with --unseal, which the pilot, the smoke
  test and the batch runner never pass.
"""
import argparse
import ast
import json
import os
import re
import shutil
import sys

from .env_adapter import MechEnv
from .exposure import summarise
from .sandbox import SandboxedTool

def _sha(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def _write_private_audit(path, row):
    """Retain replay evidence outside the tool-visible library, owner-only."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(row, f, indent=1)
        f.write("\n")


LEGACY_TEST_SEAL = "25634f7783fffbac3c2e1f74c545c2f647806218173b1af2dd3e2f1393c82371"
# v0.2.2 changes ONLY test coverage seeds (specs/dev probes unchanged).
# This is a candidate seal, not a claim of joint preregistration. Real test
# scoring still requires the separately reviewed confirmatory freeze.
PUBLISHED_TEST_SEAL = "c9f634ae53c8f62694aed012f83520b53541175462552afdac5d1e40c93b7c0d"
MAX_GLUE_LINES = 15
MAX_STR_CONST = 32            # msg #79.2 anti-interpreter caps
MAX_CONST_PAYLOAD = 128
FORBIDDEN_NAMES = {"getattr", "setattr", "__import__", "importlib", "eval", "exec", "open",
                   "compile", "globals", "locals", "vars", "__builtins__"}

SOLVER_SYSTEM = (
    "You solve a table-transform task by composing tools from a fixed library. "
    "You may NOT write any transformation logic yourself: your answer may only import "
    "library tools and chain their execute() calls."
)
SOLVER_FORMAT = (
    "Answer with one ```python block containing only:\n"
    "  from tools import <tool_id>[, <tool_id>...]\n"
    "  def execute(table, lookup, **params):\n"
    "      <name> = <tool_id>.execute(<args>)   # args: table, lookup, earlier names, constants\n"
    "      return <name>\n"
    f"No loops, conditionals, arithmetic, indexing, builtins or other code. At most {MAX_GLUE_LINES} lines."
)


# --------------------------------------------------------------------------
# Freezing L_T
# --------------------------------------------------------------------------
def freeze_library(society_dir, out_dir, env=None):
    """See module docstring.  `env` is needed to verify parametric tools
    (msg #79.1); without it parametric tools cannot be recovered."""
    src = os.path.join(society_dir, "library")
    with open(os.path.join(src, "index.json")) as f:
        index = json.load(f)
    with open(os.path.join(src, "acl.json")) as f:
        acl = json.load(f)
    groups = {}
    dropped_crash, parametric, verified_log = [], set(), {}
    for e in sorted(index.values(), key=lambda e: (e["round"], e["id"])):
        sig = e.get("signature_signal") or []
        if sig and not all(str(x).startswith("ERR") for x in sig):
            groups.setdefault(("sig", tuple(sig)), []).append(e)
            continue
        # All-ERR on P_signal: P_signal calls tools WITHOUT params, so a
        # parametric building block (e.g. filter(col, op, value)) looks like a
        # crash.  Keep it if it verifies >=1 declared IMPLEMENTS primitive.
        ok = []
        if env is not None:
            for prim in e.get("implements") or []:
                v = env.verify_primitive(SandboxedTool(src, e["id"]), prim)
                verified_log.setdefault(e["id"], {})[prim] = bool(v.get("passed"))
                if v.get("passed"):
                    ok.append(prim)
        if ok:
            parametric.add(e["id"])
            groups.setdefault(("prims", frozenset(ok)), []).append(e)
        else:
            dropped_crash.append(e["id"])
    kept = []
    for members in groups.values():
        passing = [e for e in members if (e.get("harness") or {}).get("passed")]
        kept.append((passing or members)[0])
    kept.sort(key=lambda e: (e["round"], e["id"]))
    kept_ids = [e["id"] for e in kept]
    # Include the historical ACL closure, not only statically visible imports:
    # valid tools can import a dependency lazily through importlib. Dependency-
    # only modules remain unavailable to solver glue and are not counted as reuse.
    need, todo = set(kept_ids), list(kept_ids)
    while todo:
        for d in acl.get(todo.pop(), []):
            if d in index and d not in need:
                need.add(d)
                todo.append(d)
    os.makedirs(os.path.join(out_dir, "tools"), exist_ok=True)
    open(os.path.join(out_dir, "tools", "__init__.py"), "w").close()
    for t in sorted(need):
        shutil.copy2(os.path.join(src, "tools", t + ".py"), os.path.join(out_dir, "tools", t + ".py"))
    frozen_acl = {t: acl.get(t, []) for t in need}
    with open(os.path.join(out_dir, "acl.json"), "w") as f:
        json.dump(frozen_acl, f, sort_keys=True)
    meta = {"kept": kept_ids, "kept_parametric": sorted(parametric & set(kept_ids)),
            "verified_primitives": verified_log,
            "parametric_share": (len(parametric & set(kept_ids)) / len(kept_ids)) if kept_ids else 0.0,
            "dependency_only": sorted(need - set(kept_ids)),
            "dropped_all_crash": dropped_crash,
            "dropped_duplicate": sorted(set(index) - set(kept_ids) - set(dropped_crash)),
            "n_built": len(index)}
    with open(os.path.join(out_dir, "freeze.json"), "w") as f:
        json.dump(meta, f, indent=1)
    return [e for e in kept], frozen_acl, meta


# --------------------------------------------------------------------------
# Glue gate
# --------------------------------------------------------------------------
_CODE = re.compile(r"```python\s*\n(.*?)```", re.S)


def glue_gate(source, catalogue_ids):
    """Return (ok, reason, imported_ids)."""
    if source is None:
        return False, "no python block", []
    lines = [l for l in source.splitlines() if l.strip()]
    if len(lines) > MAX_GLUE_LINES:
        return False, f"{len(lines)} lines > {MAX_GLUE_LINES}", []
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return False, f"syntax error: {e.msg}", []
    imported, funcs = [], []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "tools" and node.level == 0:
            for a in node.names:
                if a.asname is not None:
                    return False, "aliased import", []
                if a.name not in catalogue_ids:
                    return False, f"{a.name} is not in the library", []
                imported.append(a.name)
        elif isinstance(node, ast.FunctionDef) and node.name == "execute":
            funcs.append(node)
        else:
            return False, f"module-level {type(node).__name__} not allowed", []
    if len(funcs) != 1:
        return False, "need exactly one def execute", []
    fn = funcs[0]
    if fn.decorator_list:
        return False, "decorators not allowed", []
    if (fn.args.defaults or any(v is not None for v in fn.args.kw_defaults)
            or fn.returns is not None
            or any(a.annotation is not None for a in fn.args.args + fn.args.posonlyargs + fn.args.kwonlyargs)
            or (fn.args.kwarg and fn.args.kwarg.annotation is not None)):
        return False, "defaults and annotations may execute code; not allowed", []
    if (fn.args.posonlyargs or [a.arg for a in fn.args.args] != ["table", "lookup"]
            or fn.args.kwonlyargs or fn.args.vararg
            or (fn.args.kwarg and fn.args.kwarg.arg != "params")):
        return False, "execute signature must be (table, lookup[, **params])", []
    if set(imported) & {"table", "lookup", "params"}:
        return False, "tool import shadows an input", []
    bound = set(imported) | {a.arg for a in fn.args.args + fn.args.kwonlyargs}
    if fn.args.kwarg:
        bound.add(fn.args.kwarg.arg)
    if fn.args.vararg:
        return False, "*args not allowed", []

    def check_expr(x):
        if isinstance(x, ast.Constant):
            return None
        if isinstance(x, ast.Name):
            if x.id in FORBIDDEN_NAMES or x.id not in bound:
                return f"name {x.id!r} is not bound by tools/params/assignments"
            return None
        if isinstance(x, (ast.List, ast.Tuple)):
            for el in x.elts:
                if not isinstance(el, ast.Constant):
                    return "only constant lists/tuples allowed as arguments"
            return None
        if isinstance(x, ast.Dict):
            for k, v in zip(x.keys, x.values):
                if not (isinstance(k, ast.Constant) and isinstance(v, (ast.Constant, ast.List))):
                    return "only constant dicts allowed as arguments"
                if isinstance(v, ast.List) and not all(isinstance(el, ast.Constant) for el in v.elts):
                    return "only constant dicts allowed as arguments"
            return None
        if isinstance(x, ast.Call):
            f = x.func
            if not (isinstance(f, ast.Attribute) and f.attr == "execute"
                    and isinstance(f.value, ast.Name) and f.value.id in imported):
                return "only <library tool>.execute(...) calls are allowed"
            for a in x.args:
                r = check_expr(a)
                if r:
                    return r
            for kw in x.keywords:
                if kw.arg is None:
                    return "**kwargs unpacking not allowed"
                r = check_expr(kw.value)
                if r:
                    return r
            return None
        return f"expression {type(x).__name__} not allowed"

    calls = 0
    derived = set()  # names whose CURRENT value is a library call result

    def library_result(expr):
        return isinstance(expr, ast.Call) or (isinstance(expr, ast.Name) and expr.id in derived)

    for st in fn.body:
        if isinstance(st, ast.Assign):
            if len(st.targets) != 1 or not isinstance(st.targets[0], ast.Name):
                return False, "only simple name assignments allowed", []
            if st.targets[0].id in FORBIDDEN_NAMES:
                return False, "forbidden name assigned", []
            if st.targets[0].id in imported:
                return False, "cannot rebind an imported tool", []
            r = check_expr(st.value)
            if r:
                return False, r, []
            calls += isinstance(st.value, ast.Call)
            is_result = library_result(st.value)
            derived.discard(st.targets[0].id)
            if is_result:
                derived.add(st.targets[0].id)
            bound.add(st.targets[0].id)
        elif isinstance(st, ast.Return):
            if st is not fn.body[-1]:
                return False, "return must be the last statement", []
            if st.value is None:
                return False, "return value required", []
            r = check_expr(st.value)
            if r:
                return False, r, []
            calls += isinstance(st.value, ast.Call)
            if not library_result(st.value):
                return False, "return must be derived from a library execute result", []
        elif isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant):
            continue                      # docstring
        else:
            return False, f"statement {type(st).__name__} not allowed in execute", []
    if calls == 0:
        return False, "glue calls no library tool", []
    if not fn.body or not isinstance(fn.body[-1], ast.Return):
        return False, "glue must return its result", []
    payload = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node is (fn.body[0].value if fn.body and isinstance(fn.body[0], ast.Expr) else None):
                continue                  # docstring does not count
            if len(node.value) > MAX_STR_CONST:
                return False, f"string constant longer than {MAX_STR_CONST} chars", []
            payload += len(node.value)
        elif isinstance(node, ast.Constant) and node.value is not None:
            payload += len(repr(node.value))
    if payload > MAX_CONST_PAYLOAD:
        return False, f"constant payload {payload} > {MAX_CONST_PAYLOAD}", []
    return True, "ok", imported


def const_payload(source):
    """Descriptive (msg #79.2): (n tool calls, longest string constant)."""
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return 0, 0
    calls = sum(isinstance(n, ast.Call) for n in ast.walk(tree))
    longest = max([len(n.value) for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, str)] or [0])
    return calls, longest


# --------------------------------------------------------------------------
# Solver + scoring
# --------------------------------------------------------------------------
def solver_prompt(task, kept, source_of, attempt=0, society_seed=0):
    """v0.3.10 (msg #82 A'): catalogue FIRST, task spec LAST, so all tasks in
    one (society, attempt) share a cacheable prefix.  The catalogue order is
    shuffled once per (society seed, attempt) with a fixed seed; the seed does
    not depend on the arm, so the draw is identical across arms.  Position bias
    is still randomised across attempts."""
    import random as _r
    order = sorted(kept, key=lambda e: e["id"])
    _r.Random(f"solver:{society_seed}:{attempt}").shuffle(order)
    lines = ["Library:"]
    for e in order:
        lines.append(summarise(e, source_of(e["id"])))
    if not kept:
        lines.append("(empty)")
    lines += ["", SOLVER_FORMAT, "", f"TASK: {task.spec}"]
    return "\n".join(lines)


def gate_reason_class(reason):
    """Coarse class of a glue_gate reason, for per-arm tallies (msg #82 B')."""
    if reason is None:
        return "ok"
    r = re.sub(r"\d+", "N", reason)
    r = re.sub(r"^\w+ is not in the library$", "import not in library", r)
    return r.split(":")[0]


def society_seed_of(society_dir, man):
    seed = (man.get("config") or {}).get("seed", man.get("seed"))
    if seed is None:
        m = re.search(r"_s(\d+)$", os.path.basename(os.path.normpath(society_dir)))
        seed = int(m.group(1)) if m else 0
    return seed


def check_sampling(society_dir, model, split="test"):
    """S1 / msg #79.4: the solver must use the society's sampling block.
    Engineering societies (pre-freeze smoke, msg #96.3) may have adapted
    parameters in auto mode; for them, and ONLY on the dev split, the solver
    must match the EFFECTIVE (post-adaptation) block the society recorded,
    still in strict mode.  Engineering societies can never be scored on test."""
    path = os.path.join(society_dir, "run_manifest.json")
    is_stub = not hasattr(model, "send_temperature")
    if not os.path.exists(path):
        if is_stub:
            return {}
        raise SystemExit("no run_manifest.json: cannot check the sampling block")
    with open(path) as f:
        man = json.load(f)
    if man.get("engineering") and split != "dev":
        raise SystemExit("engineering (pre-freeze) society: only --split dev is allowed")
    samp = man.get("sampling") or {}
    if is_stub:
        return man
    if samp.get("param_adaptations") and not (man.get("engineering") and split == "dev"):
        raise SystemExit("society ran with adapted params (auto mode); confirmatory scoring needs strict")
    want = (samp.get("temperature_sent"), samp.get("token_param"))
    have = (model.send_temperature, model.token_param)
    if want != have or getattr(model, "param_mode", None) != "strict":
        raise SystemExit(f"solver sampling {have} (mode {model.param_mode}) != society {want} (strict)")
    if man.get("model") != model.name:
        raise SystemExit(f"solver deployment {model.name} != society {man.get('model')}")
    if man.get("arm") in ("000", "100", "011", "111"):
        for key in ("thinking", "base_url"):
            if samp.get(key) != getattr(model, key, None):
                raise SystemExit(f"solver {key} differs from society")
    return man


def score_society(society_dir, env, model, attempts=3, out_name=None, temperature=0.7,
                  max_tokens=4000, split="test", token_budget=None, task_ids=None):
    """split='test' is the confirmatory U (needs the published seal).
    split='dev' is a DIAGNOSTIC (U_dev): same freeze, gate and scoring on the
    dev tasks the agents saw.  It opens nothing sealed, so the smoke test can
    measure solver cost and gate-failure rates on the real deployment.  U_dev
    is inflated by construction and is never reported as an outcome."""
    if split not in ("test", "dev"):
        raise ValueError(split)
    if attempts < 1:
        raise ValueError("attempts must be positive")
    if task_ids is not None and split != "dev":
        raise ValueError("task subsets are allowed only for development diagnostics")
    if token_budget is not None and split == "test":
        # a cap would drop the last tasks of the sealed split and bias U
        raise ValueError("token_budget is for the dev diagnostic only; confirmatory U scores every task")
    out_name = out_name or ("utility" if split == "test" else "utility_dev")
    if not hasattr(model, "solve"):              # real solver: library tools run with the key in this process
        from .sandbox import isolation_level
        if not isolation_level().startswith("os-"):
            raise SystemExit(f"refusing real-model scoring: sandbox isolation is {isolation_level()!r} (msg #102)")
    man = check_sampling(society_dir, model, split)
    if man.get("temperature") is not None:
        temperature = man["temperature"]
    out = os.path.join(society_dir, out_name)
    if os.path.exists(out):
        raise SystemExit(f"refusing to overwrite {out}")
    lib = os.path.join(out, "frozen_library")
    kept, acl, meta = freeze_library(society_dir, lib, env)
    kept_ids = [e["id"] for e in kept]

    def source_of(tid):
        with open(os.path.join(lib, "tools", tid + ".py")) as f:
            return f.read()

    if split == "test":
        test = env.m.tasks(0, "test")              # the ONLY test-split access in the codebase
        seal = env.m.seal_hash(test)
        if seal != PUBLISHED_TEST_SEAL:
            raise SystemExit(f"test seal {seal} != published {PUBLISHED_TEST_SEAL}")
    else:
        test = env.m.tasks(env.dev_seed, "dev")
        if task_ids is not None:
            by_id = {t.id: t for t in test}
            if not task_ids or len(set(task_ids)) != len(task_ids) or not set(task_ids) <= set(by_id):
                raise ValueError("dev task_ids must be a nonempty, unique subset of the fixed dev set")
            test = [by_id[t] for t in task_ids]
        seal = env.m.seal_hash(test)
    sseed = society_seed_of(society_dir, man)
    log_path = os.path.join(out, "solver_log.jsonl")
    with open(log_path, "x"):
        pass
    audit_dir = os.path.join(out, "private_audit")
    if split == "dev":
        os.mkdir(audit_dir, mode=0o700)
    task_scores, tokens, cached, single_big = [], 0, 0, []
    truncated = False
    for ti, task in enumerate(test):
        if token_budget is not None and tokens >= token_budget:
            truncated = True          # hard cost cap (smoke): stop before the next task; overshoot <= 1 task
            break
        passes = []
        for k in range(attempts):
            prompt = solver_prompt(task, kept, source_of, k, sseed)
            audit_path = os.path.join(audit_dir, f"task_{ti:03d}_attempt_{k}.json")
            audit = {"status": "REQUEST_PENDING", "task": task.id, "attempt": k,
                     "system": SOLVER_SYSTEM, "prompt": prompt, "task_spec": task.spec,
                     "coverage_probe_seeds": task.probe_seeds["coverage"], "society_seed": sseed,
                     "temperature": temperature, "max_tokens": max_tokens, "split_seal": seal}
            if split == "dev":
                _write_private_audit(audit_path, audit)
            text, tin, tout = model.complete(SOLVER_SYSTEM, prompt, temperature, max_tokens) \
                if not hasattr(model, "solve") else model.solve(task, kept, k)
            tcached = getattr(model, "last_cached_tokens", None)
            tokens += tin + tout
            cached += tcached or 0
            m = _CODE.search(text)
            code = m.group(1) if m else None
            ok, reason, imported = glue_gate(code, set(kept_ids))
            audit.update(status="RESPONSE_RECEIVED", response=text, code=code, imported=imported,
                         gate_ok=ok, gate_reason=reason, tokens_in=tin, tokens_out=tout,
                         tokens_cached=tcached,
                         response_metadata=getattr(model, "last_response_metadata", None))
            if split == "dev":
                _write_private_audit(audit_path, audit)
            verdict = None
            if ok:
                gid = f"solver_t{ti:03d}_k{k}"
                with open(os.path.join(lib, "tools", gid + ".py"), "w") as f:
                    f.write(code)
                acl[gid] = imported
                with open(os.path.join(lib, "acl.json"), "w") as f:
                    json.dump(acl, f, sort_keys=True)
                verdict = env.harness(SandboxedTool(lib, gid), {"obj": task})
            passed = bool(verdict and verdict["passed"])
            passes.append(1.0 if passed else 0.0)
            n_calls, longest = const_payload(code)
            single_big.append(ok and n_calls == 1 and longest > MAX_STR_CONST // 2)
            row = {"task": task.id, "depth": task.depth, "attempt": k, "gate_ok": ok,
                   "n_tool_calls": n_calls, "longest_str_const": longest,
                   "gate_reason": reason, "imported": imported,
                   "tokens_in": tin, "tokens_out": tout,
                   "tokens_cached": tcached, "prompt_sha256": _sha(prompt)}
            row["response_metadata"] = getattr(model, "last_response_metadata", None)
            if split == "test":
                row.update(passed=passed, verdict=verdict, response=text)
            else:
                # Keep the public diagnostic summary blinded, but retain full
                # owner-only evidence for pipeline auditing. This is NOT a
                # claim that the run owner cannot unblind their private traces.
                audit.update(status="SCORED", passed=passed, verdict=verdict)
                _write_private_audit(audit_path, audit)
                if not ok:
                    row["response"] = text
                if ok:
                    row.pop("imported")          # imported ids + task would let anyone rebuild the glue
                    os.remove(os.path.join(lib, "tools", gid + ".py"))
                    acl.pop(gid, None)
                    with open(os.path.join(lib, "acl.json"), "w") as f:
                        json.dump(acl, f, sort_keys=True)
            with open(log_path, "a") as log:
                log.write(json.dumps(row) + "\n")
        task_scores.append(sum(passes) / len(passes))
    with open(os.path.join(out, "solver_log.jsonl")) as fh:
        rows = [json.loads(l) for l in fh]
    gate_fail = sum(not r["gate_ok"] for r in rows) / len(rows) if rows else 0.0
    reasons = {}
    for r in rows:
        if not r["gate_ok"]:
            c = gate_reason_class(r["gate_reason"])
            reasons[c] = reasons.get(c, 0) + 1
    n_calls = len(rows)
    res = {"split": split, "n_tasks": len(test), "n_tasks_scored": len(task_scores),
           "task_ids": [t.id for t in test], "diagnostic_only": split == "dev",
           "solver_truncated_by_budget": truncated, "solver_token_budget": token_budget, "attempts": attempts,
           "gate_fail_rate": gate_fail, "gate_fail_reasons": dict(sorted(reasons.items())),
           "test_seal": seal, "library": meta, "solver_tokens": tokens,
           "solver_calls": n_calls, "solver_tokens_per_call": tokens / n_calls if n_calls else 0.0,
           "solver_cached_tokens": cached,
           "parametric_share": meta["parametric_share"],
           "single_call_long_payload_share": (sum(single_big) / len(single_big)) if single_big else 0.0}
    if split == "test":
        by_depth = {}
        for task, s in zip(test, task_scores):
            by_depth.setdefault(task.depth, []).append(s)
        res["U"] = sum(task_scores) / len(task_scores)
        res["U_by_depth"] = {d: sum(v) / len(v) for d, v in sorted(by_depth.items())}
    else:
        # msg #82 B': per-arm U_dev is never written or printed (it would be a
        # pre-freeze peek at the outcome).  The task scores go back in memory
        # only, for the POOLED diagnostic in runner.pilot.
        res["_dev_task_scores"] = task_scores
    with open(os.path.join(out, "utility.json"), "w") as f:
        json.dump({k: v for k, v in res.items() if not k.startswith("_")}, f, indent=1)
    return res


class StubSolver:
    """Dry-run solver: if a library tool's description names exactly the
    task's primitive pipeline it calls that tool, otherwise it calls the first
    tool.  Mechanics only: it reads no probe data."""

    def __init__(self):
        self.last_retries = 0

    def solve(self, task, kept, k):
        want = "pipeline " + " -> ".join(n for n, _ in task.steps)
        pick = next((e["id"] for e in kept if e.get("description") == want), None) \
            or (kept[0]["id"] if kept else None)
        if pick is None:
            return "no library", 0, 0
        code = (f"from tools import {pick}\n"
                "def execute(table, lookup, **params):\n"
                f"    out = {pick}.execute(table, lookup)\n"
                "    return out\n")
        return f"```python\n{code}```", 0, 0


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--society", required=True)
    p.add_argument("--unseal", action="store_true", help="required for --split test: opens the sealed test split")
    p.add_argument("--split", default="test", choices=("test", "dev"),
                   help="dev = diagnostic U_dev for smoke tests (no unsealing)")
    p.add_argument("--attempts", type=int, default=3)
    p.add_argument("--env-path", default=None)
    p.add_argument("--model", default="stub")
    p.add_argument("--key-env", default="OPENAI_API_KEY")
    p.add_argument("--base-url", default=None)
    p.add_argument("--thinking", choices=("disabled",), default=None)
    p.add_argument("--azure-endpoint", default=os.environ.get("AZURE_OPENAI_ENDPOINT"))
    p.add_argument("--azure-api-version", default=os.environ.get("AZURE_OPENAI_API_VERSION"))
    p.add_argument("--allow-spend", action="store_true")
    p.add_argument("--no-temperature", action="store_true")
    p.add_argument("--token-param", default="max_tokens", choices=("max_tokens", "max_completion_tokens"))
    p.add_argument("--max-tokens", type=int, default=4000)
    a = p.parse_args(argv)
    if a.model.startswith("deepseek"):
        sys.exit("DeepSeek scoring must use the reviewed dev-only boidsnet.runner.sac_pilot entry point")
    if a.split == "test" and not a.unseal:
        sys.exit("refusing: U opens the sealed test split; pass --unseal only for confirmatory scoring")
    from .run import DEFAULT_ENV
    env = MechEnv(a.env_path or DEFAULT_ENV)
    if a.model == "stub":
        model = StubSolver()
    else:
        from .model import OpenAICompatModel
        model = OpenAICompatModel(a.model, a.key_env, a.allow_spend, azure_endpoint=a.azure_endpoint,
                                  api_version=a.azure_api_version, send_temperature=not a.no_temperature,
                                  token_param=a.token_param, param_mode="strict", base_url=a.base_url,
                                  thinking=a.thinking)
    res = score_society(a.society, env, model, a.attempts, max_tokens=a.max_tokens, split=a.split)
    print(json.dumps({k: v for k, v in res.items() if k != "library" and not k.startswith("_")}, indent=1))


if __name__ == "__main__":
    main()
