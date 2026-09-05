# Critic verdict: irq-step1-samplers (the dbg_dret checker fix; four IRQ covergroups on one published sampled view)

Range e1bee86..4b5730e, named by the Orchestrator; the group is e1bee86 (tb-infra-2's dbg_dret checker fix with its
red and mutant), d09ff58 (the DV Lead's CG-IRQ-001 cr_upath_pending plan line) and 4b5730e (tb-infra-2's landing 43).
The other commits in the range belong to groups already judged (pmp-step1 at 2897920), to the irq-entry group pending
its own range, or are records; the plan touches 109b654 and 1bd7439 are read here only where the four covergroups'
definitions rest on them.
Artifacts at 4b5730e (sha256 first 16 / lines):
- dv/auto_dv/env/gen_fcov_groups.svh (the four covergroups appended at :5206, :5321, :5392, :5460; 33 rendered),
  dv/auto_dv/env/gen_fcov_pkg.sv (+535: the samplers), dv/auto_dv/tb/gen_fcov_codegen.py (+99), dv/auto_dv/tb/unit/
  gen_ut_fcov_codegen.py (+14, five cases), dv/auto_dv/tb/gen_tb_pkg.sv (+59: gen_irq_view, gen_fetch_en_windows),
  dv/auto_dv/tb/gen_tb_top.sv (+1: the misc_vif publish), dv/auto_dv/env/gen_env_pkg.sv (+1: ap_state -> isa_cov),
  dv/auto_dv/env/gen_checkers_pkg.sv (+17/-10: the checker reads and writes the published view),
  dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l43_irq_step1_covergroups.log (140), gen_tdd_step2b.md (+58),
  gen_tdd_logs/gen_manifest.md (+1).
- e1bee86: dv/auto_dv/env/gen_checkers_pkg.sv (+13/-1), gen_tdd_logs/lockstep/gen_fu_l42_dbg_dret_entry.log (86),
  gen_tdd_logs/mutations/gen_fu_l42_MUTMEPCSKEW1_mutant.diff (11), gen_tdd_step2b.md (+31), gen_manifest.md (+2).
- d09ff58: dv/auto_dv/docs/gen_fcov_plan.md (1 line).
Judged against: LOG-096 and its checklist; the trust triad for the checker fix (dv_principles.md Section 6); the plan at
4b5730e (CG-IRQ-001, 003, 010, 011 sections); the RTL at the cited lines; docs/dv/dv_principles.md d9c27db18f511411
(read fresh; skill dv-principles-check).
Date: 2026-09-05T07:15:09Z   Role: Critic
Method: detached worktrees of 4b5730e, d09ff58 and e1bee86 in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/irq1/); the codegen check and unit test run by me in both directions; gen_norm_probe run on the
three trees and its refusal census diffed line by line; gen_unbuilt_mark_check and both identity recipes run on 4b5730e;
the mutant diff applied dry against e1bee86; EVERY bin classifier of the four covergroups read in gen_fcov_pkg.sv and
traced against the plan's words and the RTL terms it rests on (the rule the pmp-step1 Majors taught). The range review
rev51 was NOT read before Sections 1-5 were drafted; its artifact (in the working tree, uncommitted at the time,
sha256 71f2d4001fc47e03, 63 lines) was then read, and its five Majors and eleven Minors were each verified by me against
the sampler, the interface, the RTL and the plan at 4b5730e (2026-09-05T07:18:38Z) and adopted where they held: every Major held. My
own classifier trace had confirmed the sample events, the cause and priority maps, the CSR-save terms and the pending
model, and MISSED five classifier defects (a line-indexed pin vector compared with a bit-positioned CSR, two compares
against boot_addr where the RTL's reset pc is boot_addr + 0x80, two rendered bins no return value ever produces, and a
window decided by the wrong fetch). The verdict changed from the drafted APPROVE to REQUEST-CHANGES confined as stated
at the end. Exposure: the Orchestrator's naming message summarised the group and named the census figures.

## 1. The checker fix (e1bee86): the trust triad, complete and retained
The dbg_dret rule required the record after a dret to be at dpc in the mode dcsr.prv names; a legitimate interrupt
taken at the dret target (the plan's own cp_post_exit.taken_before_first_insn) was called a mismatch. The fix
(gen_checkers_pkg.sv, non-interrupt branch byte-identical) tests an interrupt-entry record through mepc == dpc instead.
- RED: the committed rule flags order 384 (pc 80000244 mode 3, dpc 8000011e) on gen_ut_dbg with the directed
  interrupt program under a storm regime; the log's arithmetic holds (gen_vec 0x80000200 + 4 x 17 = 0x80000244 is the
  vectored entry of cause 17, fast[1]); 460 records with zero ISA mismatches. GREEN: the fix, same fixture, 0 errors.
- MUT-MEPCSKEW1 (gen_rvfi_pkg.sv publish_state: st.mepc + 4): caught by the NAMED check alone (+gen_chk_all=0
  +gen_chk_dbg_dret=1, one UVM_ERROR "mepc 80000122, dpc 8000011e", the skew exactly); ablation control (the check not
  enabled) 0 UVM_ERRORs and the mutation survives; the reading trap stated (the counter still counts, the enable gates
  the report). The diff applies cleanly to e1bee86's tree (patch --dry-run). No-debug control PASS. The base was
  re-measured on 27212cb after the landing-41 agent fixes and the RED reproduces byte for byte. Build identities named
  per run (outRed 642b5e3a243fd342, outFix f391b509233c88cf, outMut c75ecf93c8ace43d).
