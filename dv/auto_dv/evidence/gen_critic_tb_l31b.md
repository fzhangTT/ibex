# Critic verdict: tb-infra landing 32 at a759752 (the landing-31 correction answering CR-31 and CM208) and rtl-arch's superseding ruling record at a68c021, reviewed as tb_l31b, the recorded re-review of tb_l31's REQUEST-CHANGES

Scope (the Orchestrator's): the one commit a759752 (twelve files: the drain at bound plus one, never_taken removed, the MUT-NT2 mutant diff retained with
measured root identities, gen_component_api_irq_checker.md corrected in three places, the cap moved to 227 with +gen_ibus_rvalid_max=6 as the run-time
answer to the unit-test row, the two l32a reproducer logs and the wave run record retained, the age-17 fixture stated as not constructed), judged by id
against CR-31 M-1, L-1, L-2 (tb-infra's) and L-3 (rtl-arch's, its retention half lifted here) and against CM208 Medium-1, Low-1, Low-2, Low-3, Low-4 and
Info-1; and rtl-arch's superseding ruling record a68c021 (one file, 182 lines: Section 7 from the wave, Section 8 re-pointed at landing 32's retained logs
with the knob stated uncommitted, Section 5 corrected, the configuration path fixed, CR-31-L-3 and CM208-Low-4 answered by id), added to the target by the
Orchestrator while this file was unfrozen. Both sit in the range opening at c0db7be whose end the Orchestrator names at the launch; the range's other commits get their own files (tb_l30b on
v4r). The landing-31 gate rests on this verdict.

Artifacts reviewed (committed blobs at a759752, the record at a68c021; sha256 first 16 hex):

