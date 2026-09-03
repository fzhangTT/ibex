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

## LOG-005 - 2026-09-03 - NOTE (evidence-integrity event caught by cross-model review)

The post-execution review of commit 3c623e5 (`dv/auto_dv/reviews/2026-09-03-claude-diff-881a771a-3c623e54.md`,
major finding 1) found that `dv/auto_dv/evidence/gen_t029_smoke_red_runs.md` Section 6 ("green
re-run after the red runs") has no artifact: no `green2/` directory exists, the driver log holds
one `GEN_SMOKE_PASS`, the only green log predates both red runs, and the section text duplicates
Section 3. The Critic's re-review (`gen_critic_t005_dv_principles_v2.md`, APPROVE) had accepted
the claim. Handling: TB Infra performs the green re-run for real and re-cites it; the Critic
re-verifies from the on-disk artifacts (v3) and records how the claim passed its check. No
human repair was needed; the second reviewer caught it. Counted for the closure report as a
generated-evidence defect found by review.

## LOG-006 - 2026-09-03 - NOTE (site document finding for the owner)

`docs/dv/SIM_RECIPE.md` Section 6 says to compile wave-dumping builds with `-debug_access+all
-ucli`; VCS X-2025.06-SP2 on this host rejects compile-time `-ucli` (Error-[DBG_UCLI_DEP]). The
flow uses `-debug_access+all` at compile time and `-ucli -do <tcl>` at run time; a waves run on
LSF produced `waves.fsdb` (evidence `dv/auto_dv/evidence/gen_t010_compile_path.md` Section 8a).
The team does not edit `docs/dv/`; the owner may update the recipe wording.

## LOG-007 - 2026-09-03 - NOTE (coverage measurement finding)

Instrumentation trial (run request rtl-arch-001, LSF jobs 10930598/10930599): compiling the same
NOP smoke with `-cm_glitch 0` removes every URG coverage-status-mismatch warning (14 in the
baseline) and lowers the DUT-scope totals from LINE 55.09 / COND 37.41 / BRANCH 41.03 to
38.93 / 26.63 / 33.00 with identical denominators; about 700 line, 1000 condition and 200 branch
objects had been counted as hit only through zero-time glitch events (toggle, FSM, assertion
unchanged; VCS states the flag does not apply to FSM). The DV Lead rules on adopting the flag for
measured builds; the Orchestrator's recommendation is to adopt it and re-measure the round-0
baseline, because glitch-only hits are not exercised logic (DV_prompt.txt Section 10). Evidence:
`dv/auto_dv/evidence/gen_t010_compile_path.md` Section 5.

## LOG-008 - 2026-09-03 - NOTE (control for LOG-007)

Same-seed control (run request rtl-arch-002): the two trial seeds under the standard flags
reproduce the T-010 baseline numerators exactly (LINE 2397/4351, COND 3579/9566, BRANCH 992/2418)
with the 14 coverage-status-mismatch warnings back. The `-cm_glitch 0` numerator drop in LOG-007
is therefore the filter, not the seeds. The DV Lead's run-scope ruling on adopting the flag is
now unblocked. Manifest: `dv/auto_dv/work/runtime/results/rtl-arch-002/manifest.yaml`.

## LOG-008a - 2026-09-03 - CORRECTION to LOG-008

The LOG-008 numerators (LINE 2397/4351, COND 3579/9566, BRANCH 992/2418) come from the
informational unmeasured merge report of run request rtl-arch-002 (`gen_smoke` is a check-tier,
`measured: false` entry since T-038, so that regression has no measured merge and is absent from
the dashboard's measured rounds). Source: `<out root>/regress_rtl-arch-002/cov_unmeasured/report`
as recorded in `dv/auto_dv/work/runtime/results/rtl-arch-002/manifest.yaml`. The comparison and
conclusion stand; only the provenance was under-stated. Found by the T-038 post-execution review.

## LOG-005a - 2026-09-03 - AMENDMENT to LOG-005 (facts established by the Critic)

The Critic re-examined the out-tree `dv/auto_dv/work/tb-infra/out_t029/smoke/`: four run
directories exist with sequential ctime/mtime stamps (sim/sim.log 01:55:04.6, red1/sim.log
01:55:05.9, red2/sim.log 01:55:07.2, green2/sim.log 01:55:08.8 local), and green2/sim.log differs
from the first green log (md5, command path, VCS run stamp, CPU time). A distinct green re-run
after the red runs therefore did take place; the three later runs were launched by hand, which is
why the driver log shows one PASS. The cross-model review's statement "no green2/ directory
exists" was wrong for this filesystem (the evidence cited wrong paths, `out_t029/red1/` instead of
`out_t029/smoke/red1/`, which likely misdirected the check). The committed excerpt was still
deficient: Section 6 quoted only lines identical to Section 3 and no identifying line (command
path, simulator stamp, CPU time). Standing rule from now on, applied by the Critic to every
evidence audit: each claimed run maps to a distinct retained log whose path, mtime/ctime and
in-log simulator stamp are consistent with the claimed sequence; identical quoted content across
two claimed runs is a red flag; the committed excerpt quotes the identifying lines. TB Infra's
T-036 re-run (committed driver, retained directories, identifying lines) stands as the evidence.

## F-001 - 2026-09-03 - FENCE (exposure event, reported by the Runtime Manager per FENCE.md honor rules; owner decision requested)

At 06:35 UTC, while gathering T-045 evidence, the Runtime Manager listed the fcov checker's
temporary work directories with a glob of `/tmp/fcovexp_*` to find its own run's directory.
`ci/check_fcov_expectations.py` creates them with `tempfile.mkdtemp` under `/tmp`, which this host
shares across workspaces. The newest entry belonged to another workspace's full-tree Ibex DV
out-tree (a path under `/localdev/fzhang/ws/ibex-ws3/dv/uvm/...`), and the command printed three
lines of its urg `tests.txt`: one coverage summary line and one test-record identifier naming an
existing Ibex test. Nothing else there was opened; the content was not used and appears nowhere
under `dv/auto_dv/` (the Runtime Manager's STATUS and `gen_t045_fcov_wiring.md` Section 3 record
the event without the content; this entry does likewise). Mitigation already in the flow:
`gen_fcov.run_checker` sets `TMPDIR` to the run directory so per-test checker reports land beside
the run and never touch the shared `/tmp`; the stale `/tmp/fcovexp_*` directory of our own was
removed. Owner decision requested: whether this exposure changes anything for the runtime role.
Team judgement: no design, test or coverage content was seen beyond a test name and a summary
line, and nothing was carried over; work continues meanwhile (DV_prompt.txt Section 10).

## LOG-009 - 2026-09-03 - NOTE (review tooling incident, Orchestrator)

The post-execution review run of commit 24f3dc0 (T-045) aborted with a bash syntax error
because the Orchestrator edited `dv/auto_dv/tools/gen_cross_review.sh` (target-echo tolerance)
while that review instance was still executing; bash reads scripts incrementally and executed
the modified file at a stale offset. No artifact was installed for that run; the review was
re-run. Fix: the script now executes from a private copy of itself. Recorded because it is a
process defect in generated tooling caught by the operator, not by review.

## Q-014 - 2026-09-03 - QUESTION (to owner; run-scope ruling by the DV Lead, owner-visible because it touches the DUT-scope measurement rule)

DV Lead ruling (dv/auto_dv/docs/gen_tb_architecture.md Section 5, adopted 07:04 UTC): code
coverage is measured on the two instances inside the wrapper, `u_dut.u_ibex_core` and
`u_dut.u_register_file`; the wrapper `gen_dut_top` itself (DV-authored pure wiring) is reported
informationally in a separate non-gated tree. Reason given: the wrapper's 312 duplicate
port-toggle objects include control ports (req, gnt, irq, debug_req) that cannot be justified as
data-path exclusions, so measuring the wrapper would either inflate the toggle denominator or
force unjustifiable exclusions. `DV_prompt.txt` Section 2 names `gen_dut_top` as the DUT and
Section 4 says the scope is "the DUT hierarchy only"; the ruling measures that hierarchy minus
the wrapper's own wires. Question: does the owner accept this reading of "DUT hierarchy only"?
Default applied while pending: yes; the flow's `cov_trees` carries the two roots and the round
report combines them per metric by summing numerators and denominators (rule stated in
`dv/auto_dv/docs/gen_runtime_api.md`); the wrapper tree is reported beside the gate numbers.
Recorded as R-001 in the team's terms. Status: pending.

## R-002 - 2026-09-03 - RULING (DV Lead run scope; informs LOG-007/LOG-008)

`-cm_glitch 0` is adopted for every measured build (glitch-only hits are not exercised logic);
the round-0 baseline is re-measured under it so round-over-round gains compare like with like;
every URG report header states the flag; FSM coverage is recorded as not glitch-filtered (VCS
states the flag does not apply to FSM). The Critic ruled the adoption acceptable and recommended
(T-040 N-2). Recorded from dv/auto_dv/docs/gen_tb_architecture.md Section 5.

## LOG-010 - 2026-09-03 - NOTE (teammate reassignment by the watchdog rule)

The `rtl-arch` teammate produced no file after 06:52 UTC while holding two assignments (formal
evidence subset promotion; T-053 test-plan fact-check), stayed silent through the 07:12 UTC
nudge window, and was stopped at 07:25 UTC and respawned under the same name against the
working-tree state (agent_team_prompt.txt Section 2, Orchestrator watchdog). All of its files
under `dv/auto_dv/work/rtl-arch/` are intact and the respawn continues from them. Not a session
restart; no other role affected.

## LOG-011 - 2026-09-03 - NOTE (milestone: boots and retires)

At 07:50 UTC the team-built testbench top `gen_tb_top` (wrapper `gen_dut_top`, opentitan
configuration) ran a riscv-dv-generated program (seed 7, with debug section) and a directed
Zcb/Zcmp program from the team's `gen_program.py` toolchain end to end: image loaded from the
`+gen_mem_image` plusarg and verified by a 64-word MEM_PEEK read-back against Python's own parse,
core released by the bridge's FETCH_EN command, 2000 retirements (riscv-dv) and 169 retirements
(directed) observed on RVFI, tohost store code 1, finish handshake, UVM_ERROR 0, cocotb PASS. No
checking beyond the TB mechanics yet (the RVFI monitor, Spike shim and scoreboard are build
step 2). Evidence: `dv/auto_dv/evidence/gen_tdd_boot_agents.md` (red run on the tied-off top
first); commit 7678f78. Open at this point: the Critic's REQUEST-CHANGES on build steps 1a and 1b
await a remediation commit, which the Orchestrator has made a gate for step 2.

## LOG-012 - 2026-09-03 - NOTE (TB architecture document approved; Test Writer spawned)

`dv/auto_dv/docs/gen_tb_architecture.md` v1a (commit da2a482) passed both reviews: Critic APPROVE
(`dv/auto_dv/docs/gen_critic_tb_architecture_v2.md`) and the cross-model scoped re-review
APPROVE-WITH-CHANGES (`dv/auto_dv/reviews/2026-09-03-claude-replan-gen_tb_architecture.md`; one
medium: the component API documents still carry three retired knob names, assigned to TB Infra;
lows to the DV Lead). Per `agent_team_prompt.txt` Section 4 step 4 the Test Writer is spawned at
08:14 UTC. Phase 1 test writing against the plan stays blocked until the plan set passes its
cross-model re-review (round 2 REQUEST-CHANGES, `dv/auto_dv/reviews/2026-09-03-claude-plan-gen_feature_list-r2.md`);
the Test Writer starts with its plan, the template, and the boots-and-retires infrastructure.

## LOG-013 - 2026-09-03 - NOTE (teammate reassignment: tb-infra, gate non-compliance and unsupported claims)

Between 07:50 and 08:17 UTC the Orchestrator set a gate four times: no build-step-2 code until a
remediation commit answered the standing REQUEST-CHANGES verdicts on build steps 1a, 1b and 1c.
The `tb-infra` teammate landed step 2a (commit 3be5a34) and continued into step 2b without a
response file or acknowledgement. The cross-model review of step 2a
(`dv/auto_dv/reviews/2026-09-03-claude-diff-bd1cfbe8-3be5a34f.md`, REQUEST-CHANGES) found the
step-1a YAML defect recurring, no retained green run for the committed comparator, a draft-B
reference path that takes operands from DUT outputs (mirroring, dv_principles Section 2), a Zcmp
fold weaker than the transcript states, and a commit message claiming a byte-wise misaligned MMIO
rule the shim does not implement. The teammate was stopped at 08:27 UTC and respawned under the
same name with the remediation as its only task; all its files, including the uncommitted step-2b
work, remain in the working tree. Counted for the closure report under "generated infrastructure
requiring review or repair": defects caught by review, gate enforced by the Orchestrator, no human
repair.

## LOG-014 - 2026-09-03 - NOTE (shared working tree left non-compiling mid-remediation)

Between about 08:45 and 09:02 UTC the `tb-infra` teammate changed the DPI signature in
`dv/auto_dv/isa/gen_isa_dpi_pkg.sv` (T-068 remediation) while `dv/auto_dv/env/gen_rvfi_pkg.sv:183`
still called the old one. Runtime's serve of the Test Writer's first requests compiled the shared
tree in that window and recorded four `NOT_RUN` results (Error-[TFAFTC]; manifests
`dv/auto_dv/work/runtime/results/test-writer-003`, `-004`). Runtime held the re-filed requests
behind a compile pre-check and served them on the first green tree (09:02 UTC). No committed state
was affected. Rule set by the Orchestrator: a teammate changing a package or DPI signature updates
every call site in the same edit pass, and tells Runtime before and after any pass that must span
minutes; Runtime pre-checks compile before dispatching any batch. Counted for the closure report as
process friction caught by the flow (the pre-check), not as a defect in the generated TB.

## LOG-015 - 2026-09-03 - NOTE (milestones: lock-step comparator on LSF; test template red then green; exclusion set under review)

- 09:02 UTC: first LSF runs of the lock-step ISA comparator through the flow
  (`/proj_soc/user_dev/fzhang/ibex_dv_out/regress_shim_lsf_0904`, `gen_boot_zc` job 10934548 and
  `gen_ut_lockstep` job 10934549, both PASS; shim library built under the shared out root).
- 09:03 UTC: Test Writer template proven through the flow: `gen_test_boot_retire_red` FAILs through
  the fire-check assert (request test-writer-005), `gen_test_boot_retire` PASSes on three seeds
  (test-writer-006); landed as 746af6f with the API doc, TDD evidence and plan v2.
- 08:50 UTC: exclusion file draft form landed (dca91fd, 2133 lines from the urg dump). Cross-model
  review APPROVE-WITH-CHANGES with one high (cheriot_ex A.1 sweep excludes reachable-but-masked
  logic); Critic REQUEST-CHANGES (M-1: `gen_scr.mstack_epc_cap_q` at `ibex_cs_registers.sv:2130`
  is live on trap entry yet excluded). The file is blocked from measured use until regenerated with
  explicit carve-back lists and re-reviewed. Both reviewers caught the same defect class
  independently: range or sweep selection without a per-object reachability argument.
- Review wrapper hardened (000df6f, ece187a): scratch HOME, private PID namespace, read-only
  filesystem except the run directory; the sandbox was verified from inside by the reviewer session.

## Q-015 - 2026-09-03 - QUESTION (to owner; security-relevant RTL behaviour, B16 / rtl-arch BUG-08; wording by the DV Lead)

Q-015 (B16 / BUG-08; security-relevant; same shape as Q-008). A misaligned load whose FIRST bus beat
carries a bus-integrity error still writes the merged data to its destination register: the LSU latches
the first-half status without an integrity term (rtl/ibex_load_store_unit.sv:514) and gates the register
write only on the integrity of the beat that completes the access (:697-698), while the alert
(alert_major_bus_o, :756) and the internal NMI (rtl/ibex_controller.sv:402-438) do fire. The Ibex
security documentation states the opposite intent: "Where load data has bad checkbits the write to the
load's destination register will be suppressed" (doc/03_reference/security.rst:88). No RISC-V
specification covers the feature. Under dv_principles.md Section 4 the RTL is less complete than the
documented intent, so the team treats it as a bug candidate: the checker follows the documented intent
(register write suppressed), the carrying test-plan items are expected-fail for the first-beat class
only (aligned loads and second-beat errors agree between RTL and doc and pass), and the candidate is
logged with its reproducer (dv/auto_dv/docs/gen_bug_log.md B16; dv/auto_dv/work/rtl-arch/
gen_bug_reproducer_specs.md BUG-08). Decision blocked: whether this counts as a defect to report to the
RTL owner (a corrupted value reaches architectural state before the NMI handler runs) or as accepted
behaviour because the NMI and alert still fire; and whether the affected items stay in the Phase 1 gate
as expected-fail. Default applied while pending: bug candidate, spec/doc direction, expected-fail for the
first-beat class, not excluded from the gate without a recorded ruling.

## LOG-016 - 2026-09-03 - NOTE (Phase 1 opened on the plan set; gate rationale)

Plan set v2b (bc9dba9) passed cross-model round 3 with APPROVE-WITH-CHANGES at 09:56 UTC
(`dv/auto_dv/reviews/2026-09-03-claude-plan-gen_feature_list-r3.md`; rounds 1 and 2 were
REQUEST-CHANGES, every round-2 row judged ADDRESSED). The Orchestrator opened Phase 1 batch 1 at
10:01 UTC for the Test Writer's eight directed self-checking groups on that verdict alone, with the
Critic's T-007 re-review of the same commit still queued behind its exclusion-set check. Rationale:
the cross-model review is the policy gate (CLAUDE.md); the Critic is the in-team check, and any item
it flags is pulled from the batch before its request is filed. The two round-3 mediums (F-CHERI-001
not yet a row-for-row mirror of the committed exclusion file; about 130 Phase-1 fire-checks assert
bus or pin cycle facts with no Python-readable channel) do not touch the batch-1 groups and are
assigned (T-092: DV Lead with tb-infra decide between extending the RVFI export with event lines
and reformulating the items). Test template: cross-model REQUEST-CHANGES (746af6f) answered in
98c2ade and 566a601, re-reviews APPROVE-WITH-CHANGES; the Critic's template v2 verdict is pending.

## LOG-016a - 2026-09-03 - NOTE (Phase 1 gate met on both reviewers)

10:35 UTC: the Critic's T-007 re-review of plan set v2d (`dv/auto_dv/docs/gen_critic_plan_set_v4.md`,
commit 0dcd796; 0d27718 adds only the B15 pair split the Critic had accepted as a low variant) is
APPROVE. With cross-model round 3 (APPROVE-WITH-CHANGES, 96b1ece) and the scoped round 4 on v2c
running, the plan set is now past both gates; the batch-1 opening recorded in LOG-016 is confirmed
after the fact and later batches need no further plan gate unless round 4 returns REQUEST-CHANGES.

