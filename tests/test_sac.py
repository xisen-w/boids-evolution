"""Artificial fixtures only: no paid API, no scientific experiment results."""
import copy
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from boidsnet.runner.config import RunConfig, SAC_ARMS
from boidsnet.runner.mechanisms import build_evidence, render_evidence, tci_score, text_pairs, evidence_hash
from boidsnet.runner.model import OpenAICompatModel
from boidsnet.runner.sac_pilot import (DEFAULT_CONFIG, Budget, approval_template, digest,
                                    execute, read_json, resolve, verify_approval)
from boidsnet.runner.utility import glue_gate, score_society, check_sampling
from boidsnet.runner.library import Library
from boidsnet.runner.sandbox import run_tool
from boidsnet.runner.society import Society
from boidsnet.runner.env_adapter import MechEnv
from boidsnet.runner.run import DEFAULT_ENV, main as legacy_main

SRC = "def execute(table, lookup, **params):\n    return table\n"


def entry(author, rnd, label="filter data", passed=False, tci=1, imports=(), target="d1"):
    return {"id": f"a{author:02d}_r{rnd:02d}", "author": author, "round": rnd,
            "label": label, "description": label, "target": target,
            "implements": ["filter"], "static_imports": list(imports),
            "harness": {"passed": passed}, "tci": tci, "signature_signal": ["ERR:X"] * 8}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.cfg = RunConfig(arm="111", seed=1001, n_agents=4, n_rounds=3)

    def build(self, entries, rnd=3, arm="111"):
        self.cfg.arm = arm
        return build_evidence(entries, 0, rnd, self.cfg, lambda _: SRC, {"d1"}, {"filter"})

    def test_same_evidence_four_arms_and_instruction_only_toggles(self):
        entries = [entry(1, 1), entry(3, 2)]
        data = [self.build(entries, arm=a)[0] for a in SAC_ARMS]
        self.assertEqual(len({evidence_hash(x) for x in data}), 1)
        for arm in SAC_ARMS:
            block, fired = render_evidence(data[0], arm)
            self.assertEqual(fired, {n: b == "1" for n, b in zip("SAC", arm)})
            self.assertIn('"dev_pass":false', block)
        self.assertNotIn("YOUR GOAL", render_evidence(data[0], "000")[0])

    def test_s_neighbour_pairs_not_own_tool_or_behavior(self):
        entries = [entry(1, 1), entry(3, 1), entry(0, 1, "unrelated stars")]
        e, _ = self.build(entries)
        self.assertEqual([x["author"] for x in e["S"]["tools"]], [1, 3])
        entries[0]["signature_signal"] = ["DIFFERENT"] * 8
        self.assertEqual(evidence_hash(e), evidence_hash(self.build(entries)[0]))

    def test_s_empty_and_empty_vocabulary(self):
        self.assertIsNone(self.build([entry(1, 1)])[0]["S"])
        self.assertEqual(text_pairs([entry(1, 1, "the and"), entry(3, 1, "the and")])[1], "empty_vocabulary")
        e, _ = self.build([], rnd=1)
        self.assertEqual(e, {"S": None, "A": None, "C": None})
        block, flags = render_evidence(e, "111")
        self.assertFalse(any(flags.values()))
        self.assertNotIn("YOUR GOAL", block)

    def test_alignment_pass_first_fallback_window_and_adoption(self):
        a, b = entry(1, 1, passed=True, tci=1), entry(3, 2, tci=9)
        e, _ = self.build([a, b, entry(2, 2, imports=[b["id"], b["id"]])])
        self.assertFalse(e["A"]["fallback"])
        self.assertEqual([x["tool_id"] for x in e["A"]["tools"]], [a["id"], b["id"]])
        self.assertEqual(e["A"]["tools"][1]["adoption"], 1)
        a["harness"]["passed"] = False
        self.assertTrue(self.build([a, b])[0]["A"]["fallback"])
        self.assertEqual(self.build([a, b])[0]["A"]["tools"][0]["tool_id"], b["id"])
        self.assertIsNone(self.build([a, b], rnd=6)[0]["A"])

    def test_cohesion_only_previous_round_and_future_excluded(self):
        data = [entry(1, 1), entry(3, 2), entry(2, 3)]
        e, _ = self.build(data)
        self.assertEqual(e["C"]["n_parsed_tools"], 1)
        self.assertEqual(e["C"]["primitive_counts"], {"filter": 1})
        self.assertNotIn("a02_r03", json.dumps(e))

    def test_tci_namespace_adaptation(self):
        source = "from tools import a01_r01\n" + SRC
        self.assertAlmostEqual(tci_score(source, ["a01_r01"], ["a01_r01"]) - tci_score(SRC, [], []), 0.51)

    def test_neutral_cannot_be_independent(self):
        with self.assertRaises(ValueError):
            RunConfig(arm="000", seed=1, catalogue_scope="self")
        with self.assertRaises(ValueError):
            RunConfig(arm="111", seed=1, n_agents=2)


