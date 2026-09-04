# Critic verdict: tb-infra landing 23, the WP-8 part-1 build (commit f0723d6, diff base 0673e0b), reviewed as tb_l23

CORRIGENDUM to gen_critic_tb_l22.md (160ea70a58186a13, committed e6803a0, frozen): its L-1 said the WP-8 plan's parenthetical counts (19 / 6, 18 / 5) and
its size (1469 bullets in 206 covergroups) "do not reproduce exactly under a plain definition" and asked for definitions. Re-probed with the renderer's header
regex verbatim (end-anchored), every figure of the plan's tables reproduces exactly at the commits it named: 1469 / 206 and 19 / 6 at 6457c71, 18 / 5 at
fa3fb77. My tb_l22 probe had used an un-anchored header pattern that admitted CG-DIT-004 while its trailing parenthetical still hid it from the renderer, hence
my 1483 / 207 and 20 / 7. The real inexactness was CM194-L-1's, the same off-by-one: v4h normalised that header at 61c1a1a, so the renderer sees 1483 / 207
there and the plan's present-tense prose was stale by one covergroup. tb_l22 L-1's diagnosis is withdrawn; tb-infra's CR-22-L-1 row states the same
mechanism and this landing anchors the figures at 61c1a1a, which answers it. Rule for me since: reproduce a tool-defined count with the tool's regexes
verbatim, and suspect the probe before the record.

