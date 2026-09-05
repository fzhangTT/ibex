# rt39 plan v2: five record-fidelity fixes in the flow

One document for one pre-execution review. v1 (20dad20) was REQUEST-CHANGES at 57489ff; v2 answers the
eight CM219 rows and the Critic's four gaps (gen_rt39_preread_gap.md) in the plan text. Plan only:
nothing is implemented until this replan is APPROVED. Under LOG-095 the whole of rt39, plan through
response rows, is one feature group with one Critic verdict at GROUP COMPLETE.

Every line number is at HEAD 3cc3c72 and every figure below is re-derived from the committed round-0
record, not from a review row. Where v1 stated something I had taken from a row rather than the code,
v2 says so.

## 0. What v1 got wrong

- It omitted the LOG-092 restatement of the stored round-0 group figure, and said the opposite
  (CM219 MAJOR-1). Section 2 now carries it as a required part of the same landing.
- It recorded only `+define+` tokens and kept the field name `defines`, so one name would still mean
  two things (CM219 MAJOR-2). Measured: the config group emits 5 defines and 14 `-pvalue` parameters.
- It said "same shape as full_exclusions" and "no stored name or timestamp" in the same item, which
  contradict (CM219 MAJOR-3, Critic PR-1). The committed full_exclusions archives DO store a name and
  the collect-time mtime.
- Its reds for items three and four leaned on "the record check", which does not exist (CM219 MEDIUM-1,
  Critic PR-3).
- It claimed a gen_build self-test that does not exist (CM219 MEDIUM-3).
- It said purpose 4 controls indexing; it does not (CM219 MINOR-1).
- It missed gen_dashboard as a third definer of the group cell (Critic G-3) and the two downstream
  copies of `defines` (Critic G-4).

## 1. Why these five are one group

They touch one artefact chain: gen_cov_report writes a record, gen_round copies and reshapes it,
gen_dashboard reshapes it again, gen_build writes the build manifest both cite, gen_regress copies
fields from it. The common defect is that the flow records something true of one thing beside something
true of another, and a reader cannot tell which without opening the source. That produced two wrong
figures in circulation during the round-0 record, mine and the DV Lead's.

## 2. Item one: one definition for the group cell

THE RULED QUANTITY (DV Lead criterion ruling, cited in the plan set). The gate's first condition reads
a BIN PERCENTAGE over the covergroups in gate scope: hit bins in scope over declared bins in scope,
with the witness ledger out of BOTH terms. For team round 1 that is 3477/4048 = 85.89.

NUMBERING, stated once here because this plan uses three names for two things (LOG-092 requires the
mapping in every record): TEAM ROUND 1 IS THE FLOW'S MEASURED ROUND 0, evidence directory
dv/auto_dv/evidence/gen_round_0, regression tag round_1. Every "round-0 entry" below means that same
round's entry in the flow's index. "Round-2" below uses the TEAM numbering, so it is the round after
team round 1 and would be the flow's measured round 1.

Three definers exist today and all three must end up reading the ruled quantity:

- `gen_cov_report.py:138` sets the cell to the weight-averaged covergroup score
  (`group_score_excluding`, `:230-239`, sum(score x weight)/sum(weight), no bin denominator at all)
  when a ledger row was found, and to URG's report-wide total when none was, so the cell's meaning
  depends on the contents of the run. `:139-140` then copy URG's report-wide bin ratio into the same
  row, pairing a percent from one definition with a denominator from another.
- `gen_round.py:106` overwrites the percent with URG's grand total and `:107-110` the ratio with the
  grand total's, its docstring saying "group from the grand total".
- `gen_dashboard.py:89-92` does the same overwrite again for the dashboard (Critic G-3), so the ruled
  definition must reach it or the dashboard keeps printing the unscoped figure (CM218-Info).

THE CHANGE. gen_cov_report emits three explicitly named fields, each with the denominator that produced
it: `group_bins_gate` (hit-in-scope / declared-in-scope, ledger out of both terms) with its ratio and a
scope string; `group_bins_all` with its ratio; `group_score_weighted` with its covergroup count and no
ratio. gen_round and gen_dashboard both read ONE selector and never substitute, carrying the selected
field's scope string into the row they print. The content-dependent fallback at `:138` disappears.

CORRECTION 2026-09-05T11:33Z (rev62 Medium). This paragraph said the two select `group_bins_gate`.
THEY DO NOT: the shipped selector reads `group_bins_all` (gen_flow_const.py `GROUP_CELL_FIELD`, per the
LOG-097 addendum 4 ruling that suspended the criterion field). The three fields and the one-selector
design are as described; only the field the selector names differs, and it is one token.

SCOPE BOTH TERMS, and the ruling says why this round hides the bug: the ledger was 0 of 220, so the
numerator 3477 is right either way, and a fix that scoped only the denominator would pass its round-1
test while being wrong. A witnessed clause hit in a later round must leave the gate figure untouched.

