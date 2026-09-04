# Critic verdict: the range 2402704..df28129 as one (tb-infra landing31a a9fb2c2, DV Lead plan set v4q df28129), reviewed as tb_l30

Scope (the Orchestrator's): two working commits judged together: landing31a (one file: the WP-8 part-1 plan's Section 7 cites the detector control as
flow-level evidence of the failing direction, names it a ONE-SHOT control and states why the STANDING guard waits on a Runtime flow change) and v4q (nine
files: the CM205-Medium-1 reword, the standing-guard row re-keyed to rt34, the census completeness clause, the NMI route sentence with the knob AGREED AND
NOT YET BUILT, three response rows, the contradiction-pair harness kind, the four generated records re-keyed to v4q-on-a6ae390). The commits 567e1b4,
a6ae390 and 20a11e4 in the range are review and Critic artifacts committed as written and are not judged here. Not in the range: Runtime's rt35.

Artifacts reviewed (committed blobs at df28129; sha256 first 16 hex):

- dv/auto_dv/docs/gen_wp8_part1_plan.md  adc92172b6c806d9
- dv/auto_dv/docs/gen_fcov_plan.md  450b9d45dc0686ad
- dv/auto_dv/docs/gen_test_plan.md  359bdb27d770493f
- dv/auto_dv/docs/gen_feature_list.md  233a03e2c7751612
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  604db4ec827a76cf
- dv/auto_dv/evidence/gen_round0_covergroup_set.csv  3ec608d8a13ead97
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  81562f317eceadd0
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  b9756177fd1fd14b
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  fcfe4fc48676df58
- dv/auto_dv/evidence/gen_round0_promotion_table.md  dcf9528c60726252

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l29.md (d21b23ac719ea5cd);
the CM205 artifact (67321c64cfcfd5e4, its Medium-1 the row v4q answers); the evidence rule (a claimed run maps to a retained artifact or counts as nothing)
and the honesty rule that a measured zero is stated as measured.
Method: detached git worktree of df28129 and a full archive copy for the generators. Gates on the worktree, all PASS: both codegen checks rc 0, the manifest
schema sweep 27 OK, both build identities unchanged across the range (b48479a3bc6f1d9f over 117 sources; f80e2c719e16b73c over 75 files); the range touches
no file under flow, tools, tests or fcov_expectations (git diff --stat empty), the testlist blob still d9526147a258. The four generated records regenerated on
the copy from their own header commands (gen_covergroup_set.py and gen_promotion_table.py with --plan-sha v4q-on-a6ae390; gen_round_credit.py from the
credit record's byte-for-byte line, reading the flow's round-0 manifest under the out-tree): all six files byte-identical to the committed blobs, inputs digest
923503537ddd, one label across the five files that carry it. The reword checked on whitespace-flattened text with the base as the control designed to fail:
the old clause 1 at a6ae390 and 0 at df28129, the new clause 0 then 1, CONFIRMED THROUGH THE FLOW 1 in both, the old clause absent from the WP-8 plan and the
test plan. The census re-run with the committed probe at df28129 and, through --root, over an archive of 44b336e; the response rows' figures recomputed from
the retained logs at df28129 (git grep over the tracked tree, sums by python over the checker summary lines); the agent's NMI stimulus, the controller's
interrupt-take terms and the scoreboard's pre-emption rule read in the source. Landing31a read against the detector-control log and against the red-fixture
grading code at df28129. TASKS rows 1184-1185 and tb-infra's work note read for the sweep the plan cites. The DV Lead's harness and its log (gitignored work
directory, scratchpad) read but not credited. No subagent used. EXPOSURE: none beyond the Orchestrator's message, the git log subjects and the TASKS rows.
Section 6 reconciles with this range's cross-model review; its artifact was not read before Sections 1-5 were written.

