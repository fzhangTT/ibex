# Zone A fence scope amendment: fence the collateral, not the tools

**Status:** proposed by the owner (fzhang), 2026-09-02. Amends the design spec
(`2026-09-01-auto-dv-setup-design.md`) §WS5 zone scoping and §WS7. Binding once it has passed the
cross-model review that the spec's other amendments went through.

## Decision

The fence exists to keep **previous Ibex DV collateral** out of the generation zone. Tools, skills,
and flow mechanics are not collateral. Zone A therefore gets the **same MCP servers and the same
skills** as the full tree, and the fence moves from "which tools exist" to "which data the tools
can reach".

## Why the spec fenced the tools, and why that was the wrong cut

The spec ships the cleanroom with no MCP servers because the FSDB and coverage servers read
whatever file they are pointed at, and the Zone B blind run writes the human fcov database and
cosim logs into the same artifact tree as the visible run. The hazard is the artifact tree, not
the server. The cleanroom clone itself contains no fenced files, so a code-analysis server
pointed at it has nothing fenced to read.

Without waveform and coverage-database access, the RTL/Arch agent cannot debug and the closure loop
cannot read its own holes. Fencing the tools would cripple the experiment to protect data that
can be isolated by directory.

## Required changes

1. **Zone A reads only its own artifacts.** Zone A compiles and runs its own simulations from the
   cleanroom clone (see Consequence below), so its waveforms, coverage databases, and logs land
   in the cleanroom's own out-tree. Zone A's MCP servers and skills are pointed at that out-tree
   and nowhere else. Zone B is evaluation only: its outputs, visible or blind, never enter the
   cleanroom, and nothing is returned to the team. This replaces the "no MCP servers in Zone A"
   rule and retires the spec's visible-run report as a feedback channel (code coverage and the
   generated fcov already exist in Zone A's own runs).
2. **Zone A variants of tool-adjacent files.** These currently point at fenced documents or
   paths and need a Zone A version that points at `docs/dv/SIM_RECIPE.md` and the `dv/auto_dv/`
   namespace instead:
   `.claude/skills/regress`, `.claude/skills/sim-debug`, `.claude/skills/fcov-expectation` (also
   writes outside `dv/auto_dv/`), `.claude/skills/cross-review` (artifacts to
   `dv/auto_dv/reviews/`; the wrapper asserts the expected rubric file list so a fenced rubric's
   absence is loud, not silent), `.claude/agents/ibex-debug-analyzer.md`,
   `.claude/agents/ibex-test-generator.md`, `.claude/skills/simple-english` (names the fenced
   docs as its scope), `CLAUDE.md` (carries the marker `FENCE-ZONE: A` in its first ten lines),
   `ci/env.sh` (the spike-fork comment and paths removed), `ci/mcp/README.md` (a `dv/uvm/core_ibex`
   path example), and `docs/dv/TB_CONTRACT.md` (Zone A variant: cocotb-on-VCS mechanics only,
   with the `dv/uvm/core_ibex` paths and the `BUILD_AND_SIM.md` references removed). The
   mechanical acceptance check is `DV_prompt.txt` Section 12 item 9.
3. **Escape tests** gain two cases: an MCP server asked for a path outside the cleanroom out-tree
   must fail, and a skill in Zone A must not resolve a fenced document path.
4. **Launch preconditions** (verified mechanically by the Orchestrator, `DV_prompt.txt` Section
   12): `docs/dv/FENCE.md`, `docs/dv/SIM_RECIPE.md` (one executed compile-and-run command), the
   Zone A `CLAUDE.md` and `TB_CONTRACT.md` variants, pristine upstream `vendor/riscv-isa-sim` and
   `vendor/google_riscv-dv` at the locked revisions, and `dv/auto_dv/.gitignore`. Until these
   exist, CLAUDE.md Critical Invariant 2 applies: no generation session.

## Fence-line triage: other places where the current line is off

Over-fenced (mechanics caught with the collateral; fix by splitting, not by fencing):

