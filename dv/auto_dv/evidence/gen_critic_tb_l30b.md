# Critic verdict: DV Lead plan set v4r at 2410402 (the CR-30 lift, the CM207 answers, the drain semantics sentence), reviewed as tb_l30b, the recorded re-review of tb_l30's REQUEST-CHANGES

Scope (the Orchestrator's): the one commit 2410402 (nine files: the CM207 answers with gen_record_check.py as a committed tool, the CR-30 lift with the
NMI-route paragraph rewritten as a measured zero over a thin duplicated sample and the 24-seed sweep no longer cited as a zero, the knob stated NOT YET
COMMITTED, the drain semantics sentence written from landing 32's code, the four generated records re-keyed to v4r-on-a68c021), judged by id against CR-30
M-1, L-1, L-2, L-3 and CM207 Low-1, Low-2, Info-1. It sits in the range c0db7be..2410402 with landing 32 and the superseding ruling record, which tb_l31b
judges; the CR-30 gate rests on this verdict.

Artifacts reviewed (committed blobs at 2410402; sha256 first 16 hex):

- dv/auto_dv/docs/gen_fcov_plan.md  edf8bf01bb26dafe
- dv/auto_dv/docs/gen_feature_list.md  10cdfd1a2d3240e9
- dv/auto_dv/docs/gen_test_plan.md  9c7501d286973a5f
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  fc875bcfc837ba40
- dv/auto_dv/evidence/gen_round0_covergroup_set.md  70e0ec6b1256e918
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit.md  bb3abb0895294390
- dv/auto_dv/evidence/gen_round0_credit/gen_round0_credit_summary.md  766094a7110478bd
- dv/auto_dv/evidence/gen_round0_promotion_table.md  640ddacde63f0b6c
- dv/auto_dv/tools/gen_record_check.py  7fe159eeb9cb3c7e

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l30.md (3a3d311dea84cfde, rows
CR-30) and the CM207 artifact (8e9df67b80fca6e9); the evidence rule; the honesty rule; the rule that a sentence about a record describes the record as it is.
Method: detached git worktree of 2410402 (the landing gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 27 OK, TBMAN 3469
rows 0 bad; build identity e674e6339b5bea85 unchanged, the range touching no build source). The four generated records regenerated on a full archive copy
with --plan-sha v4r-on-a68c021 and the credit record's own byte-for-byte line: all six files byte-identical, the set CSV untouched since v4q, one label
across the five files. The reword checked on whitespace-flattened text per file with a68c021 as the control (the plan at a68c021 carries every old phrase
once). The paragraph's every figure re-derived from the tracked tree at 2410402 by git grep and python over the checker summaries; its every code citation
read at the cited line. gen_record_check.py read by code path and run: --self-test seven cases PASS rc 0, the tree run one pair ok rc 0, -h rc 0. The diffs
of the response file's eight new rows read against the tree. EXPOSURE: the Orchestrator's message only. No subagent used. Section 6 reconciles with the
range's cross-model review (c0db7be..2410402, launched 17:19Z; its artifact was the wrapper's empty placeholder while Sections 1-5 were written).

