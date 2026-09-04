# Critic verdict: the range 04870ee..1b65f86 (landing 40, the joint manifest re-scope, landing 40b, the reference restore), reviewed as tb_l38

Scope (the Orchestrator's): four commits, 34 files, 1442 insertions, 2273 deletions, nothing under rtl/ or the .f-listed TB sources: 9f47277 (tb-infra-2's
landing 40: the end-of-run two-observer read race closed in gen_ut_intg_store, gen_ut_intg_span and gen_ut_lockstep by requiring the retired and consumed
counts equal on two consecutive samples; a natural red on intg_span; MUT-RETSKEW1), 04a4808 (the DV Lead's and Test Writer's joint re-scope under
LOG-090/LOG-091: 147 plan marks, the verifier gen_unbuilt_mark_check.py, nine test modules with bins_not_hit changes, ten manifests re-rendered, five
removed), 70aa0ce (tb-infra-2's landing 40b: the landing-38 log corrigendum, CR-37 L-2), 1b65f86 (runtime-2's restore of the ten references and the three
measured-false entries). Corrigendum note: tb_l37's Section 6 stays owed; no cross-model artifact for e641b24..d1f6019 exists in the tree at this writing.

Artifacts reviewed (committed blobs at the commit named; sha256 first 16 hex):

- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_store.py @9f47277  d1815de3e9f8a43d
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py @9f47277  27e85bcc7017ceb6
- dv/auto_dv/gen_tb/gen_tests/gen_ut_lockstep.py @9f47277  1a05bff218608799
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l40_pair_sample_quiesce.log @9f47277  17714126444faf28
- dv/auto_dv/docs/gen_fcov_plan.md @04a4808  a827bf159eaf3d03
- dv/auto_dv/tools/gen_unbuilt_mark_check.py @04a4808  35573c4003e44d43
- dv/auto_dv/tests/gen_test_cmp_zcmp_basic.py @04a4808  8d98fee8868c452c
- dv/auto_dv/tests/gen_test_isa_alu.py @04a4808  66db6122a57e7914
- dv/auto_dv/tests/gen_test_isa_cti.py @04a4808  365cc10f68c6b589
- dv/auto_dv/tests/gen_test_mul_div.py @04a4808  4fe6449a99abba5c
- dv/auto_dv/tests/gen_test_cmp_zcb.py @04a4808  22026778097c7952
- dv/auto_dv/tests/gen_test_rst_boot.py @04a4808  eb8ee1d83cdafb15
- dv/auto_dv/fcov_expectations/gen_test_isa_alu.fcov.yaml @04a4808  bf58cd148dc769de
- dv/auto_dv/fcov_expectations/gen_test_cmp_zcmp_basic.fcov.yaml @04a4808  f4a86772923047ee
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l38_intg_store_read_race_corrigendum.log @70aa0ce  5baf1b06636d1808
- dv/auto_dv/flow/gen_testlist.yaml @1b65f86  702be271937dcc0d
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md @1b65f86  e4ed9794b7fd6680
- dv/auto_dv/evidence/gen_tdd_step2b.md @1b65f86  a6c0dc95a9a5cc4e

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411 (trust-triad rule 3 as LOG-090 reads
it: a manifest declares per-run guarantees); LOG-089, LOG-090, LOG-091 and its corrigendum; gen_critic_tb_l37.md (c9f8e05d0bf806bf) rows CR-37 L-1..L-4 and
the P-07 note (c4b359f426fcace3); the mutation-proof standard; the retained-header rule; the pre-flight regression as the measured basis of the re-scope.
Method: detached git worktrees of 04a4808 and 1b65f86 (the gate at both: codegen --check up to date, three UTs PASS, CONST, RED-CHECK PASS, validate 23 OK,
TBMAN 3486 then 3487 rows 0 bad; flow build identity bc0cd7778e382b13 over 117 sources unchanged; my TB-source recipe a2b799c2a12c9c06, moved by landing 40's
Python only). On detached archives of 04a4808 and 1b65f86: every re-rendered manifest regenerated with gen_fcov_manifest.py --test-module --test --write
and compared byte for byte; the five removals reproduced through the tool's own refusals; the bins_not_hit dictionaries read by AST and each bin classified
against the pre-flight's per-seed unmet sets; gen_unbuilt_mark_check.py run as committed, under its --self-test, and under two faults of mine (a mark on a
rendered covergroup's coverpoint; a referenced manifest declaring a bin on an unrendered covergroup); the loader, select_tests, seeds_for_test and
gen_regress.fcov_policy_failures called on the 1b65f86 testlist; landing 40's digests recomputed by my recipe over the committed sources and over the
committed sources with the quoted mutation applied; the three fixed tests' md5s against the blobs. EXPOSURE: the Orchestrator's messages; the authors'
retained logs and the out-tree pre-flight; the re-flight regression (running, not judged here). No subagent used. Section 6 reconciles with the range's
cross-model review (launched 21:15Z) when its artifact is committed; Sections 1-5 were written before reading it.