- dv/auto_dv/evidence/gen_rvfi_irq_valid_exclusive_ruling.md  50cb25b88e41a54c
- dv/auto_dv/docs/gen_component_api_irq_checker.md  a863ed1eb43ea95b
- dv/auto_dv/env/gen_checkers_pkg.sv  3dd6470218e93f96
- dv/auto_dv/env/gen_env_pkg.sv  8ec3528a47dae139
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  e860bf1d97197a6f
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  2b392079a1fe7a0f
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_MUTNT2_mutant.diff  cefc596d8458b172
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_drain_corrections.log  3ed064cb9e0327dc
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_take_late_reproducer.log  2a5f45504673a052
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_take_window_reproducer.log  d49be44b495508ef
- dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_fu_l31b_nmi_wave_run.log  ffe530bef435104e
- dv/auto_dv/evidence/gen_tdd_step2b.md  2dc46f3dbf6b5c8a
- dv/auto_dv/mutations/gen_mut_step2b.md  d83bc5b844434e01

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; gen_critic_tb_l31.md (977652d2d0ed7bad, rows
CR-31) and the CM208 artifact (972e7ac093d41ec5); the mutation-proof standard (applied diff, baseline, mutated hash, root identity, each reproducible); the
evidence rule; the rule that a retained header names the build it claims.
Method: detached git worktree of a759752 (the landing gate: both codegen --check up to date, three UTs PASS, CONST, RED-CHECK, validate 27 OK, TBMAN 3469
rows 0 bad including the five new rows; build identity e674e6339b5bea85 over 117 sources recomputed by the tool and matched by the gate's CLAIM leg against
the new log's header; TB-source recipe 98629b00cb34e79e over 75 files). The mutation-proof reproduced end to end from the record: the retained diff applied
with patch to the gen_tb_top.sv blob (736a8d8099339024) gives 9a55bbd4103febd7; a full archive copy of a759752 gives e674e6339b5bea85 by the identity tool
and, with the patched file swapped in, d02bca6ca353117f. The code diffs read (the while condition, the summary line, the API document's three places); the
four new logs read whole; the two reproducer logs compared line for line against the runs' own sim.log files in dv/auto_dv/work/tb-infra/wit/l32a (read on
disk); the local build roots' compile figures and run headers read (wit/l31a, wit/l31c, wit/nmi1, the scratchpad roots l31fix_root and wave_root) and my
TB-source recipe computed over the committed trees at df28129 (f80e2c719e16b73c), 7b18ac7 (d34daf56c8871437) and a759752, and over the scratch roots, to
check every identity the correction log quotes. The superseding record diffed against d732ad9 and its Section 7 readings checked on the wave itself: the
scratch FSDB the record names (2501858 bytes, md5 44730e24c59e75c97cfe5e2ad13eb6f1, both re-derived) opened read-only with the fsdb tools in a session
whose workspace lives in my scratch directory, the named signals sampled and their transitions listed over 3595-3745 ns. EXPOSURE: the Orchestrator's message; tb-infra's work directories named above. No subagent used. Section 6
reconciles with the range's cross-model review when its artifact lands (none exists yet; it launches when rt35 or v4r lands).

CRITIC VERDICT: APPROVE. Every CR-31 and CM208 row is answered as stated and verified by my own reproduction: the mutation-proof's three identities
reproduce from the retained diff and the committed sources, the ablation label is corrected in a corrigendum, the counter is gone from code and document,
the drain waits the bound plus one and seed 7 passes on the corrected build, the API document describes the drain, the cap moves to 227 at run time, and
the two reproducer logs equal the runs they were redirected from; the superseding ruling record closes CR-31 L-3 in full and its Section 7 readings
reproduce on the wave, signal by signal. One Medium-class item is OWED and disclosed as such (the age-17 discriminating fixture),
which my rules admit inside an APPROVE. Two new Lows on identity figures quoted in the new logs, both record errors with every evidence run itself sound.
The landing-31 gate may lift.

## 1. What was verified

| row | as built | evidence (re-derived by me) |
|---|---|---|
| CR-31 M-1 = CM208-Low-2 | the applied diff retained as gen_fu_l31b_MUTNT2_mutant.diff (843 bytes, manifest row), cited from gen_mut_step2b.md; the identities measured on each side of the fault: ablation e674e6339b5bea85, mutant d02bca6ca353117f, gen_tb_top.sv 736a8d8099339024 to 9a55bbd4103febd7; the committed log's line 37 stated wrong and 3d8e81ccd20737c7 named as the old mutant root's digest after the fault | patch of the diff onto the blob gives 9a55bbd4103febd7; the identity tool over an archive of a759752 gives e674e6339b5bea85 and, with the patched file, d02bca6ca353117f; the scratch root l31fix_root differs from the committed tree in gen_tb_top.sv alone and its digest today is d02bca6ca353117f; the catch line and ablation PASS in the log's section 3 |
| CR-31 L-1 = CM208-Low-1 | never_taken removed from the declaration, the format string and the argument list; the summary ends "open after the drain=%0d" | the gen_checkers_pkg.sv diff; grep of the file: no never_taken |
| CR-31 L-2 = CM208-Medium-1 | the drain loop continues while the count is at or below the bound (18 records), its line says "bound 17 records plus one"; seed 7 PASS on e674e6339b5bea85 with "drain: 18 records in 126 cycles", open after the drain 0; the alternative (judging at the drain's end) declined with the reason; the age-17 discriminating fixture NOT constructed, the fix reasoned from the operators with seed 7 as the non-discriminating check, OWED in the log, gen_tdd_step2b.md and the response row | the gen_env_pkg.sv diff (<= against the strict > at gen_checkers_pkg.sv:127, so an expectation at age 17 is judged on the 18th record); the log's section 1; the disclosure present in all three records |
| CR-31 L-3 = CM208-Low-4 (retention half) | the window and late reproducers retained with every firing and error line, the build's local figure labelled as the local runner's, the take-arm diff by hash, the 1..8 sweep named and the 28-firing first attempt recorded; the wave run's own record with the FSDB named by path and md5 as non-durable | the retained firing lists equal the runs' sim.log lists exactly (11 and 25 times, 36 in all); the error counts 11 and 25; the cycle lists as in tb_l31; the take-arm diff's hash 8f54baec0b00 matches the work-directory file. The record's wording ("retained") and its rtl/ path remain rtl-arch's to fix, not in this landing |
| CM208-Low-3 | gen_component_api_irq_checker.md corrected at :20, :93 and :121 to the drain, the open-after-drain count and the retirement-stall residual as owed | the three changed lines; the remaining "never taken" mentions are the NMI-mode sentence at :40 (a different rule) and the history sentence at :121 |
| CM208-Info-1 | no SV unit case, stated; the run-time path shown instead: cap 193 at i 3/4 d 3/4 and 227 with +gen_ibus_rvalid_max=6 at i 3/6 d 3/4; rvalid_max 200 and 12 starve the run before the drain, stated | (6+3+2)*17+40 = 227; the log's section 4 lines; the plusarg reaches the cap through the effective cfg (gen_agents_pkg.sv:108-136, verified in tb_l31) |
| CR-31 L-3 = CM208-Low-4, rtl-arch's half (a68c021) | Section 8 rewritten against the three retained landing-32 logs, the knob gen_knob_nmi_after_irq_delay stated absent from the committed tree and the take-arm as a working-tree diff, the sweep width and the 28-firing wrong-shape attempt recorded, -timescale=1ns/10ps named as the reason cycle 361 reads 3655000 ps; the header's path corrected to ibex_configs.yaml at the root; Section 5's handler-retirement guess corrected in place; "Review rows answered" names both ids | the diff d732ad9..a68c021 read whole; the three paths exist at a68c021; the knob absent from gen_tb_knobs.yaml at HEAD; the compile log carries -timescale=1ns/10ps; every RTL citation unchanged and still resolving |
| the record's Section 7, read from the wave | rvfi_valid high 3645-3655 ns and rvfi_ext_irq_valid 3645-3735, the assertion reporting at 3655 on pre-edge values; the pulse guard true with new_nmi alone (instr_valid_id 0, new_debug_req 0, new_irq 0, ready_wb 1, captured_valid 0); rvfi_irq_valid 3615-3625, stage [0] from 3625, [1] from 3635, the port from 3645; instr_done_wb 3635-3645; the coincident record order 42, pc 80000120, insn fe629fe3 (bne t0,t1,loop), rvfi_intr 0, rvfi_ext_nmi 1, rvfi_ext_pre_mip 0; irq_nm_i a one-cycle pulse 3610-3620; nmi_mode never rising; the loop pc 8000011e at 3605 and 3735 | every reading reproduced on the FSDB: the transition lists of rvfi_valid (1 at 3645, 0 at 3655, 1 at 3735), rvfi_ext_irq_valid (1 at 3645, 0 at 3735), irq_nm_i (1 at 3610, 0 at 3620), rvfi_irq_valid (1 at 3615, 0 at 3625), instr_done_wb (1 at 3635, 0 at 3645, 1 at 3725) and the three stage elements ([0] 3625-3715, [1] 3635-3725, [2] 3645-3735); the samples at 3647 ns (order 0x2a, pc 80000120, insn fe629fe3, intr 0, ext_nmi 1, pre_mip 0), at 3607 (pc 8000011e, order 0x29) and at 3737 (pc 8000011e, order 0x2b, port 0); nmi_mode 0 transitions over 3600-3750; the guard terms at 3612 ns as stated (at 3607, before the pin rises at the negedge, new_nmi still reads 0, so "during the cycle beginning 3605" means the half-cycle the 3615 edge samples); the disassembly prog.dis:33-34 gives 8000011e addi and 80000120 bne t0,t1,8000011e |
| landing 31's own runs, re-identified from the local roots | the DRAINED seed-7 run and the six blast-radius rows are wit/l31c, every header build_sources_sha256 d34daf56c8871437; the pre-fix RED (seed 7 FAIL, order 3184) is wit/nmi1, header f80e2c719e16b73c | my recipe over the committed 7b18ac7 sources is d34daf56c8871437 and over df28129 is f80e2c719e16b73c, so both roots equal the committed trees the landing-31 log named by gate digest; the RED's and the GREEN's provenance hold |

## 2. Rows

- CR-31 M-1, L-1, L-2: CLOSED (L-2 with the discriminating fixture OWED, disclosed). CR-31 L-3: CLOSED, the retention half by landing 32 and the
  record's wording and path by a68c021; the wave the first record owed is read and its readings reproduce. CM208 Medium-1, Low-1, Low-2, Low-3, Low-4 (retention half), Info-1:
  answered as stated and verified.

## 3. Findings

- L-1 (gen_fu_l31b_drain_corrections.log:8-10 and the CR-31-M-1 response row): the identity section pairs landing 31's gate identity c1189fdc15a85844 with
  "its local compile figure 64f9aee6f60d7c84 from wit/l31a/compile.log". wit/l31a is neither landing 31's build nor the pre-fix root: its sources_sha256.txt
  (75 files) equals the committed df28129 tree except gen_checkers_pkg.sv (11db6e4e6126429a, matching no committed version), and its one run (seed 7)
  PASSES with no drain line, an intermediate experiment. Landing 31's build is wit/l31c (d34daf56c8871437, equal to my recipe over the committed 7b18ac7
  sources, seven runs) and the pre-fix RED is wit/nmi1 (f80e2c719e16b73c, equal to my recipe over df28129). The section written so that "the two functions
  are never confused again" therefore quotes a third root's figure; and the corrected build's own local figure, which the response row says is printed
  beside its gate digest, is described at :5-7 but not printed. Every evidence run is sound; the record's pointer is not. Fix by corrigendum row: name
  wit/l31c and d34daf56c8871437 for landing 31's build, wit/nmi1 and f80e2c719e16b73c for the RED, and print the corrected build's local figure.
- L-2 (gen_fu_l31b_nmi_wave_run.log:9-11): the record quotes three figures for its root: the compile log's "sources sha256: d71984c246000108", the root's
  filelist digest 2bae046d70476d78, and the header's build_sources_sha256 96697a6fee7025b4. The root's compile log (wave_root/out8/compile.log) says
  96697a6fee7025b4, equal to the run header and to my recipe over the root today; d71984c246000108 appears in no compile log I can find; and the identity
  tool over the root today gives 32ee156a5dd888e8, not 2bae046d70476d78. Two of the three figures are not the root's own as it stands, and the log does not
  say which state they describe. The wave is non-durable by the log's own account, so nothing rests on it; the figures should be the root's own or removed.

### Informational

- I-1: the take-arm diff (dv/auto_dv/work/tb-infra/gen_nmi_take_trigger.diff, 8f54baec0b00) that reproduces the shape of both reproducers and the wave run
  is a work-directory file, not retained; retaining it beside the logs, as the mutant diff now is, would make the shape reproducible from the repository.
- I-2: the OWED age-17 fixture is the one open item of substance; when it lands it needs its own red on the bound-only drain and green on the bound-plus-one
  drain to be discriminating, as the record already states.
- I-3: the wave the record reads is a scratch file the record itself calls non-durable; my reproduction of Section 7 stands on that copy today (size and
  md5 as the record names them) and will not be repeatable once the scratch is purged, which is why the record cites the retained wave-run log for the run
  and the FSDB for the readings; a citable wave still needs a flow run under a retained path, as the record says.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: the mutation-proof now conforms (diff, baseline, mutated hash and both
root identities reproducible; catch and ablation retained); the TDD pair conforms on the corrected build with the boundary fixture honestly owed. S4
honesty: the omitted unit case, the starving plusarg values, the wrong committed label and the unconstructed fixture are all stated plainly (conforming);
two identity figures quoted in the new logs are not the roots' own (L-1, L-2, non-conforming at those lines). One-line verdict: PASS.

## 5. Verdict

CRITIC VERDICT: APPROVE on landing 32 (a759752) and the superseding ruling record (a68c021) as the re-review of tb_l31's REQUEST-CHANGES; the landing-31
gate lifts and CR-31 L-3 is closed. Rows CR-31b: L-1, L-2, both
record corrections for tb-infra's next touch by corrigendum row; the age-17 fixture OWED as disclosed. Nothing is gated by this verdict.

## 6. Reconciliation with the range's cross-model review

Artifact: dv/auto_dv/reviews/2026-09-04-claude-diff-c0db7be8-24104029.md (a98196fd4ee0f76a, 54 lines), read after Sections 1-5 of this file and of its
companion were written (it was the wrapper's empty placeholder while they were; it covers the whole range c0db7be..2410402, so tb_l31b and tb_l30b
reconcile against this one artifact). Reviewer: Claude Fable 5.1 as the fallback (codex spend cap), fresh session on a detached read-only checkout of
2410402. Its verdict: APPROVE-WITH-CHANGES with three Lows and two Infos, the five rubrics PASS. Mine on landing 32 and the superseding record: APPROVE.
The verdicts agree in substance: the artifact's rows on this commit are two record corrections and two disclosures already made, and it finds nothing that
reopens a closed CR-31 row.

Shared recomputations, each re-run by me and equal to the artifact's: the drain loop's <= against the strict > at gen_checkers_pkg.sv:127 with order_at
from :233, seed 7's "18 records in 126 cycles"; never_taken dead at the base and removed only; the three identities by the identity tool over archives
(e674e6339b5bea85, c1189fdc15a85844, d02bca6ca353117f) and the diff applying cleanly with 736a8d8099339024 to 9a55bbd4103febd7; the cap arithmetic 193 and
227; the API document at :20, :93 and :121; the reproducer logs' firing lines and the 10 ps error times; the five manifest rows and the 3469 data rows; every
RTL citation of the superseding record, the nine-cycle port claim from :2192, the encoding 0xfe629fe3 as the loop's backward branch, the (cycle + 4.5) x
10000 ps rule on all eleven window firings, -timescale=1ns/10ps (gen_flow_const.py:206, which I also read in the wave root's compile log), the knob absent
from the committed code, Section 5 corrected in place, CR-31-L-3 and CM208-Low-4 answered by id. Beyond the artifact, this file's Section 1 also reads
the record's Section 7 on the FSDB itself and the local build roots' compile figures.

The artifact's findings against mine:

- Its Low (gen_tb_pkg.sv:556, the cap sized as per_record x GEN_IRQ_ENTRY_BOUND_RECORDS + margin while the drain now waits bound plus one, the 18th record
  covered only by the 40-cycle margin whose comment at :253 does not claim that role; the plan's semantics sentence repeating "times the record bound"):
  a miss of tb_l31b, adopted and verified (the return line at :556 multiplies by the 17-record bound; the margin's comment names the finish handshake and the
  last write-back, not an extra record; at the defaults the extra record costs 9 cycles of the 40). The class my rules name: I checked the cap formula
  against the code and its 193 default, and checked the drain against the judge, without asking whether the two changes to the same mechanism were sized
  against each other. In practice the margin covers it (the busiest retained drain used 157 of 193), so no retained run is affected; the fix is one factor
  and the 193 figure, in the code and in the plan sentence together, and it rides landing 33 through the CM209 row.
- Its Low (gen_fu_l31b_nmi_wave_run.log:10, the two figures against the header's 96697a6fee7025b4, and the superseding record's :114-115 saying
  96697a6fee7025b4 per both compile log and header, so two committed records disagree): my CR-31b L-2, reached independently; the artifact adds the
  disagreement between the two records, which I verified (the record's :114-115 states what the root's compile log and header say; the wave log's :10 does
  not). Agreement.
- Its Low (gen_fu_l31b_drain_corrections.log:9, 64f9aee6f60d7c84 attributed to wit/l31a where landing 31 built in wit/l31c): my CR-31b L-1; the artifact
  notes that nothing in the committed tree settles it, which is right, since my finding rests on the local roots' compile logs and run headers read on
  disk (Section 1), and the corrigendum should carry the figures so a reader need not. Agreement.
- Its Info (the age-exactly-bound fixture not constructed, adequately disclosed): my I-2 and Section 3's owed item. Agreement.
- Its Info (the pair table holds one pair): noted here as the tool's present scope; it bears on tb_l30b, where the record the tool guards gained a second
  contradiction the table does not declare.

Nothing in Sections 1-5 is contradicted by the artifact; no corrigendum. One miss adopted (the cap's factor), owed through CM209-Low-1 with the CR-31b rows;
no CR-31b row is added. Section 5 stands: APPROVE, the landing-31 gate lifts.