CRITIC VERDICT: REQUEST-CHANGES. One Medium: the CR-30-L-3 lift adds the corrected sentence ("the Section 1.8 rows will name the entry when it exists ...
nothing in those rows points at one") without removing the sentence it corrects ("the counted-only rows below point at the entry carrying it rather than at
a new directed test"), ten lines apart in the same paragraph, so the record now asserts both halves of a contradiction while the response row says
"fixed"; the class CM205-Medium-1 named, in the touch that commits the tool built to catch it, whose pair table does not carry this pair. Everything else
verifies: CR-30 M-1 (the measured zero stated as measured, every figure and code line re-derived), L-1 and CM207 Low-2 / Info-1 (both denominators, the
count dated), L-2 (the sweep named local and unretained), CM207-Low-1 (the committed tool), the drain semantics sentence against landing 32's code, and the
records. One Low on a figure from the unretained sweep still doing work in the paragraph.

## 1. What was verified

| row | as built | evidence (re-derived by me) |
|---|---|---|
| CR-30 M-1 | the paragraph states A MEASURED ZERO OVER A THIN, DUPLICATED SAMPLE, the window NARROW and not closed, the route targeted because it makes the case deterministic; the mechanism cited: with_nmi sets the NMI line on one event in four (gen_agents_pkg.sv:619), the engine issues it as its own one-cycle command (:651), the pin at :580, the controller takes it in DECODE when unstalled (rtl/ibex_controller.sv:498, :700-716); the sample: 23 retained logs mention with_nmi, 10 distinct IRQ-checker summaries (one retained six times, another four), 3054 interrupt entries, 12 NMI entries | old phrases absent from the plan on flattened text (present once at a68c021); the three agent lines and the controller lines read; git grep at 2410402: 23 .log files (42 files in all) mention with_nmi, their GEN_IRQ_CHK summaries 19 lines of 10 distinct texts with multiplicities 6, 4, 2 and seven singles, entries 3054, nmi 12 |
| CR-30 L-1 = CM207-Low-2 / Info-1 | both denominators carried: 2167 retained log files at a6ae390 (dated), the counter in 577 files 586 times, those files' 575 summaries 13102 / 1108, every retained summary 740 for 18621 / 1272, the 165 predating summaries 5519 / 164 never checked for pre-emption | 2167 at a6ae390 (2172 at 2410402 after landing 32's five logs, which is why the date matters); 577 / 586 / 575 / 13102 / 1108 / 740 / 18621 / 1272 / 165 / 5519 / 164 all equal my sums of tb_l30 |
| CR-30 L-2 | the sweep no longer inside the retained denominator, named local and never retained; the knob NOT YET COMMITTED, built in tb-infra's tree with its hand-off waiting on tb_l30b; the one-cycle pulse constraint carried | "24-seed storm sweep included" absent from the plan; "NOT YET COMMITTED" once; the knob absent from the committed gen_tb_knobs.yaml; the sweep's own report still cited: Section 3 L-1 |
| CR-30 L-3 | a sentence added: the Section 1.8 rows will name the entry when it exists; today they name the owed evidence and nothing in them points at one | the sentence present once at :192-194; the sentence it corrects still present at :203-204: Section 3 M-1 |
| CM207-Low-1 | the CONTRADICTION PAIR check is a committed tool, dv/auto_dv/tools/gen_record_check.py: a pair table (one pair, the CM205 phrases), whitespace flattening, the exactly-one rule, a missing record failing, a seven-case --self-test; the CM205-Medium-1 row now cites the tool by path | the code read (flat(), check() with both-present and neither-present as failures, the repo root found by dv/auto_dv/contract); --self-test PASS 7 cases rc 0; the tree run "exactly one of the pair present (B)" rc 0; -h rc 0 |
| the drain semantics sentence | bound PLUS ONE with the loop at gen_env_pkg.sv:377-378 and its info line at :379; the in-run terms at gen_checkers_pkg.sv:127, :117, :132, :142, :143; the cap computed at run time by gen_irq_drain_cap_cycles (gen_tb_pkg.sv:551) with the constants 2 and 40 and the 193 default, the reason in the comment at :547-550; the evidence a pair (the false-failure seed passing, MUT-NT2 seed 3 failing with the in-run wording at order 3718, ablation passing); the retirement-stall residual OWED | every cited line read at 2410402 and saying what the sentence says (the loop's <=, the info line's "plus one", the age comparison >, the restart at entry and while masked, the delete and the break, the function and its comment); the pair and the residual as verified in tb_l31b |
| records re-keyed | v4r-on-a68c021 in the set md (digest 17bad26a1315), the promotion table (test plan sha256 9c7501d28697), the credit md and summary; the set CSV unchanged | six files byte-identical on regeneration; the CSV absent from the commit and equal to df28129's blob; the test plan blob at 2410402 begins 9c7501d28697 |

## 2. Rows

- CR-30 M-1: CLOSED. CR-30 L-1: CLOSED (with CM207 Low-2 and Info-1). CR-30 L-2: CLOSED as to the retained denominator, with L-1 below on the sweep's
  figure. CR-30 L-3: NOT CLOSED (M-1 below). CM207 Low-1, Low-2, Info-1: answered as stated and verified.

## 3. Findings

- M-1 (gen_test_plan.md:203-204 against :192-194; the CR-30-L-3 response row): the paragraph now says both "the counted-only rows below point at the
  entry carrying it rather than at a new directed test" and, ten lines earlier, "The Section 1.8 rows will name the entry when it exists (CR-30-L-3): today
  they name the owed EVIDENCE ... and the knob's entry does not exist yet, so nothing in those rows points at one". The first is the false clause CR-30-L-3
  named (the rows at :425-426 name neither an entry nor a test); the second is its correction; the record asserts both, which is the class CM205-Medium-1
  named and the class the tool committed in this same touch exists to catch, and the tool's pair table does not declare this pair. The response row says
  "fixed by stating the present tense", which describes the added sentence and not the record. Required: delete or reword the clause at :203-204 (for
  instance "and the counted-only rows below will point at the entry once it exists"), and either add the pair to gen_record_check.py or state why not.
- L-1 (gen_test_plan.md:185-188): the sweep is no longer cited as a zero, but its own summary line ("its own runs report entries=170 nmi=0") is still
  quoted and made "the stronger argument for the targeted route", so a figure from a run the paragraph itself calls never retained carries the
  precondition argument. The retained with_nmi runs say the same thing and are citable: seeds 2-6 of the landing-7 storm set report nmi=0 at 167 to 192
  interrupt entries each, and the whole retained with_nmi sample carries 12 NMI entries in 3054. Cite those for the argument and keep the sweep as
  unretained context, or drop its figure.

### Informational

- I-1: the one-cycle pulse constraint ("a held or two-cycle NMI re-enters the handler on its first instruction and double-faults at boot") is stated as
  tb-infra's measurement and is unretained; the RTL's nmi_mode gating (ibex_controller.sv:498, :736) makes a held line re-enter after the handler's mret,
  so the constraint is plausible, and it should arrive with its evidence when the knob lands.
