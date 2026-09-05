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

## 9. Landing 57 (irq checker fix 3a), ccd755d..38b729a: the per-line enable term, the dcsr home and the fixtures; APPROVE (2026-09-05T14:37:15Z)

Artifacts at 38b729a: gen_checkers_pkg.sv, gen_fcov_pkg.sv, gen_tb_knobs.yaml, gen_tb_pkg.sv, gen_knobs.py, gen_isa_shim_map.h,
gen_fu_l57_perline_enable.log (md5 66e1064ea9a3ec47, 8426 bytes), the four fixtures under gen_irq_fixtures, gen_manifest.md; rev71
(dv/auto_dv/reviews/2026-09-05-claude-diff-ccd755dc-38b729a1.md at 60081cd, 2a38a10e59c18cff). Method: two out-of-tree archives, A of
ccd755d and C of 38b729a, each clean and with the four regular interrupt inputs tied low at the core instance by my own script (the
MUT-IRQWITHHOLDALL shape; the clean gen_dut_top.sv reads md5 56041635e557a553, the log's revert value), compiled with the local
flow; the per-line fixture rebuilt from the retained source (crc32 33ec7bd6, 150 words, tohost 800002b8, equal to the log); twelve
runs of gen_ut_lockstep at seed 1 under the storm regime with the until_taken hold; the RTL terms, the rendered constants, the code
generators' checks and unit tests, and every TDD manifest row checked on the archive; rev71 read after the findings were fixed
(dv/auto_dv/work/critic/irqfix3/draft_s9_prerev71.txt). Exposure: the Orchestrator's messages summarised the landing and relayed
rev71's three Lows before these checks; each is measured below on my own runs, and the boot_retire finding is mine. Logs:
dv/auto_dv/work/critic/irqfix3/ (runs_l57.txt, runs_l57_hypotheses.txt, static_checks_38b729a.txt, dcsr_literals_38b729a.txt,
mutdiff_apply_check.txt, codegen_checks_38b729a.txt, l57_log_at_38b729a.txt).

- L-10 CLOSED, the per-line enable term. The mask gains !line_enabled for every non-NMI expectation, line_enabled being any of the
  expectation's lines with its bit set in the model's mie (gen_irq_mie_bit, gen_agents_pkg.sv:517). The RTL term it mirrors:
  irqs_o = mip & mie_q and irq_pending_o = |irqs_o (rtl/ibex_cs_registers.sv:1044-1045); handle_irq needs irq_pending_i &
  irq_enabled (rtl/ibex_controller.sv:498) with irq_enabled = csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U) (:490); irq_nm is
  ORed outside both, and the checker skips both terms for an NMI expectation.
- THE RED REPRODUCES TO THE TOKEN, with one plusarg the log does not state. With +gen_ut_boot_retire=100 the log's table is exact:
  A clean 0 fires / 0 real errors / 1 open expectation PASS; A + mutation 4 / 328 / 1 FAIL; C clean 0 / 0 / 5 PASS; C + mutation
  5 / 329 / 1 FAIL; C + mutation + gen_chk_irq_entry=0 0 / 324 / 1 FAIL. The fifth fire reads verbatim "lines 00100 (enable bits
  00200000) raised at cycle 181 (order 28) not taken within 17 records (now order 68, takeable records 18, mie 7fff0888 mstatus
  00000088)" and the pre-fix build reports no fire at raise order 28; the other four fires are common to both builds with the same
  lines, cycles and raise orders; entries=0 in every mutant run (no trap taken); 324 + 4 and 324 + 5 are exact; the clean builds
  end with 1 and 5 open expectations, the fault-free observable. L-14 (Low, records; tb-infra-2): the log's recipe names module,
  regime, hold, seed and mutation and omits +gen_ut_boot_retire=100. Run as written the runs are longer (218 retirements, $finish
  at 1302501) and read 0/0/4, 8/1027/4, 0/0/12, 9/1028/4 and 0/1019/4: every mechanism claim holds there too (the fifth fire
  identical, one extra fire on the fixed build, exact accounting, clean open expectations 4 to 12, the check off reporting 0 irq_entry errors while its summary still counts the five detections,
  since expect_fail is incremented before the gen_chk_en gate, so "ablation 0" counts errors and not detections) and none of the
  table's figures does; boot_retire 40 and 60 give the fixed mutant 5/313/0, 120 gives 6/466/0, 100 the table. No run header or
  GEN_IRQ_CHK summary line is quoted, so the table cannot be tied to a run from the record; the plusarg line and the five summary
  lines belong in a companion.
