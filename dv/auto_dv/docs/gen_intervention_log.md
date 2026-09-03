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

## LOG-024b - 2026-09-03 - GATE HELD (landing 3b + batch 2 at 9988a2f: cross-model REQUEST-CHANGES on one high)

The cross-model review of 040984a..9988a2f (dv/auto_dv/reviews/2026-09-03-claude-diff-040984a6-9988a2f0.md)
verified the not_built two-sided guard, the fire_tp reachability rule, the bins_not_hit manifests, the csr_access
consistency compares, the seven lint red sources, the batch-2 fire checks, flow-style generators, 389 retained
files by md5 and the two unmasked TB rows. It holds the gate on one high: the library self-test is red at this
HEAD independent of the testlist transient, because the held-back gen_test_bit_draft.py has no not_built and the
new guard refuses it; the evidence texts that cite the self-test as passing over all 16 tests describe a state
that does not exist in the committed tree. Three mediums (isa_cti manifest header text is not a fresh render;
the lint residual is still understated, a bare alias of self defeats every self-rooted rule; the isa_alu retained
runs predate the 602-bin manifest) and three lows fold into landing 3c together with the LOG-030 template fix
and bit_draft. LOG-024 stays in force until 3c is committed and re-reviewed. Orchestrator note: holding bit_draft
out of a landing whose guard covers every test module created the red; a held-back file must be checked against
the new lint before the commit.

## LOG-031 - 2026-09-03 - WATCHDOG (tb-infra instance stopped and respawned)

tb-infra's STATUS.md stayed at 13:28Z, its last file (out_fu_mut_driver.log) at 13:36Z and its last shared-tree
edit (gen_rvfi_pkg.sv) at 13:32Z; the follow-up build out_fu/a had finished green at 13:29:54Z (vcs exit 0), no
simulator process remained, and the agent showed "running" with no output for 45 minutes. Nudged at 14:05Z
(watchdog rule: one nudge), still silent at 14:15Z: stopped at 14:19Z and respawned under the same name with
the common briefing, the role section, the inherited shared-tree edits (T-134, T-136, T-137, CM5/CM6 items,
codegen fixtures, README rename), the binding rulings (LOG-025, LOG-026a, LOG-028a), the open review rows
(CM5/CM6/CM8, CR5/CR6, Critic Section 7) and the RTL facts to encode (R9, R10, R11). Work order: verify the
inherited edits by rebuilding, finish the checker holes first, split into two landings if needed, close the
window with the canary. Third respawn of the day (rtl-arch LOG-010, tb-infra earlier); the pattern is a long
foreground turn with no filesystem output, which the STATUS rule is meant to expose.

## LOG-024c - 2026-09-03 - GATE HELD (landing 3c at 69be96b: cross-model REQUEST-CHANGES; Orchestrator verification error)

