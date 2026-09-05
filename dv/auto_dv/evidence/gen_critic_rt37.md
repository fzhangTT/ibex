# Critic verdict: rt37 loader tightening (feature group rt37, one commit 936afaf)

Artifacts at 936afaf (range 3cc3c72..936afaf; parent 3cc3c72; 14 insertions, 1 deletion across three flow files):
- dv/auto_dv/flow/gen_flow_util.py  sha256 75defa6ffe3d1eb5  1846 lines (the loader rule :1501-1506, the self-test case :430-432)
- dv/auto_dv/flow/gen_flow_const.py  d70dcb6252395ddd  600 (FCOV_UNMET_REASON :516 with its two-line intent comment)
- dv/auto_dv/flow/gen_fcov.py  12d1bcef2bc99578  574 (REASON_UNMET = C.FCOV_UNMET_REASON :50)
- census target, unchanged in the range: dv/auto_dv/flow/gen_testlist.yaml 702be271937dcc0d 2434 lines
Date: 2026-09-05T02:45:32Z   Role: Critic
Method: detached worktree of 936afaf in my scratchpad (removed after the logs were retained under
dv/auto_dv/work/critic/rt37/); the eight flow self-tests run there with GEN_DV_SELFTEST_TMP in my scratchpad; the red
proved in both directions by removing the rule from the worktree copy and restoring it; my own negative on the real
standing-guard entry; the loader census through load_testlist. The range's cross-model review was NOT read before
Sections 1-5 (its commit subject was seen in git log; Section 6 reconciles it). Exposure: none. LOG-095: rt37 is a code
group (flow), one verdict; LOG-085/097 placed it in the queue after the round record.

## 1. What changed
The testlist loader refuses an entry with red_fixture true whose red_expect contains the fcov checker's unmet-bin reason
("fcov expectation unmet") while the entry names no fcov_expectation_file (gen_flow_util.py:1501-1506, a die() with the
reason spelled out). The reason literal moves to gen_flow_const.FCOV_UNMET_REASON (:516); gen_fcov.py builds the
reported reason from it (:159 through REASON_UNMET :50) and its own self-test checks the prefix through the same name
(:433). A self-test case "rt37: red_expect naming the fcov unmet reason with no fcov_expectation_file" joins the
refusal list (:430-432), using the standing guard's specific-bin shape, not the canonical prefix alone.
Why it is right: with no manifest, gen_run does not defer the red grading (rt35: red_grading_deferred false), so the
fixture is graded on its sim log, where only the coverage check's line could match; the entry would fail forever for an
undeclared reason. Refusing at load is the collected mechanism (dv_principles.md Section 2), before any run.

## 2. Reproduction (worktree of 936afaf)
- Eight self-tests, rc 0 and "SELF-TEST: PASS" each: gen_flow_util, gen_fcov, gen_run, gen_verdict, gen_regress,
  gen_round, gen_mirror (one case skipped: no mirror_root in the checkout), gen_serve_requests. The commit says seven;
  eight modules carry --self-test and all eight pass (logs rt37/st_<module>.log).
- Red, both directions: with the six rule lines removed from the worktree copy, gen_flow_util --self-test reports
  "SELF-TEST BAD load_testlist refuses rt37: red_expect naming the fcov unmet reason with no fcov_expectation_file" and
  exits 2 (rt37/st_norule.log:29); restored byte-identical (cmp), rc 0 (rt37/st_rule.log).
- My negative on the real entry: a copy of the committed testlist with gen_ut_lockstep_icache_ecc_fcov_red's
  fcov_expectation_file set to null is refused by load_testlist with the rt37 message naming the entry and its
  signature, exit 1; the committed testlist loads.
- Census (load_testlist on the committed testlist at 936afaf): 103 entries; exactly one entry's red_expect carries the
  literal (gen_ut_lockstep_icache_ecc_fcov_red, red_fixture true, manifest
  dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_fcov_red.fcov.yaml); 23 red fixtures, 1 with a manifest. The
  standing guard is the positive control the commit names, and it loads because it has its manifest.
- Single source: git grep at 936afaf finds the literal in code at gen_flow_const.py:516 (the source), gen_fcov.py through
  the constant, gen_flow_util.py:432 (the self-test fixture string, deliberately literal so the test does not read the
  constant it tests), and in two other self-test fixtures: gen_run.py:315 (an evidence_line sample) and
  gen_verdict.py:268-269 (fcov_reason / fcov_sig samples). The remaining hits are records, retained logs and the testlist's
  red_expect (data).

