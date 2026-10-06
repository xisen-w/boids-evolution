# Original Boids guidance controls v1 (review draft)

This is an **unfrozen** implementation draft. Offline DEV contracts verify
engineering behavior; they do not establish experimental efficacy. No paid model
calls or sealed TEST evaluations are authorized by this update.

## Source and scope

Recovered patch base: `b0b4ff90f39231443c24e946e239330f7fe83dde`.
Integrated onto developer commit `60097b0de92fb1a9f8027ea6d62b0cba04365f51`
on 2026-10-06, preserving its newer audit figure and tests. The original main
branch is `524dc7627c9c33bf3692dd0533e9538f0af70b5f`. Original mechanisms were
read in `legacy/src/boids_rules.py`; TCI in `legacy/src/complexity_analyzer.py`.
The frozen `legacy/` tree is unchanged. The Library bundle SHA256 is
`7cc6d3c9649319d62c5f1bb6b19bc6a871b18f62054b3f0e17a663da688f4ba5`.

## Four configurations and comparisons

| CLI arm | S | A | C |
|---|---:|---:|---:|
| neutral000 | 0 | 0 | 0 |
| AC011 | 0 | 1 | 1 |
| SAC111 | 1 | 1 | 1 |
| S100 | 1 | 0 | 0 |

Primary: SAC111 minus neutral000; SAC111 minus AC011. Supporting: S100 minus
neutral000. These are adaptive-policy effects conditional on common evidence
selectors. They are not pure social-information effects or separate S-by-A and
S-by-C interactions. The four cells do not identify those two interactions.

For a fixed pre-round state, selectors and evidence are identical across arms;
only active versus neutral directional instructions vary. Histories, selected
evidence, token use, and summaries can diverge after policies change behavior.
Equal evidence is not a claim of identical realized trajectories or prompt lengths.

## Shared substrate

All four arms use the existing synchronous Society loop, ring neighbourhood,
seeded task menus, tool-building system role, task contract, catalogue, parser,
previous-tool execution feedback, sandbox, dev harness, and import ACL. All see
the society catalogue, including failed tools. Current-round tools become visible
next round. No arm gains a separate build, role, or reflection call; this runner
uses execution feedback rather than the original system's generative reflection.

A common evidence bundle is built before prompt rendering regardless of toggle.
It includes S tool excerpts, A quality/adoption exemplars and their scores/pass
metadata, and C descriptive statistics. A=0 does **not** remove quality metadata.
The historical hiding of dev harness verdicts remains true only for legacy arms;
SAC exposes selected dev-target pass metadata equally to all arms. The existing
`MechEnv.harness` uses each dev task's `probe_seeds["coverage"]`: this is a new
common P_coverage-derived correctness feedback channel, not an independent
held-out probe stream. It never reads sealed TEST tasks.
The sealed TEST split, scoring utility, sandbox and ACL enforcement are unchanged.

## Mechanisms and explicit adaptations

- S: original `TfidfVectorizer(stop_words='english')` over neighbour tool
  name/label plus description. Compare neighbour pairs, cosine >= 0.3 (the original helper default; historical
  `legacy/run_experiment.py` constructor/run default was 0.45), descending
  similarity, select at most two distinct tools, first 20 source lines. It does
  not compare a candidate or the agent's latest tool against neighbours. Stable
  tool-ID ordering makes ties reproducible. This is a lexical semantic proxy,
  not a verified functional-distance measure. The 0.3 draft threshold is a
  declared parameter choice, not reproduction of the original 0.45 runtime. `requirements-sac.txt` pins the
  optional selector dependency; missing sklearn fails explicitly, not silently.
- A: neighbours from the preceding three rounds; highest TCI among passing
  tools, otherwise highest TCI overall; optional positive-adoption leader.
  TCI-Lite retains the original weights with the tool-import namespace adapted
  to `from tools import ID`. Dev harness pass replaces original test metadata.
  Adoption counts distinct later snapshot tools statically importing
  an earlier exemplar with recorded build-time ACL permission, not execution success or verified useful reuse. Stable IDs break
  ties. TCI is a complexity proxy, not utility or quality proof.
- C: the old model-generated summary could contain suggestions. This draft uses
  explicitly versioned `descriptive_counts_v1`: deterministic preceding-round
  declared target/primitive counts (not verified capabilities), without freeform tool descriptions or suggested next
  steps. Zero observer model calls and zero observer token cost in every arm.
  The shared summary still consumes builder context tokens.
  Only active C adds a directive to contribute to the emerging trend. This is
  a disclosed summary-policy adaptation, not identical original C wording/input.

All active instructions are evidence-dependent; no available evidence means that
rule does not fire. Shared evidence is visible even when the corresponding active
instruction is off. Neutral evidence itself can influence behavior.

## Provenance and paper mapping

| Paper concept | Implementation / record |
|---|---|
| Four policy configurations | `config.py`: SAC_SPEC, design_version, mechanism_toggles |
| Common pre-round state | `society.py`: run snapshot and `_agent_turn` |
| Shared S/A/C evidence | `mechanisms.py`: build_evidence |
| Active versus neutral guidance | `mechanisms.py`: render_evidence |
| TCI adaptation | `mechanisms.py`: compute_complexity |
| Prompt and evidence provenance | rounds.jsonl evidence, hashes; prompts/*.json full text |
| Exact selector/firing metadata | mechanism_evidence; mechanism_fired; toggles |
| Common ACL/build/evaluation | existing Library.add, Society._evaluate, SandboxedTool |
| Sealed utility | existing utility.py, unchanged |

Evidence records selected IDs, authors, ages, pass/TCI/adoption/similarity metadata,
source excerpt provenance, and summary policy/cost. Prompt/block/evidence hashes
allow audit of the conditional invariance claim without asserting runtime proof.

## Legacy design stays separate

E/L0/R0/IM/L1/G0m/G0 keep their existing behavioral selectors and are tagged
`behavioral_repulsion_v0.3.13`; new arms are `original_boids_guidance_v1`.
Historical `PROTOCOL_ARMS`, smoke, pilot and batch remain legacy-only. They are
not a launcher or approval for SAC, and historical budgets/seeds/society counts
must not be carried over. Old docs and decisions describe that versioned family.

`examples/sac_design.template.json` is declarative and intentionally incomplete:
N, horizon, budgets, seeds and model require a future reviewed freeze. SAC CLI
requires explicit agent count, round count and positive token budget rather than
silently inheriting legacy CLI defaults. Library-level defaults remain for legacy
compatibility and are not approved research sizing. Offline tests use fixed fixtures and stub builders only.

Before future execution, review/pin transitive dependencies and Python version,
perform a securely configured model smoke, approve design sizing and
budget, then freeze protocol, code and dependency environment. Existing paid-run
safety checks remain in place; this draft is not itself a preregistration freeze.

## Engineering verification

`tests/test_sac_controls.py` and `tests/test_sac_sharing.py` cover nonempty S/A/C
evidence, matched descriptive content across toggles, original build ACLs,
previous-round visibility and actual transitive cross-agent `.execute` calls.
Wider runner IDs are accepted by both the sandbox and stub catalogue parser.
The Linux offline CI job requires `os-root` isolation; it does not disable the
sandbox or supply model credentials. macOS uses the existing hook-only fallback
and real-model execution still refuses that isolation level.

`SAC_STATIC_CHECKS.json` preserves the October 2 archive provenance only; its
old hashes and runtime-unverified status do not describe this integration.
