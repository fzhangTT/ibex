# Critic verdict: the range c3bd17a..2402704 as one (Runtime rt34 3691c49, tb-infra landing 30 2402704), reviewed as tb_l29

Scope (the Orchestrator's): two working commits judged together: rt34 (the detector control gen_l25_fcov_detector_control_red.log, the same entry, build and
seed, 6 of 6 PASS against a scratch-root fixture's 1 of 0 UNHIT with exit 2 and the simulation passing in both; gen_read_keyed.py with its self-test and
retained proof; the CM204-Low-2 and Info-4 rows) and landing 30 (the CM204 rows including the :46 owner correction to the UNINITALL root, the probe joining
continuations with a discriminating self-test case, the nine headers' one-sentence citation, CR-27-L-1's Section 7 correction). Not in the range: rt35, the
standing guard.

Artifacts reviewed (committed blobs at 2402704; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l25_fcov_detector_control_red.log  1ad3b2d530a285bb
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_read_keyed_selftest.log  82075dbe84a52e26
- dv/auto_dv/tools/gen_read_keyed.py  d07114e6e7746752
- dv/auto_dv/docs/gen_runtime_api.md  36c339fcb13ed32e
- dv/auto_dv/evidence/gen_critic_response_flow.md  5b4ffa1f2f7a5247
- dv/auto_dv/evidence/gen_tdd_logs/flow/gen_manifest.md  1f129c61b9ee37f0
- dv/auto_dv/tools/gen_norm_probe.py  4a6baae848cad74c
- dv/auto_dv/docs/gen_wp8_part1_plan.md  2ea5a2ccaaf053e1
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  a8e79aa0bbfb3ec1
- dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_tag_disabled.fcov.yaml  39447dceb85372dd
- the other eight per-entry manifests dv/auto_dv/fcov_expectations/gen_ut_lockstep_icache_ecc_*.fcov.yaml (headers read together)

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l27.md
(db8273d3a7426b8a, CR-27-L-1) and gen_critic_tb_l28.md (844b8439f5a3154b); the CM204 artifact (a13b705a12f137ae); the evidence rule and the trust-triad rule
that a checking mechanism's failing direction is evidenced by a run that fails.
Method: detached git worktree of 2402704. Landing 30's files list (0a8b877a0fcb, 12 rows) equals its commit's diff; 11 of 12 md5s on the on-disk hashes list
verify and the twelfth (gen_wp8_part1_plan.md) does not because that list (19790333af54) is newer than the committed one the Orchestrator named
(9bb567252ab4): tb-infra's next touch is in flight in the shared tree, and the committed content is what I judged. rt34's six files match TASKS row 1192; its
two logs' manifest rows recomputed (2552 / 662543da2c628e46, 2579 / 487794e0876c31e1). Gates on the worktree, all PASS: both codegen checks, CONST-CHECK,
RED-CHECK, the manifest schema sweep 27 OK, the flow self-test 155 ok; both identities unchanged across the range (b48479a3bc6f1d9f, f80e2c719e16b73c).
The detector control's premises re-derived: the entry gen_ut_lockstep_icache_ecc_tag_disabled carries the tag-RAM knob only, so gen_ic_ecc_cg.cp_ram.data
is unreachable by construction; its committed manifest declares 6 bins and not that one; `git diff --name-only 813994b..3691c49` over tb, env, isa, gen_tb
and rtl returns 0 files, so the 813994b build's reuse is sound. gen_read_keyed.py read by code path: it imports io, re, sys and pathlib only (neither
ci/check_fcov_expectations.py nor gen_fcov), exits 0 on agreement, 1 on a differing count or a missing key, 2 on a wrong call; its --self-test PASS here
(five cases), a wrong call and no argument rc 2. gen_norm_probe.py at 2402704: joined_lines mirrors load_plan's join, plan_bullets takes the loader's
REL_PLAN, --self-test copies the renderer from the tree --root names, -h exits 0 (run), the new wrapped-marker case discriminates and PASS, and the census is
unchanged at 154 over 64 (marker 26 as 10 plus 16), as predicted since no marker line wraps. Landing 30's rows, the plan's Section 7 correction and the nine
headers read against the diffs. No subagent used. EXPOSURE: none beyond the Orchestrator's message and the git log subjects. Section 6 reconciles with this
range's cross-model review; at the time Sections 1-5 were written its artifact did not yet exist (the review launches when the current one exits), and per the
Orchestrator's standing instruction this verdict waits for it.

