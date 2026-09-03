# Zone A fence scope amendment: fence the collateral, not the tools

**Status:** v2.1, 2026-09-02 — BINDING. v1 (owner-proposed, commit 91460209) reviewed
REQUEST-CHANGES; v2 (cb35bb86) re-reviewed **APPROVE-WITH-CHANGES**
(`docs/dv/reviews/2026-09-02-claude-plan-zone-a-fence-scope-amendment{,-v2}.md`); this revision
folds the re-review's with-changes items. Amends the design spec
(`2026-09-01-auto-dv-setup-design.md`) §WS5 zone scoping and §WS7.

## Decision

The fence exists to keep **previous Ibex DV collateral** out of the generation zone. Tools, skills,
and flow mechanics are not collateral. Zone A therefore gets the **local MCP servers and the
skills** of the full tree (Zone A variants where they point at fenced documents), and the fence
moves from "which tools exist" to "which data exists where the tools run".

## Why the spec fenced the tools, and why that was the wrong cut

The spec ships the cleanroom with no MCP servers because the FSDB and coverage servers read
whatever file they are pointed at, and the Zone B blind run writes the human fcov database and
cosim logs into the same artifact tree as the visible run. The hazard is the artifact tree, not
the server. The cleanroom clone itself contains no fenced files — and no fenced FSDBs or coverage
databases, which are run products that never enter a snapshot — so a tool running in the cleanroom
has nothing fenced to read.

Without waveform and coverage-database access, the RTL/Arch agent cannot debug and the closure loop
cannot read its own holes. Fencing the tools would cripple the experiment to protect data that
isolation-by-construction already protects. The shipped tree already disagrees with the old rule:
`DV_prompt.txt` (Section on exclusion arguments) *requires* the siliconpilot `cone_of_influence`
MCP tool for every control-vs-data exclusion argument, and spec:154's design rule ("if Zone A code
cannot compile without fenced sources, fix the contract, never grant a fence exception") is the same
fence-the-data-not-the-tooling instinct applied to compilation.

**Owner ruling (2026-09-02) on tool data-reach:** no mechanical path-enforcement layer is added to
the MCP wrappers or hooks. A freshly cloned cleanroom workspace contains no fenced FSDB, VDB, or
log to point a tool at; Zone B evaluation runs in separate clones. Under the spec's threat model
(accidental contamination by cooperative-but-fallible agents, not adversarial exfiltration), the
isolation is the clone boundary, and the escape suite verifies the boundary's contents rather than
policing per-call tool arguments. Advisory guidance (skills, `DV_prompt.txt`) still directs Zone A
tools at the cleanroom's own out-tree.

## Required changes