The cross-model review of ee2405a..69be96b (dv/auto_dv/reviews/2026-09-03-claude-diff-ee2405a7-69be96b5.md)
finds a high in the library self-test itself: every red-source loop raises AssertionError("red source ...
accepted") inside a try whose except catches AssertionError and checks the reason text, so the loops cannot
fail and none of the refused-forgery claims was ever proven; re-running with a collector shows one of the nine
new reds accepted (a helper aliasing its parameter before writing failures). Mediums: the committed-tree
self-test claim was false at 69be96b (bit_ratified has no entry in the committed testlist until e83614c); the
602-bin isa_alu green is asserted, not retained; the residual wording is still inaccurate because
indirection-free statements pass (del self.failures[:], attribute-chain writes through template-owned objects,
template patching through an import alias). Orchestrator error: the "PASS in both forms" verification for
69be96b was run in the working tree, which already carried Runtime's uncommitted testlist edit; committer
checks must run from a detached checkout of the commit, as the reviewers do. Ruling: the self-test loops get a
sentinel that cannot be swallowed and every red is re-proven; the helper-parameter rule treats every parameter
of a helper that receives self at a call site as test-standing; the lint stops growing beyond that, and the API
document replaces "any indirection defeats it" with an explicit list of the refused forms plus the sentence that
everything else passes and the lint is not a guarantee (the guarantee stays architectural: committed testlist
ids, fire-check codes, SV ledger). These fold into the pending landing 3d; LOG-024 holds until 3d is committed
and re-reviewed.

## LOG-032 - 2026-09-03 - RULING (B13: odd jalr target is a DUT bug candidate of the RVFI-only class; comparator convention)

rtl-arch row R11 (dv/auto_dv/evidence/gen_t102_rtl_facts.md, promoted 040984a): a jalr to an odd target has bit 0
dropped at fetch (rtl/ibex_if_stage.sv:244, :288, :416) and every architectural register is even, but
rvfi_pc_wdata of the jalr record carries the raw target (rtl/ibex_core.sv:2084, pc_set ? branch_target_ex :
pc_if), violating the RVFI definition while ISA execution is per spec; observed by gen_test_isa_cti as isa_pc_next
dut == model | 1 on 64 of 64 odd targets per seed. Ruling (given by message at 13:58Z, recorded here): B13 is a DUT
bug candidate of the RVFI-only class in the bug log with the one-line fix at core.sv:2084 that DV does not make;
until the RTL owner fixes it, tb-infra encodes the comparator convention (mask bit 0 of rvfi_pc_wdata on the jalr
record, or compare the next record's pc_rdata) as a documented, counted exception with a red where the mask is
removed (T-144); the plan describes that convention as owed to tb-infra until the commit lands, never as built.
R10 (mtval = 0 on a breakpoint exception, spec-legal) is a shim convention, not a bug.

## LOG-027a - 2026-09-03 - HOLD LIFTED (round-0 measured regression may be collected)

The cross-model review of b8332f9..73af457 (dv/auto_dv/reviews/2026-09-03-claude-diff-b8332f92-73af4570.md) is
APPROVE-WITH-CHANGES: the round evidence names have one home consumed by gen_round.py and both exclusion tools,
the serialized fallback pins the accepted batch sha, the rebaseline rename is real, C.selftest_tmp() is used
throughout, T-140's observed-row fields exist. One medium remains for Runtime's next landing (T-151): a request
carrying an empty elcheck key is treated as report-only by the server but as a simulation by validate, so it
would build unvouched outside the pinned set; plus four lows (URG_DUMP_MODULE_PREFIX cross-import makes
gen_excl_f1_pass.py crash when started outside the clone root, hoist it to gen_flow_const; ROUND_EC3_ASSERTS_RE
derived from EVIDENCE_DIR; T-131 row wording; response counts). The LOG-027 hold on the first measured round is
lifted: Runtime may collect round 0 once the DV Lead requests it, rtl-arch's F-1 pass follows it, and no request
with an elcheck key of any kind is served in head mode until CM13-M-1 lands.

## LOG-033 - 2026-09-03 - GO (first cycle-clause token removal, sunset pass 1)

Reference for pass 1: Runtime's head-mode build of 2696920 (canary PASS, gen_ut_export probe PASS), manifest
dv/auto_dv/work/runtime/out/probe_export_1445_v2k/build/gen_tb/build_manifest.yaml, export_sources_emitted 28 rows
over 7 sources from the export header, export_rows_observed 19 rows; nine declared rows (pin debug_req, the five
irq pins, regime phase, scrkey req and valid) are unobserved by a single gen_ut_export run and hold their items per
LOG-028a. The DV Lead lands v2k (CM12 rows, Critic v5 lows, LOG-032 citation) then v2j (row-level observed gate in
gen_trace_check.py and the driver; retained before/after log; rehearsal on the earlier probe: 115 released, 86
gated, 105 marked left) as one landing citing this manifest; pass 2 follows T-150's regression. Nothing enters the
Phase 1 numbers through this: it changes which witness bins are must-hit for the affected tests (rule (f)), and the
only built test touched, gen_csr_trap_setup, has its two items gated in pass 1.

## LOG-034 - 2026-09-03 - RULING (retained-log excerpts for per-item red runs)

Retention rule for the Test Writer's per-item red runs, given by message during the batch-1 remediation and
recorded here because the manifest header cited LOG-024 for it: a per-item red run is retained as a decisive-line
excerpt (the GEN_TEST_FAIL harness line with the fire id, the collected-failure lines that precede it, the UVM
summary or its absence, and the run header naming build, seed and plusargs), listed in gen_manifest.md with the
md5 of the excerpt file; full stdout and sim logs are retained for every green run, for every default red, and for
any red whose verdict a reviewer disputes. The excerpt must carry the line a reviewer needs to reproduce the
flow's verdict with gen_verdict.decide_lines; an excerpt that does not is treated as unretained.

## LOG-024d - 2026-09-03 - GATE HELD (landing 3d at 7f78c41: cross-model REQUEST-CHANGES on two highs)

The cross-model review of 2696920..7f78c41 (dv/auto_dv/reviews/2026-09-03-claude-diff-26969205-7f78c418.md)
finds two highs: the mul_div filler fix is ineffective (FILLER_REGS moved to x29..x31 but the filler templates still
emit x5..x7, which are operand registers; the disjointness assertion checks a set the fillers do not use; the
CR-B2-L-8 row saying FIXED is false), and the new red_expect self-test rule accepts by method name and prefix, so
the two boundary signatures it was written to catch still pass it (Runtime's T-151 at 356790d has since committed
the corrected (?!\d) signatures, but the rule must synthesize the harness line per recorded check name and require
the regex to match). Mediums: the lint grew by a del check beyond LOG-024c while the API still does not enumerate
the refused shapes one-to-one with the self-test red list, lists template patching as refused although the
import-alias form passes, and lacks the guarantee sentence; the transcript says "no rule was missing" while the
call-site fixpoint added in 3d is the rule that was missing. Rulings: (a) the red-source list at 7f78c41 (including
the del check) is the frozen set; the API enumerates exactly that list, names the probed passing forms, and states
the lint is not a guarantee; no further growth. The Critic accepted this enumeration path in its v4 Section 6, so
no Critic-versus-ruling conflict remains to route to the owner. (b) LOG-024 stays in force: the measured flip, the
tier promotion and batch-2 acceptance wait for landing 3e and its re-review; the round-0 sequence (T-158) shifts
behind it. (c) Every response row marked FIXED must be backed by a check the reviewer can rerun; a FIXED row whose
fix does not touch the failing path is an honesty defect, not a low.

## LOG-035 - 2026-09-03 - RULING (TP-CMP-001 floor; recorded because the plan cited an unlogged ruling)

The DV Lead's batch-2 ruling that TP-CMP-001's ">= 5000 instructions" floor becomes >= 3000 retired per seed with
the per-form floors governing (the template's single-program budget caps a seed near 3800; batch-2 evidence in
dv/auto_dv/evidence/gen_tdd_batch2.md) is confirmed. The plan cites this entry, not a time of day.

## LOG-036 - 2026-09-03 - GATE + RULE (plan v2k broke the committed library self-test; joint landings for group changes)

The Critic's revised v6 (dv/auto_dv/docs/gen_critic_plan_witness_v6.md) finds, and the Orchestrator reproduced
from a detached checkout of HEAD with no environment variable, that the library self-test is red since 5f530a8:
plan v2k moved TP-CSR-026, TP-CSR-029 and TP-CSR-031 out of gen_csr_trap_setup while the committed
gen_test_csr_trap_setup declares them, and the two-sided not_built guard reads the plan's groups, so it fails with
"outside the group". The Orchestrator's detached-checkout verification covered the Test Writer landing (7f78c41)
but was not repeated after the plan landing, although the guard couples the two. Rules: (1) a plan change that
moves or removes an item a committed test builds or declares lands in the same commit as the Test Writer's matching
test and manifest change (joint landing), never alone; (2) the committer runs the library self-test from a detached
checkout after every landing that touches gen_test_plan.md, the trace CSVs or dv/auto_dv/tests. Resolution: v2l
(TP-CSR-029 back in gen_csr_trap_setup; only 026 and 031 move) and the Test Writer's gen_test_csr_trap_setup change
(026 and 031 removed from its not_built, manifest re-rendered) land as one joint commit. T-153 re-retain scope is
four logs (rst_boot, csr_reset, csr_trap_setup, pmp_csr_warl); isa_cti and cmp_zca stay STALE for a different cause
(comparator rows pending T-144 and the R10 shim row) and the check must label the cause.

## LOG-037 - 2026-09-03 - NOTE (tb-infra follow-up landing 1: three findings from running the inherited checker rules)

tb-infra's follow-up landing (T-134, T-136, T-137, T-141, R10/R11 rows, all CM5/CR5/CM6/CR6/CM8/CS2 rows) reports:
(1) the inherited T-136 rule was unsound in three ways found only by running it (driver-released-and-re-raised
lines; raises between the previous record's post_mip sample and its retirement; classification from the model's
stale mcause on NMIs the model does not emulate); the landed rule is documented in gen_component_api_irq_checker.md
Section 1, with measured costs in the storm run (371 undecidable priority claims, 415 released expectations from
UNTIL_TAKEN releasing untaken lines; landing 2 narrows it to the taken line). (2) Internal NMIs from injected
integrity errors are legitimised by the driver's announcement (rtl/ibex_controller.sv:391-430), never by the DUT's
own rvfi_ext_nmi_int. (3) The shim has no NMI emulation, so NMI-enabled results stay consistency-only for the model
until landing 2. T-136's LOG-025 hold and T-137's LOG-026a hold lift only when both reviewers pass this landing.

## LOG-037a - 2026-09-03 - HOLDS STAY (tb-infra follow-up landing 1 at ce33b4f: cross-model REQUEST-CHANGES)

The cross-model review of 4cbb4be..ce33b4f (dv/auto_dv/reviews/2026-09-03-claude-diff-4cbb4bee-ce33b4f3.md)
finds one high: T-136 is blind to every interrupt entry whose handler's first record is a non-last Zcmp micro-op,
because the fold returns before the state is published, so the irq checker never sees the entry (the landing's own
retained green shows irq_entries=5 in the scoreboard against entries=0 in the irq checker, the UNTIL_TAKEN releases
hiding the loss); the "every intr record" claims in the API document, LOG-037 and the CR5-M-1 rows are false for
exactly the case gen_zcmp_irq_directed.S exercises. Mediums: a stale bus-error announcement (one word left over from a
misaligned access with both halves erroring) can legitimise an unrelated later DUT trap; the MB3/MB6/MB7/MUT-I/J/K
mutations ran on a pre-landing tree while the response row says the landed tree. Ruling: the LOG-025 (T-136) and
LOG-026a (T-137) holds stay in force; tb-infra lands a fix (1c) with: an entry state published or carried to the fold
record so the irq checker evaluates it, a report-time referee irq_chk.entries_seen == sb.irq_entries that fails on
mismatch, both words of a spanning access consumed by take() and announced minus taken reported as an error when
non-zero, the mutation record carrying the build sha per mutant with MB3/MB6/MB7/MUT-I/J/K re-run on the landed tree
or labelled as earlier-tree evidence. LOG-037's "every intr record" sentence is corrected by this entry.

## LOG-038 - 2026-09-03 - GO (cycle-clause sunset pass 2)

Reference for pass 2: Runtime's head-mode regression pinned to 979350a (canary_head_t150 PASS; gen_ut_export plus
the five T-150 export-observing entries gen_ut_export_irq_storm, gen_ut_export_dbg_storm, gen_ut_export_scrkey_delayed,
gen_ut_export_rows_nmi, gen_ut_export_rows_dbg; six runs PASS, UVM_ERROR 0, LSF jobs 10941862..10941867), build manifest
/proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/build/gen_tb/build_manifest.yaml with export_rows_observed
covering all 28 declared rows (the nine rows pass 1 never observed are first-seen here) and nothing outside the
declared set. The DV Lead runs pass 2 as landing v2m after the joint 3e + v2l commit, retains the manifest copy and
the logs under dv/auto_dv/evidence/gen_sunset_pass2/, and cites the tracked paths. Expected: the 86 items gated in
pass 1 release; the 17 icram-dependent items, TP-PMC-001 and TP-REG-018 stay marked until an icram writer exists.
Releasing a token changes which witness bins are must-hit; no result enters the Phase 1 numbers through this.

## LOG-036a - 2026-09-03 - RESOLVED (committed library self-test green again at e420c7e)

The joint landing e420c7e (plan v2l plus the Test Writer's gen_test_csr_trap_setup.py and manifest) restores the
two-sided guard: TP-CSR-029 stays built in gen_csr_trap_setup, only TP-CSR-026 and TP-CSR-031 move to
gen_csr_trap_setup_irq, and the test's not_built is empty. Verified by the Orchestrator from a detached checkout of
e420c7e with no environment variable: GEN_TEST_LIB self-test PASS; gen_trace_check.py against the retained pass-1
manifest PASS with 105 marked. The red window on the committed structure gate ran from 5f530a8 (14:49Z) to e420c7e
(15:46Z). Rules of LOG-036 stand.

## LOG-039 - 2026-09-03 - RULING (measured runs declare their functional coverage; gen_ut_lockstep measured: false)

Runtime's promotion landing sets fcov_manifest_required_tiers: [smoke, targeted], which the flow enforces at merge
time: a measured run on a required tier without an fcov_expectation_file fails. gen_ut_lockstep (tb-infra's
lock-step check, tier smoke, measured: true, no plan items, no manifest) would fail the first measured merge.
Ruling: a measured run must declare its expected functional coverage; gen_ut_lockstep becomes measured: false in
the same landing; tb-infra may re-promote it with a manifest if it wants its coverage counted. The 15 promoted
tests (14 smoke, gen_test_bit_draft targeted; gen_test_boot_retire stays check / measured: false) carry their
per-item manifests per the DV Lead's tier table.

## LOG-037b - 2026-09-03 - HOLD ANSWERS (Critic on tb-infra follow-up landing 1)

The Critic's check of ce33b4f (dv/auto_dv/docs/gen_critic_tb_fu1.md, REQUEST-CHANGES on one high and two mediums,
the same high as the cross-model review) answers the two holds explicitly: LOG-025 (T-136) does NOT lift until the
entry state is published before the Zcmp fold, a red on gen_zcmp_irq_directed proves cause-checked equals
irq_entries, and a report-time rule enforces it; LOG-026a (T-137) MAY lift with tb-infra's next landing on two
conditions that belong to it anyway: MB6 re-run on the committed sha, and take() consuming both words of a spanning
access. The 371 undecidable priority claims are not a soundness gap; the plan credits priority-pick items only from
runs where the entry's claim was decidable (condition for the DV Lead, not a hold). Two record notes: the Critic
saw the subject line of the artifact's commit in a git log listing before writing (the artifact itself was opened
only after its Section 5; H-1 is established from the code path and the retained counts); and the DV Lead's
read-only audit of the 187 retained logs found them byte-consistent with the manifest while gen_fu_a_* / gen_fu_c_*
names cited in the transcript do not exist as files (driver-log verdict lines only). Both go to tb-infra's 1c rows.