LABEL AND HEADER. Emit percent and denominator together, never the percent alone: "85.89 (3477/4048)".
The scope string names the population in words, in and out, e.g. "functional bins, covergroups in gate
scope, witness ledger gen_wit_cycle_clause_cg excluded (220 clauses)". `gen_round.py:139` and `:311-312`
hardcode the label "bins >= 80"; derive it from the selected field's scope string (CM219 MINOR-2).

THE RESTATEMENT WAS PLANNED FOR THIS LANDING (CM219 MAJOR-1) AND WAS NOT DONE.

CORRECTION 2026-09-05T11:33Z (rev62 Medium). What follows describes a restatement the landing does NOT
make, and it is kept only to say so. Because the selector reads `group_bins_all`, which is the same
quantity the round-0 entry already stores as 81.47, there is no rule change for a delta to span and
nothing to restate. The landing restates nothing. The paragraph's reasoning still holds for the day the
selector moves to `group_bins_gate`: the stored 81.47 would then need restating as 85.89 (3477/4048)
with a line saying it is the same measurement under a different rule, or a later delta would read
+4.42 points of coverage that are entirely a change of rule.

THE RED, rewritten because v1's could not be run (Critic G-2): the regression manifest carries no gate
verdict to compare with the summary, so "the two artefacts disagree" is not directly observable. The red
is instead: for one fabricated coverage record, the ruled field, its denominator and its scope string
must be identical in the manifest, the round summary and the dashboard row, and a record whose ledger is
non-empty and partly hit must yield the both-terms figure 3477/4048 and NOT the larger figure a
denominator-only scoping produces. Both fail against the pre-change code.

CORRECTION 2026-09-05T12:11Z (Critic rt39 L-1). "Both fail against the pre-change code" is not what was run
and could not have been: the pre-change code holds no such named quantity, so there is nothing in it for
either red to fail. Both are PROPERTY DEMONSTRATIONS of the landed code. The both-terms red is shown by the
shipped control's 3484/4048 against 3477/4048 and by the self-test's 15/20 against 22/20. The identity red
of the sentence above went unevidenced at the landing, which the Critic's M-2 also names; it is now run and
retained in gen_tdd_logs/flow/gen_rt39_reds2.log Section 5, where the three consumers agree over the
committed round-0 record and one consumer made to name another quantity is caught.

The failing value is 3477 plus however many ledger bins are hit, because a denominator-only fix removes
the ledger from the declared count while still counting its hits. The shipped control gives the ledger
SEVEN hit bins and so measures 3484/4048 against 3477/4048. The plan review's rewrite named 3482/4048,
which is the same mechanism with its own five-hit example (3477 + 5); the two figures are one claim, not
two, and the control's value is the one to reproduce.

WHAT THIS DOES NOT DO. It does not claim the functional gate passed: the criterion has two conditions
and the second, traceability confirmed by someone other than the author, is a separate finding the DV
Lead has not made.

## 3. Item two: the build manifest's defines field

MEASURED on the committed round-0 build manifest, not taken from a row: `defines` records
`['+define+RVFI']`, one token, while the recorded `command` carries 9 distinct `+define+` tokens and 14
`-pvalue` parameters. The config group alone emits 5 defines and 14 parameters; `flag_groups` already
carries the breakdown. `gen_build.py:117` builds the group from the testlist entry plus `--define` only,
and `:348` records that group under the name `defines`.

THE CHANGE (CM219 MAJOR-2, rt40 ruling). Record the full compile-time configuration under names that say
what they are: `defines_all` (every `+define+` token in the assembled command, in order) and
`parameters_all` (every `-pvalue` parameter), keeping the per-group breakdown under `flag_groups`. The
existing `defines` key keeps its current population for one landing and is documented as the
testlist-and-CLI subset, or is removed if the review prefers a clean break; I will implement whichever,
and I recommend removing it, since a name that has meant two things is worse than one absence.

DOWNSTREAM COPIES (Critic G-4): `gen_regress.py:84` copies `defines` into the builds entry and `:706`
into `coverage.build_defines`. Both carry the new keys.

SELF-TEST (CM219 MEDIUM-3): gen_build has no self-test today, so v1's claim was false. Adding one is
item-two work: a `--self-test` over a fabricated build spec asserting that a define emitted by the
config group appears in `defines_all` and that the parameter count matches the command. Its red is that
same assertion against the pre-change code, where `defines_all` does not exist.

## 4. Item three: the dirty-file facts (CM219 MEDIUM-1, Critic G-1, PR-2)

TWO FACTS EXIST TODAY AND THEY HAVE DIFFERENT SCOPES, which v1 conflated:

- `gen_flow_util.py:216` returns `dirty_tracked_files`, a boolean over the whole tree, tracked files
  only. `gen_regress.py:635` records `worktree_dirty` from it for worktree-mode runs only, so a
  head-mode round records None there.
- `gen_round.py:257` copies the boolean into the index as `git_dirty_tracked_files` and also records
  `flow_git_status_now`, which is flow-directory scoped and includes untracked files.

Measured on the round-0 entry: the flag reads true and there is no list. The eight-file list quoted in
discussion was read at collect time, 22:06:02Z, twelve minutes after the flag's stamp at regression
start, and I confirmed no log of mine recorded the set at the earlier stamp.

