# Critic: dv-principles conformance check of TB build step 1b (T-064)

Artifacts under review (HEAD 96cca9c; step 1b landed in efe2a3e; sha256 first 16 hex of the HEAD blob):
- dv/auto_dv/tb/gen_tb_top.sv e9a81e7ab09fe1ad | gen_bridge_if.sv 335fe501d6c769cd | gen_tb.f bae578c302ef6d1c |
  gen_tb_local.sh ccde2a293ca24c76 | gen_env_cfg_knobs.svh 5b3bfa0fac01f0c9 (rendered)
- dv/auto_dv/env/gen_env_pkg.sv 0f4255c3a98724b9 | gen_mem_pkg.sv f5d1f684db3a0f52
- dv/auto_dv/gen_tb/gen_handles.py 11db7da8fdbc6d10 | gen_bridge.py 86a11d5bd9144143 | gen_tests/gen_ut_bridge.py
  533c45dcb5a8ff16 | gen_tests/gen_ut_bridge_neg.py 654bfd33a9fde787
- dv/auto_dv/tb/unit/gen_ut_handles.py 516c172ab3328f69 | unit/gen_ut_mem_model_top.sv f858bad243ce0e4a
- dv/auto_dv/evidence/gen_tdd_bridge.md 1bdf8150df0bd1cf | gen_tdd_mem_model.md e781db162a870a50
- dv/auto_dv/docs/gen_component_api_bridge.md 39e6674271ce86b7 | gen_component_api_tb_top.md ef29686c8f9b8b8d
Working tree at review time: gen_bridge_if.sv, gen_env_cfg_knobs.svh, gen_handles.py and gen_tb_knobs.yaml differ from
HEAD and gen_tests/gen_ut_boot.py is untracked (step 1c in progress). This verdict judges HEAD.
Date: 2026-09-03 (UTC)
Role: Critic (dv-principles conformance per the dv-principles-check skill: docs/dv/dv_principles.md read fresh, sections
cited; docs/dv/TB_CONTRACT.md Sections 2-4 as the Orchestrator asked; general code quality left to the review rubrics)

CRITIC VERDICT: REQUEST-CHANGES

The step is well built and honestly evidenced: the cocotb-master handshake exists in all three TB_CONTRACT forms and each
was forced red once with retained, distinct logs; Python waits only on edges; hierarchical names live in one module;
plusarg names come from the rendered package; the memory model reproduces the image digest and was unit-tested red
first. One medium keeps it from approval: the `uvm_error` failure path, the mechanism every DUT checker from step 1c on
will use, has not been forced red, and its dangerous form (cocotb reports PASS while UVM_ERROR is non-zero) has not been
shown to fail through the flow's verdict. Six lows follow; step 1a's P-01..P-03 remain open at HEAD and ride with 1c as
agreed.

## 1. TB_CONTRACT Sections 2-4