CRITIC VERDICT: APPROVE. The re-scope does what LOG-090 and LOG-091 require and nothing more: every re-rendered manifest is byte-identical to a fresh render
from the committed modules and plan, its guaranteed set equals the ruling's projection, all 123 class-C exclusions carry a specific stimulus or declaration
cause and all 123 class-B exclusions the per-run reason, the 147 plan marks sit only on unrendered covergroups and the new verifier refuses both ways a mark
or a declaration could go stale; the restore leaves 12 measured entries all checked and the merge-time policy flips none of the round's 53 planned runs, so
the LOG-089 blocker is cleared at 1b65f86; landing 40 closes CR-37 L-1 with a natural red and a mutation, and landing 40b closes CR-37 L-2 with both figures.
Two Lows, none gating.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 9f47277 (tb-infra-2 landing 40) | the pair read in three modules waits for equality on two consecutive samples within QUIESCE_CYCLES = 20, the assertions unchanged; a natural red: 4 of 23 intg_span seeds fail on the committed test (2062654708, 3, 13, 101, retired 30 against consumed 31); the green on the same seeds plus 8 lockstep and 2 intg_store seeds; MUT-RETSKEW1 (gen_bridge_if.sv:61, one extra retired step at count 10) makes the fixed loops FAIL rather than converge; digests: compile-time 18c7a44b8edfefc4, fixed set a2b799c2a12c9c06, mutated root 7ef155c3ddcab7fd; the landing-38 pair 50981c82f49d7574 / 034f4e4f2905cb72 | the three diffs read (settled counter, break at 2, reset on inequality; the 4-cycle settle in lockstep replaced, kept in intg_span for the export flush); the three fixed tests' md5s 6a2ec81d..., 77054230..., 46b80c7a... equal the 9f47277 blobs; my recipe over 04870ee = 18c7a44b8edfefc4 and over 9f47277 = a2b799c2a12c9c06; over 9f47277 with line 61 replaced by the quoted MUT-RETSKEW1 line = 7ef155c3ddcab7fd; 50981c82f49d7574 and 034f4e4f2905cb72 are my tb_l37 figures; manifest row 18732 / fb94acdd23d2809a equals the blob; the log prints its command above every block |
| 04a4808 (DV Lead + Test Writer) | 147 "[covergroup not built, not in manifest]" marks on the coverpoints of unrendered covergroups; ten manifests re-rendered with guaranteed sets bit_ratified 654, isa_alu 563, cmp_zcmp_basic 325, cmp_zca 324, mul_div 196, isa_cti 184, csr_trap_setup 151, cmp_zcb 96, rst_boot 6, csr_access 4; five removed (bit_draft, pmp_csr_warl, pmp_lock, pmp_mseccfg refuse to render; csr_reset renders empty); nine modules changed: six gain bins_not_hit (class B and C), three lose 13 stale entries; the manifest self-test's excluded count 233 | on a detached archive: each of the ten regenerated manifests is BYTE-IDENTICAL to the committed file with exactly those bin counts; the four refusals reproduce ("no manifest bins left for [items]") and csr_reset renders 0 bins with 73 dropped; 147 marks counted, on 0 rendered covergroups (every marked covergroup absent from gen_fcov_groups.svh's 25); the 13 removed keys are 5 + 4 + 4 in csr_reset, csr_trap_setup and pmp_lock by AST diff; gen_fcov_manifest.py --self-test PASS with 233 excluded coverpoints; gate validate 23 OK |
| 04a4808 | the bins_not_hit reasons: class C (unmet at every pre-flight seed) specific per bin, class B (unmet at some seeds) the per-run reason | AST-read dictionaries classified against the pre-flight's every-seed and union sets: class C 6 + 74 + 6 + 16 + 19 + 2 = 123 with 2 / 8 / 1 / 4 / 5 / 2 distinct cause texts per test (cp_alu_operand.rand default never fires and its crosses follow; rlist and spimm subsets per run; the x0-read writer class; compressed branches and jalr rs1 = x0 never emitted; divide-by-zero dividend classes and cp_dit.on never enabled; the fixed non-zero boot address and the bit-8 readback) and none carrying the class-B wording; class B 8 + 73 + 33 + 0 + 9 + 0 = 123, all with the per-run wording; the three other exclusions are the pre-existing ones (isa_alu cp_pc_region.high / low under WP-9, rst_boot's irq-agent bin) |
| 04a4808 | gen_unbuilt_mark_check.py: a mark on a rendered covergroup fails; a referenced manifest declaring a bin on an unrendered covergroup fails; only referenced manifests are judged | --self-test PASS; as committed at 1b65f86: MARK 147 / 25 rendered, DECL 22 referenced manifests judged of 23 present, 0 offenders, PASS rc 0; my fault 1 (a mark on gen_mul_ops_cg cp_op at plan line 540): "MARK FAIL gen_fcov_plan.md:540 CG-MUL-001 cp_op: gen_mul_ops_cg IS rendered", rc 1; my fault 2 (gen_pmc_alias_cg.cp_alias.cycle inserted into gen_test_mul_mul.fcov.yaml): "DECL FAIL ... on unrendered covergroup gen_pmc_alias_cg", rc 1; both restored byte-exact; the unreferenced gen_test_pmc_ctrl manifest (all unbuilt) is the one of 23 not judged, per the DV Lead's ruling |
| 70aa0ce (tb-infra-2 landing 40b) | the landing-38 log's line 34 digest scoped: 50981c82f49d7574 = the df1d8c5 source set and the simv's compile-time figure; 034f4e4f2905cb72 = the 9baf3f9 set | both equal my tb_l37 figures; manifest row 4080 / 1c5d275b982f4092 equals the blob; the retained log stays closed |
| 1b65f86 (runtime-2) | ten references restored, three entries measured false (bit_draft, csr_reset, pmp_csr_warl), everything else unchanged; 22 manifests, 12 measured, 2961 declared bins; policy failures 0 | loader on the archive: 103 entries, 23 red fixtures, 22 manifest-naming, the guard the only red-fixture-plus-manifest entry; non-tests keys and order equal to 04a4808; exactly 13 entries differ (ten in description + fcov_expectation_file, three in description + measured); every reference resolves to a present non-empty file; select_tests full: 19 entries / 53 runs, 12 measured entries / 36 measured runs, all 12 checked, none measured without a manifest; 2961 declared over the 12 measured (3040 over all 22); gen_regress.fcov_policy_failures on the 53 planned runs with every verdict PASS flips 0 with covergroups_exist False and 0 with True |
| gate at 1b65f86 | build identity and TB manifest | bc0cd7778e382b13 over 117 sources (no .f-listed source in the range); TBMAN 3487 rows 0 bad; validate 23 OK |

