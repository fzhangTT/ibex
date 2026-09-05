# Critic verdict: the round-2 request form v2 and its checker (feature group round-2 form)

Artifacts at 8239c0b (v2; v1 is 6407118, reviewed before execution as e28cefa / CM223; range 02b9f3d..8239c0b for the
two files):
- dv/auto_dv/evidence/gen_round2_request.md  sha256 9403f5654fe26ed7  319 lines (a round request form: PLAN scope under LOG-095)
- dv/auto_dv/tools/gen_round_form_check.py  617d38e0ed0c635f  314 lines (CODE scope)
Inputs judged against: dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml (c8a2cd5bec60757d, byte-identical to the
out-tree manifest, the checker's default); gen_r1_preflight_classification.md at 8239c0b (:22-31, :126-127, :140);
gen_round1_request.md:178-179; the flow modules at 8239c0b; LOG-095/LOG-097 (round-2 scope, the per-entry seed decision);
docs/dv/dv_principles.md d9c27db18f511411.
Date: 2026-09-05T03:07:22Z   Role: Critic
Method: detached worktree of 8239c0b in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/r2form/); every figure of the form re-derived by my own code over the committed manifest, the
selector and arithmetic (r2form/rederive.py, rederive.log), not by the checker; the checker run on the committed form and
in --self-test; the new checker run on the v1 text and the v1 checker on both texts; every code citation opened. The v1
pre-execution review e28cefa was NOT read before Sections 1-5 (Section 6 reconciles it). Exposure: the Orchestrator's
naming message summarised the group's substance (the margin figures, the seed rule, the twelve-seed derivation, the
checker's claim); no review body was read.