- L-6 CLOSED: the four fixtures are in the tree with the log's md5s and their manifest rows (702, 479, 1315 and 2194 bytes); the
  toggle source's md5 equals the l54 log's value. L-15 (Low, records; tb-infra-2): both retained diffs carry the placeholder hunk
  header "@@ port map @@"; git apply --check answers "unrecognized input" and patch --dry-run "Only garbage was found in the patch
  input", so they document the mutation and do not apply it; real hunk headers, or a sentence saying the four tie lines are the
  recipe.
- L-12 CLOSED: GEN_DCSR_STEP_BIT is declared once (gen_tb_knobs.yaml:231) and rendered into gen_tb_pkg.sv:282, gen_knobs.py:190 and
  gen_isa_shim_map.h:67, used at gen_checkers_pkg.sv:137 and gen_fcov_pkg.sv:336 and :567; no dcsr[<digit>] indexing remains;
  gen_knobs_codegen --check and gen_fcov_codegen --check read up to date on the archive and GEN_UT_KNOBS_CODEGEN and
  GEN_UT_FCOV_CODEGEN pass with 0 failures, which is the gate the log says refused its first hand. L-16 (Low, code; tb-infra-2):
  gen_fcov_pkg.sv:596 still reads st.dcsr[1:0] for the prv field where GEN_DCSR_PRV_BIT_LOW and _HIGH exist (gen_tb_pkg.sv:280-281)
  and gen_checkers_pkg.sv:330 uses them; the same family, one line.
- L-13 CLOSED: the comment reads "unmasked and counted, never a mask term"; step_records stays a print-only counter, disclosed in
  the log's Row 3 with the fixture-side assertion owed when a step fixture exists.
- L-8 stays owed: the NMI-mode mirror change is held back, as the log says first, under the DV Lead's rule that a change to what a
  checker masks lands with its red; the depth mirror is present in both packages as before (four mentions each).
- Records: the TDD manifest's 3520 rows all match the archive by bytes and md5 (0 bad, 0 missing); the five new rows included. No
  rtl/ line changes; the mutation lives in out-of-tree archives only, mine included.

Reconciliation with rev71 (read after the rows above were fixed):
- Its verification list agrees with mine on the RTL terms, the mask, the fixture identities, the mtvec claim, the dcsr home, the
  manifest rows and the hold-back; it adds checks I record as its: the never-set bit is held to report_phase and reported in the
  open figure rather than failed; a mixed lines-plus-NMI expectation is judged on the NMI pin; the fifth fire's 40 elapsed, 22
  masked and 18 takeable follow from the orders and the bound; the toggle image md5 equals the l54 log's.
- Its Low 1 is my L-14 with the cause measured: the omitted plusarg is +gen_ut_boot_retire=100 and with it the table is exact.
- Its Low 2 is my L-15 (the hunk headers; I measured both tools refusing). Its Low 3 is my L-16.
- Its Info on the open-expectations figure conflating a never-enabled hold with a drain-window hold is fair, and a counter of
  expectations held with the line's own bit clear would give the lost-coverage consequence a number in every run; its Info on
  any-of line_enabled for a multi-line expectation is verified on the loop at :140 and is consistent with the still test.
- Verdict after reconciliation: unchanged. Both agree there is no Major and no Medium.

CRITIC VERDICT: APPROVE on ccd755d..38b729a. L-10, L-12, L-13 and L-6 of Section 7 are CLOSED; L-14, L-15 and L-16 are owed to
tb-infra-2's next records touch as disclosed; L-8 remains owed from Section 7 with the rule it waits on named. The group's standing
verdict of Section 8 (APPROVE) is unchanged.