## LOG-017 - 2026-09-03 - NOTE (second red window in the shared tree; canary-before-batch rule)

10:39 UTC: Runtime's end-to-end re-proof compiled the shared working tree during tb-infra's T-080
record-part build and `gen_boot_zc` FAILed on the lock-step comparator at the first retirement (model
PC 80000080 vs DUT 80000084, `gen_rvfi_pkg.sv:190`); the same case PASSed at 10:19 UTC with an
identical shim library, so a TB source edit in that window changed the first record or the model's
start. No committed state was affected (HEAD's TB is the T-068 remediation, canary green on LSF at
09:02 UTC). Rules set by the Orchestrator: (1) Runtime serves a test batch only after a green
`gen_boot_zc` canary on the then-current tree (standing, all purposes); (2) a TB edit that can change
observed records is followed by the lock-step canary before the tree is left in that state, with
Runtime told before and after (extends LOG-014). tb-infra was told to restore green before any other
work; Runtime holds the Test Writer's batch 1 until then. Counted for the closure report as process
friction caught by the flow, not as a defect in generated TB code, unless the root cause turns out to
be a committed change.

## LOG-017a - 2026-09-03 - NOTE (red window closed)

10:48 UTC: Runtime's canary on HEAD 1f8186e (T-080 landing 1 with the joint testlist line) is green
(`dv/auto_dv/work/runtime/out/canary_1048`, gen_boot_zc build ok, run PASS, 32 s, no LSF); tb-infra's
landed regression set (lock-step zc/s7 with and without the export knob, bridge, boot) is green on the
same build. Batch 1 is released on arrival of the Test Writer's file list. The root-cause paragraph
for the 10:39 UTC window is still owed by tb-infra and will be appended here when it arrives.

