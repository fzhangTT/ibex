# Critic verdict: feature group mret-bin-and-hold-mirror, range 03aafce..dc60063 (one joint commit)

Artifacts (sha256 first 16 at dc60063):
- dv/auto_dv/env/gen_fcov_pkg.sv 6e7bbedadeda474e
- dv/auto_dv/env/gen_fcov_groups.svh 3ac18437004d31e6
- dv/auto_dv/tb/gen_knobs_codegen.py 3f725fbc4e4b02ac
- dv/auto_dv/tb/gen_tb_knobs.yaml 5c10ecde8ffe1032
- dv/auto_dv/gen_tb/gen_knobs.py 9a6f82241c700bf0
- dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py 0575565a787de891
- dv/auto_dv/docs/gen_fcov_plan.md a46093736e2eef4f
- dv/auto_dv/docs/gen_trace_tp_bin.csv d8d44af32d02694a
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l47_irq_mret_bin.log 20c8beb40a0859a9
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l46_irq_step1b_corrigendum.log fb052b6434375efd
Date: 2026-09-05T09:13:51Z. Role: Critic (the reviewer other than the author). Range named by the Orchestrator: 03aafce..dc60063, one
commit carrying the DV Lead's plan half (four generated documents) and tb-infra-2's coverage and codegen half (fourteen
files). Method: the diff read in full; every classifier and the codegen parser traced against the terms they name (the
RTL lines the plan cites, the enum declaration, the rendered include); the landing's figures re-derived on my own
compile of a detached worktree of dc60063 (TB-source identity 196c0be73a622d1d, the log's) with the five smoke
commands the log retains, plus the irq-ack test; the drain-check red re-fired on a second worktree with three mutation
variants; my logs under dv/auto_dv/work/critic/mret/. Exposure: the Orchestrator's range message summarised the
landing's claims; rev56 is read only in Section 6. dv_principles.md sha256 d9c27db18f511411, unchanged.

## 1. Gates, identities, records

- On the dc60063 worktree: gen_fcov_codegen --check up to date, gen_knobs_codegen --check up to date, GEN_UT_FCOV_CODEGEN
  PASS, GEN_UT_KNOBS_CODEGEN PASS, gen_unbuilt_mark_check PASS, GEN_NORM_PROBE self-test PASS, gen_trace_check PASS
  (coverpoints declared 2279, owned by an item 2205, 74 regression-level). Gate key dd9d079062611298 (fc6a99f777d55b3d at
  55ef529); TB-source digest 196c0be73a622d1d, equal to the log's compile identity and to what my own compile printed.
- gen_fcov_groups.svh moves by exactly five lines: the CG-IRQ-003 bin count 37 to 38, the new localparam
  GEN_FC_IRQ_PENDING_MODEL_CP_MIE_GLOBAL_EDGE_MRET_MIE1_MPIE1_PENDING = 6, and the coverpoint line gaining
  mret_mie1_mpie1_pending; the cross count is unchanged (36). No manifest under fcov_expectations names any mret bin.
- The three generated plan documents carry one new inputs digest (031a495716cf) in their headers; the distinct-bin
  total moves 15833 to 15834 and gen_trace_tp_bin.csv gains the one row
  TP-IRQ-028,CG-IRQ-003,cp_mie_global_edge,mret_mie1_mpie1_pending,0.
- gen_checkers_pkg.sv at dc60063 has md5 6b3d5f77978d9321d121598d7ba57843, the value the log gives before and after
  its mutation; gen_fu_l46_irq_step1b.log at dc60063 has md5 e9be074c5036cb62956ff71bc2b29bf7, the value the
  corrigendum row gives for the untouched log; the two new logs' manifest rows match their sizes and md5s; all eighteen
  files are ASCII-clean.

## 2. The plan half, checked against the RTL and the charter

- The four-way table is stated in the coverpoint's own key (edge direction crossed with pending, as its four csr-write
  bins are): set edge = mret_mpie1_pending, no edge staying clear = mret_mpie0_pending, no edge staying set = the new
  mret_mie1_mpie1_pending, clear edge = no bin, named uncovered. TP-IRQ-028's charter ("Interrupt pending during mret:
  taken before the first instruction at mepc", gen_test_plan.md:8319, stimulus "mret with the line held; enabled case
  (MPIE = 1 or MPP = U)") covers the new bin's prose ("the return leaves interrupts enabled and the entry follows").