## LOG-038a - 2026-09-03 - LANDED (sunset pass 2 at d0e6a71)

Pass 2 landed as the joint commit d0e6a71 (plan v2m plus the Test Writer's gen_test_csr_trap_setup manifest): 86
tokens released across 36 groups by the 28 observed rows of the retained reference
dv/auto_dv/evidence/gen_sunset_pass2/gen_build_manifest_979350a.yaml, 0 gated, 19 items still marked (17
icram-dependent, TP-PMC-001, TP-REG-018). The released TP-CSR-029 witness bin is declared by gen_test_csr_trap_setup
under bins_not_hit (rule (g), irq agent absent) so it stays visible as unhit. Verified by the Orchestrator from a
detached checkout: library self-test PASS with no environment variable; trace check PASS with 19 marked. Reviews:
cross-model running; Critic v8 queued. Two passes (LOG-033, LOG-038) have now moved 201 of the 220 original
coverage-only items to must-hit; the 19 remaining wait for an icram writer.

## LOG-024e - 2026-09-03 - GATE LIFTED (landing 3e at 7ef16a0: cross-model APPROVE-WITH-CHANGES)

The cross-model review of 7d6e4f4..7ef16a0 (dv/auto_dv/reviews/2026-09-03-claude-diff-7d6e4f4e-7ef16a0a.md) is
APPROVE-WITH-CHANGES: the mul_div fillers are fixed on the failing path, the red_expect rule is in the decide_lines
form, the refused-form list is frozen and enumerated, the six pre-T-102 red logs are re-retained, the opt-out is
dropped from all 16 tests with seed-1 greens. One medium (the rule's negative exists only as a transcript record
from a staged testlist copy; an in-self-test negative is required) and one low (a history-narrating docstring) go to
a small Test Writer landing 3f. The LOG-024 gate (held since d1d68fd through LOG-024b/c/d) lifts: Runtime lands the
tier promotion (T-170, LOG-039) and serves the batch-2 acceptance wave 049..064 as check-tier runs pinned to HEAD;
the DV Lead requests round 0 after the promotion copy (T-158); the Test Writer may dispatch batch 3 (interrupt-free
groups first). The T-136/T-137 holds (LOG-037a/b) are unaffected and still gate interrupt-enabled and fault results.

## LOG-040 - 2026-09-03 - ORCHESTRATOR ERROR (a running review destroyed by housekeeping; relaunched)

While relaunching the v2n + 3f review to correct its focus text, the Orchestrator removed every run directory under
dv/auto_dv/work/orchestrator/review_tmp/ and pruned worktrees, which destroyed the run directory and detached
worktree of the v2m review (4e60cc7..d0e6a71) that was still executing; its wrapper ended with "claude -p failed
(rc=1)" and no verdict. No artifact was written and nothing was committed from it. The v2m review is relaunched with
the same focus (this note is stated in it). Rule: housekeeping after a kill removes only the killed run's directory
(by its pid file), never review_tmp/run.* wholesale, while any other review is running.

## LOG-024f - 2026-09-03 - PROMOTION LANDED (3e6f1b2): the 15 built tests are measured

Runtime's promotion landing 3e6f1b2 moves the 15 built tests to their plan tiers (14 smoke, gen_test_bit_draft
targeted) with measured: true and their per-item manifests wired, sets gen_ut_lockstep to measured: false (LOG-039)
and the header fcov_manifest_required_tiers: [smoke, targeted]; gen_test_boot_retire stays check / measured: false.
Verified by the Orchestrator: loader PASS, red-signature check PASS exit 0, util self-test 58 ok; the testlist deltas
are exactly the 15 tier/measured/manifest triples, the one gen_ut_lockstep field and the header. Runtime now serves
the batch-2 acceptance wave test-writer-049..064 (check tier, head mode, pinned to HEAD) and the DV Lead files the
round-0 request (T-158). Results of items under the T-136/T-137 holds are recorded, not credited.

