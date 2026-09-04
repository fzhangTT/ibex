# Critic verdict: the range 1bbf0a0..813994b as one (Runtime's merge 28c8c0b, Runtime's rt32 a9af624, the DV Lead's v4o 22fb64d, tb-infra's landing 26 813994b), reviewed as tb_l26

Scope (the Orchestrator's): four working commits in the range, judged together: the landing-25 testlist merge (the ninth WP-8 entry from tb-infra's staged block
3222b54ee8ec with all eighteen reference keys, nine WP-8 entries bound, 102 entries, 27 naming a manifest); rt32 (the loader's third equality in a named helper
with a function-level red and a real-manifest control, labelled defense in depth; the CM202-Minor-1 row); v4o (the CM201 rows and TI-25-1, the split note re-based
over landing 25 and the merge, the set tool's count clause, the rank 27 to 29 correction, records at label v4o-on-28c8c0b, 58 / 4106 / 27); landing 26 (CR-25 L-1
and L-2 and the CM202 rows; gen_build_identity.py; base identity plus each root's own digest in the mutation logs; the GREEN root block; the nine "own run"
definitions with both probe figures; Section 7 naming 28c8c0b). The two review artifacts (40bd5ef, 59dadee) and my two files (6fe883c, 55ab5ee) in the range are
committed-as-written and not judged. Also answered: tb-infra's question whether P6 bars the four probe-carrying WP-8 entries from the exercising run.

Artifacts reviewed (committed blobs at 813994b; sha256 first 16 hex):

- dv/auto_dv/flow/gen_testlist.yaml  d9526147a2581ae8
- dv/auto_dv/flow/gen_flow_util.py  5b65f7f8a0d87d10
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_cm202_manifest_test_field_red.log  05f22cd4288885ea
- dv/auto_dv/evidence/gen_critic_response_flow.md  565b0916155bc79b
- dv/auto_dv/tools/gen_covergroup_set.py  c4a672c371ddfe72
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  9a1ea5d55c4b044b
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  d6568696972a39c7
- dv/auto_dv/docs/gen_fcov_plan.md  fc8f6fde591fec30
- dv/auto_dv/tools/gen_build_identity.py  d640f7336b3706b6
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l24_wp8_ut_muts.log  5fb6c8ebf9b992e0
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_wp8_cov_reds.log  8ec2c3ca4779733b
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  2b2bc97de8cc0c5d
- dv/auto_dv/docs/gen_wp8_part1_plan.md  8b7d559520a5e5f7
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc.fcov.yaml  0200c12e6091fcbf
- the other eight per-entry manifests dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_*.fcov.yaml (parsed together with the one above)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l25.md
(9b11b2687a338d8e) and its supplement (81740224f1c3c974); the CM202 artifact (bdae925ee245a98a); LOG-067, LOG-077, LOG-079 and the F1 ruling for P6;
gen_run.measured_refusal (dv/auto_dv/flow/gen_run.py:203-205) and its self-test cases 251 and 255.
Method: detached git worktree of 813994b and copies. Landing 26's files list (b21c0dc49977, 15 rows) equals its commit's diff; 14 of its 15 md5s verify
against the committed tree and the fifteenth (gen_wp8_part1_plan.md) does not, because the on-disk hashes list is a newer one (629aec32a86d) than the
committed r3 (df15010d076a): tb-infra has edited the plan in the shared tree after the commit for its next touch, which the hand-off rule permits once the
commit is confirmed; the committed content is what I judged. The merge's and v4o's file hashes are in TASKS.md rows 1114 and 1127. Gates on the worktree, all
PASS: both codegen checks and unit tests, CONST-CHECK, RED-CHECK, the manifest schema sweep 27 OK 0 FAIL, the flow self-test 155 ok (rt32's four cases
inside), gen_run 28 ok, the loader dump of 102 entries, gen_covergroup_set 58 covergroups 4106 bins 27 manifests 0 extra. Both identities recomputed with
the tools' own functions: filelist_digest b48479a3bc6f1d9f over 117 sources and the TB recipe f80e2c719e16b73c, unchanged across the range (no TB source
moved), and gen_build_identity.py prints the same; its controls exercised by me: --expect the right value rc 0, --expect 0000000000000000 MISMATCH rc 1, a
wrong flag rc 2, a missing root rc 2. The merge parsed at 1bbf0a0 and 28c8c0b: 101 to 102 entries, the non-tests keys equal, exactly eight entries changed
and only in fcov_expectation_file, each to its own manifest, the ninth entry with 18 keys parsed-equal to the staged block whose sha256 first 12 is
3222b54ee8ec (read from the shared work directory), 27 entries naming a manifest; the promo key d9526147a258 equals the testlist's sha256 at 28c8c0b.
rt32's helper, its four self-test cases and the loader call read; its red log read whole. v4o's set-tool change read; its ranks read in the regenerated
set (gen_isa_lui_auipc_cg at 29, gen_ic_ecc_cg at 35); the TI-25-1 citation :499-500 present in the fcov plan. Landing 26's two logs read whole and their
manifest rows recomputed (9608 / f479483800a372c3, 6405 / 178afb5735ec8a1c); the six mutated roots' own digests equal the values I recomputed in tb_l25
(6ce5351e5daef0bc, 4952cd34d2c337f6, 34e7dd5af004e920, 3944a159f6f6e5e3, 0cef864e4ded9a27, 079a2867330a422e); the GREEN root block read; the nine manifest
headers counted (9 of 9 carry the own-run definition, 1 of 9 the probe re-measure note, the reference manifest whose run had the knob; 9 of 9 the group-wide
sentence; the of-those clause in the 5 whose exclusions intersect the owed pair, the per-entry-only clause in the 2 far entries). No subagent used.
EXPOSURE: none beyond the Orchestrator's message and the git log subjects. Section 6 reconciles with this range's cross-model review; at the time Sections
1-5 were written its artifact was the wrapper's empty placeholder, and per the Orchestrator's instruction this verdict waits for it rather than
reconciling by supplement.