## 10. Landing 59 (the irq follow-ups), dd6fa54..dd23dff: L-14, L-15, L-16 closed, one Medium on the new counter's figures (2026-09-05T14:37:15Z)

Artifacts at dd23dff: gen_checkers_pkg.sv, gen_fcov_pkg.sv, the two regenerated mutant diffs (md5 13fd25d9d214e631, 887 bytes;
bdc5aaf6601db8b6, 685 bytes), gen_fu_l59_l57_artifacts_companion.log (5290beaf0151f91b, 5439 bytes), gen_manifest.md; rev77
(dv/auto_dv/reviews/2026-09-05-claude-diff-dd6fa549-dd23dff7.md at 0624215, 8f35af81a30e80b3). Method: a dd23dff archive compiled
clean and with the retained all-lines diff applied by git apply; the per-line fixture run with the companion's plusarg set and with
five variants; the retained diff applied to ccd755d and 38b729a archives and compiled, to tie the companion's mutant identities to
a committed tree plus the diff; every manifest row checked; rev77 read after the findings were fixed
(dv/auto_dv/work/critic/irqfix3/draft_s10_prerev77.txt). Exposure: the Orchestrator relayed rev77's verdict shape before these
checks. Logs: irqfix3/l59_checks.txt, runs59.log, build59.log, build59b.log, l59_log_at_dd23dff.txt, preread_dd23dff.txt.

- L-14 CLOSED: the companion states the one plusarg set for the five l57 runs, +gen_ut_boot_retire=100 among them, the five out
  directories with build identities and sim.log paths, and quotes each run's summary line; the quoted fields (bound failures
  0/4/0/5/5, open expectations 1/1/5/1/1) equal my boot_retire=100 runs of Section 9 exactly, the four common fires listed equal
  mine line for line, and the clean identities 2f874eb63deeb6bb and b7067f660ed88693 equal my ccd755d and 38b729a builds.
- L-15 CLOSED: both diffs are real hunks against gen_dut_top.sv; git apply --check passes on the 38b729a and dd23dff files and the
  applied file reads md5 5d9ec8ba369a099a (all) and 54cb9be1213ffb76 (nmi). A ccd755d archive plus the retained all-diff compiles
  to identity 5bcfb9424b692b13 and a 38b729a archive plus it to 4baea273ea4d6723, the companion's a_mut and c_mut, so every
  identity in its table resolves to a committed tree plus a retained diff. The commit message's "the mutant digests the
  landing-54 build matrix recorded" names digests the l54 log does not carry (its PRE row is c045115's); the companion's table
  is where they are recorded.
- L-16 CLOSED: gen_fcov_pkg.sv:596 reads st.dcsr[GEN_DCSR_PRV_BIT_HIGH:GEN_DCSR_PRV_BIT_LOW]; no dcsr indexing without a GEN_DCSR_
  constant remains under env/ or tb/.
- The ablation precision: my own check-off run's summary reads bound failures=5 with irq_entry errors 0, as the companion says;
  Section 9 reads its "ablation 0" that way.
- M-1 (Medium, records; tb-infra-2): the new counter "records held by a clear per-line enable alone" is printed in the summary line
  and its condition is the mask with every non-per-line term false, but its figures have no run root, build identity or sim.log:
  "on this fixture it reads 250" and "0 on all six regression smokes" name no run, and the six smokes are unnamed (the testlist's
  smoke tier has 17 entries). On my dd23dff archive with the companion's own plusarg set the clean run reads 244 and the mutant
  runs 33; without boot_retire the clean run reads 935; boot_retire 40, 60 and 80 read 244 and 120 reads 344; none reads 250.
  The counter is nonzero on the fixture and the structural point (a number in every run) holds; the figure and the zeros are
  unsupported. Closes with a row per counter run (build identity, plusargs, sim.log, the field quoted), the 250 corrected to
  what the committed checker prints or its recipe stated, and the six smokes named.
