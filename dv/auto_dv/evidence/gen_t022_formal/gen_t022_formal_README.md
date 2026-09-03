# T-022 formal evidence subset (Critic condition N-1)

Compact, reproducible subset of the SymbiYosys k-induction proofs that carry evidence class EC-1
for the exclusion draft (dv/auto_dv/work/rtl-arch/gen_exclusions_draft.md, Critic approval
dv/auto_dv/work/critic/gen_critic_exclusions_draft_v2.md, finding N-1 and final-file condition
F-2). The analysis these artefacts back is dv/auto_dv/work/rtl-arch/gen_unreachability_evidence.md
(sections 2, 4 and 8). Build configuration: `opentitan` (ibex_configs.yaml); DUT wrapper
dv/auto_dv/tb/gen_dut_top.sv with cheriot_enable_i tied to IbexMuBiOff. The RTL was not modified:
every property lives in a converted copy of the RTL, never in rtl/.

## 1. What is here and what stays in the working tree

Naming: every committed file carries the `gen_` landing prefix (FENCE.md landing rule, strict
reading while Q-001/Q-013 are pending); the tool-native name is the basename without the prefix,
and gen_t022_regen.sh restores it in the scratch output directory. Subdirectory names are
unchanged (runs/<job>/ keeps the SymbiYosys job name).

Section 8 of gen_unreachability_evidence.md names the full retention directory
`dv/auto_dv/work/rtl-arch/t022/` (working tree, ignored by dv/auto_dv/.gitignore). This
directory holds the subset that lets a reader check every claim and regenerate the rest:

| Here (committed) | Working-tree original (dv/auto_dv/work/rtl-arch/t022/) | Content |
|---|---|---|
| jobs/gen_*.sby (16) | jobs/*.sby | SymbiYosys job files exactly as run; [files] paths point at the original scratchpad, gen_t022_regen.sh rewrites them |
| model/gen_t022_top.sv | model/gen_t022_top.sv | scratch top: the 48 wrapper ports with literal widths, gen_dut_top with the opentitan integer parameters |
| model/gen_t022_elab.ys | model/t022_elab.ys | yosys elaboration script for the flattened constant-propagated netlist |
| sources/gen_t022_assertions_extract.txt | sources/t022_assertions_extract.txt | every inserted T022_* assert/assume/cover with file:line (117 lines) |
| sources/gen_t022_formal*.patch (10) | sources/t022_formal*.v (10, about 630 KB each) | unified diff of each assertion-bearing formal copy against t022_all.v; `patch` recreates the copy byte for byte |
| logs/gen_t022_sby_summaries.txt | logs/t022_sby_summaries.txt, logs/t022_sby_*.out | the summary and DONE lines of every run with their SBY stamps (tool local clock, UTC-4) |
| logs/gen_t022_core5_rerun.out | (new, 2026-09-03 08:52Z, SBY stamp 4:52:03 local) | full sby stdout of the latest regeneration re-run of t022_core5 from this clone with the renamed, parameter-checked files (section 4) |
| runs/<job>/gen_status (`<STATUS> <rc> <seconds>` as sby writes it: `PASS 0 10` = PASS, exit code 0, 10 s wall clock; matches the `DONE (PASS, rc=0)` line), gen_PASS or gen_FAIL or gen_UNKNOWN (the empty marker file sby names after the status; absent for the three timed-out jobs), gen_config.sby, gen_implicit_declarations.txt, gen_smt2_assert_count.txt | runs/<job>/ plus logfile*.txt and every trace.vcd / trace.yw | per-run status marker, the implicit-declaration grep count and the SMT2 assert count |
| runs/t022_core5/gen_logfile.txt, gen_logfile_basecase.txt, gen_logfile_induction.txt | same | the full log of the evidence-bearing whole-core run |
| runs/t022_sem/gen_sem.v, gen_sem.sby, gen_sem.out | same | the step-semantics experiment (section 2.2 of the evidence document) |
| gen_t022_regen.sh | - | the exact regeneration commands (section 3) |

Not copied (regenerable, large): model/t022_all.v (627 KB sv2v output), model/t022_flat.il
(9.3 MB yosys netlist), sources/t022_formal*.v, the counterexample traces (0.4 to 1.7 MB each;
their reading is in gen_unreachability_evidence.md section 4.4). The jobs without a status file
(t022_zcmp3b, t022_zcmp3p, t022_zcmp3c20) were killed by the 25-minute timeout while solving
step 14; their partial logs are in the working tree (logs/t022_sby_zcmp3b.out and siblings).

## 2. Tool versions (all from /tools_risc/tt/siliconpilot/latest/bin, siliconpilot 0.18.1)

| Tool | Version | Role |
|---|---|---|
| sv2v | v0.0.13 | SystemVerilog to Verilog-2005 (yosys rejects the struct-literal cast in rtl/ibex_pkg.sv:350) |
| yosys | 0.64+181 (git sha1 8427bd3a3) | elaboration, flatten, `opt -full` constant propagation; SMT2 model through sby |
| sby | v0.64-2-gf57802a | job runner, engine smtbmc |
| yosys-smtbmc | bundled with yosys 0.64+181 | k-induction (basecase + temporal induction), bmc, cover |
| yices-smt2 | Yices 2.7.0 | SMT solver |

## 3. Regeneration (exact commands; from the clone root after `source ci/env.sh`)

```
bash dv/auto_dv/evidence/gen_t022_formal/gen_t022_regen.sh <outdir> [job ...]   # default job: t022_core5
```

The script performs, in order:

0. Parameter guard: the scratch top re-types the fourteen opentitan integer parameters; the script
   parses `util/ibex_config.py opentitan vcs_opts` (-pvalue+NAME=VALUE) and stops with the mismatch
   named if any value differs (checked 2026-09-03: 14 equal; negative control with PMPNumRegions 16 -> 4
   in a scratch copy fails as intended). A configuration change can therefore not invalidate the proofs
   silently.
1. `sv2v -DSYNTHESIS -DDV_FCOV_DISABLE -DBaseIsa=ibex_pkg::BaseIsaRV32IorCHERIoT
   -DRV32M=ibex_pkg::RV32MSingleCycle -DRV32B=ibex_pkg::RV32BOTEarlGrey
   -DRV32ZC=ibex_pkg::RV32ZcaZcbZcmp -DRegFile=ibex_pkg::RegFileFF
   -Ivendor/lowrisc_ip/dv/sv/dv_utils -Ivendor/lowrisc_ip/ip/prim/rtl <every file in
   dv/auto_dv/tb/gen_rtl.f> dv/auto_dv/tb/gen_tb_pkg.sv dv/auto_dv/tb/gen_dut_top.sv
   model/gen_t022_top.sv > t022_all_full.v`. The five enum defines are the `+define+` terms of
   `util/ibex_config.py opentitan vcs_opts`; the `-pvalue+` integers of that command are the
   parameters set on the scratch top.
2. Truncation of the converted gen_dut_top after the close of its u_register_file instantiation
   (drops the time-0 config banner and the RegFile elaboration guard, string functions yosys
   cannot parse; no behaviour): the awk program in the script. Result: t022_all.v.
3. `yosys -q -l t022_elab.log t022_elab.ys` with the script's paths pointed at <outdir>:
   `read_verilog -sv t022_all.v; hierarchy -check -top gen_t022_top; proc; flatten; async2sync;
   opt -full; stat; write_rtlil t022_flat.il`.
4. `patch -o t022_formal_<x>.v t022_all.v sources/gen_t022_formal_<x>.patch` for each formal copy (the gen_ prefix is dropped from the output name so the .sby [files] entries resolve).
5. `sby -f <job>.sby` per named job, with the [files] path rewritten to <outdir>; then the two
   evidence checks: `grep -c 'implicitly declared' <job>/model/design.log` must print 0 and
   `grep -c assert <job>/model/design_smt2.smt2` must match runs/<job>/gen_smt2_assert_count.txt.

## 4. Reproduction checks performed for this subset (2026-09-03; rtl/ and vendor/lowrisc_ip/
unchanged since the export commit 1908ddd)

Three runs of gen_t022_regen.sh from this clone: 07:32Z (original file names, clone at commit
7d91448), 08:16Z (after every file received the gen_ prefix), 08:52Z (after the step-0 parameter
guard was added; this is the committed logs/gen_t022_core5_rerun.out, SBY stamp 4:52:03 local).
All three gave the same results:

- Step 1+2 output is byte-identical to the retained model/t022_all.v (md5
  e2f97cc101f3cc835d6f7277b9cdddd8).
- Step 4 output for core5 is byte-identical to the retained sources/t022_formal_core5.v (md5
  5e749b5a75874b09064875326c257a52); the core5 and zcmp3 patches were also round-tripped against
  the retained copies.
- Step 3 netlist equals the retained model/t022_flat.il line for line after normalising the
  absolute source paths in the `src` attributes (0 differing lines); the constant connections
  cited in gen_unreachability_evidence.md section 4.3 are at the same lines (93368
  `nt_branch_mispredict 1'0`, 93394 `instr_bp_taken_id 1'0`).
- Step 5 for t022_core5: `summary: successful proof by k-induction`, `DONE (PASS, rc=0)`,
  0 implicit declarations, 46 SMT2 asserts (logs/gen_t022_core5_rerun.out from the 08:52Z run;
  original run runs/t022_core5/gen_logfile.txt with SBY stamp 1:54:04). Wall time about 25-30 s
  for steps 0-5.

## 5. Job to exclusion-draft class mapping

Classes are those of gen_exclusions_draft.md Part C (T constant-tie CHERIoT cone, P parameter
constant, D FSM default arm with spare encodings, R Zcmp mismatched-state default arms) and Part
A (the cheriot-out-of-scope carve-out). Row numbers are Part C rows; the per-row detail is
gen_unreachability_evidence.md section 4.2.

| Job | Mode, depth, top | Source | Result (status) | Evidence role | Classes / rows |
|---|---|---|---|---|---|
| t022_core5 | prove 5, gen_t022_top | t022_formal_core5.v (18 T022_* lines, 46 SMT asserts) | PASS (k-induction) | THE evidence-bearing whole-core run: all 17 groups of section 4.1 plus the named-state and BP assertions | Part A carve-out cone (T022_*_CHERI0, T022_CSR_MSHWM0, T022_RF_CAP0); T rows 2-11, 13-22, 24-29, 36, 41; D rows 1, 23, 33 (T022_CTRL_NAMED, T022_LSU_NAMED, T022_MD_NAMED); P row 12 (T022_CORE_BP0) |
| t022_core | prove 5, gen_t022_top | t022_formal_core.v (8 lines, 20 asserts) | PASS | first whole-core run; subset of core5, kept as the independent earlier PASS | Part A (T022_CORE_CHERI0, T022_CTRL_CHERI0, T022_LSU_CHERI0, T022_CRX_IDLE, T022_LSU_NO_CTX); D rows 1, 23, 33 |
| t022_core2, t022_core3 | prove 5, gen_t022_top | t022_formal_core2.v, _core3.v | FAIL at step 2 | NOT evidence: 6 and 7 implicit declarations (wb_stage and cheriot_fatal_err_q names outside their generate scope); the spurious failures motivated the implicit-declaration check | - |
| t022_core4 | prove 5, gen_t022_top | t022_formal_core4.v | UNKNOWN (induction failed) | NOT evidence: superseded by core5, which adds T022_CSR_MSHWM0 as the strengthening invariant (section 4.1 note on csr_mshwm_set) | - |
| t022_ibex_controller | prove 8, ibex_controller (free inputs) | t022_formal.v | PASS | module-level confirmation with cheriot_enable_i assumed Off | D row 1 (T022_CTRL_NAMED); T rows 6-10 (T022_CTRL_CHERI0, T022_CTRL_PRIO0) |
| t022_ibex_multdiv_fast | prove 8, ibex_multdiv_fast (free inputs) | t022_formal.v | PASS | module-level confirmation | D row 33 (T022_MD_NAMED) |
| t022_ibex_load_store_unit | prove 8, ibex_load_store_unit (free inputs) | t022_formal.v | FAIL at step 3 | non-vacuity control (section 2.2): the solver drives lsu_is_cap_i, which is free at module level and proved 0 at core level; shows the assertions bite | - (negative control for T rows 14-28) |
| t022_lsu2 | prove 8, ibex_load_store_unit | t022_formal_lsu2.v | PASS | module-level LSU with the CHERIoT inputs constrained as the core drives them | T rows 14-22, 24-28 (T022_LSU_NO_CTX, T022_CRX_IDLE, T022_LSU_CHERI0); D row 23 |
| t022_zcmp | prove 8, gen_t022_top, free bus | t022_formal_zcmp.v | FAIL at step 6 | legitimate counterexample against the 32-bit premise (icache back-fills [31:16]); premise restated on [15:0] | R rows 37-40 (method) |
| t022_zcmp2 | prove 8, gen_t022_top, free bus | t022_formal_zcmp2.v | FAIL at step 7 | artefact of a protocol-violating bus (rvalid without an outstanding request); bus assumptions added | R rows 37-40 (method) |
| t022_zcmp3 | prove 8, gen_t022_top, compliant bus | t022_formal_zcmp3.v | UNKNOWN (basecase PASS to depth 8, induction fails from an unreachable state) | bounded evidence: no class change mid-sequence within 8 cycles | R rows 37-40 |
| t022_zcmp3c | cover 12, gen_t022_top, compliant bus | t022_formal_zcmp3.v | FAIL = cover unreached | bounded evidence: no class-mismatch witness within 12 cycles | R rows 37-40 |
| t022_zcmp3b | bmc 24, same | t022_formal_zcmp3.v | no status (timeout at step 14) | no failure through step 13 | R rows 37-40 (bound 14 cycles) |
| t022_zcmp3p | prove 16, same | t022_formal_zcmp3.v | no status (timeout at step 14) | basecase clean through step 13; induction not completed | R rows 37-40 |
| t022_zcmp3c20 | cover 20, same | t022_formal_zcmp3.v | no status (timeout at step 14) | cover unreached through step 13 | R rows 37-40 (bound 14 cycles) |
| t022_sem (runs/t022_sem) | bmc 6, sem | sem.v | trace as expected | step-semantics calibration: an immediate assert in a clocked block is checked one step after the values it samples; flops without reset start free | - (method) |

Class R (rows 37-40) has bounded evidence only and stays out of the exclusion file until the
first measured regression shows the cover properties of gen_cover_props_draft.sv never hit
(gen_exclusions_draft.md Part C, Critic condition F-5). Rows 30, 32, 42-43 (class P by parameter)
and rows 31, 34, 35 (class D, full encoding) have no formal job: their evidence is the
configuration value or the enum declaration cited in section 4.2.