## LOG-039a - 2026-09-03 - CORRECTION + HOLD (the fcov header fails unmeasured smoke entries; round 0 held)

The cross-model review of the promotion landing (dv/auto_dv/reviews/2026-09-03-claude-diff-59aec18c-18f9ee04.md,
REQUEST-CHANGES) shows LOG-039's premise was wrong: gen_regress.fcov_policy_failures keys on tier only and never
reads measured, so with fcov_manifest_required_tiers: [smoke, targeted] the two unmeasured smoke entries gen_boot_zc
and gen_ut_lockstep (no manifest) are flipped from PASS to FAIL in every smoke-tier regression, and setting
gen_ut_lockstep to measured: false remedies nothing. Ruling: Runtime lands a fix before any measured round is
dispatched: fcov_policy_failures skips runs whose entry is measured: false (the LOG-039 intent), with a gen_regress
self-test case carrying the measured field and the docstring aligned; the 15 promoted entries return to flow-style
serialisation; the red-check CLI's line and summary builders become functions covered by the self-test. Round 0
(request round_0, filed 16:10Z) is HELD until that landing is committed and re-reviewed; the batch-2 acceptance wave
(check tier) is unaffected and continues. The Orchestrator's error: ruling on a described enforcement without a
grep of the enforcing code.

## LOG-036b - 2026-09-03 - GATE (the manifest generator's self-test is red since d0e6a71; committer check extended)

The relaunched cross-model review of the pass-2 landing (dv/auto_dv/reviews/2026-09-03-claude-diff-4e60cc70-d0e6a719.md,
APPROVE-WITH-CHANGES) finds gen_fcov_manifest.py --self-test red at d0e6a71 and green at its parent: its rule (f)
case asserts the cycle-clause token on TP-CSR-029, the item pass 2 released. The Orchestrator reproduced it from a
detached checkout of HEAD. The committer check ran only the library self-test; from now on both
`python3 -m dv.auto_dv.tests.gen_test_lib --self-test` and `python3 dv/auto_dv/tests/gen_fcov_manifest.py
--self-test` run from a detached checkout after every landing touching the plan, the trace CSVs or dv/auto_dv/tests.
Fix: the Test Writer retargets the rule (f) case to a row that stays marked (TP-REG-018, or the first marked = 1 row
of gen_trace_witness_ids.csv selected at run time) as landing 3g. Also recorded from the same review: TP-REG-018 is an
icram-gated item (row icram inject), not a no-export-row item, so the "19 marked" reads 18 icram-dependent plus
TP-PMC-001; and gen_wit_cycle_clause_cg (CG-WIT-001) has no SystemVerilog implementation yet, so the released witness
bins are must-hit in the plan but not scored by any covergroup until tb-infra implements it (T-179).

## LOG-041 - 2026-09-03 - EVENT (workstation login expired at about 16:20Z; restored by the owner)

At about 16:20Z every teammate reported "Login expired" and the sandboxed cross-model reviewer of tb-infra's
landing 2a (99ddf39..4d48d84) ended with "claude -p failed (rc=1)" after a complete run (no artifact written; raw
output kept under work/orchestrator/review_failed/run.ifkgjD.raw.json for the record only). The owner re-ran
/login at 16:2xZ ("Login successful"). The Orchestrator relaunched the 2a review with the same focus and re-pointed
each teammate at its pending task. Nothing in the tree changed as a result; no landing was lost. The acceptance wave
Runtime had restarted under a 6 h wrapper at 16:15Z may have been interrupted and is re-checked by Runtime.

