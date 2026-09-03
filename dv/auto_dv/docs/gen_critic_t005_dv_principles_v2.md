# Critic: DV-principles conformance check of the T-005 code, v2 (re-review after T-029)

- Artifacts under review (committed, commit 3c623e5452939458326911d4d7ddfe37a1166991 = HEAD, no
  drift): dv/auto_dv/tb/gen_smoke_tb_top.sv (sha256 first 16: 2943ca8b5e08535d),
  dv/auto_dv/tb/gen_dut_top.sv (592d9560d4e6a0a9), dv/auto_dv/tb/gen_tb_pkg.sv (e8fae175fb683410),
  dv/auto_dv/tb/gen_filelist.py, dv/auto_dv/tb/gen_rtl.f, dv/auto_dv/docs/gen_component_api_dut_top.md
  (914bfa4df7e95308), dv/auto_dv/evidence/gen_t005_compile_log_excerpt.md (Section 5 added),
  dv/auto_dv/evidence/gen_t029_smoke_red_runs.md (58b05e64d13e4977).
- Previous verdict: dv/auto_dv/docs/gen_critic_t005_dv_principles_v1.md (REQUEST-CHANGES, P-01..P-07).
- Standard: docs/dv/dv_principles.md per the dv-principles-check skill; docs/dv/TB_CONTRACT.md.
- Date (UTC): 2026-09-03 06:05
- Reviewer role: critic (Claude Fable 5.1). Verified on this host against the out-tree
  dv/auto_dv/work/tb-infra/out_t029/smoke/ (compile.log, sim/sim.log, red1/sim.log, red2/sim.log,
  green2/sim.log) and the committed diff 3c623e5. No LSF command; no fence event.

CRITIC VERDICT: APPROVE

All seven v1 findings are closed with evidence I could confirm on disk. Residual items: low 3,
info 2 (none blocks). The T-024 REQUEST-CHANGES gate is lifted for the T-005 files.

## Closure of the v1 findings

| v1 | Status | Evidence checked |
|---|---|---|
| P-01 (medium) red-run proof of the two `$fatal` checks | CLOSED | red1/sim.log:20-21 `Fatal: "dv/auto_dv/tb/gen_smoke_tb_top.sv", 386` + `GEN_SMOKE_FAIL: no RVFI retirement observed` (retired=0 with `+gen_smoke_cycles=1`); red2/sim.log:18-22 `corrupting NOP word bit 5`, `retired=999 alerts=2998`, `Fatal: ... 388` + `GEN_SMOKE_FAIL: 2998 alert cycles observed`; green (sim/sim.log:19-20) before and green2/sim.log:19-20 after, both `retired=2995 alerts=0`, `GEN_SMOKE_PASS`. The red-run knob `+gen_smoke_intg_flip` is a TB-side stimulus corruption declared once in gen_tb_pkg.sv:11 and used at gen_smoke_tb_top.sv:301-304; the real VCS `Fatal:` line format is now on record for the flow's scanner (matches gen_flow_const.py FAIL_PATTERNS `^Fatal:` and `GEN_\w*_FAIL`). |
| P-02 (medium) vacuous pass without RVFI | CLOSED | gen_smoke_tb_top.sv:281-282 `ifndef RVFI` -> time-0 `$fatal("gen_smoke_tb_top requires +define+RVFI ...")`. Its own red path is not exercised (see R-02). |
| P-03 (low) smoke contract undocumented | CLOSED | gen_component_api_dut_top.md Section 5a: tokens (`GEN_SMOKE_PASS` the only pass token, the two `GEN_SMOKE_FAIL` texts, the RVFI guard text), knobs (`PLUSARG_SMOKE_CYCLES`, `PLUSARG_SMOKE_INTG_FLIP`), informational lines, verdict rule (tokens and collected fatal, never the exit code). Consistent with gen_testlist.yaml `pass_marker: GEN_SMOKE_PASS`. |
| P-04 (low) banner gaps | CLOSED | sim/sim.log:14 `RndCnstLfsrSeed=0xac533bf4 RndCnstLfsrPerm=0x1e35...`, :15 the PMP reset parameters named as ibex_pkg defaults; gen_dut_top.sv:455-457. |
| P-05 (low) re-typed literals | CLOSED | GEN_BOOT_FETCH_OFFSET / GEN_DATA_W / GEN_INTG_W removed (gen_tb_pkg.sv, 35 lines); GEN_BOOT_ADDR_DEFAULT keeps its RTL cite and now names its consumer (gen_program.py). |
| P-06 (low) dangling Q tags | CLOSED | gen_dut_top.sv:5-14 cite gen_intervention_log.md Q-002 (revised) and LOG-004. |
| P-07 (low) guard described as elaboration-time | CLOSED | gen_dut_top.sv:471-475 generate-scope `$fatal` (IEEE 1800-2017 20.11 elaboration system task); API doc :61-63 and :86-87 reworded to match. The green compile (out_t029/smoke/compile.log: 0 errors, 32 SIOB + 1 LCA, same classes as T-005) shows the false branch elaborates cleanly. |