## 1. What the form asks and what the checker does
The form fixes round 2's base seed (20260905, disjoint from round 1's measured seed values), states a seed rule (an
entry's seed count in a measured round may not exceed the seeds its manifest was measured over) and withdraws v1's claim
that the rule is checkable today (no manifest carries a measured_seeds field; the loader comparison is a flow item),
measures the margin of every declared bin from the round-1 manifest (the smallest hit count over the entry's runs),
keeps the twelve existing measured entries at three seeds, asks twelve seeds for the three PMP entries and the IRQ
entry with the 1 - 0.05^(1/n) derivation, prices everything from the round-1 manifest, leaves Section 7 (expected
outcomes) empty with a form v3 at the round's commit owed its own pre-execution review, and does not claim the
functional gate. The checker parses each numeric claim it covers out of the form and recomputes it from the manifest,
the pre-flight record or arithmetic; a claim it cannot find fails.

## 2. Reproduction (my own code, then the checker)
- Margin table: for each of the 12 measured entries the declared bins, the bins whose smallest count over the three
  runs is 1, the share and the median smallest count reproduce row by row (csr_access 4 / 0 / 0.0 / 47.5; isa_cti 184 /
  1 / 0.5 / 118; isa_alu 563 / 30 / 5.3 / 33; csr_trap_setup 146 / 12 / 8.2 / 13.5; cmp_zca 300 / 81 / 27.0 / 5; mul_div
  196 / 55 / 28.1 / 4; isa_shift 120 / 35 / 29.2 / 5; cmp_zcb 96 / 32 / 33.3 / 4; bit_ratified 617 / 276 / 44.7 / 2;
  cmp_zcmp_basic 325 / 193 / 59.4 / 1; rst_boot 6 / 4 / 66.7 / 1; mul_mul 338 / 244 / 72.2 / 1); totals 2895 declared,
  963 hit once (33.3 percent), 1327 at three or fewer (45.8 percent); 8685 bin checks, every state HIT; the bin key sets
  are identical across each entry's runs (asserted). Section 3.2 holds.
- Costs: wall 362.9 s, 53 runs, per-run sum 940.7 (measured 689.3, unmeasured 251.4), mean 17.7 / min 6.6 / max 69.5;
  one extra seed over the twelve 229.8 s; the four with margin 102.9 (x12 = 1234.4), the eight 126.9 (x12 = 1522.8); the
  three PMP entries 49.2 (x9 = 442.8); uniform +9 seeds 2067.9; 12 x twelve 2757.2; 40 x twelve 9190.7 (the form's 9191);
  speedup 940.7 / 362.9 = 2.59. Per-run means csr_trap_setup 10.0, csr_access 9.7, cmp_zcb 8.2 (the cheapest measured
  entry, as v2 now says). Sections 3.3 and 4 hold.
- Selector at 8239c0b, base 20260904: smoke 17 entries / 47 runs / 36 measured; through targeted 20 / 56 / 36 (so the
  targeted-only rows are 3 / 9 / 0); full 20 / 56 / 36; gen_test_irq_basic at tier smoke, seeds 3, measured false. Section
  1's table (labelled the state at 6407118) is also the state at 8239c0b. The 12 measured entries' 36 seed values at base
  20260904 share 0 values with base 20260905 (Section 2).
- Confidence table: 1 - 0.05^(1/n) = 0.632 / 0.312 / 0.221 / 0.139 / 0.072 and 0.75^n = 0.42 / 0.10 / 0.032 / 0.0032 /
  0.00001 for n = 3, 8, 12, 20, 40; 0.05^(1/3) = 0.368. Section 3.5 holds.
- Section 3.4's table equals gen_r1_preflight_classification.md:22-31 (stable 123, seed-dependent 123 over four entries);
  the rst_boot bit-8 withdrawal is at :126-127. Section 5's rate has retained sources: gen_round1_request.md:178-179 and
  gen_r1_preflight_classification.md:140 (180 mie writes per run, operand 0x80000000 in 10 of 40 seeds).
- Code citations at 8239c0b open as stated: gen_flow_util.py:1618-1631 (TIER_RANK rank, the check tier apart),
  :1634-1638 (seeds_for_test takes the override for every selected entry), gen_regress.py:613-614 (base seed from the start
  time when unset), gen_fcov.py:328-331 ("manifest declares no bins") and :361 (the unverifiable verdict).
- The checker on the committed form: PASS, 133 claims compared and all reproduce; --self-test PASS, six cases (the
  committed form passes; a wrong declared-bin count, a wrong wall clock, a wrong share, a dropped claim and the wrong
  four-with-margin each fail).
- The skip defect and its fix, measured: the v1 checker on the v1 form reports PASS (123 claims) although the v1 text
  carries three wrong figures; the v2 checker on the v1 text reports exactly three failures (csr_access median 80 vs
  47.5; csr_trap_setup median 14 vs 13.5; "set at 10.0 s per run: not a measured entry", the shape-based catch of v1's
  false cheapest-entry sentence) and exits 1. The v1 checker on the v2 form fails on the table shape. The defect the
  commit describes (a per-entry-mean check that skipped when its sentence did not match) is real and closed: v2 parses
  every "<entry> at <n> s per run", requires at least one and refuses a non-measured name.

## 3. Judgement of the plan
- The seed decision follows the measurement: three seeds for the twelve because their declared sets were calibrated to
  three and a third of their bins have no margin; twelve for the newly measured entries with a derivation that says what
  twelve concludes (a bin unhit after twelve seeds has a per-seed rate below 0.22 at 95 percent) and why not fewer.
  This is LOG-097's "per-entry decision, not a blanket increase", with the derivation and the budget stated.
- Honesty: v1's "checkable" claim is withdrawn in the text, the two missing pieces are named with owners (the Test
  Writer's measured_seeds field, runtime-2's comparison), Section 7 is declared empty with the consequence (no round on
  v2; v3 at the round's commit with its own review), the Section 5 sample is marked biased and not projected, the
  functional gate is not claimed. dv_principles.md Section 4 conformance in the form itself.
- The seed rule as written is a policy until measured_seeds and the loader comparison exist; the form says so. The PMP
  and IRQ entries at twelve seeds rest on their manifests being measured over 40 seeds before the round (Section 3.5
  and the standing rule), which the joint PMP and IRQ landings must show; this verdict does not pre-approve those counts.
- What the form leaves to v3 (Section 1 restated from the selector at the round's commit, Section 7 filled, the LSU /
  ECC / timing entries' seed counts from their owners) is exactly what LOG-095 names as a form changing the round's
  shape: v3 takes a Critic verdict of its own.

## 4. Rows
- L-1 (Low, records). The CM223 rows the commit message answers (M-1 checkable claim, M-3 Section 7, the three numeric
  errors, the cheapest-entry sentence, rst_boot, the 123 scoping) appear in no response file: git grep CM223 over
  dv/auto_dv at HEAD finds nothing. The team's convention answers review rows in the author's response file with the
  next touch; add the CM223 dispositions there.
- L-2 (Low, checker scope). The checker's Section 3.3 sentence check is shape-based ("<entry> at <n> s per run"), so the
  v1 error "the cheapest entry in the set at 10.0 s per run" is caught as "set ... not a measured entry", not as the
  false superlative it was. The catch is conservative (any non-entry word before "at N s per run" fails), and the form
  now states the superlative with all three figures, so nothing is wrong today; a direct check of "cheapest" against
  min(mean) would say what is being verified. Optional.
- Observation. The margin statistic treats a bin absent from a run's check as count 0; on round 1 every entry's runs
  carry the same bin set (asserted in my re-derivation), so the rule has no effect today; it is the right default.
- dv_principles.md conformance: PASS. Section 4 as above; Section 5: the checker's comments state intent, its docstring
  states its scope and its single source is the committed manifest; Section 6: the checker's self-test drives the real
  code path with five perturbations and a positive control; the form is a plan and needs no triad.

CRITIC VERDICT: APPROVE. The round-2 request form v2 states a per-entry seed decision derived from a measurement that
reproduces figure for figure from the committed round-1 manifest, withdraws the one claim it could not support, and
leaves the round's expected outcomes to a v3 that will be reviewed at the round's commit; its checker recomputes 133
claims from sources, fails on a dropped or wrong claim, and now catches the three errors v1 carried. L-1 and L-2 are
records and scope rows, not conditions.

## 6. Reconciliation with the v1 pre-execution review (read after Sections 1-4)
dv/auto_dv/reviews/2026-09-04-claude-plan-gen_round2_request.md at e28cefa (688533aa04376f07, APPROVE-WITH-CHANGES on v1
6407118: three Medium, six Low, four Info), read at 2026-09-05T03:08:24Z. No review of v2 exists at HEAD 92d6ea2; this verdict judges
v2 and its Section 2 measurements are the evidence that each row is closed there:
- M-1 (the seed rule called checkable while nothing records the measured seed count): v2 withdraws the claim and names
  the two missing pieces with owners (Section 3.1). Closed as a plan statement; the flow items stay owed elsewhere.
- M-2 (csr_trap_setup "cheapest entry in the set" false; cmp_zcb 8.2 is cheapest): v2 states all three figures (my
  means 10.0 / 9.7 / 8.2) and the checker now parses every per-run mean in prose. Closed; my L-2 notes the check's shape.
- M-3 (Section 7 empty while Section 11 accepts against it; no review path for the restated sections): v2 declares the
  section empty, says no round is dispatched on v2, and owes a v3 at the round's commit with its own pre-execution
  review. Closed as a statement; LOG-095 gives v3 a Critic verdict as well (Section 3 above).
- Low (selector table at 0203c6e): restated at 6407118 (20 / 56 / 36, gen_test_irq_basic named); my selector call at
  8239c0b returns the same. Closed.
- Low (upper median): statistics.median in the checker and the two rows corrected (47.5, 13.5); my medians agree. Closed.
- Low (MARGIN_FOUR unverified): the constant is gone; the four are derived by ranking zero-margin shares and both sets
  are compared (self-test case "naming the wrong four with margin fails"). Closed.
- Low (default manifest out of tree): the committed gen_round_0/gen_regress_manifest.yaml is the default; byte-identical
  to the out-tree copy (c8a2cd5bec60757d). Closed.
- Low (self-test not through run_checks; "every numeric claim" overstated): the self-test drives run_checks on the
  committed form with five perturbations; the form's Section 11 scopes the checker to the claims run_checks covers.
  Closed.
- Low (rst_boot "two boundary values"): one value awaits a ruling, the bit-8 half withdrawn at :126-127. Closed.
- Info (123 scoping; cite :328-331 with :361; the hard-coded 4.0; the P-07 label): the first three are in v2 (Section
  3.4 "of the pre-flight's unmet set", Section 7's citation, the word parsed from "sit on four entries"); the P-07
  label is settled by LOG-098's corrigendum (22a338a: the P-nn namespace is review-local). Closed.
- Not in the review: L-1 (the CM223 dispositions live in the commit message only, no response-file rows). The verdict
  stands: APPROVE, rows L-1 and L-2.
