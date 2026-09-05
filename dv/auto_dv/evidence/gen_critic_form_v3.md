# Critic verdict: the round-2 request form v3 and v3.1, e95a4c9..64a4ac9 (DV Lead)

Artifacts (the two commits of the range; sha256 first 16 hex of each blob at 64a4ac9, with the v3 blob at 242a64b in brackets):
- dv/auto_dv/evidence/gen_round2_request.md 224dda7458cbd818 (v3: 37f1f13ae89d67d7)
- dv/auto_dv/tools/gen_round_form_check.py ac8594d7b60583d8 (v3: 42a19dfa29ea0380)

Date: 2026-09-05 (UTC). Role: Critic. Method: the checker run by me on a detached archive of 64a4ac9 from the archive root and
from a foreign working directory, its self-test run, and the v3 checker (the unfixed path) run from a foreign directory
against the same form to reproduce the red; the form's derivations checked against the records they rest on (the wave census
and index at 1fb417f, the PMP step-1b block at 2956a8a, the checker-fix re-run block at 69eb33f, my own re-verdicts) and the
promotion-condition statuses against the commit order. Exposure: the Orchestrator's range message named rev65's outcome
(three Mediums, seven Lows) and the v3.1 commit message describes the rows it answers; rev65's content (edbe821) is read
only in Section 6; rev68, running on 5af8269..64a4ac9, is not read. Logs: dv/auto_dv/work/critic/form3/.

CRITIC VERDICT: APPROVE (two Lows owed as disclosed; no Medium).

## 1. What the form is and how it was checked

v3 restates Section 1 from a selector call at 9c28944 (smoke 17 entries / 47 runs / 39 measured; targeted 3 / 9 / 6; the plan
20 / 56 / 45), fills Section 7 with fifteen measured entries (three seeds each, 3171 declared bins, every covergroup built, an
expected fcov verdict per row) and five unmeasured ones, and records the irq entry's six promotion conditions with a status
each; its checker grows to 203 claims by recomputing Section 1 and Section 7 through the flow's own select_tests,
seeds_for_test and validate_manifest. v3.1 fixes the checker's manifest path (repository root rather than the process
working directory), adds a control that runs the whole check from a temporary directory, adds three controls for the
seventy selection claims, reads the restatement's commit out of the form, and corrects the form's own text under its
Section 0 rule (a block is evidence for what it measured).

## 2. The checker

On my archive of 64a4ac9: `gen_round_form_check.py` PASS, 203 claims compared and all reproduce, from the archive root and
from /tmp alike; `--self-test` passes ten cases, the seven pre-existing ones, the three new selection controls (a wrong
Section 7 declared count, a dropped Section 7 row, a wrong restated plan run count, each failing as it should) and the
working-directory control (0 failures from a temporary directory). The red is real and exact: the v3 checker (blob
42a19dfa29ea0380, the unfixed path) run from /tmp against the same form reads "FAIL, 16 claim(s) did not reproduce", the
number the commit message states, and PASS from the root, so the v3 verdict depended on where it was invoked and the v3.1
one does not. The tier labels are read from the form's own "THE ROUND'S PLAN AT <commit>" row, so a later restatement is
checked rather than skipped.

## 3. Section 7 and the narrowing under the Section 0 rule

The fifteen rows reproduce through the checker (seeds, declared, built, covergroups). "No entry expects a failure" is stated
as a claim the round tests, which is the honest form. The v3.1 narrowing of "nine measured over forty fresh seeds" is right in
both figures and half right in one reason: gen_test_bit_ratified's 654 are 617 measured in the wave plus 37 declared from the
pair-fix block on a different generator, exactly as my generator-fixes re-verdict (gen_critic_genfix.md Section 7) has it;
gen_test_pmp_csr_warl's "produced a program at all forty seeds and one run refused its coverage, so its measurement is 39 of
40" describes the wave correctly (gen_wave_4017573/gen_index.md:32: 40 runs, 39 PASS, one refused on
cr_hi_mode.bit30_napot at 39 of 40), but that bin left the declared set at 9c28944, so against the manifest Section 7 names
(178 bins) every wave run passes; and "the figure its provisional status cleared on" points at the wrong measurement: the
provisional PMP entries cleared on the step-1b block (gen_pmp_measurement/gen_index.md:34-37, 86-87), whose csr_warl
denominator is 39 because seed 230969025 produced no program at all, not because a run refused (L-1).

## 4. The six conditions against the tree

- (a) "checker half fixed at b9e5fad ... the Critic's re-verdict pending": my re-verdict was committed at 5af8269, an
  ancestor of 64a4ac9 (08:30 against 08:35 local), so the status was already stale when v3.1 was committed; it now reads
  delivered, M-1 and M-2 closed, the one records sentence closed by landing 56 at fab8a61 (L-2).