- RTL terms behind "a legitimate interrupt entry at the dret target": dret restores pc from dpc and the privilege from
  dcsr.prv; in the next cycle handle_irq (rtl/ibex_controller.sv:498-500, ~debug_mode_q & ~debug_single_step_i &
  ~nmi_mode_q & (irq_nm | (irq_pending_i & irq_enabled))) may take an interrupt before the instruction at dpc retires,
  and csr_save_cause books mepc_d = exception_pc (rtl/ibex_cs_registers.sv:929), the displaced resume point, with
  mstatus.mpie <= mie and mie <= 0 (:924-926). The record after the dret is then the vector in M mode with mepc = dpc,
  which is exactly what the fixed rule tests.

## 2. The plan line (d09ff58) and the census
CG-IRQ-001 cr_upath_pending loses the parenthetical between its component list and the colon. gen_norm_probe (its own
tool on each tree) reads scope 23 at e1bee86 and 22 at d09ff58 and 4b5730e; retired 32, marker 26, guard 1 unchanged.
Between d09ff58 and 4b5730e the "other" class falls 104 -> 69 and "groups with a refusal" 76 -> 59: the 35 lines that
left the census (retained: irq1/census_left_d09ff58_to_4b5730e.txt) are all coverpoints whose iff guard holds a
comparison, which is what the codegen's iff-guard loosening exists to parse; none appeared. The probe's self-test
passes at 4b5730e. The landing's refused first version (a loader tolerance that took scope from 23 to 4) is not in the
tree: gen_fcov_codegen.py:110-112 states the tag and the parenthetical are not tolerated.

## 3. The four covergroups (4b5730e), LOG-096 item by item
1. COMPILE WITH IDENTITY. The retained log names the local compile's TB-source digest 4153c078b0704697; my recipe over
   dv/auto_dv/env, tb, isa and gen_tb at 4b5730e gives the same value, so the smoke tree is the range end's TB source
   set. The gate key at 4b5730e is 9879ca90c6beba35 (gen_build_identity.py; it moved with gen_fcov_pkg.sv and
   gen_fcov_groups.svh, both in gen_tb.f). Four smokes PASS with zero referee errors on that build; the line-sweep
   fixture's arithmetic holds (six lines over five masks: 12 edges, 1 mie access, 1 mstatus set + 6 mrets = 7
   global-enable events; the log reads entry=6 edge=12 access=1 mie_global=7), and the fetchen fixture is the one that
   opens AND closes a fetch-enable Off window (fetch_off=1 there, 0 elsewhere).
2. RENDER AND UNIT TEST. gen_fcov_codegen.py --check: up to date at 4b5730e; 33 covergroups rendered, the four at the
   lines the log states; gen_ut_fcov_codegen.py PASS. Both directions: the new unit test file against d09ff58's codegen
   fails exactly its five new cases (array bin, its base localparam, array element in a cross, an iff guard holding a
   comparison, a parenthesised comment before the colon). The svh diff d09ff58..4b5730e is one appended hunk with no
   deletion: no existing covergroup changed.
