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

## 11. Step 2: the event writers, format version 2, the active-source list (version 4d)

Built in one announced window (Runtime told 13:05Z): every event source whose component exists after the step-2b
re-application writes its rows (ibus/dbus req, gnt, rvalid in gen_bus_driver; pin fetch_enable/mcounteren_writable in
gen_ctrl_driver; the irq lines in gen_irq_driver::apply_levels, debug_req in gen_dbg_driver; alert and misc rows in
gen_misc_monitor, sampled at the posedge; scrkey req/valid in the key responder; regime phase in gen_cmd_dispatch), each
through `sink.write_event` with the rendered line function and the stamp `sink.cycle()` (new; the bridge's cycle_count);
the pin, alert and misc writers also emit the level at reset release. gen_bridge_if gained evt_ibus_grants /
evt_dbus_grants (incremented in the grant beat, non-blocking); the flush and end markers carry ibus_grants= dbus_grants=
and the header says `v2`. The yaml key `export_active_sources` renders EXPORT_ACTIVE_SOURCES (the attribute Runtime's
manifest reader expects), GEN_EXPORT_ACTIVE_SOURCES and gen_export_source_active(); the sink derives the header's
sources= from that list intersected with +gen_export_sources and fatals on a writer for an inactive source or an active
source without a writer. read() gains three rules: the header's sources= equals the rendered active list restricted to
the run's knob (the test passes its +gen_export_sources value), the E gnt count of every enabled bus equals the marker's
grant counter (MUT-G), and both marker kinds carry the two grant keys. Codegen unit test PASS with the new checks and one
new refused fixture (an active source outside the event table).

Red: no dedicated red run exists for the writers. A missing writer is not observable through the format (an inactive
source is legal and its rows simply do not appear), and the pre-step-2 build's file fails the new reader on the `v1`
header before any rule, which is a version refusal, not a red of the writers. The trust evidence for the writers is
therefore the content of the first green (below) and the two mutations MUT-G / MUT-H.

First green (build out_t080s2/a, compile clean on the first try; gen_tdd_logs/export/gen_s2a_*): export_zc 175 records,
902 E lines (ibus req 155 / gnt 154 / rvalid 153: one response pending at the flush; dbus 29/29/29; 13 lines at cycle 0:
the four alert rows, the seven misc rows (irq_pending, core_busy and the five crash_dump fields) and the two ctrl pins;
crash_dump_current_pc 151 and next_pc 165 in total; pin fetch_enable at
cycle 0 = MuBiOff and at cycle 60 = MuBiOn, mcounteren_writable at 0); export_s7 2008 records, 15765 E lines incl. scrkey
req/valid 10 each; export_irq_storm 3939 records, 47672 E lines incl. irq_fast 6327, irq_pending 1722; export_zc_counters
PASS; the canary (boot_zc, lockstep_zc, lockstep_s7) PASS. Content facts checked by hand and retained
(gen_s2a_event_content_analysis.txt): the first ibus req at cycle 61 (the cycle after fetch_enable rose at 60), its gnt
at 64 with req_cycle 0x3d = 61 and outstanding_after 1, its rvalid at 67; the first dbus store of the Zc program at
0x8000039c. The fetch_enable line offset (the line's cycle against cycle_count read after the FETCH_EN ack edge) was 0 on
all four runs and is now asserted exactly (`FETCH_EN_LINE_OFFSET = 0`); the "minus one" the version-4c text predicted was
wrong and is withdrawn. Cost: about 2 misc lines per retired instruction come from the crash_dump pc fields (the plan
demands them for one item); a consumer that does not need them uses `+gen_export_sources` without misc.

Mutations (out of tree, gen_tdd_logs/mutations/gen_mut_export_MUT*): MUT-H (fetch_enable line stamped one cycle late)
caught by the fixture's offset rule (`offset -1 != 0`), ablation PASS; MUT-G (one gnt line dropped, counter intact)
caught by read()'s gnt-count rule (`GEN_EXPORT: 153 E ibus gnt lines, marker says ibus_grants=154`), ablation PASS. Pinned reruns export_zc / export_s7 PASS with the offset
asserted; a restricted run (`+gen_export_sources=ibus,pin`) PASS with the header sources= equal to the restricted list
(gen_s2a_export_zc_ibusonly_*). Window closed on build out_t080s2/a; the follow-up landing (T-134 / T-136 / T-137 and the
review rows) starts in the same tree.

## 12. T-141: writers register their rows, the sink fatals in every run, the bus count rules, the never-observed rows

Cross-model CM8-M-1 / M-2 / M-3 and the Critic's step-2 Section 7 (LOG-028a). Built (dv/auto_dv/env/gen_export_pkg.sv,
gen_agents_pkg.sv, gen_checkers_pkg.sv, gen_env_pkg.sv, gen_knobs_codegen.py, gen_export.py):
- each writer instance calls `sink.register_row(source, event)` for every row it emits in its own end_of_elaboration_phase
  (bus driver: req / gnt / rvalid; ctrl: fetch_enable / mcounteren_writable; irq driver: the five irq rows; debug driver:
  debug_req; misc monitor: the four alert and seven misc rows; key responder: req / valid; dispatcher: regime phase);
  gen_env's seven `register_source` calls are gone;
- the codegen renders `GEN_EXPORT_ROWS` (every source/event, yaml order) and `gen_export_row_header(source, ev)`; the
  sink walks the list at start of simulation BEFORE the enabled test and fatals on a row of an active source with no
  registered writer, so a build with a silent writer fails every run, export knob or not; the header's sources= and
  `# events` rows are derived from the registered rows (a deleted writer changes the header);
- `read()` gains the two presence rules per enabled bus: #req - #gnt in {0, 1}, 0 <= #gnt - #rvalid <= the bus's
  outstanding cap; `+gen_export_sources` naming an inactive source is a uvm_warning; a yaml without export_active_sources
  dies with a message (fixture in the codegen unit test, gen_fu_knobs_codegen_ut.log).
Red: the sink fatal has its red as mutant MUT-K (the key responder never registers: `emitted row scrkey/req has no
registered writer in this build`, in a run without +gen_export_file and in one with it); the count rules as MUT-I (silent
req writer) and MUT-J (silent rvalid writer), each with a Python ablation (gen_mut_export.md).
Green on out_fu2/h: export_zc (175 records, 902 events at flush 2), export_s7 (2008 records, 15765 events) pass the new
rules; every other run of the set passes the every-run registration check by construction.
Never-observed rows (CM8-M-3, Critic s2 M-2, LOG-028a): new test gen_ut_export_rows.py (knob `+gen_ut_rows_set`) issues two
REGIME_SET on knob_imem_gnt_delay (short, then long) and one DBG_REQ (assert, CYCLES policy 60) or one NMI_PULSE (4
cycles), reads the export and requires one regime phase line per REGIME_SET with (knob_id, value_idx, phase_idx) as
issued and a 1-then-0 pair of the pin row. Retained (gen_tdd_logs/lockstep/gen_fu_h_rows_*, export excerpts
gen_tdd_logs/export/gen_fu_h_rows_*_export_excerpt.txt), first lines hand-checked against the component reports:
- rows_dbg_s7 (seed-7 image, debug ROM): `E 23b regime phase 0 1 1` and `E 45f regime phase 0 2 2` against the dispatcher's
  `GEN_PHASE phase 1 ... cycle=571` (0x23b) and `phase 2 ... cycle=1119` (0x45f); `E 23b pin debug_req 1` (the DBG_REQ
  dispatched in the same cycle as the first REGIME_SET: commands are event-driven, not clocked) and `E 277 pin debug_req 0`
  at 0x277 = 631 = 571 + 60, the hold the command asked for; 4 debug entries; 316 records, 1611 events, 0 mismatches.
- rows_nmi_irqp (interrupt program, vector 31 = mret): `E 3d5 regime phase 0 1 1` (GEN_PHASE cycle=981) and `E 5d5 regime
  phase 0 2 2` (1493); `E 3d5 pin irq_nm 1` and `E 3d9 pin irq_nm 0` (4 cycles, the NMI_PULSE argument); 310 records, 2340
  events. Run with `+gen_chk_all=0`: the model has no NMI emulation (shim document Section 4a, DEFERRED), so the NMI entry
  is 58 isa misses in the unsilenced run (out_fu2/b rows_nmi_irqp, FAIL, not retained as green); this run is an export
  observation only and says nothing about the DUT's NMI entry.
Doc corrections of the review lows: addendum line 41 garble, the read() signature with `sources` (addendum :27, :161 and
the sink document), the "version 1" heading, the FETCH_EN_LINE_OFFSET comment now states the derivation (ack in the
ReadWrite region after posedge N, the driver acts at the next negedge and stamps N).

T-150 (Orchestrator, committed form of CM8-M-3): five check-tier, measured-false, debug_only-free testlist entries are
drafted for Runtime to merge (dv/auto_dv/work/tb-infra/gen_t150_testlist_entries.yaml; tb-infra does not edit
gen_testlist.yaml): gen_ut_export_irq_storm (gen_irq_directed.S, storm + multi: irq_fast 6327, irq_external 422,
irq_software 418, irq_timer 390 lines, irq_pending 1722, 1591 I markers), gen_ut_export_dbg_storm and
gen_ut_export_scrkey_delayed (riscv-dv gen_rand_smoke seed 7: 77 debug_req lines over 107 debug entries; 10 scrkey req and
10 valid lines under the delayed regime), gen_ut_export_rows_nmi (gen_irq_directed.S, regime phase + irq_nm, isa rows
silenced) and gen_ut_export_rows_dbg (seed 7, regime phase + debug_req). Each was rehearsed on build out_fu2/j with the
entry's exact plusargs (gen_fu_j_export_irq_storm_t150_*, gen_fu_j_export_dbg_storm_s7_t150_*, gen_fu_j_export_scrkey_s7_t150_*,
gen_fu_j_rows_*). Two vehicle facts decided the programs: the interrupt program starves under a debug storm inside
gen_ut_export's tohost budget (export_dbg_storm_t150 on out_fu2/j: `no tohost store`, not a checker red) and requests no
scramble key even under the interrupt storm, while the seed-7 program requests 10.