| Contract item | Where | Status |
|---|---|---|
| 2.1 alive-bit watchdog, `$fatal` in hardware | gen_tb_top.sv:180-187 (budget from PLUSARG_ALIVE_TIMEOUT, default GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT); gen_bridge.py:27 sets alive first | met; forced red neg_noalive (Section 3) |
| 2.2 objection holder / active flag | gen_bridge.py:30 stim_active = 1 after listener_armed; gen_env_pkg.sv:192-197 objection held until finish_req and !stim_active | met; see L-1 on the drop order |
| 2.3 finish with caller-sized timeout | gen_bridge.py:66-74 awaits the finish_ack edge with a budget (default GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT, override per test); gen_env_pkg.sv:200-203 toggles finish_ack in final_phase, after the UVM report; finish_on_completion = 0 (:188) | met (edge-await rather than polling, which is better than the contract's minimum) |
| 2 ordering: checks before the finish handshake | gen_ut_bridge.py:24-29 asserts before finish(); gen_bridge.py:69-73 drops stim_active, asserts cmds_consumed, then raises finish_req | met in effect (finish_req follows the assert); L-1 on the letter |
| 3 failure path: Python assert only; SV uvm_error/uvm_fatal; each proven red once | gen_bridge.py raises AssertionError on every timeout and on seq/consumed mismatch; gen_env_pkg.sv uvm_fatal GEN_UNKNOWN_PLUSARG (:148), GEN_BAD_KNOB (:159), uvm_error GEN_BRIDGE on MEM_PEEK without a model (:76); gen_mem_pkg.sv MEM_LOAD fatal, MEM_UNMAPPED error | $fatal, uvm_fatal (twice) and Python assert forced red; uvm_error NOT forced (M-1) |
| 4 ASCII-only logging | gen_handles.py, gen_bridge.py messages ASCII; gen_ut_handles.py:51 asserts the message is ASCII | met |

## 2. Principle walk (docs/dv/dv_principles.md)

| Artifact | Section | Finding |
|---|---|---|
| gen_tb_top.sv | S1 realistic drive | DUT inputs tied idle for step 1b only, stated in the header (:4-5); boot_addr from the plusarg (:57-62); config banner from gen_dut_top plus the TB banner (defines SIMULATION/COCOTB_SIM, seed, knobs) | conformant for this step; L-3 hart_id |
| gen_tb_top.sv | S1 future-proof counts | widths derived from ibex_pkg (IC_NUM_WAYS, IC_INDEX_W, BUS_SIZE, IC_LINE_BEATS) or mirrored from the DUT's own port declarations (irq_fast [14:0], mhpmcounters [10]) | conformant |
| gen_bridge_if.sv | S2 place the check where the failure lands | threshold engine latches on the arm edge and hits on the first cycle at or beyond the target (:59-72); counters reset with rst_n | conformant; per-threshold bits (N-02) |
| gen_env_pkg.sv gen_bridge | S2 fail through a collected mechanism | MEM_PEEK without a memory model is `uvm_error`, never a silent 0 (:75-78) | conformant in code; unproven (M-1) |
| gen_env_pkg.sv gen_base_test | S5 declared-once plusargs, S2 collected failure | names checked against gen_is_known_plusarg (rendered), unknown -> uvm_fatal; enum values validated -> uvm_fatal; both forced red | conformant |
| gen_env_pkg.sv gen_cmd_item | S5 single source | kind_name() re-types the command names as string literals (:36-46) that the yaml already defines | I-1 |
| gen_mem_pkg.sv | S2 end-to-end, S5 single source | digest reproduces gen_elf2mem.checksum() and is checked against the real sidecar; regions from the rendered GEN_MM_* constants; unmapped access errors unless the knob allows | conformant |
| gen_handles.py | S5 one Python handles module | the only file spelling hierarchical names; fails loud with the path on a missing handle (unit-tested) | conformant |
| gen_bridge.py | S1/A-01 no polling, S5 constants | every wait is an edge with a timeout; CMD codes and the clock period from gen_knobs.py | conformant; L-1 |
| gen_ut_bridge.py | S5 hygiene | all handles through GenHandles (h.b.*) | conformant (the Orchestrator's concern does not apply to this file) |
| gen_ut_bridge_neg.py | S5 hygiene | `dut.clk` used directly (:11) outside gen_handles.py | L-2 |
| gen_ut_handles.py | S5 comments intent-only | docstring narrates history ("Written before the module existed") | I-2 |
| gen_tb_local.sh | S5 single source; S6 evidence | plusarg name read from the package (sv_string); summary columns for cocotb pass/fail | L-4 |
| gen_tdd_bridge.md, gen_tdd_mem_model.md | S4 honesty, S6 TDD | compile defects and the wrong test expectation disclosed; red before green for handles, bridge (stubbed), memory model | conformant; Section 3 |
| step 1a files | S5 | P-01 (unknown yaml keys, 4 spurious), P-02 (re-typed derived values), P-03 (--check mutation) unchanged at HEAD | open, riding with step 1c per the Orchestrator |

Trust triad for this step: TDD met for all three components (Section 3). Mutation-proof: the new checks are TB
self-checks (alive watchdog, unknown plusarg, bad knob, bridge accounting, digest verification) whose forced-red runs
and the digest-rejection checks serve as their proof; no DUT checker exists yet. fcov-expectation: not applicable (no
covergroup, no regression test).

## 3. Transcript audit (four-point rule: retained artifact, path, mtime, in-log stamp; local time -0400)

| Claim | Artifact | mtime | In-log identity | Result |
|---|---|---|---|---|
| handles red 07:26:25Z, green 07:28:02Z | tdd/handles_red.log, handles_green.log | 03:26:25, 03:28:02 | stamped headers, FAIL 1 / PASS | consistent; my own run: PASS |
| bridge red on a stubbed gen_bridge (compile out_1b_red vcs exit 0) | out_1b_red/compile.log, ut_bridge_red/sim.log, tdd/bridge_red.log | 03:32:05, 03:32:09, 03:32:58 | 0 Error lines; VCS stamp Sep 3 03:32; "no edge on listener_armed within 2000 cycles"; stub retained as tdd/gen_env_pkg_full.sv | consistent (the excerpt carries no UTC header; the Command line identifies it) |
| bridge green (fresh compile out_1b) | out_1b/compile.log, ut_bridge_green/sim.log, stdout.log | 03:33:35, 03:33:37 | 0 Error lines; finish_req at cycle 73, 6 commands; UVM Report Summary UVM_ERROR 0 / UVM_FATAL 0; stdout TESTS=1 PASS=1 FAIL=0; GEN_UT_BRIDGE_PASS | consistent |
| neg_noalive, neg_unknown_plusarg, neg_bad_enum | out_1b/<run>/sim.log | 03:33:40, :42, :44 | distinct md5; GEN_ALIVE_TIMEOUT / UVM_FATAL GEN_UNKNOWN_PLUSARG / UVM_FATAL GEN_BAD_KNOB; UVM_FATAL : 1 summaries; stdout FAIL=1 | consistent |
| mem model red compile 07:31:10Z | out_ut_mem/red_compile.log, tdd/mem_model_red.log | 03:31:14 | Error-[SFCOR] gen_mem_pkg.sv cannot be opened, vcs exit 255 | consistent |
| mem model green 1 (one wrong expectation) and green 2 PASS 25 | out_ut_mem/green_compile.log + sim.log, green2_compile.log + sim2.log, tdd/mem_model_green.log | 03:33:40-41, 03:34:24-26 | FAIL 1 then PASS (0 failures) | consistent |
| driver summary out_1b/runs_summary.txt | same | 03:38:35 | cocotb_pass=0 cocotb_fail=0 for ut_bridge_green and for the negatives, although stdout.log:57 holds "TESTS=1 PASS=1 FAIL=0" and the driver's own grep on the retained file returns 1 today | summary unreliable (L-4); the transcript quoted the logs, not the summary |
| boot_red (gen_ut_boot, 03:38:35) and out_ut_mem/red2_compile.log (03:39:43) | present | after the landing | step 1c work in progress; not judged here |

## 4. Findings

M-1 (medium) [S2 "fail through a mechanism the flow actually collects"; S6 "a check never exercised to fail is not
trusted"; TB_CONTRACT Section 3 "prove each failure path once"]. Three of the four failure mechanisms are forced red
(the `$fatal` watchdog, `uvm_fatal` twice, the Python assert via the stubbed bridge). `uvm_error` is not: the only
step-1b instance, MEM_PEEK without a memory model (gen_env_pkg.sv:75-78), was never driven, and no run shows the form
that matters most for a cocotb-master TB, where Python finishes cleanly (TESTS=1 PASS=1) while the UVM report carries
UVM_ERROR > 0. That run must FAIL through the flow's verdict (gen_verdict.py: uvm_error_count), not only be visible in
the log; the green log shows the UVM Report Summary is printed under finish_on_completion = 0, so the count is
available. Required: one forced-red run (a MEM_PEEK command from a test that otherwise passes) retained under the
tdd/out tree, quoted in gen_tdd_bridge.md with its UVM_ERROR summary line and stdout PASS line, and the flow's verdict on
that log (FAIL, reason uvm_error_count) recorded. This may ride with the step-1c landing, before the first DUT checker.

L-1 (low) [TB_CONTRACT Section 2 item 2 and ordering rule] gen_bridge.py:69-71 drops stim_active before asserting
cmds_consumed == sent. The effect is harmless today because finish_req is raised only after the assert, but the
contract's letter is "drop stim_active only after its own checks have completed". Reorder: assert, then stim_active = 0,
then finish_req.

L-2 (low) [S5 one Python handles module] gen_ut_bridge_neg.py:11 uses `dut.clk` directly. Resolve through
GenHandles(dut).clk (the module exists precisely so a rename fails in one place). gen_ut_bridge.py is clean: every
access goes through h.b.*.

L-3 (low) [S1 "if it's a config, program it"; architecture C1] gen_tb_top.sv:141 ties hart_id_i to the literal 32'd0.
C1 lists hart_id_i as a knob with default 0 and the yaml has no hart_id entry. Add the plusarg (rendered) or amend C1.

L-4 (low) [S6 evidence over inference] gen_tb_local.sh:55-58 records cocotb_pass / cocotb_fail from a grep run right
after the simv subshell; the retained runs_summary.txt shows 0/0 for a run whose stdout.log line 57 says PASS=1, and
for the negatives whose stdout says FAIL=1. The cause was not determined (the same grep on the retained file returns 1
now). A summary that disagrees with its logs is worse than no summary: derive the columns after the logs are complete
and verified non-empty, or drop the two columns and let the transcript quote the log line, as it already does.

L-5 (low) [S6 artifact rule] The bridge red excerpt in gen_tdd_bridge.md Section 2 and tdd/bridge_red.log carry no UTC
stamp header (the other transcripts do); the VCS run stamp (Sep 3 03:32) and the Command path identify it, so it passes
the audit, but the header convention should be uniform.

L-6 (low, status) Step 1a P-01..P-03 are unchanged at HEAD: the yaml still parses with four spurious keys, load() still
accepts unknown keys, the unit test still has no --check mutation, GEN_IBUS_MAX_OUTSTANDING and GEN_IRQ_FAST_MASK are
still re-typed for Python/C. Riding with step 1c per the Orchestrator; the step-1a response file
dv/auto_dv/evidence/gen_critic_response_tb_step1a.md does not exist yet.

I-1 (info) [S5] gen_env_pkg.sv:36-46 kind_name() re-types the eleven command names the yaml defines; render the name
table with the codes or accept the duplication with a comment. I-2 (info) [S5] gen_ut_handles.py:3 docstring narrates
history. I-3 (info) The TB banner does not print boot_addr; gen_dut_top's banner does not either (it prints the
parameters). One of them should, since +gen_boot_addr changes the first fetch.

## 5. Correction to my T-061 finding P-07

I wrote that SystemVerilog cannot enumerate the plusargs on the command line, so A-23 would need the argument list from
outside SV. gen_base_test.check_unknown_plusargs (gen_env_pkg.sv:135-150) uses uvm_cmdline_processor::get_args, which
does enumerate them, and the neg_unknown_plusarg run proves A-23 end to end. P-07 is withdrawn; the UVM route is right.

## 6. Required before re-review

1. M-1: the forced-red uvm_error run with the flow's verdict, retained and quoted (may land with step 1c).
2. L-1, L-2, L-3, L-4 as small edits in the same landing; L-5 convention.
3. Step 1a P-01..P-03 with their response file at the latest in the step-1c landing (already agreed).
4. Response file: dv/auto_dv/evidence/gen_critic_response_tb_step1b.md, one row per finding.

## 7. Method and fence record

Inputs: the HEAD blobs listed above, the retained out-trees out_1b_red, out_1b, out_ut_mem and the tdd/ logs, rtl/ibex_core.sv
port declarations (widths), the two API documents, the flow's gen_verdict.py rules from my T-042 review. I ran the
handles unit test myself (PASS) and the driver's cocotb grep on the retained stdout (L-4). No VCS compile or LSF command
by me; no fence event.