CRITIC VERDICT: APPROVE. Every row the range answers is answered with evidence that reproduces from the committed tree; the merge is the staged block and
the eight bindings and nothing else; the third equality is a real refusal with its red and control; the DV Lead's records are re-keyed to what HEAD holds;
the identity record now carries the base and each root's own digest with the baseline line in a GREEN block. One low on the new tool's proof.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 28c8c0b (Runtime) | the ninth entry gen_ut_lockstep_icache_ecc_tag_disabled appended with 18 keys (measured false, cocotb_module, component, expected_fail, keep_artifacts among them); the eight entries repointed at their own manifests; nothing else changed | parsed-equal to the staged block 3222b54ee8ec; 8 entries changed in one field each; non-tests keys equal; 27 naming a manifest; the loader reads 102 |
| a9af624 (Runtime rt32) | manifest_test_mismatch(path, entry): the manifest's own test field against the entry name, called from load_testlist after the stem rule; four self-test cases (own name passes; another test, no test key, not a mapping refused); the red log: section 1 the stub helper failing three cases, section 2 green, section 3 a control on a real committed manifest, section 4 the committed testlist loading with the rule; the CM202-Minor-1 row | the diff; the log read whole; the flow self-test 155 ok; the row's account of the null bindings (deliberate between 514bb74 and 28c8c0b) consistent with the history |
| 22fb64d (DV Lead v4o) | the set tool's count clause over in-home entries only; records re-keyed to testlist d9526147a258 at label v4o-on-28c8c0b, 58 covergroups, 4106 bins, 27 manifest files; the rank correction (gen_isa_lui_auipc_cg at 29, CG-IC-006 entering at 35); CM201 L-1..L-4 and I-1 rows; TI-25-1 (:499-500) in the bin text and the row; the split note re-based (nine manifests at 1bbf0a0, nine entries bound at 28c8c0b) | the tool run on the worktree gives 58 / 4106 / 27 / 0; the promo key equals the testlist's sha; the ranks in the regenerated set; the :499-500 citation present |
| 813994b (tb-infra landing 26) | the CR-24-L-1 row corrected to fc376b9db3ad3868 with the old figure named; gen_build_identity.py (--expect, --root, exit codes 0 / 1 / 2, the flow module loaded against the given tree); the mutation logs' per-root lines: base identity b48479a3bc6f1d9f plus the root's own digest for the six mutated roots, the GREEN roots keeping "gate identity"; the ut_muts GREEN root block with the run's own "self-test: 148 cases, 0 failures" from L25b/ut_isa_cov_zc; the cov_reds header naming the deleted group manifest by path and declining the all-hit claim; the nine headers defining "this entry's own run" as the local runner and recording the reference manifest's probe-on and probe-off re-measure (all fifteen counts identical); the per-manifest owed wording computed from each file's exclusions; Section 7 "DECLARED AND BOUND, NOT YET EXERCISED" naming 28c8c0b; two own findings (the staged block reached its consumer by disk; one measurement carried a probe knob its entry lacks) | the six own digests equal my tb_l25 recomputation; the tool's controls reproduced; the header counts 9 / 1 / 9 / 5 / 2; the two logs' manifest rows recompute; the response rows read against the diffs |
| the P6 question | gen_run.measured_refusal refuses a debug-only knob only when `measured` is true (line 204); the exercising runs of the four probe-carrying entries are unmeasured (measured false on all nine), so P6 does not apply to them, coverage on or off; the self-test cases 251 ("the same knob unmeasured runs") and 255 pin it | the code and the self-test read; agrees with the Orchestrator's reading and Runtime's confirmation |

