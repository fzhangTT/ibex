# Critic verdict: tb-infra landing 17, the landing-16 review rows (commit 8ce613d, diff base c0ce69f), reviewed as tb_l18

CORRIGENDUM to gen_critic_tb_l17.md (c19ecfa1274acf89, committed d6d5c15, frozen): its Section 2 says "CR-16 L-1..L-5 CLOSED". CR-16 L-1 was closed on
two of the three sites tb_l16 named: at e2f3f65 the CM173-M-1 row of gen_critic_response_fu2a.md still read "scratchpad/gen_l15_figures.py" (checked on
whitespace-flattened text with the committed tool name as the control), the site the landing-16 cross-model review's m-1 also named. CR-16 L-1 was
therefore OPEN on that site after tb_l17; this landing closes it (Section 1). The failure was mine: I verified the two record sites the diff touched and
took the row's DONE for the third instead of grepping the class; the rule since (absence claims on flattened text with a control) covers it.

Scope (the Orchestrator's): the six files of landing 17 (the checker response file, the retained-log manifest, the tag-write history artifact, the
three derivation tools), answering CR-17-L-1 and the seven CM182 rows: the tag-write header separating what the file evidences from the causal
account marked as derived from two RTL line ranges; gen_trace_tagwrite_history.py's --from-artifact mode, claimed byte-identical to the scratch path;
corrected usage lines and exit 2 on a wrong call for the three tools; the identity gate's three outcome classes; the CM173-M-1 row and every record
site citing the committed tool names. This verdict also carries the owed reconciliation with the landing-16 cross-model artifact (Section 6).

