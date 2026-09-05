# Critic verdict: feature group irq-checker-fix, range 65b7cb0..9c7f8f6 (one commit, landing 52)

Artifacts (sha256 first 16 at 9c7f8f6):
- dv/auto_dv/env/gen_checkers_pkg.sv 37206a966a08ea04
- dv/auto_dv/env/gen_agents_pkg.sv c271ef7cce08c653
- dv/auto_dv/env/gen_fcov_pkg.sv 7eff3ce75a1b404b
- dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py 4ecb66cf507e9ebb
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l52_irq_entry_bound.log af0eeb37d9b3d23e
Date: 2026-09-05T10:59:02Z. Role: Critic (the reviewer other than the author). Range named by the Orchestrator: 65b7cb0..9c7f8f6, the
one commit 9c7f8f6 (tb-infra-2 landing 52; six files). Method: the diff read in full; the checker's new mask traced
against the RTL take condition; the landing's red, mutation and parser claims re-derived on my own compiles of detached
worktrees of 9c7f8f6 (TB-source identity 77b9ac313955dc59), of the range start 65b7cb0 (fd9ba5b4ffae6a3c) and of
9c7f8f6 with the interrupt input tied low (c7dddfbf0017e908), using the wave's own failing runs and the retained smoke
recipes; my logs under dv/auto_dv/work/critic/irqchk/ (README.txt with the commands). Exposure: the Orchestrator's
range message listed the points to judge; rev59 runs on the same range and is read only for Section 6.
dv_principles.md sha256 d9c27db18f511411, unchanged.

## 1. Gates, identities, records

On the 9c7f8f6 worktree: gen_fcov_codegen --check and gen_knobs_codegen --check up to date, GEN_UT_FCOV_CODEGEN and
GEN_UT_KNOBS_CODEGEN PASS, gen_unbuilt_mark_check PASS; gate key fb0798b2432ca7e1 (3219e5ceb2426c90 at 9bb1974); the
TB-source digest 77b9ac313955dc59 is what my compile printed. The l52 log names its build only as "compile rc=0" and
prints no sources sha256 (L-1). The retained log's manifest row matches its size and md5 (9116 bytes,
fe418c61e39bf272f2814ec581a82794); all six files are ASCII-clean; the checker comment the log quotes ("NMI mode and
debug mode mask every line ...") exists at gen_checkers_pkg.sv:136 at 9c7f8f6; gen_dut_top.sv at 9c7f8f6 has md5
56041635e557a5531283918982a3f37f, the value the log gives before and after its mutation.

## 2. The checker fix, traced against the RTL

- The defect: an expectation's bound accrued over records on which the DUT was right to withhold, because the global
  enable was tested only at expiry, where it had already been restored by the mret. The fix advances every open
  expectation's baseline on each record while a mask holds, before the expiry test (gen_checkers_pkg.sv:122-129 at
  9c7f8f6): masked = nmi_mode || st.debug_mode || (!st.mstatus[MIE] && st.prv == PRIV_LVL_M). Against the RTL's take
  condition (rtl/ibex_controller.sv:498-500: handle_irq = ~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q & (irq_nm
  | (irq_pending_i & irq_enabled)) & !(instr_gets_expanded_i == INSTR_EXPANDED_COMMIT), with irq_enabled =
  csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U) at :490): for a REGULAR line the three masked terms are the RTL's
  three and the U-mode qualification is exact. For an NMI expectation the mask is wrong in one term: the RTL takes
  irq_nm regardless of irq_enabled (the OR at :499), so MIE clear in M-mode does not withhold an NMI, yet the new step
  advances EVERY expectation's baseline while MIE is clear, expects[i].nmi included, where the expiry test at :140 still
  judges an NMI expectation regardless of MIE. A withheld NMI raised while MIE is clear in M-mode can therefore never
  expire while that state lasts (M-1). Two further RTL withholding terms are not masked for regular lines, single step
  outside debug mode and the Zcmp expansion's commit phase (L-2); the log says both were measured absent in its
  fixture, which is true of that fixture and not of the tree.
- Why the per-record form and not a restart at expiry: the enable mask lifts exactly at the mret and the bound expires
  just after, so an expiry-time restart never observes it; the log measured this (every fire reports mstatus 0x88, MIE
  already set) and my reproduction below confirms the mechanism by outcome.
- The message now prints the raised lines' enable bits through gen_irq_lines_to_mie_bits (gen_agents_pkg.sv:527-530),
  which builds them from gen_irq_mie_bit and so is not a second copy of the mapping; line 18 (NM) is deliberately
  unmapped. My fire lines below read "lines 00004 (enable bits 00000800)" and "lines 00020 (enable bits 00040000)": line
  2 to bit 11 and line 5 to bit 18, both right.

