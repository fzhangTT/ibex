# rt39 plan: five record-fidelity fixes in the flow

One document for one pre-execution review, covering five items that the round-0 record and its reviews
found. Plan only. Nothing is implemented until the plan review and, under LOG-095, the single Critic
verdict for this feature group are recorded. Author: Runtime Manager.

Every claim below was read in the code or measured on the committed round-0 record, and the line
numbers are at HEAD 3e23389. No item changes what the flow measures; all five change what it records
or how consistently it records it.

## 1. Why these five together

They are one feature group under LOG-095 because they touch the same three modules and the same
artefact chain: gen_cov_report writes a record, gen_round copies and reshapes it, gen_build writes a
build manifest that both cite. Reviewing them separately would review the same chain five times.

The common defect is not arithmetic. In each case the flow records something true of one thing beside
something true of another, and a reader cannot tell which is which without opening the source. That is
what produced two wrong figures in circulation during the round-0 record: mine and the DV Lead's.

## 2. Item one: the group cell has two definitions and the gate sits between them

What the code does now.

`gen_cov_report.py:138` sets the gate row's group percent to the weight-averaged covergroup score when
a ledger row was found and excluded:

    res["gate_row"]["group"] = gs["score"] if gs["ledger_excluded"] and gs["score"] is not None else res["totals"].get("group", C.NOT_APPLICABLE)

and `:139-140` then copy URG's report-wide bin ratio into the same row:

    if (res["totals"].get("ratios") or {}).get("group"):
        res["gate_row"]["ratios"]["group"] = res["totals"]["ratios"]["group"]

`gen_round.py:106` overwrites that percent with URG's grand total, and `:107-110` overwrite the ratio
with the grand total's ratio, its docstring stating "group from the grand total".

Measured consequence on round 0. The manifest carries 78.29 beside 3477/4268; that ratio is 81.47. The
generated summary carries 81.47 with the same ratio and is self-consistent. `gen_round.py:139` tests
whatever the cell holds against `C.GATE_PCT`, 80.0 at `gen_flow_const.py:514`, so the two committed
artefacts of one run reach opposite verdicts on the same metric. A third quantity, bins excluding the
ledger's 220 clauses, is 3477/4048 = 85.89 and no artefact reports it.

There is also a content-dependent fallback: `:138` yields the weighted score when a ledger row exists
and the report-wide total when it does not, so one field name carries different quantities across runs.

The change. One module owns the cell. gen_cov_report emits three explicitly named fields rather than
one overloaded one: `group_bins_all` with its ratio, `group_bins_excl_ledger` with its ratio, and
`group_score_excl_ledger` with its covergroup count and no ratio. gen_round selects the one the gate
criterion names, carries its scope string into the row it prints, and never substitutes a different
quantity. The fallback disappears because each field is either present with its own denominator or
absent.

Which one the gate uses is a criterion question, not a coding one, and belongs to the DV Lead: the
criterion's words are "bins >= 80", a weight-averaged score is not a bin percentage, and the
report-wide ratio's denominator includes a ledger that is not coverage. I will implement whichever the
review rules and will not pick it inside the diff.

Reds. A fabricated coverage record whose weighted score and bin ratio straddle 80.0 must produce the
same verdict in the manifest and in the summary; against the pre-change code that case produces
opposite verdicts, which is the red. A second red: a record with no ledger row must not silently change
which quantity the field holds.

## 3. Item two: the build manifest's `defines` lists one of nine

What the code does now. `gen_build.py:117` builds the defines group from the testlist entry's own list
plus `--define` arguments only:

    groups["defines"] = [f"+define+{d}" for d in list(build.get("defines") or []) + list(a.define or [])]

and `:348` records exactly that group as the manifest's `defines`.

Measured on the committed round-0 build manifest: `defines` is `['+define+RVFI']`, one entry, while the
recorded `command` contains nine distinct `+define+` tokens: BaseIsa, COCOTB_SIM, RV32B, RV32M, RV32ZC,
RVFI, RegFile, UVM, UVM_REGEX_NO_DPI. The other eight come from other flag groups, `config_opts()` at
`:118` and the UVM flags at `:116`, which are equally part of the compile.

Why it matters beyond tidiness: a reader auditing what a measured build actually defined reads
`defines`, gets one token, and concludes the build had one define. The full set is in `command`, and
`flag_groups` already carries the breakdown, so the data is present and the summary field is the
misleading part.

The change. Record `defines` as every `+define+` token in the assembled command, in order, and keep the
per-group breakdown under `flag_groups` as it is. The field then means what its name says.

Red. A build whose config or UVM group contributes a define must record it in `defines`; against the
pre-change code it does not, and the round-0 manifest is the positive control with a real 1-of-9 case.

## 4. Item three: the dirty-file flag has no list and no stamp (CM218-L-1)

What the code does now. `gen_flow_util.py:216` returns `"dirty_tracked_files": bool(dirty)`, a boolean
and nothing else. `gen_regress.py:635` records `worktree_dirty` only for worktree-mode runs, so a
head-mode round records None there. `gen_round.py:257` copies `git_dirty_tracked_files` from the
regression manifest's git section into the index entry, and `:301` prints it in the summary beside the
collect-time flow status.