## 3. dv_principles.md conformance (d9c27db18f511411, read fresh)
PASS. Section 2: the refusal is collected at load and derives from the flow's own grading rule, not from a symptom;
Section 4: the die() states the cause and the consequence in one sentence; Section 5: the two new comments state intent
(the "LOG-067" / "LOG-077" tag style already in the file is followed by "rt37:"); Section 6: the TDD evidence is the
executable self-test case, reproduced red and green above; mutation-proof and fcov-expectation do not apply to a loader
rule (removing the rule is the mutation, and the self-test catches it).

## 4. Rows
- L-1 (Low, records). No retained TDD log under dv/auto_dv/evidence/gen_tdd_logs/flow/ and no gen_manifest.md row for the
  rt37 red; the commit carries the three code files only. The evidence exists in executable form (the self-test case)
  and is reproduced here in both directions, so the finding is retention, not proof: retain the two-direction excerpt with
  a manifest row at the next flow touch (rt39's implementation), or the Orchestrator rules the committed self-test case
  sufficient for a loader rule.
- L-2 (Low, single source, dv_principles.md Section 5). gen_run.py:315 and gen_verdict.py:268-269 still embed the reason
  text as fixture strings. They test the graders against a sample, so a future change of FCOV_UNMET_REASON would move
  gen_fcov and the loader together while these two self-tests kept exercising a stale text without failing. Build the
  samples from C.FCOV_UNMET_REASON (gen_flow_util.py:432 may stay literal on purpose: it is the case that proves the rule
  reads the constant).
- Observation. The rule tests substring containment (C.FCOV_UNMET_REASON in rx), so a signature that quotes the literal in
  any position is caught, the generic and the specific-bin form alike; a red_expect that names the literal only to exclude
  it is not a shape any entry uses (census above).

CRITIC VERDICT: APPROVE. The rt37 loader rule at 936afaf refuses exactly the unsatisfiable fixture shape, proves its red in
both directions through the committed self-test, leaves the committed testlist loading at 103 entries with the standing
guard as the positive control, and keeps the reason literal in one source for the two modules that must agree. L-1 and
L-2 are records and single-source rows, not conditions.

## 5. Reconciliation with the cross-model range review (read after Sections 1-4)
dv/auto_dv/reviews/2026-09-04-claude-diff-3e233893-0203c6e5.md at 156dac5 (a341fd9bcd473ef5, APPROVE-WITH-CHANGES) covers
three groups; only its rt37 lines (23, 39, 41) were read, at 2026-09-05T02:46:32Z, by a grep restricted to rt37 terms. Exposure recorded:
its commit subject (the headline rows of all three groups) was seen in git log after Sections 1-4 were written; the
regen-round1 and pass-14-rows rows of the body stay unread until that verdict's Sections 1-5 exist.
- Line 23 (rt37 probes): agrees with Section 2 on every point (self-test rc 0; rule removed gives "SELF-TEST BAD
  load_testlist refuses rt37" and exit 2; 103 entries; generic and specific-bin forms refused on a manifest-less fixture;
  the standing guard loads with its manifest; gen_fcov.REASON_UNMET is C.FCOV_UNMET_REASON; no second copy of the literal
  in flow code outside test fixtures). The reviewer's note that a read-only worktree fails the self-test for environmental
  reasons matches my method: GEN_DV_SELFTEST_TMP pointed at my scratchpad.
- Info :430-432 (the self-test fixture spells the literal; safe because the case expects refusal and would fail loud if
  the constant changed): the same reading as my Section 2 and L-2's last sentence. It sharpens L-2: gen_run.py:315 and
  gen_verdict.py:268-269 do NOT fail loud on a constant change (sample compared against sample), so L-2 stands for those
  two fixtures and not for gen_flow_util.py:432.
- Info (no pre-execution plan artifact for rt37; the trail is the LOG-085/LOG-097 owner queue): recorded by the
  Orchestrator in LOG-097 addendum 2 (c9dec93, "policy trail for regen-round1 and rt37 reviewed after execution");
  closed there.
- Not in the review: L-1 (no retained TDD log or manifest row for the rt37 red). The verdict stands: APPROVE, rows L-1
  and L-2.