## 3. Red, green and mutation, reproduced

- The red on the entry that failed the wave. gen_test_irq_basic at wave seed 159577667 with the wave run's own program
  image (crc32 03c84170, 217 words) and plusargs, on the range-start build: 17 [irq_entry] fires and 17 UVM_ERRORs, the
  wave's own count, the first "lines 00001 raised at cycle 199 (order 23) not taken within 17 records (now order 42, mie
  7fff0888 mstatus 00000088)"; on the 9c7f8f6 build: 0 fires, 0 UVM_ERROR, the entry's GEN_TEST_PASS printed. The fix
  removes the false fires on a real failing seed, not only on the log's fixture.
- The seed the log says is owed. Wave seed 1207954461 fires 258 times on BOTH builds with 693238 UVM_ERRORs of other
  kinds (450021 sva_ibus_outstanding_max, 70208 sva_rvalid_legal, 70208 sva_ibus_rvalid_outstanding, 23387 isa_insn,
  23384 isa_pc, 23369 crash_dump), the ruled T-044 property firing at cycle 6587 and the ibus properties from cycle 9246
  before the first irq_entry fire at order 742. It is one of the two ibus-signature runs rtl-arch read at d8afbfd (its
  table names 1207954461 with the same firing counts). Its irq_entry fires are downstream of that breakdown (the core
  trapping continuously at pc 80000022 with insn 00000000), not the masked-window mechanism, and this landing neither
  fixes nor claims them; the log's owed pass criterion ("it should collapse to zero with the rest") is answered here:
  it does not collapse (L-4).
- The mutation MUT-IRQWITHHOLD, re-fired by me with gen_dut_top.sv's .irq_external_i connection tied to 1'b0 (my first
  attempt matched no parenthesised port and left the file unchanged; those runs were clean-build runs and are retained
  as such). Quiet fixture (gen_ut_irq on the directed interrupt program): CATCH 1, "lines 00004 (enable bits 00000800)
  raised at cycle 1802 (order 361) not taken within 17 records", and 0 with +gen_chk_irq_entry=0, so the named rule is
  what fires. Storm fixture (gen_ut_lockstep on the NMI-long program under the storm regime): CATCH 12. The clean build
  fires 0 on both. The log's storm arm read CATCH 0 on its fixture and states the sensitivity reduction from it; on the
  retained storm smoke the fixed checker still catches the withheld line twelve times, so the reduction is
  fixture-dependent rather than a property of the storm regime (L-3).

## 4. The invariant, the helper, the parser test, the rev57 rows

- The two-route invariant counts a stays-set booking when this record is an interrupt entry OR the previous record
  trapped (gen_fcov_pkg.sv:474 at 9c7f8f6) and raises GEN_FCOV_REF when non-zero (:2905), so it is collected. Both routes
  are zero by construction of the current classifier (the override for is_intr; the post-trap model state for a trap
  predecessor), so the counter witnesses a future regression of either pre-state source and not today's behaviour; the
  log says it cannot be exercised, which is the honest limit.