- I-2: the DV Lead's harness figures in the commit message (153 checks, fourteen mutations) remain unretained; the committed tool carries one pair. Not a
  finding: the row now cites the tool and not the harness.
- I-3: the CR-30-M-1 row's "the Critic's count" (one seed-1 run retained twelve times) and the plan's re-derivation (23 logs, 10 distinct summaries, one six
  times and another four) count different things (files carrying the counter versus logs mentioning the knob value) and agree on the substance: 12 NMI
  entries in 3054, from a handful of distinct runs.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the NMI-route paragraph now states the zero as measured with its denominators
and its duplication (conforming), the drain sentence describes the built code with its residual owed (conforming), the sweep's unretained figure still does
argument work (L-1), and the paragraph contradicts itself on the Section 1.8 rows (M-1, non-conforming). S6: not exercised (records and one tool with its
self-test). One-line verdict: FAIL on S4 at :203-204; PASS elsewhere.

## 5. Verdict

CRITIC VERDICT: REQUEST-CHANGES on v4r (2410402) as the re-review of tb_l30's REQUEST-CHANGES: CR-30 M-1, L-1 and L-2 are lifted; CR-30 L-3 is not, and the
attempt leaves the record self-contradictory. Rows CR-30b: M-1, L-1. What lifts it: the DV Lead's next plan touch (v4s) removing or rewording the clause at
gen_test_plan.md:203-204 and citing retained runs for the precondition argument, re-reviewed as tb_l30c on that commit. The CR-30 gate therefore stands as
recorded: nothing built on the NMI-route statement proceeds before then; the drain semantics sentence and the CM207 answers are not gated.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-c0db7be8-24104029.md (a98196fd4ee0f76a, 54 lines), read after Sections 1-5 of this file and of its
companion were written (it was the wrapper's empty placeholder while they were; it covers the whole range c0db7be..2410402, so tb_l31b and tb_l30b
reconcile against this one artifact). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of
2410402. Its verdict: APPROVE-WITH-CHANGES with three Lows and two Infos, the five rubrics PASS. Mine on v4r: REQUEST-CHANGES. The verdicts differ on one item the artifact did not examine, and agree on every shared fact.

Shared recomputations, each re-run by me and equal to the artifact's: gen_record_check.py's tree run (1 pair, 0 problems, exit 0) and its seven self-test
cases with both failure directions and the flattening; the sample counts (2165 / 2167 / 2172 .log files at c3bd17a / a6ae390 / HEAD; 586 in 577 files, all
zero; 740 summaries 18621 / 1272; 575 summaries 13102 / 1108; 23 with_nmi logs, 10 distinct summaries with multiplicities 6, 4, 2, 3054 entries, 12 NMI
entries); every plan citation (gen_env_pkg.sv:377-379, gen_checkers_pkg.sv:117 / :127 / :132 / :142 / :143, gen_tb_pkg.sv:547-551, gen_agents_pkg.sv:580 /
:619 / :651, ibex_controller.sv:498 / :700-716); the sweep no longer cited as a zero; the four records byte-identical from the byte-for-byte invocations,
the set CSV last changed at v4q, the test plan prefix 9c7501d28697 in the promotion header; the response rows' severity words and the CR-30 ids against
gen_critic_tb_l30.md.

The artifact's findings against mine:

- Its Low (gen_tb_pkg.sv:556, the cap sized over the record bound while the drain waits bound plus one, "the plan's semantics sentence repeats 'times the
  record bound'"): a miss of tb_l30b, adopted and verified. My Section 1 checked the drain sentence against the code line by line and found them equal,
  which they are; neither the code nor the sentence sizes the cap for the 18th record, so the sentence inherits the code's factor. The plan sentence and
  the 193 figure change with the code, through landing 33 and the DV Lead's next touch; the CM209 row carries it and no CR-30b row is added.
- Its Lows on the wave log's figures and on wit/l31a, and its Info on the fixture: tb-infra's and rtl-arch's items, reconciled in tb_l31b's Section 6.
- Its Info (the pair table holds one pair; add pairs as new classes are found): agreement, and it is the point of my M-1's second half: the record the tool
  guards acquired a second contradiction in this very touch (the two clauses about the Section 1.8 rows), and the table does not declare it.
- Not in the artifact: my M-1 (gen_test_plan.md:203-204 against :192-194, both clauses standing in one paragraph, the CR-30-L-3 row saying "fixed") and my
  L-1 (the unretained sweep's "entries=170 nmi=0" still carrying the precondition argument). The artifact verified that the sweep is no longer cited as a
  zero and that the plan's citations resolve; it did not test the L-3 lift against the clause it was meant to replace. The Orchestrator confirmed on the
  tree that both clauses stand. The verdicts therefore differ on an item only one of us examined, not on a shared fact; under the team's gating my
  REQUEST-CHANGES stands until the recorded re-review (tb_l30c on v4s).

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. One miss adopted (the cap's factor, owed through CM209-Low-1). Section 5 stands:
REQUEST-CHANGES on v4r, rows CR-30b M-1 and L-1, the CR-30 gate as recorded.
