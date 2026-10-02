# boidsnet.runner (DRAFT, not frozen), protocol v0.3.11

Single runner for the protocol arms: confirmatory E, L0, R0, IM and exploratory L1, G0m (G0 kept in code only), wired to the mechanism env
(`boidsnet/env/mechenv.py`, mechenv v0.2.1, the single copy in the repo). Stdlib only, except for
the optional `openai` package, which is used only for paid runs. Status: dry-run only. It has
made no model calls and does not touch the old corpus. The stub model writes real table-pipeline
tools from the env's reference primitives, sometimes adding a bug or a neighbour import.

    python -m boidsnet.runner.run --arm L0 --seed 3 --out runs/        # stub model, no API calls
    python -m unittest discover -s tests -t . -v             # 83 tests (incl. mechenv) (protocol properties, sandbox isolation, batch, API retry, hash-seed determinism, U harness)
    python -m boidsnet.runner.smoke --out smoke/                               # protocol §8 ENGINEERING smoke (stub); real: add --model/--key-env/--azure-*/--allow-spend
    python -m boidsnet.runner.pilot --out pilot/ --seed 900 --n-per-arm 10 --score-dev   # 1 society/arm (+2nd L0) + gates + dev U diagnostic
    python -m boidsnet.runner.batch --out runs/ --seeds 1001-1010 --jobs 6     # all arms x pre-listed seeds
    python -m boidsnet.runner.utility --society runs/L0_s1001 --unseal     # U on the SEALED test split (confirmatory only)
    python -m boidsnet.runner.freeze --protocol joint_thesis_protocol.md > FROZEN.json