- Records: the TDD manifest's 3522 rows match the archive (0 bad, 0 missing); the three touched rows match their blobs.
- The ledger against Section 8's owed Lows, since the landing maps its work to rev71 alone: landing 57 (Section 9) closed L-10 and
  L-13 and answered L-6 and L-12 in part; this landing completes L-6 (the diffs apply) and L-12 (the last bare slice) and closes
  Section 9's L-14, L-15 and L-16; L-9 is answered by the reds2 block at 67c6ac1; L-7 and L-11 are records notes needing no code;
  L-8 (the NMI-mode mirror) stays held back under the DV Lead's rule.

Reconciliation with rev77 (read after the rows above were fixed):
- Its verification agrees with mine on every shared item (the diffs applying, the six identities from committed trees plus the
  diff, the dcsr accesses, the counter's condition and any-of, the ablation ordering at :164 before :165, the manifest rows).
- Its Medium is my M-1; it adds that the five sourced rows are builds without the counter, so the 250 comes from a sixth build the
  log never names (the committed dd23dff env digests to c684bc82a9d070dc, my D build), and my measurement adds that that tree
  reads 244 on the stated recipe.
- Its Low on the l57 log's Row 4 md5s, VERIFIED and adopted as L-17 (Low, records; tb-infra-2): the l57 log still lists
  6bb801edb599b5d3 and 49bf2735cdccc195 for the two diffs, values no file carries after this landing (13fd25d9d214e631 and
  bdc5aaf6601db8b6), and the companion names neither set; one superseding sentence is owed.
- Its Low on the counter's unit, VERIFIED and adopted as L-18 (Low, code; tb-infra-2): the increment sits inside foreach
  (expects[i]), so two expectations held on one record count two while the label says "records"; label or count, one of them
  moves.
- Its Low on the comment at gen_checkers_pkg.sv:66-68, VERIFIED and adopted as L-19 (Low, comment; tb-infra-2): "Before that term
  existed the checker spent them ..." narrates history in a code comment, against the intent-only rule; state the intent.
- Its Low on the missing L-mapping is answered by the ledger above; its reading (L-6 and L-12 answered, L-7, L-8, L-9, L-11 not
  touched) is right against Section 8's list and does not see Section 9, which was not in the tree it read.
- Its two Infos (the diff header could name the gen_dut_top.sv blob rather than a commit; the "applies inside the assembled tree"
  check is a process claim with no committed gate) are fair and need no row.

CRITIC VERDICT: REQUEST-CHANGES on dd6fa54..dd23dff, confined to M-1 (the counter's 250 and six zeros without a run root, and the
250 not reproducing on the committed checker with the stated recipe). L-14, L-15 and L-16 are CLOSED; L-17, L-18 and L-19 owed
with M-1's companion; the group's standing verdict (Section 8, APPROVE) is unchanged and L-8 stays held back.

## 11. Landing 60 (the NMI-mode mirrors exit on the first mret), dd23dff..139c325: L-8 closed; APPROVE (2026-09-05T15:01:38Z)

Artifacts at 139c325: gen_checkers_pkg.sv (md5 412733ec), gen_fcov_pkg.sv (0d99a8c0), gen_irq_nmi_aligned.S (4a790cfab0d39791, 2520
bytes), gen_fu_l60_nmi_mode_exit.log (bdcd757daf052a29, 6041 bytes), gen_manifest.md; rev80 (dv/auto_dv/reviews/2026-09-05-claude-diff-dd23dff7-139c325b.md at e5ddfff, 4ff5af5b1e6ed8e6). Method: two out-of-tree roots exactly as
the log names them, G an archive of dd23dff (the depth mirror; its two packages read the log's md5s ed3ef053 and 3a3c6c35) and H the
same archive with 139c325's two packages laid over it (412733ec and 0d99a8c0), each with the retained gen_mut_irqwithholdall.diff
applied by git apply (gen_dut_top.sv md5 5d9ec8ba); the fixture rebuilt from the retained source; gen_ut_irq_nmi_long at seed 1 with the
module's plusarg and the ablation; the RTL term read; every manifest row checked on a 139c325 archive. Findings fixed before any review
of the landing was read (irqfix3/draft_s11_prerev.txt). Logs: irqfix3/l60_checks.txt, l60_runs.log, l60_log_at_139c325.txt,
l60_diff_at_139c325.txt.

- L-8 CLOSED by the code and the RTL: both packages drop the nesting depth and leave NMI mode on the first mret record that is not a
  trap, which is what rtl/ibex_controller.sv:954-960 does (mret_insn in the FLUSH branch clears nmi_mode_d with no count), the term
  Section 7 quoted. The log states the RTL fact in its own text rather than only in the fixture's header.
- THE RED REPRODUCES VERBATIM. The mutant build identities read 311aaf1ed6d1c9cc (G) and 00a451af15ba8b17 (H), exactly the log's two,
  and the log says of them what they are: mutant builds, recomputable from a committed tree plus the retained diff, which is the
  discipline my counters M-2 asks for. The fixture assembles to crc32 3cba3f47, 218 words, tohost 800003c8 as stated. The depth mirror
  reports "lines 00004 (enable bits 00000800) raised at cycle 902 (order 206) not taken within 17 records (now order 267, takeable
  records 18)" and the RTL mirror the same raise at "now order 225", forty-two records apart with takeable 18 in both, so the mask
  moved and the bound did not; the ablation reads 0 irq_entry errors with bound failures=1 in its summary. The other 867 real errors in
  every mutant run are irq_pending mismatches, the withheld lines' pending view, the same on both mirrors. I agree with the DV Lead's
  ruling as the log states it: the judgment-order difference with its window quantified isolates the mask with the confounder held
  equal, and a run ending inside the window loses the report, which follows; the nested ecall inside the NMI handler is the case L-8
  named.
- L-20 (Low, records; tb-infra-2): the recipe names module and seed and omits +gen_fetch_en_at_reset=0, which gen_ut_irq_nmi_long
  requires; run as written the simulation ends at 10 ps with a cocotb FAIL and no summary, so the omission is found at once rather
  than misleading, but the recipe does not run as written (+gen_ut_boot_retire=100 changes nothing here).
- L-21 (Low, records; tb-infra-2): "all six regression smokes PASS on the tree build" names no smoke, run or summary line, as in
  landing 59; the log itself says the control bounds little.
- Records: the TDD manifest's 3524 rows match a 139c325 archive (0 bad, 0 missing); the two new rows match their blobs. No rtl/ change.

Reconciliation with rev80 (read after the rows above were fixed):
- Its verification agrees with mine and goes further on the RTL: it quotes all three nmi_mode_d assignments (the hold, the set at :745
  under irq_nm && !nmi_mode_q, the clear at :959 in FLUSH) and confirms both mirrors match; it recomputed every digest in the log
  from committed archives plus the retained diff and names the clean roots c684bc82a9d070dc (dd23dff, my D build) and
  1940c64a528d078c, which my own clean build of the RTL-mirror root reads exactly.
- Its Medium, the red's figures and the ablation's summary quoted from no named out directory or sim.log, is the artifact half of
  what my L-20 and L-21 name; adopted as L-22 (Low, records; tb-infra-2): the figures reproduce verbatim on my builds, so the gap is
  quotation, not truth, which keeps it Low in my scale where rev80 says Medium.
- Its Low on rev77's comment still present at gen_checkers_pkg.sv:64-67, VERIFIED (the "Before that term existed" sentence stands at
  139c325); it is fixed in the next landing (Section 12).