## LOG-041a - 2026-09-03 - RECOVERED (all six teammates resumed after the owner's /login)

By 16:34Z every teammate had resumed on its pending task after the re-pointer messages: critic, rtl-arch, runtime
and tb-infra refreshed STATUS; dv-lead and test-writer resumed writing (plan parts, batch-3 sweeps). No respawn was
needed. The relaunched 2a review is running. rtl-arch reports that the times it wrote into STATUS and messages today
were estimates that drifted hours ahead of the clock (the file mtimes were on cadence); from 16:29Z its stamps come
from date -u. The same drift was reported earlier by tb-infra (LOG-031 period). Rule for all roles: stamps come from
the clock, never from an estimate; the watchdog reads mtimes and is unaffected.

## LOG-042 - 2026-09-03 - HOLD (batch-2 acceptance wave: 13 of 24 greens fail the template's schedule check; round 0 held for the triage)

The batch-2 acceptance wave test-writer-049..064 (head mode pinned to d3c6ca8, served 16:17-16:29Z, survived the login
expiry) gives 11 PASS, 13 FAIL, 8 RED-OK, 0 NOT_RUN; every run's GEN_TEST_BINS equals its committed manifest, UVM_ERROR
0 on every PASS, every red RED-OK on its pinned fire id (cmp_zca and isa_cti reds included), cmp_zcmp_basic 3 of 3 PASS
with slow_total rounds 3, 3, 1 as LOG-030 intends. Every one of the 13 FAILs carries one signature, the template's
fire_schedule_applied check ("reached N of M scheduled entries by EOT, applied 6, missed [layer entries such as
imem_outstanding_cap:cap8@c1871, dmem_rvalid_delay:random@c16270, scr_key_delay:withheld_then_valid@c158]"): cmp_zca
1/3, bit_ratified 0/3, isa_alu 1/3, isa_shift 2/3, isa_cti 1/3, mul_div 0/3, mul_mul 3/3. The same tests passed at
seed 1 on a local ce33b4f export before landing 2a (7ef16a0's l9g proofs); the wave ran on a tree carrying 2a
(taken-line-only release, storm mean 100). "applied 6" on every failing run points at a cap or a stop in the
dispatcher or the schedule runner rather than at the DUT; whether the drawn schedule is applied by the TB or is
unreachable within the program is the triage question. Ruling: the Test Writer leads the triage with tb-infra
(reproduce one failing seed locally on d3c6ca8, read the GEN_CMD_DISPATCH and GEN_TEST_PHASE lines, decide whether the
template's check, the schedule draw or a layer driver is wrong; a fix lands as the Test Writer's or tb-infra's next
landing with a red); round 0 stays held until both the T-178 review and this triage conclude, because a measured
round whose smoke tier fails on a TB-side schedule check would not be a Phase 1 gate baseline. LOG-024 remains lifted;
the wave counts as batch-2 acceptance evidence for the 11 greens and 8 reds only.

## LOG-037c - 2026-09-03 - HOLDS STAY + NEW HOLD (tb-infra landing 2a at 4d48d84: cross-model REQUEST-CHANGES)

The relaunched cross-model review of 99ddf39..4d48d84 (dv/auto_dv/reviews/2026-09-03-claude-diff-99ddf39f-4d48d844.md)
confirms what tb-infra had stated item by item: none of the LOG-037a/b fixes are in 2a (the two highs: the interrupt
entry whose handler starts with a non-last Zcmp micro-op is still folded before publish_state, retained landed-tree
green irq_entries=15 versus irq checker entries=0; take() still consumes one word and the announced-minus-taken referee
is absent), so the T-136 and T-137 holds stay for landing 1c. Two new mediums of the DUT-driven-acceptance class: the
NMI-pre-empted rule writes t.intr = 1 into the shared monitor transaction, so the observation-only export R line and
every later subscriber see intr=1 where the DUT drove 0, and no retained green exercises the path (nmi_preempted=0
everywhere) while the scoreboard doc claims 2; and rf_wr_suppress acceptance rests on the DUT's flag alone (the model's
write is undone and the rd compare skipped whenever the DUT asserts it, with no check that a corruption was announced
for that load), so a DUT that spuriously drops a load's register write is accepted. Rulings: (1) 1c carries both
LOG-037a/b fixes, the t.intr mutation replaced by a local flag with a retained green showing nmi_preempted > 0, the
rf_wr_suppress undo gated on an announced corruption for that load with the DUT's rd fields compared against no write
(T-183), MB6 re-run on the committed sha with a per-mutant build-sha column, and a response table for every fu1 and 2a
row; (2) until 1c passes both reviewers, integrity-error runs stay consistency-only for the model (the "full lock-step
compares" sentence in the scoreboard doc is withdrawn) and NMI-enabled results stay under LOG-025; (3) the plan's
Section 0a must not describe rf_wr_suppress handling or the NMI-pre-empted convention as built checks. Third instance
today of a comparator rule that takes a DUT-side field as its reason to skip or undo a compare (F3 vectored cause,
fault arming, now rf_wr_suppress): any such rule must be gated on an independent TB-side fact before it counts.

## LOG-039b - 2026-09-03 - CONDITION MET (T-178 reviewed APPROVE-WITH-CHANGES; round 0 now waits only on the T-181 triage)

Runtime's T-178 fix (7a468ec: fcov_policy_failures exempts measured: false with a self-test covering both cases; the
promoted entries back in flow style; the red-check CLI builders self-tested) is APPROVE-WITH-CHANGES
(dv/auto_dv/reviews/2026-09-03-claude-diff-04dea6be-7a468ec7.md; two lows on documentation wording and a diff count,
one fixture info). The LOG-039a condition on round 0 is met; round 0 (request round_0, filed 16:10Z) now waits only
on the LOG-042 condition: the fire_schedule_applied triage (T-181, Test Writer with tb-infra) concluding with a fix
landed and reviewed, since the same smoke-tier tests would otherwise fail the round on a TB-side check.

## LOG-042a - 2026-09-03 - CAUSE FOUND (the 3e template's schedule runner never applies mid-run phases)

