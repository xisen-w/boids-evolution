"""One independent society: N agents, T synchronous rounds, one arm.

Round semantics (pre-register): rounds are synchronous.  Every agent in
round r sees the library as it stood at the END of round r-1; tools built in
round r become importable and listed from round r+1.  Agents act in a
seeded-shuffled order, but since they all read the same snapshot, order has
no effect on what they see.

Per agent-round, one JSONL record is written to rounds.jsonl with every rule
flag (did an exemplar block fire, which tools, what similarity, what mode),
token counts and the harness verdict; the full prompt and response go to
prompts/.  Nothing in this module reads the sealed test split.
"""
import hashlib
import json
import os
import random
import time

from .exposure import ring_neighbours, select_exemplars, select_matched, render_block
from .library import Library
from .prompts import SYSTEM, build_user_prompt, parse_response
from .sandbox import SandboxedTool


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


class Society:
    def __init__(self, cfg, env, model, out_dir):
        self.cfg, self.env, self.model = cfg, env, model
        self.out = out_dir
        os.makedirs(os.path.join(out_dir, "prompts"), exist_ok=True)
        self.lib = Library(os.path.join(out_dir, "library"))
        self.rng = random.Random(f"society:{cfg.seed}")
        self.dev_tasks = env.dev_tasks()          # fixed dev seed; never "test"
        self.task_by_id = {t["id"]: t for t in self.dev_tasks}
        self.feedback = {}      # agent -> {tool_id, text} from its previous build (D9)
        self.tokens = 0
        self.truncated = False
        self.log = open(os.path.join(out_dir, "rounds.jsonl"), "w")

    # -- helpers -----------------------------------------------------------
    def _source(self, tool_id):
        with open(os.path.join(self.lib.pkg, f"{tool_id}.py")) as f:
            return f.read()

    def _pool(self, agent, snapshot, rnd=0):
        others = [e for e in snapshot if e["author"] != agent]
        if self.cfg.exemplar_scope == "local":
            nb = set(ring_neighbours(agent, self.cfg.n_agents, self.cfg.k))
            return [e for e in others if e["author"] in nb], sorted(nb)
        if self.cfg.exemplar_scope == "global":
            return others, None
        if self.cfg.exemplar_scope == "matched":
            nb = set(ring_neighbours(agent, self.cfg.n_agents, self.cfg.k))
            return ([e for e in others if e["author"] in nb],
                    [e for e in others if e["author"] not in nb]), sorted(nb)
        if self.cfg.exemplar_scope == "random":
            rng = random.Random(f"randnb:{self.cfg.seed}:{agent}:{rnd}")
            cand = [a for a in range(self.cfg.n_agents) if a != agent]
            nb = set(rng.sample(cand, self.cfg.k))
            return [e for e in others if e["author"] in nb], sorted(nb)
        return [], None

    # -- main loop ---------------------------------------------------------
    def run(self):
        cfg = self.cfg
        for rnd in range(1, cfg.n_rounds + 1):
            snapshot = [dict(e) for e in self.lib.entries.values()]
            order = list(range(cfg.n_agents))
            self.rng.shuffle(order)
            built = []
            for agent in order:
                if cfg.token_budget is not None and self.tokens >= cfg.token_budget:
                    self.truncated = True
                    break
                built.append(self._agent_turn(agent, rnd, snapshot))
            for rec, entry in built:
                self._evaluate(rec, entry)
                self.log.write(json.dumps(rec, sort_keys=True) + "\n")
            self.log.flush()
            if self.truncated:
                break
        self.log.close()
        return self._summary()

    def _agent_turn(self, agent, rnd, snapshot):
        cfg = self.cfg
        t0 = time.time()
        agent_rng = random.Random(f"{cfg.seed}:{agent}:{rnd}")
        catalogue = ([e for e in snapshot if e["author"] == agent]
                     if cfg.catalogue_scope == "self" else snapshot)
        pool, neighbours = self._pool(agent, snapshot, rnd)
        own = [e for e in snapshot if e["author"] == agent]
        own_latest = max(own, key=lambda e: e["round"]) if own else None
        match = None
        if cfg.framing is None:
            chosen, sims, mode = [], [], "no_exposure_arm"
        elif cfg.exemplar_scope == "matched":
            ring_pool, other_pool = pool
            chosen, sims, mode, match = select_matched(ring_pool, other_pool, own_latest, cfg.m,
                                                       agent_rng, self.env.similarity)
            pool = other_pool
        else:
            chosen, sims, mode = select_exemplars(agent, pool, own_latest, cfg.m, agent_rng,
                                                  self.env.similarity)
        block = render_block(cfg.framing, chosen, self._source)
        menu = self.env.menu(cfg.seed, agent, rnd, self.dev_tasks, cfg.menu_size)
        fb = self.feedback.get(agent)
        user = build_user_prompt(rnd, menu, catalogue, block, fb)
        text, tin, tout = self.model.complete(SYSTEM, user, cfg.temperature, cfg.max_tokens_per_call)
        self.tokens += tin + tout
        retries = getattr(self.model, "last_retries", 0)
        parsed = parse_response(text, self.env.primitives)
        tool_id = self.lib.make_id(agent, rnd)
        with open(os.path.join(self.out, "prompts", f"{tool_id}.json"), "w") as f:
            json.dump({"system": SYSTEM, "user": user, "response": text}, f, indent=1)
        rec = {
            "arm": cfg.arm, "seed": cfg.seed, "round": rnd, "agent": agent,
            "neighbours": neighbours, "exemplar_scope": cfg.exemplar_scope,
            "framing": cfg.framing, "catalogue_size": len(catalogue),
            "pool_size": len(pool), "selection_mode": mode,
            "menu": [t["id"] for t in menu],
            "exec_feedback_shown": fb,
            "exemplars": [e["id"] for e in chosen],
            "exemplar_authors": [e["author"] for e in chosen],
            "exemplar_similarity": sims,
            "exemplar_match": match,
            "exemplar_age": [rnd - e["round"] for e in chosen],
            "exemplar_passed": [bool((e.get("harness") or {}).get("passed")) for e in chosen],
            "rule_fired": bool(block) and cfg.framing in ("avoid", "emulate"),
            "block_nonempty": bool(block), "block_chars": len(block),
            "prompt_chars": len(SYSTEM) + len(user), "prompt_sha256": _sha(SYSTEM + user),
            "tokens_in": tin, "tokens_out": tout, "tokens_cum": self.tokens,
            "api_retries": retries,
            "tool_id": tool_id, "parse_ok": parsed["parse_ok"],
            "label": parsed["tool_label"], "target": parsed["target"],
            "implements": parsed["implements"], "implements_unknown": parsed["implements_unknown"],
            "wall_s_model": round(time.time() - t0, 3),
        }
        entry = None
        if parsed["parse_ok"]:
            entry = self.lib.add(tool_id, agent, rnd, parsed["tool_label"],
                                 parsed["description"] or "", parsed["target"], parsed["source"],
                                 parsed["implements"], acl=[e["id"] for e in catalogue])
            visible = {e["id"]: e["author"] for e in snapshot}
            rec["static_imports"] = entry["static_imports"]
            rec["cross_agent_imports"] = [t for t in entry["static_imports"]
                                          if t in visible and visible[t] != agent]
            rec["unresolved_imports"] = [t for t in entry["static_imports"] if t not in visible]
        return rec, entry

    def _evaluate(self, rec, entry):
        if entry is None:
            rec["harness"] = None
            rec["exec_feedback"] = "response could not be parsed into a tool (no ```python block with def execute)"
            self.feedback[rec["agent"]] = {"tool_id": rec["tool_id"], "text": rec["exec_feedback"]}
            return
        tool = SandboxedTool(self.lib.root, entry["id"], self.cfg.tool_timeout_s)
        # D9: zero-model-call execution feedback, shown to the author next round.
        rec["exec_feedback"] = self.env.exec_feedback(tool, rec["round"])
        rec["exec_feedback_seed"] = self.env.public_example_seed(rec["round"])
        self.feedback[entry["author"]] = {"tool_id": entry["id"], "text": rec["exec_feedback"]}
        vec = self.env.signature(tool)
        entry["signature_signal"] = vec
        rec["signature_signal"] = vec
        rec["signature_errors"] = sum(1 for y in vec if y.startswith("ERR"))
        # Verdict is logged only; it is never shown to agents (msg #30, E2/D5).
        task = self.task_by_id.get(entry["target"])
        if task:
            rec["harness"] = self.env.harness(tool, task)
        else:
            rec["harness"] = {"passed": False, "reason": "no_or_unknown_target"}
        entry["harness"] = rec["harness"]
        self.lib.save()

    def _summary(self):
        with open(os.path.join(self.out, "rounds.jsonl")) as fh:
            recs = [json.loads(l) for l in fh]
        n = len(recs) or 1
        s = {
            "records": len(recs), "tokens_total": self.tokens, "truncated": self.truncated,
            "tools_built": sum(r["parse_ok"] for r in recs),
            "harness_passed": sum(1 for r in recs if (r.get("harness") or {}).get("passed")),
            "rule_fire_rate": sum(r["rule_fired"] for r in recs) / n,
            "block_nonempty_rate": sum(r["block_nonempty"] for r in recs) / n,
            "cross_agent_import_rate": sum(bool(r.get("cross_agent_imports")) for r in recs) / n,
        }
        with open(os.path.join(self.out, "summary.json"), "w") as f:
            json.dump(s, f, indent=1)
        return s