CRITIC VERDICT: REQUEST-CHANGES. One Medium on v4q: the test plan states that seed variation CANNOT reach the NMI pre-emption window and the response row
infers that the window is "unreachable by seed variation rather than thinly sampled", while the TB's own agent draws the one-cycle NMI pulse in any cycle and
the retained storm-with-NMI runs carry twelve NMI entries from one distinct seed, so the zero is a thin sample stated as a structural fact. Everything else
in the range verifies: the reword, the re-keyed records, the census clause to the line, the standing-guard row's rt34 facts, landing31a's every claim. Three
Lows on figures and attributions in the same NMI paragraph and row. Landing31a carries no finding.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| a9fb2c2 (tb-infra landing31a) | Section 7 cites gen_l25_fcov_detector_control_red.log at 3691c49: the same entry, build and seed twice through gen_run differing only in the declared bin set, PASS six of six against the committed manifest, FAIL with "fcov expectation unmet: 1 declared bin(s) not hit" and exit 2 against the fixture, the simulation passing in both; a ONE-SHOT control because the fixture lives in a scratch archive and the committed manifest is untouched; the STANDING guard pending a Runtime flow change because a red fixture is graded from a collected evidence line and an fcov-unmet failure produces none; the landing-23 mutation reds kept beside it as the mutation-driven direction | the log's :5-7, :19-26, :28-32 say exactly that; gen_verdict.py:135-151 grades a red fixture RED-OK only when a collected evidence line matches red_expect and marks a passing simulation "red fixture passed unexpectedly", and gen_run.py:148-155 applies the fcov check after that verdict, turning only PASS or XFAIL into FAIL, so an fcov-unmet fixture is FAIL and never RED-OK at df28129 (rt35, out of range, is the fix); the old clause and the new paragraph diffed |
| df28129 (DV Lead v4q) | CM205-Medium-1: gen_fcov_plan.md:4957 reworded to the measured-run sense, the contradiction with :4928 gone, the figures untouched | flattened-text counts above (base 1/0, head 0/1); the paragraph at :4928 still says the nine ran through the flow |
| df28129 | the standing-guard row re-keyed: rt34 at 3691c49 exercised the failing direction (the fixture bin gen_ic_ecc_cg.cp_ram.data unhittable by the entry, FAIL with the reason string and exit 2, the committed manifest 6 of 6, the simulation passing in both, read from the log), so the guard now adds a COMMITTED PERMANENT check | every fact re-read from the log at :13-15, :21-26, :29 (tb_l29 verified the premises) |
| df28129 | the census completeness clause: the probe partitions the 158 at 44b336e into retired 32, marker 30, scope 23, guard 1 (CG-SEC-001) and other 72 across 37, so 30 + 23 + 1 + 72 = 126 actionable; 26 marker lines and zero CG-CSR-016 refusals at this tree; adjacency alone and adjacency-plus-a-bare-token select the same 30 lines across the same 14 groups | probe over the 44b336e archive: 158/65, retired 32/16, actionable 126/56, marker 30/14, scope 23/15, union 53/21, guard 1 in CG-SEC-001, other 72/37; at df28129: 154/64, 122/55, marker 26/13, scope 23/15, union 49/20, guard 1, other 72/37, no CG-CSR-016 header; the 30 marker bullets of 44b336e re-read from the joined plan: 30 match a token glued to "(" and the same 30 match a bare token inside the parentheses |
| df28129 | the four generated records re-keyed to v4q-on-a6ae390: covergroup set (58 covergroups, 4106 bins, 27 manifests, digest 923503537ddd), promotion table (test plan sha256 359bdb27d770, testlist d9526147a258), credit md and summary; the set's plan anchors shifted by two lines after :4954 (5720 to 5722, 5619 to 5621, 5885 to 5887, 6860 to 6862) and unchanged before it | six files byte-identical on regeneration; the test plan blob is 359bdb27d770493f; the reword is -2 +4 lines at :4954, so +2 for every later anchor |
| df28129 | three new response rows (the CM205 header, CM205-Medium-1, the NMI route) and the NMI route paragraph in the test plan: the counter named in 577 tracked files, 586 occurrences, zero every time; gen_tb_top.sv:174 assigns irq_nm from the IRQ agent's interface and :212 wires it into the core; no NMI knob of the described kind exists; the knob deliberately not debug_only because gen_run refuses debug_only knobs in a measured run | 577 files, 586 occurrences (581 "nmi_preempted=0" and 5 "stays 0"), 0 nonzero, faults_armed in 666 files as the control; :174 and :212 read; gen_tb_knobs.yaml carries knob_irq_line_mix with_nmi and knob_irq_regime only, no delayed-NMI knob; gen_run.py:204 "if measured and debug_only". The figures 2165, 18621, 1272, the 24-seed sweep and the rows-below clause do not verify: Section 3 |