- The clear edge's reachability argument holds term by term: rtl/ibex_controller.sv:490 assigns irq_enabled =
  csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U) and gates interrupts with it, not synchronous exceptions;
  rtl/ibex_cs_registers.sv:926 saves mstatus_d.mpie = mstatus_q.mie at the trap, so an exception taken with MIE clear
  saves MPIE = 0, and a handler that sets MIE before its mret produces MIE 1 before and 0 after. The M-mode clause
  follows from the same gate (outside M-mode the MIE bit stops deciding). Named NOT-BUILT-STIMULUS with an item owed.
- The cp_fetch_on_after sentence now states membership in the 32-slot table at the current base, with the slot identity
  owned by CG-IRQ-006 at the entry record: the ruling on my L-12 and rev54's Minor, consistent with the classifier that
  was never changed and with the gen_link.ld geometry (PROG at ORIGIN 0x80000080, the table the 0x80 bytes below).
- cp_mepc_src.boot_pc and cr_line_mepc.nmi_ext_boot_pc carry the fourth-category reason with the same geometry,
  matching my Section 7.2 M-3 reading at gen_critic_irq_step1.md.

## 3. The sampler, traced and measured

- irq_mie_global_sample: was = irq_mstatus_prev[MIE] (the PREVIOUS RETIRED RECORD's mstatus), now = st.mstatus[MIE]
  (this record's), pend = the pending model at the commit cycle from the view; for an mret the RTL restores MIE from
  MPIE (ibex_cs_registers.sv:954 ff.), so now is the saved MPIE and the four arms map (now, was) onto the table
  correctly GIVEN A CORRECT was. was is not correct across an interrupt entry: the entry retires no record and clears
  MIE (rtl/ibex_cs_registers.sv:924 mstatus_d.mie = 1'b0), so when the mret is the handler's first instruction the
  previous record is the interrupted one, whose MIE is 1, and the arm reads (now && was) where the truth is a 0 -> 1
  set edge. Both smoke programs make every regular vector a bare mret (gen_irq_directed.S:3-4 "every handler is one
  mret"; gen_nmi_long_directed.S gen_vec ".rept 31 / mret"), so every mret these smokes retire is that case. MEASURED
  on my build: the lines run books its six handler mrets as mret_mie1_mpie1_pending 6, mret_mpie1_pending 0; the
  storm run books 173 and 0. The truth for both is the declared bin mret_mpie1_pending (0 -> 1 with MPIE = 1, MPP = M,
  a line pending, the entry following), and the new bin's true count in these programs is 0: no handler here runs
  with MIE set before its mret. This is Section 5 M-1; the log's "THE NEW BIN IS HIT" and the plan's "the case every
  program in the tree performs" describe the classifier's reading, not the design's behaviour. The dependency the
  log states (was is the pre-state because records are consecutive) is true for csr writes and false for the one
  event this coverpoint is about.
- The view is decided once in write_mst before any classifier reads it; irq_others_bin returns -1 on a miss instead of
  classifying from a zero pin vector; irq_pins_at no longer counts, so a miss counts once per record (rev54 Minor 3,
  my L-15). The literals 12'h344, 12'h304 and 12'h7b0 are CSR_MIP, CSR_MIE and CSR_DCSR (L-14). irq_lines_now is gone
  (L-20). The comment jam at :161-162 is resolved with each comment on its own declaration (L-17). The run summary
  prints windows published and dropped-as-short (L-19's cause made visible) and the masked count.
- Smokes, from the five commands the log now retains (L-13), on my build, each verdict from its own verdict.txt and
  referee 0, UVM_ERROR 0:
    storm    entry=173 entry_rel=173 edge=348 mie_global=174 reset=1 fetch_off=1 (published 1, dropped 0) masked 0
    lines    entry=6   edge=12  mie_global=7   fetch_off=0 (published 0, dropped as shorter than the minimum 1)
    dbgstorm entry=39  edge=80  mie_global=40  debug_window=1  fetch_off=0 (dropped 1)
    fetchen  entry=15  edge=33  mie_global=16  fetch_off=1 (published 1)
    rr       reset=5, mstatus 00000080 mie 00000000 mtvec 80000001 mip 00000800
  every figure the log's table gives. The storm's entry=173 needed exactly what the log says my earlier attempts
  lacked, +gen_ut_boot_retire=100 and the image's own tohost address.
- urg on the storm run alone (Total tests in report: 1): cp_mie_global_edge expected 7 uncovered 5 covered 2, the two
  covered being mret_mie1_mpie1_pending with 173 hits and set_pending with 1: THE NEW BIN IS HIT and the 173 land in
  it, as the log's third reading says. cp_fetch_on_after 1 of 2 with resume_at_on hit, which is L-19's answer: the
  reset-opened window's first fetch is the boot fetch.

## 4. The codegen half, traced and exercised

- sv_enum_members matches the plain declaration at gen_agents_pkg.sv:489 (typedef enum {GEN_IRQ_HOLD_CYCLES,
  GEN_IRQ_HOLD_UNTIL_ACK, GEN_IRQ_HOLD_UNTIL_TAKEN, GEN_IRQ_HOLD_STICKY} gen_irq_hold_e), returns positional ordinals
  and refuses an explicitly valued member. The mirror renders into gen_knobs.py alone (SV_ENUMS), no SV copy, so the
  package stays the one authority. The unit test's three checks (mirror equals the declaration; the key set is the
  enum's, prefixed, not the knob's; the two namespaces disagree on until_taken) are the log's; its RED reproduced by
  me: the dc60063 test against the 03aafce-rendered gen_knobs.py fails the log's two checks ("python SV_ENUMS mirrors
  gen_irq_hold_e", "the mirror is the enum, not the knob value set") plus the staleness check my file swap induces
  (the log ran the new test against the committed codegen, so it saw two), and passes with the rendered file restored
  (sha256 equal to the committed blob).
- GEN_IRQ_MIP_BIT_EXTERNAL derives from ibex_pkg::CSR_MEIX_BIT (11) into the TB package (with its _PY mirror the top
  checks) and the Python module; gen_ut_irq_reset_reads reads it and the hold enum from the mirror; gen_ut_irq_ack
  reads HOLD_UNTIL_ACK from the mirror. Both tests ran on my build: reset-reads PASS with the four values above;
  irq-ack PASS (the log's discriminating consumer of the enum, since a wrong ordinal would change the hold policy).

## 5. The drain-check red (my L-16), the corrigendum, conformance, rows

- The log's MUT-FEDRAIN0 ("the Off window never closes") is described, not printed. Three edits of mine on a second
  worktree, each with gen_ut_fetch_en on the irq program and +gen_fetch_en_at_reset=0: (a) the clear on the return to
  On removed (identity 65ecd7be78374b46): 38 [fetch_en] UVM_ERRORs naming the test's own Off edge, 0 with
  +gen_chk_fetch_en=0; (b) the same plus no re-capture (e8fddcf4267b93ce): 38, same edge; (c) the Off cycle never
  written and the window never closed (6e8d3d067a8c79d2): 38 errors whose first line is the log's byte for byte,
  "record at order 201, cycle 1301, 1301 cycles after fetch_enable_i left On at cycle 0 (drain window 64)", and 0
  ablated. The unmutated build PASSES with 0. So the red is reproduced and the ablation is clean. What (c) shows about
  the wording: "cycle 0" is the variable's initial value, not a window the checker observed at reset (the fetch-enable
  test turns the pin On at 5 ns, before the release, so no reset window exists in it; the reset-reads and lines
  shapes do open one and drop it as shorter than the minimum), and the rule judging a window whose cycle reads 0 is
  exactly the predicate the valid flag changed, which is the point of L-16. State it that way (L-1).
- The l46 corrigendum's three corrections are each true: the third jammed comment at :162 (fixed here), the three
  literals left after "11 sites" (fixed here), and the membership description of the vector test (the plan now states
  it). The log's untouched md5 is the committed blob's.
- Conformance (dv_principles.md): the covergroup change is a bin addition under LOG-096 with render, compile identity,
  the sampling point and field semantics stated, the unreachable case named with a mechanism and an owed item, and no
  manifest consequence; the checker is unchanged, and the red owed on it (L-16) is now retained; the enum mirror's
  guard is a live test rather than a comment; comments state mechanism.
- M-1 (Medium, classifier; tb-infra-2, with the DV Lead for the plan's narrative). The mret arm's pre-state is the
  previous retired record's MIE, which across an interrupt entry is the interrupted instruction's, so an mret that is
  the handler's first instruction (every vector of both smoke programs) is booked (now && was) into the new bin while
  the design performed the 0 -> 1 set edge of the declared mret_mpie1_pending: 173 false hits in the storm run and 6
  in the lines run on my build, and a false zero on the declared bin in both. Fix: derive the pre-state from the
  record itself when st.is_intr is set (MIE is 0 at entry by rtl/ibex_cs_registers.sv:924), or carry the entry's
  clearing into irq_mstatus_prev at the entry record; re-measure the smokes with the discriminator "st.is_intr is 0
  for every sample of the new bin" stated before the reading; correct by corrigendum the l46 log's two-build
  inference and the l47 log's "173, from false coverage to honest coverage" arc, which rest on the same pre-state,
  and the plan's sentence that the enable-already-set case is what every program performs. The new bin itself is a
  legitimate fourth combination and stays.
- L-1 (Low, records). The mutation text of MUT-FEDRAIN0 is not printed; my third edit reproduces its first line
  exactly, and the reproduction shows "left On at cycle 0" is the unwritten variable's initial value rather than an
  observed reset window. Print the diff and describe the red as the rule judging a window whose cycle reads 0.
- L-2 (Low, codegen; verified by construction). sv_enum_members splits the brace body on commas, so a `//` comment
  inside the braces with a comma becomes a member ("A, // a comment, with a comma / B" parses to four names), and
  the unit test re-derives the expectation with the same regex, so both agree on the same wrong parse. The committed
  declaration carries no comment. Strip comments before splitting, assert each member is an identifier, and compare
  the unit test against a hand-listed tuple.
- Info. The storm smoke's cp_fetch_on_after reads resume_at_on, which closes rev54's Minor 6 and my L-19 on the
  evidence; the l47 log says so under M6. The knobs mirror, the derived mip bit, both tests on the committed build,
  the literal cleanups, the once-per-record view decision, the comment split and the corrigendum discipline are
  sound and reproduced.

CRITIC VERDICT: REQUEST-CHANGES, confined to M-1 (the mret classifier's pre-state at an interrupt-entry record, the
smoke evidence that rests on it, and the two logs' and the plan's narrative built on the 173). APPROVED within the
group: the plan's four-way table and its RTL-cited reachability argument, the membership sentence and the two
layout lines; the render (five lines, no manifest consequence); the codegen mirror with its live guard and both
consumer tests; the literal, comment, dead-field and once-per-record fixes; the drain-check red (L-16 closed on the
reproduction above); the five smoke commands retained and reproduced to the digit; the l46 corrigendum. Re-review
on the classifier fix with the discriminator stated and the smokes re-measured.

## 6. Reconciliation with the cross-model range review rev56 (written 2026-09-05T09:20:39Z)

Artifact: dv/auto_dv/reviews/2026-09-05-claude-diff-03aafce2-dc60063e.md, committed 96825af, sha256 dd0f0e4dd1b6c77d,
41 lines, verdict REQUEST-CHANGES, read after Sections 1-5 were drafted. Exposure: the Orchestrator's messages
summarised its three rows before I read it; the Major's mechanism was then re-derived here from the two programs, the
RTL and my own lines and storm runs before Section 5 was written.

Agreement. rev56's Major is my M-1, from the same terms (the previous record's mstatus as the pre-state; the entry
clearing MIE at :924; the bare-mret vectors); mine adds the measured counts on both smokes (6 and 173 into the new
bin, 0 on the declared) and the consequence for the l46 two-build inference and my own Section 7.3 at
gen_critic_irq_step1.md, corrected there by corrigendum. Its Minor is my L-2, verified by construction. Its Low (state
"st.is_intr is 0 for every sample" as the prediction) is the discriminator M-1 asks for. Its verified list (the render,
the single SV authority, the guard, the derived bit, the literals, the RTL mret semantics with st.prv as MPP, the plan
citations, the manifest rows) matches Sections 1-4; it did not run the smokes, which Section 3 and 5 do. Verdict words
agree.

Disagreement: none.

## Corrigendum to Section 3 and Section 5 M-1 (written 2026-09-05T09:35:34Z, HOLD sent to the Orchestrator first; Sections 1-6 unchanged)

Section 3 attributes to "the plan" the words "the case every program in the tree performs", and M-1 asks for a plan
corrigendum on "the plan's sentence that the enable-already-set case is what every program performs". The attribution
is wrong. gen_fcov_plan.md at HEAD carries no such sentence (grep for "every program" and "the case every" finds none);
the landed bin text describes what the case is: "mret_mie1_mpie1_pending{NO EDGE, MIE stays 1 (MIE 1 before, MPIE = 1,
MPP = M) with irq_pending_o == 1: the return leaves interrupts enabled and the entry follows}". The sentence is in the
dc60063 commit message (its fourth line) and in the DV Lead's messages to the Orchestrator, where the DV Lead retracted
it at 09:19Z (no program performs the case; the bin stands as a fourth combination, reachable with no stimulus built).
So the disposition M-1 asks of the plan on that point is void; the corrigenda owed for the 173 narrative are the l46
and l47 logs', and the DV Lead's coming plan line is additive (the reason, the structural fact, the fixture sentence).
M-1's mechanism, measurement and verdict word are unchanged. Found by the Orchestrator; verified by me at HEAD.

## Section 7. Recorded re-review of the mret pre-state fix (written 2026-09-05T10:21:33Z)

Scope. The range the Orchestrator named is 03aafce..9bb1974; the commits judged are tb-infra-2's landing 49 at
9a42c17 (the pre-state fix, the discriminator counters, the parser fix, the l49 log, the corrigendum companion for the
l46 and l47 logs), the fixture companion at 021684d (landing 50, judged under L-3 and L-4 below) and the DV Lead's clause-free plan
line at 9bb1974; the joint landing dc60063 was judged in Sections 1-6 and stands as judged, with one
annotation: its commit body carries the sentence "the case every program in the tree performs" (the DV Lead's hand-off
prose), which the pre-state defect invalidated; the corrected reading is that no program in the tree performs the
stays-set case, the 173 being the declared restoring edge, and the DV Lead retracted the claim at 09:19Z. The plan
never carried it. Method: the diff read in full;
the fix traced against the RTL's rvfi_intr and trap-entry terms; the four smokes re-run on my own compile of a
detached worktree of 9a42c17 (TB-source identity fd9ba5b4ffae6a3c, gate key 3219e5ceb2426c90) with the commands the
l47 log retains, each run's own urg report read; the parser exercised on synthetic declarations; my logs under
dv/auto_dv/work/critic/mret2/ (README.txt). Exposure: the Orchestrator's messages summarised the landing; rev57 is
read only for a Section 8 when it lands. dv_principles.md sha256 d9c27db18f511411, unchanged.

7.1 Gates and records. On the 9a42c17 worktree gen_fcov_codegen --check and gen_knobs_codegen --check are up to date,
GEN_UT_FCOV_CODEGEN and GEN_UT_KNOBS_CODEGEN PASS, gen_unbuilt_mark_check PASS. The l46 and l47 logs are byte-unchanged
(md5 e9be074c5036cb62956ff71bc2b29bf7 and 1456cef854e37c0df572b29d05ca9b87, the values the corrigendum names); the two
new logs' manifest rows match their sizes and md5s; all seven files are ASCII-clean; the corrigendum's three quoted
l47 sentences exist verbatim at its :120, :122 and :128.

7.2 M-1 (the pre-state at an entry record) FIXED, traced and measured.
- The fix is one term at the one site that reads the pre-state: was = st.is_intr ? 1'b0 : irq_mstatus_prev[MIE]. Why
  st.is_intr is exactly the right discriminator: the RTL sets rvfi_intr for the first instruction of a trap handler
  only when the pc was set through EXC_PC_IRQ (rtl/ibex_core.sv:2403-2413, rvfi_set_trap_pc_d), that is for interrupt
  and NMI entries, which retire no record of their own while clearing MIE (ibex_cs_registers.sv:924). A synchronous
  exception is different in both respects: its faulting instruction retires a record with rvfi_trap, and the model
  state that record carries is the post-trap state, MIE already clear, so the handler's first instruction reads the
  right pre-state from the previous record and needs no override; the log's decision to leave st.is_trap alone is
  therefore correct, not merely cautious. Debug entry does not touch MIE.
- MEASURED on my build with the retained recipes, each run's own report: mret_mie1_mpie1_pending 0 in all four smokes;
  mret_mpie1_pending 173 (storm), 6 (lines), 39 (dbgstorm), 15 (fetchen); cp_mie_global_edge 2 of 7 in each; the two
  new counters read "mrets that are a handler's first instruction" 173 of 173, 6 of 6, 39 of 39, 15 of 15 and "wrongly
  booked stays-set" 0 in every run; all four verdicts PASS with referee 0. These are the l49 log's figures to the digit.
- The invariant the second counter states (nothing booked into the stays-set bin may be an entry record) is the
  discriminator rev56's Low and my M-1 asked for, and it is a run-summary line rather than a review argument.

7.3 L-2 (the parser) FIXED. sv_enum_members strips both comment forms before splitting and asserts each member is an
identifier; the unit test hand-lists the four members and checks the declaration still lists exactly those in order,
so it no longer shares the implementation's regex. Exercised by me on synthetic declarations: a // comment carrying a
comma parses to {A_ONE, A_TWO, A_THREE}, a block comment to {B_ONE, B_TWO}, an explicit value and a non-identifier
member die with the named reason.

7.4 L-1 (the mutation text and the cycle-zero wording) FIXED by the corrigendum: the mutation is printed as a diff
(the clear of the valid flag removed while the cycle is still cleared), the three cycle-zero sentences are quoted and
corrected, and the fetch-enable fixture is stated to have no reset window, which is what my three variants showed
(Section 5). The corrigendum also inverts the l46 and l47 logs' 173 narrative to the true reading and states why the
two-build comparison could not have caught a shared input; that matches the corrigendum I appended to
gen_critic_irq_step1.md Section 7.3.

7.5 The plan line. The plan line at 9bb1974 (gen_fcov_plan.md, the cp_mie_global_edge bullet; gen_test_plan.md and
gen_feature_list.md move only in their inputs-digest header, 7c0527c89b39) gives mret_mie1_mpie1_pending its class,
NOT-BUILT-STIMULUS, with the derivation in gating terms: a non-debug trap entry clears MIE (the csr_save_cause_i arm,
!debug_csr_save_i, !debug_mode_i, :924) and retires no record, so an mret shows MIE 1 before it only where the record is
not a trap entry and MIE is set at that point; this is the reading of L-5 and L-6 above and it names the debug guard
that the l49 log omits. Its survey of every mret site holds on my own census at 9bb1974: 22 files under gen_programs
and gen_directed emit mret; every mstatus write within six lines of an mret sets MPP alone (gen_cpuctrl_directed.S:36
and gen_dmem_err_directed.S:63 with 0x1800, gen_isa_cti_prog.py:849 and gen_csr_trap_setup_prog.py:771 and :781 with
MPP = M, gen_rst_boot_prog.py:330) or clears bits (gen_pmc_ctrl_prog.py:371, gen_pmp_csr_warl_prog.py:780); none sets
MIE; the vectors of gen_irq_directed.S and gen_nmi_long_directed.S are bare mrets; the irq generator's handler
(gen_irq_basic_prog.py:189-196) stores and returns. The measured outcome it reads at 021684d matches the companion
(both shapes leave the three mret bins uncovered, the return arm never fires, the only hit is the superseded
incidental one, the "only path" sentence withdrawn, the re-entry read from counts, the three limits carried, the
window consequence under the per-run rule); no bin is added or removed, the trace and mark checks pass
(gen_trace_check 2279/2205/74, gen_unbuilt_mark_check PASS, both codegen checks up to date at 9bb1974) and the three
documents are ASCII-clean. One precision point, not a defect: the line says the bin's only hit "to date" is incidental;
it is, and the companion's probe runs are unretained (L-4), so the line's measured clause rests on the companion's
words as the companion itself does. No item owns the bin and one is owed, as the line says. APPROVED.

7.6 Rows and verdict.
- L-3 (Low, records; disclosed and corrected inside the range). The l49 log's fixture sentence at its lines 55-56,
  "THE FIXTURE MUST WRITE mstatus.MIE BEFORE THE mret, with a line pending at the mret. That is the only path to
  (now && was)", is wrong, and tb-infra-2's companion gen_fu_l49_fixture_corrigendum.log (021684d, landing 50)
  withdraws it on its own measurement: in the retained probe pair (a handler that reports each entry, then sets MIE,
  then returns; one line held sticky 3000 cycles, or thirty short pulses) all three mret bins stay uncovered and the
  mret arm never fires; the sticky shape completes with 151 entries in 3000 cycles, so a handler that sets MIE with a
  line pending re-enters instead of retiring its mret; the bin's only hit to date is one incidental hit in a superseded
  timed-out storm probe. The RTL supports the inferred mechanism: a CSR write other than mscratch or mepc flushes the
  pipeline (rtl/ibex_id_stage.sv:595-599), and in the empty ID slot that follows, DECODE takes a pending enabled
  interrupt (rtl/ibex_controller.sv:703-711: no stall, no special request, nothing in ID or WB, handle_irq) before the
  mret is fetched, so the reachable shape is a line arriving after that bubble and before the mret's commit, a timing
  window. The companion states its limits (mechanism inferred from counts, one run incomplete, an arbitrary pulse
  spacing) and keeps the classification: not-built-stimulus, with the consequence that a windowed fixture could buy
  merged-report credit but never a declared bin under the per-run rule. Nothing in the classifier fix depends on the
  withdrawn sentence. The companion's probe programs and test were scratch and removed from the tree, so its figures
  (151 entries, 607 records, the two urg readings) rest on the log's words alone with no run directory retained; under
  the evidence-audit rule that is a records Low (L-4): retain the two probe runs' sim logs and urg excerpts beside the
  companion, or say where they live. The l49 log's bytes are unchanged, as the manifest row says.
- L-5 (Low, precision; raised by tb-infra-2 after the DV Lead corrected the citation; judged unreachable by me). The
  classifier's override treats every is_intr record's pre-state as cleared, citing an unconditional clear at
  rtl/ibex_cs_registers.sv:924; the clear sits under `else if (!debug_mode_i)` after `if (debug_csr_save_i)` (:911-927),
  so a debug entry and an exception in debug mode leave MIE alone, and "unconditionally" in the l49 log (:9), its
  corrigendum (:11) and the classifier comment (gen_fcov_pkg.sv:445 at 9a42c17) is imprecise. The gap is theoretical:
  st.is_intr is rvfi_intr, set only through rvfi_set_trap_pc_d on `pc_set && pc_mux_id == PC_EXC && exc_pc_mux_id ==
  EXC_PC_IRQ` (rtl/ibex_core.sv:2405-2410); EXC_PC_IRQ is driven only in IRQ_TAKEN (rtl/ibex_controller.sv:727),
  entered only through handle_irq = `~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q & (irq_nm | (irq_pending_i &
  irq_enabled)) & ...` (:498-500), while a debug entry drives EXC_PC_DBD (:766) and sets no marker. Every is_intr record
  therefore follows an interrupt or NMI entry taken outside debug mode, where :924 did clear MIE. Disposition: the
  one-term guard rides tb-infra-2's counter touch as hygiene; the three citations take a records corrigendum.
- L-6 (Low, records; the exception-entry question, raised by tb-infra-2, settled here from the source as hygiene). An
  exception also clears MIE through the same arm and rvfi_intr does not mark its handler's first instruction, so the
  override does not fire there; that is correct, because the classifier's pre-state is the ISA model's mstatus read by
  publish_state at the end of each record (gen_rvfi_pkg.sv:199-207, :583), after the model stepped that record. A
  trapping instruction is stepped and the trap is taken inside that step (the scoreboard requires `trap && retired ==
  0` from it, :518-520, and the next record's pc must equal the model's post-step pc, the handler, :514), so the trap
  record's published mstatus is post-trap with MIE clear, and the handler's first instruction reads the right
  pre-state from the previous record. The interrupt entry is the one event with no record: the model takes it only
  when the handler's first record arrives with intr (:352-376), so the interrupted instruction's published mstatus
  still has MIE set, exactly the case the override keys on. The fix is complete for programs with exception handlers;
  the l49 log's sentence "an entry retires no record of its own" should read "an interrupt entry", which rides the
  same records corrigendum as L-5.
- Conformance (dv_principles.md): the fix reads the entry's own effect rather than a neighbouring record; the
  discriminator is a collected counter; the two logs whose interpretation inverted are corrected beside, not inside;
  the parser's oracle is independent of its implementation.
CRITIC VERDICT: APPROVE for 9a42c17, 021684d and 9bb1974. The REQUEST-CHANGES of Section 5 on 03aafce..dc60063 is LIFTED on
this record: the mret-bin-and-hold-mirror group stands approved. Sections 1-6 and the corrigendum above are
byte-identical to the ec70820 commit (dc9e64def0536c4e).