Runtime's bisect (two operator probes, gen_test_bit_ratified seed 288888690 pinned to 7ef16a0, the 3e template on the
pre-2a TB, and to d3c6ca8, the wave's tree) is identical on every point: six GEN_TEST_PHASE lines, all idx=0 at cycles
60-65; zero idx>0 lines; the same "fire_schedule_applied ok=False reached 11 of 14 scheduled entries by EOT ... applied 6,
missed [... @c709 ..., @c11563]"; GEN_TEST_SCHED shows the derived schedule with entries at c0, c709 and c11563; no
dispatcher refusal at either sha. So the cause is the 3e template's schedule runner (7ef16a0): the later triggers are
scheduled and logged as reached but never applied. tb-infra's 2a is cleared of this item. Consequence for the record:
the 3e promotion proof "the layers are live" (l9g, 16 seed-1 greens) exercised only the idx=0 batch (six knobs at
start-up), so mid-run regime changes have never run on any test; the promoted tests' measured status does not depend on
it, but no plan item that needs a mid-run regime change is credited until the runner is fixed. Owner: the Test Writer
(landing 3h, with 3g): fix the runner, add a red where a scheduled c-triggered entry is not applied (fail loud on the TB
side as well if the dispatcher was never called), retain a green with idx>0 GEN_TEST_PHASE lines and re-run the 13
failing acceptance seeds; round 0 dispatches after 3h is committed and reviewed.

## LOG-042b - 2026-09-03 - RULING (plan hold for the schedule-runner defect, Section 1.6)