| Item | Why it is caught | Proposed cut |
|---|---|---|
| `dv/uvm/core_ibex/{Makefile,scripts/,yaml/,wrapper.mk,vcs.tcl}` | under the `dv/**` deny root | factor TB file lists out; publish the mechanics as the Zone A sim recipe (handoff item 1) |
| `docs/dv/BUILD_AND_SIM.md`, `docs/dv/COSIM.md` | name existing tests, describe the existing cosim | split into a mechanics/gotchas doc (allowed) and collateral references (fenced) |
| `ci/reviews/*.md` rubrics | `test-overlap.md` references existing tests | fence that one file, allow the rest |
| skills, agent files, `CLAUDE.md` | point at the two docs above | Zone A variants (change 2) |
| MCP servers | data-reach concern | change 1 |
| `vendor/lowrisc_ip/dv/**`, `vendor/lowrisc_ip/ip/prim/dv/**` | generic lowRISC DV libraries, unclassified | allow: open source, not Ibex-specific |

Under-fenced or unclassified collateral (add to the manifest as denied):

| Item | Why it is collateral |
|---|---|
| `formal/**` at repo root | Ibex formal proofs (icache, data-independent timing); the spec's deny root is `dv/**` only |
| `ci/jenkins/**` | names existing tests (`testdata/regr_pass.log`), testlists, and drives the existing flow (`common.sh`, `check_testlist_knob.sh`) |
| `ci/build-spike.sh`, `ci/setup-cosim.sh`, `ci/run-cosim-test.sh` | build and exercise the Zone B cosim (lowRISC Spike fork) |
| `vendor/riscv-isa-sim/**` | the lowRISC fork (`mseccfg_tests`), not upstream; replace with pristine upstream at the locked rev, as done for riscv-dv |
| OpenTitan `hw/ip/rv_core_ibex/dv/**` and its testplans | Ibex DV in an integrator repo, not a fork; the DV prompt's "any fork" wording misses it |
| CHERIoT-Ibex `dv/**` | a fork with its own DV; a likely web-search hit because the `opentitan` config's base ISA names CHERIoT |
| rendered Ibex docs on readthedocs | include the fenced verification pages; the URL deny is right, and the design pages are available locally |

Consistent as written, kept for the record: `dv/**` tests, testlists, `fcov/`, `env/`, `dv/cosim/`;
the six verification RSTs under `doc/`; `vendor/patches/**`; human fcov bin names never returned
to Zone A; the blind referee as evaluation-only measurement.

## Consequence for the execution model

The DV prompt has the team build its own TB. Zone A can therefore compile and run its own
simulations on LSF from the cleanroom clone: the RTL is present, and nothing fenced is needed to
build a from-scratch TB. Zone B is then for evaluation only. Two spec items follow:

- §WS7 "overlay the Zone A diff onto a full `master` tree, run the stock flow" assumed generated
  tests ran inside the existing TB. **Owner ruling 2026-09-02:** both the TB and the tests are
  built from scratch in Zone A. The blind run therefore builds the generated TB and attaches the
  human fcov binds and, where feasible, the cosim referee to it. The attachment mechanics are a
  Zone B implementation task, not an open policy question.
- Zone A owns its own regression scripts: compile of the generated TB, the team's testlist tiers on
  LSF, coverage merge, and URG reporting. Nothing from the existing flow is reused. Zone A submits
  its branch for Zone B evaluation at the Phase 1 gate and at closure; the submission command is
  part of `SIM_RECIPE.md`, and nothing returns.
- `docs/dv/dv_principles.md` §6 states "hidden referees inert" operationally as `+disable_cosim=1`,
  which exists only in the full-tree TB. The Zone A operationalization (all Zone A checks other
  than the named one disabled) is stated in `DV_prompt.txt` Section 8; the principles file should
  gain the same scoping sentence outside its hash-anchored block (as handoff item 4.2 already
  plans for the boundary rules).
- `docs/dv/TB_CONTRACT.md` documents cocotb stimulus on the existing TB. For the from-scratch TB it
  is a mechanics reference (seeding, handshake, failure path, ASCII rule), not the interface the
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

## Open items for the owner

1. Approve this amendment through cross-model review.
2. Encode the triage tables in `ci/fence.yaml` when WS7 is planned.
3. Implement the blind-run attachment of the human fcov binds and cosim referee onto the
   generated TB (Zone B, WS7 planning).
