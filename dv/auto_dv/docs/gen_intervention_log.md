# Intervention log (Zone A team)

Append-only record of every owner question and answer, every restart, every fence event, and
every manual repair a human made to generated work (humans append their own entries). Entry
header: `## <ID> - <YYYY-MM-DD> - <LAUNCH|QUESTION|ANSWER|RESTART|FENCE|REPAIR|NOTE>`. IDs are
`LOG-nnn` for team entries, `Q-nnn` for owner questions (the answer is appended under the same
question), `H-nnn` for human repairs.

## LOG-001 - 2026-09-03 - LAUNCH

Launch-precondition check (`DV_prompt.txt` Section 12, items 1-11) PASS at export commit
`1908ddd`. Script: `dv/auto_dv/tools/gen_launch_check.sh`. Evidence:
`dv/auto_dv/evidence/gen_launch_check_2026-09-03.log`. The first run of the script reported
items 9 and 11 FAIL; cause was locale-dependent `sort` inside the script's set comparison, not a
clone defect. Fixed (`LC_ALL=C`), re-run, all items PASS. Team startup sequence step 1 begins.

Tooling inventory at launch (for the record): codex-cli 0.152.1 (cross-model reviewer), Claude
Code 2.1.259 (this session), VCS X-2025.06-SP2 + Verdi, LSF (`bsub` available, `regress` queue),
Python 3.12.10 venv present with cocotb, lowRISC rv32imcb GCC present. No Spike in the clone or
on PATH: the team builds upstream `riscv/riscv-isa-sim` under `<clone>/tools/` per
`SIM_RECIPE.md` Section 11 (`tools/` is excluded locally through `.git/info/exclude`).

## Q-001 - 2026-09-03 - QUESTION (to owner)

File-naming conflict between fence and team prompt. `docs/dv/FENCE.md` (Updates and landing)
says every new file under `dv/auto_dv/**` uses the `gen_` prefix, exempting only
`dv/auto_dv/.gitignore` and `dv/auto_dv/contract/**`. `agent_team_prompt.txt` names
`dv/auto_dv/docs/intervention_log.md` and `dv/auto_dv/docs/dashboard_metrics.md` without the
prefix, and the fence-provided cross-review wrapper writes `dv/auto_dv/reviews/<date>-codex-<name>.md`
without it. Applying "FENCE.md wins": every file the team creates carries the `gen_` prefix
(this log is `gen_intervention_log.md`); review-wrapper artifacts keep the wrapper's own naming
because the team does not edit fence-provided tooling. Please confirm this reading, or state that
the landing check exempts `docs/` and `reviews/`. Status: pending; no work depends on the answer.

## LOG-002 - 2026-09-03 - NOTE

`IBEX_TOOLS_DIR` (`/localdev/fzhang/ws/tools`) contains `spike-ibex-cosim/` and `src/`. The
first is the lowRISC Spike fork, which `DV_prompt.txt` Section 3 fences. Every teammate spawn
prompt names both paths as do-not-read. `ci/env.sh` does not reference either.

## LOG-003 - 2026-09-03 - NOTE (reviewer availability)

Probe of the preferred cross-model reviewer failed: `codex exec` (codex-cli 0.152.1, model
gpt-5.6-sol, reasoning high) returns "ERROR: You hit your spend cap set by the owner of your
workspace." before answering. Per CLAUDE.md (Cross-model review policy, reviewer preference)
and the cross-review skill's fallback clause, reviews use a fresh Opus-class-or-above Claude
session until codex is available again; every artifact header records the model used and the
raw codex error. Owner action that would restore the preferred path: raise the codex spend cap.
The Orchestrator re-probes codex before each review and switches back when it answers.

## A-001 - 2026-09-03 - ANSWER (owner ruling on LOG-003, relayed verbatim)

Owner (Forrest Zhang), in the Orchestrator session, 2026-09-03: "Note, if codex is still
unavailable, use a fable reviewer". Applied: while codex reports the spend cap, cross-model
reviews run in a fresh `claude -p --model fable` session (Claude Fable 5.1, the same model
family as the executing session but a separate session with no shared context). Each artifact
header records the CLI version, the model the run reports, and the codex error that triggered
the fallback. The Orchestrator re-probes codex before every review.