CRITIC VERDICT: APPROVE. The failing direction of the fcov-expectation leg is now evidenced by a run that fails for the expectation alone, with its
discriminating pair and its premises checkable from the committed record; the independent reader is a committed tool with a proof; and landing 30 answers
every CM204 row and CR-27-L-1 as stated, each verified. No new rows.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 3691c49 (Runtime rt34) | the detector control: the fixture is an archive of HEAD with one manifest's bins replaced by gen_ic_ecc_cg.cp_ram.data alone, stem and test field unchanged so the loader accepts the entry; the run FAILs with "fcov expectation unmet: 1 declared bin(s) not hit" and exit 2 while the simulation passes; the discriminating pair on the committed manifest PASSes at 6 of 6; the bin is unreachable from the entry's own plusargs, not merely unhit | the plusargs (tag-RAM knob only) and the committed manifest (6 bins, no cp_ram.data) at 2402704; 0 build inputs moved since 813994b; the log read whole |
| 3691c49 | gen_read_keyed.py: an independent parser of urg's grpinfo.txt (Group, Summary for Variable / Cross, NAME COUNT tables), compared bin by bin with the checker's keyed output per run directory, the owed bins printed; exit codes 0 / 1 / 2; --self-test over a fabricated report and three result files (agreement, a count mismatch, a missing key, a run with no derived report); the proof log with the exit codes captured directly and the nine real runs re-read (7, 10, 10, 7, 10, 11, 9, 8, 6 agreeing) | the code's imports and exits; the self-test PASS; the wrong calls rc 2; the manifest rows |
| 3691c49 | API Section 7c names the reader and its use; the response rows: CM204-Low-2 accepted, CM204-Info-4 (the run log's header sentence overstates section 2; corrected in the row, the log untouched by the ruling), the control closing the does-not-establish gap | the diffs |
| 2402704 (tb-infra landing 30) | CM204-Medium-1: the three rows name the UNINITALL root's baseline field for gen_icache_ram.sv at :46, with how the owner was got wrong; Low-1: the CM202-Minor-1 row's first half labelled the landing-26 state and the 78 counts cited to the corrigendum at aaff8f5; Low-3: joined_lines mirroring load_plan with a self-test case whose first physical line holds a full tuple and whose continuation holds a short one; Low-4: mod.REL_PLAN; Info-1: --self-test --root and -h exit 0; Info-2: "no 3.10-only syntax"; Info-3: the nine headers' one sentence naming the run log and its corrigendum, no sha, no figures; CR-27-L-1: Section 7 says the plan over-claimed the two-form agreement and cites the corrigendum for the nine-entry measurement | the diffs; the probe's self-test and census re-run; the plan's flattened text; the nine headers still parse to the same data (sweep 27 OK) |

## 2. Rows

- CR-27-L-1 CLOSED (tb-infra's half here; Runtime's half by the corrigendum at aaff8f5). CM204 Medium-1, Low-1, Low-3, Low-4, Info-1..3 (tb-infra's) and
  Low-2, Info-4 (Runtime's): answered as stated. The exercising log's does-not-establish gap: closed by the detector control.

## 3. Findings

None.

### Informational

- I-1: the fixture manifest itself is not retained as a file; its whole content is one declared bin named in the log, and the committed manifest it replaces
  is the entry's, so the control is reproducible from the log's description. A retained fixture would remove even that step.
- I-2: the run log's header sentence corrected by a response row rather than a file: consistent with the ruling that a retained log's bytes never move
  and with the rule against reopening a committed supplement; the row is the record a reader must pair with the log, and Runtime says so.
- I-3: tb-infra's next touch is in flight in the shared tree (the plan's md5 differs from the committed one); judged the committed content.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: the leg's failing direction evidenced by a discriminating pair that
differs only in the declared bin set, with the bin unreachable by construction (conforming). S2: the reader is independent of the checker it audits, by
import and by design, and its self-test observes each exit path (conforming). S4 honesty: the over-claim corrected on both halves and the owner of a cited
line corrected with how it was got wrong (conforming). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range c3bd17a..2402704. Rows CR-29: none.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-c3bd17a2-2402704d.md (57cae3d7dc078c0f, 46 lines), read after Sections 1-5 were written (it was the wrapper's
empty placeholder while they were; content landed 15:43:00Z). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached
read-only checkout of 2402704. Its verdict: APPROVE-WITH-CHANGES, two Lows, two Infos, the five rubrics PASS. Mine: APPROVE with no rows. The verdicts
are compatible: both Lows are refinements of a record figure and of the reader's table handling, neither touches a claim the range makes, and a Low does not
force REQUEST-CHANGES under my rules; both are misses of this verdict, adopted and verified below, owed through the rows the Orchestrator relays.

Shared recomputations, each re-run by me after reading the artifact and equal to it: the exercising log's blob at 8f265b2 equals HEAD's (55bc5f7e9e578024)
and the corrigendum's at aaff8f5 equals HEAD's (fa086f0624281a76), no commit of the range touching either; gen_manifest.md:207-208 carry 2552 /
662543da2c628e46 and 2579 / 487794e0876c31e1 with 26 md5 rows; the reader's --self-test prints five ok lines and exits 0, and no argument, an unknown
argument, --self-test with an argument and a directory without result.yaml each exit 2; the reader imports io, re, sys and pathlib at the top and yaml inside
its functions; the entry's plusargs at gen_testlist.yaml:2404 carry the tag-RAM knob only, gen_tb_pkg.sv:86 and :87 define the tag-RAM and data-RAM knobs,
gen_fcov_groups.svh:4621 gives cp_ram the bins tag and data; `git diff --name-only 813994b 3691c49` returns 0 files over tb, env, isa, gen_tb and rtl and 0
over stim, flow and ci; the exercising log's :9 reads "every figure below is from the second"; cov_reds.log:31-36 is the GREEN root without a baseline pair,
:38 opens UNINITALL and :46 is its baseline fc376b9db3ad3868; the nine manifests parse equal between c3bd17a and 2402704 with 7, 11, 10, 10, 10, 9, 8, 6, 7
bins (78), each test field equal to its stem, the text differing in the headers only; gen_norm_probe.py's joined_lines mirrors the loader's join at
gen_fcov_codegen.py:57-61; -h exits 0 and an unknown argument 2; the census is 154 classification rows at c3bd17a and at 2402704 with the name and class
columns identical line for line, and 158 at 332aa17 (65 groups, marker 30 as 11 plus 19) from the 2402704 probe over an archive of that commit's dv/auto_dv.

The artifact's findings, each adopted and verified:

- Low (gen_critic_response_fu2a.md, the CM204-Low-3 row): the row says the committed and the fixed probe give "153 classification rows"; I measure 154 at
  c3bd17a and 2402704 and 158 at 332aa17, so no commit in play produces 153 and the figure has no retained artifact. The row's conclusion (identical tuples)
  holds: my two runs are identical in the classified columns. A miss of tb_l29: Section 1 re-ran the census at 154 and read the row for its conclusion
  without comparing the row's own figure to it, the class my rules name (a response row that quotes a count is itself a site). The artifact cites the row
  at :102; in the committed blob (a8e79aa0bbfb3ec1) it is line 478 (:102 is an A2c row); the substance is unaffected.
- Low (gen_read_keyed.py:49): parse_report opens a table on Covered bins, Uncovered bins or Bins and closes it only at the next Group or Summary line,
  while the checker's ci/check_fcov_expectations.py:87 also closes on Excluded/Illegal bins, Summary for, Variables for and rule lines. Reproduced on a
  fixture in both directions: without an excluded table the two parsers read the same two bins; with an Excluded/Illegal bins table after cp_a's covered
  table the reader carries gen_x_cg.cp_a.na = 5 that the checker drops, and a result.yaml declaring only that bin gets rc 0 from the reader (the masking
  the artifact names). Exposure at 2402704: every coverpoint of the groups carries an ignore bin (215 illegal_bins / ignore_bins lines), so real reports
  hold such tables (the checker's reset regex was written for them), but no manifest declares a bin ending in .na (0 of 27), an extra key never enters the
  bin-by-bin comparison, and the owed listing filters by suffix; the nine agreeing runs are unaffected. A miss of tb_l29's code-path reading, which checked
  imports and exit paths and not the table-boundary set against the checker's.
- Info (gen_read_keyed.py:20): OWED_SUFFIXES hand-encodes during_invalidation and masked_duplicate_copy; both are cp_no_alert_case bins in the plan
  (gen_fcov_plan.md:4848, :4867) and appear once each in gen_fcov_groups.svh; a display-only filter, agreed.
- Info (the detector control log): no result.yaml of either run is retained, so the FAIL / PASS pair is read from the log alone; agreed, and it complements
  my I-1 (the fixture manifest described, not retained). The artifact cites :137; the log has 32 lines, the FAIL block is :21-26 and the PASS line :29.

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. The two adopted Lows are misses, not errors, of this verdict.
