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
import copy

from .config import SAC_ARMS
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
        try:
            return self._run_rounds()
        finally:
            self.log.close()

    def _run_rounds(self):
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
                item = self._agent_turn(agent, rnd, snapshot)
                if cfg.extra.get("stop_on_smoke_anomaly"):
                    # Evaluate immediately, but keep the frozen round-start
                    # snapshot for every agent. Do not pay for the next agent
                    # after discovering a system/security/resource failure.
                    # Ordinary generated-code failures remain failed outcomes.
                    self._evaluate(*item)
                    self.log.write(json.dumps(item[0], sort_keys=True) + "\n")
                    self.log.flush()
                else:
                    built.append(item)
            for rec, entry in built:
                self._evaluate(rec, entry)
                self.log.write(json.dumps(rec, sort_keys=True) + "\n")
            self.log.flush()
            snapshots = os.path.join(self.out, "snapshots")
            os.makedirs(snapshots, exist_ok=True)
            with open(os.path.join(snapshots, f"round_{rnd:02d}.json"), "w") as f:
                json.dump(self.lib.entries, f, sort_keys=True, indent=1)
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
        sac_evidence, sac_meta, sac_fired = None, None, None
        if cfg.arm in SAC_ARMS:
            from .mechanisms import build_evidence, render_evidence
            sac_evidence, sac_meta = build_evidence(snapshot, agent, rnd, cfg, self._source,
                                                    self.task_by_id, self.env.primitives)
            block, sac_fired = render_evidence(sac_evidence, cfg.arm)
            chosen, sims, mode = [], [], "sac_text_quality_activity_v1"
        elif cfg.framing is None:
            chosen, sims, mode = [], [], "no_exposure_arm"
        elif cfg.exemplar_scope == "matched":
            ring_pool, other_pool = pool
            chosen, sims, mode, match = select_matched(ring_pool, other_pool, own_latest, cfg.m,
                                                       agent_rng, self.env.similarity)
            pool = other_pool
        else:
            chosen, sims, mode = select_exemplars(agent, pool, own_latest, cfg.m, agent_rng,
                                                  self.env.similarity)
        if cfg.arm not in SAC_ARMS:
            block = render_block(cfg.framing, chosen, self._source)
        menu = self.env.menu(cfg.seed, agent, rnd, self.dev_tasks, cfg.menu_size)
        fb = self.feedback.get(agent)
        user = build_user_prompt(rnd, menu, catalogue, block, fb)
        if sac_evidence is not None:
            # Shrink all four renderings identically for the SAME snapshot.
            # Byte budget is a conservative, tokenizer-independent input cap.
            from .mechanisms import evidence_hash
            cap = cfg.extra.get("max_input_bytes", 16000)
            evidence = copy.deepcopy(sac_evidence)
            cat = copy.deepcopy(catalogue)
            shrink_steps = 0
            while True:
                variants = {arm: build_user_prompt(rnd, menu, cat, render_evidence(evidence, arm)[0], fb)
                            for arm in SAC_ARMS}
                if max(len((SYSTEM + u).encode("utf-8")) for u in variants.values()) <= cap:
                    break
                excerpts = [e for name in ("S", "A") for e in (evidence[name] or {}).get("tools", [])]
                if any(e["code_excerpt"] for e in excerpts):
                    for e in excerpts:
                        e["code_excerpt"] = "\n".join(e["code_excerpt"].splitlines()[:-1])
                else:
                    max_desc = max((len(e.get("description") or "") for e in cat), default=0)
                    limit = next((n for n in (200, 100, 50) if n < max_desc), None)
                    if limit is None:
                        raise ValueError("shared SAC prompt exceeds input cap; no task or evidence module was dropped")
                    for e in cat:
                        e["description"] = (e.get("description") or "")[:limit]
                shrink_steps += 1
            sac_evidence = evidence
            block, sac_fired = render_evidence(evidence, cfg.arm)
            user = variants[cfg.arm]
            sac_meta.update(evidence_sha256=evidence_hash(evidence), prompt_shrink_steps=shrink_steps,
                            max_rendered_input_bytes=max(len((SYSTEM + u).encode("utf-8")) for u in variants.values()))
        tool_id = self.lib.make_id(agent, rnd)
        # Keep the exact research prompt even if the first provider call fails.
        # No transport headers or credentials are part of this artifact.
        prompt_path = os.path.join(self.out, "prompts", f"{tool_id}.json")
        with open(prompt_path, "w") as f:
            json.dump({"system": SYSTEM, "user": user, "response": None,
                       "status": "REQUEST_PREPARED"}, f, indent=1)
        text, tin, tout = self.model.complete(SYSTEM, user, cfg.temperature, cfg.max_tokens_per_call)
        self.tokens += tin + tout
        retries = getattr(self.model, "last_retries", 0)
        parsed = parse_response(text, self.env.primitives)
        with open(prompt_path, "w") as f:
            json.dump({"system": SYSTEM, "user": user, "response": text,
                       "status": "RESPONSE_RECEIVED"}, f, indent=1)
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
            "rule_fired": any(sac_fired.values()) if sac_fired is not None else bool(block) and cfg.framing in ("avoid", "emulate"),
            "block_nonempty": bool(block), "block_chars": len(block),
            "prompt_chars": len(SYSTEM) + len(user), "prompt_sha256": _sha(SYSTEM + user),
            "tokens_in": tin, "tokens_out": tout, "tokens_cum": self.tokens,
            "api_retries": retries,
            "tool_id": tool_id, "parse_ok": parsed["parse_ok"],
            "label": parsed["tool_label"], "target": parsed["target"],
            "implements": parsed["implements"], "implements_unknown": parsed["implements_unknown"],
            "wall_s_model": round(time.time() - t0, 3),
        }
        if sac_evidence is not None:
            rec.update(sac_evidence=sac_evidence, sac_selection=sac_meta, sac_fired=sac_fired)
        rec["response_metadata"] = getattr(self.model, "last_response_metadata", None)
        rec['model_parse_failure'] = not parsed['parse_ok']
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
            if cfg.arm in SAC_ARMS:
                from .mechanisms import tci_score
                entry["tci"] = tci_score(parsed["source"], entry["static_imports"], visible)
                rec["tci"] = entry["tci"]
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
        parametric = None
        if self.cfg.extra.get("stop_on_smoke_anomaly") and rec["exec_feedback"].startswith("raised "):
            from .smoke_policy import SmokeStop, verified_parametric_component, ordinary_model_code_error
            diagnostic = {}
            parametric = verified_parametric_component(self.env, tool, entry, rec["exec_feedback"], diagnostic)
            rec["parametric_probe_diagnostic"] = diagnostic
            # The independent verifier can reveal a timeout/security failure
            # even when the earlier public call was just missing a parameter.
            critical_verifier = diagnostic['status'] == 'primitive_verification_failed'
            if parametric is None and (critical_verifier or not ordinary_model_code_error(rec['exec_feedback'][7:])):
                reason = ("builder_parametric_verification_failed"
                          if diagnostic['status'] == 'primitive_verification_failed'
                          else "builder_public_execution_error")
                self.log.write(json.dumps(dict(rec, smoke_stop=reason), sort_keys=True) + "\n")
                self.log.flush()
                raise SmokeStop(reason)
            if parametric is not None:
                rec["parametric_probe_contract"] = parametric
            else:
                rec['model_public_execution_failure'] = True
        rec["exec_feedback_seed"] = self.env.public_example_seed(rec["round"])
        self.feedback[entry["author"]] = {"tool_id": entry["id"], "text": rec["exec_feedback"]}
        vec = self.env.signature(tool)
        entry["signature_signal"] = vec
        rec["signature_signal"] = vec
        rec["signature_errors"] = sum(1 for y in vec if y.startswith("ERR"))
        if self.cfg.extra.get("stop_on_smoke_anomaly") and rec["signature_errors"]:
            from .smoke_policy import SmokeStop, missing_parameter, ordinary_model_code_error
            # Inspect the actual cached no-kwargs outputs, not the coarse ERR
            # fingerprints. A verified primitive does not excuse another error.
            outputs = tool.prefetch(self.env.signal_calls())
            expected = model_errors = 0
            for y in outputs:
                error = y.get('__error__') if isinstance(y, dict) else None
                if parametric and missing_parameter(error, parametric['parameter_names']):
                    expected += 1
                elif ordinary_model_code_error(error):
                    model_errors += 1
            rec['model_probe_error_count'] = model_errors
            if expected + model_errors != rec["signature_errors"]:
                self.log.write(json.dumps(dict(rec, smoke_stop="builder_probe_execution_error"), sort_keys=True) + "\n")
                self.log.flush()
                raise SmokeStop("builder_probe_execution_error")
            if parametric:
                parametric['signal_errors_classified'] = expected
        # Legacy arms hide verdicts. SAC exposes selected-exemplar dev-pass
        # metadata identically in all four conditions (never reference outputs).
        task = self.task_by_id.get(entry["target"])
        if task:
            rec["harness"] = self.env.harness(tool, task)
        else:
            rec["harness"] = {"passed": False, "reason": "no_or_unknown_target"}
        entry["harness"] = rec["harness"]
        self.lib.save()
        if self.cfg.extra.get("stop_on_smoke_anomaly"):
            from .smoke_policy import SmokeStop, verdict_has_execution_error, ordinary_solver_code_error
            rec['model_harness_execution_failure'] = verdict_has_execution_error(rec['harness'])
            if rec['model_harness_execution_failure'] and not ordinary_solver_code_error(rec['harness']):
                self.log.write(json.dumps(dict(rec, smoke_stop="builder_harness_execution_error"), sort_keys=True) + "\n")
                self.log.flush()
                raise SmokeStop("builder_harness_execution_error")

    def _summary(self):
        with open(os.path.join(self.out, "rounds.jsonl")) as fh:
            recs = [json.loads(l) for l in fh]
        n = len(recs) or 1
        s = {
            "records": len(recs), "tokens_total": self.tokens, "truncated": self.truncated,
            "tools_built": sum(r["parse_ok"] for r in recs),
            "model_parse_failures": sum(bool(r.get('model_parse_failure')) for r in recs),
            "model_public_execution_failures": sum(bool(r.get('model_public_execution_failure')) for r in recs),
            "model_probe_execution_failures": sum(bool(r.get('model_probe_error_count')) for r in recs),
            "model_harness_execution_failures": sum(bool(r.get('model_harness_execution_failure')) for r in recs),
            "harness_passed": sum(1 for r in recs if (r.get("harness") or {}).get("passed")),
            "rule_fire_rate": sum(r["rule_fired"] for r in recs) / n,
            "block_nonempty_rate": sum(r["block_nonempty"] for r in recs) / n,
            "cross_agent_import_rate": sum(bool(r.get("cross_agent_imports")) for r in recs) / n,
        }
        with open(os.path.join(self.out, "summary.json"), "w") as f:
            json.dump(s, f, indent=1)
        return s