1. **Zone A ships the three local MCP servers only** — siliconpilot, fsdb-mcp-server,
   verdi-cov-mcp, pointed (advisorily) at the cleanroom's own out-tree. **The atlassian server is
   Zone B only**: it is a remote HTTP server reaching Confluence/Jira, a plausible home for Ibex
   testplans and DV pages, and no path-based rule can scope it. Any future Zone A MCP addition
   requires a fence review (clause retained from §WS5). Zone A compiles and runs its own
   simulations from the cleanroom clone (see Consequence below), so its waveforms, coverage
   databases, and logs land in the cleanroom's own out-tree. Zone B is evaluation only: its
   outputs, visible or blind, never enter the cleanroom, and nothing is returned to the team.
   This replaces the "no MCP servers in Zone A" rule and retires the spec's visible-run report as
   a feedback channel (code coverage and the generated fcov already exist in Zone A's own runs).
2. **Zone A variants of tool-adjacent files.** These currently point at fenced documents or
   paths and need a Zone A version that points at `docs/dv/SIM_RECIPE.md` and the `dv/auto_dv/`
   namespace instead:
   `.claude/skills/regress`, `.claude/skills/sim-debug`, `.claude/skills/fcov-expectation` (also
   writes outside `dv/auto_dv/`), `.claude/skills/mutation-check` (operationalizes "hidden
   referees inert" as the full-tree-only `+disable_cosim=1`; the Zone A variant states the Zone A
   operationalization — every Zone A check other than the named one disabled — per
   `DV_prompt.txt` Section 8), `.claude/skills/cross-review` (artifacts to `dv/auto_dv/reviews/`;
   the wrapper asserts the **expected Zone A rubric list** so a missing or extra rubric is loud,
   not silent), `.claude/skills/simple-english` (surface list rescoped: `SIM_RECIPE.md` and the
   Zone A docs, not `BUILD_AND_SIM.md`/`ci/reviews/`), `.claude/agents/ibex-debug-analyzer.md`,
   `.claude/agents/ibex-test-generator.md`, `CLAUDE.md` **and `AGENTS.md` as a pair** (the
   validator asserts them together; codex teammates in Zone A need the delegator),
   `.codex/config.toml` (Zone A variant: three local servers, no atlassian), `ci/env.sh` (Zone A
   variant: the lowRISC-spike-fork/cosim disclosure — `SPIKE_INSTALL`, `ci/build-spike.sh`
   references — removed; MCP exports kept), `ci/mcp/README.md` (Zone A variant: the
   `dv/uvm/core_ibex` worked example replaced), and
   `docs/dv/TB_CONTRACT.md` — the Zone A variant is a **positive-list rewrite**, not a redaction:
   seeding, handshake pattern, failure path, ASCII-only logging, with no existing-TB module names,
   event names, manifest paths, or `check_logs.py` behavior.
3. **Zone A rubric set is defined positively** (the cross-review wrapper asserts exactly this
   list): `ai-slop-comments` as-is; `rtl-purity`, `magic-numbers`, `forces-and-hier-access`
   rewritten against `dv/auto_dv/` homes (central handles/binds homes named for the generated TB,
   not `dv/uvm/core_ibex` paths); `assertion-integrity` with the Zone A inert-referee sentence.
   `fence-integrity` and `test-overlap` are Zone B / evaluator rubrics and do not ship to Zone A.
   The mechanical acceptance check for changes 2 and 3 is `DV_prompt.txt` Section 12 item 9, whose
   string and file lists are extended to match: `AGENTS.md` and `.codex/config.toml` join the
   scanned set, and the wrapper's asserted Zone A rubric list is itself checked.
4. **Escape tests** are adjusted to what the rulings make true:
   - the snapshot/clone contains no fenced artifacts: the suite scans the full clone (history
     included) for `*.fsdb`, `*.vdb`, fenced paths, and testlist/fcov identifiers — run products
     cannot enter a snapshot, and the sync validator rejects unclassifiable paths (spec:139; that
     validator and this escape case land together in WS7);
   - spec:163's "read sibling clone" case is **retained and is the escape test for the tool
     data-reach ruling** (the ruling's premise is the clone boundary — this probe tests it), along
     with the retained "fetch master" and "fetch upstream ibex DV" cases; only "query an MCP" is
     replaced;
   - a Zone A session has **no remote MCP configured** (positive assertion against the Zone A
     `.mcp.json`/`.codex/config.toml`; replaces the spec's old "query an MCP" case);
   - a skill in Zone A must not resolve a fenced document path;
   - **negative control:** an allowed operation must succeed (fsdb-mcp opens a Zone A-produced
     FSDB; the recipe's compile-and-run executes) — otherwise a suite whose every probe fails
     passes vacuously (`dv_principles.md` §6 anti-vacuity, applied to the suite itself).
5. **Launch preconditions** (verified mechanically by the Orchestrator, `DV_prompt.txt` Section
   12): `docs/dv/FENCE.md`; `docs/dv/SIM_RECIPE.md` (one executed compile-and-run command, and the
   document **passes the fence-integrity rubric** — see the change-6 allowlist); the Zone A
   `CLAUDE.md`+`AGENTS.md` and `TB_CONTRACT.md` variants (the latter also fence-integrity-checked);
   pristine upstream `vendor/google_riscv-dv` at the locked revision; **`vendor/riscv-isa-sim`
   absent from the snapshot** (see triage below); and `dv/auto_dv/.gitignore`. Until these exist,
   CLAUDE.md Critical Invariant 2 applies: no generation session. (`DV_prompt.txt` Section 12
   precondition 6 bundles both vendors as "pristine upstream at their locked revisions"; it is
   split as part of implementing this amendment — riscv-dv stays "pristine upstream at the locked
   revision", riscv-isa-sim becomes "absent".)
6. **`docs/dv/SIM_RECIPE.md` content allowlist** (it is a derived document distilled from fenced
   flow files, so its content is bounded): VCS compile/elaboration mechanics and flags, run/env
   contract, LSF submission, coverage-merge/URG reporting, site gotchas, the Zone B submission
   command. Excluded: test names, the testlist schema, cosim attachment mechanics, fcov bind
   wiring, `metadata.pickle` internals. Enforced by the fence-integrity precondition in change 5.

## Fence-line triage: other places where the current line is off

Over-fenced (mechanics caught with the collateral; fix by splitting, not by fencing):

| Item | Why it is caught | Proposed cut |
|---|---|---|
| `dv/uvm/core_ibex/{Makefile,scripts/,yaml/,wrapper.mk,vcs.tcl}` | under the `dv/**` deny root | factor TB file lists out; publish the mechanics as the Zone A sim recipe (handoff item 1), bounded by the change-6 allowlist |
| `docs/dv/BUILD_AND_SIM.md`, `docs/dv/COSIM.md` | name existing tests, describe the existing cosim | split into a mechanics/gotchas doc (allowed) and collateral references (fenced) |
| `ci/reviews/*.md` rubrics | five of seven carry fenced paths/identifiers (see review artifact) | positive Zone A set per change 3; `fence-integrity`+`test-overlap` Zone B only |
| skills, agent files, `CLAUDE.md`/`AGENTS.md`, `.codex/config.toml` | point at the two docs above / carry Zone B MCP config | Zone A variants (change 2) |
| MCP servers | data-reach concern | change 1 + the owner ruling above (isolation by clone contents, not per-call policing) |
| `vendor/lowrisc_ip/dv/**`, `vendor/lowrisc_ip/ip/prim/dv/**` | generic lowRISC DV libraries, unclassified | allow: open source, not Ibex-specific (verified: no Ibex-named files) |

Under-fenced or unclassified collateral (add to the manifest as denied):

| Item | Why it is collateral | Action |
|---|---|---|
| `formal/**` at repo root | Ibex formal proofs (icache, data-independent timing); the spec's deny root is `dv/**` only | deny |
| `vendor/riscv-isa-sim/**` | the lowRISC fork's vendored `mseccfg_tests` tree IS the collateral, and the locked rev exists only in the fork — "pristine upstream at the locked rev" is unsatisfiable | **omit from the snapshot**; Zone A fetches upstream `riscv/riscv-isa-sim` itself per `DV_prompt.txt` |
| OpenTitan `hw/ip/rv_core_ibex/dv/**` and its testplans | Ibex DV in an integrator repo, not a fork; the DV prompt's "any fork" wording misses it | add to the prompt's deny wording |
| CHERIoT-Ibex `dv/**` | a fork with its own DV; a likely web-search hit because the `opentitan` config's base ISA names CHERIoT | deny (URL/web guidance) |
| rendered Ibex docs on readthedocs | include the fenced verification pages; the URL deny is right, and the design pages are available locally | keep URL deny |
| `ci/jenkins/**` | names existing tests (`testdata/regr_pass.log`, smoke defaults), testlists, and drives the existing flow (`common.sh`, `check_testlist_knob.sh`) | deny; Zone A owns its own regression scripts (see Consequence) |
| `ci/build-spike.sh`, `ci/setup-cosim.sh`, `ci/run-cosim-test.sh` | build and exercise the Zone B cosim (lowRISC Spike fork) — with `vendor/riscv-isa-sim` absent, a shipped `build-spike.sh` still discloses that a spike cosim referee exists and how it is built | deny |

Consistent as written, kept for the record: `dv/**` tests, testlists, `fcov/`, `env/`, `dv/cosim/`;
the six verification RSTs under `doc/`; `vendor/patches/**`; human fcov bin names never returned
to Zone A; the blind referee as evaluation-only measurement; the Zone B fence notes in
`ci/reviews/fence-integrity.md` and `test-overlap.md`.

## Supersession list (shipped files carrying the retired Zone-B-only rule)

To update when WS7 implements this amendment: `ci/mcp/README.md` §Zone scoping;
`ci/mcp/{siliconpilot-mcp,fsdb-mcp,verdi-cov-mcp}.sh` header comments; `.codex/config.toml`
header comment; `ci/env.sh` MCP-block comment; spec §WS5 zone-scoping paragraph and the WS5 gate
item "the cleanroom clone demonstrates *no* MCP servers configured" (which becomes: the cleanroom's
client configs list exactly the three local servers and no remote ones); spec §WS7
enforcement-stack item 2 and its "query an MCP" escape case. The WS5 ledger/evidence lines that
mark that gate item PENDING-WS7 point at the superseded criterion; WS7 closes them against the
new one.

## Consequence for the execution model

The DV prompt has the team build its own TB. Zone A can therefore compile and run its own
simulations on LSF from the cleanroom clone: the RTL is present, and nothing fenced is needed to
build a from-scratch TB. Zone B is then for evaluation only. Spec deltas that follow:

- §WS7 "overlay the Zone A diff onto a full `master` tree, run the stock flow" assumed generated
  tests ran inside the existing TB. **Owner ruling 2026-09-02:** both the TB and the tests are
  built from scratch in Zone A. The blind run therefore builds the generated TB and attaches the
  human fcov binds and, where feasible, the cosim referee to it. The attachment mechanics are a
  Zone B implementation task, not an open policy question.
- **The dual-run architecture collapses to a single Zone B evaluation run.** With no visible
  report returned, there is no channel for a blind finding to perturb, so the visible/blind split
  and its canary noninterference test are retired. Zone B runs one evaluation (generated TB +
  attached referees); its artifacts stay Zone B-side for the human evaluation report.
- **`ci/zoneb-submit.sh --compile-only` is retired** (it was a sanitized return channel onto the
  existing TB, which no longer hosts generated tests). Zone A's compile feedback is its own local
  `ci/cleanroom-compile.sh` and its own sim runs. A Zone B submission returns a mechanical
  acceptance only (branch received, evaluation queued — an exit status, no content).
- **WS7 gate rewording:** submission accepted; the evaluation run's artifacts produced Zone-B-side
  only; a dummy `dv/auto_dv/**` artifact lands on a `master` branch through the landing validator.
  (Replaces "results returned through the dual-run structured report".)
- Zone A owns its own regression scripts: compile of the generated TB, the team's testlist tiers on
  LSF, coverage merge, and URG reporting. Nothing from the existing flow is reused. Zone A submits
  its branch for Zone B evaluation at the Phase 1 gate and at closure; the submission command is
  part of `SIM_RECIPE.md`, and nothing returns.
- `docs/dv/dv_principles.md` §6 states "hidden referees inert" operationally as `+disable_cosim=1`,
  which exists only in the full-tree TB. The Zone A operationalization (all Zone A checks other
  than the named one disabled) is stated in `DV_prompt.txt` Section 8; the principles file gains
  the same scoping sentence outside its hash-anchored block (as handoff item 4.2 already did for
  the boundary rules), and the Zone A `mutation-check` skill variant carries it (change 2).
- `docs/dv/TB_CONTRACT.md` documents cocotb stimulus on the existing TB. For the from-scratch TB
  the Zone A variant is a positive-list mechanics reference (change 2), not the interface the
  team builds against.

## Rulings recorded (2026-09-02)

- The DUT is the `gen_dut_top` wrapper (`ibex_core` + `ibex_register_file_ff`; lockstep,
  scrambled RAMs, and top-level alert aggregation out; `cheriot_enable_i` tied to `IbexMuBiOff`
  inside the wrapper).
- CHERIoT mode is out of scope under the "cheriot-out-of-scope" carve-out. The `opentitan`
  configuration's `BaseIsaRV32IorCHERIoT` puts 23 CHERI-touching RTL files in the DUT with no
  allowed specification or reference model.
- The riscv-dv clause stands: generator in scope; coverage model and testlists reference-only;
  adopted bins marked and counted separately.
- Tool data-reach: no mechanical MCP path-enforcement layer (see the Decision section); the
  atlassian MCP does not ship to the cleanroom.

## Open items for the owner

1. Approve this v2 through cross-model re-review (v1 verdict REQUEST-CHANGES; both Critical
   findings resolved by the owner rulings above; Major/Minor findings folded into changes 1–6,
   the triage tables, the supersession list, and the execution-model deltas).
2. Encode the triage tables in `ci/fence.yaml` when WS7 is planned.
3. Implement the blind-run attachment of the human fcov binds and cosim referee onto the
   generated TB (Zone B, WS7 planning).
