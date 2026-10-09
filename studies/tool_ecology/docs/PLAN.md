# Tool ecology implementation plan

Goal: deliver the three authorized steps with reproducible engineering evidence.
Architecture: immutable package registry, snapshot receipt controller, mini-SWE-agent Docker runtime, separate pinned LDB grader.
Tech stack: Python 3.12 host, mini-SWE-agent 2.4.6, Docker, AgentPort Responses API with GPT-6-Luna.
Spec: docs/DESIGN.md
Execution: native in this session, as requested by the user (complete steps 1, 2, 3).

## Constraints and review focus
- Hidden statements/tests/reference solutions never enter builder mounts or prompts.
- Same-round publications invisible; unknown dependency IDs rejected; duplicates cannot overwrite.
- Dependency bundles propagate only via explicit receipts; symlinks/path traversal rejected.
- API keys stay on host, every physical request reserved before dispatch, no silent retry/fallback.
- Grader failure is distinct from a failed solution; empty/missing test results must never be success.

## Tasks
- [x] 1. Audit three Python specifications, inventory visible and held-out problems and pin source hashes. Check chosen reference solutions against original verifiers.
- [x] 2. Implement registry, snapshots, bundle receipts and private mature agent runtime. Test immutable IDs, snapshot barrier, non-neighbor exclusion, dependency propagation, isolation and multi-step edit/test/repair.
- [x] 3. Implement frozen downstream consumer and grader, runtime call tracing and budget ledger. Test absent hidden files, frozen hashes, missing results and replay.
- [x] 4. Commit a version; run a small genuine Luna engineering smoke on local-neutral/Local-Boids plus no-library consumer baseline. Retain every attempt and publish a clearly scoped Chinese report.

Delivered: valid smoke-07 at c7e22a6, 179 model requests, six consumer grades, full uninstrumented replay, 24 native-import checks, actual cross-author CSV witness and separate one-edit weather diagnosis. The confirmatory eight-agent specialization study remains a separate future experiment.
