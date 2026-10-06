# Strict re-audit: repair and verification

Subsequent same-Mac Docker implementation and AgentPort smoke gates are documented in [MAC_AGENTPORT_SMOKE.md](MAC_AGENTPORT_SMOKE.md). The report below preserves the earlier repair checkpoint; its then-unavailable Docker daemon is historical, not the latest runtime status.

2026-10-06. Baseline: `981e6ab352b319aaef4d6b366c52b19409487be6`.

This report concerns software fixes and offline artificial fixtures only. No real model experiments, provider requests, experiment keys, test-result-based design tuning or spending approval were used. The HTTP deadline integration test connects only to a local fake server with a fake key.

## Repair scope

| Finding | Repair | Regression evidence |
|---|---|---|
| A caught profiler exception disabled subsequent ACL checks | Forbidden cross-tool calls terminate the probe without raising into generated code. Unexpected profiler errors also fail closed. Hook replacement is rejected. | Catch-and-retry and hook-disable fixtures |
| `os.open` write flags bypassed the mode-string check | Check write/create/append/truncate flags; make the tool tmpfs explicitly read-only before pivoting, including userns mode. | All write-flag variants leave fixture sources unchanged; read-only access still works. OS mount tampering test added but not executable on this macOS host. |
| Abnormal generated-tool exit was labelled infrastructure failure | Add a trusted pre-tool readiness marker; preserve worker exit status. Post-readiness termination/corruption is a tool failure; pre-readiness failure aborts as infrastructure. | Import-time/runtime `_exit(7)`, `_exit(0)`, corrupted result pipe, worker initialization exception and initialization timeout |
| Relative imports were omitted from dependency/adoption/TCI inputs | Normalize package-relative and absolute static imports to the same tool identifier; relative imports are not external packages in TCI. | Five import forms produce equal dependencies/TCI; relative import also executes successfully. |
| SDK inactivity timeout was mistaken for total request deadline | Add POSIX main-thread wall-clock interruption around the entire synchronous SDK call; unwind and close the transport on expiry, stop without resampling, and refuse reuse of that client. | Real SDK against a trickling localhost server; fake blocking client; alarm restoration; no subsequent request; unsupported threads/occupied timers refused before reservation. |

## Problems found during subsequent review and also repaired

- Negative/non-integer/non-finite token counts and invalid cache counts could enter cost accounting. Validate usage in both model and budget; an accounting anomaly makes the budget refuse subsequent requests. Actual positive usage exceeding reservation assumptions is retained and stops the run. Duplicate response accounting is rejected; unanswered retries keep their reservations.
- Completed, billed responses with a missing assistant choice previously lost the response usage callback. Record valid usage before rejecting the malformed answer, without a new model sample.
- The first repair still classified a timeout before worker readiness as a tool timeout. Readiness is now checked before either timeout or envelope classification.
- Mutable module `__name__` could spoof the caller identity. Identify generated namespaces by their loader source paths and retained namespace identity, not a writable name string. Check file reads against the originating tool's historical ACL as well, not only the top-level reachable union; a cached future tool cannot be read as source by an old tool.
- Regression runs exposed unclosed manifest/summary handles in the legacy smoke and run entrypoints. Use context-managed reads; close equivalent handles in the batch/utility test fixtures. No scientific data or scoring rules were changed by this cleanup.

## Verification rounds

1. Original five counterexamples converted into regression tests and repaired: 69 targeted tests, 1 OS-only skip.
2. Accounting and initialization-timeout review, repairs and added tests: 74 targeted tests, 1 OS-only skip.
3. Caller-identity/source-access review, repairs and added tests: 90 targeted tests, 2 OS-only skips, including the existing sandbox suite.
4. Final full-suite verification is recorded below. A preceding discovery run (141 tests, 4 skips, no failures) was started before the last repairs and is not treated as final-revision acceptance.

All fixtures are independent of scientific effect claims. A passing unit test is not evidence that separation improves a library.

## Deadline policy and compatibility

- The SDK's own timeout still bounds individual I/O waits. The additional POSIX timer interrupts the synchronous call even when body data keep arriving.
- Total-deadline expiry is terminal and does **not** trigger the ordinary network-error retry loop. Local cancellation does not prove server-side cancellation or zero billing; its reservation remains spent/unknown.
- Calls are supported on the POSIX main thread. Existing active real-time alarms and unsupported threading are refused before a request. The previous signal handler is restored after success, ordinary exceptions and deadline expiry.
- Legacy batch jobs use separate Python processes, so their own model calls remain on each process's main thread. This is not a new thread-concurrent model API.

