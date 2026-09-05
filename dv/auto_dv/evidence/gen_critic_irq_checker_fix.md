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