Requirements for paid runs: see requirements.txt. `openai==1.51.0` REQUIRES `httpx<0.28`. With
httpx 0.28 every OpenAI or AzureOpenAI client fails at construction ("unexpected keyword argument
'proxies'"). Azure: `--azure-endpoint` (or AZURE_OPENAI_ENDPOINT), `--azure-api-version`, and
`--model <deployment name>`. The key is read from `--key-env` and is never written anywhere.

## What each society writes (runs/<arm>_s<seed>/)
- `run_manifest.json`: the full config (arm, seed, N, T, k, m, model, temperature, catalogue scope,
  code and protocol hashes, env name). Fixes audit item 7.
- `rounds.jsonl`: one record per agent-round. It holds the rule flags (`rule_fired`,
  `block_nonempty`, `selection_mode`, `exemplars`, `exemplar_authors`, `exemplar_similarity`,
  `pool_size`, `neighbours`), `prompt_sha256`, prompt length, tokens in/out/cumulative,
  `tool_id`, `parse_ok`, `target`, `static_imports`, `cross_agent_imports`,
  `unresolved_imports`, the harness verdict, and the P_signal signature hash and error count.
- `prompts/<tool_id>.json`: the full system prompt, user prompt and response (for the AAMAS
  AI-disclosure requirement).
- `library/tools/<tool_id>.py` plus `library/index.json`. Every built tool, with its per-probe
  P_signal signature vector and mechenv's own `behaviour_signature` hash. The record also
  holds the declared IMPLEMENTS list, for verify_primitive / M6 / M7 at analysis time.
- `summary.json`: fire rates, tokens, pass count and cross-agent import rate.

## Guarantees (each is tested)
- One prompt template for every arm. Arms differ only in the exemplar block. The three
  framing texts are equal in length to within 3 characters.
- E, L0 and L1 get the same exemplars, chosen by the same rule over the same pool. G0 uses
  the same rule over the whole society. IM gets no exemplars, sees only its own tools, and
  therefore has zero cross-agent imports.
- Local exemplars come only from the ring neighbours.
- Tool ids are assigned by the runner (`aNN_rNN`), so no build can overwrite another.
- A tool is importable AND listed from the next round on, whether or not it passed.
- Rounds are synchronous: nothing built in round r is visible in round r.
- The runner only ever calls `tasks(dev_seed, "dev")`. The test wraps mechenv.tasks and
  raises an error if "test" is requested.
- Sandbox (v0.8, tests/test_sandbox.py): the tool child runs with `python -I`, cwd = library,
  *_API_KEY stripped, and an audit hook that allows importing `tools.<id>` only if <id> was in
  the author's catalogue at build time (per-tool ACL in library/acl.json; self-only in IM). File
  reads are limited to the stdlib and to reachable tool files, so a tool cannot reach the env's
  reference implementations, index.json (hidden verdicts), other runs or site-packages. Writes,
  sockets, subprocesses, exec/spawn/fork and signals are all blocked. Before v0.8 a tool COULD
  load mechenv by absolute path and pass the harness, and IM agents could import guessable
  tool ids.
- A paid run refuses to start without `--allow-spend` and a freeze file whose code hash
  matches. Run directories are never overwritten.

## Decisions to ratify (these are not in v0.3.2 text)
D1 Synchronous rounds.
D2 Catalogue scope (which tools are listed and importable) is society-wide in E, L0, L1
   and G0, and self-only in IM.
D3 Exemplar selection: the m tools in the pool most behaviourally similar to the agent's
   own latest tool, by exact-match fraction on P_signal (errors match nothing). At cold start
   the choice is a seeded random draw.
D4 IM: the merge step is algorithmic (signature dedupe) at analysis time and costs zero
   tokens. The IM prompt has no block, so it is shorter than the other arms' prompts.
D5 The per-build harness verdict is taken on the agent's declared TARGET dev task. An
   unknown target counts as a fail.

D6 One fixed dev seed (0) shared by every society, so all arms see the same task menu. The
   society seed drives only the agents' RNG and the exemplar tie-breaks.
D7 Tool contract: `execute(table, lookup, **params)`. Tools declare TARGET (a dev task or
   NONE) and IMPLEMENTS (primitives, or NONE).
D8 (msg #30) Exemplars are shown as description + execute signature + docstring + IMPLEMENTS,
   capped at 400 characters, never as source. Each agent-round sees a seeded sample of 8 dev
   tasks, drawn from (society seed, agent, round), so the draw is identical across arms.
   Similarity is mechenv.behaviour_similarity on behaviour_vector (P_signal). The build
   verdict is logged but never shown to agents. There is no agent self-test step.

D9 (msg #33) Execution feedback: after each build, the runner (not the model) runs the tool on
   one fixed public input from the DEV seed range and shows the author, in its next prompt,
   the exception or the first 5 rows (capped at 600 chars). No pass/fail and no reference
   output. It is identical across arms and costs zero model calls. Logged as
   `exec_feedback` / `exec_feedback_shown`.

Pilot gates (msg #33, in `runner/pilot.py`): parse rate >= 0.80 in every arm, rule fire rate
>= 0.50 after round 2 in L0/L1/G0, and median pass rate in [0.05, 0.80]. Any failure means we
fix and re-pilot, with no main runs. The stub model passes these trivially, so only a real-model
pilot is informative.

D10 (msg #49 issue 2) R0 = random-neighbourhood repulsion. Each agent-round draws k other agents
   at random (seeded by society seed, agent and round), and the same selection rule and framing
   as L0 run over their tools. The pool size, and so the expected exemplar similarity, match L0.
   L0 vs R0 isolates a stable local neighbourhood at fixed content. G0 stays as the society-wide
   pool contrast.

D11 (v0.3.6, msgs #51/#52) G0m = well-mixed repulsion at matched similarity. `select_matched`
   runs the L0 rule on this agent's OWN k-ring in THIS society and round to get target
   similarities, then gives each target (highest first) the unused NON-neighbour tool with the
   smallest |sim - target|, with a seeded tie-break. No L0-society outcome is used. An empty ring
   pool (round 1) shows nothing, as in L0. A cold start is a seeded random draw of
   min(m, |ring pool|) from non-neighbours, as in L0. If the non-neighbour pool runs out, the
   record is 'matched_short' and the shortfall is logged. Every arm logs `exemplar_match`
   (targets, abs_diff, shortfall), `exemplar_age`, `exemplar_authors` and `exemplar_passed` as
   manipulation checks. The pilot runs PROTOCOL_ARMS = (E, L0, L1, G0m, IM).

D12 (v0.3.8, msgs #59/#60) The pilot runs PROTOCOL_ARMS = E, L0, R0, IM (confirmatory) + L1, G0m
   (exploratory). The fire-rate gate covers L0, R0, L1 and G0m. pilot_report.json also reports the
   G0m matching gate on real-model data (mean exemplar-similarity gap to L0 <= 0.05 and
   shortfall <= 10%). If that gate fails, G0m is reported as 'not tested at matched similarity'.

D13 (v0.8) Robustness. API calls retry transient errors (429/5xx/network) with exponential backoff,
   up to 6 attempts, and log `api_retries` per record. Auth and bad-request errors are not retried.
   A crashed society writes FAILED.json. `runner.batch` reruns it ONCE under the same seed and moves
   the failed directory aside (never deletes it); batch_status.json records every attempt.
   selection_mode `own_tool_crashed` marks rounds where the agent's own latest tool crashed on every
   probe, so its "nearest" exemplars are effectively the seeded shuffle.

D14 (v0.9) mechenv v0.2.1: `sorted(TERMINAL)` (msg #75). The dev menu and test split are now
   independent of PYTHONHASHSEED, and the published seal 25634f77... is unchanged (tested across
   hash seeds, including a whole-society determinism test). The manifest records PYTHONHASHSEED,
   and batch sets it to 0. Reasoning deployments: `--no-temperature`,
   `--token-param max_completion_tokens`, `--param-mode strict|auto`. The manifest's `sampling` block
   records what was actually sent and any adaptation. strict (the default) refuses rather than
   silently changing a pre-registered parameter. exec_feedback rotates its public dev input per
   round from a pre-listed list that is the same in every arm (seed logged).
D15 (v0.9) U harness, runner/utility.py (msgs #73 B1/B3, #76.1/#76.3). L_T is frozen with ONE rule
   in all arms: drop all-crash tools, group by P_signal vector, keep the earliest passing tool per
   group (else the earliest). Dependencies are copied but not listed. The solver sees one test spec
   plus the catalogue. An AST gate allows only from-tools imports and one execute() made of name
   assignments, return and `<tool>.execute(...)` calls with names/constants; no loops,
   conditionals, arithmetic, subscripts, builtins, getattr/importlib/eval/open; <=15 lines; every
   name bound. Scoring uses mechenv.harness on tasks(0,'test') after checking the published seal.
   Task score = MEAN over R attempts; U = mean over tasks; U_by_depth is reported. The test
   split opens only with --unseal.

D16 (v0.10, msg #79) U harness fixes:
   (1) parametric tools are kept when they verify >=1 declared IMPLEMENTS primitive
       (mechenv.verify_primitive), grouped by frozenset of verified primitives;
   (2) each string constant is <=32 chars and the total payload <=128;
   (3) the FULL seal is checked;
   (4) the solver must match the society's sampling block (strict, same deployment), or it
       refuses;
   (6) the catalogue is shuffled per (task id, attempt).
   `--split dev` gives U_dev_DIAGNOSTIC for smoke tests without unsealing. The pilot report adds
   missing_module / sandbox_block / all_crash_on_signal / parametric_candidate /
   own_tool_crashed rates and api_retries.

D17 (v0.11, protocol v0.3.10, msgs #81/#82) Solver cost and diagnostics:
   (A') the solver prompt puts the catalogue FIRST and the task spec LAST; the catalogue is
        shuffled once per (society seed, attempt) with a fixed seed that does not depend on the
        arm. Every task within an attempt then shares a cacheable prefix. cached_tokens are
        logged when the API returns them (solver_log `tokens_cached`, utility.json
        `solver_cached_tokens`).
   (B') `--split dev` never writes or prints a per-society/per-arm U_dev. `runner.pilot
        --score-dev` reports gate_fail_rate plus gate_fail_reasons per arm, and U_dev POOLED
        across arms only.
   Smoke gates in pilot_report.json `smoke_gates`: gate_fail <= 0.20 and missing_module <= 0.10
   in every arm. D3-P (parametric_candidate > 0.25 in any arm) is reported as a trigger for
   mechenv v0.3. S1: `projected_solver_calls` / `projected_solver_tokens`
   (= n_per_arm x 6 arms x 60 tasks x 3 attempts x measured tokens/call), for Xisen to approve
   before the freeze.

D18 (v0.11.2, Qi-side security review msg #91) Credential isolation. Before this version, the tool
   child inherited the parent env minus *_API_KEY, so a key named e.g. AZURE_AI_KEY (or any
   *_TOKEN/*_SECRET) was readable by model-generated tool code via os.environ. Now the child env
   is an explicit ALLOWLIST (PATH, LANG/LC_ALL, PYTHONHASHSEED), and os.environ is cleared in the
   child before the tool is imported. Canary tests (tests/test_sandbox.py
   CredentialIsolationTests) put AZURE_AI_KEY/..._TOKEN/..._SECRET canaries in the parent env and
   assert that they are absent from os.environ, /proc/self/environ and /proc/<parent>/environ in
   the child. The canary test FAILS on v0.11.1 (regression verified). The container that
   built and tested this runner never held any model-API key, and no real-model run has ever
   been made with it.
   Residual risk: a Python audit hook is not an OS-level boundary. A real-model run should use
   a dedicated low-quota key that is rotated afterwards.

D19 (v0.12, Qi-side review msg #96) Smoke/pilot integrity.
   (1) Dev blinding is real, not just in the reports. With --split dev, solver_log.jsonl
       has no passed/verdict. Gate-passing attempts persist neither the response, nor the
       imported ids, nor the glue file, so per-arm U_dev cannot be recomputed from disk.
       Gate-failing responses (score 0 by rule) are kept for debugging. Tested.
   (2) `runner.smoke` runs exactly the §8 smoke: seed 9001; E, L0, R0, IM; N=8, T=3; budget
       300000; societies in auto mode. Those knobs cannot be passed. It ASSERTS coverage (the
       exact dirs, each manifest's seed/N/T/budget/param_mode/engineering flag, no FAILED.json,
       N*T records unless truncated, the same effective sampling across arms, dev diagnostic for
       all four arms) and has PASS=False on any problem. smoke_gates has PASS=False if the dev
       diagnostic was skipped. The pilot runs a 2nd L0 society (--l0-seed2, default seed+1)
       and reports the L0 pair.
   (3) `run.py --engineering` is the pre-freeze path. It is mutually exclusive with --frozen,
       writes dirs ENG_<arm>_s<seed>, and the manifest records engineering:true plus the
       deviation note and param_mode. Utility refuses split=test for engineering societies;
       batch and pilot refuse --engineering. Dev-only compatibility rule: for an engineering
       society, auto adaptations are allowed, and the solver must match the society's
       EFFECTIVE (post-adaptation) sampling block in strict mode. Confirmatory societies still
       refuse any adaptation.

D20 (v0.13, msg #102 from i_alx4y9xgu1) The OS is the boundary, not the audit hook. The hook's
   policy (OK_FILES, STDLIB, acl, BLOCK_PREFIX) lived in the child's own mutable globals.
   `import __main__` plus one assignment re-opened ALL of these, verified on v0.12:
     - the PARENT's initial environ (/proc/<ppid>/environ), i.e. the model key;
     - mechenv's reference implementations;
     - index.json verdicts;
     - other agents' tools (IM ACL bypass).
   So D8/D18's "closed" claims held only against non-adversarial tools.
   Now each tool child runs under `unshare --mount --pid --fork --kill-child --mount-proc --net`,
   then `setpriv` to uid/gid 65534 with no capabilities and no_new_privs (os-root). Without
   root: an unprivileged user namespace (os-userns). The child sees:
     - its own PID namespace only, so the runner is invisible;
     - no network;
     - a tmpfs view at /mnt/lib holding ONLY the ACL-reachable tool files;
     - empty tmpfs over /tmp, /var/tmp, /home, /root, /srv, the runner tree and the run-output tree.
   The hook remains as a second layer. isolation_level() probes this by running it. run.py
   and real-model utility scoring REFUSE unless the level is os-*, and it is recorded in the
   manifest as sandbox_isolation. Tests: HookTamperTests tamper first, then attempt each leak
   (parent initial environ with a canary, reference impl, index.json, ACL import, network,
   uid). On hook-only, every attack succeeds (regression verified); on os-root, all fail.
   No real-model run has ever been made, so no data are affected.

D21 (v0.14, msg #105 from i_alx4y9xgu1) Allowlist ROOT instead of a denylist of hidden dirs.
   v0.13 covered /tmp, /home, /root, /srv and the repo with tmpfs but left the rest of the host
   FS readable (/etc, /opt, /run, /var ...), which has the same shape as the #91 env bug. Now
   _NS_SCRIPT pivot_roots into a minimal root. The root contains ONLY:
     - a read-only copy of: the real interpreter; mount/umount/setpriv; the ELF dependency
       closure of all of them plus every lib-dynload extension (ldd, 23 libs here);
       /etc/ld.so.cache;
     - the host's /bin /sbin /lib /lib64 symlinks;
     - a ro bind of the stdlib dir;
     - /dev/{null,urandom};
     - a fresh /proc;
     - /sandbox/lib/tools with the ACL-reachable tools, on tmpfs.
   /usr is NOT bound wholesale (msg #107): /usr/local, /usr/share and dist-packages do not
   exist in the sandbox. The root is built once per process (_sysroot), so a call costs about
   0.07 s.
   The old root is detached and / is remounted ro. Applies to os-root and os-userns alike, so the
   os-userns "real uid can read the host" caveat is gone. The skip-silently hide list (#105.2)
   no longer exists.
   isolation_level() probes it by running it. It requires all of: parent PID invisible, NONE of
   /etc/passwd, /etc/hostname, /home, /root, /tmp, /opt, /var, /run, /usr/local, /usr/share,
   dist-packages or a host tempdir exists,
   CapEff == 0, and uid 65534 in os-root. PROBE_REPORT (level, probe output, root spec) is
   written into every manifest as sandbox_probe.
   model.py also refuses to load a key unless the level is os-* (the run.py check is kept too).
   Tool ids passed to the namespace script must match runner-assigned formats.
   New tests, each tampering with the hook first:
     - canaries planted in /etc, /opt, /var/lib, /usr/local/etc, /usr/share and the repo are invisible;
     - mount escape (ctypes unshare(USER|NS), umount2('/'), mount tmpfs) still cannot reach a
       /etc canary;
     - loopback to a listener in the runner's netns fails;
     - uid 65534, CapEff 0, NoNewPrivs 1;
     - non-runner tool ids are refused.
   Known: inside the sandbox a tool can still create its own unprivileged user namespace
   (unshare succeeds). It gains nothing reachable, but a seccomp filter would remove it.

D22 (v0.16, msg #130 cost cap) The smoke's dev-diagnostic solver had no token cap; only the
   societies did. score_society(..., token_budget=) now stops before the next task once the
   cap is reached (overshoot <= 1 call) and reports n_tasks_scored and
   solver_truncated_by_budget. It REFUSES a budget on split='test', because a cap would drop
   sealed tasks and bias U. runner.smoke sets 300000 solver tokens per arm, so the whole smoke
   is hard-capped at about 4 x 300k society tokens + 4 x 300k solver tokens (~2.5M with
   overshoot).

D1-D9 were ratified by the Xisen side (msgs #30, #33) and still need Qi-side ratification.

## Env integration notes
`runner/env_adapter.py` is the only file that touches mechenv. Tools run in a subprocess, and
`SandboxedTool` prefetches all probe calls in one batch, then serves mechenv.harness /
behaviour_signature from the cache.