## 2. Rows

- CR-37 L-1: answered by landing 40 (two consecutive samples, the second of the two fixes offered). CR-37 L-2: answered by landing 40b and by landing 40's
  digest section. CR-37 L-3: answered by landing 39c (previous range). CR-37 L-4 (the form's stale clauses): open, folds into the DV Lead's form corrigendum.
- CR-36 L-1 (the report-phase boundary) and CR-36 L-2 (the discriminating red): open, post-round, as landing 40's log states.
- Rows raised here: CR-38 L-1 (tb-infra-2), CR-38 L-2 (Orchestrator, records).

## 3. Findings

- L-1 (landing 40; MUT-RETSKEW1): the mutation is retained as a quoted line in the log (gen_bridge_if.sv:61 with the one-cycle extra step) and its root
  digest is named, but not as a .diff file with a manifest row, the convention landing 39b adopted for MUT-ALERTSUP after CR-35 L-2. One line, and it
  reproduces the digest 7ef155c3ddcab7fd from the committed sources, so Low; retain the diff with the next records touch.
- L-2 (records; the LOG-091 corrigendum, item (c)): the ruling text says the three measured-false entries go "with their references left null, their test
  modules and committed manifests untouched"; 04a4808 removes five manifests (those three plus pmp_lock and pmp_mseccfg) and edits csr_reset.py and
  pmp_lock.py (stale bins_not_hit entries). The landing's reason is sound and stated in its commit body (the tool refuses to render them or renders empty,
  so a committed manifest would declare nothing), and the round is unaffected (the entries are unmeasured); the ruling text needs one corrigendum line so
  the log and the tree agree.