Scope (the Orchestrator's): the thirteen paths of landing 23 on build w23 (sources 61da6da315ee239e): the data-RAM written flag and never-written report,
the bypass queue with its two drains and its 512 bound, the CG-IC-006 sampler with its classifiers and seventeen GEN_FCOV_UT cases, the alert_minor_o and
major level histories, the rendered group (24 coverpoint and 16 cross bins), the part-1 group manifest (15 coverpoint bins declared, 14 cross bins owed under
LOG-084), the plan, the response file (the CM194 rows, the CR-22 withdrawal, the deviations table with the copy-in protocol failure) and two retained logs.
Judged with the disclosed gate failure in view: gen_knobs_codegen.py --check STALE on gen_tb_pkg.sv and gen_ut_knobs_codegen.py 16 failures at f0723d6,
both passing at 36bc3a4; tb-infra holds and owes landing 24. This verdict also carries the reconciliation owed by tb_l22 with the landing-22 cross-model
review (Section 6).

Artifacts reviewed (committed blobs at f0723d6; sha256 first 16 hex):

- dv/auto_dv/tb/gen_icache_ram.sv  cdfbbdaa096856f8
- dv/auto_dv/tb/gen_tb_pkg.sv  1e9c6220b81b298f
- dv/auto_dv/env/gen_checkers_pkg.sv  ceae51ad2b959198
- dv/auto_dv/env/gen_fcov_pkg.sv  d4b339e24ff36ba8
- dv/auto_dv/env/gen_env_pkg.sv  4e3513eba51a9cf5
- dv/auto_dv/tb/gen_fcov_codegen.py  7ea325a7101a7984
- dv/auto_dv/env/gen_fcov_groups.svh  cd4c1f69fdfc4a30
- dv/auto_dv/fcov_expectations/gen_cg_ic_ecc_part1.fcov.yaml  e937e62c2845f05a
- dv/auto_dv/docs/gen_wp8_part1_plan.md  490f2708544eed0b
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  87b961cd55189782
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  46d00d72451f4f78
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_wp8_cov_reds.log  a7262475a6b94d00
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l23_fcov_checker_cross_bins.log  2eba4c409cafd9c5

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; LOG-084 and LOG-084a;
the DV Lead's rulings folded in gen_critic_response_plan_set_v1.md:781; rtl/ibex_icache.sv:580-585 (data ECC checked only where the tag is valid and hit,
the RTL's own comment saying unused data may have incorrect ECC), rtl/ibex_pkg.sv:401-405 (IC_NUM_WAYS 2, IC_NUM_LINES 256); the team's mutation-proof
standard (a named mutant caught with the referees inert, an ablation, the mutant build differing from the landing build in exactly the mutated file, the
applied diff retained) and the evidence rule (an unretained claim counts as nothing).
Method: detached git worktree of f0723d6 and copies of it. The landing-23 list equals the thirteen-path diff and 13 of 13 md5s verify at f0723d6. Build
w23 identity first-hand: the recipe on the tree gives 61da6da315ee239e, equal to the reds log's GREEN root, so the retained runs compiled the committed
tree, hand-edited package included. Gates on the worktree: gen_fcov_codegen --check up to date, the fcov codegen unit test PASS, CONST-CHECK PASS,
gen_knobs_codegen --check STALE gen_tb_pkg.sv and gen_ut_knobs_codegen 16 failures (reproduced). The stale section diagnosed by regenerating in a copy
holding rtl/ and ibex_configs.yaml: the generator's output differs from the committed package in exactly six lines, 248-253, the hand-written
gen_ic_in_window function and GEN_ICRAM_UNINIT_Q_DEPTH placed inside the GEN_KNOBS_BEGIN..GEN_KNOBS_END block (lines 10 to 547); every other generator
output equals its committed file. The render claim reproduced in tb_l22 (66 lines, exact prefix) holds at this commit with --check up to date. The
traceability CSV read for the LOG-084 masking argument: CG-IC-006 has 19 distinct coverpoint bin names (the record's 22 counts coverpoint-and-bin pairs) and 16 cross bin names with an empty intersection
(none), and all 15 declared bins have CSV rows. The source diffs read against the plan (the report condition, the drains, the histories, the
classifiers, the sample order); the two retained logs read whole; the response rows against the diffs. No subagent used. EXPOSURE: none beyond the
Orchestrator's message and the git log subjects. Section 7 says whether this range's cross-model artifact was read.

CRITIC VERDICT: REQUEST-CHANGES. The build is on the committed tree and the two manifest-detected reds discriminate, but (M-1) six hand-written lines
sit inside the knobs generator's rendered block, so the flow's gate fails at HEAD and the regeneration the gate demands would delete a function and a
parameter the checkers and the package use; and (M-2) of the four mutations claimed caught, two are retained without build identity or applied diffs and
two, the routing and the window arithmetic, have no retained failing run at all, and the seventeen unit-test cases have no retained in-simulation pass.
Two lows. The gate on the gen_l14 entries that would carry this build is not lifted by this verdict; landing 24 with the fix and the missing evidence is
the re-review.

## 1. What was verified

| item | as built at f0723d6 | evidence (re-derived by me) |
|---|---|---|
| build identity | w23 sources 61da6da315ee239e = the committed tree | the recipe on the worktree, 75 rows |
| the never-written report | gen_icache_ram.sv: per-line written and uninit_reported bits; written set on any write; a data read of a never-written, not-yet-reported line on a qualified cycle calls note_uninit_read once per line | the diff; consistent with the plan's Section 5 and the bound (256 lines x 2 ways = 512) |
| the bypass queue and its drains | gen_tb_pkg.sv: uq (own queue), uninit_reads / uninit_dropped, GEN_ICRAM_UNINIT_Q_DEPTH = IC_NUM_LINES x IC_NUM_WAYS, enabled_at / sweep_clear_at split from qualified_at, gen_ic_in_window; gen_checkers_pkg.sv: drain_uninit(0) after the per-cycle pass and drain_uninit(1) at report time, an event classified once its ECC window closed, skipped when an injection shared its cycle or alert_minor_o was high in the window, else sampled; minor_hi and major_hi level histories pruned to the longest window; the GEN_MISC summary extended with reads / sampled / skipped / dropped | the diffs; the GREEN run's line "reported=37 sampled=35 skipped(injection 2, alert 0) dropped=0" |
| the sampler | gen_fcov_pkg.sv: ic_no_alert_case in the plan's precedence (disabled_cache, during_invalidation, masked_duplicate_copy, unused_way_data, uninitialised_data_ram, else -1); ic_major_nmi_quiet -1 unless both levels low and a retirement seen; ic_knob_cls per RAM kind; sample() arguments in the renderer's order with -1 at positions 6, 7, 9, 11; seventeen GEN_FCOV_UT cases (seven precedence, four quiet, two routing, four window boundaries) with the routing probe restoring the queue and the counter | the diff; the order matches the rendered sample() signature reproduced in tb_l22 |
| the render | gen_fcov_codegen.py IMPLEMENTED gains CG-IC-006; gen_fcov_groups.svh +66 lines, --check up to date | the check on the worktree; the tb_l22 reproduction |
| the group manifest | 15 coverpoint bins declared, 14 cross bins under bins_owed_checker_defect with the LOG-084 reason and the measured masking argument | the yaml; the CSV: 19 distinct coverpoint bin names (22 coverpoint-and-bin pairs, the record's figure) against 16 cross bin names, intersection empty; cp_knob declares no bin |
| the two manifest-detected reds | gen_fu_l23_wp8_cov_reds.log: GREEN (61da6da315ee239e) hits cp_no_alert_case.uninitialised_data_ram at 35; UNINITALL (bf78b5c353a92660, the flag set for every line) reported=0, the bin UNHIT; UNINITDRAIN (08e1f203a788b1f5, both drains removed) reported=37 sampled=0, the bin UNHIT; the ablations remove the bin from the manifest and the bin is named 0 times; the checker exits 2 on all three because one run cannot hit all fifteen bins | the log read whole; the discrimination is the HIT-to-UNHIT transition and the statistic (M-2 on what is missing around it) |
| the LOG-084 evidence | gen_fu_l23_fcov_checker_cross_bins.log: the committed checker's parse_groups_report on a real report emits 38 keys, 0 under a cross name, and 14 cross-bin counts wearing cp_knob's name (483, 421, 904 among them) | the log; the interim ruling applied as written |
| the response rows | CM194 M-1, L-1..L-4, I-1..I-3 answered; CR-22-L-1 answered with the header-regex mechanism (agreeing with the corrigendum above); a deviations table naming the coverage wiring, the build-before-red order not followed, the window-span residual, the run script's error count, the manifest reduced to 15, the copy-in protocol failure (five compile inputs dirty in the shared tree from about 10:44Z with no window), the self-found-defect pattern, and the self-test perturbation fixed | read against the diffs; honest, and the failure is on the record the reviewers read |

## 2. Findings

### M-1 (medium) [S5 single source; S6 the flow's gate] Hand-written code inside the knobs generator's rendered block

gen_tb_pkg.sv lines 248-253 (gen_ic_in_window and GEN_ICRAM_UNINIT_Q_DEPTH) sit between the GEN_KNOBS_BEGIN marker at line 10 ("edit the yaml, not this
block") and GEN_KNOBS_END at line 547. The generator's output for this tree drops exactly those six lines (re-derived in a copy holding rtl/ and
ibex_configs.yaml; every other generator output equals its committed file), which is why gen_knobs_codegen --check reports STALE and the unit test fails
its sixteen --check cases. Regenerating, which the flow's gate requires at every landing, would delete a function the checkers call three times and a
parameter the package's own queue bound uses, so the tree would not compile after the gate's normal action. Build w23 compiled the committed file, so the
retained runs describe this tree; the fix (move the six lines below GEN_KNOBS_END, or add them to the generator's inputs) changes gen_tb_pkg.sv and so the
sources identity, and landing 24 must either re-take the evidence on the new build or state that the moved lines are byte-identical in semantics and the
w23 evidence stands with that difference named. Disclosed by the Orchestrator and held by tb-infra; recorded here as the gating item it is.

### M-2 (medium) [S6 trust triad; the evidence rule] Half of the mutation evidence is unretained and the retained half carries no identity

The landing claims four mutations caught with ablation controls. Retained: UNINITALL and UNINITDRAIN in gen_fu_l23_wp8_cov_reds.log with a build sha each
and their statistics, assembled from the roots' own files. Not retained for them: the applied mutant diff, the per-file list of the mutant build, and the
check that each differs from w23 in exactly the mutated file (the identity gate tb-infra itself committed, gen_mutant_build_identity.py, has no output here);
under the standard applied since landing 14, a mutant identified by a header sha alone is a claim. Not retained at all: the routing mutation (the
never-written event pushed into q) and the window-arithmetic mutation, both detected by GEN_FCOV_UT cases in simulation; no log shows a run on either
mutated build failing with uvm_error("GEN_FCOV_UT"), and the deviations row says the reds "are being obtained" rather than that they were. The seventeen
unit-test cases likewise have no retained in-simulation pass line on w23 (the GREEN block shows only the run verdict). What stands: the two manifest reds
discriminate as recorded. What does not: "all four mutations caught". Landing 24: retain the two routing and window catch runs with their ablations, the
four mutant diffs and per-file lists with the identity check's output, and the GREEN run's GEN_FCOV_UT summary.

### L-1 (low) [S2 usable evidence] The group manifest cannot pass any single run the flow checks

The manifest is a GROUP manifest by design (no single entry hits every part-1 bin; the checker exits 2 on the GREEN run with five declared bins unhit),
but the flow's expectation check runs per entry against that run's report. As committed, any entry naming this manifest fails its check, and no
mechanism in the tree merges the reports of several entries for one manifest. State how the fifteen bins reach a passing check (a merged report of the
named entries, split per-entry manifests, or a flow change agreed with Runtime) before the gen_l14 entries carry it.

### L-2 (low) [S4 what the bin evidences] The never-written observation covers the unchecked way

The report fires for a never-written data line read on a qualified lookup, in either way. The DUT checks data ECC only on the way whose tag is valid and
hit (rtl/ibex_icache.sv:580-585, whose own comment says unused data may have incorrect ECC), and after the reset sweep a never-written data line cannot be
the hit way (a fill writes tag and data together, an invalidation writes the tag invalid), so the sample records the DUT not alerting on data it did not
check, never a checked read of garbage ECC. That is a real RTL property (the non-hit way's ECC is masked) and worth the bin, but the RAM comment ("a
never-written data line read on a lookup the DUT checks") and the fcov plan's "the FIRST checked read of a never-written line" say more than the mechanism
can show. Say in the plan and the comment what the bin evidences; for the plan owner as much as for tb-infra.

### Informational

- I-1: the copy-in protocol failure is disclosed in the record with its cause and its inference error; the statement that nothing of Runtime's compiled
  against the dirty tree is Runtime's to confirm and should be, in its own record.
- I-2: the checker exits 2 on the GREEN run; the reds are read as the declared bin's HIT-to-UNHIT transition with the statistic localising the break. That
  reading is sound for the two retained reds (a statistic per half of the mechanism).
- I-3: the window-span residual (a call site passing the constant less one is caught by nothing this build carries) is named in the plan and the
  response; an honest residual, to be weighed by the plan owner when the group is credited.
- I-4: the build-before-red order was not followed and is stated in those words; the reds now rest on ablations of the mechanism, which is why M-2 asks
  for the retained failing runs rather than the passing ones.

## 3. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S5 single source: generated text and hand-written code share one block against the
block's own instruction (M-1). S6 trust triad: two of four mutations unretained, the retained two unidentified, the unit tests unretained (M-2); the fcov
expectation applied under LOG-084 with the hazard measured (conforming). S4 honesty: the deviations table, the copy-in failure and the residual are on the
record (conforming). One-line verdict: FAIL on M-1 and M-2 until landing 24.

## 4. Verdict

CRITIC VERDICT: REQUEST-CHANGES (M-1, M-2). Lows L-1 and L-2 with the same landing. Rows CR-23.

## 6. Reconciliation owed by tb_l22 (frozen): the cross-model review of 61c1a1a..5a24676

Read after tb_l22 was frozen: dv/auto_dv/reviews/2026-09-04-claude-diff-61c1a1ad-5a246762.md (sha256 7bf8743e7ce24d0f, 48 lines, committed 27e6482),
APPROVE-WITH-CHANGES, eight CM194 rows all on tb-infra's plan and response file. Its verification agrees with tb_l22 on the render, the tool, the response
rows and the ": values" table; verdicts agree.

- Its Low on the stale anchor (:21) is the corrigendum above: tb_l22 L-1 mis-diagnosed the same off-by-one. Answered by this landing (the figures at
  61c1a1a with the reconciliation table).
- Its Medium (Section 1 calling the whole-plan question open while the plan owner had ruled it at gen_critic_response_plan_set_v1.md:781): verified, my
  renderer-regex probe reproducing 158 non-parsing bullets across 65 covergroups (77 coverpoint in 42, 82 cross in 38, at 6457c71). Answered by this
  landing (the ruling recorded, the framing withdrawn).
- Its Lows on Section 4 (no pointer to the drains), :205 (the drain's alert_minor_o source not a record the checkers kept; verified: only a_minor_q for
  the export edge) and :360 (Section 11 inside Section 10's table): verified; answered by this landing (the pointer, the minor_hi history built, the rows
  moved).
- Its three Infos (the "is owed" wording, the CM191 key order, the build figures for this landing's reviewer): the first answered; the second the
  Orchestrator's; the third is this verdict's Section 1 and M-2.
- Verdicts agree in substance; no corrigendum to tb_l22 beyond L-1's diagnosis.

## 7. The cross-model review of this range

Not read: at hand-off dv/auto_dv/reviews/2026-09-04-claude-diff-36bc3a4c-f0723d6d.md existed as an empty, uncommitted file (0 lines, sha256 of the
empty input e3b0c44298fc1c14; `git log` names no commit for it): the review of 36bc3a4..f0723d6 was still running. Its rows are reconciled by the
Orchestrator's relay or in my next verdict, which will be the re-review of landing 24.
