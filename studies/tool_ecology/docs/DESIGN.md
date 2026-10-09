# Tool ecology v0.2: LibraryDesignBench adaptation

The user authorized sequential completion of task audit, continuous local tool-building, and hidden downstream evaluation on 2026-10-08. This implementation is a bounded engineering pilot; it is not the original LDB leaderboard protocol or the proposed confirmatory experiment.

- Pin LDB framework 905bb62859cf5ae340562bf4bde6abfa1b9f5a41, tasks a1f4e886063373d43e52b53b98492cf108f294e3, mini-SWE-agent 2.4.6 a83fcae82d2a08f0ee0c688f9d137b3566c097f8.
- Audit pyda, python_validation and uglypie from design specs; choose pyda for initial implementation because diverse deterministic IO, time and grouping capabilities can be combined. No requirement for atomic tools or fixed specialists.
- Each builder uses DefaultAgent with private persistent files and fresh per-round conversation, repeated common design specification and the same per-round demand menu. All internal model calls counted. Four builders x three rounds in the first engineering smoke; the --agents option supports eight.
- Publish an immutable Python package plus README and manifest; arbitrary native Python API. No author-assigned IDs. Host assigns aNN_rNN. Candidate can repair old work or be monolithic. Dependencies must be in the pre-round received view.
- Each round reads a fixed snapshot. Local arms deliver only a neighbor's previous-round new publication. Independent sees only own output. No global catalogue or global adoption counts. Local-neutral and Local-Boids have identical evidence fields; directional S/A/C differs.
- Amendment from v0.1: use explicit dependency bundles. When an agent receives a publication it also receives its declared frozen dependencies, with every member separately recorded in the receipt ledger. This permits source reading and native imports. It does NOT implement opaque wrapper execution, and can propagate information over multiple hops through republished dependencies. No automatic forwarding of unrelated received artifacts.
- Docker private work directory mounted rw; published view ro; no network, no Docker socket, no API credentials, dropped capabilities and no-new-privileges. Hidden task statements/tests/references/logs absent from builder mounts.
- Frozen merged library is read-only to a fresh downstream consumer. Consumers receive only their problem instruction and workspace fixtures. They may write arbitrary adapter code, matching native LDB use, and may ignore the library. A no-library consumer baseline is included. This differs from the earlier restricted JSON consumer; do not carry its metrics over silently.
- Score with pinned original task verifiers after the consumer exits, in a separate container. Never feed scores or hidden tests back to builders. Exclude design-visible example problems from held-out generalization. Freeze code hashes, task file hashes and all candidate bytes before downstream evaluation.
- Record semantic correctness, original simplicity score where verifier completes, model calls/tokens, declared dependencies and executed Python call edges. Executed calls alone are not functional causality. The short smoke cannot establish sustained division of labor or a Boids advantage.
- Failures: Docker/setup/API/auth/invalid publication-contract failures are infra/protocol failures; valid running programs with wrong behavior are task failures; imports and failed calls are not automatically reliable reuse. Retain failed attempts and never rerun a scientific cell to improve its score.

## Implementation limits established during review

Ordinary static Python imports are checked against declared received dependencies; reflective/dynamic imports are not a complete static proof. Physical builder views exclude unreceived files, but final consumer views intentionally contain all frozen packages. Do not claim per-importer opaque dependency execution. Executed function traces cover module-level Python functions, not all class methods, native calls, or reflective calls. Functional attribution requires an intervention that was hit and changed a correct output without crashing; the Docker witness test verifies this capability, not every edge in a real run. Public capability labels remain author claims, not verified specialization profiles.

The two selected problem IDs were chosen before inspecting test assertions or executing models. Host engineering verification necessarily executes original hidden tests on references. Builders never receive those files or results. These are public benchmark problems: held-out here means withheld during this run, not proven absent from model pretraining.

## Environment parity and host boundary fixes

Agent bash runs without login-shell PATH resetting, so `python` selects /opt/venv/bin/python with the same pinned pyarrow/numpy used by verifiers. A real Docker regression checks this before paid runs. Rejected archives never follow unvalidated roots; feedback is replaced atomically; relative imports may remain within one publication, but escaping imports must use explicit declared published.ID names. Grader containers are named and force-removed after success, failure or timeout.

Smoke-03 at a648fac is retained as environment-defective engineering evidence, because its default login shell used system Python despite the pinned venv. It cannot support an arm-effect claim. Smoke-07 completed the complete fixed protocol without altering task IDs, rules, budgets or topology in response to scores.

Final evidence is in REPORT_ZH.md and evidence/pilot-07. A subsequent image-preflight resolver and stricter regression assertions do not change the c7e22a6 generated programs or their preserved grades.