## 2. Rows

- CM205-Medium-1 (the DV Lead's): answered as stated and verified. CM205-Low-1, Info-1 and Info-2 are Runtime's and not in this range. CR-29: none were
  open. Nothing else was owed to this range.

## 3. Findings

- M-1 (v4q; gen_test_plan.md:168 "SEED VARIATION CANNOT REACH IT" and the NMI-route response row's "So the window is unreachable by seed variation rather
  than thinly sampled"): a measured zero is stated as a structural impossibility, and the record's own numbers say the opposite. (a) The TB does not exclude
  the window: the IRQ agent draws a regime event each cycle with probability 1/irq_event_mean (gen_agents_pkg.sv:646-647; storm mean 100, gen_tb_knobs.yaml:185),
  under with_nmi includes the NMI in one event of four (:619) and pulses it for one cycle (:650 with :596, released by the countdown at :626-633), so a pulse
  can fall in any cycle, the window included; the controller takes an NMI in DECODE whenever not stalled, without a special request and with no writeback
  pending (rtl/ibex_controller.sv:498, :700-716), the condition the plan's own case needs to hold inside the window. (b) The zero rests on almost no NMI
  entries: the 19 with_nmi runs among the 577 carry about 817 one-cycle NMI pulses (sets minus regime sets from the agent's report line), 3054 interrupt
  entries and 12 NMI entries, and those 12 are one seed-1 storm run retained twelve times across landings (sets 223, regime 175, nmi 1 in each) beside
  seeds 2-6 with 225 pulses and nmi 0; so the retained evidence against pre-emption is one distinct NMI entry. tb-infra's TASKS row 1185 says the same thing
  as an observation ("a window ... the storm regime never lands in") on a local 24-seed sweep, not as a mechanism. The two structural reasons the paragraph
  gives are true and are about why the mechanism must be agent-side, not about reachability by seeds. The route decision (a targeted knob with a swept
  delay) is right either way and is not the finding. Required: state the zero as measured with the NMI-entry count it rests on, drop "cannot" and
  "unreachable rather than thinly sampled" or give the structural reason the record does not contain, and let the reachability estimate stand as the reason
  the route is targeted (about W cycles of window in 400 per pulse-bearing cycle at the storm mean, and a pulse taken in about one of seventy).
- L-1 (v4q; gen_test_plan.md:170-172 and the NMI-route row): three figures are not the record's own. "every retained log (2165 files)": the tracked
  .log files under gen_tdd_logs number 2167 at the touch's base a6ae390 and at df28129; 2165 is the count at c3bd17a, before rt34's two flow logs. "over
  18621 interrupt entries and 1272 NMI entries in those runs' own checker summaries": 18621 and 1272 are the GEN_IRQ_CHK entries= and nmi= sums over ALL
  2167 logs (740 summary lines); the 577 runs that report the counter sum to 13102 interrupt entries and 1108 NMI entries. The conclusion (zero
  pre-emptions where the counter is reported) holds over the smaller totals; state the grep and the scope.
- L-2 (v4q; gen_test_plan.md:171-172 "tb-infra's 24-seed storm sweep included"): the sweep is not among the retained logs. TASKS row 1185 and tb-infra's work
  note call it a local sweep (~4200 interrupt entries, counter zero), and the tracked storm-with-NMI set is the six-seed l7 set plus the seed-1 run repeated
  per landing; under the evidence rule an unretained sweep counts as nothing, and the sentence places it inside "every retained log".
- L-3 (v4q; gen_test_plan.md:180-181 and the row's "the Section 1.8 counted-only rows point at the entry carrying it rather than at a new directed test"):
  the two rows (:425-426, TP-IRQ-079 and TP-SEC-025) name neither an entry nor a test; their Until column reads "a run in which the local intr_now rule
  fires with nmi_preempted > 0 and the comparator stays green". True that they do not point at a directed test; false that they point at the entry, which
  does not exist yet. Say the rows will name the entry when it lands, or leave the rows as they are and drop the clause.

### Informational

- I-1: the DV Lead's harness (gen_v4q_battery.py, the CONTRADICTION PAIR kind at :322-323) and its run log (v4q_verify.log: 111 checks, eleven mutations
  each FAILED as required, restored 111/0) live in the gitignored work directory and the scratchpad; read, not credited. The plan set's generator has always
  been gitignored (its header says so), so this is the established practice and not a finding; the CM205-Medium-1 row's "the defect class now has a check"
  is a statement about that unretained tool.
- I-2: the CM205-Medium-1 row says the old clause "came from tb-infra's framing, written before rt33 existed"; the clause first appears in the tree at v4p
  (5e1bcd7) in the DV Lead's file, and tb-infra's WP-8 plan at 332aa17 carries no such sentence; the provenance is not checkable from the tree and is not
  contradicted by it.
- I-3: landing31a's statement about the grading is checked against the code at df28129 (Section 1); rt35's four files on HOLD in the shared tree change
  gen_run.py and gen_verdict.py and are not judged here.
- I-4 (for tb-infra and the DV Lead, not a finding on the range): the with_nmi one-cycle pulse yields an NMI entry about once in seventy pulses in the
  retained storm runs (12 of 817), and only one seed of six ever produced one; the knob design's swept delay is the right shape because a fixed one-cycle
  pulse is mostly not taken, which is also why the retained NMI-entry evidence under with_nmi is so thin.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty over green: NON-CONFORMING at one sentence and one clause (M-1: a zero over one
distinct NMI entry stated as "cannot" and "unreachable rather than thinly sampled") and at three figures not the record's own (L-1, L-2); conforming
elsewhere, including the CM205-Medium-1 reword, which states the measured/unmeasured distinction plainly, and landing31a, which names its control ONE-SHOT and
says what the standing guard still waits for. S6 trust triad: not exercised by this range (records only; landing31a's evidence is rt34's, verified in
tb_l29). S2: the records regenerate byte-identically from committed inputs. One-line verdict: FAIL on S4 for the NMI-route sentence; PASS elsewhere.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES on the range 2402704..df28129, for M-1 (v4q). Rows CR-30: M-1, L-1, L-2, L-3. What lifts it: the DV Lead's next plan touch
(v4r is already in the chain) rewording gen_test_plan.md:168-182 and the NMI-route response row as M-1 and L-1..L-3 state, re-reviewed as tb_l30b on that
commit; nothing built on the NMI-route statement (the knob's testlist entry, the LOG-037c lift) proceeds before then. Landing31a (a9fb2c2) carries no finding
and nothing of tb-infra's is gated by this verdict.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-2402704d-df281290.md (8e9df67b80fca6e9, 38 lines), landed 16:01:48Z and read after Sections 1-5 were
written. Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of df28129. Its verdict:
APPROVE-WITH-CHANGES with two Lows and one Info, the five rubrics PASS with no matching lines. Mine: REQUEST-CHANGES on one Medium. The two disagree on the
NMI-route sentence, below; on every shared item they agree.

Shared recomputations, each re-run by me and equal to the artifact's: landing31a's every fact against the detector-control log (entry, seed, the 813994b build,
6 of 6, the reason string, exit 2, the simulation passing in both, the scratch-root fixture, the committed manifest untouched) and against the flow at
gen_run.py:404-407 / :438, apply_fcov_check :148-155 and gen_verdict.py:135-149; the UNINITALL root of gen_fu_l23_wp8_cov_reds.log moving
cp_no_alert_case.uninitialised_data_ram from HIT (count=35, :35) to UNHIT (count=0, :53); the reword on flattened text with the CONFIRMED THROUGH THE FLOW
paragraph intact; the nine entries at measured: false and the exercising log's :8 "Unmeasured (each entry's own flag)"; "OVERTAKEN THE SAME HOUR" (5e1bcd7
11:21:16, 3691c49 11:28:44, -0400); the census at 44b336e and df28129 to every figure, the guard CG-SEC-001 cr_window, zero CG-CSR-016 refusals; the
generated records byte-identical with --plan-sha v4q-on-a6ae390 against the round-0 manifest (sha256 4c9a21df...); gen_tb_top.sv:174 and :212; no knob name
containing "nmi" in any testlist plusarg; the 577 files / 586 occurrences / 666 control; the CM205 severity word and the row id. One item the artifact
records as unverified I verified: the adjacency versus adjacency-plus-bare-token equivalence (its item 3, "not produced by the tool"), which I reproduced
from the 30 marker bullets of 44b336e re-read from the joined plan (30 match each criterion across the same 14 groups), so the row's fact stands on my
measurement as well as the DV Lead's.

The artifact's findings against mine:

- Its Low (gen_test_plan.md, "over 18621 interrupt entries and 1272 NMI entries in those runs' own checker summaries"): the same finding as my L-1, reached
  independently with the same numbers (740 summary lines over all logs; 13102 and 1108 over the 577; 5519 and 164 never checked for pre-emption). Its Info
  (the 2165 count keyed to c3bd17a, 2167 at the base and at HEAD) is the third figure of my L-1. Agreement, nothing to adopt. The artifact cites both at
  gen_test_plan.md:166, the paragraph's opening line; in the blob the figures sit at :170-171.
- Its Low (the CM205-Medium-1 row's CONTRADICTION PAIR check lives in an untracked harness, so the row's "added to my harness" and the commit title's 111
  checks and eleven mutations cannot be verified from the repository; commit the check with a --self-test or disclose the scratch class): adopted and
  verified as a miss of severity in my Sections 1-5, which carried the same fact as informational (I-1) on the ground that the plan set's generator has always
  been gitignored. The artifact's rule is the better one and the team has already applied it (compare_forms.py and read_keyed.py were named scratch-only in
  CM205-Info-2 and then committed in rt34): a record that claims a check exists names where it lives. I-1 is withdrawn as informational and the item rides
  the same v4r touch through the Orchestrator's CM207 row; no CR-30 row is added for it.
- Not in the artifact: my M-1 (the plan's "SEED VARIATION CANNOT REACH IT" and the row's "unreachable by seed variation rather than thinly sampled"), my L-2
  (the 24-seed sweep is local and not among the retained logs) and my L-3 (the Section 1.8 rows name no entry). The artifact's item 4 verified the NMI
  route's tree citations (the two wiring lines, the RVFI property, the knob's absence, the 577/586/666 figures) and did not test the reachability claim
  against the agent's stimulus or against the NMI-entry count the zero rests on; my basis is in Section 3 (gen_agents_pkg.sv:619, :646-650, :596, :626-633;
  ibex_controller.sv:498, :700-716; 817 pulses, 3054 interrupt entries, 12 NMI entries from one seed across the 19 with_nmi runs; TASKS row 1185). The two
  verdicts therefore differ on severity, not on any shared fact: the artifact did not examine the sentence M-1 is about. Under the team's gating a
  REQUEST-CHANGES stands until the recorded re-review; the Orchestrator arbitrates if the DV Lead disputes M-1.

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. Section 5 stands: REQUEST-CHANGES, rows CR-30 M-1, L-1, L-2, L-3.