## 2. Rows

- CR-25-L-1 CLOSED (base identity plus the root's own digest, re-derived by tb-infra and equal to mine). CR-25-L-2 CLOSED (the GREEN root block; the
  cov_reds silence explained, since the covergroup self-test runs in the isa-cov test and not in lockstep runs, which is the honest form).
- CM202 Minor-1, Low-1..5, Info-1: answered as stated. CM201 L-1..L-4, I-1 and TI-25-1: answered as stated by the DV Lead. rt32's item and the
  CM202-Minor-1 row: answered.

## 3. Findings

### L-1 (low) [S6 retention] gen_build_identity.py's four-way proof is not retained and the tool has no self-test

The CM202-Low-2 row says the tool was "self-tested four ways before handing" (the digest at rc 0, --expect equal rc 0, --expect 0000000000000000 MISMATCH
rc 1, a wrong argument rc 2, plus --root on the archive). No retained log carries those runs and the tool has no --self-test, so the proof lives in a
response row; I reproduced all four controls, so the claim is true, and this is the retention form of the other tools (a red log or a self-test that pins
the negative control). Add a short retained control log or a --self-test that fabricates a mismatch.

### Informational

- I-1: the on-disk landing-26 hashes list (629aec32a86d) is newer than the committed r3 (df15010d076a) and its gen_wp8_part1_plan.md md5 no longer matches
  the committed blob: tb-infra's next touch is in flight in the shared tree. Permitted after the commit's confirmation; the committed content is judged here.
- I-2: the fcov leg is declared and bound and not yet exercised, as Section 7 now says; the first flow run of a WP-8 entry will be the first enforcement of a
  declared bin, and its verdict should be read with the per-entry counts in the manifest notes.
- I-3: the reference manifest's probe-on measurement is disclosed with its re-measure (identical counts), and the block-by-disk finding is recorded with the
  rule taken from it; both are tb-infra's own findings, recorded in the record that reviewers read, which is the pattern earlier corrigenda asked for.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 retention and identity: base and own digests per root, the baseline line in a root
