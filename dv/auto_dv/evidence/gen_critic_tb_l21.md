# Critic verdict: tb-infra landing 21, the call-forms log rebuilt (commit 3720962, diff base b88b270), reviewed as tb_l21

CORRIGENDUM to gen_critic_tb_l20.md (195fa70e180c9c66, committed a005700, frozen): its L-1 says the call-forms log's "first line of output" column
was wrong for THREE of six rows. It was wrong for FIVE of six: the two exit-0 rows recorded the tool's second and last line ("indices [26, 27], 322 of
1564 tag-write lines kept") while its first line is the retained-file line with the size and md5. My own run had printed that first line and I compared
only the three refusal rows against the column; the landing-20 cross-model review (CM189-L-1) and tb-infra's own re-run both counted five. The finding
stands and is sharper; only tb_l20's count is corrected. Rule for me since: when a column is wrong for the rows a pattern first shows, check every row of
the column before stating a count.

Scope (the Orchestrator's): the two files of landing 21, gen_fu_l20_tagwrite_arg_forms.log rebuilt as one block per call form read from redirected
output with the fixed-width truncation removed, and its refreshed manifest row; answering CR-20-L-1 and CM189-L-1. The tool itself is unchanged in this
landing. This verdict also carries the reconciliation owed by tb_l20 with the cross-model review of 2f9fd13..6457c71 (Section 6).

Artifacts reviewed (committed blobs at 3720962; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l20_tagwrite_arg_forms.log  e740b3ef1759ae49
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  0401ef3f6d68b367

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: gen_critic_tb_l20.md (195fa70e180c9c66);
dv/auto_dv/reviews/2026-09-04-claude-diff-2f9fd13c-6457c715.md (c7f44cbe8df1431d, CM189-L-1); the team's excerpt rule (recorded output = the producing
command's redirected output).
Method: detached git worktree of 3720962 and a copy of it. The landing-21 list equals the two-file diff and both md5s verify at 3720962; the manifest
holds 3460 rows and the log's row recomputes (4067 bytes, md5 2f6cb07f3b38dcea10bd00205dab25c6); gen_trace_tagwrite_history.py is byte-identical to
6457c71's. Re-derived by me: the log's six blocks parsed (form, exit, lines); each of the five forms runnable from the tree run on the copy with stdout
and stderr redirected to a file, and compared block by block: exit codes and every line MATCH for (none), <landing root>, <landing root>
--from-artifact, <landing root> <scratch root> --from-artifact and <landing root> --from-artifact <scratch root>; the artifact's md5 is
a7702922e3b65efc56b340e6ee2b1348 before and after the --from-artifact run and the manifest unchanged; the self-check reproduction repeated (one
appended tag-write line with index 30) gives the log's one-line refusal exactly, exit 1. The <landing root> <scratch root> block (a real trace session)
is not reproducible from the tree and rests on the log alone; an absent scratch root refuses naming the flag. No subagent used. EXPOSURE: none beyond
the Orchestrator's sha-and-scope message, tb-infra's direct message of 10:21Z announcing this landing (which named the five-of-six count and the
provenance; I read no file of tb-infra's before the commit) and the git log subjects. The cross-model review of this range had not launched at hand-off
(Section 7).

CRITIC VERDICT: APPROVE. The log now holds each form's whole output, read from redirected files, and every runnable block reproduces line for line;
CR-20-L-1 is closed with the count corrected above. No new findings.

## 1. What was verified

| item | as built at 3720962 | evidence (re-derived by me) |
|---|---|---|
| the rebuilt log | one block per form (form, exit, every output line), six forms; a header naming the archive (a detached archive of b88b270 with the kept TRACE17 session as the scratch root), the two refusal shapes and the correction made (five of six rows, the truncation); a footer with the byte-identity before and after both accepted runs and the self-check reproduction from a pristine control | five blocks reproduced line for line with redirected output; the refusal line reproduced exactly; md5 unchanged across the --from-artifact run |
| CR-20-L-1 / CM189-L-1 | the "first line of output" column is gone; each block carries the whole output untruncated | the blocks; no fixed-width cut (the retained-file line runs to its end with the md5) |
| the correction's own account | the header states the defect as wider than CR-20-L-1 (five of six, the truncation) and what was right before (exit codes, the accept-or-refuse split) | matches the corrigendum above and CM189-L-1 |
| the manifest | the log's row refreshed; 3460 rows | recomputed |
| the tool | unchanged | `git diff --quiet 6457c71 3720962` on the tool |

## 2. Closure

CR-20 L-1 CLOSED (count corrected to five of six). CM189-L-1 answered. Still owed by tb-infra's next touch, outside this landing's two files: CM189-L-2
(the history-narrating sentence in the tool's comment at line 23) and CM189-I-1 (the CM185-I-1 wording's breadth).

## 3. Findings

None.

### Informational

- I-1: the `<landing root> <scratch root>` block is the only record of the real-scratch form; not reproducible from the tree, as the log's header says.
- I-2: the log's header sentence "A third argument was previously accepted and then ignored" is record prose in a retained log, where history belongs;
  the same sentence in the tool's code comment is CM189-L-2 and remains owed.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the log states the defect it corrects as wider than the row that found it
and keeps what was right (conforming). S6 retention: every block from redirected output, the archive and scratch root named, the byte-identity re-verified
rather than carried forward (conforming). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE. Rows CR-21: none.

## 6. Reconciliation owed by tb_l20 (frozen): the cross-model review of 2f9fd13..6457c71

Read after tb_l20 was frozen: dv/auto_dv/reviews/2026-09-04-claude-diff-2f9fd13c-6457c715.md (sha256 c7f44cbe8df1431d, 46 lines, committed dfb8086),
APPROVE-WITH-CHANGES, rows CM189 attributed by file owner (part A Runtime's rt23, part B tb-infra's landing 20). Its part-B verification agrees with
tb_l20 (the six call forms, the byte-identical regeneration, the refusal wording singular and plural, the record sentences); verdicts agree.

- Its Low 1 (the log column wrong for five of six rows) is the corrigendum above: tb_l20 L-1 under-counted at three. Answered by this landing.
- Its Low 2 (the tool's comment at line 23 narrates history) tb_l20 read and did not flag; adopted, and owed by tb-infra's next touch (the tool is not in
  this landing).
- Its Info on fu2a:297 (an altered index field is caught; other alterations pass) adopted as informational, owed with the same touch.
- Part A (Runtime's rt23 rows) and its second Info are Runtime's.

## 7. The cross-model review of this range

Not read: at hand-off no artifact for b88b270..3720962 existed under dv/auto_dv/reviews/. Its rows are reconciled by the Orchestrator's relay or in my
next verdict.
