# TDD transcript: record and event export, record part (T-080, architecture Section 9)

Components: `dv/auto_dv/env/gen_export_pkg.sv` (gen_export_sink), the rendered `dv/auto_dv/env/gen_export_record_line.svh`
and `gen_export_event_lines.svh`, the export block of `dv/auto_dv/tb/gen_tb_knobs.yaml` (knobs export_file,
export_counters, export_sources, export_flush_every; command EXPORT_FLUSH; export_record_fields, export_counter_fields,
export_events) with `gen_knobs_codegen.py`, the monitor changes in `dv/auto_dv/env/gen_rvfi_pkg.sv` (sink hand-off,
one I line per rising edge of rvfi_ext_irq_valid, counters under the knob), the dispatcher route in
`dv/auto_dv/env/gen_env_pkg.sv`, `dv/auto_dv/gen_tb/gen_export.py` (read), `gen_bridge.py` (export_flush).
Test: `dv/auto_dv/gen_tb/gen_tests/gen_ut_export.py` (written first). Design: `dv/auto_dv/docs/gen_rvfi_export_addendum.md`
(version 4b). API: `dv/auto_dv/docs/gen_component_api_export_sink.md`. Retained logs:
`dv/auto_dv/evidence/gen_tdd_logs/export/` and `gen_tdd_logs/mutations/gen_mut_export_*` (manifest `gen_tdd_logs/gen_manifest.md`).
Build configuration opentitan, seed 1, host soc-l-11, 2026-09-03. Owner: tb-infra.

## 1. Red 1 (the test exists, the reader module does not)

Run on the T-068 build `out_t068b` (`gen_export_red1_no_reader_t068b_*`): cocotb fails to import the test module:

```
0.00ns CRITICAL cocotb.regression  Failed to import module dv.auto_dv.gen_tb.gen_tests.gen_ut_export
ImportError: cannot import name 'gen_export' from 'dv.auto_dv.gen_tb'
verdict: FAIL   reason: cocotb_critical at stdout.log:12
```

## 2. Red 2 (reader and rendered knobs exist; the SV side of the old build does not know the knob)

Same build (`gen_export_red2_knob_unknown_t068b_*`):

```
UVM_FATAL dv/auto_dv/env/gen_env_pkg.sv(198) @ 0: uvm_test_top [GEN_UNKNOWN_PLUSARG] unknown plusarg +gen_export_file=gen_export.txt (names live in gen_tb_knobs.yaml)
** TESTS=1 PASS=0 FAIL=1 SKIP=0        verdict: FAIL   reason: uvm_fatal at sim.log:19
```

## 3. Compile (two defects on the way, both retained)

`gen_compile_t080_attempt1_fflush_task.log`: `Error-[STASKEC_TIWFE] Task not expected ... $fflush is invoked where
function is expected` (VCS treats `$fflush` as a task; the `void'()` casts were removed).
`gen_compile_t080_attempt2_uvm_name_clash.log`: `Error-[SV-IRT] Incompatible return types ... uvm_component::flush`
(the sink's `flush()`/`record()` collided with UVM virtuals; renamed `flush_export`, `write_record`, `write_marker`,
`write_event`). `gen_compile_t080.log`: `vcs exit: 0`, zero `Error-[` lines; the flag set from `gen_flow_const.py` is in
`gen_config_opts_t080.txt`. The tree was non-compiling for about four minutes at 10:1xZ; Runtime was told before and after.

## 4. Green (test defects on the way, disclosed)

UNRETAINED (the three attempts below and the single-flush green runs `export_zc`, `export_zc_counters`, `export_s7`
were lost when the mutation runner recompiled with FORCE=1 into the same `out_t080` directory; their identifying
lines are quoted from the driver output of that session; rule adopted: a build directory holding retained runs is
never recompiled in place). The FORCE recompile also changed source (driver log line 2: the `sink.enabled`
guard was added), so the lost greens ran on a different source than the retained build. In the 10:37Z mutation pass the
MUT-B/MUT-C sed anchors did not match after that guard was added, so those two runs PASSed with no mutation applied;
B and C were redone at 10:40-10:41Z (`gen_mut_export_bc_driver.log`) and only those runs count. Attempt 1: a TEST defect, `await` inside a generator expression
(`TypeError: 'async_generator' object is not iterable`). Attempt 2: the test asserted
that the last store record is the tohost store and failed with `last store is 0x8000039c <= 0x8000025e`; my first
reading (a stack push after the tohost store) was WRONG: the flushed prefix ended before the tohost record (attempt 3
below), and the Zc program spins after its store. The rule became "every store to the tohost address carries 1 and
their count does not exceed the memory model's end-of-test count", which is program-independent either way. Attempt 3: two RVFI facts
recorded, not export defects: (a) the tohost store's record (order 170) retired a few cycles after the memory model
saw the bus store, so it landed AFTER the flush marker taken 4 cycles after the end-of-test edge (marker
`records=a9 retired=a9`, record 170 written next), and `read()` correctly excluded it as trailing bytes, which is the
case the plan review predicted; the test now settles 40 cycles (longer than the 32-cycle maximum rvalid regime).
(b) On the seed-7 program the single trap record (order 466, ecall at 0x80002164) has `pc_wdata` 0x80002168 = pc + 4,
not the handler address 0x80001700: this RTL does not report the vector in `pc_wdata` of a trap record (open ruling
F-RVFI-010; the comparator skips isa_pc_next on traps for the same reason), so the continuity rule excludes trap
records. Then green, with the final test issuing two flushes and binding `read()` to the second:

```
gen_export_zc_twoflush_t080_*   : GEN_UT_EXPORT flush seq 2: records 175 retired 175 markers 0 events 0 (bridge retired now 175; early flush seq 1 had 0 records)
                                  GEN_UT_EXPORT_PASS   UVM_ERROR : 0   TESTS=1 PASS=1   verdict: PASS
gen_export_zc_counters_twoflush : same counts, header counters=1, every R line 54 fields (34 + 20)   verdict: PASS
gen_export_s7_twoflush_t080_*   : GEN_UT_EXPORT flush seq 2: records 2008 retired 2008 markers 0 events 0   GEN_UT_EXPORT_PASS   verdict: PASS
```
The export files are retained beside their runs (`gen_export_zc_twoflush_t080_gen_export.txt` and the other two):
header `# gen_export v1 seed=1 build_config=opentitan counters=0 sources= fields=order,pc_rdata,...`, image line,
`# flush seq=1 ...`, `# flush seq=2 records=af retired=af markers=0 events=0 cycle=...`, `# end records=af retired=af
markers=0 events=0` written in extract_phase. `sources=` is empty: no event writer registers in this landing.

## 5. Regression set on the same build (with and without the knob)

`gen_runs_summary_t080.txt`: `lockstep_zc`, `lockstep_zc_export`, `lockstep_s7`, `lockstep_s7_export`, `ut_bridge_green`,
`boot_zc` all verdict PASS (re-run on the final build for retention after the FORCE recompile; the retained sim.log and
verdict.txt of each carry the identifying lines). Wall clock (VCS CPU time, retained runs) 0.27 s vs 0.33 s (Zc) and
0.54 s vs 0.55 s (seed 7) without vs with the knob: a few tens of milliseconds at these record counts. File sizes:
21144 bytes for 175 Zc records (121 per record), 28982 with counters (166), 219090 bytes for 2002 seed-7 records (109).

## 6. Mutations (trust triad rule 2 for the consumer checks)

`dv/auto_dv/mutations/gen_mut_export.md`: MUT-A field corruption (153 discontinuities caught by the fixture), MUT-B
dropped record (read(): records 174 != retired 175), MUT-C swapped records (read(): order 51 after 49), MUT-D
suppressed marker (read(): no marker with seq=2), MUT-E first record pc moved (fixture first-pc), MUT-F stale marker
(read(): no marker with seq=2). Every mutation run with `+gen_chk_all=0`; every ablation control (the named rule
disabled) PASSES, with the second catchers recorded where a rule's ablation exposed another (dropped and swapped
records are caught by three independent rules; the stale marker by the fixture's content checks too). Logs
`gen_tdd_logs/mutations/gen_mut_export_[a-f]_*`; the first mutation pass (`gen_mut_export_attempt1_driver.log`) lost
its per-mutation directories to a runner naming defect and was repeated.

## 7. Codegen unit test

`gen_tdd_logs/knobs_codegen/gen_knobs_codegen_t080.log`: `GEN_UT_KNOBS_CODEGEN PASS (0 failures)`, 763 OK lines, with
the export knobs, the field lists (every record field a gen_rvfi_txn member), the event table and the two rendered
includes checked, and Runtime's `debug_only_plusargs` line for `gen_export_flush_every` in place
(`gen_knobs_codegen_t080_before_runtime_line.log` is the run before that line, one red check as stated).

## 8. What is NOT in this landing

