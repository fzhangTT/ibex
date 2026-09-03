# Cycle-clause sunset, pass 1 (ruling LOG-033)

Ruling LOG-033 (Orchestrator, 2026-09-03): the DV Lead removes the cycle-clause marker token from every plan item whose export rows
are ALL in the observed-row list of the reference build manifest below (LOG-028a: observed rows decide, never the declared or the
rendered table), in the same change as the plan landing v2k + v2j (commit 5f530a8; Section 0 reference fix bc4ede6). This directory
holds byte copies of the inputs and outputs that release rested on; the originals live under gitignored work directories. Every
later pass gets its own dv/auto_dv/evidence/gen_sunset_pass<n>/ the same way (gen_test_plan.md Section 0, operational rule).

Files:
- gen_build_manifest_2696920.yaml: byte copy of dv/auto_dv/work/runtime/out/probe_export_1445_v2k/build/gen_tb/build_manifest.yaml
  (Runtime head-mode build of committed 26969205c1025c464ab6ee45785e577cc355859e; gen_ut_export seed 1 PASS behind the gen_boot_zc canary);
  sha256 c31f7734312582f45023538a642b34413528812d6719c3de4eb5e4009055ae60. export_sources_declared 28, export_sources_emitted 28
  (header-derived), export_rows_observed 19.
- gen_token_sunset_released_gated.log: the driver's per-item output (dv/auto_dv/tools/gen_token_sunset.py --build-manifest <that
  manifest> --observed-field export_rows_observed): 115 items RELEASED across 62 groups (every row observed), 86 items GATED (every
  row emitted, at least one never observed; the gating rows are listed per item).
- gen_trace_check_before_after.log: dv/auto_dv/tools/gen_trace_check.py --build-manifest <that manifest> before the removal
  (220 marked items; FAIL: 115 violations, the sunset line names every due item) and after it (105 marked items, PASS), plus the
  re-run after the Section 0 reference fix (bc4ede6, PASS).

Observed rows (19): alert alert_major_bus; alert alert_major_internal; alert alert_minor; alert double_fault_seen; dbus gnt; dbus req; dbus rvalid; ibus gnt; ibus req; ibus rvalid; misc core_busy; misc crash_dump_current_pc; misc crash_dump_exception_addr; misc crash_dump_exception_pc; misc crash_dump_last_data_addr; misc crash_dump_next_pc; misc irq_pending; pin fetch_enable; pin mcounteren_writable.
Emitted but never observed in that run (9): pin debug_req; pin irq_external; pin irq_fast; pin irq_nm; pin irq_software; pin irq_timer; regime phase; scrkey req; scrkey valid.
The probe_export_t140 rehearsal reference (head 11413df) carried the identical 19-row observed list.
Items left marked after pass 1: 105 = 86 gated + 17 icram-dependent + TP-PMC-001 + TP-REG-018 (no export row).
Pass 2 follows T-150's regression (LOG-033) and is retained under dv/auto_dv/evidence/gen_sunset_pass2/.