## Q-002 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-1 (gen_dut_top parameters; supersedes rtl-arch Q-A/Q-B by consolidating them). ibex_core
parameters that ibex_top derives from SecureIbex default to 0 on ibex_core. The team intends
gen_dut_top to mirror ibex_top for the opentitan configuration: MemECC=1 (39-bit bus data),
DummyInstructions=1, ICacheTweakInfection=1, ResetAll=1, RegFileECC=0 with RegFileDataWidth=32,
DbgHwBreakNum=1, DmBaseAddr=0x1A110000, DmAddrMask=0xFFF, DmHaltAddr=0x1A110800,
DmExceptionAddr=0x1A110808, CsrMvendorId=0, CsrMimpId=0, PMP reset values from ibex_pkg.
Consequence to confirm: with RegFileECC=0 the in-core register-file ECC alert is unreachable (the
RF ECC of the shipped configuration lives in the lockstep shadow core, outside the DUT), so
alert_major_internal_o has one live source (PC increment check) and F-SEC-004..006 become negative
checks. Blocks: the SEC/DIT feature set, bus widths, and the wrapper. Default: mirror ibex_top
exactly; do not enable RegFileECC.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-003 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-2 (fence confirmation for two non-Ibex specification sources). (a) The draft bitmanip 0.93
specification (github.com/riscv/riscv-bitmanip) defines the roughly 40 pre-ratification encodings
RV32BOTEarlGrey enables (F-BIT-016, F-BIT-022..033); (b) the riscv-formal RVFI description
(github.com/YosysHQ/riscv-formal, docs/rvfi.md) defines the trace fields the ISA-model comparator
consumes (F-RVFI-001..033). Both are open-source and not Ibex DV collateral, so the DV Lead reads
DV_prompt.txt Section 3 as allowing them. Blocks: whether the reference model for those
instructions and the RVFI comparator rules are spec-derived or "RTL-defined reference". Default:
treat as allowed, clone both into tools/specs with recorded SHAs; if the owner denies, derive from
rtl/ibex_alu.sv comments and rtl/ibex_core.sv and mark every such feature "RTL-defined reference".

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-004 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-3 (MPRV after dret and in debug mode, B1/B2 above; security-relevant). The RTL leaves
mstatus.MPRV set when dret resumes into U-mode and honours MPRV for data PMP checks in debug mode
although dcsr.mprven reads 0; the debug specification requires MPRV cleared on resume to a less-
privileged mode and ignored in debug mode when mprven=0. Blocks: the PMP privilege model after
dret and in debug mode, and whether the affected tests count as failures at the Phase 1 gate.
Default: checkers implement the debug spec, the tests are marked expected-fail, both are logged as
bug candidates with reproducers, and neither is excluded from the gate without a recorded ruling.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-005 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-4 (dummy instructions and architectural counters, B7). Dummy instructions are counted in
minstret and in the mul-wait/div-wait HPM counters although security.rst states they have no
functional impact. Blocks: the minstret/HPM comparison against the ISA model whenever
cpuctrlsts.dummy_instr_en=1, and the exact-count test design. Default: exact-count checks run with
dummy_instr_en=0; a directed test with dummies enabled asserts minstret_delta >= retired count and
records the RTL count; logged as a bug candidate pending ruling.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-006 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-5 (standing checker-direction policy for Section 5.3). For every doc-vs-RTL mismatch where
the RTL is spec-legal, the team applies dv_principles.md Section 4: the checker follows the RTL and
the doc mismatch is logged. Blocks: expected values in the CSR, counter and icache-port checkers.
Default: apply the policy without waiting; the owner may override any single item by naming it.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-007 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-6 (run-scope defaults for DUT inputs that are neither CSR nor bus; DV Lead decision unless the
owner objects). mcounteren_writable_i tied IbexMuBiOn by default with directed Off and invalid-MuBi
tests; hart_id_i random per test and constant within a test; fetch_enable_i On after reset with
directed Off/invalid tests (RTL treats invalid encodings as Off with no alert, F-IMEM-023, recorded
as a design note); debug_req_i driven as a level held until debug-mode entry, plus one directed
pulse-drop test for the dcsr.cause=0 window (B9); boot_addr_i random per test, stable through
reset. Blocks: TB knob defaults and the RST/SEC test-plan rows. Default: as stated.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).
