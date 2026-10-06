"""Offline DEV-only SAC contracts; no model or sealed evaluation calls."""
import unittest
import contextlib
import io
import tempfile

from boidsnet.runner.config import RunConfig, SAC_ARMS
from boidsnet.runner.mechanisms import build_evidence, render_evidence
from boidsnet.runner.run import main


class SacControlContract(unittest.TestCase):
    def test_cli_requires_explicit_sizing_and_positive_budget(self):
        with tempfile.TemporaryDirectory() as out:
            base = ['--arm', 'SAC111', '--seed', '1', '--out', out]
            for extra in ([], ['--n-agents', '4', '--n-rounds', '2', '--token-budget', '0']):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                    main(base + extra)
                self.assertEqual(exc.exception.code, 2)

    def test_invalid_sac_configuration_rejected(self):
        for kw in ({'catalogue_scope': 'self'}, {'n_agents': 2}, {'n_rounds': 0}):
            with self.assertRaises(ValueError):
                RunConfig(arm='SAC111', seed=1, **kw)

    def test_configurations_keep_shared_catalogue(self):
        for arm in SAC_ARMS:
            cfg = RunConfig(arm=arm, seed=1)
            self.assertEqual(cfg.catalogue_scope, "society")
            self.assertEqual(cfg.exemplar_scope, "local")
            self.assertEqual(cfg.design_version, "original_boids_guidance_v1")

    def test_empty_snapshot_does_not_fire(self):
        bundle = build_evidence([], [1, 3], 1, lambda _: "")
        self.assertEqual(bundle["fired"], {"S": False, "A": False, "C": False})
        for arm in SAC_ARMS:
            cfg = RunConfig(arm=arm, seed=1)
            self.assertIsInstance(render_evidence(bundle, cfg.mechanism_toggles), str)

    def test_legacy_im_remains_distinct(self):
        cfg = RunConfig(arm="IM", seed=1)
        self.assertEqual(cfg.catalogue_scope, "self")
        self.assertEqual(cfg.design_version, "behavioral_repulsion_v0.3.13")
        self.assertIsNone(cfg.mechanism_toggles)
