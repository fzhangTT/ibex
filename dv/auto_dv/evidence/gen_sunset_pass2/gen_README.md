# Cycle-clause sunset, pass 2 (ruling LOG-038)

Ruling LOG-038 (Orchestrator, 2026-09-03): pass 2 of the cycle-clause sunset runs on Runtime's head-mode regression pinned to
979350a (canary_head_t150 PASS; gen_ut_export plus the five T-150 export-observing entries gen_ut_export_irq_storm, gen_ut_export_dbg_storm, gen_ut_export_scrkey_delayed, gen_ut_export_rows_nmi, gen_ut_export_rows_dbg;
six runs PASS, UVM_ERROR 0, LSF jobs 10941862..10941867), whose build manifest observed all 28 declared rows and nothing outside
the declared set. LOG-028a rule: an item loses its token only when EVERY one of its export rows was observed. This directory holds
byte copies of the inputs and outputs the release rested on (originals under the shared out root and gitignored work directories).

Files:
- gen_build_manifest_979350a.yaml: byte copy of /proj_soc/user_dev/fzhang/ibex_dv_out/probe_t150_979350a/build/gen_tb/build_manifest.yaml (head 979350aadee1845dbc46856aece825f3497e6f67, source mode head);
  sha256 325e71facbd975190e8e1c2d3b88509799ececf872e01f81a55b4e8ebd057956. export_sources_declared 28, export_sources_emitted 28 (header-derived), export_rows_observed 28; first_run values:
  gen_ut_export_1, gen_ut_export_dbg_storm_1, gen_ut_export_irq_storm_1, gen_ut_export_rows_dbg_1, gen_ut_export_rows_nmi_1.
- gen_token_sunset_released_gated.log: the driver's per-item output (dv/auto_dv/tools/gen_token_sunset.py --build-manifest <that
  manifest>): 86 items RELEASED (every row observed) across 36 groups, 0 GATED.
  Released per area: IRQ 34, DBG 13, REG 12, XIF 8, CSR 4, BIT 2, CMP 2, PRV 2, TRG 2, DMEM 1, EXC 1, FE 1, IC 1, IMEM 1, ISA 1, MUL 1.
- gen_trace_check_before_after.log: dv/auto_dv/tools/gen_trace_check.py --build-manifest <that manifest> before the removal
  (plan v2l: 105 marked items; FAIL, the sunset line names every due item) and after it (19 marked items, PASS).

Items left marked after pass 2 (19): the 18 icram-dependent items (17 IC items plus TP-REG-018, whose rows include icram inject),
which wait for an icram writer, and TP-PMC-001, the one no-export-row item (gen_test_plan.md Section 0, Section 1.3). Pass 1 is under dv/auto_dv/evidence/gen_sunset_pass1/ (LOG-033).
Runtime's retained run headers, verdicts and stdout of the reference regression sit beside these four files (its gen_manifest.md lists them).
The group column of gen_token_sunset_released_gated.log reflects the plan at pass 2 (v2l: TP-CSR-029 in gen_csr_trap_setup); an item's group is
read from the current gen_test_plan.md. The release of the interrupt- and debug-pin rows (TP-ISA-040, TP-MUL-023 and the other items whose
rows only T-150's storm entries observed) rests on one head-mode regression of 979350a (six runs), as LOG-028a requires (observed once in a
retained run of the pinned build); a later regression that never observes such a row again is a stimulus regression to triage, not a
release error.
Consequence (rule (f)): the released items' witness bins become must-hit bins of their owning tests; the one built test affected is
gen_test_csr_trap_setup (TP-CSR-029, bin w_tp_csr_029), whose manifest re-render lands in the same commit (LOG-036).
