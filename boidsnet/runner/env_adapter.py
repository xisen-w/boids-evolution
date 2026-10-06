"""Adapter from the runner to the mechanism env (mechenv.py, art_MVkfBKAjhF,
owned by i_alx4y9xgu1).  The runner touches the env only through this class.

- dev tasks come from ONE fixed dev seed shared by every society, so all arms
  see the same task menu; the society seed only drives agents and RNG.
- The sealed test split is never requested here.
- The repulsion signal uses mechenv.behaviour_vector on P_signal (one hash
  per probe) and mechenv.behaviour_similarity (crashes never agree).
  behaviour_signature is for M5 at analysis time and is not used here.
- Each agent-round sees a seeded sample of `menu_size` dev tasks; the draw
  depends only on (society seed, agent, round), so it is identical across
  arms.
"""
import hashlib
import importlib.util
import json
import random
import sys
import copy
from dataclasses import asdict

CONTRACT = (
    "A tool is a module defining execute(table, lookup, **params) -> table. "
    "Both table and lookup are lists of dict rows, not dictionaries keyed by region. "
    "Table row values are float, str or None. Each lookup row has region (str), "
    "target (float), and manager (str); iterate its rows to find an exact region "
    "match. Do not mutate either input. Tools that implement a single "
    "primitive take that primitive's parameters as keyword arguments."
)


def load_module(path, name="mechenv"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclasses need the module registered
    spec.loader.exec_module(mod)
    return mod


class MechEnv:
    def __init__(self, path, dev_seed=0):
        self.m = load_module(path)
        self.path = path
        self.dev_seed = dev_seed
        with open(path, "rb") as f:
            self.file_sha256 = hashlib.sha256(f.read()).hexdigest()
        self.name = f"mechenv@{self.file_sha256[:12]}"
        lo, _ = self.m.SEED_RANGES["signal"]
        self.signal_seeds = list(range(lo, lo + self.m.PROBES_PER_SET))
        self.primitives = sorted(self.m.PRIMITIVES)

    def dev_tasks(self):
        out = []
        for t in self.m.tasks(self.dev_seed, "dev"):
            out.append({"id": t.id, "spec": t.spec, "depth": t.depth,
                        "primitive_set": t.primitive_set, "obj": t})
        return out

    FEEDBACK_ROWS = 5
    FEEDBACK_CHARS = 600

    def public_example_seed(self, rnd):
        """Pre-listed public input for round `rnd`, from the DEV seed range
        (never a probe set); the same list in every arm and society.  Rotated
        per round (msg #73 B4/#76.4) so tools are not tuned to one table."""
        return self.m.SEED_RANGES["dev"][0] + 7 + 101 * rnd

    def exec_feedback(self, tool, rnd=0, params=None):
        """D9: run the tool on one public dev example; return the exception
        or the first rows.  No pass/fail, no reference output, no P_coverage."""
        s = self.public_example_seed(rnd)
        call = {"args": [self.m.gen_table(s), self.m.gen_lookup(s)], "kwargs": copy.deepcopy(params or {})}
        y = tool.prefetch([call])[0]
        if isinstance(y, dict) and "__error__" in y:
            text = "raised " + y["__error__"]
        elif isinstance(y, list):
            text = f"returned {len(y)} rows; first {self.FEEDBACK_ROWS}: " + json.dumps(y[:self.FEEDBACK_ROWS], sort_keys=True)
        else:
            text = "returned non-table value: " + json.dumps(y)[:200]
        return text[:self.FEEDBACK_CHARS]

    def signal_calls(self, params=None):
        return [{"args": [self.m.gen_table(s), self.m.gen_lookup(s)], "kwargs": copy.deepcopy(params or {})}
                for s in self.signal_seeds]

    def menu(self, society_seed, agent, rnd, all_tasks, menu_size):
        rng = random.Random(f"menu:{society_seed}:{agent}:{rnd}")
        return sorted(rng.sample(all_tasks, min(menu_size, len(all_tasks))), key=lambda t: t["id"])

    def signature(self, tool, params=None):
        """Per-probe output hashes on P_signal ('ERR:<type>' for crashes)."""
        tool.prefetch(self.signal_calls(params))
        bound = (lambda table, lookup: tool(table, lookup, **copy.deepcopy(params))) if params else tool
        return self.m.behaviour_vector(bound, "signal", self.signal_seeds)

    def similarity(self, a, b):
        if not a or not b or len(a) != len(b):
            return 0.0
        return self.m.behaviour_similarity(a, b)

    def verify_primitive(self, tool, primitive):
        """mechenv.verify_primitive on P_coverage.  The calls are prefetched in
        one subprocess by replaying mechenv's own seeding; if that replay ever
        drifts from mechenv, the cache simply misses and correctness holds."""
        import zlib
        if primitive not in self.m.PRIMITIVES:
            return {"passed": False, "reason": "unknown primitive"}
        _, sampler, _ = self.m.PRIMITIVES[primitive]
        lo, _hi = self.m.SEED_RANGES["coverage"]
        rng = random.Random(zlib.crc32(primitive.encode()) % 10_007 + lo)
        calls = []
        for _ in range(3):
            params = sampler(rng)
            for s in [rng.randrange(lo, _hi) for _ in range(self.m.PROBES_PER_SET // 2)]:
                calls.append({"args": [self.m.gen_table(s), [dict(r) for r in self.m.gen_lookup(s)]],
                              "kwargs": params})
        tool.prefetch(calls)
        return asdict(self.m.verify_primitive(tool, primitive, "coverage"))

    def harness(self, tool, task, params=None):
        t = task["obj"]
        params = copy.deepcopy(params or {})
        calls = [{"args": [self.m.gen_table(s), [dict(r) for r in self.m.gen_lookup(s)]], "kwargs": copy.deepcopy(params)}
                 for s in t.probe_seeds["coverage"]]
        tool.prefetch(calls)
        bound = (lambda table, lookup: tool(table, lookup, **copy.deepcopy(params))) if params else tool
        return asdict(self.m.harness(bound, t, "coverage"))
