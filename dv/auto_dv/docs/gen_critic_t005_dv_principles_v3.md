# Critic: DV-principles conformance check of the T-005 code, v3 (re-verification after LOG-005 / T-036)

- Artifacts under review (committed at HEAD 24f3dc0, no drift in these files):
  dv/auto_dv/tb/gen_smoke_tb_top.sv (sha256 first 16: 2943ca8b5e08535d), dv/auto_dv/tb/gen_dut_top.sv
  (592d9560d4e6a0a9), dv/auto_dv/tb/gen_tb_pkg.sv (e8fae175fb683410),
  dv/auto_dv/docs/gen_component_api_dut_top.md (914bfa4df7e95308): all four byte-identical to the
  files my v2 reviewed. New since v2: dv/auto_dv/tb/gen_smoke_run.sh (8a7193c989d4ff29, the committed
  driver) and the rewritten dv/auto_dv/evidence/gen_t029_smoke_red_runs.md (18c5a18140136937).
- Out-tree verified: dv/auto_dv/work/tb-infra/out_t036/smoke/ (compile.log, runs_summary.txt, four
  run directories) and dv/auto_dv/work/tb-infra/out_t036_driver.log; the earlier out_t029/smoke/ tree
  for the LOG-005 facts.
- Previous verdicts: v1 (REQUEST-CHANGES, P-01..P-07), v2 (APPROVE, residuals R-01..R-05).
- Standard: docs/dv/dv_principles.md per the dv-principles-check skill; docs/dv/TB_CONTRACT.md;
  the evidence-audit rule recorded in gen_intervention_log.md LOG-005a.
- Date (UTC): 2026-09-03 06:58
- Reviewer role: critic (Claude Fable 5.1). No LSF command; no fence event.

CRITIC VERDICT: APPROVE

The v2 approval stands and is now backed by an artifact-identity audit, not by log content alone.
Both red paths and the green runs before and after them map to four distinct retained logs in
creation order. The T-005 files did not change. New findings are low (Section 4).

## 1. Re-verification of the T-036 evidence (artifact identity)

Rule: each claimed run maps to a distinct retained log whose path, mtime/ctime and in-log stamp
agree with the claimed order; identical quoted content across two claimed runs is a red flag; the
committed excerpt must quote identifying lines. Local times are -0400 (UTC = local + 4 h).

| Claimed run | Path (out_t036/smoke/) | mtime = ctime | sim.log md5 | Identifying content in the log | Claim in the evidence | Match |
|---|---|---|---|---|---|---|
| compile | compile.log | 02:22:17 | - | 0 Error lines; 32 Warning-[SIOB], 1 Warning-[LCA_FEATURES_ENABLED]; CPU time 6.702 s compile | Section 2 | yes |
| green before | run_01_green/sim.log | 02:22:19 | 9d668412 | Command line names run_01_green; retired=2995 alerts=0; GEN_SMOKE_PASS; $finish at 3004500 | 3.1 | yes |
| red, no retirement | run_02_red_noretire/sim.log | 02:22:24 | 89861960 | +gen_smoke_cycles=1; retired=0; Fatal: ... 386; GEN_SMOKE_FAIL: no RVFI retirement observed; $finish at 5500 | 3.2 | yes |
| red, integrity flip | run_03_red_intg/sim.log | 02:22:33 | 10134d0f | +gen_smoke_intg_flip=5; retired=999 alerts=2998; Fatal: ... 388; GEN_SMOKE_FAIL: 2998 alert cycles observed | 3.3 | yes |
| green after | run_04_green/sim.log | 02:22:38 | 75077b17 | Command line names run_04_green; retired=2995 alerts=0; GEN_SMOKE_PASS | 3.4 | yes |
| summary | runs_summary.txt | 02:22:38 | - | four lines with simv_exit=0, token, fatal_lines, as-expected; "sequence result: ALL-AS-EXPECTED" | Section 3, verbatim | yes |
| driver log | ../out_t036_driver.log | 02:22:38 | - | vcs exit: 0, then the same four summary lines | Section 3 | yes |

Notes on identity. run_01 and run_04 quote identical result lines and have the same size and CPU
time (0.180 s); they are distinct runs because their Command lines name different -l paths, their
hashes differ and their stamps are 19 s apart with the two red runs in between. The VCS header
stamp has minute resolution (Sep 3 02:22 for all four), so the order rests on mtime/ctime and on the
driver log's sequence. Every excerpt in the evidence is a verbatim copy of the named file. The simv
exit status is 0 in all four runs and is recorded per run, which closes v2 residual R-05 and
demonstrates SIM_RECIPE Section 5 rather than asserting it.