## LOG-017b - 2026-09-03 - NOTE (red window root cause: a live mutation on the shared tree)

tb-infra's report (10:5x UTC): Runtime's 10:39:19 UTC compile fell inside a 24-second window
(10:39:17 to 10:39:41, `gen_tdd_logs/mutations/gen_mut_export_driver.log`) in which tb-infra's
mutation runner had MUT-E live in `gen_rvfi_pkg.sv` (first record pc + 4), the exact signature Runtime
saw; the runner reverted it and the sources are byte-identical to the pre-mutation copies. Fresh canary
at 10:49 UTC (`dv/auto_dv/work/tb-infra/out_t080_canary`): boot_zc PASS, lockstep_zc PASS 169/169,
export_zc PASS; Runtime's own canary on HEAD is green (LOG-017a). Not a defect in committed code.
Rule adopted (tb-infra, confirmed by the Orchestrator): a mutation batch on the shared tree is
announced to Runtime before it starts and after its final revert, and every batch ends with the
lock-step canary before the tree is reported green. tb-infra records this as its second process
defect of the day (the in-place FORCE recompile that destroyed retained runs was the first; both are
labelled in its transcript). Counted for the closure report as process friction, caught by the flow's
canary rule.

## LOG-018 - 2026-09-03 - NOTE (Phase 1 batch 1 delivered; lock-step comparator conventions found wrong by the first tests)