## Boundaries and remaining preparation

- Native macOS cannot execute the Linux namespace paths. This does not require a separate computer: the intended local route is a Linux environment inside Docker Desktop on the same Mac. Docker Desktop is installed, but its daemon was unreachable during verification. Container packaging and compatibility with the existing namespace sandbox are not implemented or validated by this patch. The Linux read-only mount and adversarial OS-isolation tests must pass in that environment before any real-model run. No skipped OS check is counted as passed.
- Python hooks are defense in depth, not a proof against arbitrary in-process interpreter tampering. Paid runs continue to require OS isolation. No broad sandbox-security guarantee follows from these targeted repairs.
- The CNY-500 experiment document remains a **proposal**. This repair does not implement its complete Experiments 2–4 analysis pipeline, importer-specific functional edge ablation, staged CNY ledger or main-study launcher. The current guarded launcher remains development-only and small-scale; do not relabel its diagnostics as complete paper evidence or use the old batch launcher for the revised SAC study.
- Source changes invalidate all earlier prepared approvals. Any real smoke, including a retry after a fix, needs newly resolved configuration and explicit user approval, with the collaborator's key only.
- No code was pushed during the repair turn; subsequent publication of this patch is separately authorized by the user. Scientific outputs and the older plan were not edited.

## Final verification receipt

The suite was split across four processes after all functional repairs. File-handle cleanup was applied while those processes were running; affected smoke/batch tests and the short model/SAC regression suite are checked again on that final source. Counts across overlapping reruns are not added together.

| Verification group | Result |
|---|---|
| Core: audit figure, previous bugfixes, environment, model, new regressions, SAC, sandbox | 99 tests, OK, 4 skips |
| Orchestration: batch and determinism | 4 tests, OK |
| Society construction | 22 tests, OK |
| Frozen library and utility | 24 tests, OK |
| Final-source short rerun: new regressions, SAC, previous bugfixes, model | 77 tests, OK, 1 OS-only skip |
| Final-source file-handle cleanup rerun: utility smoke and batch | 7 tests, OK; no unclosed-file warnings |

- The four full-suite groups report **149 tests: 145 passed, 4 skipped, 0 failures/errors**. Final-source reruns overlap those tests and are not extra independent acceptance cases. There are 22 new regression test methods in `tests/test_reaudit_regressions.py`.
- `git diff --check`, runner/test bytecode compilation and `pip check` pass.
- Final runner/environment `code_sha256`: `68c1f7f57d74979a5805d75764458e5392959a54a6eb683a7a3ab95d21cb4a5f`.
- The four full-suite skips are two optional plotting tests, an existing Linux-only adversarial test class and the new Linux read-only mount test. A skipped class is reported as one skip by unittest; do not describe its constituent cases as passed.
- This receipt is not approval to execute experiments and does not replace Linux runtime validation.

Disposition: all reproduced defects in this repair scope are fixed; no additional unresolved functional defect was found in the completed offline reviews. **Linux OS-isolation acceptance remains unverified**, so this is not an unconditional ready-to-run or bug-free certification. No paid experiment was performed. Publishing this patch does not authorize one.

Offline reproduction commands (run from the repository, with pinned dependencies):

```sh
.venv/bin/python -m unittest tests.test_audit_figure tests.test_bugfix_regressions tests.test_mechenv tests.test_model tests.test_reaudit_regressions tests.test_sac tests.test_sandbox -q
.venv/bin/python -m unittest tests.test_batch tests.test_determinism -q
.venv/bin/python -m unittest tests.test_runner -q
.venv/bin/python -m unittest tests.test_utility -q
.venv/bin/python -m unittest tests.test_utility.SmokeTests tests.test_batch -q
.venv/bin/python -m unittest tests.test_reaudit_regressions tests.test_sac tests.test_bugfix_regressions tests.test_model -q
```

These use synthetic fixtures and stub models, not the paid SAC launcher. The trickling-HTTP test uses a localhost server and a fake key. Linux validation still needs these tests on a host where the runner reports `os-*` isolation; passing with hook-only isolation does not validate the OS boundary.
