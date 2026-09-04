# Critic verdict: DV Lead plan set v4s at 390f40f (the CR-30b lift, the inputs-digest headers, the CM209 answers), reviewed as tb_l30c, the recorded re-review of tb_l30b's REQUEST-CHANGES

Scope (the Orchestrator's): the one commit 390f40f (nine files: the generated-record headers carrying an inputs digest over every part file instead of a
wall-clock stamp at all three sites, the CR-30b-M-1 clause fix with the pair added to gen_record_check.py, the CR-30b-L-1 argument moved onto the retained
with_nmi runs, CM209-Low-1 stated in the drain sentence, CM209-Info-2's three declared pairs, the gitignored-generator statement, the four generated records
re-keyed to v4s-on-e988ee6), judged by id against CR-30b M-1 and L-1 and against CM209 Low-1 and Info-2. It sits in the range fd76548..390f40f with rt35 and
landing 33, which tb_l32 judges; the CR-30 gate rests on this verdict.

Artifacts reviewed (committed blobs at 390f40f; sha256 first 16 hex):

- dv/auto_dv/docs/gen_fcov_plan.md  f3eb5b5f7c9fa35b
- dv/auto_dv/docs/gen_feature_list.md  2bd7b33ba65ff7b5
- dv/auto_dv/docs/gen_test_plan.md  7294ee9071da271c
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  f637545b0e5a5918
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  5d27e1b645626aa7
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  036021c0c3b6c1dc
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  e1a397fcebe93d10
- dv/auto_dv/evidence/gen_round0_promotion_table.md  0fe27d1ff55a6e25
- dv/auto_dv/tools/gen_record_check.py  4f59e8c3cfe2ff02

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l30b.md (1533f3725d179933, rows
CR-30b) and the CM209 artifact (a98196fd4ee0f76a); the rule that a correction removes or reconciles the clause it corrects; the evidence rule.
Method: detached git worktree of 390f40f (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 27 OK, TBMAN 3472 rows 0
bad; build identity e674e6339b5bea85 unchanged, no build source touched). The four generated records regenerated on a full archive copy with --plan-sha
v4s-on-e988ee6 and the credit record's byte-for-byte line: all six files byte-identical, the set CSV untouched since v4q, one label across the five files.
The reword checked on whitespace-flattened text per phrase with 2410402 as the control (the old clause present once there, absent here; the new clauses
absent there, present once here). gen_record_check.py read and run at 390f40f: three declared pairs, the tree run reporting exactly one phrase present for
each (B, A, A), --self-test seven of seven, -h 0. The three record headers read for the digest (86adeb302725 at all three, no UTC stamp left, checked
case-insensitively); the promotion header's test-plan sha against the blob (7294ee9071da). The response file's content rows checked for duplicates
(no content row of the response file is duplicated; the four repeated lines are table header rows of separate sections). EXPOSURE: the Orchestrator's message only. No subagent used. Section 6 reconciles with the range's
cross-model review of fd76548..390f40f, whose artifact was the wrapper's empty placeholder while Sections 1-5 were written.

CRITIC VERDICT: APPROVE. Both CR-30b rows are lifted as stated and verified: the surviving clause now says the Section 1.8 rows WILL point at the entry once
it exists and today name the owed evidence, the clause it corrects is gone, and the tool declares the pair; the precondition argument rests on the 23
retained with_nmi logs (12 taken NMI entries, no pre-emption) and the unretained sweep argues nothing. CM209-Low-1 is stated in the drain sentence as the
code's, one record short, moving with tb-infra-2's resize; CM209-Info-2 has three declared pairs with none violated on this tree. The headers now carry an
inputs digest instead of a clock, so a regeneration from unchanged parts is byte-identical, which the records' own byte-identity on my copy shows for the
four tool-generated records; the plan records' generator stays gitignored and the record says so. No rows. The CR-30 gate lifts.

## 1. What was verified

| row | as built | evidence (re-derived by me) |
|---|---|---|
| CR-30b M-1 | gen_test_plan.md's clause now reads "the counted-only rows below WILL point at the entry carrying it once that entry exists, rather than at a new directed test; today they name the owed evidence, as the clause above says"; gen_record_check.py declares the pair (old clause against "nothing in those rows points at one") | the old clause 0 on flattened text (1 at 2410402), the new clause 1, "nothing in those rows points at one" still 1; the tool's tree run: pair 2 "exactly one of the pair present (B)"; the response row |
| CR-30b L-1 | the sweep "argues nothing either way" and the argument rests on the 23 retained logs (12 taken NMI entries, no pre-emption), "too rarely to rely on rather than never" | the phrases present once; the 23 / 12 figures are mine from tb_l30 and tb_l30b (23 with_nmi .log files, 10 distinct summaries, 3054 entries, 12 NMI entries at 2410402, unchanged at 390f40f since no log landed between); the sweep's "entries=170 nmi=0" remains as context only, which my row allowed |
| CM209-Low-1 | the drain sentence names the cap as the code stands and states that it is one record short of the drain it bounds, the clause and its 193 moving with tb-infra-2's resize | the phrase present once; landing 33's measurement (193 against 202, the source edit owed) as verified in tb_l32 |
| CM209-Info-2 | three declared pairs: the CM205 promotion pair, the CR-30b rows pair, and "so that case stays OWED" against "so that case is CLOSED by the cap rule" | the table read; the tree run reports B, A, A with 0 problems; --self-test 7 of 7; the OWED phrase present once and the CLOSED phrase 0 |
| the inputs-digest headers | gen_fcov_plan.md, gen_feature_list.md and gen_test_plan.md carry "inputs digest 86adeb302725 over every part file" and no clock; the digest moved on a one-byte part change and returned on restore; the generator's root overridable | the three headers carry the same digest and no "generated ... UTC" stamp remains (case-insensitive); the move-and-return property and the twice-generation are the generator's, which is gitignored: the row says so (Section 3 I-1) |
| the records | re-keyed to v4s-on-e988ee6: set md (digest 2f2b1a92c6bc), promotion table (test plan 7294ee9071da), credit md and summary; CSV unchanged | six files byte-identical on regeneration; the CSV absent from the commit; the test plan blob begins 7294ee9071da |
| the gitignored-generator statement | the three plan records cannot be regenerated from the repository alone; each now self-describes its parts by digest; the relocation left as a plan-level item | the row read; consistent with what every plan-set verdict has recorded since v4 |