## 2. Status of the v2 residuals

| v2 item | Status | Basis |
|---|---|---|
| R-01 tier statement contradicts the testlist | CLOSED | gen_testlist.yaml: gen_smoke is tier check, measured false; the evidence's tier statement now says the same (Runtime R-01 resolution, verified in gen_critic_t010_dv_principles_v2.md) |
| R-02 two guards never compiled red | OPEN, owed on the next touch | evidence Section 1 says so; gen_smoke_tb_top.sv unchanged |
| R-03 flip-bit range guard | OPEN, owed on the next touch | gen_smoke_tb_top.sv:304 unchanged; no range check |
| R-04 API doc coverage-scope sentence | OPEN, pending the DV Lead's P-04 ruling | unchanged |
| R-05 exit status per run not evidenced | CLOSED | runs_summary.txt simv_exit per run (Section 1) |

## 3. Method note: how the v2 claim passed, and what changes

What v2 did. I opened out_t029/smoke/green2/sim.log, confirmed it existed and showed retired=2995
and GEN_SMOKE_PASS, and wrote "green before and after ... verified against the out-tree". That was
a content check. I did not record the artifact's identity (the -l path in its Command line, its
mtime/ctime relative to red1 and red2, its hash) and I did not object that the committed Section 6
quoted lines identical to Section 3 with no identifying line. The cross-model review then reported
"no green2/ directory" (its cited paths lacked the smoke/ level), and LOG-005 was opened against an
evidence claim my verdict had endorsed. LOG-005a later established from ctime that the green2 run
did exist; my v2 was right in substance and under-specified in method. A verdict that cannot show
why a reviewer's contrary claim is wrong has not audited the evidence.

What every evidence audit now does, applied in this file, in gen_critic_exclusions_draft_v2.md and
in gen_critic_t010_dv_principles_v2.md:
1. One table row per claimed run: retained path checked verbatim against disk, mtime and ctime,
   in-log simulator stamp, content hash, and the identifying line (Command path, seed, plusargs).
2. Identical quoted content across two claimed runs is a red flag until the identity row shows two
   artifacts; a committed excerpt that repeats another excerpt must carry an identifying line.
3. When the claim is about exit codes or a sequence, the exit code per run and the creation order
   must be in the retained artifacts, not only in prose.
4. A claim whose artifact lives only in a volatile place (scratchpad, a reused outdir) is recorded
   as unretained and is not credited as evidence past that session.

## 4. Findings on the new committed code (gen_smoke_run.sh)

D-01 (low, hazard) [LOG-005 standard: an outdir that evidence cites is never reused]
gen_smoke_run.sh:17 `rm -rf "$OUT"` deletes the output directory on every invocation, so
reproducing "from one command" with the same OUT destroys the very artifacts the evidence cites
(out_t036/smoke/). Required on the next touch: refuse to run when OUT exists (exit with a message),
or require a fresh directory name. Not blocking: the cited artifacts exist today and TB Infra's
per-task directory convention (out_t005, out_t019, out_t029, out_t036) has protected them so far.

D-02 (low) [dv_principles Section 5, single source of names]
gen_smoke_run.sh:51-52 and :60-62 re-type the tokens GEN_SMOKE_PASS / GEN_SMOKE_FAIL and the
plusarg names gen_smoke_cycles / gen_smoke_intg_flip that gen_tb_pkg.sv declares once. The flow's
constants check (gen_flow_const.py --check) does not cover this script. Acceptable for a local
evidence driver; state the coupling in the header comment or derive the names from gen_tb_pkg.sv.

D-03 (info) The driver's token test is a substring grep (:51-52), weaker than the flow's whole-token
rule (gen_verdict.marker_matches). The driver is evidence tooling, not the pass/fail authority;
the flow's verdict remains the rule for any tiered run. No change required.

## Summary
The T-005 wrapper, package, smoke top and API document are unchanged since v2 and stay approved.
The T-036 evidence replaces the v1 excerpt with four retained, distinct, ordered logs and a per-run
exit status, and every quoted line in it is verbatim from disk. Residuals R-02, R-03 and R-04 are
carried forward; D-01 and D-02 go to TB Infra for the next touch of the driver. APPROVE.
