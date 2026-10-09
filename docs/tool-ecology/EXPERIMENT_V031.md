# Repeated-demand v0.3.1 — corrected service-entry attribution

This supersedes the *measurement implementation* of v0.3. The task contracts,
local rules, opportunity distribution and budget are unchanged. Read the
[original fixed protocol](EXPERIMENT_2026-10-09.md) for those details.

## Why a new run is necessary

In v0.3 a package could directly re-export a received function as a service
adapter. Its execution was recorded as `__main__ -> published.provider.function`,
so the host classifier missed the cross-author delegation. This was not a
generated-program failure. It undercounted neutral engineering reuse from 72
correct requests to zero. Wrong metrics were also visible in private feedback;
retrospective recounting cannot reconstruct behavior with corrected feedback.

The old main batch was therefore interrupted for an infrastructure reason,
after two complete seed-71 societies and a partial independent society. All
outputs and 581 actual requests are preserved and labelled invalidated. No old
cell will be inserted into this corrected batch.

## Corrected guarantee and its limit

During each service invocation only, the instrument identifies the requested
publication as the entry caller and records the actually executed provider as
the callee. Direct and transitive re-exports are covered; aliases to the same
author's previous code remain non-cross-author. `service_entries` and per-case
`service_entry_edges` distinguish entry dispatch from an internal Python call.
This is service delegation provenance, not evidence that the wrapper author
wrote or independently understands the provider implementation.

Both entry and internal edges allow the same shape-preserving return
intervention. Tests require a correctly executed request, an actual edge hit,
and lost correctness without exception or input mutation. Instrumented/plain
parity verifies that observation does not change the service result. Native C,
arbitrary reflection and generator iteration remain incompletely traced.

## Fixed corrected batch, declared before model calls

- Fresh output directory `studies/tool_ecology/runs/demand-batch-02`.
- Eight role-free agents, six rounds, seeds 71/108/2026.
- Local-neutral, local-boids, independent; counterbalanced order as before.
- At most six model calls per agent-round, four concurrent agents, 3,000 maximum
  output tokens per call; maximum 2,592 physical requests.
- Same GPT-6-Luna gateway/model, pinned mini-SWE-agent and Docker image.
- Exact source committed and recorded before launch. No runtime edits while
  agents or graders use it. No silent retries, model fallback or score-selected
  stopping. A concrete infrastructure failure may stop the batch with evidence.
- Complete all nine valid societies, then freeze, replay without instrumentation,
  intervene on the predeclared first eligible edges, and run the common fresh DEV
  panel and dependency-provenance analysis. Three seeds remain exploratory.

Report correctness, adoption, self-contained capability, persistent narrow
contribution and collective coverage separately. A failure to form specialists
is a valid result. This toy ecology may be too inexpensive for generalists to
make complementary specialization useful; this is a testable interpretation,
not a reason to reclassify whole-library adoption as division of labour.