Measured consequence on round 0: the index says true, the flag was stamped at regression start
21:54:27Z, and the eight files everyone quoted were read at collect time 22:06:02Z, twelve minutes
later. Nothing recorded which files were dirty at the earlier stamp, and I confirmed no log of mine
did either. The two sets could differ, because two roles had work in flight across that window.

The change. `git_head()` returns the porcelain list alongside the boolean. gen_regress records the list
with the stamp at which it was taken. gen_round records its own list with its own stamp at collect,
rather than reusing the regression's flag, and the summary names both moments.

Red. A fabricated tree with two dirty files must produce a two-name list at the stamp recorded, and a
record carrying a bare boolean with no list must be refused by the record check rather than accepted.

## 5. Item four: the canary is named by paths a reader cannot open (CR-40 L-2)

What the code does now. The index entry's `canary_build` carries `path` and `manifest` under
`dv/auto_dv/work/`, which `dv/auto_dv/.gitignore:4` ignores, so `git ls-files` knows neither file.

What survives is more than the paths, and the row that raised this understated it: the entry copies the
gate's inputs as values, `source_mode`, the full `head_sha`, `covergroups_declared`, `covergroup_files`
and both b8 defaults. What it does not copy is the identity. The record's own build manifest carries
`sources_sha256 bc0cd7778e382b13991...`, the canary's manifest carries the same value, and the index
entry contains that string zero times. So the record proves the round's build identity and does not
prove the canary shared it.

The change. Copy the canary's `sources_sha256` into the index entry beside the gate facts already
copied. The paths stay as recorded facts, which is all they are.

Red. An index entry built from a canary whose identity differs from the round's build must record both
values and the record check must flag the mismatch; today neither value is present to compare.

## 6. Item five: the collect step drops the two files its own analysis needs (CR-41 L-4)

What the code does now. `collect()` copies six URG text reports into the evidence directory. The
round-0 tables and the DV Lead's analysis both rest on `modlist.txt` and `modinfo.txt`, which stay in
the out-tree. I retained them by hand as `gen_modlist.txt.gz` and `gen_modinfo.txt.gz` at commit
a6f811a; without that the record cited files it did not carry.

The change. collect retains both by default, gzipped with no stored name or timestamp so the artefact
is reproducible, in the same shape as `full_exclusions`.

Red. A collect over a regression whose report contains both files must produce both archives, and each
must decompress to the source bytes; a re-run must reproduce the same sha256, which plain `tar czf` or
plain `gzip` would not.

## 7. What this plan does NOT change

- No measurement changes. No item alters what is simulated, merged, or checked, and none touches a
  verdict path. Round 0's numbers stand exactly as recorded.
- The gate threshold is untouched. Item one makes the cell unambiguous; it does not move 80.0 and does
  not decide which quantity the criterion names.
- No committed record is edited. Items three, four and five change what future records contain.
- The measured/unmeasured split, the head-mode pin, the canary gate's logic and the fcov policy are all
  untouched.

## 8. The LOG-096 question, folded in as directed

Can the fcov pre-flight run per family landing as a fixed command, so each family's re-scope is
measured before dispatch rather than discovered at it?

Yes, and the command already exists in the shape run twice on 2026-09-04:

    gen_regress.py --tests <the measured entries carrying a manifest> --base-seed <the round's base> \
      --source head --head-sha <the family landing's FULL 40-character sha> --max-parallel 8 \
      --tag <family>_fcov_preflight

Coverage on, no `--purpose 4`, so it indexes nothing. It derives each entry's own seeds, so the
manifests are the only difference from the retained waves. Cost measured: 202.3 s for 24 runs, 280.2 s
for 36.

Two conditions the review should impose. The `--tests` list must be derived by calling the selector at
that landing's commit, never reused from a stored list, because a family landing can change which
entries are measured; reusing a list is what produced a wrong round size earlier. And the sha must be
the full 40 characters: an abbreviated `--head-sha` builds and passes and then makes the round refuse
after it has pinned.

## 9. Evidence, sequencing and cost

Reds as listed per item, each failing against the pre-change code and passing after. Positive controls
on the real committed round-0 record wherever one exists, which is items one, two and four. Whole-flow
self-tests green: gen_flow_util, gen_regress, gen_run, gen_fcov, gen_verdict, gen_round, gen_mirror,
gen_serve_requests, plus gen_build and gen_cov_report. Retained TDD log under gen_tdd_logs/flow with a
manifest row.

No simulation at any point: every item is Python over records that already exist, so this competes with
no round for machines.

Under LOG-095 this is one feature group: plan review first, then implementation, self-tests and
response rows as one range, with GROUP COMPLETE in the hand-off of the last touch so the range review
and the single Critic verdict follow.

Expected wall time, mine, no LSF: 90 to 120 minutes for the implementation with its reds and controls,
about 30 for the retained log and the response rows.