Event lines (Section 8 of the addendum): no writer registers yet, `events=0` everywhere; build step (2) adds the bus,
ctrl, scrkey and icram writers with the bridge grant counters and MUT-G/MUT-H; step (3) the step-2b sources. The
Zcmp micro-op pc convention is recorded, not asserted (micro-op records are skipped by the continuity rule).

## 9. Version 4b follow-up (v4a replan review rows that touch the record part)

Changes: `rs3_addr` / `rs3_rdata` added to `gen_rvfi_txn` and to the R line (36 fields; the yaml comment names the
carve-out basis of the excluded capability fields); flush and end marker key=value pairs written decimal (R/I/E
values stay hex) with `gen_export.read()` parsing them so; the pc-continuity rule of the test excludes mret and dret
records (plan C-1) besides trap records. Announced to Runtime as an edit pass; fresh compile into
`dv/auto_dv/work/tb-infra/out_t080d` (`gen_compile_t080d.log`, vcs exit 0): canary boot_zc, lockstep_zc, lockstep_s7,
ut_bridge_green PASS; export_zc, export_zc_counters, export_s7 PASS (`gen_export_*_t080d_*`; the seed-7 run exercises the
mret/dret exclusion on a program with a trap); lockstep zc/s7 with the knob PASS (`gen_runs_summary_t080d.txt`). Wall
clock on this build: 0.29 s vs 0.26 s (Zc), 0.52 s vs 0.54 s (seed 7) without vs with the knob. The Section 4 runs
(`*_twoflush_t080_*`) remain retained as the hex-marker version. The red-window canary of 10:49Z that closed Runtime's
LOG-017 report is retained as `gen_canary_*_t080_*` (boot_zc, lockstep_zc, export_zc PASS on the pre-v4b tree).

## 10. Version 4c (r4 replan REQUEST-CHANGES, T-104): exact event rows

The r4 replan review (of 6d16d9c) required exact event rows (the plan's sunset input (2)). Change: gen_tb_knobs.yaml renders
29 rows over 8 sources (pin irq_software/irq_timer/irq_external/irq_nm/debug_req/fetch_enable/mcounteren_writable with
`value`, pin irq_fast with `idx, value`, alert x4, misc x7, scrkey req/valid, the bus/icram/regime rows unchanged);
gen_knobs_codegen.py refuses an event token `<name>`; gen_export.py drops the wildcard fallback (an `E` token that is not
a header row fails) and requires every rendered row of every source named in `sources=`; gen_ut_knobs_codegen.py gains
the refused-wildcard fixture and checks the exact function names; codegen unit test PASS (0 failures). The reader change
was checked against the retained t080d files: gen_export_s7_t080d_gen_export.txt (2008 records) and
gen_export_zc_counters_t080d_gen_export.txt (175 records) read OK; the pre-rs3 twoflush file fails on the field list as it
should (34-field header). No writer exists yet, so no run's header changes; the export_zc / export_zc_counters /
export_s7 runs on the T-102 build (gen_tdd_logs/export/gen_export_*_t102_*) PASS with the new reader and the
re-rendered gen_tb_pkg.sv. Documents: addendum v4b final (stale text swept, MUT-H relation, Section 9 owner set and
standing, icram to step (3)), sink API document Section 2, response tables R3 and R4 in
gen_critic_response_rvfi_export.md.

T-108 lows closed in the same landing: `read()` requires every marker key (seq, records, retired, markers, events, cycle
on a flush marker; a truncated marker is a GEN_EXPORT completeness FAIL, checked on a synthetic truncation of the retained
s7 file, gen_tdd_logs/export/gen_export_reader_truncated_marker_t102.log); the first-fetch offset is the rendered
`boot_reset_offset` of the yaml memory map (GEN_MM_BOOT_RESET_OFFSET in gen_tb_pkg.sv and gen_isa_shim_map.h,
MEMORY_MAP in gen_knobs.py; the shim, its unit test, gen_ut_export.py and gen_program.py read it; disclosed: the first
gen_program.py edit used the bare name MEMORY_MAP where the tool holds the module as GEN_KNOBS, so the shared tree's
gen_program.py failed on import for about two minutes at 11:56Z before the fix; the Zc image regenerated afterwards is
byte-identical, crc32 cf0cb3b8); SETTLE_CYCLES derives from the
rendered rvalid window maximum plus a pipeline margin; the early flush is issued after half the retirement target so the
prefix assertion compares non-empty lists. Decision recorded: gen_ut_export stays a local-driver unit test (no testlist
entry) until the Test Writer's first export consumer lands; a check-tier entry then follows the gen_ut_bridge pattern.