- Its Low on the fixture's include path, VERIFIED and adopted as L-23 (Low, records; tb-infra-2): gen_irq_nmi_aligned.S includes
  gen_mmio_map.h, the directed recipe as written ends "assemble/link failed", and --gcc-opts=-Idv/auto_dv/tests/gen_programs, which
  my assembly used, builds it to the stated 218 words and crc32; the same holds for the two earlier retained fixtures.
- Its Low on the missing clean-build row, agreed and MEASURED here as L-24's answer: on the unmutated RTL-mirror root (identity
  1940c64a528d078c) the fixture reads PASS, irq_entry 0, entries=2 nmi=1, bound failures 0, open expectations 0, so the design takes
  the NMI and then the external line inside the handler remainder after the inner mret, the window the depth mirror masked and the
  RTL mirror leaves open. L-24 (Low, records; tb-infra-2) is the row for the record to carry it.
- Its Infos (the fixture header's history sentence; the comment duplicated by design in the fcov mirror; the identity recipe's sort
  being locale-dependent, under which my digests and theirs agree because both ran on the site's locale) are noted.

CRITIC VERDICT: APPROVE on dd23dff..139c325. L-8 is CLOSED, the last of Section 7's Lows that named code; L-20 and L-21 owed to tb-infra-2's next
records touch; the group's standing verdict of Section 8 (APPROVE) stands, with Section 10's M-1 on landing 59 still the open row.

## 12. Landing 61 (the artifacts and identity companion), 139c325..41bcbe8, the irq half: Section 10's REQUEST-CHANGES lifted (2026-09-05T15:01:38Z)

Artifacts at 41bcbe8: gen_checkers_pkg.sv, gen_protocol_props.sv, gen_fu_l61_artifacts_and_identity.log, gen_manifest.md. No review of
41bcbe8 exists at HEAD e85fe5b (rev81 is running), so none is read here; a reconciliation follows when the Orchestrator names one.
Method: the log's runs read on the clone's own output directories it names (dv/auto_dv/out_l65 and its eight runs), the build
identity compared with a 41bcbe8 archive compiled by me, the code diff read, my Section 10 and Section 11 rows checked one by one.
Logs: dv/auto_dv/work/critic/l53/l61_checks.txt, l61_log_at_41bcbe8.txt.

- Section 10's M-1 CLOSED. Row 1 puts the counter's figures on ONE named build, dv/auto_dv/out_l65 with identity d9a0553bd4e0b326,
  which is the identity of a 41bcbe8 archive compiled by me, so the runs are on the committed tree; the six smokes are named with
  their modules and plusargs (storm, lines, dbgstorm, fetchen, rr, nmilong) and each run's field is quoted; on the clone's out_l65 I
  read the eight verdicts PASS, the six zeros, perline 244 and nmiclean entries=2 nmi=1, all as the log says. The figure is corrected
  to 244, my Section 10 measurement, and the log says the earlier 250 came from an unnamed build and does not assert which change
  moved it, which is the right thing to say.
- L-17 CLOSED (Row 4 names the superseded md5s 6bb801ed and 49bf2735 and the regenerated 13fd25d9 and bdc5aaf6). L-18 CLOSED: the
  counter is bit_clear_expectation_records and its summary field reads "expectation-records held by a clear per-line enable alone".
  L-19 CLOSED: the comment states what the counter counts and why, and nothing of its history.
- Section 11's rows: L-20 CLOSED (Row 6 states the plusarg set with +gen_fetch_en_at_reset=0); L-21 CLOSED (the six smokes named, on
  one identity); L-22 CLOSED (Row 6 quotes the two fire lines and the three summary lines verbatim, equal to mine, with the ablation's
  bound failures=1 beside its zero errors); L-23 CLOSED (Row 8 gives the assembling command with -Idv/auto_dv/tests/gen_programs);
  L-24 CLOSED (Row 7's nmiclean on out_l65 reads PASS, entries=2 nmi=1, irq_entry 0, which my clean run of Section 11 also reads).
  Row 6's l60 run paths are <scratch> placeholders again where the out_l65 rows are clone-relative and checkable; folded into L-25.
- L-25 (Low, records; tb-infra-2): Row 5's ledger of my owed Lows mislabels them. It says L-6 was answered by landing 57's per-line
  enable term (L-6 is the toggle source and the mutant diffs; the per-line term is L-10), that L-12 was answered by the ablation
  precision (L-12 is the dcsr home; the ablation precision is no row of mine), and that L-8 and L-9 are untouched (landing 60 closed
  L-8, Section 11; the reds2 block at 67c6ac1 answered L-9, my flow Section 7). The ledger a reader should use is this file's:
  L-6 closed by landings 57 and 59; L-8 by landing 60; L-9 by the reds2 block; L-10 and L-13 by landing 57; L-12 by landings 57 and
  59; L-7 and L-11 are records notes with nothing owed; L-14 to L-24 as Sections 9 to 12 state.
- Records: the manifest row for the l61 log matches its blob (checked with the others in l61_checks.txt); no rtl/ change.

CRITIC VERDICT: APPROVE on 139c325..41bcbe8 for the irq checker group. The REQUEST-CHANGES of Section 10 on dd6fa54..dd23dff is
LIFTED (M-1 closed by measurement on the committed tree); L-25 is owed to tb-infra-2's next records touch. The group's standing
verdict is APPROVE with every code-bearing Low of Section 7 closed; the promotion of the irq entry stays gated on the end-of-test
expectation as 7.5 says.

### 12.1 Reconciliation with rev81 (appended under a HOLD, 2026-09-05T15:14:03Z; Sections 1-12 unchanged)

rev81 (dv/auto_dv/reviews/2026-09-05-claude-diff-139c325b-41bcbe8c.md at 913b76f, c324e618e8cb44b4) on 139c325..41bcbe8, read after
Section 12 was committed at bc7a15d. Its verification matches Section 12 item for item (the seven counter runs and the green on
out_l65 at identity d9a0553bd4e0b326, the regenerated diffs' md5s, the include path, the re-dump arithmetic of 297 in four ids and
330 omitted, the manifest row). Its Medium 1 is my L-25, the per-Low ledger wrong against the tree's own record; it rates the row
Medium where I hold Low, because the ledger of record is this file and the mislabels cost a reader a lookup, not a claim about the
code. Its Low on the 250-to-244 cause: my Section 10 measurement of 244 on a dd23dff archive, before the NMI-mode mirror landed, does
isolate it as rev81 says, so the mirror did not move the figure and the unnamed build's 250 stays unexplained by anything committed.
Its Low on the <scratch> roots is folded in L-25. Its Low on the manifest row for the l61 log, VERIFIED and adopted as L-26 (Low,
records; tb-infra-2): the row says three landings where the log says four and five bus-protocol ids where the log and the run say
four. Its Info on the identity recipe's locale dependence is noted, as in Section 11. Verdict unchanged: APPROVE, L-25 and L-26 owed.

### 12.2 Landing 62, 41bcbe8..a8792ce: L-25 and L-26 closed (appended under a HOLD, 2026-09-05T15:50:28Z; Sections 1-12.1 unchanged)

gen_fu_l62_counters_m2_companion.log at a8792ce, Rows 7 and 8, read against this file and the retained runs (l53/l62_checks.txt).
L-25 CLOSED: Row 7 corrects the ledger on the four lines against this file's Section 12.1 and names the document. L-26 CLOSED: the
l61 manifest row reads FOUR landings, and the "five bus-protocol ids" wording is shown to live in 41bcbe8's commit message and not the
row, which I confirmed (the manifest at 41bcbe8 has no "five bus"). rev81's Lows on the l61 log: the five runs' roots, headers, whole fire
lines and whole summary lines are given, and on the retained g_mut, h_mut and h_abl I read irq_pending 867 and irq_entry 1, 1 and 0
with the summary line md5 71a730485766 on all three, as the log says; the ablation sentence is corrected to zero errors OF THE NAMED
CHECK beside the 867 from the mutation's own signature, which is the precision Section 9 adopted and Section 12 should have read that
way too; the mirror is ruled out as the 250's cause by my 244 on a pre-mirror archive; the locale is named beside the recipe; the
fetch-enable plusarg is recorded (the log does not measure a run without it; Section 11 did).

No review of a8792ce has landed at this writing; its reconciliation follows as a further line if the Orchestrator asks for one.

Verdict unchanged: APPROVE; nothing owed to tb-infra-2 on the irq checker group from this file.
