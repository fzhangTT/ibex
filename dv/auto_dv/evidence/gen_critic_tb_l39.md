# Critic verdict: the range 1b65f86..4a00702, closing at the round-1 HEAD (iteration 2, v4y, landings 40c and 40d, two LOG corrigenda, the Test Writer's records touch, the request-form corrigendum; four artifacts committed as written), reviewed as tb_l39

Scope (the Orchestrator's): twelve commits, 28 files, 995 insertions, 276 deletions, nothing under rtl/ and no .f-listed TB source (the flow build identity is
unchanged from 726682a): 54f1e17 (the review of 04870ee..1b65f86, as written), 85dea9c (tb_l38, as written), cd9a234 (LOG-091 corrigendum: the five manifest
removals and two module edits, CR-38 L-2), 3142adc (the Test Writer's iteration-2 re-scope of bit_ratified, cmp_zca and csr_trap_setup), 6f360ba (the DV Lead's
v4y: the verifier's mark-set text corrected, CR-38 L-5), ae6e73e (tb-infra-2's landing 40c: the quiesce assertion gated on the loop's own two consecutive
samples, CR-38 L-3), 01e515a (landing 40d: MUT-RETSKEW1 as a retained diff file, CR-38 L-1), 9e7c17b (the review of e641b24..04870ee, as written; the artifact
tb_l37's Section 6 was owed against), c118720 (LOG-089/091 corrigendum: class A 758 = 631 + 127, seven modules, gen_regress.py:16), 802cae5 (the Test Writer's
records touch: the class explanation kept once, rst_boot's bit-8 reason given its cause, CR-38 L-4), 755e813 (my P-07 note as an evidence file, as written),
4a00702 (the DV Lead's request-form corrigendum, the round HEAD: 12 checked entries, 36 measured runs, 2895 declared bins, 8685 bin checks, 17 unmeasured runs,
the instrument accounting). This file also carries tb_l37's owed Section 6 (a corrigendum section at the end). The cross-model review of the same range
launched at 21:48Z; Section 6 follows when its artifact is committed. Sections 1-5 were written before reading it.

Artifacts reviewed (committed blobs at the commit named; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_round1_request.md @4a00702  9f0e88e4072af842
- dv/auto_dv/tests/gen_test_bit_ratified.py @3142adc  fecf18d5c2e32fe3
- dv/auto_dv/tests/gen_test_cmp_zca.py @3142adc  45a03f313f466119
- dv/auto_dv/tests/gen_test_csr_trap_setup.py @3142adc  ada2e1df1823c3f7
- dv/auto_dv/fcov_expectations/gen_test_bit_ratified.fcov.yaml @3142adc  8b0b8d1301a6004e
- dv/auto_dv/fcov_expectations/gen_test_cmp_zca.fcov.yaml @3142adc  2f87dd57681d15c9
- dv/auto_dv/fcov_expectations/gen_test_csr_trap_setup.fcov.yaml @3142adc  4dc47e9e2451eddb
- dv/auto_dv/tools/gen_unbuilt_mark_check.py @6f360ba  8bf4f6034780344b
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_store.py @ae6e73e  8308c6d7c34e3d99
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py @ae6e73e  0c84cf73e2940b5f
- dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py @ae6e73e  0beeec988eba471f
- dv/auto_dv/tb/unit/gen_ut_pair_quiesce_model.py @ae6e73e  048de32612e75097
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l40c_quiesce_exhaustion.log @ae6e73e  4c193f9a71886cd6
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l40_MUTRETSKEW1_mutant.diff @01e515a  a75295b6b533356b
- dv/auto_dv/tests/gen_test_rst_boot.py @802cae5  f0b3dd19b4d2bab1
- dv/auto_dv/fcov_expectations/gen_test_rst_boot.fcov.yaml @802cae5  f2adf3ed9e75efcc
- dv/auto_dv/tests/gen_test_template.py @802cae5  22cd1010e3d9ba12
- dv/auto_dv/docs/gen_intervention_log.md @c118720  d22e4fbd79c50d7e
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md @4a00702  a5299eb291054035
- dv/auto_dv/flow/gen_testlist.yaml @4a00702  702be271937dcc0d

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411 (trust-triad rule 3 as LOG-090 reads it);
LOG-085 to LOG-091 with their corrigenda; gen_critic_tb_l38.md (e7a1909c8a7ec7d3) rows CR-38 L-1..L-5 and gen_critic_tb_l37.md (c9f8e05d0bf806bf) row CR-37 L-4;
the acceptance-form rule; the retained re-flights r1_fcov_reflight (1b65f86) and r1_fcov_reflight2 (3142adc) as the measured basis.
Method: detached git worktree of 4a00702 (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK PASS, validate 23 OK, TBMAN 3489 rows 0 bad;
flow build identity bc0cd7778e382b13 over 117 sources, unchanged since 726682a; my TB-source recipe 7585b4afb4d05cd8, moved by the Python of landing 40c and its
unit test only). On detached archives: the three iteration-2 manifests and rst_boot's regenerated with gen_fcov_manifest.py --test-module --test --write and
compared byte for byte; the added bins_not_hit entries read by AST and classified against the first re-flight's per-seed unmet sets, each class-C reason read for
a cause; the verifier run as committed at v4y and under its --self-test; landing 40c's model unit test run under its --self-test on the committed tree and, as its
own positive control, against the pre-40c tests of 9f47277; landing 40d's diff applied to gen_bridge_if.sv; the form corrigendum's every figure re-derived with
the flow's own loader, select_tests, seeds_for_test, measured_refusal and gen_regress.fcov_policy_failures on the 4a00702 testlist and with the checker's parser
over the twelve manifests; the two re-flight manifests read in the out-tree; the RTL and TB terms behind the new rst_boot reason read at their lines. EXPOSURE:
the Orchestrator's messages (its "8 unmeasured runs" slip named before I read the form, verified at the line); the authors' retained logs and the out-tree. No
subagent used.

CRITIC VERDICT: REQUEST-CHANGES, confined to the request form as pinned at 4a00702 (four stale cells adopted from the range's cross-model review and
verified by me, M-1..M-4 below); every other commit in the range is verified and approved. The round-level figures of the form reproduce through the flow's
own functions (19 / 53, 12 measured entries all checked over 36 runs, 2895 declared bins, 8685 bin checks, 17 unmeasured runs, zero policy flips) and the
second re-flight observed all 36 expectations met, so the round itself stands as dispatched; what is gated is progress built on the form's text, that is,
the round record's citation of it, until the DV Lead's v5c corrects the four cells and a re-review records it. Sections 1-5 below were written as APPROVE
before the review artifact was read; Section 6 states what changed and why.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 3142adc (Test Writer iteration 2) | bins_not_hit added to bit_ratified, cmp_zca and csr_trap_setup after the first re-flight; manifests re-rendered to 617 / 300 / 146 | on a detached archive the three manifests (and rst_boot's) are BYTE-IDENTICAL to the re-render; the added entries equal the r1_fcov_reflight unmet unions exactly (37 / 24 / 5; nothing unmet anywhere stays declared); class C = the every-seed sets (24 / 22 / 1), each reason a cause (an operation never paired with this aliasing shape, equal-operand class or destination state; binv never applied twice to one bit; an adjacency order never placed; no self-targeting compressed jump; no half-word-aligned placement; a bit pattern never written); class B (13 / 2 / 4) with the per-run wording; no removals or rewordings |
| 6f360ba (DV Lead v4y) | the verifier's docstring and MARK leg reworded to the referenced-manifest scope, a population line added (CR-38 L-5) | at 4a00702 it prints "147 marked coverpoint(s) of 1944 on 182 unbuilt covergroup(s); 25 covergroup(s) rendered", 1944 being my own count in tb_l38, and "a MISSING mark is caught by DECL, not here"; PASS; --self-test PASS |
| ae6e73e (tb-infra-2 landing 40c) | the loop samples the pair into the variables the assertion uses and the assertion is gated on settled == 2 in gen_ut_lockstep, gen_ut_intg_span and gen_ut_intg_store (CR-38 L-3); the discriminating red at model level in the committed unit test gen_ut_pair_quiesce_model.py; MUT-RETSKEW1 re-run through the new gate; the "Two writers, one pair" comment kept once (CM215-Low-4) | the three diffs read: the fresh post-loop read is gone, the assertion reads settled == 2 with the loop's last pair in its message (:63 / :76 / :78); the unit test is committed (seven files in the landing) and its --self-test passes on the 4a00702 archive (the in-flight stream passes the old shape and fails the new, a settled stream passes); run against the 9f47277 tests it reports itself stale, rc 1, the positive control the log states; the MUT-RETSKEW1 re-run reads 175 vs 176 and 176 vs 177 on lockstep through the new gate's message; the log states plainly that this is the exhaustion path's positive control and not the discriminating red, and why the transient case is not constructible in simulation; manifest row 14697 / fa520c1fc48430c3 equals the blob |
| 01e515a (landing 40d) | gen_fu_l40_MUTRETSKEW1_mutant.diff retained with a manifest row (CR-38 L-1) | the diff (407 bytes, md5 b0b46c7a12ce3be6 = row) applies to gen_bridge_if.sv at 9f47277 and reproduces the quoted line 61; that line gave the mutated root's digest 7ef155c3ddcab7fd in tb_l38 |
| 802cae5 (Test Writer records touch) | the class explanation kept once on the attribute's declaration in gen_test_template.py with one-line pointers in six modules (CM215-Low-4); rst_boot's reason for gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero names its cause (CR-38 L-4) | the rst_boot manifest re-renders BYTE-IDENTICAL with the new header line; the cause holds in the RTL and the TB: CSR_CPUCTRLSTS reads {zeros, cpuctrlsts_ic_scr_key_valid_q, cpuctrlsts_part_q} at rtl/ibex_cs_registers.sv:666-669 with cpu_ctrl_sts_part_t eight bits wide (:238-246), so the key-valid flag is bit 8, registered from ic_scr_key_valid_i at :1942-1945; the TB knob key_reset_valid (gen_tb_knobs.yaml:32, default 1; PLUSARG_KEY_RESET_VALID = gen_key_reset_valid, gen_tb_pkg.sv:31) drives vif.valid out of reset (gen_agents_pkg.sv:450 / :454) |
| cd9a234, c118720 (LOG corrigenda) | (c) of LOG-091 corrected: five manifests removed and two modules edited, with the instrument accounting; class A 758 = 631 + 127; seven modules assign bins_not_hit; the R-5.5 text at gen_regress.py:16; the three work-directory citations to be committed as evidence | every figure equals mine (tb_l38 Section 1 and its L-2; the 631 / 127 / 282 split of tb_l37 I-3; my earlier count of seven assignments against nine files carrying the token); the P-07 note is the first of the three committed (755e813) |
| 4a00702 (DV Lead, the form corrigendum, the round HEAD) | 19 entries / 53 runs; 12 measured entries at 36 runs, all checked, 2895 declared bins, 8685 bin checks; 7 unmeasured entries at 17 runs; --seeds 3 gives 57 with 36 measured, --seeds 5 gives 95 with 60; the 12 pin nothing; the detaches superseded and the instruments named; the expectation measured by r1_fcov_reflight2 (36 / 36 / 0) | select_tests, seeds_for_test, the loader and the checker's parser on the 4a00702 testlist give exactly those figures (declared per entry 617 / 563 / 338 / 325 / 300 / 196 / 184 / 146 / 120 / 96 / 6 / 4); gen_regress.fcov_policy_failures on the 53 planned runs flips 0 with covergroups_exist False and True; measured_refusal 0 of 19; the r1_fcov_reflight2 manifest (head 3142adc, status done) reads 36 runs, 36 PASS, fcov_check PASS on all 36 with the same twelve declared counts, so the form's per-entry expectations are observed; the testlist at 4a00702 equals 1b65f86's and the twelve manifests equal 3142adc's, so the prediction carries to the round HEAD |
| 54f1e17, 85dea9c, 9e7c17b, 755e813 | artifacts committed as written | 54f1e17 reconciled in tb_l38 Section 6; 85dea9c content e7a1909c8a7ec7d3 = handed; 9e7c17b reconciled below as tb_l37's Section 6; 755e813 content c4b359f426fcace3 = handed |
| gate at 4a00702 | identity and TB manifest | gen_tb bc0cd7778e382b13 over 117 sources (git diff over tb, env, isa and rtl since 726682a lists no .f-listed source); TBMAN 3489 rows 0 bad; validate 23 OK |

## 2. Rows

- CR-38 L-1 (40d), L-2 (cd9a234), L-3 (40c), L-4 (802cae5), L-5 (v4y): all answered and verified above. CR-37 L-4 (the form's stale clauses): answered by
  4a00702. CR-36 L-1 (the report-phase boundary) and CR-36 L-2 (the tag-half discriminating red): open, post-round. CM216-Low-2: half answered by 755e813.
- Row raised here: CR-39 L-1 (DV Lead, the form).

## 3. Findings

- L-1 (gen_round1_request.md:231 at 4a00702): section 10 says "one of the 8 unmeasured runs is a round-1 blocker" while the round has 17 unmeasured runs over 7
  entries, as sections 1 and 6 of the same version state (lines 36, 43, 153). A wording slip in the acceptance clause; the round record should quote 17.

### Informational

- I-1: the form says a tool derived and re-checked its section and "refuses when an input differs from the commit"; the commit carries the form alone, so the
  tool is not in the record. Every figure re-derives here with the flow's own functions, so nothing rests on the tool; the round record should name it or the
  DV Lead should commit it.
- I-2: landing 40c's discriminating red is at model level by stated reasoning (the transient equal 21st sample is not constructible with this TB's stimulus);
  the model is committed with a self-test that reads the test file it models and fails when the shape drifts, which is the right shape for a Python-only
  predicate; the simulation-side evidence (MUT-RETSKEW1 through the new gate) is correctly labelled a positive control and not a discrimination.
- I-3: the TB-source recipe at the round HEAD is 7585b4afb4d05cd8 (moved by landing 40c's three tests and its unit test); the committer's identity the canary
  must report is bc0cd7778e382b13, unchanged since 726682a.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S3 intent-derived checking / trust-triad rule 3: every measured run in the round carries an
enforced per-run claim and the second re-flight observed all 36 met (conforming). S4 honesty: the form corrigendum states how the round got here and what its
first version promised against what it now claims; the three unmeasured entries are named with the rule that removed them; landing 40c labels its
simulation evidence as a positive control rather than a red (conforming); one wording slip (L-1) and one uncommitted tool (I-1). S6 trust triad: landing 40c's
predicate change carries a discriminating red at model level with a staleness control, landing 40d retains the mutation diff, the verifier's self-test stands
(conforming). One-line verdict: PASS, one Low owed.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES on the range 1b65f86..4a00702, confined to the request form gen_round1_request.md as pinned at 4a00702. Rows CR-39 M-1..M-4
(DV Lead; adopted from the range review and verified in Section 6), CR-39 L-1 (DV Lead, the "8 unmeasured runs" clause, since fixed in v5b) and CR-39 L-2
(Test Writer, adopted). Gated: the round record may not cite the pinned form's per-tier measured cells, its "45" measured seeds, its 246-only instrument
accounting or its "empty diff" statement; it cites v5c (or later) once that corrigendum is committed and re-reviewed. Not gated: iteration 2, v4y, landings
40c and 40d, the records touch, the LOG corrigenda, the dispatch and the round itself, all verified. The round record's verdict will read the round manifest
against the form's per-entry table, the 36 measured runs against the twelve manifests, the 17 unmeasured runs as clean, and the identity against the canary.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-1b65f864-4a007028.md, committed a1d2bdb, blob 780b498c7500603f, 53 lines, verdict APPROVE-WITH-CHANGES:
four Mediums, four Lows, one Info. Reviewer identity as its header states: the Claude fallback (claude-fable-5-1, a fresh session on a detached checkout of
4a00702). Read after Sections 1-5 were written.

WHAT CHANGED ON READING IT, stated first. Sections 1-5 were written as APPROVE with one Low, and their Section 1 row for 4a00702 says the form corrigendum's
figures reproduce. That is true of every round-level and derived figure I recomputed (the selection, the seeds, the declared and checked counts, the
overrides, the policy, the gates, the re-flight) and false of four cells of the pinned text that I did not read against the tree, all four found by the
review and each verified by me at 4a00702 before adoption:

- M-1 (gen_round1_request.md:28-31): the per-tier table still reads smoke 42 and targeted 3 "of which measured" (45) while THE ROUND row was corrected to
  36; the flow at HEAD gives smoke 36 / targeted 0 (bit_draft is targeted and unmeasured; csr_reset and pmp_csr_warl are smoke and unmeasured); line 26
  still says "Derived at e641b24".
- M-2 (:53): "0 of the 45 measured values shared with base 20260905"; the measured set is 36 (my derivation in Section 1 gave 0 of 36 and I did not compare
  it to the sentence).
- M-3 (:144-146): the instrument accounting counts 246 built-covergroup declarations removed (123 stable + 123 seed-dependent) and omits iteration 2's 66
  (47 stable + 19 seed-varying) that the same version's table already reflects (617 / 300 / 146); the bins_not_hit removals are understated by 66.
- M-4 (:245): "a diff of 726682a against HEAD over dv/auto_dv/tb, dv/auto_dv/env, dv/auto_dv/isa and rtl is empty" is false at the pinned HEAD: git diff
  --name-only lists dv/auto_dv/tb/unit/gen_ut_pair_quiesce_model.py (landing 40c's unit test, Python under dv/auto_dv/tb). The identity bc0cd7778e382b13 is
  unchanged because that file is not .f-listed, which is the claim that matters and which my Section 1 stated in that qualified form; the form's unqualified
  statement contradicts the tree, and the form tells the Orchestrator that anything under those paths makes the canary stale, so the sentence would have
  misdirected the very check it prescribes.

CORRIGENDUM to Sections 1-5: the Section 1 row for 4a00702 reads "every figure re-derived"; it should read "every round-level and derived figure
re-derived; four cells of the pinned text are stale (Section 6)". The verdict paragraph and Section 5 were rewritten before the hand-off to state the
REQUEST-CHANGES, because a header may not carry a verdict the file no longer holds; the original wording was APPROVE with one Low. The lesson is
recorded in my STATUS and notes: re-deriving a record means reading every cell of it against the tree, not only the totals one can recompute.

Why REQUEST-CHANGES and not owed Mediums inside an APPROVE: M-4 is a statement about the tree contradicted by the tree at the pinned HEAD, undisclosed by
the author; under the standing rule that forces REQUEST-CHANGES. It is confined to the form's text, the DV Lead's v5c is already announced for these four
cells (CM217), and v5b (0dfac95, outside this range) already fixes L-1 and carries the 25 / 41 measurement, so the gate is narrow: the round record cites
v5c or later. Nothing about the dispatch or the round changes.

Agreements with the rest of the artifact: its verifications equal Section 1 (the four manifests byte-identical at 617 / 300 / 146 / 6; the 66 added keys
equal the re-flight unions with the right stability classes; the verifier's population line and self-test; landing 40c strictly stronger with no read after
the loop and the exhaustion path failing; the form's round-level figures; the two review artifacts and the two as-written commits). Its Lows: L-1 is my
CR-39 L-1 (the "8 unmeasured runs" clause), fixed in v5b; its second Low (the LOG corrigendum's "seven test modules" against six with a non-empty dict at
04870ee, pmp_mseccfg carrying an empty one) is agreed and already corrected by 5e72506 outside this range (at 4a00702 the count is eleven non-empty of
fourteen assignments, the re-scope having added five); its third Low, adopted as CR-39 L-2 (Test Writer): the bit_ratified reason for the cr_op_same
*_all_same crosses says "the register-aliasing classes are reached" while cp_same_regs.all_same is itself listed seed-dependent one entry above, so the
wording over-claims for the all_same crosses (the stability class is right); its fourth Low (the model's BOUND = 20 re-types QUIESCE_CYCLES, guarded by the
staleness needle) is agreed as informational. Its Info (the reflight2 manifest records git.dirty_tracked_files True for the dispatching clone at 3142adc
while the runs came from the head-mode mirror of 3142adc, so the form should say the mirror is the source) is verified in the manifest and adopted as
informational for v5c.

Disagreements: none. Rows after reconciliation: CR-39 M-1..M-4 (DV Lead, adopted and verified), CR-39 L-1 (DV Lead, fixed in v5b), CR-39 L-2 (Test Writer,
adopted). CRITIC VERDICT: REQUEST-CHANGES, confined to the pinned form, as stated in Section 5.

## Corrigendum: tb_l37's Section 6, reconciliation with the cross-model review of e641b24..04870ee

tb_l37 (gen_critic_tb_l37.md, committed e87368f, c9f8e05d0bf806bf) covered e641b24..d1f6019 and could not reconcile because no review of that range had been
launched; its Section 6 is written here against the review the Orchestrator commissioned afterwards for e641b24..04870ee: dv/auto_dv/reviews/
2026-09-04-claude-diff-e641b24c-04870ee1.md, committed 9e7c17b, blob 24c92aacfff4d6d2, 59 lines, verdict APPROVE-WITH-CHANGES, five Lows and two Infos.
Reviewer identity as its header states (the Claude fallback, a fresh session on a detached checkout of 04870ee).

Agreements: its verifications equal tb_l37 Section 1 point for point: select_tests 19 / 53 and 84 / 88; seeds 53 distinct and deterministic, 0 of 45 shared
with base 20260905, 57 and 95 under the overrides; measured_refusal None for all 19 with both controls live; identities bc0cd7778e382b13 at 726682a and at the
range end, 6a1d73dfb815cfc7 at 9baf3f9; gen_covergroup_set.py 5 / 471 / 12; the pre-flight totals 24 / 6 / 18 with the round's seeds; the classification's
123 / 123; the six-field detach byte-exact outside its two fields; the 39b / 39c rows and the mutant diff's hashes. Its Lows: (1) the rt38 plan file's header
still reads as pending with no rejected-alternative status line (records; not raised by me, agreed); (2) gating rulings cited at untracked work-directory
paths (my P-07 note is now committed as evidence at 755e813; the DV Lead's ruling and worklist follow, per c118720); (3) "class A 758 + 127" not reproducible
from committed inputs, 631 over the thirteen and 282 over the ten (= tb_l37 I-3; corrected by c118720); (4) "nine committed tests use it" should read seven
that assign bins_not_hit (corrected by c118720; my earlier caveat to count assignments, not the token); (5) the form committed unchanged while superseded
(= CR-37 L-4, wider; answered by 4a00702). Its Infos ("110 crosses" are distinct names against 146 declarations; R-5.5 at gen_regress.py:16) are agreed and
the second is corrected by c118720.

Disagreements: none. It raises nothing against tb_l37's Sections 1-5 and misses nothing tb_l37 raised inside its range (CR-37 L-1 and L-2 concerned landing
38, outside its range). Corrigenda to tb_l37: none. Rows after reconciliation: CR-37 L-1..L-4 as recorded, all since answered (L-1 by 40 and 40c, L-2 by 40b, L-3
by 39c, L-4 by 4a00702). tb_l37's CRITIC VERDICT: APPROVE, unchanged.