Artifacts reviewed (committed blobs at 8ce613d; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_critic_response_fu2a.md  084229799d018c4a
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  6df93f2d1671b80d
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l16_trace17_tagwrite_history.log  06ad6ff007c6f574
- dv/auto_dv/tools/gen_icache_ecc_figures.py  27d4633250e8451c
- dv/auto_dv/tools/gen_mutant_build_identity.py  ab712be1648fd95a
- dv/auto_dv/tools/gen_trace_tagwrite_history.py  45d1586fe055e95f

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l17.md
(c19ecfa1274acf89) and gen_critic_tb_l16.md (ba4940caec224e93); rtl/ibex_icache.sv:534-535 (sel_way_ic1: the lowest invalid way, else the round-robin
way, chosen in IC1) and :589-594 (the correction invalidates the matching ways), the two ranges the header cites as the source of its derived account.
Method: detached git worktree of 8ce613d. The six listed files equal the diff (0 mismatches); the md5 list the Orchestrator named
(gen_landing17_hashes.txt) was not present in the shared work directory at review time, so the files were verified as committed blobs against the
diff and the manifest row recomputed (24188 bytes, md5 a7702922e3b65efc56b340e6ee2b1348). Re-derived by me: the three tools print their usage line and
exit 2 with no arguments and with --help (six calls); the figures reader on the tree exits 0 with an empty problems list; in a copy of the tree,
`gen_trace_tagwrite_history.py <copy> <absent scratch> --from-artifact` regenerates the artifact byte-identical to the committed one (same md5) and
leaves the manifest unchanged, while the same call without the flag refuses and names the flag; the identity gate exercised on synthetic roots built
from the retained per-file lists: all 13 present gives verified 13 and exit 0 (which re-proves the 13-root identity claim from committed files alone),
two roots removed gives NOT VERIFIABLE for both and exit 3, one root replaced by the landing list gives MISMATCH and exit 1; my own reconstruction of
the 16 episodes from the 322 retained writes is still identical to the artifact's block; `git ls-files` content flattened of whitespace holds the
scratchpad tool names in 0 files with the committed name in 3 as the control. No subagent used. EXPOSURE: none beyond the Orchestrator's
sha-and-scope message and the git log subjects. The cross-model review of this range had not launched at hand-off (Section 7).

CRITIC VERDICT: APPROVE. CR-17-L-1 and the seven CM182 rows are answered as stated, each behaviour claimed of the tools reproduced by me, the
artifact's header now says what the writes show and marks the cause as derived, and the reconstruction is reproducible from the tree alone. One low
on the tagwrite tool's usage line.

## 1. What was verified

| item | as built at 8ce613d | evidence (re-derived by me) |
|---|---|---|
| CM182 l-3: the header's claim | "WHAT THIS FILE EVIDENCES: ... valid in both ways at one index at the same time, and which way's copy was added second. Nothing more." "WHAT IT DOES NOT EVIDENCE: the cause ... DERIVED from rtl/ibex_icache.sv:534-535 and :590-592, not measured here. The writes below are CONSISTENT with that account ... consistency and not causation." | the cited ranges are the IC1 way selection and the correction's invalidation of the matching ways (read); the consistency facts hold on the 322 writes (16 of 16 episodes end on a same-cycle valid=0 write of both ways, tb_l17's draft check) |
| CM182 l-4: the 1564 total | "counted from the trace session's stdout, which is scratch and NOT retained, so that total is not checkable from the tree; the 322 lines below are" | the header text; the from-artifact mode carries the total forward from the header rather than recounting it |
| CM182 l-5: --from-artifact | re-derives the episode block from the raw writes inside the retained artifact; refuses when the artifact or its total is missing; the scratch path's refusal names the flag | regenerated in a copy: byte-identical (md5 a7702922e3b65efc56b340e6ee2b1348), manifest unchanged; the 16-episode block equals my independent reconstruction |
| CR-17-L-1 / CM182 l-1, l-2: usage text and wrong calls | each docstring opens with the tool's own name and real argument list; a USAGE constant and _usage() print the line and exit 2 on a missing argument or -h / --help | six wrong calls, six usage lines, six exit codes of 2 |
| the identity gate's classes (tb-infra's own finding) | verified / MISMATCHED / NOT VERIFIABLE (root purged), exit 0 / 1 / 2 (wrong call) / 3 (nothing mismatched, a root unchecked); the docstring states the codes and says to run before the post-landing cleanup | synthetic roots from the retained lists: 13 present exit 0 with verified 13; two purged exit 3 naming both; one equal to the landing build exit 1 with the MISMATCH line |
| CM182 m-1 / CR-16 L-1 (the third site) | the CM173-M-1 row names "the reader now committed as dv/auto_dv/tools/gen_icache_ecc_figures.py" | flattened `git ls-files` content: gen_l15_figures and gen_l15_mut_identity in 0 tracked files (reviews and Critic files excluded), gen_icache_ecc_figures in 3 |
| CM182 l-6: docstring narration | the retirement history removed from gen_trace_tagwrite_history.py's docstring; intent and inputs only | the diff |
| the figures reader | unchanged in behaviour; rc 0, problems [] on the tree | run |
| the response rows | CR-17 L-1 DONE with its cause (a rename script's first-occurrence substitution) and a method note; CM182 m-1, l-1..l-6 DONE; the "beyond the row" identity-gate finding recorded with its cause (a purged root counted as a mismatch) | read against the diffs |

## 2. Closure

CR-17 L-1 CLOSED. CR-16 L-1 CLOSED on its remaining site (the corrigendum above). CM182 m-1 and l-1..l-6: answered as stated (Section 6).

## 3. Findings

### L-1 (low) [S5 single source] The tagwrite tool's usage line omits the mode its docstring documents

gen_trace_tagwrite_history.py's USAGE string reads "<landing root> <scratch root>" while the docstring's first line reads "<landing root> <scratch root>
[--from-artifact]"; a wrong call therefore prints a usage line that does not mention the one mode a reader of the tree can run, and the mode still
demands a scratch-root positional it never reads. Add "[--from-artifact]" to USAGE (and let the flag stand in for the scratch root, or say the positional
is ignored with it).

### Informational

- I-1: the identity gate reads the landing build's list from the gitignored work directory, so from the tree a reader reconstructs its inputs from the
  retained per-file lists, as I did; the tool's three classes then behave as documented. It remains tb-infra's process gate, run before the cleanup.
- I-2: the md5 list the Orchestrator named for this landing was not in the shared work directory at review time; the six files were verified as
  committed blobs against the diff, which is the stronger check, so nothing is lost.
- I-3: the response file records the cause of each of its own defects (the rename script; the purged root counted as a mismatch) and the method gap
  behind them (positive checks only, never a wrong call). That is the record honesty the principles ask for, noted without a row.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the artifact header now separates evidence from derivation and labels the
unretained total (conforming). S6 retention: the reconstruction is reproducible from the tree alone and byte-identical (conforming). S5 single source:
one usage line short of its docstring (L-1). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE. Low L-1 with tb-infra's next touch. Rows CR-18.

## 6. Reconciliation owed by gen_critic_tb_l17.md (frozen): the cross-model review of landing 16, ae0ce2f..e2f3f65

Read after tb_l17 was frozen: dv/auto_dv/reviews/2026-09-04-claude-diff-ae0ce2f1-e2f3f65d.md (sha256 0ad051c4b7aef207, 45 lines, committed 678b27b),
APPROVE-WITH-CHANGES, one minor and six lows (the CM182 rows). Its independent verification (the 322 writes, the 16 episodes replayed byte-identically,
the delta applied, the figures reader's controls, the 400-character comparison, the retirement accounting) agrees with tb_l17 Section 1.

- Its minor (the CM173-M-1 row's scratchpad citation) is the corrigendum above: tb_l17 under-closed CR-16 L-1 on that site. Answered by this landing.
- Its lows l-1 and l-2 equal tb_l17 L-1 (the docstring name and the four-argument usage line). Answered by this landing.
- Its low l-3 (the causal account presented as evidenced): adopted and verified; tb_l17 had not raised it. Answered by this landing (Section 1).
- Its low l-4 (the 1564 total unretained) equals tb_l17 I-2, which asked for nothing; the review asked for the label, and the header now carries it.
- Its low l-5 (no re-run from the tree) sharpened tb_l17 I-1, which recorded the fact without asking for a change; the mode now exists and reproduces
  the artifact byte-identically (Section 1).
- Its low l-6 (docstring history narration) tb_l17 had not raised; the narration is removed.
- Verdicts agree: both approve landing 16 with wording and tooling changes; where it saw more than I did (l-3, l-6, the third site of L-1) the rows
  stand and are now closed.

## 7. The cross-model review of this range

Not read: at hand-off no artifact for c0ce69f..8ce613d existed under dv/auto_dv/reviews/ (the Orchestrator said it launches after the running one
finishes). Its rows are reconciled by the Orchestrator's relay or in my next verdict.
