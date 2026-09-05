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
