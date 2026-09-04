# Critic verdict: tb-infra landing 20, the CM187 rows (commit 6457c71, diff base 4927ef5), reviewed as tb_l20

CORRIGENDUM-LITE to gen_critic_tb_l19.md (4d03328f1418ad44, committed 2f9fd13, frozen): its verdict line and Section 1 call the --from-artifact mode
"self-checking" and say "the self-check works". The check catches one thing: tag-write lines outside the indices the duplicate-copies artifact names.
Verified by me on copies of the 1e6dbc5 tree: an index appended to the duplicate-copies artifact regenerates quietly (rc 0, header "Indices 26, 27, 30",
md5 822c172b164f4432c95eb7143841e8e8; the landing-19 review's probe reproduced) and a deleted index-26 write regenerates quietly (rc 0, 321 lines kept).
tb_l19 probed only the direction that refuses and repeated the row's broad wording; nothing it states is false for the case it tested, but
"self-checking" over-states and its "No new findings" missed the five CM187 rows. My rule since: probe a claimed check in both directions before
repeating the record's wording.

Scope (the Orchestrator's): the four files of landing 20 answering the five CM187 rows: the tool accepting exactly the two usage forms (the mode as the
second positional, FROM_ARTIFACT computed once, any other argument count refused naming the forms); the refusal naming the duplicate-copies artifact
with the plural handled; the CM185-I-1 wording stating what the check tests and the two cases that pass; the premise paragraph naming the two behaviour
findings; the heading reading landings 17 and 18; the retained call-forms log and its manifest row. This verdict also carries the reconciliation owed by
tb_l19 with the landing-19 cross-model review (Section 6).

Artifacts reviewed (committed blobs at 6457c71; sha256 first 16 hex):

- dv/auto_dv/tools/gen_trace_tagwrite_history.py  ac2becc6f2ce2175
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  7fabdee5cd96b158
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l20_tagwrite_arg_forms.log  b4762997cc6bf6e5
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  266ec85b50d99228

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: gen_critic_tb_l19.md (4d03328f1418ad44);
dv/auto_dv/reviews/2026-09-04-claude-diff-d1f24f84-1e6dbc5a.md (c09e4be235eac694, the CM187 rows).
Method: detached git worktree of 6457c71 and a copy of it. The landing-20 list equals the four-file diff and all four md5s verify at 6457c71; the
manifest holds 3460 rows and the new log's row recomputes (1958 bytes, md5 e2f2e0a3a070eb9558812647ca40bebc). Re-derived by me: py_compile ok; the
call forms on the copy: none and -h print the usage line and exit 2; the landing root alone, a scratch root beside the flag, and a trailing argument
after the flag each print "exactly one of a scratch root or --from-artifact follows the landing root" then the usage line and exit 2; the landing root
with --from-artifact exits 0 and regenerates the artifact byte-identical (md5 a7702922e3b65efc56b340e6ee2b1348) with the manifest unchanged; an
absent scratch root refuses with exit 1 naming the flag; the form with a real scratch root is not runnable from the tree (the trace session is
scratch) and is taken from the retained log only. One appended index-30 line makes the mode refuse with "1 tag-write line outside the indices
[26, 27] the duplicate-copies artifact names" (singular), two appended lines with "2 tag-write lines" (plural). FROM_ARTIFACT is assigned once, before
use, from the second positional. The record sentences checked on whitespace-flattened text with controls: the CM182 heading reads "answered by
landings 17 and 18" (the stale form 0), the premise paragraph names CM182-l-5 and CM185-I-1 (the old generalisation 0), the CM185-I-1 row reads "It
catches only that" (the old over-statement 0). No subagent used. EXPOSURE: none beyond the Orchestrator's sha-and-scope message and the git log
subjects. The cross-model review of this range (2f9fd13..6457c71, shared with Runtime's rt23) was running at hand-off; Section 7 says whether its
artifact was read.

CRITIC VERDICT: APPROVE. The five CM187 rows are answered as stated and every claimed behaviour of the tool reproduced. One low on the retained
call-forms log, whose "first line of output" column does not equal the tool's first line for the three refusals that carry a message.

## 1. What was verified

| item | as built at 6457c71 | evidence (re-derived by me) |
|---|---|---|
| CM187-L-3: exactly two forms | `if len(sys.argv) != 3: _usage("exactly one of a scratch root or --from-artifact follows the landing root")`; `FROM_ARTIFACT = sys.argv[2] == "--from-artifact"` assigned once before use; S from the second positional otherwise | the six call forms above; a scratch root beside the flag and a trailing argument now refused (they were accepted at 1e6dbc5); the artifact byte-identical after every form |
| CM187-I-1: the refusal's wording | "the retained artifact holds %d tag-write line%s outside the indices %s the duplicate-copies artifact names" | one appended line: singular; two: plural; the source named |
| CM187-L-2: the CM185-I-1 wording | the row now says the check catches "an artifact holding tag-write lines OUTSIDE the indices the duplicate-copies artifact names ... It catches only that: a hand-edit that deletes or alters a line at one of the named indices passes ... and an extra index appended to the duplicate-copies artifact regenerates quietly" | the two passing cases are the ones I reproduced for the corrigendum above; the wording now matches the behaviour |
| CM187-L-1: the premise paragraph | "every defect was found by someone calling them in a way I had not, or reading a claim of mine against what the code does. Two were behaviour rather than text ... CM182-l-5 ... and CM185-I-1" | flattened check; the two rows exist on the same page |
| CM187-I-2: the heading | "rows CM182): answered by landings 17 and 18" | flattened check, the stale form 0 |
| the retained call-forms log | gen_fu_l20_tagwrite_arg_forms.log: six rows (exit 2, 2, 0, 0, 2, 2), the byte-identical regeneration across both accepted forms, the refusal reproduction; manifest row 1958 / e2f2e0a3a070eb9558812647ca40bebc | exit codes match mine for the five forms I can run; the "first line of output" column: L-1 |
| the response rows | CM187 L-1..L-3, I-1, I-2 DONE; L-3 records the author's own first-attempt name error caught by retesting the untouched forms | read against the diff; the lesson recorded is the one tb_l19's corrigendum-lite draws for me |

## 2. Closure

CM187 L-1, L-2, L-3, I-1, I-2 answered. No Critic row on landings 14 to 20 remains open other than L-1 below.

## 3. Findings

### L-1 (low) [S4 record] The call-forms log's "first line of output" is not the tool's first line for three rows

gen_fu_l20_tagwrite_arg_forms.log gives "usage: gen_trace_tagwrite_history.py ..." as the first line of output for `<landing root>`, `<landing root>
<scratch root> --from-artifact` and `<landing root> --from-artifact <scratch root>`. The tool's _usage(msg) prints the message first, so the first line
those forms print is "exactly one of a scratch root or --from-artifact follows the landing root" and the usage line is the second (re-derived on the
copy for all three). The exit codes and the claim "prints the usage line and exits 2" are right; the column is not what its header says it is, so
either the rows were transcribed rather than redirected or the column was normalised. Rebuild the table from redirected output (the team's excerpt
rule) or head the column "usage line printed" and keep a second column for the message.

### Informational

- I-1: the row `<landing root> <scratch root>` (exit 0, a real trace session) is not reproducible from the tree, since the scratch session is not retained;
  the log is the only record of that form. Consistent with everything else, and stated here so a reader does not look for a way to re-run it.
- I-2: the reviewer's and my probes of the self-check exercised different inputs (the duplicate-copies artifact against the retained artifact), as the
  Orchestrator noted; both stand, and the CM185-I-1 row now describes both outcomes.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the record's claims narrowed to what the check tests, the premise corrected
against the rows beside it, the heading made true; the retained log's one column is not what it says (L-1). S6 retention: the call forms retained with
their exit codes and the regeneration's md5 (conforming). One-line verdict: PASS with L-1.

## 5. Verdict

CRITIC VERDICT: APPROVE. Low L-1 with tb-infra's next touch. Rows CR-20.

## 6. Reconciliation owed by tb_l19 (frozen): the cross-model review of d1f24f8..1e6dbc5

Read after tb_l19 was frozen: dv/auto_dv/reviews/2026-09-04-claude-diff-d1f24f84-1e6dbc5a.md (sha256 c09e4be235eac694, 39 lines, committed 3b813c2),
APPROVE-WITH-CHANGES, the five CM187 rows. Its verification agrees with tb_l19 (the call forms, the byte-identical regeneration, the out-of-index
refusal, the per-site attribution, the three-tool usage audit); verdicts agree. Its five rows I verified on the 1e6dbc5 tree before this landing and all
five hold; all are answered here (Section 1). tb_l19 found none of them and over-stated the self-check as described in the corrigendum-lite above.

## 7. The cross-model review of this range

Not read: at hand-off dv/auto_dv/reviews/2026-09-04-claude-diff-2f9fd13c-6457c715.md existed as an empty, uncommitted file (0 lines, sha256 of the
empty input e3b0c44298fc1c14; `git log` names no commit for it): the review of 2f9fd13..6457c71, shared with Runtime's rt23, was still running. Its rows
are reconciled by the Orchestrator's relay or in my next verdict.