3. SAMPLING POINTS AND FIELD SEMANTICS, checked classifier by classifier.
   CG-IRQ-001 gen_irq_entry_cg (irq_entry_sample, :234): one sample per record with is_intr from the scoreboard's model
   of record. cp_line: gen_irq_line_of_cause inverts the mie-bit map (software 3, timer 7, external 11, fast 16 + i),
   the RTL's ExcCauseIrq* lower_cause values, with the NMI cases from ext_nmi_int and ExcCauseIrqNm; cp_priv_pre from
   mstatus[12:11] and cp_mie_global from mstatus[7], the MPP and MPIE the entry books (rtl/ibex_cs_registers.sv:926-927:
   mpie <= mie, mpp <= priv_lvl_q); cp_others from mie and the agent's pin levels with gen_irq_rank matching the
   controller's chain (lowest fast id, then external, software, timer; rtl/ibex_controller.sv:503-511 and the
   exc_cause_o block); cp_mepc_src decided against the record before the entry (sequential = prev pc + 4 or + 2,
   branch/jump/mret/dret/wfi targets, cm_pc), consistent with mepc_d = exception_pc (:929), EXCEPT boot_pc: :210 and
   :220 test st.mepc == cfg.boot_addr while the RTL's reset pc is {boot_addr_i[31:8], 8'h80} (rtl/ibex_if_stage.sv:243;
   gen_tb_pkg.sv:813 says the same) and cfg.boot_addr is boot_addr_i (gen_tb_pkg.sv:22), so boot_pc and
   cr_line_mepc.nmi_ext_boot_pc can never hit (M-3). cp_rvfi_marks (irq_marks_bin, :224) returns five of the seven
   rendered values: pre_post_mip_equal and pre_post_mip_differ (gen_fcov_groups.svh:5216) and the cross bin
   timer_pre_post_mip_differ (:5221) are unreachable by construction although the record carries ext_pre_mip and
   ext_post_mip (M-4). cp_others reads irq_lines_now, the agent's level when the record arrives, not the pins at the
   entry's commit cycle from the view (L-6). cp_u_path and cp_u_pending_at_return passed -1 until CG-IRQ-005 (stated).
   CG-IRQ-003 gen_irq_pending_model_cg: three events. ev_edge pin side (irq_edge_pins, :336) from the agent's event at
   its own cycle with mie from the published view; the pending model is |(pins & mie bits) with the nm line outside it,
   the RTL's irqs_o = mip & mie_q, irq_pending_o = |irqs_o (rtl/ibex_cs_registers.sv:1044-1045); rise_disabled,
   rise_enabled, rise_enabled_other_high, fall_last, fall_not_last, nmi_only_rise as the plan (:2247) words them, an
   unclassified edge sampling nothing. ev_edge mie side (:362) at the write's commit cycle (GEN_CSR_WRITE_TO_RVFI_OFFSET
   before the record). cp_state (:310): debug_mode > nmi_mode (tracked as the checker tracks it) > sleep read from
   core_busy mubi-off at a cycle event (WAIT_SLEEP / SLEEP: rtl/ibex_controller.sv:598, :619 ctrl_busy_o = 0) > step
   (dcsr bit 2, the packed dcsr_t's step field above prv[1:0], rtl/ibex_cs_registers.sv:222-233) > U > mie1_m / mie0_m.
   cp_mip_access (:381): mip writes booked ignored, which the RTL bears out (CSR_MIP appears only in the read mux,
   :495; no write path); reads classified from the pins and mie at the commit cycle. cp_mie_write: the PRESENTED value
   (rs1_rdata or the immediate), the caveat the log states, against the sampler's own WARL mask. cp_mie_global_edge
   (:424): an mret with a pending line (mpie1 / mpie0) or an mstatus write changing MIE, in M mode.
   CG-IRQ-010 gen_irq_debug_interplay_cg (irq_dbg_record, :515): a window opens on a record in debug mode or stepping
   outside it with a line pending (the line class NMI_INT > NMI_EXT > IRQ), closes at a dret or the stepped record
   itself, and is sampled once after the FIRST record after the exit decides cp_post_exit (an entry: taken; the line
   still asserted on an ordinary retirement: not_taken; else undecided into the ignore bin); a window inside an NMI
   handler defers past that handler's mret; an unclosed window is dropped and counted. This matches the plan at
   4b5730e (:2372, "decided by the FIRST RVFI RECORD AFTER THE EXIT ... not by comparing an address to dpc") and the
   RTL: no debug entry nests (enter_debug_mode gated by ~debug_mode_q, rtl/ibex_controller.sv:476), so one window slot
   suffices. cp_dcsr_prv from dcsr[1:0].
   CG-IRQ-011 gen_irq_reset_fetch_en_cg (irq_rst_record, :603): cp_lines_at_reset from the pins latched at release
   (a debug request alone samples nothing, as the plan has no bin); cp_first_event.boot_insn tests st.pc_rdata ==
   cfg.boot_addr (:612) and can never hit, the first retirement being at boot_addr + 0x80 (M-2); cp_reset_reads judged
   against the record's rd_wdata: mstatus 0x80 is the RTL reset value (MSTATUS_RST_VAL: mie 0, mpie 1, mpp U;
   rtl/ibex_cs_registers.sv:1052-1055), mie 0, mtvec on the boot page (mtvec_d = csr_mtvec_init_i, :736-739) hold, but
   mip_reflects_pins (:625) compares rd_wdata[17:0] with pins[17:0], a bit-positioned CSR (MSIX 3, MTIX 7, MEIX 11, MFIX
   16..30, gen_irq_mie_bit) against a line-indexed vector ({nm, fast, ext, timer, sw}, gen_irq_if.sv lines()), so the bin
   hits only when every pin is low (M-1); cp_boot_mret an mret before any trap to U with MIE set. ev_off (irq_off_take,
   :660) TAKES a closed window from gen_fetch_en_windows, published by gen_misc_monitor at the return to On
   (gen_checkers_pkg.sv:538), and classifies cp_fetch_off from the published samples in the plan's order; but
   irq_off_take is called only from irq_pend_record (:462), on a retired record, and irq_off_first_fetch (:670-672)
   ignores fetches while irq_off_open is 0, so the first post-On fetch, which completes before the first post-On
   retirement, never decides cp_fetch_on_after: a later fetch does, and the page compare (:673, addr[31:8] against
   mtvec[31:8]) hides it while also conflating the vector page with the boot code that shares it (M-5).
   The field caveat that decides CG-IRQ-003's design is a TB fact (the checker's sample at an edge cycle holds the
   value before the driver's falling-edge change), so the pin edge alone is taken from the agent's event: stated.
4. UNREACHABLE BINS. The log lists what no stimulus in the tree reaches today per covergroup (CG-IRQ-003 cp_state
   u_mode / step / sleep / debug_mode / nmi_mode and others; the whole of CG-IRQ-010 outside the dbgstorm fixture;
   most cp_fetch_off bins; cp_boot_mret.to_u_mie1) as stimulus statements, not prunes. It does NOT list the bins dead by
   construction that M-2, M-3 and M-4 name (boot_insn and its two cross bins; boot_pc and nmi_ext_boot_pc;
   pre_post_mip_equal, pre_post_mip_differ and timer_pre_post_mip_differ), nor mip_reflects_pins (M-1), which the
   reset group's missing referee (L-5) lets pass silently.
