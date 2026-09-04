# Critic verdict: landing 39 (726682a, tb-infra-2: the icache-ECC tag-half end-of-run allowance re-keyed on observability), the recorded re-review of CR-35 M-1, reviewed as tb_l36

Scope (the Orchestrator's): one commit, 726682a, five files (gen_checkers_pkg.sv re-keyed; gen_fu_l39_tag_eor_observability.log; gen_fu_l37_tag_eor_corrigendum.log;
two manifest rows; the gen_tdd_step2b.md section), judged as the re-review of tb_l35's REQUEST-CHANGES (CR-35 M-1) and of the corrigendum answers to CR-35 L-1
and L-3, with CR-35 L-2 (the mutation diff as a file) judged for whether it blocks. The round-1 dispatch waits on this verdict, so Sections 1-5 are handed as
soon as written; the cross-model review of df1d8c5..726682a (launched 20:14Z) is reconciled in Section 6 when its artifact lands, by corrigendum if that is
after this file is committed.

Artifacts reviewed (committed blobs at 726682a; sha256 first 16 hex):

- dv/auto_dv/env/gen_checkers_pkg.sv @726682a  3d45837727fb8708
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l39_tag_eor_observability.log @726682a  45947e56e63003b5
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l37_tag_eor_corrigendum.log @726682a  cdb06875985b3807
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md @726682a  288eaf536628895f
- dv/auto_dv/evidence/gen_tdd_step2b.md @726682a  f126ada907782e63

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l35.md (9f05a5dc05f52c11,
committed 3cabc7e) whose M-1 named the required fix: the log's DUT statements corrected by corrigendum, the allowance re-keyed on the condition it names with the
code comment corrected, the failing seed and side B re-run, and a red the old predicate would have excused failing under the new one; the RTL-facts rule; the
retained-header rule; the mutation-proof standard.
Method: detached git worktree of 726682a (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK PASS, validate 28 OK, TBMAN 3482 rows 0
bad; flow build identity bc0cd7778e382b13 over 117 sources for gen_tb, 273622bb3b90ed9d over 95 for the smoke builds; my TB-source recipe over the committed
sources 18c7a44b8edfefc4). The re-keyed rule read against the counter it consults (gen_misc_if.sv:12-13) and the in-run judging rule (gen_checkers_pkg.sv:520);
every figure of both retained logs re-derived from the committed blobs and from tb-infra-2's roots tagfix39_root and tagmut39_root (read on disk); the digests
re-derived by my recipe over the committed sources and over the committed sources with the retained mutant applied. A PROBE RUN of my own on a scratch copy of
726682a: two $display lines in gen_misc_monitor::report_phase and nothing else (diff retained at scratchpad l36/probe39.diff, sha256 f96200e8f46c9668, 13
lines; compile digest 5c27393eec53d9ed; stdout at scratchpad l36/probe39_stdout.log), printing misc.cycle at report_phase and every qualified unseen tag
injection with its window end; the run reproduces the landing's figures for the failing seed exactly (906 / 894 / 0 / 1, UVM_ERROR 0). The tag alert latency
read from the pulse-latency histogram of every retained run and of the landing's roots. EXPOSURE: the Orchestrator's messages (including its identity figure
bc0cd7778e382b13, re-derived here); tb-infra-2's roots; the landing's own logs (read after my prep notes were written from the code and the RTL). No subagent
used.

