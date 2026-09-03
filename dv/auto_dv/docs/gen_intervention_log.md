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

## Q-002 (revised) - 2026-09-03 - QUESTION revision (DV Lead wording, filed verbatim; supersedes the Q-002 text above and absorbs rtl-arch Q-A/Q-B/Q-C)

Q-DL-1 (revised) gen_dut_top build choices that fix the DUT boundary. The DUT is ibex_core plus
ibex_register_file_ff; ibex_core parameters that ibex_top derives from SecureIbex default to 0 on
ibex_core, so the wrapper must set them. The team proposes to mirror ibex_top for the opentitan
configuration: (a) RegFileECC=0 with RegFileDataWidth=32 (rtl/ibex_top.sv:215,217): the shipped
integration checks register-file ECC only in the lockstep shadow core, which is outside the DUT,
so gen_regfile_ecc (rtl/ibex_core.sv:1214-1303) does not elaborate and alert_major_internal_o has
a single live source, the PC-increment check; setting RegFileECC=1 instead would bring the ECC
encoder/decoders, a 39-bit register file and the rf_ecc_err alert into the DUT (RegFileDataWidth
=39, RegFileCapEccWidth=42, WordZeroVal=39'h2A00000000) but departs from the shipped
configuration; (b) ResetAll=1 (rtl/ibex_top.sv:212-213) so data-path flops reset and coverage
sampling sees no X; (c) compile with +define+RVFI so the retirement trace exists for the ISA-model
comparison DV_prompt Section 7 requires (RVFI adds flops and outputs only, reads ibex_core
internals at rtl/ibex_core.sv:1851-1853 and 2280-2292, and is recorded in the probe register as a
define-gated DUT interface); (d) MemECC=1 (39-bit bus data), DummyInstructions=1,
ICacheTweakInfection=1, DbgHwBreakNum=1, Dm* defaults, CsrMvendorId=CsrMimpId=0, PMP reset
values from ibex_pkg. Decision blocked: T-005 (wrapper), every SEC/DIT/IRQ feature that depends
on these values (feature list Section 2), bus widths in the memory agents. Default while pending:
exactly the proposal above; the config banner prints every value.

Status: pending. Default applied meanwhile.

## Q-008 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-7 (MEM-13, security-relevant, RTL-defined). After a PMP fault on the first half of a
misaligned data access, Ibex still issues the permitted second half on the data bus, so a
misaligned store that faults performs its second-word write (rtl/ibex_load_store_unit.sv:489-531,
rtl/ibex_core.sv:1063; F-PMP-087, F-EXC-033). The RISC-V privileged specification permits a
decomposed misaligned access to be partially performed, so this is not a specification violation;
OpenTitan-level expectations may still require suppression. Decision blocked: whether the
scoreboard models the partial write as legal or the checker asserts suppression (expected-fail bug
candidate). Default: model it as RTL-defined, cover it with bins pmp_fault x {aligned, mis_first,
mis_second, mis_both} x {load, store}, and log it in the bug log as a security/integration note
rather than a bug.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-009 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-8 (CTRL-04, security-relevant, RTL-defined). With fetch_enable_i not exactly IbexMuBiOn,
interrupt and debug entry still update mepc/mcause/dpc and the PC (only the handler fetch is
blocked), and every invalid MuBi encoding acts as Off with no alert, unlike cheriot_enable_i which
raises alert_major_internal_o (rtl/ibex_core.sv:644-649, 1339-1351; F-RST-015, F-IMEM-023).
Decision blocked: whether a checker expects an alert on an invalid fetch_enable_i encoding (would
fail on current RTL) and whether trap-state changes while fetch is disabled count as a defect.
Default: check the RTL behaviour as-is, cover both cases, record both as design notes for the
security owner, no bug filed.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-010 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-9 (MEM-05 / MEM-19, RTL-defined). Neither bus interface defends against an rvalid with no
outstanding request or an rvalid in the grant cycle; the bus-integrity check runs on such
responses too (alert plus internal NMI on the data side). Decision blocked: whether the TB ever
drives protocol-violating responses. Default (DV Lead run-scope decision): passing tests never
violate the protocol (the memory agents enforce it and a protocol assertion layer checks it);
one directed informational test per bus demonstrates the RTL response to an unsolicited rvalid
and is excluded from the pass gate; recorded as a design note.

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## Q-011 - 2026-09-03 - QUESTION (to owner; worded by the DV Lead, filed verbatim by the Orchestrator)

Q-DL-10 (tb-infra Q-7, ISA model). If an Ibex legalisation cannot live in the DPI shim (for
example the fast-interrupt mie bits 16..30 or mip semantics), may the team carry a local patch
file against the pinned upstream Spike commit (4ffd6ba860f4190ceac2716fa3c2cf139e85538f)? Decision
blocked: the shim design and how divergences are documented. Default: allowed as a patch file
under dv/auto_dv/tools/ with each hunk justified and applied by the build script; never a fork,
never a fetch of any Ibex-specific Spike; the shim remains the first choice.

Bug candidate added from rtl-arch: B14 (BUG-04): rvfi_id_done suppresses the ID-stage trap record
when a WB load/store error coincides (rtl/ibex_core.sv:1851-1853; rtl/ibex_controller.sv:336-337),
so the RVFI stream may lack a trapped instruction. RVFI-only; affects the comparator; unverified
in simulation. rtl-arch's A.1 does not list B1 (dret leaves MPRV set); asked to verify
(gen_t003_acceptance.md follow-up 1).

Status: pending. Default stated above applied meanwhile (DV_prompt.txt Section 10).

## LOG-004 - 2026-09-03 - NOTE (wrapper representation decisions)

The DV Lead recorded TB Infra's Q-1 (expose integrity bits as separate *_intg wrapper ports) and
Q-2 (no clock gate in the wrapper) as wiring choices decided by the DV Lead, not owner questions.
The pre-execution cross-model review of the T-005 plan
(dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_scoping_notes.md, finding 1, medium) requires
the opposite on Q-1: the wrapper exposes instr_rdata_i, data_rdata_i and data_wdata_o exactly as
ibex_core declares them (MemDataWidth-wide, integrity in bits [38:32]); the split happens in the
TB bus interface (test equipment). The Orchestrator applied the review finding in the T-005
assignment; the wrapper therefore stays literal to the DV_prompt.txt Section 2 ruling. Q-2 (no
clock gate) stands as decided. If the owner wants the split at the DUT boundary, answer here.

## Q-012 - 2026-09-03 - QUESTION (to owner; site/infra finding worded by the Runtime Manager, filed by the Orchestrator; the DV Lead may amend the wording)

The clone lives on `/localdev`, a local NVMe of the submit host (soc-l-11). LSF compute hosts
cannot see it (LSF job 10930291 failed for that reason; evidence in
`dv/auto_dv/evidence/gen_t010_compile_path.md` Section 1). `docs/dv/SIM_RECIPE.md` Section 7
requires shared storage. Workaround now built into the flow: out-trees live under
`/proj_soc/user_dev/fzhang/ibex_dv_out` (pointer `dv/auto_dv/work/runtime/gen_site.yaml`,
override `GEN_DV_OUT_ROOT`), the compile runs on the submit host, and the LSF job is a pure-bash
script sourcing a copy of `ci/env.sh` staged in the build outdir. Consequence: cocotb runs on
LSF are blocked until the clone (its `.venv` VPI library and the Python test modules) is on
shared storage; pure-SV runs are unaffected; cocotb builds compile and run with `--local`.
Options: (a) move or mirror the clone to shared storage (Runtime Manager's recommendation);
(b) accept SV-only regressions on LSF plus local cocotb runs. Default applied while pending: the
team builds a shared-storage mirror (rsync of the clone without .git and out-trees, plus a venv
created on shared storage from ci/requirements.lock) that LSF jobs use, so option (a) is met
without moving the owner's working clone. Status: pending.

## Q-013 - 2026-09-03 - QUESTION (to owner; landing-rule mechanics, worded by the Orchestrator)

Tool-mandated filenames versus the `gen_` prefix rule. The riscv-dv generator requires fixed
names inside a target directory (`riscv_core_setting.sv`, `testlist.yaml`,
`user_extension/user_define.h`, `user_extension/user_extension.svh`, `user_extension/user_init.s`;
included by name from the vendored generator sources). The T-023 commit placed them under
`dv/auto_dv/stim/gen_riscv_dv_target/` without the prefix; the post-execution review
(`dv/auto_dv/reviews/2026-09-03-claude-diff-0b9c93c7-0b8d60b4.md`, major finding 3) flags that
FENCE.md's landing rule exempts only `.gitignore` and `contract/**`. Question: does the landing
check accept tool-mandated fixed filenames inside a `gen_`-prefixed directory? Default applied
while pending: the committed sources are renamed with the `gen_` prefix and the program driver
materializes the fixed-name target directory out-of-tree at flow time, so the tree passes the
strict reading either way. Status: pending.