block, the merge tied to its staged block, the third equality with red and control (conforming; L-1 on the new tool's proof). S4 honesty: the deleted
fixture named rather than re-claimed, the probe-knob divergence disclosed, the fcov leg labelled not yet exercised (conforming). S2: the loader's third
equality follows the flow's real check order, as rt32's log says. One-line verdict: PASS with L-1.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range 1bbf0a0..813994b. Low L-1 with tb-infra's next touch. Rows CR-26.

## 6. Reconciliation with the cross-model review of this range

Read after Sections 1-5 were written, as the Orchestrator instructed: dv/auto_dv/reviews/2026-09-04-claude-diff-1bbf0a09-813994b3.md (sha256 d923ddbbffb7fae2, 38 lines, committed aa8b663; a fresh claude session at
813994b), APPROVE-WITH-CHANGES: one Medium, four Lows, one Info. Verdicts agree: both approve the range, and every figure both of us recomputed is equal
(the merge shape and the 18 keys, the testlist sha d9526147a258, rt32's red and its real-manifest control, the set at 58 / 4106 / 27 / 0 with CG-IC-006 at
35, the RTL spans, the identity tool's digest and controls, the mutated roots' own digests, the manifest union of 13). The reviewer went two steps further
than tb_l26 on rt32 (a loader-level refusal in a temp copy with a drifted manifest) and on v4o (byte-identical regeneration of the records at 22fb64d).

Its rows, each verified by me on the tree or in history:

- Medium (the DV Lead's CR-1v12-L-7 CORRECTED clause, "at 29 in every committed version I checked, so the figure was wrong when written rather than
  overtaken"): the committed set CSV reads rank 27 for gen_isa_lui_auipc_cg at b57b08c, a1fd231, 9fdef64 and 252ec36, and 29 from cf7c275 on, so the row's
  provenance claim is false and the reviewer's wording ("correct when written at a1fd231, overtaken when cf7c275 re-ranked the set") is the true one.
  tb_l26 read v4o's rows for their checkable figures and did not check this history claim; missed, adopted for the DV Lead.
- Low (two tb-infra rows cite gen_fu_l23_wp8_cov_reds.log:33 for the baseline line, which landing 26's 13 header lines moved to :46): verified (2
  occurrences; the line is :46 at HEAD). Missed by tb_l26 (I checked the log, not the rows' line numbers). Adopted.
- Low (the CM202-Low-3 and Low-4 rows record the two logs' manifest rows as 5416 / e26f9d63 and 8939 / 9fde2083 while the committed rows and files read
  6405 / 178afb5735ec8a1c and 9608 / f479483800a372c3): verified. tb_l26 recomputed the committed rows and did not re-read the rows' quoted figures, the very
  class my tb_l25 supplement wrote down; missed again, adopted.
- Low (the set's inputs digest a244f08448d7 exact at 22fb64d but stale at HEAD after landing 26's comment-only header rewrite of the nine manifests): the
  committed record at 813994b reads a244f08448d7, and regenerating on a copy of 813994b gives 3b83f8d563b5 with the CSV and ranking unchanged, as the
  reviewer says. Missed by tb_l26; adopted (regenerate the four records or state that only the digest moved).
- Low (gen_build_identity.py's docstring names CM200-Major-1 and narrates the recurrence, against the intent-only comment rule): verified at line 6. tb_l26
  L-1 asked for the tool's proof and self-test and did not flag the comment; the two rows complement each other; the tool's owner is now Runtime.
- Info (the CR-23-L-1 row's "I will hand eight PER-ENTRY manifests" survivor): verified, 1 occurrence on flattened text against 2 "nine per-entry"; a dated
  record of the moment, one clause owed. Adopted.

No corrigendum to Sections 1-5: nothing tb_l26 states is false; it under-found on six record sites, four of them the response-row-figure class I had
already named for myself after tb_l25. The verdict on the range stands as APPROVE; the reviewer's rows are record-accuracy items for the DV Lead
(the Medium), tb-infra and Runtime, and the next range carries them.