CRITIC VERDICT: APPROVE. CR-35 M-1 is lifted: the allowance is now keyed on observability (the injection's alert window against the last observed cycle), the
DUT statement is corrected in the code comment and by corrigendum with the RTL chain quoted at first hand, the in-run deferral is gone, the counter is renamed,
and the two-sided red is re-run on builds whose digests equal the committed sources. CR-35 L-1 and L-3 are answered by the corrigendum log. Owed and disclosed,
none blocking: CR-35 L-2 (the mutation diff as a file) is not in this landing; the discriminating red M-1 asked for (an injection the old predicate would have
excused and the new one fails) was not run, the new rule being verified here by reading and by my report-phase measurement instead (CR-36 L-2); and the
report-phase predicate is off by one at the boundary against the in-run rule, with no measured exposure while the tag alert latency is one cycle (CR-36 L-1).
The REQUEST-CHANGES of tb_l35 no longer gates progress built on the tag-half allowance.

## 1. What was verified

| item | evidence (re-derived by me) |
|---|---|
| the rule as committed: close_owed keeps only the judged/closed and held_in_window continues (:740-741); at report_phase a qualified unseen tag injection is UNOBSERVABLE iff q[i].cycle + GEN_ICACHE_ECC_WINDOW > misc.cycle (:749-751), else missing with the uvm_error (:752-756); landing 37's in-run deferral removed; the counter and the GEN_MISC token renamed unconsumed -> unobservable (:343, :751, :782-783); the comment quotes rtl/ibex_icache.sv:585 and lookup_valid_ic1 | the diff read line by line against bc4eba8; misc.cycle is gen_misc_if.sv:12-13's posedge counter (the RAM models' announce cycle has the same definition), so at report_phase it reads one past the last posedge's pre-increment value: my probe prints misc_cycle=21480 with the last export event at cycle 21479; in-run the branch cannot fire because an injection is judged only when misc.cycle > cycle + GEN_ICACHE_ECC_WINDOW (:520, in the posedge loop), which makes cycle + WINDOW > misc.cycle false at every in-run close_owed(0) |
| the failing seed under the new rule: the injection at 21479 unobservable, PASS 0 errors | my probe: CPROBE_UNSEEN cycle=21479 judged=0 window_end=21481 against misc_cycle=21480, so unobservable; 906 / 894 / 0 / 1, UVM_ERROR 0, the same figures as tagfix39_root/out/fixed and out/t508609593 |
| side A: seed 508609593 PASS 906/894/0/1, seed 1 PASS 944/935/0/0; side B: MUT-ALERTSUP FAIL 875 first at cycle 862 way 1 index 25 with unobservable 1, ablation PASS 0 with unobservable 1; digests 18c7a44b8edfefc4 (side A) and 0ff5f8f3545f6de9 (side B) | tagfix39_root: fixed 906/894/0/1, ctrl 944/935/0/0, t1..t5 all unobservable 0, every header digest 18c7a44b8edfefc4 = my recipe over the COMMITTED 726682a sources (so the green ran on the landed bytes); tagmut39_root: mut 875 first at 862, abl 0, both 0ff5f8f3545f6de9 = my recipe over 726682a with gen_tb_top.sv replaced by the retained mutant 85b50e1343c65af1 (baseline 736a8d8099339024 = the committed blob) |
| gen_fu_l37_tag_eor_corrigendum.log: part 1 the DUT statement corrected with :585, :578-582, :470, :266, :262, :644 and ibex_core.sv:1337 quoted; part 2 (CR-35 L-1, CM213-Low-2) the side-A and side-B roots and digests 50981c82f49d7574 and 46f6e1dfdddebb10 with the closing claim scoped; part 3 (CR-35 L-3, CM213-Low-1) the supplement's counts pinned to df1d8c5 as 24 / 2 own / 20 logs / 2 prose (tb_l34, step2b) with the cause named (a dirty-tree count) | every RTL line re-read at HEAD (rtl/ unchanged in the range); 50981c82f49d7574 = my recipe over bc4eba8 and 46f6e1dfdddebb10 = my recipe over the landing-37 mutated root (tb_l35); 24 / 2 / 20 / 2 = my git grep at df1d8c5 (tb_l35 L-3); parts 2 and 3 print their commands |
| gen_fu_l39_tag_eor_observability.log: the RTL chain, both directions of the proxy's failure, the re-run figures, the two digests, the mutant identity | as above; the log's closing line claims "the command printed above it" while its blocks paste run summaries without commands (see L-3) |
| two manifest rows | gen_fu_l37_tag_eor_corrigendum.log 6347 / 467980032e371c2e, gen_fu_l39_tag_eor_observability.log 4508 / 9e6709609ef297f6: sizes and md5s equal the blobs; TBMAN 3482 rows 0 bad |
| gen_tdd_step2b.md landing-39 section | consistent with the code and the logs; states the lesson (a two-sided red cannot catch a right outcome with a wrong reason) |
| the alert latency the boundary depends on | pulse-latency histograms: every retained run with tag injections (ecc injections judged > 0) shows index 1 only; the only histograms with a latency-2 count are the four l16 DATAWAY excerpts, whose runs carry zero tag injections (data-injection pulses); the landing's roots read {0, N, 0} in all ten runs |

## 2. Rows

- CR-35 M-1: LIFTED (this verdict). CR-35 L-1: answered by the corrigendum's part 2 (roots, digests, the closing claim scoped). CR-35 L-3: answered by part 3.
  CR-35 L-2: NOT in this landing; carried as owed (Low), not blocking (see Section 3). CM213-Low-1/Low-2 (= my L-3 / L-1): answered by the same corrigendum.
- Rows raised here: CR-36 L-1, CR-36 L-2, CR-36 L-3 (all tb-infra-2, all owed with the next touch of the landing-37 family).

## 3. Findings

- L-1 (gen_checkers_pkg.sv:750; the boundary): the report-phase predicate treats an injection at the second-to-last observed posedge as fully observable.
  Measured: at report_phase misc.cycle = L + 1 where L is the last posedge's pre-increment count (21480 for L = 21479 on the failing seed); an injection at
  cycle L has window end L + 2 > L + 1 (unobservable, correct); an injection at L - 1 has window end L + 1, not greater than L + 1, so it is judged, though
  the window's second posedge (pre-increment L + 1) never occurred and only a latency-1 alert could have been observed. The in-run rule (:520) judges only
  when misc.cycle > cycle + GEN_ICACHE_ECC_WINDOW, so the two rules disagree by one at the end of a run. Exposure: none measured, since every retained run
  with tag injections shows alert latency 1 only (the latency-2 pulses in the four DATAWAY excerpts are data-injection pulses in runs with zero tag
  injections), but the window constant is 2 and a latency-2 tag alert at the boundary would be a false FAIL, the class landing 37 set out to remove. Fix:
  mirror :520 (unobservable iff not misc.cycle > cycle + GEN_ICACHE_ECC_WINDOW) and re-run the same red set. Low, owed.
- L-2 (the discriminating red): M-1 asked for a red the old predicate would have excused and the new one fails (a qualified injection after the last
  retirement whose window closes inside the run, alert withheld). Not run; side B fires the missing path under both predicates and side A shows only the
  positive unobservable case. The new rule is verified here by reading (:520, :749-751, the counter definitions) and by my report-phase measurement, which
  is why this is a Low and not a block; the red is still owed, a unit-level or fixture red would do. Low, owed.
- L-3 (gen_fu_l39_tag_eor_observability.log:56): the closing line claims every figure is read "by the command printed above it" while the log prints no
  command; the same overclaim the corrigendum landing alongside it scopes for the landing-37 log (CM212-Low-2, CM213-Low-2). Corrigendum row. Low, owed.
- CR-35 L-2, carried: the MUT-ALERTSUP applied diff is still retained only as two hashes and a prose description; the mutated root on disk and my
  re-derivation (three lines in gen_tb_top.sv) identify it, so it does not block, but the retention convention stands. Low, owed.

### Informational

- I-1: gen_icache_ecc_figures.py TAG_RE still matches the widened GEN_MISC line and reads no unobservable figure (tb_l35 I-1, still open).
- I-2: the round-1 consequence stated in tb_l35 Section 5 is now moot for the masking direction: a genuine missing alert after a run's last retirement is
  judged unless its window reaches past the last observed cycle; what remains is the L-1 boundary in the other direction, with no measured exposure.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S3 intent-derived checking: the allowance now derives from the RTL's own gating term
(lookup_valid_ic1 alone) and from what the run can observe (conforming; one boundary inconsistency, L-1). S4 honesty: the corrigendum states what landing 37
got wrong in the author's own words and why a two-sided red could not catch it; the unmeasured items (the discriminating red, the mutation diff) are named here
rather than implied (conforming). S6 trust triad: the red is two-sided with an ablation on builds equal to the committed sources (conforming); the
predicate-discriminating red is owed (L-2). One-line verdict: PASS, three Lows owed.

## 5. Verdict

CRITIC VERDICT: APPROVE on 726682a (landing 39). CR-35 M-1 lifted; CR-35 L-1 and L-3 answered; CR-35 L-2 carried as owed. Rows CR-36 L-1, L-2, L-3 (tb-infra-2),
all Low and all owed with the next touch of the landing-37 family, none gating. The REQUEST-CHANGES recorded in tb_l35 no longer gates progress built on the
tag-half allowance; nothing of mine gates the round-1 dispatch.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-df1d8c53-726682a0.md, committed e641b24, blob f20a5ccbff7fa13c, 51 lines, verdict APPROVE-WITH-CHANGES,
with the re-review statement that landing 39 resolves the substance of CR-35 M-1 and lifts the REQUEST-CHANGES. Reviewer identity as its header states: the
Claude fallback (claude CLI 2.1.261, run-reported model claude-fable-5-1 with claude-haiku-4-5-20251001, requested effort high, a fresh session on a detached
read-only checkout of 726682a; codex unavailable on the spend cap; owner ruling A-001). Five rubrics PASS. Its range is df1d8c5..726682a (six commits, 10
files, 539 insertions, 11 deletions, nothing under rtl/; re-derived), wider than this verdict's named scope of 726682a alone. Read after Sections 1-5 were
written; nothing above was changed on reading it.

Agreements:

- Its re-review statement agrees with Section 5 point for point: the premise corrected against the RTL, the predicate re-keyed on observability, the in-run
  allowance impossible by construction, the red re-run on the landed bytes (its recipe over the committed 726682a sources gives 18c7a44b8edfefc4 as mine
  does), L-1 and L-3 answered, L-2 and the discriminating red open.
- Its Low-1 is my L-3 (the l39 log's line-56 claim with no command in the file). Its Low-2 is CR-35 L-2 carried, with one difference of fact worth
  stating: it could not reproduce side B's digest 0ff5f8f3545f6de9 from the committed tree; I reproduced it from the author's mutated root on disk applied
  to the committed sources (Section 1), which is why the retention gap is a Low and not a break in the evidence. Its Low-3 is my L-2 (the discriminating
  red), with the addition, adopted, that the log and the step2b section should say the run was not done and why the failing seed cannot produce it.
- Its code readings match Section 1: :520 judges only after the window, close_owed(0) runs in the same iteration with misc.cycle unchanged, the
  uvm_error branch is untouched, the five deleted lines are landing 37's in-run continue and the old predicate, TAG_RE still matches (I-1).

Adopted and verified, outside this verdict's named scope and recorded for the next range's verdict:

- Its Low-4 on landing 38 (9baf3f9; gen_ut_intg_store.py:67 at 9baf3f9, the artifact cites :66): the quiesce loop breaks on a single-instant equality of the two counts, so a genuine
  one-record skip (consumed one behind) coinciding with a record in flight (consumed one ahead) reads as equality and the assertion passes. Verified by
  reading the committed loop (break when evt_retired_count == evt_isa_records, sampled once per cycle up to QUIESCE_CYCLES); non-convergence still fails as
  the landing says, transient convergence does not. Landing 38 was not named for tb_l36; the finding is adopted for its verdict, together with my own
  landing-38 note (the log's single digest 50981c82f49d7574 is the pre-fix tree's, the recipe over 9baf3f9 being 034f4e4f2905cb72, which the artifact reads
  as consistent and I read as a figure to be stated beside the other).
- Its Info-1 (a stray preamble sentence above the TARGET line in the e89d01f artifact): cosmetic, the wrapper's.

Missed by the artifact, standing here: my L-1, the boundary off-by-one of the report-phase predicate against the in-run rule (an injection at the
second-to-last observed posedge judged with only its first window posedge observed). The artifact verified the in-run direction and the failing seed's
case; it did not test the boundary. L-1 stands on the measurement in Section 3 (misc.cycle = 21480 at report_phase for a last posedge of 21479) and is a
Low with no measured exposure.

Corrigenda to Sections 1-5: none; nothing above was found false. Rows after reconciliation: CR-36 L-1, L-2, L-3, CR-35 L-2 carried; the two verdicts
agree that CR-35 M-1 is lifted. CRITIC VERDICT: APPROVE, unchanged.