class DeepSeekTests(unittest.TestCase):
    def model(self, **kw):
        # The SDK client itself is mocked; no external request is possible.
        with mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-test-fixture"), \
                mock.patch.dict(os.environ, {"BOIDS_PARTNER_API_KEY": "FAKE_NOT_A_KEY", "BOIDS_SANDBOX": "auto"}), \
                mock.patch("openai.OpenAI"):
            return OpenAICompatModel("deepseek-flash", "BOIDS_PARTNER_API_KEY", True,
                                     base_url="https://api.deepseek.com", thinking="disabled", **kw)

    def test_explicit_mode_cache_and_response_metadata(self):
        m = self.model(max_attempts=2)
        m.client.chat.completions.create.return_value = types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="x"), finish_reason="stop")],
            usage=types.SimpleNamespace(prompt_tokens=10, completion_tokens=2, prompt_cache_hit_tokens=7),
            model="deepseek-flash", id="fake-response")
        self.assertEqual(m.complete("s", "u", 0.7, 100), ("x", 10, 2))
        kw = m.client.chat.completions.create.call_args.kwargs
        self.assertEqual(kw["extra_body"], {"thinking": {"type": "disabled"}})
        self.assertEqual(kw["temperature"], 0.7)
        self.assertEqual(m.last_cached_tokens, 7)
        self.assertEqual(m.last_response_metadata["finish_reason"], "stop")
        self.assertEqual(m.MAX_ATTEMPTS, 2)

    def test_no_user_key_fallback_no_implicit_thinking(self):
        for kw in ({"key_env": "OPENAI_API_KEY", "thinking": "disabled"},
                   {"key_env": "BOIDS_PARTNER_API_KEY", "thinking": None}):
            with self.assertRaises((ValueError, PermissionError)):
                OpenAICompatModel("deepseek-flash", allow_spend=True,
                                   base_url="https://api.deepseek.com", **kw)

    def test_missing_usage_not_retried(self):
        m = self.model()
        m.client.chat.completions.create.return_value = types.SimpleNamespace(usage=None)
        with self.assertRaises(RuntimeError):
            m.complete("s", "u", 0.7, 10)
        self.assertEqual(m.client.chat.completions.create.call_count, 1)

    def test_budget_refusal_never_calls_sdk(self):
        m = self.model(before_request=mock.Mock(side_effect=PermissionError("cap")))
        with self.assertRaises(PermissionError):
            m.complete("s", "u", 0.7, 10)
        m.client.chat.completions.create.assert_not_called()

    def test_real_sdk_serialization_against_in_memory_transport(self):
        import httpx
        from openai import OpenAI
        requests = []

        def handler(request):
            requests.append(json.loads(request.content))
            self.assertEqual(str(request.url), "https://api.deepseek.com/chat/completions")
            return httpx.Response(200, json={"id": "fixture", "object": "chat.completion", "created": 1,
                "model": "deepseek-flash", "choices": [{"index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": "fixture output"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12,
                          "prompt_cache_hit_tokens": 4, "prompt_cache_miss_tokens": 6}})

        m = self.model()
        with httpx.Client(transport=httpx.MockTransport(handler), trust_env=False) as http:
            m.client = OpenAI(api_key="FAKE_NOT_A_KEY", base_url="https://api.deepseek.com", http_client=http, max_retries=0)
            self.assertEqual(m.complete("system", "user", 0.7, 4000), ("fixture output", 10, 2))
        self.assertEqual(requests[0]["thinking"], {"type": "disabled"})
        self.assertEqual(requests[0]["max_tokens"], 4000)
        self.assertEqual(m.last_cached_tokens, 4)


class PilotGuardTests(unittest.TestCase):
    def setUp(self):
        self.c = read_json(DEFAULT_CONFIG)

    def test_small_size_and_dev_only(self):
        with mock.patch("boidsnet.runner.sac_pilot.MechEnv", wraps=MechEnv) as ctor:
            r = resolve(self.c)
        self.assertEqual((r["builder_calls"], r["solver_calls"], r["nominal_model_calls"]), (48, 48, 96))
        self.assertEqual(len(r["eval_task_ids"]), 6)
        self.assertTrue(all(t.startswith("dev-") for t in r["eval_task_ids"]))

    def test_pending_approval_blocks_before_any_model_or_sandbox(self):
        r = resolve(self.c)
        with mock.patch("boidsnet.runner.model.OpenAICompatModel") as model, \
                mock.patch("boidsnet.runner.sandbox.isolation_level") as iso:
            with self.assertRaises(PermissionError):
                execute(r, approval_template(r), "SHOULD_NOT_EXIST", True)
            model.assert_not_called()
            iso.assert_not_called()

    def test_approval_bound_to_config_and_code(self):
        r = resolve(self.c)
        a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "TEST_FIXTURE"}
        verify_approval(r, a, True)
        with self.assertRaises(PermissionError):
            verify_approval(r, a, False)
        changed = copy.deepcopy(r)
        changed["config"]["n_agents"] = 8
        with self.assertRaises(PermissionError):
            verify_approval(changed, a, True)
        changed = dict(r, code_sha256="different")
        with self.assertRaises(PermissionError):
            verify_approval(changed, a, True)

    def test_old_cli_cannot_bypass_sac_review(self):
        with self.assertRaises(SystemExit) as cm:
            legacy_main(["--arm", "111", "--seed", "1001", "--out", "none", "--model", "deepseek-flash", "--engineering"])
        self.assertIn("sac_pilot", str(cm.exception))

    def test_budget_reserves_retry_and_counts_failed_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = Budget(dict(self.c, max_http_requests=2), Path(tmp) / "ledger.jsonl")
            b.before("s", "u", 10, 0)
            first = b.reserved
            b.before("s", "u", 10, 1)
            self.assertAlmostEqual(b.reserved, 2 * first)
            self.assertEqual(b.reported_responses, 0)
            with self.assertRaises(PermissionError):
                b.before("s", "u", 10, 0)
            self.assertEqual(b.requests, 2)
            b.config["max_http_requests"] = 3
            b.config["max_reserved_usd"] = b.reserved
            with self.assertRaises(PermissionError):
                b.before("s", "u", 10, 0)
            # Exhaustion is now sticky: mutating a config cannot resume spend.
            with self.assertRaises(PermissionError):
                b.before("s", "x" * 16001, 10, 0)
            fresh = Budget(self.c, Path(tmp) / "fresh.jsonl")
            with self.assertRaises(ValueError):
                fresh.before("s", "x" * 16001, 10, 0)

    def test_subset_cannot_be_used_for_test_score(self):
        with self.assertRaises(ValueError):
            score_society("never_read", None, None, split="test", task_ids=["test-1-d1"])

    def test_fully_mocked_launcher_passes_reviewed_config_to_all_routes(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("boidsnet.runner.sandbox.isolation_level", return_value="os-test-fixture"), \
                mock.patch("boidsnet.runner.model.OpenAICompatModel") as model, \
                mock.patch("boidsnet.runner.society.Society") as society, \
                mock.patch("boidsnet.runner.utility.score_society") as score:
            r = resolve(self.c, Path(tmp) / "mocked")
            a = approval_template(r) | {"approved": True, "status": "APPROVED", "reviewed_by": "TEST_FIXTURE"}
            model.return_value.sampling.return_value = {"thinking": "disabled"}
            model.return_value.transport_policy.return_value = {}
            society.return_value.run.return_value = {"records": 12, "truncated": False}
            score.side_effect = lambda *args, **kw: {"_dev_task_scores": [0.0] * 6, "split": "dev"}
            report = execute(r, a, Path(tmp) / "mocked", True)
            self.assertEqual(report["http_requests"], 0)
            self.assertEqual([c.args[0].arm for c in society.call_args_list], ["000", "111", "100", "011"])
            for call in score.call_args_list:
                self.assertEqual(call.kwargs["split"], "dev")
                self.assertEqual(call.kwargs["attempts"], 2)
                self.assertEqual(call.kwargs["task_ids"], r["eval_task_ids"])
            self.assertEqual(model.call_args.kwargs["thinking"], "disabled")
            self.assertEqual(model.call_args.args[1], "BOIDS_PARTNER_API_KEY")


class GateAndStateTests(unittest.TestCase):
    def test_glue_rejects_defaults_annotations_shadowing_dead_calls(self):
        good = "from tools import a00_r01\ndef execute(table, lookup, **params):\n    return a00_r01.execute(table, lookup)\n"
        bad = [good.replace("lookup, **params", "lookup=__import__('os').getcwd(), **params"),
               good.replace("table, lookup, **params", "table: __import__('os').getcwd(), lookup, **params"),
               good.replace("    return", "    a00_r01 = table\n    return"),
               good.replace("    return", "    return table\n    return")]
        for source in bad:
            self.assertFalse(glue_gate(source, {"a00_r01"})[0])
        self.assertTrue(glue_gate(good, {"a00_r01"})[0])

    def test_probe_state_is_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            lib = Library(tmp)
            source = "count = 0\ndef execute(table, lookup):\n    global count\n    count += 1\n    return count\n"
            lib.add("a00_r01", 0, 1, "fixture", "fixture", None, source)
            self.assertEqual(run_tool(tmp, "a00_r01", [{"args": [[], []]}] * 2), [1, 1])

    def test_empty_library_has_index_and_acl(self):
        with tempfile.TemporaryDirectory() as tmp:
            Library(tmp)
            self.assertEqual(read_json(Path(tmp) / "index.json"), {})
            self.assertEqual(read_json(Path(tmp) / "acl.json"), {})


class IntegrationFixtureTests(unittest.TestCase):
    def test_snapshot_evidence_prompt_and_sync_acl_without_execution(self):
        # One artificial agent-turn per arm; local evaluator/model are mocked.
        # This is a software fixture, not a stub experiment batch.
        users, hashes = {}, set()
        for arm in SAC_ARMS:
            with tempfile.TemporaryDirectory() as tmp:
                cfg = RunConfig(arm=arm, seed=1001, n_agents=4, n_rounds=3)
                model = mock.Mock()
                model.complete.return_value = ("TOOL_LABEL: fixture\nTARGET: NONE\nIMPLEMENTS: NONE\nDESCRIPTION: fixture\n```python\n" + SRC + "```", 1, 1)
                model.last_response_metadata, model.last_retries = None, 0
                env = MechEnv(DEFAULT_ENV)
                society = Society(cfg, env, model, tmp)
                try:
                    snapshot = [entry(1, 1), entry(3, 1)]
                    for e in snapshot:
                        society.lib.add(e["id"], e["author"], 1, e["label"], e["description"], "d1", SRC)
                    rec, created = society._agent_turn(0, 2, snapshot)
                    hashes.add(rec["sac_selection"]["evidence_sha256"])
                    users[arm] = model.complete.call_args.args[1]
                    self.assertEqual(society.lib.acl[created["id"]], sorted(e["id"] for e in snapshot))
                    self.assertNotIn(created["id"], society.lib.acl[created["id"]])
                    self.assertEqual(rec["sac_fired"], {n: b == "1" for n, b in zip("SAC", arm)})
                finally:
                    society.log.close()
        self.assertEqual(len(hashes), 1)
        self.assertNotEqual(users["000"], users["111"])


if __name__ == "__main__":
    unittest.main()
