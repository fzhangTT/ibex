# Critic verdict: tb-infra landing 2c (commit cbadb7f, diff base bd75f16), reviewed as tb_l7

CORRIGENDUM to dv/auto_dv/docs/gen_critic_tb_l6.md:225 (frozen): the clause "the offset the API doc names (GEN_CSR_WRITE_TO_RVFI_OFFSET)
exists in no code or yaml" is false and withdrawn (LOG-072): the constant is declared in gen_tb_knobs.yaml, rendered into gen_tb_pkg.sv,
gen_knobs.py and gen_isa_shim_map.h and used in gen_checkers_pkg.sv; the rest of that L-9 (the pin read at the RVFI record, not in the
write's W-DEC window) stands. The clause was an artifact statement I adopted without re-running the check.

Base verdicts re-reviewed here: gen_critic_tb_fu2a.md (14def8c07df49bf8) M-1 / M-2 / M-5 / L-2..L-6, gen_critic_tb_l2b.md (6dc57b57174842d5)
M-2 and its lows, gen_critic_tb_l2b_v3.md (68d623446b7b243d), gen_critic_tb_l6.md (9c2e15956008be26) M-1..M-4.

Artifacts reviewed (committed blobs at cbadb7f; sha256 first 16 hex):

- dv/auto_dv/env/gen_rvfi_pkg.sv  cc8bc78d76a57505
- dv/auto_dv/env/gen_checkers_pkg.sv  1f967ca3935d4961
- dv/auto_dv/tb/gen_protocol_props.sv  a45f47f78ba89525
- dv/auto_dv/tb/gen_binds.sv  aea0cf20ebfce630
- dv/auto_dv/isa/gen_isa_shim.cc  eff6d5185976e8eb
- dv/auto_dv/isa/gen_ut_isa_shim.cc  991603011f5b4f6f
- dv/auto_dv/env/gen_fcov_pkg.sv  2c65c1fe75fd934b
- dv/auto_dv/tb/gen_tb_pkg.sv  8f916541eca76066
- dv/auto_dv/tb/gen_tb_knobs.yaml  6b415b8fbfed235b
- dv/auto_dv/env/gen_agents_pkg.sv  8160e436ce3ecad7
- dv/auto_dv/evidence/gen_tdd_step2b.md  5918f74bf9a00b51
- dv/auto_dv/mutations/gen_mut_step2b.md  5cd92a96dddc4679
- dv/auto_dv/mutations/gen_mut_t102.md  54d9b86b8d51f615
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  e5b3e08f0b51f372
- dv/auto_dv/docs/gen_component_api_scoreboard.md  d846857afa985358
- dv/auto_dv/docs/gen_component_api_irq_checker.md  9b8c8569fb4cb0d0
- dv/auto_dv/docs/gen_component_api_isa_shim.md  6fa3bbcf51e1eaeb
- dv/auto_dv/docs/gen_component_api_binds.md  0d7ef811471babeb
- dv/auto_dv/stim/gen_directed/gen_zcmp_dummy_popret_directed.S  f86bc2b11a34ef5f
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  b576669db6ef4104
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l7_sources_sha256_w.txt  e287c87e3fdf8a97
- the 156 added logs gen_fu_l7_* under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations}/ (manifest rows recomputed 156/156)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411,
doc/03_reference/exception_interrupts.rst, doc/03_reference/security.rst, rtl/ibex_core.sv:2343-2357 and :2379-2385 (the rd fields and
rf_wr_suppress), rtl/ibex_cs_registers.sv:918-935 and :967-974 (the recoverable-NMI stack), rtl/ibex_controller.sv:498-500 and :954-957,
LOG-037c, LOG-051, LOG-057, LOG-072.
Method: clean archive of cbadb7f; library self-test PASS, gen_knobs_codegen --check and gen_fcov_codegen --check up to date on the archive;
the flow self-test FAILS from the archive at cbadb7f and at its parent bd75f16 on Runtime's new build-input gate case, which runs
`git ls-files` and needs a git checkout; run from the clone root my invocation was refused by its A-002 root guard, so the flow self-test
is UNVERIFIED by me for this landing (the library self-test and both codegen --check runs pass); not a landing-2c item. Build identity checked
first-hand: the recipe of gen_tb_local.sh on the archive gives e287c87e3fdf8a97 under the UTF-8 sort, equal to build w in the 19 final run
headers and to the compile log, and the retained per-file list gen_fu_l7_sources_sha256_w.txt is byte-identical to my recompute over the 67
committed files. Two unnamed subagents (an evidence audit of the 156 logs; a code review of each rule against the docs and the RTL), both
told the fence and kept out of dv/auto_dv/reviews/; the findings below re-checked in the blobs. The cross-model artifact for cbadb7f was
not read before Sections 1-6; Section 7 reconciles.