- The parser test: three synthetic declarations with a hand-written expected tuple. Its red reproduced by me against
  the pre-fix codegen (dc60063's file swapped into the worktree): FAIL x4 (the two comment cases, parse and ordinals),
  the no-comment control PASS; restored, GEN_UT_KNOBS_CODEGEN PASS (0 failures). The oracle is independent of the
  parser's regex.
- rev57's rows carried here, each seen in the diff: the misplaced counter comment moved to n_irq_mret_masked; the
  review reference removed from the invariant's comment; the "unconditionally" comment now names the debug guard and
  the rvfi_intr scope; a trapping mret excluded from the arm (st.is_trap).

## 5. Conformance, rows, verdict

Conformance (dv_principles.md): the checker fails through the collected mechanism it always had, now on the right
records; the invariant is an error, not a print; the message states its mapping; the mutation proves the fixed rule
still fires on a genuine withhold with the ablation clean; the log discloses the sensitivity consequence and the
unfixed seed rather than hiding them.
- M-1 (Medium, checker weakening; tb-infra-2; MY MISS in the first draft of Section 2, corrected above). The per-record
  mask applies the MIE term to NMI expectations (gen_checkers_pkg.sv:127-129 at 9c7f8f6 advance every expects[i]),
  while rtl/ibex_controller.sv:498-499 takes irq_nm without irq_enabled and the pre-fix expiry test at :140 (kept) judged
  an NMI expectation regardless of MIE. So while MIE is clear in M-mode (every regular handler, reset until the program
  enables interrupts, the with_nmi storm mix) a withheld NMI's bound cannot expire and nmi_entry cannot fire; the log's
  mutation ties only the external line low and never exercises the NMI path. MEASURED by me: gen_ut_irq_nmi_long on the reset-reads program (which never sets MIE, so mstatus stays 0x80)
  with gen_dut_top.sv's .irq_nm_i tied to 1'b0, on the range-start build: nmi_entry fires once, "lines 40000 raised at
  cycle 1361 (order 200) not taken within 17 records (now order 218, mie 00000000 mstatus 00000080)"; on the 9c7f8f6
  build with the same mutation and recipe: 0 nmi_entry fires and 0 UVM_ERROR while the test itself reports the NMI not
  taken within 4000 cycles; on the clean 9c7f8f6 build the same recipe takes the NMI and the test passes. The fixed
  checker is blind to a withheld NMI under MIE clear where the pre-fix checker caught it. Fix: apply the MIE term per
  expectation, masked_i = nmi_mode || st.debug_mode || (!expects[i].nmi && !MIE && prv == M), and add an NMI-withhold
  control (irq_nm tied low, a program that never sets MIE) to the log.
- M-2 (Medium, semantics against the stated rule; tb-infra-2 with the DV Lead). The comment and the commit message say
  the bound "accrues only over records in which the interrupt could be taken"; the code resets the baseline on every
  masked record, discarding unmasked records already accrued, so the bound fires only on 18 or more CONSECUTIVE unmasked
  records. The log discloses the consecutive behaviour as a sensitivity reduction, but the comment states accrual, and
  the two differ on any raise-unmasked-mask-unmasked sequence. On the retained storm smoke the fixed checker still
  catches a withheld line twelve times (Section 3), so the reduction is fixture-dependent, not a property of the storm
  regime as the log generalises. Fix: a per-expectation unmasked-record count (increment on unmasked records, reset at
  entries as :112 does, compare to the bound), which is the stated semantics, needs no second expectation and restores
  sensitivity across masked gaps; or reword the comment and the plan's bound line (gen_test_plan.md:6792) to "restarts".
- L-1 (Low, records). The l52 log prints no compile identity, and its A/B, structural-fix and mutation blocks name no
  fixture, plusargs or out directory while closing with "every figure above is produced by the command printed above
  its block"; the figures are internally consistent and not reproducible from the log. Append the commands.
- L-2 (Low, checker scope; the DV Lead and tb-infra-2). The mask omits two RTL withholding terms for regular lines:
  single step outside debug mode (dcsr.step, available as st.dcsr) and the Zcmp expansion's commit phase (up to the
  sequence length in micro-op records, not in gen_model_state). No committed fixture drives interrupts across Zcmp
  today (gen_zcmp_irq_directed.S has no testlist entry), so this is latent. Mask both, or state them as known exclusions.
- L-3 (Low, invariant precision). The is_intr route of the two-route invariant is zero by construction against the
  current classifier (the override at :449 forces was to 0), so it guards the classifier rather than measures the model;
  the prev_trapped route reads the published mstatus and can fire, and has one false-positive path: an exception taken
  in debug mode leaves MIE untouched (rtl/ibex_cs_registers.sv:918), so prev_trapped with MIE 1 followed by an mret with a
  line pending would raise GEN_FCOV_REF on a legitimate booking. Record prev_trapped = st.is_trap && !st.debug_mode at
  :505 and say in the comment which route guards what. (My Section 4 said both routes are zero by construction; the
  second is not, as this path shows.)
- L-4 (Low, records; rtl-arch and runtime-2). Seed 1207954461 does not collapse on the fixed checker; it is the
  ibus-signature run of d8afbfd and its 258 fires follow the protocol breakdown. Say so where the re-run of the thirteen
  is recorded, so the seed is not counted against this fix.
- L-5 (Low, test hygiene). The three new parser cases write their synthetic .sv under tempfile.mkdtemp() in the system
  temp directory and never remove it, against the file's own docstring (scratch under dv/auto_dv/work/tb-infra/
  ut_scratch). Write them under SCRATCH and remove them.
- Info. My runner derives the pass marker from the module name (GEN_TEST_IRQ_BASIC_PASS) while the Test Writer's
  entries print GEN_TEST_PASS; I graded the fixed run by the printed marker and the zero error count.

