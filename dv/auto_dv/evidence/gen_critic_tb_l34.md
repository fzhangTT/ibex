# Critic verdict: the range b105c09..1deec4c (the LOG-085 corrigendum 734417a, the round-1 pmc detach 92c0850, tb-infra-2's landing 36 1deec4c; b9bc640 and 102c17b committed as written), reviewed as tb_l34

Scope (the Orchestrator's): three working commits judged together: 734417a (the LOG-085 corrigendum on the staged-guard counts, CM211-Low-3), 92c0850
(round-1 gating by the Test Writer and runtime-2: gen_test_pmc_ctrl's fcov_expectation_file detached for round 1 with the reason in its description, the
committed manifest untouched, the R1-DRY-1 response row) and 1deec4c (tb-infra-2's landing 36: the debug-request driver livelock fixed by releasing the
UNTIL_DEBUG_MODE hold on the debug-mode LEVEL published from the scoreboard instead of the entry-edge toggle, seven files, the retained log
gen_fu_l36_dbg_driver_livelock.log). The commits b9bc640 (the cross-model review of the previous range) and 102c17b (tb_l33) are artifacts committed as
written. The range closed at 1deec4c; its review launched at 19:11:55Z.

Artifacts reviewed (committed blobs at each commit; sha256 first 16 hex):

- dv/auto_dv/docs/gen_intervention_log.md  8efd6f969b4c0690
- dv/auto_dv/evidence/gen_critic_response_batch3.md  615c5acce61322f1
- dv/auto_dv/flow/gen_testlist.yaml  203732c47eb26fe7
- dv/auto_dv/docs/gen_component_api_dbg_agent.md  04400750984897ba
- dv/auto_dv/env/gen_agents_pkg.sv  217c3910142dd3a0
- dv/auto_dv/env/gen_rvfi_pkg.sv  f41f8c8cde61b5ad
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  783a77bd759aba3e
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l36_dbg_driver_livelock.log  20e158a533e410c5
- dv/auto_dv/evidence/gen_tdd_step2b.md  863677f07f75e060
- dv/auto_dv/tb/gen_bridge_if.sv  16aa4c868f79fbb2

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l33.md (e22083fa8241dd1c); the
CM211 artifact (da7f548279e8f151) whose Low-3 the corrigendum answers; the retained-header rule (a header names the build it claims and the run it quotes);
the RTL-facts rule applied to TB mechanisms (every gating term quoted); LOG-085 (round-1 gating).
Method: detached git worktree of 1deec4c (the gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 28 OK, TBMAN 3475 rows 0 bad;
build identity 804995dc55125148 over 117 sources, the TB sources having changed). The pmc detach checked against the committed manifest (204 bins over eight
covergroups, none defined in gen_fcov_groups.svh), the checker's one classification rule, the entry's measured flag through the testlist, and the round-1
dry-run manifest under the out-tree (our flow's output). Landing 36's mechanism read in the diffs term by term; its figures checked against the runs I could
locate: the dry run's LSF run in the out-tree and tb-infra-2's fixed-driver root in the shared scratchpad (drv_root/out: the fixed seed and the seed-1 control,
both run headers and the compile log), plus the retained logs that carry the "before" counters; my TB-source recipe computed over the committed 1deec4c and
962d31f sources. EXPOSURE: the Orchestrator's messages; tb-infra-2's scratch root (read on disk); the out-tree dry-run records. No subagent used. Section 6
reconciles with the range's cross-model review when its artifact lands (none exists yet).

CRITIC VERDICT: APPROVE. The corrigendum states the committed counts; the pmc detach is the right round-1 gating for a manifest whose eight covergroups are
not built (its premises hold to the bin); the livelock fix is a genuine defect traced with every gating term, the fixed root's build equals the committed
sources by my recipe, and the request-equals-release counters reproduce from the runs and the retained logs. One Low: landing 36's retained log names no
build identity and no run path for any of its four runs, so its figures were checkable only by finding the roots myself.

## 1. What was verified

| commit | item | evidence (re-derived by me) |
|---|---|---|
| 734417a | LOG-085's "103 entries, 23 red fixtures, 28 manifests" qualified as the tree with the staged guard (landed b105c09); the committed state at 71c1c70 stated as 102 / 22 / 27 | the two added lines read; the loader gave 102 / 22 / 27 at e988ee6..71c1c70 and 103 / 23 / 28 at b105c09 in tb_l32 and tb_l33 |
| 92c0850 (Test Writer and runtime-2) | gen_test_pmc_ctrl's fcov_expectation_file set to null with the reason in the description, every other field byte-equal; the committed manifest untouched; the R1-DRY-1 row: FAIL at all three seeds with "fcov expectation unmet: 204 declared bin(s) not hit", the unmet set equal to the declared set, the run's report holding 26 covergroups and none of the eight the manifest names, an unmeasured entry's manifest consumed by the check | the diff (two testlist hunks, one response row); the manifest: 204 bins over gen_pmc_alias_cg, gen_pmc_ctrl_csr_cg, gen_pmc_hpm_csr_cg, gen_pmc_hpm_event_cg, gen_pmc_mcycle_cg, gen_pmc_minstret_cg, gen_pmc_rvfi_ext_cg, gen_pmc_write_timing_cg, none defined in gen_fcov_groups.svh at 92c0850; classify() has one rule (no positive hit count is unhit), so an unbuilt covergroup's bins read UNHIT and never "missing"; the entry is measured false, tier check, 3 seeds, so the loader's measured-entry rule does not bind and the 15 measured entries all keep manifests; the dry-run manifest (head-mode 962d31f, 87 planned: 57 pass, 22 red_ok, 2 xfail, 6 fail) shows the three pmc_ctrl seeds 504672532 / 1193196759 / 1256849831 with that reason |
| 1deec4c (tb-infra-2 landing 36) | the defect: the storm request gated on the line being low (event_mean != 0 && !vif.req) and asserting with UNTIL_DEBUG_MODE, whose release tested the entry TOGGLE (evt_dbg_entered != entered_q) flipped only on a debug-mode entry edge (gen_rvfi_pkg: if (t.ext_debug_mode && !dbg_mode_q) toggle), so a request asserted while already in debug was never released and the program stopped; the fix publishes the LEVEL evt_dbg_mode (gen_bridge_if, set in gen_rvfi_pkg beside dbg_mode_q) and releases on it; the edge sampler removed; no constant added; gen_component_api_dbg_agent.md's two sentences corrected | every term read in the diffs of gen_agents_pkg.sv, gen_rvfi_pkg.sv and gen_bridge_if.sv; the API document's diff |
| 1deec4c | the evidence: the round-1 dry-run failure of gen_ut_export_dbg_storm at seed 700483392 (no tohost store, zero UVM errors); the last program record at cycle 1052 in three runs on the committed driver including one with a 16x bound; on the fixed driver PASS ending at 10858 with the last program record 10852; requests = releases 54/54 and 46/46 after, 39/38 on a passing seed before; the irq driver audited, both round-1 irq-storm entries PASS | the dry-run manifest names the seed and the cocotb failure and its run directory holds no GEN_DBG report (the abort precedes it); tb-infra-2's fixed root: seed 700483392 PASS with "GEN_DBG] requests=54 releases=54" and seed 1 PASS with "requests=46 releases=46", both headers build_sources_sha256 1a7de65f7001a0fa, equal to the root's compile log AND to my TB-source recipe over the committed 1deec4c sources, so the fixed runs were built from the landing's sources; the "requests=39 releases=38" line is in 22 retained logs the log does not cite (every retained seed-7 dbg_storm excerpt since landing 1c and the t150 seed-1 export run, e.g. dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_dbg_storm_s1_stdout.log), so the leak was visible in retained evidence long before the fix; the hung local reproduction and the 16x run were not located |

## 2. Rows

- CM211-Low-3: answered by 734417a. R1-DRY-1 (the dry run's own row): the pmc detach. CR-33 rows: not in this range (rt35c pending). Landing 36 answers
  no review row; it is round-1 gating under LOG-085.

## 3. Findings

- L-1 (landing 36; gen_fu_l36_dbg_driver_livelock.log, whole): the retained log names no build identity for any of its four runs and no run path for
  three of them. The failing LSF run is placed at head-mode 962d31f (its identity recoverable from the dry-run manifest); the local reproduction, the
  16x-bound run and the FIXED root carry no figure at all, and the fix's own identity 804995dc55125148 is not named. Located by me: the fixed root's
  compile log and both run headers read 1a7de65f7001a0fa, which equals my recipe over the committed 1deec4c sources, so the pair's green is on the
  landing's sources; the "before" counters 39/38 sit in 22 retained logs the log does not cite (e.g. dv/auto_dv/evidence/gen_sunset_pass2/gen_t150_export_dbg_storm_s1_stdout.log); the two hung runs I could not locate. The
  rule the log misses is the one every landing since 23 has kept: a retained header names the build it claims (gate identity for a committed shape,
  the local figure otherwise) and the run directories it quotes. Fix by corrigendum row (the log's bytes never move): the four roots' figures and paths,
  and the retained-log citation for 39/38.

### Informational

- I-1: the irq-driver audit's two caveats (a fresh assert overwrites a held line's policy; UNTIL_ACK depends on the program's ack handler) are stated and
  not fixed, neither a hang; the flat 20000-cycle tohost bound shared by six cocotb tests is named as a separate landing and is the dry run's remaining
  cocotb failure class (gen_ut_intg_store 2062654708).
- I-2: the dry run's fourth failing entry, gen_ut_lockstep_icache_ecc_tag_two at 508609593 (a uvm_error), is not addressed by this range; it stays on
  the round-1 gating list.
- I-3: the pmc detach removes the only manifest-bearing check-tier entry whose covergroups are unbuilt; the eight groups' 204 declarations return with
  the covergroup landing, and until then the entry's runs carry no fcov check at all (runs_without_fcov_manifest counts it).
- I-4: tb-infra-2's scratch root for this landing sits in a directory named l33 in the shared scratchpad, the name my own tb_l33 working directory uses;
  no file collided, but the two roles share a name there.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 realistic stimulus: the livelock was stimulus acting on a state it could not see, fixed
by publishing the state, not by a cap (conforming). S4 honesty: the corrigendum states the committed counts, the detach states its reason in the entry,
the livelock record says what more time did not buy and which runs pass; one retained log without identities or paths (L-1). S6 trust triad: a red-green
pair on one root with the bound untouched and a control seed (conforming). One-line verdict: PASS, with one record correction.

## 5. Verdict

CRITIC VERDICT: APPROVE on the range b105c09..1deec4c. Row CR-34 L-1 (tb-infra-2, a corrigendum row). Nothing is gated. Round-1 gating stands as LOG-085
records: two of the dry run's four failing entries are addressed here, the tohost bound and the tag_two error remain.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-b105c096-1deec4c5.md, committed 20b3a4e, blob 7f5e6ba6a259ee0f, 41 lines, verdict
APPROVE-WITH-CHANGES. Reviewer identity as its header states: the Claude fallback (claude CLI 2.1.260, run-reported model claude-fable-5-1 with
claude-haiku-4-5-20251001, requested effort high, a fresh session on a detached read-only checkout of 1deec4c; codex unavailable on the spend cap; owner
ruling A-001). Five rubrics PASS. Read after Sections 1-5 were written; nothing above was changed on reading it.

Agreements:

- Its Low-1 is my L-1 (the log's four runs without a build identity or run path). Its recommended form, a head-mode supplement naming the root's git
  head and the sha256 of the three changed SV files before and after, is stronger than the corrigendum-row shape I named, so CR-34 L-1 takes that
  content: for each of the four runs the root's identity (the gate identity for a committed shape, the TB-source figure otherwise), the sha256 of
  gen_agents_pkg.sv, gen_rvfi_pkg.sv and gen_bridge_if.sv on each side of the fix, the run directory, and the retained-log citation for 39/38. The
  log's bytes never move.
- Its verified figures, re-derived by me: five commits, 12 files, 383 insertions, 9 deletions, nothing under rtl/; the loader on the committed
  testlist gives 103 entries / 23 red fixtures / 27 manifests with gen_ut_lockstep_icache_ecc_fcov_red the only entry carrying both red_fixture and a
  manifest (the artifact states 103 / 27); the three SV files are unchanged between 962d31f and 102c17b (an empty git diff --stat), so the dry run's
  build is the committed driver; entered_q has no reader at 1deec4c outside the line the log quotes; gen_agents_pkg.sv:720 tests evt_dbg_mode and
  gen_rvfi_pkg.sv:97 / :148 / :149 declare, maintain and publish it as cited; the manifest row's 8107 bytes and md5 65adfa0e978325a9 equal the
  committed blob; the dry run's export (runs/gen_ut_export_dbg_storm_700483392/gen_export.txt, R lines, fields ext_debug_req, ext_debug_mode, cycle)
  gives 4315 records, 4044 with the debug-mode flag, 4040 with debug_req high, last cycle 35924 and the last record outside debug mode at cycle 1052
  (the same 1052 whether a program record is read as the flag clear or as pc_rdata inside the image; the debug-mode records sit at 1a110800); the
  fixed root's two exports give 2025 / 106 / 53 / 10852 and 2024 / 88 / 10690 as the log's lines 51, 76 and 83 state, and the drain messages in the
  two stdout logs are stamped 10858500 and 10696500 in the run's 10 ps precision unit (-timescale=1ns/10ps, period GEN_CLK_PERIOD_NS 10),
  cycles 10858 and 10696 as the log's lines 74 and 81 state. post_fcov_checks filters on fcov_expectation_file and vdb and on verdict PASS / XFAIL (or a
  deferred red) with no measured test, and fcov_policy_failures exempts measured false and every tier outside TIERS (smoke, targeted, full), so the
  check tier is exempt as its docstring says.

Adopted and verified (misses of mine):

- Low-2, adopted as row CR-34 L-2 (tb-infra-2, the same corrigendum row): on the committed blob 20e158a533e410c5, line 43 ends "the log's own
  severity counts read" and line 44 continues "so no checker fired" with no quoted count between them; lines 73 and 80 are whitespace-only where a
  per-run severity line belongs; line 106 says every figure is read "by the command printed above it" while the log's only command line is line 41
  (the one line beginning with a dollar sign; no other grep, awk or python invocation appears in the log). I read the log for identities and paths
  and did not check each quoted-figure site for its command. Fix in the corrigendum row: the three missing lines, and either the commands or a
  closing claim the log supports.
- Info-1: gen_testlist.yaml:1788 at 1deec4c reads "on the report channel Round 1: fcov_expectation_file detached (null)" with no separator.
  Cosmetic; the entry's next touch.
- Info-2: the commit subject's "the failure lives only in the run manifest" overstates. post_fcov_checks (gen_regress.py:156-163) writes verdict,
  reason, fcov_check and evidence_line back into the per-seed result.yaml; at seed 504672532 that file reads verdict FAIL, the unmet reason,
  fcov_check.status UNHIT, declared 204, hit 0, while driver.log line 2 reads PASS. The response row's wording is right; Section 1 above quotes the
  manifest and not the "only".
- Info-3: the published level lags on exit as on entry. Terms: rvfi_ext_stage_debug_mode[0] takes debug_mode at rvfi_id_done (rtl/ibex_core.sv:2101)
  and the controller clears debug_mode_d on dret_insn in FLUSH (rtl/ibex_controller.sv:961-964; dret_insn = dret_insn_i & instr_valid_i at :229), so
  the dret record carries the flag set and gen_rvfi_pkg.sv:149 publishes 1 from the dret's retirement until the next record retires; a request
  asserted at gen_agents_pkg.sv:723 in that window meets the :720 test at the next negedge and is released, a one-cycle pulse counted once on each
  side. Not a hang; the log's ONE LIMIT (lines 31-34) names the entry lag only. One sentence in the API document or the corrigendum row.
- Info-4: gen_tb_architecture.md:615-617 still describes the edge release; known, the DV Lead's corrigendum pending; not counted here either.

Re-derivation notes on the artifact: its irq-driver line numbers do not match 1deec4c (ack_seen is :607-611, the HOLD_CYCLES countdown :633-635, the
UNTIL_TAKEN release :637-643, against its :606-610, :622-625, :626-632); the code it describes sits at those lines and its claims hold. Its
gen_ut_export.py:119 is dv/auto_dv/gen_tb/gen_tests/gen_ut_export.py:119 (the flat 20000-cycle wait, with gen_ut_export_rows.py:61 and :75).
post_fcov_checks spans gen_regress.py:142-163, not :143-164.

Corrigenda to Sections 1-5: none; nothing above was found false. Two precisions: the "last program record at cycle 1052 in three runs" in Section 1
is re-derived by me for the LSF run only (the two local runs are the unlocated roots of L-1); the fixed root's record figures are now re-derived from
its exports as stated above.

Disagreements: none. The verdicts agree (APPROVE here, APPROVE-WITH-CHANGES there, both Lows on the same retained log). Rows after reconciliation:
CR-34 L-1, CR-34 L-2 (adopted). CRITIC VERDICT: APPROVE, unchanged.
