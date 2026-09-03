# Critic verdict: the Test Writer's four template-guard touches 674d026, 5bb10e7, 99cba0e and ac5853e, reviewed as one (gen_critic_t226 v2)

Base verdict: dv/auto_dv/docs/gen_critic_t226.md on ae4b2e2 (committed at 2f161dd, sha256 first 16 d2d196fb5da74a20, 122 lines; APPROVE with
M-1 owed: the lint accepted a test rebinding self.bridge.cov_witness or self.cmd inside a method). That file is frozen; this file carries
every later finding on the same target. Sections 1-3 below were written on 2026-09-03 at 20:49 UTC on 674d026 and 5bb10e7 (the text the
Orchestrator saved from the frozen file's extension, carried verbatim apart from section numbers); Section 4 adds 99cba0e and ac5853e;
Section 5 reconciles with their artifacts.

Targets (committed blobs; sha256 first 16 hex):

- 674d026 (the LOG-050 regime-handler structural check): dv/auto_dv/tests/gen_test_lib.py bff3eab2e917750e, gen_test_template.py 77546aa545628f2c
- 5bb10e7 (the CM77 lint reach and the API doc restore): gen_test_lib.py 5f8ed7b5076af2c0, gen_test_template_api.md eb6d5476d117a2af
- 99cba0e (the knob-mapped rule, the NMI closure, the values-aware run-time check): gen_test_lib.py 925c8f43af2d21c4, gen_test_template.py b9ae9669e80d896f, gen_test_template_api.md ada16d55566b7954
- ac5853e (the helper-branch attribute-chain walk): gen_test_lib.py 2bf1bc93912272d1, gen_test_template_api.md eb9f53461be0a658, gen_tdd_test_template.md 52aed5c3d52cc9a5
- the added logs: gen_t2guard_* (5), gen_t2cm77_lint_red_before.log, gen_t2cm80_* (6), gen_t2cm85_helper_chain_red_before.log (manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, LOG-050,
LOG-024d, my gen_critic_tb_l2b.md M-1, gen_critic_batch1_v8.md L-1 and gen_critic_t226.md M-1. Method: clean archives of the four commits;
on ac5853e the library self-test PASS, REFUSED_FORMS fifteen with api_doc_forms equal; my injection probes through check_test_source and
regime_handler_violations on the ac5853e archive (results in Section 4); retained reds and greens read from the blobs. EXPOSURE: the
Orchestrator's queue messages described 99cba0e as "the knob-mapped rule and NMI closure" and ac5853e as "the helper-branch walk" before
this review; the two artifacts for those commits were not read before Section 4 was written.

CRITIC VERDICT: APPROVE (the four touches together). They close my gen_critic_tb_l2b.md M-1 on the code (the template's part of T-226,
with Runtime's witness_render and the DV Lead's plan text landed) and my gen_critic_batch1_v8.md L-1 (the regime-handler guard), and
they close M-2 of Section 3 (the NMI exemption) and its L-4 / L-5. My own CR-T226-M-1 is closed for the two attribute-chain forms and
stays OPEN, narrowed, for the single template-method rebinding inside a method and the local-alias form (Section 4).

## 1. 674d026: the LOG-050 regime-handler rule (closure of gen_critic_batch1_v8.md L-1)

- What landed: GenTest gains `program_handlers = ()` and `mie_stays_zero = False`; gen_test_lib.regime_handler_violations applies
  the rule from gen_knobs.KNOB_CONSUMER (the yaml's regime_set_consumer: dbg for knob_debug_req_regime, irq for knob_irq_regime
  and knob_irq_line_mix, bus for the delays); check_regime_handlers reads every test module by AST (schedulable as a literal
  tuple, a module-level constant, lib.TIMING_ONLY_KNOBS or GenTest.schedulable; the two declarations as literals; anything else
  refused as unreadable) and the library self-test runs it on every committed test plus seven red and five green sources;
  setup() applies the same rule at run time before the first fetch. REFUSED_FORMS stays at fifteen with api_doc_forms equal
  (LOG-024d respected: the rule is a structural check beside the lint, as LOG-050 says).
- Verified first-hand on the 5bb10e7 archive: the self-test PASS; my synthetic red (gen_test_csr_reset.py with
  knob_debug_req_regime put back into schedulable) is refused with "class CsrReset schedules a regime knob its program cannot
  survive: knob_debug_req_regime (consumer dbg) needs a dbg handler the program does not declare"; the committed csr_reset and
  rst_boot pass with mie_stays_zero = True, which their docstrings support (csr_reset only reads CSRs; rst_boot never writes
  mstatus.MIE or mie). Retained: the before-check structural red (the pre-check library accepting the fixture body), the
  run-time red gen_ut_regime_handler_red failing in setup() before the first fetch (`GEN_TEST_FAIL ... knob_debug_req_regime
  (consumer dbg) needs a dbg handler`), and a green csr_reset run on the guarded template (GEN_TEST_PASS, bins 68 = the T-222
  manifest). Manifest rows for the five logs recompute.
- Judgement: this is the guard I asked for in v8 L-1 and it is built where I proposed (TB-side facts: the yaml consumer and a
  per-test declaration), with red and green proofs and a run-time backstop. One caveat as L-3 below.

### L-3 (low) [S2 derive from TB-side facts] The handler declaration is the test's own claim

`program_handlers` is a class attribute the test author writes; a test may declare "dbg" without a debug ROM and the guard
passes. The program generator knows whether it emits code in the DM window and an interrupt handler, so the declaration could
be derived from (or checked against) the program plan at generation time. Not required now (no test declares a handler it
lacks: the only declarations are mie_stays_zero = True on csr_reset and rst_boot); note it for the first test that declares
"dbg" or "irq".

## 2. 5bb10e7: the CM77 touch (M-1 narrowed; the record fixes)

- The lint's class-method walk now refuses an assignment whose target is an attribute chain rooted at self with a
  template-owned first attribute (`self.bridge.cov_witness = f` -> "rebinds self.bridge.cov_witness ...; a template method
  reached through a template-owned attribute is read-only for a test"), as F_OVERRIDE reaching further (REFUSED_FORMS stays
  fifteen); two red sources join the self-test; the before-fix red is retained (gen_t2cm77_lint_red_before.log, the 04cf523
  library accepting the chain assignment). Verified first-hand: `self.bridge.cov_witness = self._f` REFUSED, `self.bridge =
  self._f` REFUSED ("template-owned names are read-only").
- M-1 narrowed, not closed: the single-attribute rebinding of a template METHOD inside a method body is still accepted --
  `self.cmd = self._f` and `self.witness_epilogue = self._f` pass check_test_source at 5bb10e7 (my injection test). The chain
  branch requires a chain longer than one; the class-body F_OVERRIDE branch sees class-level assignments only. Exposure is the
  same as before (the Python pre-check and the log line, never the SV ledger). Required, still under LOG-024d: extend the same
  branch to a single template-owned method name assigned inside a method, with `self.cmd = _f` as the red source.
- Record fixes verified: the unguarded-control row now says the template printed GEN_TEST_PASS and the fixture's own guard then
  failed the run (my L-1 closed); Section 10 says the fixtures prove the Python side only and the SV round trip rests on
  tb-infra's gen_ut_witness until the first real witness green (my I-1 stated); the fixture docstring's history clause dropped;
  the API document's two witness paragraphs describe the as-built form and no longer call Runtime's witness_render pending
  (the flow-side correction of my Section 4).
- Self-found and stated by the Test Writer (SF-TT-1): the LOG-050 touch built its API document from a staging copy that
  predated T-226 and so dropped the rewritten Section 9 witness paragraph; 5bb10e7 restores it and states the staging rule
  (re-archive HEAD after every commit before copying a staged file over the tree). Honest, and the kind of regression the
  immutable-artifact rule exists for.
- Manifest row for the one added log recomputes.

Closure statement: with ae4b2e2 (the epilogue), Runtime's witness_render (as built at ae4b2e2, Section 4) and the DV Lead's
part 4b (WP-1 and the CG-WIT-001 Sample line as built, gen_critic_plan_witness_v11.md), the three owners of T-226 have landed
their parts; my gen_critic_tb_l2b.md M-1 is closed on the code, with the end-to-end green (the first entry that lists
witness_ids) as the remaining evidence. My gen_critic_batch1_v8.md L-1 is closed by 674d026.

## 3. Reconciliation with the 674d026 and 5bb10e7 artifacts (read after Sections 1-2 were written, on 2026-09-03 at 20:49 UTC)

dv/auto_dv/reviews/2026-09-03-claude-diff-0c189eb1-674d026b.md (APPROVE-WITH-CHANGES: two mediums, three lows, one info) and
dv/auto_dv/reviews/2026-09-03-claude-diff-5e05ad75-5bb10e79.md (APPROVE-WITH-CHANGES: two mediums, one low, two infos).

674d026 artifact:
- Its first medium (the API document's witness paragraph reverted to the pre-T-226 wording by the touch) is fixed in 5bb10e7
  (SF-TT-1, Section 2): verified there.
- Its second medium, adopted and verified as M-2: `mie_stays_zero` is not a sound exemption for knob_irq_line_mix, whose
  with_nmi value drives the irq_nm line on one event in four (gen_agents_pkg.sv:588, m[18]) and an NMI is not masked by
  mstatus.MIE; regime_handler_violations(("knob_irq_regime", "knob_irq_line_mix"), (), True) returns [] on the 5bb10e7 archive,
  so a handler-less program declaring mie_stays_zero = True with both knobs schedulable would take an NMI storm, the T-206 class
  of runaway. No committed test is exposed: csr_reset schedules irq_line_mix without irq_regime (quiet, no events) and rst_boot
  schedules irq_regime with line_mix at its default single. Required (owed, the Test Writer's next touch): require an "irq"
  handler when knob_irq_line_mix is schedulable together with knob_irq_regime (or a pinned non-quiet regime), or exclude
  with_nmi from the draw under mie_stays_zero, and state the NMI reasoning beside HANDLER_OF; until then the first test that
  declares mie_stays_zero with both knobs waits for the fix. The dbg rule needs no exemption (debug_req_i is always honoured).
- Its first low, adopted and verified as L-4: the four bus error-rate knobs (imem / dmem err and intg rates) inject faults a
  program needs a trap or NMI handler to survive, and regime_handler_violations(("knob_dmem_err_rate", "knob_imem_err_rate"),
  (), False) returns []; either an "exc" handler kind in HANDLER_OF or a sentence in the API doc that these knobs are outside
  the rule.
- Its second low (the AST reader skips annotated or unpacked class attributes and decorated classes silently, so "anything
  else refused as unreadable" overstates) and its third (a supplied +gen_regime_sched plusarg is applied without the run-time
  check) are adopted as L-5, artifact-quoted: reuse the lint's attribute collector, refuse decorated test classes, and run the
  rule over a supplied schedule's knobs as well, or narrow the API doc's claim.
- Its info (an absent declaration on a subclass of another test resolves to the GenTest default, a conservative false refusal)
  is carried as its own.

5bb10e7 artifact:
- Its first medium, adopted and verified as L-6: the API document's residual paragraph ("Shapes known to pass today",
  gen_test_template_api.md:257-261) still lists `self.schedule.phases = []`, `self.h.b.evt_eot_seen.value = 1`,
  `self.bridge.cmd = None` and `self.log.info = print` as passing while the lint at 5bb10e7 refuses them; the residual must be
  restated with the shapes that still pass. Rated low here because the document errs on the side of claiming less protection
  than exists.
- Its second medium widens my M-1: the helper branch was not extended, so `def _h(t): t.bridge.cov_witness = _f` called with
  self is accepted (verified by my injection on the archive); the same chain walk belongs in the helper branch with a red
  source. M-1 therefore covers three forms: the single template-method rebinding inside a method (`self.cmd = _f`), the helper
  chain, and the shapes the residual paragraph must list.
- Its low (the refusal message says "template method" for non-method attributes) and its two infos (the fixture list in the
  API doc lacks the fifth fixture; a log id kept in the section) are carried as its own.

Mine that neither artifact carries: L-3 (the handler declaration is the test's own claim). Both artifacts agree with Sections
5-6 on the mechanism, the retained reds and greens, and the fifteen-form freeze.

## 4. 99cba0e and ac5853e (verified on the ac5853e archive, which contains both)

99cba0e, the regime rule re-keyed by knob and made values-aware:
- KNOB_HANDLER maps each regime knob to the handler its events need ("dbg" for the debug request; "irq" for knob_irq_regime,
  knob_irq_line_mix, knob_irq_hold and knob_dmem_intg_err_rate, whose load integrity error is an internal NMI; "exc" for the imem /
  dmem error rates and the imem integrity rate), INACTIVE_VALUE names the value under which a knob drives nothing, and the table is
  asserted against gen_knobs at import. regime_handler_violations takes the knobs in play with their values; mie_stays_zero exempts
  the irq knobs only while no NMI can be driven: knob_irq_regime with events and knob_irq_line_mix with with_nmi in play is refused.
  My probes: irq_regime + irq_line_mix under mie_stays_zero -> refused ("events flow and with_nmi is in play (irq_nm is not masked by
  MIE)"); irq_line_mix alone under mie_stays_zero -> accepted (quiet regime, no events); the pair with line_mix pinned to single ->
  accepted; knob_dmem_err_rate without handlers -> "needs a exc handler"; knob_dmem_intg_err_rate -> "needs a irq handler"; the debug
  knob pinned to none -> accepted. Section 3's M-2 (the NMI exemption hole) and L-4 (the bus error-rate knobs) are closed.
- The template's run-time check is values-aware over the pinned knobs, the draw and every phase of the schedule, derived or supplied,
  before any REGIME_SET or the first fetch: Section 3's L-5 (the +gen_regime_sched bypass) is closed. Retained: the before-check
  structural red (gen_t2cm80_structural_red_before.log: the three probes ACCEPTED by the old library), two run-time reds on
  gen_test_csr_reset (pin_storm_nmi: "knob_irq_regime with knob_irq_line_mix: mie_stays_zero exempts ..."; sched_dbg_storm:
  "knob_debug_req_regime needs a dbg handler"), and three greens (the declared test; storm with the line mix pinned single; quiet with
  with_nmi), each failing or passing in setup() as designed. Manifest rows for the eight added logs recompute (8/8).

ac5853e, the helper branch:
- check_test_source's helper walk now applies the attribute-chain rule to a chain rooted at the helper's parameter
  (`def _h(t): t.bridge.cov_witness = _f` -> "helper _h rebinds t.bridge.cov_witness ...; an attribute reached through a template-owned
  name is read-only for a test"), with a red source in the F_HELPER list and the before-fix red retained
  (gen_t2cm85_helper_chain_red_before.log); the refusal message no longer says "template method" for non-method attributes. REFUSED_FORMS
  stays fifteen. My probe: the helper chain is REFUSED.
- My CR-T226-M-1, restated against ac5853e: the chain forms are closed (`self.bridge.cov_witness = f` REFUSED; the helper chain
  REFUSED). Still ACCEPTED by my probes: the single template-method rebinding inside a method (`self.cmd = self._f`,
  `self.witness_epilogue = self._f`) and the local alias (`b = self.bridge; b.cov_witness = self._f`). The API document's residual
  paragraph (restated in 5bb10e7 and ac5853e) is where these two shapes must be listed as passing until refused. M-1 stays owed,
  narrowed to those two shapes; exposure unchanged (the Python pre-check and the log line, never the SV ledger).

Closure statement for the four touches: gen_critic_tb_l2b.md M-1 closed on the code (T-226's three owners landed; the end-to-end
green through the real dispatcher remains the closing evidence with the first entry that lists witness_ids); gen_critic_batch1_v8.md
L-1 closed and strengthened (the rule is now knob-keyed, values-aware, run-time enforced over pinned and scheduled values, with reds
and greens retained); Section 3's M-2, L-4 and L-5 closed; Section 3's L-3 (the handler declaration is the test's own claim) and
L-6 (the residual paragraph) stand; CR-T226-M-1 open as narrowed above.

## 5. Reconciliation with the 99cba0e and ac5853e artifacts (read after Section 4 was written)

dv/auto_dv/reviews/2026-09-03-claude-diff-9b3e6583-99cba0e3.md and 2026-09-03-claude-diff-99cba0e3-ac5853eb.md, both APPROVE-WITH-CHANGES.
Both agree with Section 4 on the mechanism: the knob-keyed, values-aware rule with the NMI closure sound (the artifact traced
knob_dmem_intg_err_rate to irq_nm_int under MemECC = SecureIbex and the external NMI to the with_nmi mix alone), the run-time check
before any REGIME_SET, the helper chain refused, the retained reds and greens as recorded.

Adopted after verification on the ac5853e archive:
- M-1 widened again (the ac5853e artifact's second medium): a decorated module-level helper evades every helper check
  (`@deco def _h(t): t.bridge.cov_witness = 1` called with self: ACCEPTED by my probe), because the escape rule's helper
  set includes decorated functions while the body walk excludes them; and a helper given the attribute rather than the test object
  (`def _h(b): b.cov_witness = 1` called as `_h(self.bridge)`: ACCEPTED) passes, as does the local alias of Section 4.
  CR-T226-M-1 therefore stays open for four shapes: the single template-method rebinding inside a method, the local alias, the
  decorated helper and the helper given a template attribute. The fix the artifact names (the escape rule's helper set equal to the
  walked set; a parameter bound to self.<template attribute> treated as template-rooted) is the right one; until then the API
  document's residual paragraph must list these shapes as passing.
- L-7 (low, its first medium kept low): gen_test_template_api.md's new parenthetical says `b = self.bridge` is refused as an escape;
  my Section 4 probe shows the alias followed by `b.cov_witness = self._f` ACCEPTED, so the paragraph that was rewritten to remove
  false refusal claims carries a new one; drop the parenthetical or make it true with a red / green pair in the self-test.
- L-8 (low, artifact-quoted): the 99cba0e artifact's medium is a record error outside the guard: gen_tdd_batch3.md says gen_isa_shim.cc
  is "unchanged since 3be5a34" while the shim changed in five later commits; the conclusion holds only because 9e912bb precedes the
  export; the sentence and the log header that repeats it should be corrected beside the manifest row.
- L-9 (low, artifact-quoted): the run-time check covers the knob plusargs, the draw and the schedule but not the raw per-mille
  plusargs the bus agents also honour (+gen_ibus_err_rate, +gen_ibus_intg_err_rate, +gen_dbus_err_rate, +gen_dbus_intg_err_rate),
  which inject the same faults outside any regime knob; check them in setup() or state the limit in the API doc.
- Its remaining lows are carried as its own: the import guard checks KNOB_HANDLER's names but not the converse (a new irq / dbg
  consumer or err_rate knob absent from the map would be silently unmapped) and not the yaml defaults the NMI closure relies on;
  AugAssign on the rule attributes and a metaclass keyword pass the structural reader (setup() catches the real value); the API
  doc's "a pin of the other knob to an active value fails" is conditional on the drawn or scheduled values; "helpers in other
  modules" and "string-built names" in the residual paragraph name shapes imprecisely.

Mine that neither artifact carries: Section 3's L-3 (the handler declaration is the test's own claim) and the closure statements.