### Informational

- I-1: the pmc_ctrl manifest is now the one manifest file (of 23) no entry references; the verifier judges referenced manifests only, so it stays
  unjudged by design (the DV Lead's ruling); it declares 204 bins on eight unbuilt covergroups and returns with the covergroup landing.
- I-2: the re-flight regress_r1_fcov_reflight at head 1b65f86 was running at this writing with every completed run PASS; it is the acceptance gate for the
  round HEAD and is judged with the round record, not here.
- I-3: the LOG-091 corrigendum's "class A 758 (631 measured + 127 unmeasured)" counts bins on unbuilt covergroups over all nine LOG-086 entries, including
  the three now measured false; the ten re-scoped tests' share is 282 (176 + 76 + 17 + 13).
- I-4: the manifest self-test's excluded-coverpoint count 233 reproduces; the pre-state 86 was not re-derived.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S3 intent-derived checking / trust-triad rule 3: every measured entry in the round again
carries an enforced per-run claim, and the claims were cut to what the runs guarantee with a written reason per bin rather than deferred (conforming; the
route my P-07 note named as within the rules). S4 honesty: the 123 stable bins are recorded as stimulus and declaration defects with their causes, the
class-B bins as per-run non-guarantees credited from the merge; the removed manifests are explained; one ruling text lags the tree (L-2). S6 trust triad:
landing 40's red is natural and its mutation makes the fixed loops fail (conforming); the mutation diff is owed as a file (L-1); the verifier carries a
self-test and fails under both faults I applied. One-line verdict: PASS, two Lows owed.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range 04870ee..1b65f86. Rows CR-38 L-1 (tb-infra-2) and CR-38 L-2 (records), both Low, none gating. The LOG-089 blocker is
cleared at 1b65f86 by measurement (fcov_policy_failures 0 of 53). Nothing of mine gates the round HEAD or the dispatch; the round record's verdict will
re-derive the re-flight's 36 measured runs against the 12 manifests, the 53 outcomes against the form's expectations as corrected, and the identity against
the canary.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-04870ee1-1b65f864.md, committed 54f1e17, blob dfe9d4b8fe92c112, 44 lines, verdict
APPROVE-WITH-CHANGES, four Lows and one Info. Reviewer identity as its header states: the Claude fallback (claude CLI 2.1.261, run-reported model
claude-fable-5-1 with claude-haiku-4-5-20251001, requested effort high, a fresh session on a detached read-only checkout of 1b65f86; codex unavailable on
the spend cap; owner ruling A-001). Read after Sections 1-5 were written; nothing above was changed on reading it, and one claim above is corrected below.

Agreements: its verified figures are mine (ten manifests byte-identical with the same guaranteed sets; the old-minus-new decomposition into unbuilt bins and
bins_not_hit, 176 / 13 / 17 / 76 and 14 / 147 / 39 / 16 / 28 / 2, matching my unbuilt counts and not_hit lines with isa_alu's two pre-existing WP-9
exclusions; 123 class C; 147 pure mark insertions; 233 excluded coverpoints; the five removals; the 13 stale entries as 5 + 4 + 4; the verifier PASS with
22 of 23 judged and its self-test PASS; the loader 103 / 22 / 12 with the guard the only red-fixture-plus-manifest entry; 2961 declared bins; zero
policy violators over 53 runs; landing 40's digests and the natural red). Its statement that the ten restored blocks are byte-identical to their
pre-LOG-086 blobs: re-derived, the ten entries' dictionaries at 1b65f86 equal those at 8b22572. Its Info (which instrument removed the 282 unbuilt bins of
the four surviving LOG-086 entries: the marks, while the LOG-091 corrigendum called the marks unnecessary) is the same records point as my L-2 and I-3;
adopted: the round record should say which instrument did the removal.

Adopted and verified, misses of mine:

- Its Low-1 (the quiesce loop's exhaustion path), adopted as CR-38 L-3 (tb-infra-2, all three modules): after twenty iterations without two consecutive
  equal samples the loop ends, and lines 59-60 (lockstep) / 74-75 (intg_span, intg_store) take a FRESH read of the two counters for the assertion, so a
  twenty-first sample that happens to read equal passes on a single instant, the shape landing 38 and 40 set out to remove. The break path is sound; the
  exhaustion path is not the "never decides" the comment claims. Fix: fail explicitly when settled < 2 after the loop, or assert on the last sampled pair.
  I read the loop and accepted the comment's claim without reading what follows the loop.
- Its Low-2 (gen_test_rst_boot.py:155), adopted as CR-38 L-4 (Test Writer): the class-C reason for gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero,
  "stimulus: the readback never returns zero for this field in any run of this entry", restates the pre-flight observation and names no cause, unlike its
  sibling cp_boot_addr.zero (the TB drives a fixed non-zero boot address). My classification tested the reasons for class-B wording and for distinctness,
  not for whether each names a cause. CORRIGENDUM to Section 1 and the verdict paragraph: 122 of the 123 class-C exclusions carry a specific cause; this
  one carries the observation, and needs the cause (why bit 8 of the cpuctrlsts read-back cannot read zero in this program) or the drivability ruling the
  pre-flight classification asked for.
- Its Low-3 (gen_unbuilt_mark_check.py:6 and the 04a4808 message: "the coverpoints of an unbuilt covergroup carry the mark"), adopted as CR-38 L-5 (DV
  Lead): re-derived with the verifier's own heading and line regexes over the committed plan, the coverpoint and cross lines under unrendered
  covergroups number 1944, of which 147 are marked and 1797 are not, and 1729 of the unmarked ones have a (CG id, coverpoint) row in gen_trace_tp_bin.csv
  (the artifact reads 147 of 1911 and 1728; the difference is line-filter width, the conclusion is the same); CG-CSR-016 carries six marked lines beside
  three unmarked (cp_hart, cr_dbg_reset, cr_hart_rd). So the marks cover the coverpoints the referenced manifests would otherwise declare, not the unbuilt
  set, and the MARK leg cannot detect a missing mark: protection for a newly referenced manifest rests on the DECL leg, which the ruling accepts. The
  docstring and the message should say so, or a completeness leg should be added.
- Its Low-4 (verbatim repeated comment blocks across the six test modules and the three quiesce loops): agreed as fact; the l40 log states the repetition
  is deliberate; informational here, the ai-slop rubric's call, no row.

Corrigenda to Sections 1-5: one, stated above (the class-C count with a cause is 122 of 123). Rows after reconciliation: CR-38 L-1, L-2, L-3, L-4, L-5, all
Low, none gating. CRITIC VERDICT: APPROVE, unchanged.