5. MANIFEST CONSEQUENCE. gen_test_irq_basic.fcov.yaml (the Test Writer's, irq-entry group) declares 38 bins on
   gen_irq_entry_cg, now rendered, but also 29 on gen_irq_vector_cg and 4 on gen_exc_trap_csrs_cg, which this step
   does not render (my grep of the svh at 4b5730e); the manifest is not referenced by the testlist, so the DECL leg
   does not judge it today (25 of 27 manifests judged; PASS, 34 rendered incl. the ledger). The landing note does not
   state this consequence for the owning test (L-3).
6. TRUST TRIAD FOR TESTS AND CHECKERS. No test changed. gen_checkers_pkg.sv changed in 4b5730e: the irq checker's mie
   history moves into gen_irq_view (push_mie at :93, clear at reset :73, mie_at :81 delegating), it publishes its
   per-cycle sample (:239) and the fetch-enable window end (:538). mie_at is the same loop (the last update with
   eff_cycle <= c; depth 64) and the writers are the checker alone (the coverage class only reads: gen_fcov_pkg.sv
   :281, :285, :291, :643, :645, :663). The four smokes pass with the refactored checker; no red was re-fired after it
   in the landing's evidence (L-4).

## 4. Conformance (dv_principles.md, read fresh)
PASS with the Section 3 defects carried as rows (Section 4, don't hide failures: bins that cannot hit are reported by the
log as stimulus gaps or not at all). Section 2: the covergroups sample from the model of record and the checker's own view rather than re-deriving
DUT state, and an edge or window the plan does not name samples nothing; Section 4: the log states the two refusals
(the loader tolerance reverted with the measured census, the missing gen_tb_top.sv line found by running from the
handed list) and the pin-edge caveat; Section 5: comments state intent (the codegen's :110-112 rule included);
Section 6: the checker fix carries red, mutant, ablation and control; the codegen fix its two-direction unit test.

## 5. Rows
- M-1 (Medium, environment; tb-infra-2; adopted from rev51 Major 1, verified). gen_fcov_pkg.sv:625 compares the mip
  read-back's bits [17:0] with the line-indexed pin vector; only an all-low pin state can match. Map each pin through
  gen_irq_mie_bit (or build the expected mip from the pins) before the compare.
- M-2 (Medium; adopted from rev51 Major 2, verified). :612 cp_first_event.boot_insn tests pc_rdata == cfg.boot_addr; the
  reset pc is {boot_addr_i[31:8], 8'h80} (rtl/ibex_if_stage.sv:243), so boot_insn, none_boot_insn and regular_only_boot_insn
  are unreachable as written. Compare against the reset pc derived from boot_addr.
- M-3 (Medium; adopted from rev51 Major 3, verified). :210 and :220 cp_mepc_src.boot_pc test st.mepc == cfg.boot_addr, the
  same defect: boot_pc and cr_line_mepc.nmi_ext_boot_pc are unreachable. Same fix.
- M-4 (Medium; adopted from rev51 Major 4, verified). irq_marks_bin (:224-232) never returns pre_post_mip_equal or
  pre_post_mip_differ; the rendered bins (svh:5216) and the cross bin timer_pre_post_mip_differ (:5221) are unreachable by
  construction and unlisted. Sample the pre/post relation as its own fact, or sample cp_rvfi_marks once per applicable mark.
- M-5 (Medium; adopted from rev51 Major 5, verified). cp_fetch_on_after is decided by a later fetch than the first after
  On (irq_off_take only from irq_pend_record :462; irq_off_first_fetch :672 ignores fetches while the window is not
  taken); take the window inside write_ibus before judging and compare the fetch address to the vector itself, not its page.
- L-1 (Low, records). The log's "KNOWN DIVERGENCE FROM THE PLAN TEXT" paragraph on cp_post_exit and the manifest row are
  stale: the plan at 109b654 (:2372) already decides the bin by the first record after the exit, as the sampler does
  (also rev51's Minor).
- L-2 (Low, records). "Neither loosening moves the probe" holds for scope (22) only; 35 "other" refusals, all iff guards
  holding a comparison, leave the census between d09ff58 and 4b5730e (retained: irq1/census_left_d09ff58_to_4b5730e.txt).
- L-3 (Low, records; routed to the irq-entry group). gen_test_irq_basic.fcov.yaml declares 29 bins on gen_irq_vector_cg
  and 4 on gen_exc_trap_csrs_cg, neither rendered by this step; unreferenced today, it fails the DECL leg at the flip
  unless those covergroups render or it is re-rendered. The landing note does not state this consequence.
- L-4 (Low, environment). The irq checker's history refactor into gen_irq_view rides this landing with the smokes as its
  only evidence; a re-fired existing irq red on the range end is owed at the next irq touch.
- L-5 (Low, environment; adopted). The referee block (:2803 ff.) guards three of the four new groups and not
  gen_irq_reset_fetch_en_cg; add (n_irq_rst + n_irq_off) > 0 && irq_rst_cg.get_coverage() == 0.0.
- L-6 (Low, environment; adopted). cp_others reads irq_lines_now rather than the view at irq_commit_cycle(st); under a
  storm regime a line raised or released between the decision cycle and the record changes the bin.
- L-7 (Low, environment; adopted). A view miss on a record returns from irq_pend_record (:448-452) before irq_dbg_record,
  irq_rst_record and irq_off_take run, dropping a window's open or close record silently; skip only the CG-IRQ-003 arms.
- L-8 (Low, environment; adopted). cp_mie_global_edge.mret_mpie1_pending (:432) fires for any M-mode mret with MIE 1 and a
  pending line; the plan wants the 0 -> 1 restore: require !was && now.
- L-9 (Low, records and test; adopted). The unit test's fifth check ("a parenthesised comment before the colon still
  renders") asserts only that cr_line_mode_post renders; plan :2377 has no parenthetical and the loader refuses that shape
  by design (codegen :110-113). Rename it to what it tests or drop it; the other four checks name real features.
- L-10 (Low, code hygiene; adopted). Hand-encoded CSR numbers and mstatus bit indices where ibex_pkg names exist; the
  mret/dret/wfi encodings duplicating GEN_INSN_MRET / GEN_INSN_DRET; dead _unused_split_cross_bin; two comments displaced
  onto other lines by the insertions; the misc_vif comment naming irq_pending where only core_busy is read; one
  history-narrating comment in gen_tb_pkg.sv:579.
- Info (adopted). An Off window beginning at cycle 0 is never published because 0 is the "no window" sentinel
  (gen_checkers_pkg.sv:538); use a valid flag if reset-time Off windows are in CG-IRQ-011's scope.
- Observation. The gate build identity moves with this landing (9879ca90c6beba35 at 4b5730e); the TB-source digest
  4153c078b0704697 equals the retained log's compile identity, so the smokes ran on the range end's TB sources.

CRITIC VERDICT: REQUEST-CHANGES, confined to the CG-IRQ-001 and CG-IRQ-011 sampler defects (M-1..M-5) and the log's
reachability list. APPROVED within the group: the dbg_dret checker fix at e1bee86 (its full trust triad retained, the base
re-measured, the mutant caught by the named check alone), the plan line at d09ff58 (a scope row of the census closed),
and at 4b5730e the render, the codegen fix proved in both directions, the compile with its stated identity, the four
smokes, the published sampled view, and the CG-IRQ-003 and CG-IRQ-010 classifiers as traced. Five coverpoints of two
covergroups book bins by tests that can never hold or return values no bin owns, and the log reports none of them; a
covergroup family is validated by what it samples. Re-review on the sampler fix with the smokes re-run; the manifest
consequence (L-3) goes to the irq-entry group.

## 6. Reconciliation with the cross-model range review
dv/auto_dv/reviews/2026-09-05-claude-diff-253f08ef-4b5730ec.md (rev51; read from the working tree at 2026-09-05T07:18:38Z, sha256
71f2d4001fc47e03, 63 lines, uncommitted then; REQUEST-CHANGES: five Majors, eleven Minors, one Info). Its five Majors
are M-1..M-5 here, each re-verified by me against gen_fcov_pkg.sv, gen_irq_if.sv, gen_agents_pkg.sv, the RTL reset pc
and the rendered svh (adopted and verified). Its Minors: the referee gap (L-5), cp_others (L-6), the view-miss early
return (L-7), mret_mpie1_pending (L-8), the fifth unit-test check (L-9), the hygiene items (L-10), the stale divergence
paragraph (my L-1, found independently). Its Info is adopted. Not in the review: my L-2 (the census wording), L-3 (the
irq manifest's bins on unrendered covergroups) and L-4 (the checker refactor without a re-fired red). Same verdict word.
If the committed artifact differs from the hash above, the difference is noted by corrigendum.

## Corrigendum (2026-09-05T07:34:09Z, HOLD sent to the Orchestrator first; the verdict above is unchanged)
Scope, restated so the record covers the checker fix: the group judged here is the three commits e1bee86 (tb-infra-2's
dbg_dret checker fix with its red and mutant, Section 1), d09ff58 (the CG-IRQ-001 cr_upath_pending plan line, Section 2)
and 4b5730e (landing 43, Section 3), inside 27212cb..4b5730e. The header's "Range e1bee86..4b5730e" excludes e1bee86 by
git range semantics (it is the parent of 253f08e); the range review rev51 (253f08e..4b5730e) did not judge it either,
and it sat unnamed inside rev49's range. It is named here explicitly and was judged on its own retained evidence.
Section 6's artifact hash 71f2d4001fc47e03 is the one committed at 24da095; no corrigendum on its content is needed.

## Section 7. Recorded re-review of the named range 27212cb..55ef529: IRQ step 1b at 55ef529 (written 2026-09-05T08:40:35Z)

Scope. The group is e1bee86, d09ff58 and 4b5730e (judged above) plus the fix landing 55ef529 (twelve files:
gen_checkers_pkg.sv, gen_fcov_pkg.sv, gen_tb_pkg.sv, gen_tb_top.sv, gen_fcov_codegen.py, gen_ut_fcov_codegen.py,
gen_irq_reset_reads_directed.S and gen_ut_irq_reset_reads.py (new), gen_fu_l46_irq_step1b.log and
gen_fu_l43_irq_step1_corrigendum.log (new), gen_manifest.md, gen_tdd_step2b.md). The range also carries a148548 (the
irq entry's manifest re-render, 66 declarations on unrendered covergroups removed: the L-3 disposition, judged with
the irq-entry group), the DV Lead's plan touches 8559958, 73e94d7 and f11fc3d (read here only as the classifiers'
reference), records (269415a row T5, 2c6366c) and my own verdicts. Method: the diff read in full; every classifier
traced against the RTL terms it names; the landing's figures re-derived on my own compile of a detached worktree of
55ef529 (TB-source identity 1a2c9707a8a108e9, the log's), one fixture run, two smoke shapes, a lines run, the mutation
re-fired on a second worktree, urg on each run's own vdb; logs retained under dv/auto_dv/work/critic/irq1b/. Exposure:
the Orchestrator's range message summarised the landing's claims; rev54 runs on the same range and is not read; its
reconciliation is owed as a Section 8 when it lands. dv_principles.md re-hashed d9c27db18f511411, unchanged.

7.1 Gates and identities. gen_fcov_codegen --check up to date, gen_knobs_codegen --check up to date,
GEN_UT_FCOV_CODEGEN PASS (0 failures), gen_unbuilt_mark_check PASS, all on the 55ef529 worktree. gen_fcov_groups.svh is
byte-identical between 4b5730e and 55ef529 (git diff empty): no bin moved, as claimed. Gate key fc6a99f777d55b3d at
55ef529 (449f0e66969bd42b at 4cd3ff6 and 721bab8); TB-source digest 1a2c9707a8a108e9 equals the retained log's compile
identity and my own compile printed the same. No manifest under fcov_expectations or tests names mret_mpie1_pending,
boot_insn, boot_pc or a pre_post_mip bin (git grep), so the bin that went dark and the bins freed move no entry.
All twelve files ASCII-clean. gen_tb_pkg.sv at 55ef529 has md5 049c0fe4f1e93bb5f6ef5e56abe45434, the value the log
gives before and after the mutation, and no MUT-MIEVIEW1 marker exists under dv/auto_dv outside the log and the record.

7.2 The five Mediums, each traced and reproduced.
- M-1 (mip line-indexed against bit-positioned) FIXED. The expected word is built by setting bit gen_irq_mie_bit(l) for
  each high pin l < 18 and compared whole (gen_fcov_pkg.sv, cp_reset_reads arm). gen_irq_mie_bit (gen_agents_pkg.sv:517-523)
  maps 0/1/2 to CSR_MSIX_BIT 3, CSR_MTIX_BIT 7, CSR_MEIX_BIT 11 and 3..17 to CSR_MFIX_BIT_LOW 16 + (l-3), the positions
  ibex_cs_registers.sv:497-500 reads mip through (ibex_pkg.sv:712-716); line 18 (nm) is outside the loop, and the RTL
  keeps no mip bit for it. The arm is guarded on irq_view_ok, the one reset read that needs the view. REPRODUCED: the
  fixture built from the worktree (24 words, crc32 0x69379b6e, entry 0x80000080, the log's three figures) run on my
  build reads mstatus 00000080, mie 00000000, mtvec 80000001, mip 00000800 with line 2 raised before fetch enable,
  retired 10 compared 10 mismatches 0, verdict PASS, referee 0; urg on that run alone (Total tests in report: 1):
  cp_reset_reads expected 4 covered 4 (mip_reflects_pins, mtvec_boot_page, mie_0, mstatus_0x80 one hit each).
- M-2 (boot_insn against the raw boot address) FIXED. cp_first_event compares pc_rdata with gen_reset_pc(cfg.boot_addr)
  = {boot_addr[31:8], GEN_MM_BOOT_RESET_OFFSET[7:0]} with the offset 32'h80 (gen_tb_pkg.sv:293), the RTL's PC_BOOT
  fetch address {boot_addr_i[31:8], 8'h80} (ibex_if_stage.sv:243). REPRODUCED: the same run covers cp_first_event 1 of 3
  (boot_insn hit, debug_before_insn and nmi_before_insn uncovered), the log's figures; the fixture's ELF entry is
  0x80000080 in my sidecar too.
- M-3 (boot_pc, same defect) FIXED IN CODE, BIN UNHIT FOR THE STATED REASON. Both arms of irq_mepc_bin compare mepc with
  gen_reset_pc, the shared helper. The layout argument holds term by term: mtvec after reset is
  {boot_addr_i[31:8], 6'b0, 1'b0, 1} (ibex_cs_registers.sv:739-743 with CheriotEnable = IbexMuBiOff at gen_dut_top.sv:206,
  so the mode bit is 1, vectored); a vectored entry fetches {mtvec[31:8], 1'b0, irq_vec[4:0], 2'b00} (ibex_if_stage.sv:
  EXC_PC_IRQ arm), so the external NMI (cause 31) vectors to boot_page + 0x7c; gen_link.ld (dv/auto_dv/stim/
  gen_riscv_dv_target/gen_link.ld) declares PROG at ORIGIN 0x80000080, so no program byte can sit at 0x80000000..7f.
  The plan's cross ignores every line but nmi_ext with boot_pc (gen_fcov_plan.md:2229), consistent. Reachable with no
  stimulus built, the fourth category; not declaration-class. The remedy (a second region) is the Test Writer's.
- M-4 (relation bins unreachable by construction) FIXED. The relation t.ext_pre_mip == t.ext_post_mip (gen_rvfi_pkg.sv:27,
  :122, the monitor's copy of rvfi_ext_pre_mip/post_mip) is emitted as a second sample under the same v_line with every
  other argument -1, which every coverpoint ignores (ignore_bins na = {-1}, svh:5206 ff.), so only cp_rvfi_marks and
  cr_line_marks see it; n_irq_entry_rel counts the second samples and the summary prints it. REPRODUCED: gen_ut_fetch_en
  on the NMI-long program under the storm regime (my recipe, PASS, referee 0): cp_rvfi_marks 7 expected 4 uncovered 3
  covered, the log's 42.86, with pre_post_mip_differ 18 and pre_post_mip_equal 42 hits; a storm-shaped gen_ut_lockstep
  run hits the cross timer_pre_post_mip_differ twice. entry_rel equalled entry in every run (60/60, 6/6).
- M-5 (window opened late; page compare) FIXED. irq_off_take() now runs in write_ibus before irq_off_first_fetch, so the
  window is open at the first fetch; irq_addr_is_vector tests membership of the 32-entry table {base + 4k} with base =
  {mtvec[31:2], 2'b00} (equal to {mtvec[31:8], 8'h00} because the RTL zeroes mtvec[7:2]), against irq_mtvec_base after a
  retirement or gen_mtvec_reset(boot_addr) before one, which is the plan line at 8559958. REPRODUCED: the fetch-enable run
  covers cp_fetch_on_after 1 of 2 with handler_fetched_at_on hit and resume_at_on uncovered, the log's row; the cross
  irq_arrives_while_off_handler_fetched_at_on is hit with it.

7.3 The Lows of Section 5 and the Info.
- L-1 CLOSED: the corrigendum log stands beside the landing-43 log, whose blob at 55ef529 has md5
  a707ba4376d747172559ba8590210728 as it says, and quotes gen_fcov_plan.md:2380 correctly (checked verbatim).
- L-2 NOT IN THIS LANDING (records: the 35 "other" census refusals between d09ff58 and 4b5730e); stands as owed where
  the census is kept.
- L-3 ROUTED and acted: a148548 removed the 66 declarations; the promotion is the DV Lead's conditional.
- L-4 CLOSED, REPRODUCED EXACTLY: on a second 55ef529 worktree I mutated gen_irq_view::mie_at to answer every query with
  no line enabled, compiled (identity 9ce30e7bbe118715) and ran gen_ut_irq on the directed interrupt program (156 words,
  crc32 0x8e882c5b): verdict FAIL, 62 UVM_ERROR lines all [irq_pending], the first "gen_checkers_pkg.sv(247) @ 1494500
  ... cycle 1486: irq_pending_o=1 expected 0 (pins 00040 mie 00000000)", the log's line byte for byte; the same mutant
  with +gen_chk_irq_pending=0: PASS, 0 UVM_ERROR; the same recipe on the unmutated build: PASS, 0 UVM_ERROR, with the
  lines smoke's own figures entry=6 edge=12 access=1 reset=1 fetch_off=0 (the log's "lines" row) and mie_global=1 with
  six mrets counted as MIE-already-set.
- L-5 CLOSED: the referee for gen_irq_reset_fetch_en_cg is gated on (n_irq_rst + n_irq_off) > 0.
- L-6 CLOSED: cp_others reads irq_pins_at(irq_commit_cycle(st)); see L-15 for the miss case.
- L-7 CLOSED: a view miss skips only the NMI-mode bookkeeping, irq_edge_mie, irq_access_sample and irq_mie_global_sample;
  irq_dbg_record, irq_rst_record and irq_off_take run, and the miss is counted.
- L-8 CLOSED: mret_mpie1_pending requires now && !was; !now books mret_mpie0_pending; MIE 1 -> 1 across an mret is
  counted (n_irq_mret_noedge) and printed by name. The 173-to-1 argument is sound: mret_mpie0_pending uncovered in both
  builds means MIE was set after each mret; all 173 booking no-edge means it was set before; my fetch-enable run counts
  60 such mrets with the bin at 0. The two missing combinations are the DV Lead's plan touch, as the log says.
- L-9 CLOSED: the fifth unit check is renamed to what it verifies (a cross of three coverpoints renders).
- L-10 CLOSED with one residue (L-14): CSR numbers and mstatus indices now come from ibex_pkg; GEN_RV32_MRET/DRET/WFI are
  composed from OPCODE_SYSTEM beside GEN_RV32_NOP; the dead helper is gone; the displaced and misnamed comments fixed.
- Info (cycle-0 Off window) CLOSED: fe_off_valid beside fe_off_cycle at the three sites (gen_checkers_pkg.sv:450, :539,
  :540); the register row T5 at 269415a records it; my fetch-enable and storm shapes read fetch_off=1 where landing 43's
  storm read 0.

7.4 New findings on 55ef529.
- L-11 (low, sampler; undisclosed count effect). irq_rst_emit samples the reset group with irq_rst_lines and irq_rst_first
  on EVERY emission, so cp_lines_at_reset and cp_first_event take one hit per reset-group sample: in my fixture run
  boot_insn and none read 5 hits from one event (reset=5: the first event plus four reads). The covered set is right;
  per-bin counts overstate events the way the log discloses for entry_rel but not here. Pass -1 for those two on the
  read emits, or disclose the effect beside entry_rel.
- L-12 (low, classifier precision vs the log's wording). irq_addr_is_vector accepts any of the 32 table slots, because the
  cause is unknown at fetch time; the plan says "the base plus four times the cause" and the log calls the test "the
  exact vector". State the accepted set as the table, or bind the slot to the entry record's cause when it arrives.
  Info: the direct-mode arm is dead in this DUT (mtvec_d forces the mode bit to 1).
- L-13 (low, records). The smoke table names shapes, not commands: no plusargs, image or seed are retained for storm,
  lines, dbgstorm and fetchen. I reproduced lines exactly and the fetch-enable bins exactly, but two storm attempts of
  mine (with and without the NMI line mix) time out at the tohost store and cannot confirm entry=173. Retain the four
  commands beside the table.
- L-14 (low, hygiene; L-10 residue). gen_fcov_pkg.sv:404 still compares csr with 12'h344 and 12'h304 two lines above the
  ibex_pkg::CSR_MIP compare.
- L-15 (low, classifier on a view miss). irq_entry_sample is not gated on irq_view_ok, and irq_pins_at returns '0 on a
  miss, so cp_others is then decided from an all-low pin vector (only_this or others_enabled_idle) rather than skipped;
  the miss is counted but the bin is booked. Return -1 for cp_others when the view has no sample at the commit cycle.
- L-16 (low, checker triad). The drain check at gen_checkers_pkg.sv:450 now also judges windows opened at cycle 0. No red
  shows the rule firing for such a window; the broadening cannot hide a failure, so this is owed, not blocking.
- Observation (not this landing's). My fetch-enable shape with the NMI line mix fires sva_rvfi_irq_valid_exclusive at
  cycle 11 (gen_protocol_props.sv:299, ruled legitimate DUT behaviour in gen_rvfi_irq_valid_exclusive_ruling.md; the
  property replacement is frozen under LOG-085); without the NMI mix the same shape is clean.
- Conformance (dv_principles.md): the classifiers remain reporting-only and the collected mechanisms (referee, checker)
  decide; the mret bin removed is honesty over green; the code comments trimmed to mechanism; L-16 is the one triad gap.

7.5 Verdict on 55ef529. All five Mediums of Section 5 are fixed as classifier changes with no bin moved, each reproduced
on my own build from the landing's own fixture or an equivalent shape; L-1, L-3..L-10 and the Info are closed; L-2 stands
where the census lives; L-11..L-16 are new Lows, none blocking. CRITIC VERDICT: APPROVE for 55ef529. The
REQUEST-CHANGES of Section 5 on the group e1bee86, d09ff58, 4b5730e is LIFTED on this record: the irq-step1-samplers
group stands approved with L-2 and L-11..L-16 owed as disclosed. Sections 1-6 and the corrigendum above are
byte-identical to the d355f7f commit (a17ace6ae10690e8).

## Section 8. Reconciliation of Section 7 with the cross-model re-review rev54 (written 2026-09-05T09:01:35Z)

Artifact: dv/auto_dv/reviews/2026-09-05-claude-diff-27212cb0-55ef529a.md, committed 0029b94, sha256 0e53e7d9f4ad2f81,
47 lines, verdict APPROVE-WITH-CHANGES, read after Section 7 was on the record (31903f9). Exposure before Section 7: the
Orchestrator's message summarised its rows (disclosed in Section 7's method line).

Agreement. rev54 re-traces the five Majors to the same mechanisms and the same fixture and smoke figures as Section 7.2
(the expected mip word through gen_irq_mie_bit; gen_reset_pc from GEN_MM_BOOT_RESET_OFFSET against PC_BOOT; the
relation as a second sample whose only cross gain is cr_line_marks; the window opened in write_ibus with the reset
mtvec base), judges e1bee86 clean, and confirms the valid flag at the three sentinel sites, the referee, the mret edge
and the l43 corrigendum. Its verdict word differs from mine by the form each of us uses: my APPROVE lifts a
REQUEST-CHANGES with the Lows owed as disclosed; its APPROVE-WITH-CHANGES routes seven Minors to tb-infra-2's paired
touch. Four of its Minors are Section 7's L-12 (table membership, not base plus four times the cause), L-14 (residual
CSR literals), L-15 (cp_others before the view check) and the valid-flag effect Section 7.3 closed on my own fetch_off
reading. Three are rows Section 7 did not carry, adopted below with the mechanism verified.

- L-17 (Low, records and hygiene; adopted from rev54 Minor 1, verified). gen_fcov_pkg.sv:162 still carries the jammed
  second comment ("// the debug driver's request changes (the same item: changed[0] = req)") on state_imp while dbg_imp
  at :161 has none; the log's Minors list says "two jammed comments split". Move the comment and correct the list.
- L-14 extended (adopted from rev54 Minor 4, verified). Besides :404, dcsr is compared as 12'h7b0 at :572 where
  ibex_pkg::CSR_DCSR exists.
- L-15 extended (adopted from rev54 Minor 3, verified). A view miss is counted at every irq_pins_at call (:299) and
  again in irq_pend_record (:467), so one record's miss can count two or three times (the entry sample's call, the
  debug record's at :534, the record's own); count once per record.
- L-18 (Low, test hygiene; adopted from rev54 Minor 5, verified). gen_ut_irq_reset_reads.py:26 and :28 hand-encode
  HOLD_STICKY = 3 and MIP_EXTERNAL_BIT = 11, whose authorities are gen_agents_pkg.sv's hold enum and ibex_pkg's
  CSR_MEIX_BIT; the hold enum through the knobs codegen is deferred in the log with a reason and needs an owner.
- L-19 (Low, records; adopted from rev54 Minor 6, verified with my own run). The log does not say which bin the storm
  smoke's new fetch_off=1 window produced. My storm-shaped gen_ut_lockstep run on the same build (Section 7.3, retained
  under dv/auto_dv/work/critic/irq1b/) reads cp_fetch_on_after resume_at_on 1, handler_fetched_at_on 0: the reset-opened
  window's first fetch is the boot fetch, as rev54 infers, and the fetch-enable shape's window is the handler fetch.
  State both in the log at its next corrigendum.
- L-20 (Low, dead code; adopted from rev54 Minor 7, verified). irq_lines_now is declared at :179 and written at :722
  "for cp_others", which now reads the view; nothing reads the field. Delete it.
- Info (adopted from rev54, verified). The comment above the view-ok block ("the three below read the record itself")
  is wrong for irq_dbg_record, which reads irq_pins_at at :534. The reviewer's second Info (the handler-with-interrupts-
  disabled fixture and the two missing mret bins owed) is Section 7.3 L-8's disposition.

Disagreement: none. rev54 records nothing Section 7 disputes, and Section 7's L-11 (the reset group's per-sample hit
inflation), L-13 (smoke recipes not retained) and L-16 (no red for the cycle-0 drain check) are rows rev54 does not
carry; they stand. Verdict unchanged: APPROVE for 55ef529, the REQUEST-CHANGES lifted; L-2, L-11..L-20 owed as
disclosed. Sections 1-7 and the corrigendum above are byte-identical to the 31903f9 commit (6b86f0c732cc05f5).

## Corrigendum to Section 7.3 (L-8) and 7.4 (written 2026-09-05T09:21:12Z, HOLD sent to the Orchestrator first; Sections 1-8 unchanged)

Section 7.3 says of L-8: "The 173-to-1 argument is sound: mret_mpie0_pending uncovered in both builds means MIE was set
after each mret; all 173 booking no-edge means it was set before; my fetch-enable run counts 60 such mrets with the bin
at 0." Section 7.4 says "the mret bin removed is honesty over green". Both rest on the classifier's pre-state, which is
the PREVIOUS RETIRED RECORD's MIE, and that is not the mret's pre-state when the mret is the first instruction of an
interrupt handler: the entry retires no record and clears MIE (rtl/ibex_cs_registers.sv:924), so the previous record
is the interrupted instruction with MIE 1. Both smoke programs make every regular vector a bare mret (gen_irq_directed.S
"every handler is one mret"; gen_nmi_long_directed.S gen_vec ".rept 31 / mret"), so all 173 storm samples, the 60 of
my fetch-enable run and the six of the lines run were true MIE 0 -> 1 set edges with MPIE = 1, MPP = M and a line
pending: the declared bin mret_mpie1_pending. Landing 46's edge fix therefore did not remove false coverage; it
dropped 173 true hits of the declared bin to unclassified, and my Section 7 approved that reading. The correct
statement of L-8's disposition: the edge semantics the fix introduced are right, but the pre-state it compares
against is wrong at an entry record, and the bin's count fell for that reason. Found by rev56 (96825af) on the
follow-on range 03aafce..dc60063, where the same pre-state books the 173 into the new bin; verified by me from the two
programs, the RTL and my own runs on a dc60063 build (lines: mret_mie1_mpie1_pending 6, mret_mpie1_pending 0; storm:
173 and 0), and recorded as M-1 of gen_critic_mret_hold.md, which owns the fix and the corrigenda to the two landing
logs. My earlier verdict word for 55ef529 stands as recorded; the misjudgement is this closure's, and it is stated
here rather than edited away.