Until the Test Writer's 3h (the 3e schedule runner applying mid-run phases, with a red and a green showing an idx>0
phase) is committed and reviewed, the plan holds every item whose stimulus depends on a mid-run regime change: the
union of a group rule (Test group gen_reg_* or *regime*; preview 71 items in 11 groups, none promoted for round 0) and a
stimulus-text rule (Stimulus or Preconditions name a mid-run regime change, a layer-3 schedule phase or a knob switched
during the run, in the plan's own vocabulary); not every Phase-2 item. The DV Lead emits the hold as Section 0 bullet
T-181 and a generated Section 1.6 whose heading prints the group count, the text count and the union; the hold lifts
by removing both in the revision that cites the reviewed 3h commit. Round-0 crediting is unaffected by this hold.

## LOG-043 - 2026-09-03 - WATCHDOG (Test Writer instance stopped and respawned)

The Test Writer's STATUS.md stayed at 16:03Z; its last file (batch3/gen_pmp_mseccfg/regen_check/red1.S) is from 16:38Z;
four Orchestrator messages since 16:04Z (the 3g hand-off request, the T-181 triage lead, the bisect fact, the LOG-042a
ownership) went unanswered; nudged at 16:46Z, still silent at 16:54Z with no new file for 16 minutes: stopped and
respawned under the same name with the common briefing, the role section, the team rules (10-minute STATUS from date -u,
answer within one tool round, LOG-029/034/036/036b/024d), the inherited state (3e/3f committed; 3g uncommitted in the
tree with the working-tree manifest self-test passing; batch-3 gen_pmp_mseccfg files from a subagent; gen_pmp_lock brief)
and the work order: 3g hand-over, then 3h (the schedule-runner fix, LOG-042a, the critical path for round 0), the CR6-L
lows, the acceptance re-file, then batch 3. Fourth respawn of the day; the pattern is again a long foreground fan-out
with the inbox unread.

## LOG-037d - 2026-09-03 - HOLD CONDITIONS REFINED (Critic fu2a on landing 2a)

The Critic's check of landing 2a (dv/auto_dv/docs/gen_critic_tb_fu2a.md, REQUEST-CHANGES on one high and five mediums)
reaches the same two hold answers as the cross-model artifact and refines the T-137 condition: T-136 does NOT lift
(the fold still returns before publish_state; the landed build's own green shows irq_entries=15 against cause checked=0);
T-137 lifts with the one-line take() change (both words of a spanning access consumed), its announced-minus-taken referee
and a red, because P13 (the model losing pmpaddr0 -> isa_trap, 20 catches, ablation 0) is accepted as the committed-tree
proof of the LOG-026a arming form; the MB6 re-run on the committed sha then closes the record, not the hold. One new
owed item with conditions: the irq_entry bound now restarts at every entry, so under a storm a raised line that is never
taken is never flagged while priority is undecidable for 448 of 573 entries (Critic M-5); tb-infra states the bound's
intent and a rule that flags a never-taken raised line at end of run, in 1c or explicitly owed to 2b with the
decidable-only crediting condition of LOG-037b. The promotion check (docs/gen_critic_flow_promotion.md) upholds LOG-039
and the lowest-tier rule; its high is closed by Runtime's T-178 (7a468ec), and its lows ask that the tier table be a
committed file and that the two unmeasured smoke entries carry a one-line reason.

## LOG-042c - 2026-09-03 - ROOT CAUSE (schedule runner: the EOT wait ended at the first report-word store)

The respawned Test Writer found the T-181 root cause from Runtime's bisect probe log: GenTest._edge_or_eot in
gen_test_template.py treated the first store to the EOT register as the end of test, while report words store
through the same register (gen_bridge_if.sv toggles evt_eot_seen on every store), so the schedule runner exited at
report 0 (cycle 289) before the first mid-run trigger (c709); the dispatcher was never called for idx>0 (exactly six
[GEN_PHASE] dispatch lines, no REGIME_SET after cycle 65). Consistent with the wave: all 13 failures carry only
fire_schedule_applied, and the 11 passes are seeds whose mid-run triggers fell after the program's end. Fix in landing
3h: the wait ends only when the store count reaches the final store; red, mutation red, green with idx>0 phases and the
13 acceptance seeds re-run on a HEAD export follow. tb-infra is clear of T-181.

## LOG-036c - 2026-09-03 - RESOLVED (manifest self-test green again at 5816601)

Landing 3g (5816601) retargets the manifest generator's rule (f) case to any still-marked item with a CG-WIT-001 bin
and makes the library self-test run the manifest self-test as a subprocess. Verified by the Orchestrator from a
detached checkout with no environment variable: both self-tests PASS. The red window on the manifest self-test ran
from d0e6a71 (15:58Z) to 5816601 (17:05Z).

## LOG-037e - 2026-09-03 - Priority-item credit rule and L-7 (Critic fu2a Section 6 adopted)

The Critic's answers to the two fu2a questions (gen_critic_tb_fu2a.md Section 6, committed 35e74c6) are adopted as
rulings. (1) The NMI emulation and the nmi_internal rule are intent-derived for their semantics from
doc/03_reference/exception_interrupts.rst, with the controller's pending-bit mechanics as the permissible internal
anchor; the latency bound of 4 records and the counting of debug-mode records are DUT-tuned, not intent-derived, and
must be anchored to a document statement or declared as TB-side bounds with their origin stated (L-7, tb-infra,
T-189). (2) Interrupt-priority items are credited only from directed or sparse cases in which the contending lines do
not move inside the checker's decision window; the storm test never credits a priority item (448 undecidable claims);
the checker publishes per-entry decidability so a priority item's fire check can assert its own entry was decidable;
the cause of the decidable share rising from 40 to 78 percent is stated in the TB doc. The plan's credit rule carries
the same sentence (DV Lead, T-190). The LOG-037b condition on T-137 is unchanged.

## LOG-042d - 2026-09-03 - RESOLVED (round 0 released on landing 3h)

Landing 3h (9500268) is committed and its cross-model review is APPROVE (reviews/2026-09-03-claude-diff-3cc1fe78-9500268b.md):
the schedule runner's wait ends only at the program's final store, a pre-fix red reproduces the probe's numbers, a mutation
red fails loud after the fix, and the 13 batch-2 acceptance seeds pass with mid-run phases applied. The LOG-042 hold on round
0 is lifted: Runtime dispatches round_0 head-mode from e8ac866 (plan of record fd632aa, tests at 9500268) behind the recorded
canary-vs-pinned hold; rtl-arch's pass 14 runs on the committed round evidence under dv/auto_dv/evidence/gen_round_0/. Results
that need an interrupt-enabled regime, a PMP-denial or bus-error regime, an integrity-error regime, or the T-137 comparator
remain uncredited (LOG-025, LOG-026a, LOG-037b); the round measures them for consistency only until T-136 and T-137 lift.
Two lows from the review (cite the committed testlist in gen_tdd_batch1.md Section 10; record the template sha256 in future
pre-fix red headers) ride with the Test Writer's next touch.

## LOG-044 - 2026-09-03 - Critic plan witness v9 REQUEST-CHANGES: scope of the gate

The Critic's v9 verdict on plan v2p parts 1 and 2 (gen_critic_plan_witness_v9.md) is REQUEST-CHANGES on three mediums:
the promotion table's held-items column omits TP-CSR-029 (7 held items over 5 groups, T-136: 6, not 6 over 5); the Section
1.6 stimulus-text rule is stated nowhere in the plan, so the 37 text-rule rows are not regenerable by a reader; the four
Notes bullets split multi-line Pass criteria bullets (closed at fd632aa, plan v2q). Ruling: the gate applies to crediting,
not to measurement. Round 0 dispatches as released in LOG-042d and its results are retained as evidence; no plan item is
credited from round 0 until the DV Lead lands the held column generated from Sections 1.4 and 1.5 and the stated text-rule
vocabulary that reproduces exactly the 37 rows, and the Critic's re-review reaches APPROVE or APPROVE-WITH-CHANGES. The
crediting revision (v2r) carries both fixes and the CR9 rows.

## LOG-042e - 2026-09-03 - T-181 measurement hold may lift (landing 3h passed both reviews)

Landing 3h (9500268) is APPROVE from the cross-model reviewer and APPROVE with three lows from the Critic
(gen_critic_batch1_v7.md): the fix is at the cause, the final-store count is a TB-side fact (the program plan's report
count), both reds are verified from the retained logs on one build, and the 13 seeds pass with applied equal to reached.
Ruling: the T-181 hold (LOG-042b, Section 1.6) may lift; the DV Lead lands the lift in v2r part 1 with the Critic's
caveats stated beside it: a seed whose mid-run triggers all fall after the end of test passes with no mid-run phase
applied, so a mid-run bin can stay unhit on a PASS and the fcov gate is where that shows; the 82 held items are in
unbuilt groups, so the lift credits none of them today; Runtime's head-mode wave on 9500268 (13 of 13 PASS, 17:22Z) is
the record LOG-042 asked for and preceded the round-0 dispatch. Lows to the Test Writer's next touch: an edit-ablation
control for mutation 3h-M1 on the same seed; CR6 rows for the v6 lows; the Section 10 testlist citation (CM30-L-1).

## LOG-045 - 2026-09-03 - RTL mutants found applied in the shared working tree (reverted)

At 17:37Z the Orchestrator's committer boundary check found rtl/ibex_core.sv and rtl/ibex_load_store_unit.sv modified in the
shared working tree (mtimes 17:36:54Z and 17:37:17Z): three mutants whose own comments read "RM1/RM2/RM3 (out-of-tree RTL
mutant)" (core_busy_o forced to 1'b0; rvfi_halt tied to rvfi_valid; data_tag_o driven high). DV never modifies RTL in this
clone and no shared-tree window had been announced. The Orchestrator saved the diff and restored both files from HEAD at
17:38Z (git status of rtl/ clean at 17:39Z). Runtime's head-mode round 0 (git archive of 37c7ecb) and the Test Writer's
HEAD-export runs cannot have seen the mutants; the presumed owner is tb-infra's landing-2b protocol-bind mutation work, whose
mutant edits belong in its out-of-tree copy. tb-infra is asked to name the script that wrote into the shared tree and any
build that compiled it inside the window; results of such a build are discarded. Rule restated: every mutant edit and build
happens in an out-of-tree copy; the shared tree carries committed RTL only.

## LOG-045a - 2026-09-03 - RESOLVED (cause of the shared-tree RTL mutants)

tb-infra's account: its mutation driver mut_oot_rtl.sh copied the rtl directory of a scratch copy whose rtl entry was a
symlink to the clone, so cp -r reproduced the symlink and the RM1..RM3 mutant edits went through it into the shared tree
(17:36:33Z to 17:39:28Z). tb-infra detected it from the driver's start/end sha lines and restored both files from HEAD
(read-only git show redirected) at 17:39:28Z, concurrently with the Orchestrator's restore at 17:39:16Z; both files equal
HEAD. Impact: no build compiled the shared tree in the window (out_l1c was built at 17:29Z; landing 1c's evidence stands);
the RM1..RM3 results are re-run from a real rtl copy and the tainted ones are not cited; the agent-side mutants MUT-M/MUT-N
ran before and stand. Standing fix: the copy step dereferences and refuses a non-private rtl directory, and the driver
compares its own start/end shas. Runtime asked to confirm no worktree-source compile in the window.

## LOG-046 - 2026-09-03 - Round 0 refused: the TB implements no covergroup; probe record only; covergroups become the TB's top item

Round 0 (dispatched 17:29Z head-mode on 37c7ecb behind canary 9110052, LOG-042d) finished at about 17:41Z with 47 runs: 2 PASS
(gen_boot_zc and gen_ut_lockstep, the entries without manifests) and 45 FAIL, 44 of them "fcov expectation unverifiable:
per-test urg report has no grpinfo.txt (no covergroup in this vdb)" with covergroups_exist false, and one gen_test_csr_reset
run failing on cocotb_summary (sim_stdout.log:112). The Orchestrator read the manifest. Cause, confirmed by the DV Lead from
git grep: the TB carries no SystemVerilog covergroup at HEAD, so every promoted manifest declares bins nothing implements and
the checker refuses to verify them, which is the intended behaviour of the manifest-required policy (LOG-039, T-178).
Ruling: gen_round.py's clean rule stands; round 0 as run is refused, with no round evidence and no index entry; Runtime
retains it as a probe record under dv/auto_dv/evidence/gen_round_0_probe/ (T-207) stating that nothing is credited from it;
the plan's crediting tool reports every hosted item UNVERIFIED. The functional half of the Phase 1 gate cannot be measured
until the covergroups referenced by the 16 promoted manifests exist: the DV Lead commits the minimum referenced set ranked
by bins (T-204); tb-infra implements them with CG-WIT-001 as the core of landing 2b after the T-162 binds, in reviewable
slices, misc rules and dbg_dret moving to 2c (T-205); no purpose-4 regression is dispatched meanwhile; acceptance waves
continue. Round 0 is re-declared on the first HEAD whose TB implements the referenced set. The csr_reset failure is a
separate triage (T-206, Test Writer). Owner notice: the Phase 1 gate's functional-coverage half slips by the covergroup
implementation time; the code-coverage probe of 37c7ecb is retained.

## LOG-047 - 2026-09-03 - Response-row ids are frozen once a committed review artifact cites them

Ruling recorded for the record (given in the 3g relay, referenced by the CM3e heading of gen_critic_response_batch1.md): a
response-row id becomes frozen the moment a committed review artifact cites it. The Test Writer's CM3e-* rows stay CM3e-*
because reviews/2026-09-03-claude-diff-a5f03ff5-1cbbcfcd.md cites "CM3e-I-1"; no relay number replaces them. New rounds get
a fresh prefix assigned by the Orchestrator per artifact; roles never renumber their own rounds.

## LOG-046a - 2026-09-03 - Round 0 follow-up rulings (flow)

Runtime's account adds a second cause: the round's relative --elfile (dv/auto_dv/excl/gen_exclusions.el) reached urg
unresolved with the coverage directory as cwd (URG-OFR file not found) and gen_regress checked the file's existence nowhere
before the first job, so the merge failed after the full pass. The test-side failure is gen_test_csr_reset seed 1028791296,
a runaway program (end-of-test store 1 of 89 not seen within 16 x 100000 cycles while the core kept retiring), not the
fcov class; it is the Test Writer's triage (T-206). Rulings on Runtime's proposals: (A) rejected as proposed: a measured run
with a manifest whose expectation cannot be verified stays FAIL (LOG-039, honesty over green); relaxing it to a
NO_COVERGROUPS status would let a TB with no covergroup produce indexable rounds. (A') accepted instead: gen_build records
covergroups_compiled from the compiled SV set, and gen_round refuses to dispatch a measured round when the canary build's
covergroups_compiled is false, so the gap is caught before a 700-second pass rather than after. (B) accepted: relative
elfiles resolve against the pinned source root and a missing elfile is refused before the first job. A' and B land as one
reviewed flow touch (T-208) before round 0 is re-declared; the refused run is recorded as a probe (T-207), never as round 0.

## LOG-042e-note - 2026-09-03 - where the T-181 lift landed

LOG-042e says the DV Lead lands the lift in v2r part 1; part 1 (ce21d32) was committed from an earlier list before that
ruling reached the DV Lead, and the lift landed in v2r part 2 (e93c880). No content consequence.

## LOG-048 - 2026-09-03 - Orchestrator error: a review launched with an unverified reproduction claim (killed, relaunched)

The first cross-model review of plan v2r part 3 (43b47da..79ef3fa, 18:03Z) was launched with a REVIEW_FOCUS stating that the
promotion table's header command "leaves it byte-identical", derived from a check whose command string had been mis-parsed
from the header (the tool exited 2 without regenerating, so the "0 files changed" result was vacuous). The Orchestrator
noticed within a minute, killed that review, removed only its run directory, re-ran the exact header command
(python3 dv/auto_dv/tools/gen_promotion_table.py --plan-sha 43b47da) from a detached checkout of 79ef3fa (rc 0, table
byte-identical), and relaunched with the verified text. No artifact from the first launch exists. Rule restated (LOG-040
class): a focus claim is written from a reproduction's exit code and output, never from a derived count.

## LOG-051 - 2026-09-03 - T-136 lifted; T-137 lifted for bus-error arming; LOG-044 crediting gate lifted

Landing 1c (9e912bb) has passed both reviewers: cross-model APPROVE-WITH-CHANGES (two comment-level lows) and the Critic's
gen_critic_tb_l1c.md APPROVE with six lows. The Critic read the retained evidence first-hand: entry state is published once
inside the fold block and two unconditional report-time referees fail a stepped-but-unseen entry (pre-fix red, green 15/15,
mutant RC1 caught); the vectored cause is checked for every entry through the pending-and-enabled set; one announcement is one
cycle-stamped event with take() consuming the oldest entry of each word and the bus_err_leftover referee (RM-L1 red, 61/61
green); the mutation batch re-ran from the final sources with per-mutant build shas equal to the committed blobs. Rulings:
T-136 (LOG-025) is LIFTED: interrupt-enabled results are credited under the plan's crediting rule. T-137 (LOG-026a) is
LIFTED for bus-error arming; integrity-corruption results that rest on a suppressed register write stay uncredited until
T-183 (rf_wr_suppress gated on an announced corruption) lands and passes review, and the pre-empted rule stays counted only
until its t.intr fix lands (both owed to tb-infra's 2c per gen_critic_response_fu2a.md). The DV Lead applies the lifts in
plan v2r part 4 with the T-183 carve-out named item by item. Plan witness v10 (ce21d32 with e93c880) is APPROVE with two
adopted lows already closed in parts 2 and 3, so the LOG-044 crediting gate is lifted; crediting still yields nothing until
a clean measured round exists (LOG-046). The Critic's six 1c lows (unretained figures, the asserted drain window, the
grant-cycle comment, the intg slot outside the leftover referee, the shim's tval-0 gap, MUT-K's without-export run, the
stale gen_rvfi_pkg.sv:338 comment) go to tb-infra's 2c with the CM33 lows.
