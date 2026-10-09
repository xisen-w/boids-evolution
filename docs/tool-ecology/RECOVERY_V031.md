# Explicit transport recovery — declared before replacement calls

The corrected `demand-batch-02` stopped with one `APITimeoutError` in seed108,
local-neutral, a07 round2 (physical request55 in that society). The client read
timeout was55 seconds. Five societies are complete and frozen with zero API
errors. The failed neutral society has only eight graded opportunities and69
physical requests; its partial code/trajectories are preserved but cannot count
as a completed society or as semantic failure.

Recorded batch costs:1,218 physical requests; known usage5,326,395 input,
380,564 output and3,923,156 cached-input tokens, one API error. The timed-out
request's provider usage/billing is unknown, not assumed free.

## Recovery rule

Do not edit, resume or overwrite batch02. It remains aborted. Do not use the
older measurement-invalidated batch01. Retain the five valid frozen corrected
societies and recover only missing predeclared cells, in this order:

1. seed108 local-neutral — `demand-recovery-108-neutral-01`;
2. seed2026 independent — `demand-recovery-2026-independent-01`;
3. seed2026 local-neutral — `demand-recovery-2026-neutral-01`;
4. seed2026 local-boids — `demand-recovery-2026-boids-01`.

Each uses a completely fresh society/workspace, eight agents, six rounds,
maximum six calls per agent-round, four concurrent agents, and at most288
physical requests. Launch at most one such society per automation continuation.
Commit exact source before paid calls. Preserve every attempt, including another
failure; no silent retries or model fallback. Any further recovery needs a new
ledgered decision, never an unbounded retry loop.

Transport waiting is increased from55 to180 seconds and recorded in the new
manifest. SDK retries remain0. Model, reasoning effort, output/action budget,
task data, prompts, visibility, publication rules and service grader are
unchanged. Existing tests plus new offline transport tests verify the longer
wait and one archived failed request without fallback. Original and recovery
source revisions/timeouts must be reported per society, not as one uniform run.

If these four attempts succeed, the original1,218 requests plus their maximum
1,152 requests total at most2,370, within the original2,592 request ceiling.

## Analysis and limitations

After all nine valid cells exist, construct a separate *recovered exploratory
collection* with explicit per-cell lineage, revisions, manifest hashes, frozen
hashes, and all original/recovery costs. This does not turn batch02 into a
successful uninterrupted batch. Never copy replacement cells into batch02 or
write a COMPLETE marker there. Reject incomplete, duplicated, wrong-protocol,
wrong-seed/condition or semantically incompatible cells.

Use the same frozen replay, return-intervention selection, shared DEV panel,
dependency provenance, structural removal and graphs as previously declared.
The observed original completion selection and change in transport waiting
must be disclosed. These three-seed results remain exploratory, not a clean
confirmatory trial. Do not rerun a valid cell because its score is inconvenient.