CRITIC VERDICT: APPROVE, with the owed items named (the NMI pre-empt red; the tb_l6 M-2 / M-3 / M-4 items, which this landing does not touch)
and eleven lows. Every rule this landing claims is built, derived from the documented intent, and proven by a retained red with its
ablation, on a build whose sources are identified file by file.

## 1. What was verified

| rule | as built | intent anchor | red / green |
|---|---|---|---|
| T-183 suppressed-write gate | gen_rvfi_pkg.sv:476-487: `sup_ok = announced && (t.rd_addr == 0)` with `announced = gen_bus_err_log::take_intg_word(t.mem_addr)` (a per-word queue the data driver fills at grant, gen_tb_pkg.sv:543-554, gen_agents_pkg.sv:321); a flag without an announcement or with a written rd is an isa_rd miss (:482-483); the undo and the skipped rd compare only under sup_ok (:487, :524) | rtl/ibex_core.sv:2384-2385 (the flag needs an outstanding load with an integrity error and no rf_we) and :2354-2357 (rd fields cleared without a write); security.rst; LOG-037c | reds MUT-SUP (a clean c.lwsp flagged, 1 error naming 8000039c), MUT-SUPB (a clean c.lbu), MUT-SUP2 (the announced address off by 0x100: every real suppressed load refused), ablations `+gen_chk_isa_rd=0` PASS; green gen_fu_l7_intg_s7_allchk_*: 4979 records, 0 mismatches, 83 suppressed loads accepted, 54 internal NMIs, every checker at its default (on) |
| irq checker per-line release | gen_checkers_pkg.sv:114-118: an entry clears only the taken line (or the NMI) of each expectation and restarts the others' bound | exception_interrupts.rst: level-sensitive lines, priority order; a line raised beside a taken one is still owed its entry | red MUT-NT (irq_external tied 0 while held: 31 bound errors; the same mutant PASSED before the per-line rule), ablation PASS; greens lockstep_irq_storm 573 entries / 0 mismatches / 0 released, ut_irq_dir, rows_nmi_irqp |
| end-of-run never-taken rule (fu2a M-5) | :257-264: a line of an open expectation still on the pins with its mie bit set, enabled (mstatus.MIE or a lower privilege, or the NMI) and not in debug mode at report -> uvm_error irq_entry / nmi_entry under the entry knobs | a held, enabled line must eventually be taken (exception_interrupts.rst) | red MUT-NT2 (the line withheld from order 3572 on, simulator seed 3: 1 error "still held and enabled at the end of the run, never taken"; seeds 1 and 2 raised nothing in the tail and passed both ways, stated), ablation PASS |
| nmi_internal debug suspension and bound origin | :149: records in debug mode not counted (handle_irq closed in debug, rtl/ibex_controller.sv:498-500); GEN_NMI_INT_ENTRY_BOUND_RECORDS stays 4 and is declared TB-side | RTL anchor cited | red MUT-NIB (the bound at 0: 54 errors, one per announcement, `announced at order 497 (now order 498)`), ablation PASS |
| NMI pre-empt rule on a local flag (fu2a M-2) | gen_rvfi_pkg.sv:332-340: `intr_now` local; the monitor's transaction untouched; publish_state takes the flag as a parameter | rtl/ibex_core.sv:2402-2413 | the red is OWED and declared so in the scoreboard doc, the response row and the transcript; nmi_preempted = 0 in every retained run |
| external / internal NMI classification | :176-177, :359: the pin sample OR a raise of the NM line in the current or previous record's window (the irq driver's events subscribed) | the irq checker's two-record window; rtl/ibex_controller.sv:736-738 | greens with 1 NMI entry (seed 1) |
| protocol SVA fixes | knob names from PLUSARG_CHK_SVA_* / PLUSARG_CHK_ALL (:89-101); sva_alert_minor_window on ICACHE_ECC_WINDOW (:273) bound to GEN_ICACHE_ECC_WINDOW = 2; widths from TagSizeECC / LineSizeECC (:239, see L-2); dcsr prv through GEN_DCSR_PRV_BIT_*; header exception list names the two split covers; api_binds instance name gen_protocol_props_i | the companion table | reds MS-ICRAM (rtl copy of ibex_icache.sv: 397 sva_icram_tag_write_implies_req), MS-IRQ (irq_timer_i X: 2 sva_irq_pins_known), MS-DBG (debug_req_i X: 2 sva_dbg_req_known), MS-ALERT (rtl copy of ibex_core.sv: 2851 sva_alert_internal_never), each under `+gen_chk_all=0 +gen_chk_sva_<group>=1`, ablations PASS; the inert ibex_top.sv form recorded and not counted |
| shim recoverable-NMI stack (fu2a L-3) | gen_isa_shim.cc:456-459, :483: every exception entry outside debug mode pushes the stack; restore on mret in NMI mode (:497-505); mstatus shifts from the MSTATUS_* masks; the NMI causes named once | rtl/ibex_cs_registers.sv:918-933 (mstack_en on any entry outside debug), :967-974; rtl/ibex_controller.sv:954-957 | unit test section 12b: 6 failures on a shim without the push (gen_fu_l7_ut_isa_shim_red_nested.log), PASS (0 failures) on the landed shim, both stamped with shim and test shas |
| witness covergroup weight 0 (l2b L-1) | gen_fcov_pkg.sv:20 `option.weight = 0` | the addendum's promise | greens ut_witness / ut_witness_nofcov; WM2 (the bookkeeping records index 0): caught by wit_referee alone with the unit test's own asserts passing; its fcov-off ablation is not clean (the mutant also breaks the bookkeeping count, so the unit test's own assertion fails) and the record says so |

Evidence: 156 manifest rows recompute (md5 and bytes) and the working-tree copies equal the blobs; 41 run headers all carry build shas, 12
distinct, each equal to its compile log; every mutant's "original sha256" equals the committed blob of the mutated file (gen_tb_top.sv,
gen_tb_pkg.sv, gen_fcov_pkg.sv, rtl/ibex_icache.sv, rtl/ibex_core.sv) and the batches' tree-line hashes equal the committed blobs; the
retained per-file list identifies build w file by file (Method). No compare removed and no error demoted; the one tolerance change is
GEN_ICACHE_ECC_WINDOW 1 -> 2, shared by the misc rule and the SVA (L-3).