THE CHANGE. `git_head()` returns the porcelain list beside the boolean. Each recorder states ONE scope
in the field name and in a scope string: `dirty_tracked_tree` (tree-wide, tracked only) at regression
start with its stamp, and `dirty_flow_dir` (flow directory, including untracked) at collect with its
stamp. Both stamps are recorded, so a regression-start set can never be read as a collect-time set.

WHERE THE CHECK LIVES (CM219 MEDIUM-1, Critic PR-3). v1 said "the record check" refuses; no such check
exists beyond `check_canary_build`. There is no new refusal: a bare boolean with no list is RECORDED as
such, not refused, because the committed round-0 manifest carries exactly that shape and refusing it
would reject a committed record. The schema tell is the presence of the list field; its absence means an
older record. This keeps Section 7's "no verdict path" true.

THE RED is synthetic on both sides and the plan says so honestly: no committed record carries a list
yet, so no positive control can exist until this lands. The red is a fabricated tree with two dirty
files producing a two-name list at the recorded stamp, and an older record without the field being read
without error.

## 5. Item four: the canary identity (CM219 MEDIUM-2, CR-40 L-2)

The index entry's `canary_build` names paths under `dv/auto_dv/work/`, ignored at
`dv/auto_dv/.gitignore:4`, so `git ls-files` knows neither. It DOES copy the gate's inputs as values:
source_mode, the full head_sha, covergroups_declared, covergroup_files, both b8 defaults. What it omits
is the identity: the record's build manifest carries `sources_sha256 bc0cd7778e382b13991...`, the
canary's manifest carries the same value, and the index entry contains that string zero times, which I
grepped.

THE CHANGE. Carry BOTH values and their compare result: `canary_sources_sha256`, `round_sources_sha256`,
`sources_sha256_match`. State in the record that the digest covers the filelist sources only, so it is
not a claim about defines or parameters; once item two lands, carry the define and parameter sets too so
the comparison covers the compile configuration as well.

THE RED: an index entry built from a canary whose identity differs from the round's build records both
values and a false match flag. Positive control: the committed round-0 pair, where the two digests are
equal, so the flag reads true on real data.

## 6. Item five: collect retains modlist and modinfo (CM219 MAJOR-3, Critic PR-1)

v1 said "the same shape as full_exclusions" and "no stored name or timestamp" in one item. Those
contradict: the collect's `gzip.open` embeds the source name and the collect-time mtime, and all eight
committed full_exclusions archives store both. The reproducible shape is the one I used by hand for
`gen_modlist.txt.gz` at a6f811a.

THE CHANGE. collect retains both files with `gzip.GzipFile(fileobj=..., filename="", mtime=0)`, and item
five's red reproduces the sha256 against that shape: compressing the same source twice must give the
same digest, which fails against `gzip.open`. Converting the eight full_exclusions archives to the same
shape is proposed as part of this item and stated as a change rather than assumed, since it alters bytes
that are already committed.

## 7. What this plan does NOT change

- No measurement changes. Nothing here alters what is simulated, merged or checked. Round 0's
  measurements stand; item one restates one stored FIGURE under the ruled definition and says so.
- No new refusal path. Item three records rather than refuses, for the reason in Section 4.
- The gate threshold is untouched, and this plan does not claim the functional gate passed.
- The measured/unmeasured split, the head-mode pin, the canary gate's logic and the fcov policy are
  untouched.

## 8. The per-family pre-flight (LOG-096), unchanged from v1 except one correction

    gen_regress.py --tests <the measured entries carrying a manifest> --base-seed <the round's base> \
      --source head --head-sha <the family landing's FULL 40-character sha> --max-parallel 8 \
      --tag <family>_fcov_preflight

Coverage on, no `--purpose 4`. CM219 MINOR-1: purpose 4 controls the head-mode default, the exclusion
dump and retention pruning, NOT indexing; the reason this wave is never indexed is that gen_round never
collects it. Cost measured: 202.3 s for 24 runs, 280.2 s for 36. Two conditions for the review: derive
`--tests` by calling the selector at that landing's commit, never from a stored list, and use the full
40-character sha, since an abbreviated one builds and passes and then makes the round refuse after it
has pinned.

## 9. Evidence, sequencing and cost

CORRECTION 2026-09-05T12:11Z (Critic rt39 L-1). Read "each failing against the pre-change code" as it applies:
items two, four and five have reds that do fail against the code they replace, and item one's are property
demonstrations of the landed quantity, for the reason given in Section 2's correction.

Reds as listed per item, each failing against the pre-change code and passing after. Positive controls
on the real committed round-0 record for items one, two and four; item three has none by construction
and the plan says so; item five's control is the a6f811a pair. Whole-flow self-tests green, plus the new
gen_build self-test. Retained TDD log under gen_tdd_logs/flow with a manifest row.

No simulation at any point: every item is Python over records that already exist.

Expected wall time, mine, no LSF: 120 to 150 minutes for the implementation with its reds and controls,
about 30 for the retained log and the response rows.