- (b) REOPENED, rightly, under the form's own rule; my irq re-verdict Section 7 measured RED-OK at seed 1038372995 on a
  b9e5fad build (the designed fire alone, zero checker fires), which supports the re-run and does not replace the record of
  all three seeds that (b) asks for.
- (c) "fixed at 6b894ab, re-review pending": correct at the commit; my APPROVE was committed at ba189fe, after v3.1.
- (d) open: correct.
- (e) open and LOAD-BEARING: correct, and now measured rather than argued: my irq re-verdict's M-3 and landing 56's companion
  (fab8a61) establish that the storm-shape vacuity survives landing 54 through the entry restart, so the end-of-test
  expectation is the only thing that closes it.
- (f) open; the form's 6447 is exact (15737500 - 9290500 = 6447000 ps at 1000 ps a cycle) and the two chkfix records that
  say "about 6443" are the ones owed the one-line corrigendum the form names.

## 5. Records, conformance, rows, verdict

Section 3.5 now says its seed table is a request and not the plan, with the consequence spelled out (twelve-seed runs
against three-seed rows would fail Section 7); Section 7 derives which eleven entries are capped at forty and which four at
three; the directory holds 27 manifests as v3.1 says; the two open items (the hart_id plusargs, the coverage criterion) are
named as not claimed. Both files are ASCII. Conformance (dv_principles.md): every figure in the form is derived by calling
the flow and re-derivable by its checker, the checker has a red that fires the defect it fixes, and the form claims no
outcome it has not measured.

- L-1 (Low, records; DV Lead). The csr_warl sentence: name the wave as the measurement it describes, say the refused bin has
  since left the declared set, and attribute the provisional clearing to the step-1b block and its no-program seed.
- L-2 (Low, records; DV Lead). Condition (a)'s status was stale at the form's own commit; restate it from 5af8269 and fab8a61.

Verdict: CRITIC VERDICT: APPROVE on e95a4c9..64a4ac9. The checker reproduces all 203 claims from any working directory and
its red is the sixteen failures claimed; Section 7 and the conditions hold against the tree with the two record corrections
above owed. The form gates round-2 dispatch on conditions it states correctly; the irq entry stays unmeasured as it says.

## 6. Reconciliation with the cross-model artifact rev65

Read after Sections 1-5 were written: dv/auto_dv/reviews/2026-09-05-claude-diff-e95a4c99-242a64b1.md at edbe821 (claude CLI
fallback under A-001; APPROVE-WITH-CHANGES on v3, 242a64b; three Mediums, seven Lows). rev65 reviewed v3 alone; the range I
judge ends at v3.1, which answers it, so the reconciliation is against v3.1's answers.

- Its Medium 1 (validate_manifest opening the testlist's repo-relative path against the process working directory) is fixed
  at 64a4ac9 (the path resolves against the repository root) and my Section 2 reproduces its red exactly: the v3 checker
  from /tmp fails sixteen claims, the v3.1 checker passes from anywhere.
- Its Medium 2 (no self-test control for the seventy selection claims) is fixed: three selection controls and the
  working-directory control are in the self-test and each fails as it should (Section 2).
- Its Medium 3 (Section 3.5 asking twelve seeds while Section 7 states three) is fixed by v3.1's request-versus-plan
  paragraphs, which say what applying the request without the testlist touch would do and that Section 7 is restated from
  a fresh selector call if it lands (Section 5).
- Its seven Lows are all answered in v3.1: "five" is "six"; the 6447 figure is kept as the re-derived one with a corrigendum
  owed on the "about 6443" records (Section 4, (f)); the "nine over forty fresh seeds" sentence is narrowed under the
  Section 0 rule, on which my L-1 adds the csr_warl attribution; the antecedent is repaired; the hart_id plusargs are named
  as an open item; the tier labels are read from the form; the manifest count reads 27. Its closing note that no flow tool
  reads the form, so Section 11's "does NOT claim the functional gate" cannot be misread by a gate, is right and matches
  gen_flow_const.py's GROUP_CELL selector note in the rt39 range.
- Nothing in rev65 bears on my two Lows, which are v3.1 text: L-1 (the csr_warl sentence's attribution) and L-2 (condition (a)
  stale at the commit). rev68, running on 5af8269..64a4ac9, will see v3.1 itself; I have not read it.
- Verdict unchanged: APPROVE on e95a4c9..64a4ac9; L-1 and L-2 owed as disclosed. rev65 and this file agree there is no Major,
  and its three Mediums are closed by v3.1.