## 2. Closure of the base verdicts

- gen_critic_tb_fu2a.md: M-1 (rf_wr_suppress on the DUT flag) CLOSED by the gate and its three reds; M-2 (t.intr written into the shared
  transaction) CLOSED as a mechanism (intr_now), its red still owed and declared; M-5 (the bound restarts at each entry) CLOSED by the
  per-line release and the end-of-run rule with MUT-NT / MUT-NT2; L-2 (figures without logs) closed by withdrawal; L-3 (the mstack)
  CLOSED with 12b; L-4 (mutation record text blocks) closed as far as the record allows (P1..P9 stated as not retained); L-5, L-6 closed.
- gen_critic_tb_l2b.md: M-2 (four SVA groups without a catching mutant) CLOSED by MS-ICRAM / MS-IRQ / MS-DBG / MS-ALERT; L-1 (weight 0)
  closed in form (L-8 below); L-2, L-3, L-4 (the split rule: stated as unowned, covers), L-5 (the ECC window), L-6, L-7, L-8, L-9 closed;
  L-16 / L-17 were closed in v3. M-1 is T-226's (closed on the code, gen_critic_t226_v2.md). With M-2 closed, the landing-2b thread has
  no open medium.
- gen_critic_tb_l6.md: M-1 (build identity) CLOSED for this landing by the retained per-file list (the mechanism that landing 6 lacked),
  and landing 6's own identity is still owed with the CR-L6 rows; M-2 (the malformed move pair), M-3 (the unit test's vectors and its
  red) and M-4 (the referee's red and coverage) are NOT touched by 2c (gen_fcov_pkg.sv changes by the one weight line) and stay owed to
  tb-infra's next touch, as the Orchestrator's hand-off says.

## 3. Findings

### L-1 (low) [S2 gate precision] The suppressed-write gate's word queue can be satisfied by a stale store announcement, and skips spanning second beats and Zcmp micro-ops

note_intg announces every data-side corruption at grant, stores included (gen_agents_pkg.sv:321), while only loads can raise the flag
(rtl/ibex_core.sv:2385); a store's word stays in intg_words until consumed and would vouch for a lying flag on a later load of the same
word (the MUT-SUP class slips at that address). The lookup uses the record's effective address masked to its first word, so a corruption
injected on the second beat of a spanning load is not found (a false, loud isa_rd miss). Inside a Zcmp sequence the gate is bypassed
(`!is_seq`, :479) and the union compare judges. Required: announce loads only (or consume store words at the store's completion), look
up both words of a spanning access as the bus-error path does, and state the Zcmp bypass in the scoreboard doc.

### L-2 (low) [S6 a check that cannot fail] sva_icram_widths became tautological

gen_protocol_props.sv:239 compares the port widths with TagSizeECC / LineSizeECC passed by the bind from gen_dut_top, whose localparams
size those very ports (gen_dut_top.sv:80-81). The literal 28 / 78 was the only independent width check; CM43-L-1 asked for the ibex_pkg
derivation (IC_TAG_SIZE + IC_TAG_ECC_SIZE, BusSizeECC x IC_LINE_BEATS), not the wrapper's parameters. Compare against ibex_pkg or drop the
assertion.

### L-3 (low) [S4 provenance] GEN_ICACHE_ECC_WINDOW 1 -> 2 with an unsupported "measured" origin

The yaml desc says landing 2b measured 1 or 2; no retained artifact carries such a measurement and the same documents say no icache ECC
injection exists (CM43-M-1: no red possible). State the value as a declared bound without a measured origin until an injection exists.

### L-4 (low) [S2] The end-of-run rule has no grace window and no starvation exemption

A raise landing in the last records of a run cannot be served and would fire; a line legitimately starved under a hold that never
releases (a direct STICKY, or through_handler without an ack) would fire; the NM line held at the end inside NMI mode would fire
nmi_entry although nested NMIs are ignored by design. None fires in the retained greens (until_taken releases at entry; the NM pulse is
one cycle). State the preconditions in the irq checker doc, or bound the tail (a raise younger than the entry bound at report is not
owed).

### L-5 (low) [S4 record] The pre-empt rule's one-record window and the sweep's single NMI

The pre-empt rule consumes after_nmi_entry at the next record, so it covers an NMI handler whose entry record is itself the mret (the
storm image); a longer handler would diverge loudly, which the documents do not say. The "six-seed with-NMI storm sweep" behind
nmi_preempted = 0 contains one NMI entry in total: seeds 2-6 report nmi=0 (5 of 5 excerpts checked). State both beside the owed red.

### L-6 (low) [S4 record] Record errors

gen_mut_step2b.md's MUT-NT2 row names build 2643308399b05e33 (present in the record) where the retained header, compile log and
batch log say 4e4a02897de732d3 (2643308399b05e33 is the batch whose runs died on an unknown plusarg); MUT-SUP2 "FAIL (UVM_ERROR 83)"
where the excerpt header counts 421 UVM_ERROR lines and no UVM summary exists (83 is the green run's suppressed-load count); "573 rows"
for gen_fu_l7_lockstep_irq_storm_export_irq_entry_rows.txt, which retains 199 rows (573 is supported by the GEN_SB / GEN_IRQ_CHK lines);
the scoreboard doc's row 130 keeps "on the DUT's flag alone" in front of the gate text it now describes (a stale fragment inside one
row); the irq checker doc's nmi_entry row still attributes the mstack restore compare to the checker while Section 1 assigns it to the
shim rows.

### L-7 (low) [S4 provenance] The shim red is a retro-fitted variant, not the pre-2c shim

gen_fu_l7_ut_isa_shim_red_nested.log is stamped shim sha256 46324b7522a4dda3, which is neither bd75f16's gen_isa_shim.cc
(76293bbdd49351b1) nor cbadb7f's (eff6d5185976e8eb), and its compiler warnings name 2c symbols; it is the landed shim with the push
removed, run after the green. That is a valid mutant-style red; the record's "red on the pre-2c shim" is not what the log shows. Say
"the landed shim with the stack push removed".

### L-8 (low) [S4 precision] option.weight = 0 on a per_instance = 0 covergroup

A covergroup-level option.weight weights the instance score; the type-based total urg reports uses type_option.weight, which is not
set, so whether the ledger group leaves urg's own total is not shown by this line and no retained report demonstrates it. The comment
already names Runtime's by-name exclusion as the mechanism of record; say in the addendum that weight 0 is not shown to move urg's
total, or set type_option.weight as well.

### L-9 (low) [S6 record] The one-record latency claim is half-evidenced

"MUT-NIB with the bound at 1 PASSED both runs, so the latency is exactly 1 record" rests on a batch-log line for build 16b938ccd6021cc1
with no retained header, compile log or line stating that build's bound; the bound-0 side (54 errors, `announced at order 497 (now order
498)`) is retained. Retain the bound-1 run's header and its constant, or word the claim as the bound-0 evidence supports it.

### L-10 (low) [S4 record] Unlabelled red and unretained incidental reds

The B8 vehicle gen_fu_l7_lockstep_zcmp_dummy_popret_* (9408 errors, red by design) has a manifest row without the "red by design" label
the excerpt header carries; the "unregistered writer" FATAL of the first build with the irq_entry row and the "codegen --check up to
date" claim have no retained log (I reproduced --check up to date from the archive myself).

### L-11 (low) [S6 provenance] Mutant bases straddle builds u, v and w

The mutants are said to be built from the wit_root copy between builds v and w; MS-ICRAM's build sha is build u's, MS-IRQ / MS-DBG
precede the first retained build carrying the per-line release, and MUT-NIB / MUT-NT2 postdate build w's runs. Each mutant's original
file sha equals the committed blob, so the mutated files are identified; the sentence should name the base per mutant rather than one
interval.

### Informational

- I-1: WM2's ablation is not clean and the record says so; the referee's own proof is the catch run with the unit test's asserts
  passing. Acceptable as recorded.
- I-2: the flow self-test's new build-input gate case needs a git checkout and fails from a plain archive at cbadb7f and at bd75f16
  alike, and my run from the clone root was refused by its A-002 root guard; unverified by me. A note for Runtime's self-test, not a
  landing item.
- I-3: greens are run at default knobs (no +gen_chk plusargs), which is the "every checker on" state; no retained line names the SVA
  groups' enable state.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: the gate, the per-line rule, the end-of-run rule
and the stack follow the documented behaviour and the RTL anchors (conforming; L-1, L-4 name the corners); S4 honesty: the owed red
declared everywhere, the withdrawn figures withdrawn, record errors listed (L-6, L-7, L-9, L-11); S5: knob names from the constants home
(conforming); S6 trust triad: every new rule has a retained red and ablation on an identified build (conforming), one existing check
made vacuous (L-2). One-line verdict: PASS with the lows.

## 5. Owed after this landing

The NMI pre-empt red (a directed raise-then-NMI timing program); the tb_l6 items M-2 / M-3 / M-4 and landing 6's own per-file identity;
the CR-L6, CM98, CR-4, CR-5, CR-6, CM81 rows, the CM60 delta record, the T-235 sizing section and the B8 probe bind, all named by the
Orchestrator as tb-infra's next touch.

## 6. Verdict

CRITIC VERDICT: APPROVE. Landing 2c closes every medium of the fu2a and l2b threads with a retained red and ablation on an identified
build; the tb_l6 mediums M-2 / M-3 / M-4 and landing 6's own identity remain owed and are not claimed closed here; the eleven lows go to
tb-infra's next touch with the CR-L6 rows.

## 7. Reconciliation with the cross-model artifact (read after Sections 1-6)

dv/auto_dv/reviews/2026-09-03-claude-diff-bd75f161-cbadb7f8.md (55 lines): APPROVE-WITH-CHANGES, one medium and nine lows. Re-checked in
the cbadb7f blobs:

- Its medium (the spanning load's second-half corruption is not found by the gate: a false, loud isa_rd miss) is the second clause of my
  L-1, found independently. Level disagreement, stated: a false loud miss on a case no retained run exercises is a stimulus limitation
  that cannot hide a defect, so Low here; the silent side of the same gate (its Low: store announcements vouching for a later lying
  flag) is the clause of L-1 I weight. Both fixes are required either way.
- Its MUT-NT2 build-sha, provenance-interval and 574-rows lows are my L-6 / L-11, found independently.
- Adopted and verified: the CM43-L-3 response row names gen_protocol_props.sv as the DCSR consumer while the slice is in
  gen_checkers_pkg.sv:300 (row 54 of the response file; verified); the dbg_dret message still prints `dcsr_q[1:0]` beside the constant
  compare (gen_checkers_pkg.sv:303; verified); `never_taken` is counted but absent from the GEN_IRQ_CHK summary line, so a green log
  cannot show the end-of-run rule ran (:262-267; verified; joins L-9's class: a rule whose green side leaves no trace); the end-of-run
  rule has no `!nmi_mode` term although the DUT masks every line in NMI mode (rtl/ibex_controller.sv:498; :261 verified; sharpens my
  L-4's third case to all lines, not only the NM line); the parameter default ICACHE_ECC_WINDOW = 1 disagrees with the yaml's 2 and the
  window form `$past(x,1) || $past(x,N)` is two points, not the 1..N range the comment says (gen_protocol_props.sv:16, :273; verified;
  joins L-3). All five are lows; they are added to the list owed to the next touch.
- Not in the artifact: L-2 (the tautological width assert; the artifact's assertion-integrity rubric says "no assertion removed or
  weakened", which I dispute: a check that cannot fail is a weakened check), L-3's "measured" origin, L-5, L-7 (the red's shim sha),
  L-8, L-9, L-10 and the row-130 fragment of L-6.
- Verdict levels agree in substance: no medium open on landing 2c itself; the artifact's changes and my lows are the same next touch.