## Residual findings

### R-01 (low) [S4 "Evidence over inference"; S6 trust triad scope]
gen_t029_smoke_red_runs.md:23-27 and gen_component_api_dut_top.md Section 5a state that
gen_smoke_tb_top "is NOT a regression-tier test" and that trust-triad rules 2 and 3 therefore do
not apply, "if Runtime ever lists it, this statement is void". dv/auto_dv/flow/gen_testlist.yaml:
43-58 already lists `gen_smoke` with `tier: smoke`, `feature_groups: [bringup]`, so the statement is
void by its own terms. Required: align the two, either (a) Runtime keeps gen_smoke in the smoke
tier as the flow's bring-up test and TB Infra supplies the rule-2 evidence for its two checks
(two named RTL mutations in a scratch copy: one that suppresses RVFI retirement, one that raises a
spurious alert, each caught by the named `$fatal` and surviving with the check disabled; rule 3
is n/a until a covergroup exists, recorded as such), or (b) the tier statement is dropped and the
testlist entry is marked `bringup` outside the measured tiers. Decide before the first measured
regression; not a defect of the T-005 code itself.

### R-02 (low) [S2 "prove it once"; TB_CONTRACT Section 3]
Two guards added in T-029 have unproven failure paths: the `ifndef RVFI` time-0 `$fatal`
(gen_smoke_tb_top.sv:281-282) and the generate-scope RegFile `$fatal` (gen_dut_top.sv:473-474).
The mechanism (`$fatal`) is proven by red1/red2, but the conditions (a build without
`+define+RVFI`; a build with `+define+RegFile=ibex_pkg::RegFileFPGA`) were not compiled. One
compile each, recorded in the evidence file at the next touch, closes it.

### R-03 (low) [S5 "a mistyped gate silently no-ops"]
gen_smoke_tb_top.sv:304 `nop_word ^ (MemDataWidth'(1) << intg_flip_bit)`: a bit index of
MemDataWidth or more shifts the 1 out and corrupts nothing, so `+gen_smoke_intg_flip=40` would
run green while claiming a red run. Add `if (intg_flip_bit >= MemDataWidth) $fatal(...)` in the
same initial block.

### R-04 (info) Cross-reference, not part of T-029
gen_component_api_dut_top.md:86-88 still names the coverage scope as two `+tree` entries on
`u_ibex_core` and `u_register_file`, while the flow instruments `+tree <tb_top>.u_dut`
(gen_critic_t010_dv_principles_v1.md P-04, DV Lead run-scope ruling pending). Fix when the ruling
lands; the sentence is otherwise unchanged from v1.

### R-05 (info) Evidence note
gen_t029_smoke_red_runs.md:80-82 states the simv exit status was 0 on the red run; the committed
excerpt and out_t029/smoke_driver.log record an exit status only for the green run (`sim exit:
0`). The claim is plausible (SIM_RECIPE Section 5 warns of exactly this) but not evidenced; log
the exit status per run in future red-run evidence so the "never from the exit code" rule is
demonstrated, not asserted.

## Summary
The T-005 wrapper, package, smoke top, filelist tooling, API document and evidence now conform:
both smoke checks have real red runs with the VCS `Fatal:` signature and their tokens, the smoke
cannot pass vacuously without RVFI, the smoke contract is documented for the flow's scanner, the
banner covers every parameter the wrapper forwards or defaults, no re-typed literal remains, the
header tags resolve to the intervention log, and the RegFile guard is an elaboration check as
documented. APPROVE. The three low residuals (tier statement versus testlist, the two unproven
guard conditions, the flip-bit range) go to TB Infra and Runtime for the next touch.