## 2. Rows

- CR-30b M-1: CLOSED. CR-30b L-1: CLOSED. CM209-Low-1 (the DV Lead's half): stated, moving with the resize. CM209-Info-2: answered. The CR-30 gate lifts.

## 3. Findings

None.

### Informational

- I-1: the two generation properties the header row claims (byte-identical regeneration from unchanged parts; the digest moving on a one-byte part change and
  returning) are measured on the DV Lead's gitignored generator and parts and cannot be re-run from the repository; the record says so in the same touch.
  The digest itself (86adeb302725 at all three sites) is the checkable residue, and the four tool-generated records regenerate byte-identically on my copy.
- I-2: the response file's "duplicated inserted row caught and fixed": no content row of the response file is duplicated; the four repeated lines are table header rows of separate sections.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the record now agrees with itself on the Section 1.8 rows, states the sweep as
arguing nothing, names the cap clause as the code's and one record short, and says which of its properties rest on gitignored tooling (conforming). S6: not
exercised (records and one tool with its self-test). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE on v4s (390f40f) as the re-review of tb_l30b's REQUEST-CHANGES; CR-30b M-1 and L-1 are closed and the CR-30 gate lifts. Rows
CR-30c: none.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-fd765489-390f40f1.md (47ac33f727903e7d, 59 lines), read after Sections 1-5 of this file and of its
companion were written (it was the wrapper's empty placeholder while they were; one artifact covers the range, so tb_l32 and tb_l30c reconcile against
it). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of 390f40f. Its verdict:
APPROVE-WITH-CHANGES with five Lows and two Infos; the rubrics PASS except one minor item each under ai-slop-comments and magic-numbers. Mine on v4s: APPROVE. The verdicts agree; the artifact's one row on v4s is a record inconsistency I missed.

Shared recomputations, each re-run by me and equal to the artifact's: no "generated 2026" stamp left in docs or evidence (case-insensitive); the digest
86adeb302725 in all three headers; the gitignored-generator statement once; gen_record_check.py's three pairs with 0 problems, --self-test 7 of 7, and
the negative cases on an archive copy (phrase B removed: VACUOUS rc 1; phrase A appended: CONTRADICTION rc 1; pair 3's B appended: CONTRADICTION rc 1;
restored: rc 0); the old clause gone from gen_test_plan.md; 23 with_nmi logs, 19 summaries of 10 distinct with multiplicities 6, 4, 2 and seven singles,
3054 entries and 12 NMI entries, every nmi_preempted 0; the four records and the CSV byte-identical from the byte-for-byte invocations; 7294ee9071da and
d9526147a258 in the promotion header; the label v4s-on-e988ee6 at every site; nine files changed, the CSV unchanged since v4q.

The artifact's findings against mine:

- Its Low (gen_critic_response_plan_set_v1.md:845): the CR-30b-M-1 row says "two declared pairs with no problem on this tree" while the tool declares
  three and the CM209-Info-2 row at :848 says "Three declared pairs, no problem on this tree". A miss of tb_l30c, adopted and verified (both lines read
  at 390f40f). I checked the tool's count and the Info-2 row against it and read the M-1 row for its clause fix, not for its count; a response row that
  quotes a count is itself a site, the rule I have written down since tb_l29. The fix is one word; it rides the DV Lead's next touch through the CM210
  row, no CR-30c row added.
- Its Info (gen_test_plan.md:190, "12 taken NMI entries between them" sums the duplicated summaries; over the 10 distinct summaries the figure is 4 NMI
  entries over 1654 interrupt entries): adopted and verified (my sum over the distinct texts gives 1654 and 4). The sentence is consistent with the
  duplication the paragraph discloses two lines earlier, and the distinct-run figure is the sharper support for "too rarely to rely on"; worth quoting
  in the same touch.
- Its other rows (the rt35 identity block, the reader's reset set, the age-17 figures, the default entry list, a comment) are Runtime's and tb-infra's
  and are reconciled in tb_l32's Section 6.

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. One miss adopted (the two-versus-three count), owed through the CM210 row.
Section 5 stands: APPROVE on v4s, CR-30b M-1 and L-1 closed, the CR-30 gate lifts.