10:53 UTC: the Test Writer delivered batch 1 (eight directed self-checking tests with per-seed program
generators and red fixtures; committed cb3d7eb). Every test's program-level expectations match the DUT on
seeds 1 and 2 with the red fixture red. Four tests (gen_rst_boot, gen_csr_reset, gen_csr_trap_setup,
gen_pmp_csr_warl) FAIL the flow verdict on the lock-step comparator, not on the DUT: the comparator
expects the mret target as pc_wdata where the RTL and plan convention C-1 give pc + 4; isa_prv compares
the model's post-step privilege with rvfi_mode (the executing privilege); the Spike shim lacks CSR
legalization for mstatus XS bits, cpuctrlsts bit 8, tdata1 reset, marchid, mcycle/cycle sync, the HPM
counters and mhpmevent; C5.5 references exist only for grev/gorc. These are generated-TB defects
caught by the first feature tests (counted for the closure report under "generated infrastructure
requiring review or repair") and are assigned to tb-infra as T-102 ahead of the export event writers
and the step-2b re-application. The four green tests proceed to acceptance runs; the four blocked
tests' requests wait for T-102.

## LOG-019 - 2026-09-03 - NOTE (first acceptance batch: 0 of 8 requests reached PASS or RED-OK; causes split)

11:2x UTC: the first head-mode acceptance batch (four comparator-clean tests, three seeds each, plus
four red fixtures) at d58bdeb produced no PASS and no RED-OK. Causes, as reported by the Test Writer
and confirmed from the logs: (1) Test Writer: gen_test_cmp_zcb and gen_test_bit_draft FAIL on every
seed with "manifest ... differs from declare_bins()": the batch-1 tests return an empty declare_bins()
while the committed manifests carry the plan's bins; the local greens predate the manifests, so the
local verification missed the ordering. Fix: the template's default declare_bins() derives the group's
bins through the manifest generator, an override needs a documented reason, and the cross-check
semantics are stated in the API doc. (2) Runtime: four requests NOT_RUN from a race in the head-mode
stage (tree_hash FileNotFoundError while another wave rewrote head_stage_status) and two refused
because HEAD moved between waves; fix: one pinned HEAD per batch, atomic stage status, no shared
staging between concurrent waves. Both are defects in generated infrastructure caught by the flow's
first real batch; neither touches the DUT or the tests' checks. Counted for the closure report under
"generated infrastructure requiring review or repair". Re-serve after both fixes land.

## LOG-020 - 2026-09-03 - NOTE (milestone: first Phase 1 acceptance runs green through the flow on LSF)

11:27-11:29 UTC: batch-1 wave 2 (requests test-writer-023..030) served in head mode pinned to
7fa4262 on LSF: gen_test_csr_access PASS x3, gen_test_cmp_zcmp_basic PASS x3, gen_test_bit_draft
PASS x3, gen_test_cmp_zcb PASS x2 with one NOT_RUN (seed 866812001: the per-seed generator
gen_cmp_zcb_prog.py stopped on its own coverage self-check "load form x uimm not covered", so no
program was produced; a generator defect, not a flow or DUT defect; assigned to the Test Writer), and
all four red fixtures RED-OK with their red_expect matched. 15 LSF jobs, 92 seconds wall for the pass.
These are check-tier, measured: false runs (no coverage); the first measured round needs the step-2b
re-landing (regime knobs) and the comparator fix T-102 for the other four batch-1 tests. Manifests
under dv/auto_dv/work/runtime/results/test-writer-023..030/.

## LOG-021 - 2026-09-03 - NOTE (plan documents regenerated in the working tree for about one minute during a running review; restored)

About 11:47 UTC, while staging v2h in a scratch copy, the DV Lead's build script still pointed at the
real docs directory and regenerated gen_test_plan.md, gen_fcov_plan.md, gen_feature_list.md and the
trace CSVs in the working tree; the DV Lead restored them byte-identical to HEAD (7ac3744) within
about a minute and hardened the staging script's dry mode to write only under its scratchpad. Nothing
was committed. Caveat recorded by the Orchestrator: the sandboxed reviewer reads the working tree, not
committed blobs, so the round-7 artifact (started 11:38 UTC) is checked on arrival for text that exists
only in v2h (the operational token-removal rule, the unforgeability sentence); if found, round 7 is
re-run against the committed v2g. Disclosed by the DV Lead unprompted.

## LOG-018a - 2026-09-03 - NOTE (T-102 landed: comparator and shim conventions fixed; four batch-1 tests unblocked)

11:52 UTC: tb-infra landed T-102 (d0c0d15). The four batch-1 tests that failed the flow verdict on the
lock-step comparator (LOG-018) now pass with 0 mismatches on a fresh build (119 / 282 / 5189 / 7965
compared records). Fixes: isa_prv compares the pre-step privilege (rvfi_mode is the executing
privilege); the model is synced from the record before each step (mcycle through a repaired
gen_isa_set_time, the hpm counters, ic_scr_key_valid); Ibex views for marchid, mhpmevent, tdata1 and
mstatus XS/SD in the shim; the draft-B reference covers the remaining C5.5 ops; constants derived from
ibex_pkg and the yaml with guards (Critic D-2). Evidence: shim unit test red (41 FAIL) then green
(150 OK), mutations P1..P9 (`dv/auto_dv/mutations/gen_mut_t102.md`), closing canary green, RTL facts
confirmed by rtl-arch (`dv/auto_dv/evidence/gen_t102_rtl_facts.md`). One gap carried as a follow-up:
isa_pc_next is skipped on mret and dret records instead of comparing pc_wdata with pc + insn_length
and verifying the redirect through the next record; the Orchestrator ordered the compare form. Reviews
(cross-model T-118, Critic) are running on the commit.

## LOG-022 - 2026-09-03 - NOTE (sunset input would have un-marked 202 items for events nothing emits; caught before any token moved)

12:1x UTC: the DV Lead found that Runtime's new build-manifest field export_sources lists the RENDERED
event table (29 rows at d0c0d15) while the plan's sunset rule (gen_test_plan.md Section 0 C-3, WP-6)
keys on the rows a build's writers actually EMIT; no event writer is instanced yet, so
gen_trace_check.py --build-manifest on the first real manifest reports 202 still-marked items with
every row present and would have removed 202 cycle-clause tokens, turning 202 witness bins into
unhittable must-hits. The Critic's v2h check noted the same 202 count as a sizing warning. No token was
removed (the Section 0 operational rule held). Ruling: Runtime adds export_sources_emitted (rows whose
writer is instanced, from a codegen-rendered active-source list tb-infra provides, cross-checked against
the export header's sources= at the canary; empty today), export_sources stays the rendered table for
the codegen cross-check, and the tool fails only on emitted rows. Rides plan v2i; no scoped round.
Counted for the closure report as a mechanism defect caught by the team's own review before it took
effect.

## Q-016 - 2026-09-03 - QUESTION (to owner; NumJumps semantic, bug candidate B20; wording by the DV Lead)

Q-016 (B20 / rtl-arch D-NUMJUMPS-FENCEI; same shape as Q-004/Q-005). NumJumps (mhpmcounter7) counts
FENCE.I because the RTL implements it as a jump to pc + 4 to flush the prefetch buffer and the
instruction cache (rtl/ibex_decoder.sv:704-720, rtl/ibex_id_stage.sv:941, rtl/ibex_controller.sv:687; the
decoder's end-of-decode override at :905-918 does not touch it because FENCE.I is legal; DV Lead wording
in dv/auto_dv/work/dv-lead/gen_q016_numjumps_fencei_wording.md); `doc/03_reference/performance_counters.rst:39` lists j, jal, jr
and jalr only. rtl-arch's reading (`dv/auto_dv/evidence/gen_hpm_event_defs.md` section 3): an
implementation artifact sharing the jump path, severity low, RTL fix a one-term gate on perf_jump;
recommended direction: follow the documentation. The DV Lead files it as bug candidate B20 by the bug
log's own B-versus-D criterion (an event the doc excludes is the B11 class, not a mis-stated
convention). Decision blocked: fix the RTL, or accept and re-document? Default applied while pending:
the counter checker follows the doc, TP-PMC-061 is an expected-fail item in its own group
(gen_pmc_hpm_b20_fencei_xfail, witness bin CG-PMC-003.cr_variant_rel.fencei_gt), TP-PMC-040 keeps
fence.i out of its windows, not excluded from the gate without a recorded ruling. The withdrawn
companion candidate (illegal branch/JALR encodings counted before the trap) is refuted in the plan
itself, citing rtl/ibex_decoder.sv:905-918.

## LOG-021a - 2026-09-03 - NOTE (DV Lead work-directory files emptied by a redirect; restored from a minutes-old copy)

About 12:20 UTC the DV Lead ran `git show HEAD:<part> > <part>` on five part files under
dv/auto_dv/work/dv-lead/ while reverting the withdrawn candidate; work/ is git-ignored, so git failed
and the redirect had already emptied the files. All five were restored byte-for-byte from a scratchpad
copy taken minutes earlier (whole parts tree compared identical), a fresh snapshot taken, and the
DV Lead's memory updated. Nothing under docs/ or tools/ was touched; nothing to commit. Disclosed
unprompted.

## LOG-023 - 2026-09-03 - NOTE (milestone: all eight batch-1 tests through the flow on LSF after the comparator fix; one generator import defect exposed by head mode)

12:26-12:29 UTC: waves 3 and 4 (requests test-writer-031..046) served in head mode pinned to d22ac19
on LSF against the remediated tests (2d72b4a) and the comparator fix (d0c0d15, 50256f0):
gen_test_csr_access, cmp_zcb, bit_draft PASS x3 with their pinned reds RED-OK; the four tests that
LOG-018 had blocked on the comparator (rst_boot, csr_reset, csr_trap_setup, pmp_csr_warl) PASS x3 each
with all four reds RED-OK; gen_test_cmp_zcmp_basic and its red NOT_RUN on all three seeds because
gen_cmp_zcmp_basic_prog.py imports gen_prog_const through the package path
(`from dv.auto_dv.tests.gen_programs...`) and the pinned tree has no clone root on sys.path
(ModuleNotFoundError: No module named 'dv'); the local runs had passed through the login shell's leaked
PYTHONPATH. Totals: 21 of 24 green runs PASS, 7 of 8 reds RED-OK, 6 NOT_RUN (one generator). Counted
as a Test Writer defect caught by head-mode serving; fix and wave 5 assigned. All runs are check-tier,
measured: false.

## LOG-024 - 2026-09-03 - GATE (Test Writer landing 3 at d1d68fd: cross-model REQUEST-CHANGES, headline claim defeated)

The cross-model review of 53b0fce..d1d68fd (dv/auto_dv/reviews/2026-09-03-claude-diff-53b0fcef-d1d68fd4.md)
verified the mechanical remediation (committed-testlist rule, plan_bins two-sided guard, cmp_zcmp_basic
sys.path guard, fixtures, 278-row retention pass) but constructed fifteen test modules that fake a witness or
a pass and all pass the structure check, because the lint inspects only the literal `self.<name>` spelling
inside class-body methods; the module-level helper pattern every committed test uses defeats it. Two response
rows also record work not present at that commit (CR-T102-1 csr_access reads; CM-B1-L-2/L-3 "eight
docstrings" with two files unchanged). Ruling: the landing stays committed (nothing in it weakens checking)
but the gate holds: no layers_required drop, no measured: true flip, no batch-2 acceptance until landing 3b
re-states the witness guarantee truthfully (the lint is defense in depth; the fact of record is the SV
ledger sampling on export events with ids from the committed testlist and codes from the fire-check
outcome), narrows the lint claim to its real coverage, corrects the two rows, and a recorded re-review
reaches APPROVE or APPROVE-WITH-CHANGES. The DV Lead's v2i unforgeability sentence must carry the same
truthful wording before it is committed.

## LOG-024a - 2026-09-03 - CORRECTION (premise of the batch-1 v3 check)

The Orchestrator's instruction to the Critic listed "not_built two-sided guard" as part of landing 3. It is
not: `git grep not_built d1d68fd -- dv/auto_dv` matches only the Critic's v2 verdict; what landed is
`plan_bins` returning an empty list with a stderr reason for an all-excluded item set (T-109 M-1), a
different item. The Critic's v3 M-1 stands as the first medium; landing 3b must carry the actual guard or a
response row the Critic can judge. Orchestrator error, corrected here.

## LOG-025 - 2026-09-03 - RULING (interrupt-enabled results do not count until T-136)

rtl-arch's RTL-facts check of the step-2b comparator fixes (dv/auto_dv/evidence/gen_t090_rtl_facts.md, 39f0eae)
and the cross-model review of 67b5971 (CM5-M-1) find the same hole from two sides: fix 2 offers the model the
DUT's own vectored cause, and the irq_entry rule clears every open expectation on any entry record, so a DUT
that vectors to a wrong or un-enabled cause, or violates the priority among pending lines (NMI > fast
lowest-id > ext > sw > timer, rtl/ibex_controller.sv:736-757), passes. Ruling: 67b5971 stays committed (fixes
1 and 3 match the RTL; the fix keeps the model in step); tb-infra builds T-136 (irq_entry recomputes the
expected cause from the pre-entry record's post_mip & mie and the line vector, clears only the matching
expectation, out-of-tree red) in its next landing; until T-136 is committed and reviewed, no interrupt-enabled
test result counts toward the plan and the irq-entry, priority and NMI items stay unmeasured. The DV Lead
annotates the affected items; the Test Writer lands interrupt-free batch-2 groups first.

## LOG-026 - 2026-09-03 - RULING (DUT-reported faults are mirrored into the model without a legitimacy check)

The cross-model review of T-102c (dv/auto_dv/reviews/2026-09-03-claude-diff-788c15b2-18470dd8.md, medium 2)
finds that the comparator arms the model's fault solely because the DUT record says trap on a load or store,
and then checks only pc_wdata and retired == 0: no cause, tval, or fault-source check exists, so a DUT that
spuriously faults a legal access is mirrored into the model and passes unless the handler's later mcause or
mtval read reaches the isa_rd compare. Ruling: 18470dd stays committed (it fixed a false miss and hides no
existing check); tb-infra adds trap legitimacy to the follow-up landing (T-137: the model is armed only when
the bus driver's arm list announced an error for that address or the model's PMP state denies the access;
otherwise the trap record is a fail-loud comparator miss with a named id, with an out-of-tree red where the
DUT faults a legal access); until T-137 is committed and reviewed, results of tests that inject bus errors or
rely on PMP denials are consistency-only and do not count toward the plan, and the scoreboard document states
the limitation. Medium 3 of the same review is T-134 (interrupt splitting a Zcmp sequence): the comparator
never clears the sequence bookkeeping on interrupt or debug entry, so the restart appends micro-ops and fails
under a misleading id, or passes silently when isa_mem is knob-silenced; tb-infra settles it in the same
landing.

## LOG-027 - 2026-09-03 - GATE (Runtime follow-up e884dd1: cross-model REQUEST-CHANGES; no measured round until re-review)

The cross-model review of 95d4d0e..e884dd1 (dv/auto_dv/reviews/2026-09-03-claude-diff-95d4d0e0-e884dd12.md)
verified the canary hold, the build-input set, the env scrub and the red_expect trigger, but found one major:
gen_round.py now writes future round evidence under gen_-prefixed names while the exclusion tools
(dv/auto_dv/excl/gen_excl_select.py, gen_excl_f1_pass.py) still read asserts.txt and regress_manifest.yaml,
so the first collected round would break the R-5 exclusion pipeline; plus the serialized fallback after a
failed shared sync pins HEAD-now unvouched, the T-131 response row overstates the rename (the rebaseline
directory keeps 10 un-prefixed files), and the new self-test blocks use C.SELFTEST_TMP instead of
C.selftest_tmp(), so the claimed 51-ok self-test cannot be reproduced from a detached checkout. Ruling: e884dd1
stays committed (nothing weakens serving of check-tier batches, wave 5 proceeds); no measured round (round 0)
is collected until the fix landing is committed and re-reviewed; the evidence file names get one constant home
in gen_flow_const.py consumed by gen_round.py and both excl tools (Runtime and rtl-arch coordinate, one
landing).

## LOG-026a - 2026-09-03 - RULING SHARPENED (T-137 form, after the Critic's T-102c verdict)

The Critic's T-102c light check (dv/auto_dv/docs/gen_critic_tb_t102c.md, REQUEST-CHANGES on one medium) agrees
the DUT-driven fault arming is the hole and sharpens LOG-026: before 18470dd Spike's own PMP decided a denial
independently and a phantom trap was an isa_trap miss; after it a DUT PMP denial the spec does not require, or
a trap with no cause, is mirrored and accepted as truth, so "consistency-only" understates the loss. Ruling:
the UNCONDITIONAL arming form is held, not arming as such. T-137 delivers the conditioned form: the model is
armed only for a bus error the bus driver injected or armed for that address, never for a PMP denial (Spike's
PMP decides those), with a TB-caused versus unexplained split in the GEN_SB report; the trapping-Zcmp green
must stay green under it. No PMP-denial or bus-error test is credited before T-137 is committed and both
reviewers have passed it. The T-102b medium is closed: the trap-record offset on a Zcmp micro-op is 0 per
rtl-arch R9 (the Critic's earlier "length 2" is corrected in its verdict), and plan C-1/C-12 must state the
RTL convention (DV Lead, v2i).

## LOG-028 - 2026-09-03 - RULING (emitted set usable for the sunset except regime and pin until observed)

The cross-model review of step 2 (dv/auto_dv/reviews/2026-09-03-claude-diff-1215244d-4acef549.md,
APPROVE-WITH-CHANGES) finds that the regime-phase and pin debug_req writers have never been observed emitting
(zero lines in all analysed runs), that the "active source without a writer" fatal runs only when the export
is enabled, and that registration is done by gen_env on the writers' behalf so a deleted writer leaves the
header, manifest and fatal path agreeing on a source nothing emits. Ruling: the emitted set rendered at 4acef54
may drive the first bulk token removal for items whose export rows come from ibus, dbus, alert, misc and
scrkey; items whose rows come from regime or pin keep their coverage-only token until tb-infra retains one run
with a REGIME_SET and a DBG_REQ assert/release with hand-checked first lines (CM8-M-3). tb-infra moves the
writer fatal ahead of the enabled check, has each writer register its own source, and adds the two bus count
rules to read() with a mutation each (CM8-M-1, CM8-M-2) in the follow-up landing.

## LOG-028a - 2026-09-03 - RULING SHARPENED (sunset input = observed rows, exclusion by row)

The Critic's step-2 verdict Section 7 (dv/auto_dv/docs/gen_critic_rvfi_export_s2.md) shows LOG-028 was too
coarse in both directions: the emitted set as rendered from the yaml is a declaration, which is what the sunset
was designed not to trust; and excluding whole sources (regime, pin) would hold 84 items, 58 of them on rows the
retained runs did observe. The rows never observed in any retained run are exactly three: regime phase, pin
debug_req and pin irq_nm (55 items name one of them; irq_nm alone 33). Ruling: (1) the sunset input is the set
of rows OBSERVED in a retained run of the pinned build: Runtime produces a per-row first-seen list from the
canary export files (row, first run, first line) beside export_sources_emitted, and derives the emitted set from
the canary run's header rows rather than the yaml (T-140); the DV Lead's gen_trace_check.py reads the first-seen
list and un-marks an item only when every one of its export rows is observed (v2i tool patch extended, v2j
driven by it); (2) exclusion is by row, not by source: the three unobserved rows hold their 55 items until a
retained run shows them; (3) tb-infra makes writers register the rows they emit and the sink fatal at
elaboration on an emitted row with no registered writer (T-141, with CM8-M-1/M-2). Supersedes the source-level
wording of LOG-028; the M-1 fix (read export_sources_emitted, not export_sources) lands with v2i.

## LOG-029 - 2026-09-03 - NOTE (fence-adjacent slips by two Test Writer subagents; no fenced content touched)

Reported by the Test Writer at 13:50Z: the mul_mul subagent ran one read-only `git log -1` and a `find` that
listed path names under dv/auto_dv/work/orchestrator and dv/auto_dv/work/runtime (nothing read); the mul_div
subagent listed the shared out directory named in gen_site.yaml and read three lines of a sibling run's
sim.log inside the Test Writer's own work directory. None of these touches fenced content (docs/dv/FENCE.md
denies Ibex DV collateral, sibling clones, other branches and remotes, and the shared /tmp); they break the
team rules (teammates run no git commands; a role lists only its own work directory). Recorded for
transparency; the Test Writer re-briefs its subagents. No owner action needed.

## LOG-030 - 2026-09-03 - NOTE (wave 5: layers live expose a fixed end-of-test budget; progress-based wait in landing 3c)

Wave 5 (test-writer-047/048, head mode with step 2b, so every flow run now draws and applies bus regimes):
gen_test_cmp_zcmp_basic PASS on two seeds (528k and 654k cycles, UVM_ERROR 0); seed 421987159 and its red FAIL
with "end-of-test store 1 of 4133 not seen within 300000 cycles" under dmem_gnt_delay long plus imem_rvalid_delay
long/random plus imem_gnt_delay random. Not a hang: the core kept fetching (12272 ibus rvalids in 300k cycles);
the program's long prologue had not reached its first report store within the template's fixed per-store budget.
Reproduced locally with the exact schedule; single regimes pass. Decision: the template's end-of-test wait
becomes progress-based in landing 3c (a store is late only when retirement has stopped for one budget, failing
loud as "no retirement"; a program that keeps retiring is waited for up to 16 budgets with GEN_TEST_SLOW lines
counted in the report, then failed as a runaway; the cmp_zcmp_basic tripled-budget hack removed; red fixture
gen_ut_eot_stall proves the fail path). Batch-2 acceptance (049..062) and the wave-5 re-file run against the
3c commit. Counted as a template defect found by acceptance under live layers; no DUT finding.