CRITIC VERDICT: REQUEST-CHANGES, confined to M-1 (the MIE mask applied to NMI expectations, a weakening of nmi_entry
against the RTL's take condition) and M-2 (the reset-on-mask form against the stated accrue-only semantics). APPROVED
within the group: the per-record masking of regular lines (red and green on a failing wave seed, 17 fires to 0 with the
entry passing; the withheld-line mutation caught by the named rule alone on the quiet fixture and twelve times on the
storm smoke); the mapping helper as one copy; the two-route invariant as a referee error; the parser test with its
independent oracle, red against the pre-fix parser; the rev57 rows. L-1..L-5 owed as disclosed. Re-review on the NMI
term with its own withhold control and on the accrue-or-restart decision.

## 6. Reconciliation with the cross-model range review rev59 (written 2026-09-05T11:03:51Z)

Artifact: dv/auto_dv/reviews/2026-09-05-claude-diff-65b7cb00-9c7f8f63.md, committed 5df6403, sha256 46b0dcec44541017,
45 lines, verdict REQUEST-CHANGES, read after Sections 1-5 were drafted. Exposure: the Orchestrator's range message listed
the points to judge; rev59's rows were not summarised to me before I read it.

Agreement, and the order of events stated plainly: my Sections 1-5 as first drafted approved the landing with the
sentence "the NMI expectation is judged by the same arm with the same masks". rev59's Major says the opposite and is
right: the RTL takes irq_nm without irq_enabled, so the MIE term must not advance an NMI expectation. I re-read
rtl/ibex_controller.sv:498-499 and gen_checkers_pkg.sv:127-129 and :140, found the reading correct, measured it with
the NMI-withhold control above, and changed my verdict to REQUEST-CHANGES with M-1; the miss is mine and is recorded in
Section 2 and M-1. rev59's Medium (the reset-on-mask form against the stated accrue semantics) is my M-2, which my first
draft carried as a Low on the plan owner's question; rev59's framing, that the comment states accrual and the code
resets, is the contradiction that makes it a Medium, and the cumulative count it proposes is the same remedy I reached.
Its Low on the invariant (the is_intr route zero by construction; the prev_trapped route's debug-mode false positive)
is my L-3, corrected there from my first draft's "both routes zero by construction". Its Low on tempfile.mkdtemp() is
my L-5. Its Low on the log's unreproducible figures is folded into my L-1. Its verifications (the take condition, the
post-state semantics, the helper, the is_trap exclusion, the parser red, the log's md5 and the referee placement) match
Sections 1-4, which add the wave-seed red and green, the storm-fixture catch count and the seed-1207954461 attribution.

Disagreement: none. Verdict words agree: REQUEST-CHANGES, confined to M-1 and M-2.

## Corrigendum to Section 3 (appended after the HOLD of 2026-09-05; the sections above are unchanged)

Raised by tb-infra-2's landing-54 log, which reproduces every figure I state for the 9c7f8f6 run of seed 1207954461
and corrects one sentence; checked against my own retained records under dv/auto_dv/work/critic/irqchk/.

- "its table names 1207954461 with the same firing counts" is WRONG. rtl-arch's table
  (gen_ibus_props_irq_signature_reading.md:51-54) gives 70199 sva_ibus_rvalid_outstanding and 449948
  sva_ibus_outstanding_max for the 4017573 wave run of that seed; my run on the 9c7f8f6 build gave 70208 and 450021.
  Two runs of one seed on two builds, the same signature and the same ordering (the T-044 property first, the ibus
  properties from cycle 9246, the irq_entry fires downstream), different counts. The attribution to the ibus-signature
  mechanism rests on the signature and the ordering and stands; the words "the same firing counts" do not.
- "on the clean 9c7f8f6 build the same recipe takes the NMI and the test passes" overstates the control. My retained
  record (nmi_withhold_demonstration.txt, nm_fix_clean) reads: nmi_entry fires 0, GEN_UT_IRQ_NMI_LONG_PASS with retired
  400 and 0 mismatches, and TWO UVM_ERRORs with the run's verdict FAIL. The test's own marker passes; the run does not.
  tb-infra-2's diagnosis, consistent with the tree: the reset-reads program installs no NMI handler and the NMI vector
  (mtvec base 0x80000000 plus 4 x 31 = 0x8000007c) lies below the linker script's PROG origin 0x80000080, so the entry
  double-faults. The control's claim is therefore "nmi_entry fires zero times on the clean build", not "a clean run".
- A counting note for anyone re-deriving my totals: a `grep -c UVM_ERROR` over a sim.log counts the UVM summary tally
  line as well and reads one high. My retained "all UVM_ERROR" counts excluded it (seed 159577667: 17 fires and 17
  errors; the NMI control: 2), so no figure above moves; the 693238 total is reproduced by tb-infra-2 exactly.

## 7. Recorded re-verdict on 65b7cb0..b9e5fad, the irq checker group (landings 52 and 54, the re-run block; HOLD sent to the Orchestrator first; Sections 1-6 and the corrigendum unchanged)

Artifacts at b9e5fad (sha256 first 16 hex): dv/auto_dv/env/gen_checkers_pkg.sv 8e412507010d6fd0; dv/auto_dv/env/gen_fcov_pkg.sv
a397c8fcf0201eb6; dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py f869797e5cc74fb1;
dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l54_irq_nmi_mask_accrual.log 76959296e8897242;
dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l52_commands_corrigendum.log 5f4c3f03c8acdbbe; dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md
4345983379320a55. Method: the checker diff read against rtl/ibex_controller.sv:490-500; both reds re-run by me on my own compiles of
detached worktrees of b9e5fad (clean 861209d7f0fd1ed1; the NMI input tied low 1fdf071ecc24a5bc; every interrupt input tied low
88ac45f0791b01e7; the external line alone tied low df807317bf3d36fe) and of c045115 with the same all-lines mutation (854a96f43286b4d2;
its checker is byte-identical to 9c7f8f6), with
the landing's toggle program rebuilt by me from the source in the shared scratch (md5 equal to the log's, image md5 equal) and the l52 long-handler fixture from the same scratch (image md5 equal to the
commands corrigendum's); the six smokes, the wave seed and the standing irq red fixture re-run on the clean build; the records
checked against the blobs. Exposure: the Orchestrator's earlier
messages named rev59's rows and tb-infra-2's landing message summarised the fix before this section; rev60 is read only in Section 8.
Logs: dv/auto_dv/work/critic/irqchk2/.

### 7.1 M-1, the NMI term: closed

The mask is decided per expectation (gen_checkers_pkg.sv:140-141 at b9e5fad) with the MIE term qualified on !expects[i].nmi, which
is the fix I named; nmi_mode and debug_mode still mask every expectation, matching ~nmi_mode_q and ~debug_mode_q at
rtl/ibex_controller.sv:498. Re-derived by me (Red A, gen_ut_irq_nmi_long on the reset-reads program, the NMI input tied low): the
fixed build fires nmi_entry once with the line "lines 40000 (enable bits 00000000) raised at cycle 1361 (order 200) not taken within
17 records (now order 218, takeable records 18, mie 00000000 mstatus 00000080)", the same cycle and order numbers as the
pre-landing-52 checker in my Section 2 measurement; with +gen_chk_nmi_entry=0 the run carries zero errors, so the named rule is the
fire; the pre-fix arm is my 9c7f8f6 record (zero fires, zero errors, blind). Closed.

### 7.2 M-2, accrual: closed, with the semantics the plan needs

expect_t carries an unmasked count (:39-41) incremented once per record in which that expectation could have been taken, reset only
at the entry restart (:118), incremented at :143 and compared against the bound (:144); masked records neither spend nor judge (:142). Re-derived by me (Red
B, gen_ut_lockstep on the MIE-toggle program, six takeable records then six masked, six times, every line tied low): the fixed build
fires irq_entry once with "raised at cycle 181 (order 40) not taken within 17 records (now order 82, takeable records 18, mie 7fff0888
mstatus 00000088)", forty-two records elapsed and eighteen takeable, the composition 408 [irq_pending] + 1 [irq_entry] against 408
with the named check off; the pre-fix build with the same mutation and program fires zero times (408 [irq_pending] only), because
its restart needed eighteen consecutive takeable records and the longest run is six. That is the numerical separation of the two
semantics I asked for, and it is the case the plan's set_pending bin asserts. The l52 vacuity regime (no takeable stretch of 18) is
therefore no longer vacuous: the accrued count judges it. Closed. The DV Lead's owed second expectation (end-of-test reconciliation)
is a promotion condition, not this landing's, and the log carries forward the constraint that the NMI's reconciliation term is
nmi_mode and debug mode only, which is right.

### 7.3 L-1..L-5 and the seed

- L-1: gen_fu_l52_commands_corrigendum.log names five builds where the l52 log claimed one, the common fixture's plusargs, each
  block's out directory, stamp, fire count, verdict and reason, and states that the quiet fixture is a scratch cocotb module not in
  the clone, with its md5 and the placement a reproducer needs. Its tally-corrected totals (3002/3001) are stated with the rule.
  FIXED, and better than asked.
- L-2: single step is counted (step_records, :64-67, :138, :286-287) rather than masked on the model's dcsr copy, for the reason the log
  gives (a mask on a mirror not proved to track the pin is the shape this landing removes); Zcmp stays a named exclusion. Measured
  zero in my six smokes. A named, observable exclusion is the second option I offered. FIXED as an exclusion with an observable.
- L-3: prev_trapped = st.is_trap && !st.debug_mode (gen_fcov_pkg.sv, the trapped-predecessor route), with the comment stating that
  both arms are now structurally zero and the referee guards the classifier and the post-step publication, not the DUT. FIXED, and
  the log says plainly what the referee can and cannot fire on.
- L-4: the seed 1207954461 diagnosis is produced from the run's own log: the first model-versus-DUT divergence 6447 cycles before the
  first irq_entry fire, 23387 isa_insn mismatches by then, the core executing zeros at pc 0x80000022; the fires are the checker
  reporting a takeable interrupt a wedged core did not take. Consistent with my L-4 attribution and my Section 3 counts, which the log
  reproduces exactly; the log also corrects my "same firing counts" sentence (my corrigendum above) and runtime-2's "fires 6 times"
  (three fires; the assertion-source lines are not fires). FIXED as a records diagnosis.
- L-5: the parser cases write under the repo-local SCRATCH root and clean up (gen_ut_knobs_codegen.py). FIXED.

### 7.4 Smokes, records, what I noticed

Six smokes on my clean build: storm, lines, dbgstorm, fetchen, rr, nmilong all PASS with zero real errors, zero GEN_FCOV_REF, zero
irq_entry and nmi_entry fires, step_records 0, entries 173/6/39/15/0/2 (one NMI in nmilong). Wave seed 159577667 (gen_test_irq_basic on the wave run's own image and plusargs, 17 irq_entry fires before landing 52, 0 at 9c7f8f6): on the fixed build 0 irq_entry fires, 0 real UVM_ERROR, GEN_TEST_PASS printed (in the cocotb stdout capture), so the accrual change does not re-open the seed landing 52 closed.
The manifest holds 3513 rows and the two new rows equal the blobs (20012 bytes / 051ea7b9061b5f80874ecbc5f0b0eb8d; 7506 bytes /
44ed232180fc5db85d8f7403c8d6a26e); both logs ASCII. The l54 log names its six builds by identity, the mutation by port and file, the
fixture by module, image digest and plusargs, and the verdict path, which is the shape my L-1 asked for. Its "WHAT I GOT WRONG" note
(the consequence asserted to the Orchestrator without a derivation) is the right kind of record.
- L-6 (Low, records; tb-infra-2). The toggle program gen_irq_mie_toggle.S is named by scratch path and md5 only and is not in the
  tree; Red B is therefore reproducible only while that scratch survives. Fold the 40-line source into the log's next companion or
  commit it under dv/auto_dv/tests/gen_programs/ with a header naming it a checker fixture.
- L-7 (Low, records). The log's "SAME cycle and the SAME two order numbers the Critic quotes" refers to my Section 2 measurement on
  the 65b7cb0 build; my Section 3 sentence on the clean control was wrong in the way the log states and my corrigendum above corrects.
  Nothing owed by tb-infra-2; recorded so the two files read together.

### 7.4a Three measurements the range's records need

- THE STORM-ARM VACUITY IS NOT REMOVED. gen_fu_l52_commands_corrigendum.log:56-57 says of the l52 storm arm "This is the
  block the DV Lead later ruled VACUOUS rather than less sensitive ... and landing 54 removes the shape that caused it".
  Measured by me on the fixed checker with the external line tied low, on the l52 log's own storm fixture (the
  long-handler program, storm, hold through_handler, the corrigendum's plusargs): catch 0 irq_entry fires and 0 real
  errors, ablation 0 and 0, both runs ending at the alive timeout on the test's own "no tohost store" exactly as the l52
  arm did. The same mutation on the P_NMI storm smoke fires 12 times on the fixed checker (ablation 0), so the checker is
  not blind to a withheld external line in general; it is blind in that fixture, and the landing's own log says why in
  its last paragraph: the entry restart at gen_checkers_pkg.sv:118 resets every surviving expectation's count to zero at
  every interrupt entry, "so in a regime where entries recur the accrued count never builds". Landing 54's accrual
  removes the masked-record restart (the MIE-toggle case) and leaves the entry restart, so under a storm whose entries
  recur inside the bound the check still cannot fire whatever the DUT does. The corrigendum's sentence is false, the log's
  paragraph is right, and the two are in one landing (M-3). The remedy stays the DV Lead's end-of-test expectation; the
  vacuity corrigendum's regime statement should name the entry restart as the mechanism.
- THE NMI-MODE MIRROR IS DEEPER THAN THE RTL. rtl/ibex_controller.sv:958-960 clears nmi_mode_q on ANY mret while in NMI
  mode, nesting or none; the checker's mirror (gen_checkers_pkg.sv:162-164) increments a depth on every trap or interrupt
  inside NMI mode and leaves nmi_mode set until as many mrets have retired. After a trap inside the NMI handler and its
  handler's mret, the RTL is out of NMI mode and takes an enabled interrupt or a second NMI, while the checker still masks
  every expectation until the NMI handler's own mret: a withheld line in that window is not judged. The mirror predates
  the range (landing 2a) and no committed fixture drives a trap inside an NMI handler; the landing's log claims only that
  the mask carries the ~nmi_mode_q term, not that the mirror equals nmi_mode_q. Low (L-8): exit the mirror on the first
  mret as the RTL does, or count the divergence as step_records counts single step.
- THE STANDING RED FIXTURE ON THE FIXED CHECKER. The range's re-run block (69eb33f) reads gen_test_irq_basic_red RED-OK
  3 of 3 on the 9c7f8f6 checker, which landing 54 supersedes; nothing in the range re-measures it. Measured by me on the fixed clean build at runtime-2's seed 1038372995 (the entry's program
  regenerated with its --red --red-item TP-IRQ-002 arguments, the entry's plusargs, PASS_MARKER GEN_TEST_PASS): the designed
  red is the only failing fire check (fire_tp_irq_002, "vector 7 carried mcause 0x00000007, expected 0x80000007"), the
  entry's red_expect matches the GEN_TEST_FAIL line, irq_entry fires 0, real errors 0, which is RED-OK under the flow's
  grading rule. The range's figure holds on the fixed checker; the record should carry the re-measurement (L-9, Low,
  records; runtime-2 or tb-infra-2).

### 7.5 Verdict

CRITIC VERDICT: REQUEST-CHANGES on 65b7cb0..b9e5fad, confined to M-3 (records). M-1 and M-2 are CLOSED by mechanism and by my own
re-run of both reds with their controls, and the REQUEST-CHANGES of Section 5 on them is lifted; L-1..L-5 FIXED as stated; L-6..L-9
owed as disclosed (L-10..L-13 join them from 7.6). What remains is one sentence: the commands corrigendum says landing 54 removes the storm-shape vacuity and the
measurement and the landing's own log say it does not (the entry restart). A companion correcting that sentence, naming the entry
restart as the mechanism and the end-of-test expectation as the remedy, closes M-3 and the group. Promotion of the irq entry remains
gated on that expectation, which under this measurement is not optional: the per-record bound is vacuous under every storm whose
entries recur inside the bound.

### 7.6 Reconciliation with the cross-model artifact rev60

Read after 7.1-7.5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-65b7cb00-b9e5fad3.md at 775847f (claude CLI
fallback under A-001; APPROVE-WITH-CHANGES; three Mediums, five Lows). Its verified list agrees with 7.1-7.4 on every shared
point (the per-expectation mask against :490 and :498-500, the dropped fire-side clause implied by the mask, the reset points of
the count, both reds' internals to the bit and the order, the 258-seed timestamps, the manifest rows, the parser cases) and adds
two checks I record as its: the release path (:239-244) drops lines and keeps the count, and st.debug_mode is the DUT's pin and
not a model mirror, which is why masking on it is consistent with not masking on st.dcsr.

- Its Medium 1 (the nmi_mode mirror deeper than nmi_mode_q) is my L-8, found independently. It adds that the coverage package
  carries the same mirror (gen_fcov_pkg.sv:499-501, irq_nmi_depth), which I verified. I hold the grade at Low: the mirror
  predates the range, no committed fixture drives a trap inside an NMI handler, and the landing claims the mask's terms rather
  than the mirror's equality with nmi_mode_q; the fix it names (first-mret exit, or a counted divergence) is the one I named.
- Its Medium 2 (the commands corrigendum's "landing 54 removes the shape") is my M-3, found independently; rev60 reasoned it from
  the entry restart and the log's own paragraph, my 7.4a measures it on the l52 storm fixture (0 fires on the fixed checker with
  the line withheld, ablation 0) and shows the same mutation firing 12 times on a storm whose entries leave gaps. Same fix.
- Its Medium 3 (RED-OK measured on the superseded checker) is my L-9, which I measured: RED-OK reproduces at seed 1038372995 on
  the fixed checker (7.4a). I hold it at Low because the figure now exists; the record beside the 69eb33f block is what stays
  owed, and its request to re-run the 258 seed on a b9e5fad build is reasonable but not gating: that seed's fires follow a wedge
  the checker cannot judge, on either semantics.
- Its Low 1 (the per-line mie bit is not a mask term, so a line raised with its enable bit clear accrues takeable records and is
  dropped silently at the bound, or fires on the record whose csrw enables it) is verified on :140-152: the mask has no per-line
  enable term and the still test at :148 requires the bit set. Pre-existing; the new comment's "COULD have been taken" makes it
  a stated-semantics mismatch. Adopted as L-10 (Low; tb-infra-2): a per-line enable term for single-line expectations, or the
  exclusion named in the comment.
- Its Low 2 (the log's "the checker telling the truth: the interrupt was takeable" overstates after the lockstep divergence, since
  the takeability is judged on model state that no longer tracks the DUT) is right and adopted as L-11 (Low, records).
- Its Low 3 (GEN_DCSR_STEP_BIT hand-encoded in the checker while gen_tb_pkg.sv:280-281 is the dcsr bit home and gen_fcov_pkg.sv
  reads a bare st.dcsr[2] at :336 and :568) is verified and adopted as L-12 (Low, code): one home for the step bit.
- Its Low 4 (the mutant diffs and the toggle source retained only as scratch paths with md5s) is my L-6, with the mutant-diff
  half added to it.
- Its Low 5 (single step is not an exclusion but a counted, judged term, so "named exclusion" is a misnomer; step_records is a
  print-only counter) is right on the code (:138 counts, the mask at :140-141 carries no step term) and adopted as L-13 (Low,
  wording): "unmasked and counted", with a fixture-side assertion on the count when a step fixture arrives.
- On the verdict we agree on every finding and differ on the form: rev60 approves with changes; under my rules a sentence in the
  landing's own record that reverses what the landing achieved for the promotion decision is REQUEST-CHANGES until the
  companion lands. M-1 and M-2 are closed in both reviews.

Verdict unchanged: REQUEST-CHANGES on 65b7cb0..b9e5fad confined to M-3; M-1 and M-2 closed; L-1..L-5 fixed; L-6..L-13 owed.

## 8. The lift: M-3 closed by landing 56 at fab8a61; the REQUEST-CHANGES on 65b7cb0..b9e5fad is lifted (appended under a HOLD, 2026-09-05T13:58:24Z; Sections 1-7 unchanged)

The companion: dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l56_storm_vacuity_companion.log at fab8a61, sha256 a5efb3ea37645cef,
md5 d224cf45049c6c8b, 4161 bytes; its manifest row is gen_tdd_logs/gen_manifest.md:3521 at fab8a61 (manifest blob 9678c82de94200b5).
Its header names itself the answer to rev60's Medium and to my M-3, quotes the sentence it corrects
(gen_fu_l52_commands_corrigendum.log:57, "landing 54 removes the shape that caused it"), states the second clause false, derives
the entry restart from gen_checkers_pkg.sv:118 at b9e5fad exactly as 7.4a measured it, and separates what landing 54 closed (the
software-toggle vacuity) from what it did not (the storm-arm vacuity, whose remedy stays the end-of-test expectation). The
commands corrigendum's bytes are untouched (md5 44ed232180fc5db8, 7506 bytes, the figures 7.1 recorded). That is the companion 7.5
asked for, so M-3 is CLOSED.

Standing verdict on the irq checker group, 65b7cb0..b9e5fad: CRITIC VERDICT: APPROVE. M-1 and M-2 are closed by mechanism and by
my re-runs (Section 7), M-3 by fab8a61, L-1..L-5 fixed; L-6..L-13 are owed as disclosed. The tree now carries answers to several,
which Section 9 judges on the named range ccd755d..38b729a (landing 57, measurements in progress): L-6 (the toggle source and the
mutant diffs, retained under gen_irq_fixtures at 38b729a), L-10, L-12 and L-13 (the per-line enable term, the dcsr home, the
wording); L-9 (the re-measurement record) is answered by the reds2 block at 67c6ac1, verified in gen_critic_flow_followups.md
Section 7; L-7 and L-11 are records notes; L-8 (the NMI-mode mirror) is held back by landing 57's own statement and stays owed.
Promotion of the irq entry remains gated on the end-of-test expectation, as 7.5 says.

The lift was first recorded in gen_critic_form_v3.md Section 4 (:54-56 at 55d784a, 12:56:46Z) and in my message to the
Orchestrator after fab8a61 landed; this section is the gating record's own statement of it, written after rev74 found that this
file still read REQUEST-CHANGES at :300 with no section lifting it.
