# Component API: gen_export_sink (record and event export)

Owner: tb-infra. Status: written from the code as built (2026-09-03). Design: `dv/auto_dv/docs/
gen_rvfi_export_addendum.md` version 4b (embedded as gen_tb_architecture.md Section 9); where the code and the
addendum differ this document describes the code and says so in one sentence at the place of the difference; what
the addendum specifies and the code does not carry yet is marked "planned with the event part".
Source: DV_prompt.txt deliverable 4 (TB architecture document, component API documents). Conventions (shared by
every component document): every runtime knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg`
(column 2 below) and a generated Python constant of the same value; every checker fails through `uvm_error` with
its id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker, `+gen_chk_all=0
+gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Makes the per-record RVFI facts (one line per retired record), the interrupt markers (one line per rising edge of
`rvfi_ext_irq_valid`) and the boundary events (one line per bus, pin, alert, misc, icache-RAM, key or regime event)
of a run readable by Python from ONE ASCII file that a test parses once after a bridge command, never a signal per
cycle (A-01). RVFI is a define-gated DUT boundary interface (probe register row RVFI, `boundary`), so the export is
not a probe under DV_prompt Section 7. The export is observation only: nothing on the SV side reads it back, and the
checks over its content are the tests' own active checks (DV_prompt Section 7). The knob is opt-in per testlist
entry; without it no file is opened.

AS BUILT: `gen_export_pkg::gen_export_sink` (`dv/auto_dv/env/gen_export_pkg.sv`), a `uvm_component` created
unconditionally by `gen_env` as `uvm_test_top.env.sink`; `enabled = cfg.export_file_set`, so with `+gen_export_file`
absent every `write_*` call returns at once and nothing is opened. The sink is the ONE writer of the file: it owns the
descriptor (`fd`), writes the header lines in `start_of_simulation_phase`, appends the `R`, `I` and `E` lines that
the RVFI monitor and the event writers hand in as ready-formatted strings (`write_record`, `write_marker`,
`write_event`, each counting into `records`, `markers`, `events`), writes the flush marker in `flush_export()`
(returns the flush sequence number, which the dispatcher places in `peek_data`), and writes the end marker,
`$fflush`es, checks `$ferror` and `$fclose`s in `extract_phase`. `$ferror` is checked after every `$fflush` of a flush
marker and at the end. Every writer instance registers the (source, event) rows it emits through
`register_row(source, event)` in its own `end_of_elaboration_phase` (T-141; gen_env only hands out the sink handle) and
gates every line through `source_on(name)`. At start of simulation, in EVERY run (export knob on or off, since the
emitted set is a build property), the sink walks the rendered row list `GEN_EXPORT_ROWS` and fatals on a row of an
active source (yaml `export_active_sources`, rendered `GEN_EXPORT_ACTIVE_SOURCES` / `EXPORT_ACTIVE_SOURCES`, the set
Runtime records as `export_sources_emitted`) with no registered writer; `register_row` fatals on an unknown row or a row
of an inactive source. The header's `sources=` field is the active sources that registered a row, intersected with
`+gen_export_sources`, in yaml order, and its `# events` rows are exactly the registered rows of those sources
(`gen_export_row_header(source, event)`), so a deleted writer changes the header and fails Runtime's emitted-set check
and `read()`'s header rule instead of leaving header, manifest and fatal path agreeing on a row nothing emits. A
`+gen_export_sources` value naming a known but inactive source (icram) is a `uvm_warning`. Since the step-2 landing (format version 2) every source but icram
has its writers connected: the bus drivers (req, gnt, rvalid), the key responder (req, valid), the ctrl driver
(fetch_enable, mcounteren_writable), the irq and debug drivers (pin lines), gen_misc_monitor (alert and misc rows) and the
regime dispatcher (phase); the pin, alert and misc writers also emit the level at reset release. `sink.cycle()` (the
bridge's `cycle_count`) is the stamp of every E line; the flush and end markers carry `ibus_grants=` / `dbus_grants=`
(the bridge fields the drivers increment in the grant beat) and `read()` requires the E gnt count of every enabled bus
to equal them. The line text is formatted by functions
rendered from the yaml (`gen_export_record_line` in `dv/auto_dv/env/gen_export_record_line.svh`, one
`gen_export_line_<source>_<event>` per event row in `dv/auto_dv/env/gen_export_event_lines.svh`), whose argument
names are the field names, so the SV side cannot reorder a column. The addendum's Sections 4 and 8 still name one
include `gen_export_fields.svh` and the sink methods `line(kind, text)` and `flush()` (its Section 2 names the two
rendered includes); as built these are the two rendered includes named above and the methods `write_record` /
`write_marker` / `write_event` and `flush_export()`. The
Python reader is `dv/auto_dv/gen_tb/gen_export.py` (`read(path, seq, counters=False, sources="all")`, `sources` = the run's `+gen_export_sources` value), the bridge wrapper is
`GenBridge.export_flush()` (`dv/auto_dv/gen_tb/gen_bridge.py`), and the consumer test is
`dv/auto_dv/gen_tb/gen_tests/gen_ut_export.py`.

## 2. Files and how to call it

SV: `dv/auto_dv/env/gen_export_pkg.sv` (package `gen_export_pkg`, class `gen_export_sink`; includes the rendered
`dv/auto_dv/env/gen_export_event_lines.svh`); `dv/auto_dv/env/gen_export_record_line.svh` (rendered; included inside
`gen_rvfi_pkg` after `gen_rvfi_txn`). Both includes, the `gen_tb_pkg` strings `GEN_EXPORT_RECORD_FIELDS`,
`GEN_EXPORT_COUNTER_FIELDS`, `GEN_EXPORT_SOURCES`, `GEN_EXPORT_ACTIVE_SOURCES`, `GEN_EXPORT_ROWS` (every
`source/event` row, yaml order) and the functions `gen_export_source_known(s)`, `gen_export_source_active(s)`,
`gen_export_event_header(source)` (the `# events` rows of one source, newline-terminated) and
`gen_export_row_header(source, ev)` (one row's header line; empty for an unknown row), and the Python tuples
`EXPORT_RECORD_FIELDS`, `EXPORT_COUNTER_FIELDS`, `EXPORT_SOURCES`, `EXPORT_EVENTS` in `dv/auto_dv/gen_tb/gen_knobs.py`
are rendered by `dv/auto_dv/tb/gen_knobs_codegen.py` from the yaml keys `export_record_fields`,
`export_counter_fields` and `export_events` of `dv/auto_dv/tb/gen_tb_knobs.yaml` (one origin for the column order;
`dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py` asserts the renderings equal the yaml and that every event row has its
line function). Wiring (`gen_env_pkg.sv`): `gen_env` creates `sink`, and `connect_phase` sets `rvfi_mon.sink`,
`dispatch.sink` and `dispatch.bvif`; the dispatcher route is `GEN_CMD_EXPORT_FLUSH: bvif.peek_data =
sink.flush_export()`.

SV writer contract: in the writer's `end_of_elaboration_phase`, when `sink != null`, call `sink.register_row("ibus",
"req")` once per row it emits (an unknown row, or a row of a source the yaml calls inactive, is `uvm_fatal GEN_EXPORT`;
the sink fatals at start of simulation on any active row nobody registered), then per event `if (sink.source_on("ibus"))
sink.write_event(gen_export_line_ibus_gnt(cycle, addr, we, be, req_cycle, outstanding_after));` (no formatting cost
when the source is off); the request rise is `gen_export_line_ibus_req(cycle, addr, we, be)`. The `cycle` argument
is the one cycle base of Section 4: every event writer stamps `sink.cycle()`, which returns the bridge's `cycle_count`.
Registration is a self-declaration: it says which rows this writer emits, and the header is derived from it; that the
writer then emits every registered row is the row observation tests' business (gen_ut_export_rows), not the sink's.
The RVFI monitor calls `sink.write_record(gen_export_record_line(t, cfg.export_counters))` per record and
`sink.write_marker("I ...")` per marker (gen_component_api_rvfi_monitor.md Section 8); the record's `cycle` field is
the RVFI interface's posedge counter, which equals the bridge count (both count posedges from reset release).

Python: `seq = await bridge.export_flush()` (issues `EXPORT_FLUSH`, default ack timeout 200 cycles, returns the
sequence number carried in `peek_data`), then `data = gen_export.read(path, seq, counters=<bool>, sources="all")` (`sources` is the value the run gave
`+gen_export_sources`). `read()` returns
`Export(header, records, markers, events, flush)`: `header` is the dict of the first line's `key=value` tokens;
`records` is a list of namedtuples whose field names are `EXPORT_RECORD_FIELDS` (plus `EXPORT_COUNTER_FIELDS` when
`counters=True`), so `data.records[0].pc_rdata` reads by name; `markers` is a list of `Marker(cycle, ext_pre_mip,
ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode)`; `events` is a list of `Event(cycle, source,
event, fields)` with `fields` a tuple in the header row's order; `flush` is `Flush(seq, records, retired, markers,
events, ibus_grants, dbus_grants, cycle)` from the marker. The caller states `counters` and the header must agree; the
addendum let the header alone decide the namedtuple, as built the reader asserts `counters=` equals the caller's flag. `read(path, None)`
reads to the `# end` marker (post-run diagnostics only, never the basis of a pass). `read()` has no simulator access
and every failure is an `AssertionError` whose message starts with `GEN_EXPORT:`.

### 2a. File format (version 2)

```
# gen_export v2 seed=<n> build_config=<name> counters=<0|1> sources=<csv of active sources enabled by the knob> fields=<csv of R field names>
# image <path as given to +gen_mem_image, rest of line, or the word none>
# events <source> <event> <csv of field names>     one row per (source, event) of every registered and enabled source
R <field values in header order>                    one line per retired record
I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req> <ext_debug_mode>   one line per rising edge of rvfi_ext_irq_valid, at the rise cycle
E <cycle> <source> <event> <field values in the row's order>   one line per boundary event
# flush seq=<s> records=<n> retired=<r> markers=<m> events=<e> ibus_grants=<gi> dbus_grants=<gd> cycle=<c>   written by EXPORT_FLUSH; s = the number the command returns; r = the bridge's evt_retired_count read in the same call; the addendum's ibus_grants=<g> dbus_grants=<h> (the bridge's grant counters) are planned with the event part
# end records=<n> retired=<r> markers=<m> events=<e> ibus_grants=<gi> dbus_grants=<gd>   written in extract_phase
```

`fields` (every `gen_rvfi_txn` field except the CHERIoT carve-out, in this order): `order, pc_rdata, pc_wdata, insn,
trap, halt, intr, mode, ixl, rs1_addr, rs1_rdata, rs2_addr, rs2_rdata, rs3_addr, rs3_rdata, rd_addr, rd_wdata,
mem_addr, mem_rmask, mem_wmask, mem_rdata, mem_wdata, ext_pre_mip, ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req,
ext_debug_mode, ext_rf_wr_suppress, ext_ic_scr_key_valid, ext_irq_valid, ext_exp_valid, ext_exp_insn, ext_exp_last,
ext_mcycle, cycle` (36 names); with `counters=1` the 20 names `mhpmcounter3..mhpmcounter12,
mhpmcounter3h..mhpmcounter12h` follow. `rs3_addr` and `rs3_rdata` are exported because the draft-B ternary ops (Zbt
cmov/cmix/fsl/fsr) read a third operand and the plan's ISA items name it. Not exported, with the basis: the `*_rcap`
capability fields and `mem_is_cap` are the CHERIoT carve-out ("cheriot-out-of-scope", DV_prompt Section 2), constant
in this configuration and owned by the `rvfi_cap_quiet` check. Radix rule: every value of an `R`, `I` or `E` line is
hex without prefix and without leading zeros (`%0h`; a flag is `0` or `1`); every `key=value` pair of the header
(`seed=`, `counters=`), the flush marker and the end marker is DECIMAL (`%0d`; `build_config=`, `sources=` and
`fields=` are names, not numbers). A value with X or Z renders as `x`/`z` characters and `read()` fails on the
non-hex token.
`R` lines are in retirement order (`order` ascending). The `# image` line is rest-of-line, so a path with spaces
cannot break the tokeniser. Every event row names one exact event (no wildcard rows; the codegen refuses `<name>`):
the header carries one `# events <source> <event> <fields>` row per rendered row of every registered and enabled
source, and `read()` requires all rows of every source named in `sources=`. Every active source (ibus, dbus, pin,
alert, misc, scrkey, regime) has a registered writer, so a file written with `+gen_export_sources=all` carries all
29 rows of the 7 active sources; `icram` is the one inactive source (yaml `export_active_sources`).

### 2b. Completeness rule of read(path, seq), as implemented

1. The file is read whole and split on newline; fewer than three lines is `has no header`.
2. Line 1 must start with `# gen_export v2 `; its `counters=` must equal the caller's `counters` flag, its
   `fields=` must equal the comma-joined rendered `EXPORT_RECORD_FIELDS` (plus `EXPORT_COUNTER_FIELDS` when
   `counters`), and its `sources=` must equal the rendered `EXPORT_ACTIVE_SOURCES` restricted to the caller's
   `sources` argument (an active source missing from the header fails; the sink can only omit one when its writer did
   not register, which the sink itself fatals on). Line 2 must start with `# image `.
3. Every following line that starts with `# events ` is a header row: its (source, event) must be a row of the
   rendered `EXPORT_EVENTS` with the same field list, and its source must appear in the header's `sources=`; every
   rendered row of every source in `sources=` must be present (a registered source with a missing row fails).
4. The marker is the FIRST line after the header rows that starts with `# flush ` and carries `seq=<seq>` (decimal,
   the number `export_flush()` returned; every marker `key=value` pair is parsed as decimal)
   (with `seq=None`, the first `# end ` line). No such line is `no complete flush marker with seq=<seq>`: a missing
   marker, an earlier marker in its place, or a marker with another sequence all fail, so a test that flushes more
   than once can never pass on a stale earlier marker. Every byte after the marker is ignored (at the ack posedge the
   monitor may already have written record N+1 into the buffer, which a buffer-full flush can put on disk). No "last
   line must be a marker" rule exists.
5. The marker's `records` must equal its `retired` (the sink's count and the bridge's `evt_retired_count`, read in
   the same call).
6. Every line between the header and the marker is parsed: empty lines and earlier `# flush ` markers of the same run
   are skipped; an `R` line must have exactly 1 + (field count) tokens, all hex, and its `order` must be the previous
   record's `order` + 1; an `I` line must have exactly 7 value tokens, all hex; an `E` line must have at least four
   tokens, its (source, event) must be a header row (an unlisted or misspelled event token is a failure), and its value
   count must equal that row's field count; any other first token is `unknown line kind`. The cycle of each line (the `cycle`
   field of an `R` line, the first value of an `I` or `E` line) must be non-decreasing across all three kinds;
   nothing is required about the order of lines inside one cycle.
7. The parsed counts must equal the marker: `R` lines == `records`, `I` lines == `markers`, `E` lines == `events`
   (the `I` lines are bound to `markers=` exactly as the `R` lines to `records=` and the `E` lines to `events=`).
8. For each of ibus and dbus named in `sources=`: the `E <bus> gnt` line count must equal the marker's
   `<bus>_grants=` (the bridge's `evt_ibus_grants` / `evt_dbus_grants`, counted by the bus driver in the grant beat
   and sampled in the same `flush_export()` call as the other counts; mutation MUT-G).
9. For each of ibus and dbus named in `sources=`, the presence rules (T-141): `#req - #gnt` is 0 or 1 (at most one
   request awaits its grant at the marker; MUT-I) and `0 <= #gnt - #rvalid <= GEN_<BUS>_MAX_OUTSTANDING` (every
   response follows a grant and the outstanding responses stay within the bus depth; MUT-J). The constants are the
   rendered `BUS_MAX_OUTSTANDING` in gen_export.py.

Not part of `read()`: the test's own read of `evt_retired_count` after the ack is a `>=` check against the marker's
`retired` (gen_ut_export.py does this), and every program-derived check (boot pc, tohost stores, pc continuity) is
the test's. A missing file raises the Python `FileNotFoundError` from `Path.read_text()` before any rule runs.

### 2c. Event channel rows (addendum Section 8)

The yaml `export_events` table, one line function per row in `gen_export_event_lines.svh`. Connected: ibus/dbus (req at the first cycle a request is seen, gnt in the grant beat with `req_cycle` = the req line's
stamp and `outstanding_after` = the queue depth after the grant, rvalid in the response beat with `intg_injected` = the
driver's corruption flag), pin (fetch_enable, mcounteren_writable, irq_software, irq_timer, irq_external, irq_fast with
its index, irq_nm, debug_req), alert and misc (every change, plus the level at reset release), scrkey (req observed,
valid driven), regime (phase per applied REGIME_SET). Not connected: icram (inactive in `export_active_sources` until the
RAM model's announcement port). Every writer registers its rows in `end_of_elaboration_phase` (Section 2); the
registered writer of each row is the component in the table's writer column.

| source | event | fields | writer | when |
|---|---|---|---|---|
| ibus, dbus | req | addr, we, be | gen_bus_driver | the first cycle a request is seen (its rise); with the following gnt line's `req_cycle` this gives the cycles the request was held with gnt withheld, and its absence is the "no request" fact |
| ibus, dbus | gnt | addr, we, be, req_cycle, outstanding_after | gen_bus_driver | the cycle the grant is driven (one per beat); `req_cycle` is the cycle of the matching req line |
| ibus, dbus | rvalid | addr, we, err, intg_injected, outstanding_after | gen_bus_driver | the cycle the response is driven (one per beat) |
| pin | irq_software, irq_timer, irq_external, irq_nm, debug_req | value | gen_irq_driver / gen_dbg_driver | every value change (rise and fall) |
| pin | irq_fast | idx, value | gen_irq_driver | every value change of one fast line; `idx` is the line index, so the line count is not re-typed in the table |
| pin | fetch_enable, mcounteren_writable | value (MuBi encoding) | gen_ctrl_driver | every value change |
| alert | alert_minor, alert_major_bus, alert_major_internal, double_fault_seen | value | gen_misc_monitor | every value change (a one-cycle pulse is a rise line and a fall line) |
| misc | irq_pending, core_busy, crash_dump_current_pc, crash_dump_next_pc, crash_dump_last_data_addr, crash_dump_exception_pc, crash_dump_exception_addr (one row each) | value | gen_misc_monitor | every value change (irq_pending_o is the DUT output pin that 26 marked items assert in a named cycle; core_busy as the MuBi encoding; one line per changed crash_dump_o field) |
| icram | inject | way, index | gen_icache_ram (announcement port) | the lookup cycle of an injected ECC error (the expected-alert feed of C3.4) |
| scrkey | req, valid | value | gen_scrkey_driver | every change of ic_scr_key_req_o / ic_scr_key_valid_i |
| regime | phase | knob_id, value_idx, phase_idx | gen_cmd_dispatch (REGIME_SET consumer) | the cycle a phase is applied |

As rendered, the yaml carries every row of the table above as its own exact row (29 rows over 8 sources), one writer
function per row named `gen_export_line_<source>_<event>` with the fields as named arguments; the yaml, the rendered
include, `EXPORT_EVENTS` in gen_knobs.py and the addendum's version-4c table agree row for row (the codegen unit
test checks the first three).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_export_file=<path>` | `PLUSARG_EXPORT_FILE` | open the export file at `<path>` (relative paths resolve in the run directory, the simv working directory in `gen_run.py` and `gen_tb_local.sh`); absent = no export, no file. Normal knob (not debug-only), opt-in per testlist entry; suggested value `gen_export.txt` | unset |
| `+gen_export_counters=1` | `PLUSARG_EXPORT_COUNTERS` | append the 20 hpm counter words to every `R` line; the header's `counters=` records it; the monitor samples `ext_mhpmcounters`/`ext_mhpmcountersh` into the txn only under this knob | 0 |
| `+gen_export_sources=<csv>` | `PLUSARG_EXPORT_SOURCES` | comma-separated subset of `GEN_EXPORT_SOURCES` (`ibus,dbus,pin,alert,misc,icram,scrkey,regime`) whose events are written; `all` = every known source; a name outside the list is `uvm_fatal GEN_EXPORT`; records and markers are always written when the file knob is set | `all` |
| `+gen_export_flush_every=<n>` | `PLUSARG_EXPORT_FLUSH_EVERY` | debug-only: `$fflush` after every n-th `R` line, for triage of abnormal ends (refused in measured runs like every debug-only knob) | 0 (off) |

Bridge command: `EXPORT_FLUSH` (`GEN_CMD_EXPORT_FLUSH`, code 12, last in `bridge_cmds` so the existing codes keep
their values; `CMD["EXPORT_FLUSH"]` in Python), arguments none; the sink's flush sequence number returns in
`peek_data` with the ack, the way `MEM_PEEK` returns a word; `GenBridge.export_flush()` wraps it. Yaml keys (top
level): `export_record_fields`, `export_counter_fields`, `export_events`.

## 4. Wave-level behaviour

- Header: `$fopen` and the header lines are written in `start_of_simulation_phase` (time 0), before the first record.
- `R` lines: written at the posedge where `rvfi_valid` is 1, in the monitor's active-region step after its
  `records++` and `ap.write`. `I` lines: written at the posedge where `rvfi_ext_irq_valid` is 1 and was 0 at the
  previous posedge (the level is sampled every cycle, the line is written once per rising edge, at the rise cycle,
  with or without a retirement in that cycle). `E` lines: written in the cycle of the event in the active region,
  drivers at the negedge and monitors at the posedge, so within one cycle the order is driver lines, then the record
  line, then monitor lines; `read()` requires non-decreasing cycles and nothing more about
  intra-cycle order. With the file knob absent the monitor neither formats nor hands over a line: the call
  `sink.write_record(gen_export_record_line(...))` sits inside the `sink != null && sink.enabled` guard
  (gen_rvfi_pkg.sv, run_phase), and the `I` line the same way; the `write_*` methods return at once as a second guard.
- One cycle base (addendum Section 3): the stamp of every line is the bridge's `cycle_count` (`gen_bridge_if`,
  counted at the posedge), read through `sink.cycle()` at write time by every writer, so a driver acting at the
  negedge stamps the cycle whose posedge just passed, the same base as the record cycle; a driver's own negedge
  counter is never used for a stamp. The record line's `cycle` is `gen_rvfi_if.cycle`, the interface's posedge counter,
  which equals the bridge count; the flush marker's `cycle=` is `bvif.cycle_count` read in `flush_export()`.
- Same-instant constraint (what makes `records == retired` exact): `flush_export()` runs inside
  `gen_cmd_dispatch::write()`, which `gen_bridge::run_phase` calls from its `@(vif.cmd_valid)` wake. That wake
  follows cocotb's deferred write of `cmd_valid`, i.e. it lands after the NBA region of the posedge in which
  `gen_bridge_if` counted the last retirement and after the monitor's active-region `write_record` of that posedge.
  The marker therefore carries the sink's counts and `bvif.evt_retired_count` and `bvif.cycle_count` read in the same
  function call; `flush_export()` is never called from a clocked process, and dispatching it at the ack posedge would
  break the equality by one. The `$fflush` and the `$ferror` check complete inside the call; `cmd_ack` toggles one
  posedge later, so an acked `EXPORT_FLUSH` means the marker and everything before it are on disk.
- End: the end marker, `$fflush`, `$ferror` and `$fclose` run in `extract_phase` (bottom-up, before the UVM report
  and before `gen_base_test::final_phase` toggles `finish_ack`), so the file is complete before Python is released
  from the finish handshake.
- Abnormal ends: (a) `uvm_fatal` anywhere (UVM `$finish`es before extract/final): no end marker, no `$fclose`; the
  file holds everything through the last `$fflush` plus whatever the simulator's buffer reached the OS; the run
  FAILS through the collected fatal, and if Python was awaiting an ack `GenBridge.cmd` raises its timeout
  `AssertionError` as well; the file is diagnostic only. (b) the alive watchdog `$fatal`: as (a). (c) a timeout on
  the `EXPORT_FLUSH` ack: `GenBridge.cmd` raises `AssertionError` (test FAIL); the file state is that of the last
  completed flush. (d) `$ferror` non-zero after a flush or at the end: `uvm_error GEN_EXPORT`, the run FAILS;
  `read()` is the second line of defence. `+gen_export_flush_every=<n>` narrows the window of (a) and (b) for
  triage.

## 5. Checkers

None: the export is observation only and carries no pass/fail check of its own (no checker id, no `+gen_chk_`
knob). The consumer checks are the tests'. Format-internal presence rules in `read()` (T-141, one mutation each): per
enabled bus `#req - #gnt` is 0 or 1 (MUT-I) and `0 <= #gnt - #rvalid <= GEN_<BUS>_MAX_OUTSTANDING` (MUT-J), beside
the `#gnt == <bus>_grants` marker rule (MUT-G), so a silent req or rvalid writer is visible from the file alone. As
built in `gen_ut_export.py`: the misc stamp rule (Critic step-2 L-4, landing 2a): the `misc crash_dump_current_pc` line
carrying the first record's pc_rdata is stamped `MISC_CURRENT_PC_LINE_OFFSET` = 2 cycles before that record
(crash_dump_o.current_pc = pc_id, the boot jump spends one cycle in ID and one in WB; MUT-L is the misc writer reporting
the previous sample's value); the header field list equals the rendered list; the marker's `records` equals its
`retired` and the parsed `R` count (through `read()`); `order` increments by one and every line has its header's field
count (through `read()`); two flushes are issued and the
early flush's records are a prefix of the final one; the bridge's `evt_retired_count` read after the ack is `>=`
the marker's `retired`; the first record's `pc_rdata` is the boot page + 0x80; every `R` store to the tohost
address carries the value 1 and their count does not exceed the memory model's independent `evt_eot_count`; pc
continuity `pc_rdata[k+1] == pc_wdata[k]` between consecutive records with no `I` line between them, skipping
trap records (this RTL reports `pc + 4` as the `pc_wdata` of a trap record, ruling F-RVFI-010), mret and dret
records (matched by `insn` encoding; their `pc_wdata` is the next sequential address, plan convention C-1, not the
return target), debug-mode changes and Zcmp micro-op records that are not the sequence's last. The addendum's count
of `cm.push` / `cm.pop` encodings in `ext_exp_insn` is not among the built checks.

## 6. Failure path and diagnostics

- `uvm_fatal GEN_EXPORT`: `cfg` or `bridge_vif` missing from `uvm_config_db` (build); `+gen_export_sources` names a
  source outside `GEN_EXPORT_SOURCES` (build; the message lists the known set); `register_row` with an unknown row or
  a row of an inactive source; an active row with no registered writer at start of simulation, in every run (`emitted
  row <source>/<event> has no registered writer in this build`; MUT-K); the export file cannot be opened (`$fopen` returns 0; never a silent run without a file); `EXPORT_FLUSH`
  issued without `+gen_export_file`.
- `uvm_warning GEN_EXPORT`: `+gen_export_sources` names a known source that has no writer in this build (icram).
- `uvm_error GEN_EXPORT`: `$ferror` non-zero after a flush (`write error after flush: <text>`) or at the end
  (`write error at end: <text>`).
- Python `AssertionError` from `read()` (message prefix `GEN_EXPORT:`; the rule that failed is named in the text,
  with the line number where one applies) and from `GenBridge.cmd` on an ack timeout (`GEN_BRIDGE: no edge on
  cmd_ack for EXPORT_FLUSH ...`). Every Python-side string is ASCII (TB_CONTRACT Section 4).
- Diagnostics: `uvm_info GEN_EXPORT` at open (`export file <path> open; sources: <csv or (none)>`) and in
  `report_phase` (`export: records=<n> markers=<m> events=<e> flushes=<f>`, decimal); the monitor's `GEN_RVFI_MON
  records=<n> irq_markers=<m>` report must agree with it; an `EXPORT_FLUSH` counts into `dispatch.routed` (the
  `GEN_ENV` report's `commands routed`). `read(path, None)` after the run reads to the end marker for triage.

## 7. Coverage hooks

None: no covergroup samples the export, and the fcov-expectation rule is not applicable to the check-tier unit test
(standing ruling); the Test Writer's tests that consume the file carry their own manifests.

Witness command (addendum Section 9; planned, build step 3, nothing of it exists in the yaml or the env yet): a test
whose cycle-level clause passed against the export records the fact through the bridge command `COV_WITNESS`
(appended to `bridge_cmds`; arg0 = the rendered index of the marked test-plan item), routed by `gen_cmd_dispatch` to
the covergroup `gen_cg_wit_cycle_clause` (plan id CG-WIT-001, `gen_fcov_pkg`), one bin per marked item, the bin list
rendered from `gen_trace_tp_bin.csv`. Coverage only: no checker reads it, and the sample is the command itself, which
a test issues only after its own clause passed.

Mutation classes the export's CONSUMER catches (for the Test Writer; each with hidden referees inert,
`+gen_chk_all=0`, and an ablation control with the named rule disabled):

| Class | Mutation form | Named detector |
|---|---|---|
| dropped record | `records++` runs but one `R` line is skipped | `read()`: `R` count != marker `records`, and the `order` gap |
| swapped records | two adjacent `R` lines exchanged | `read()`: `order` not strictly +1 |
| stale or missing flush marker | the marker's `$fflush` suppressed or the marker not written; or the marker written for the first flush only while the test flushes twice | `read(path, seq)`: no complete marker with that `seq` (an earlier marker does not satisfy it), or marker `records` differs from the parsed count |
| corrupted field | the monitor writes `pc_wdata + 2` | the test's pc-continuity check between consecutive `R` lines |
| program contradiction | image swapped, or `+gen_boot_addr` moved so the first `R` line is not boot page + 0x80 | the test's content assertions (boot pc, tohost stores), not `read()` |
| dropped event / wrong event cycle | a writer skips a `gnt` line while its counter increments; a `fetch_enable` line stamped `cycle + 1` | owed with the event writers: the fixture's independent count against the bridge's grant counters and its cycle correlation |

The existing `rvfi_order` checker is NOT relied on (it is off under `+gen_chk_all=0`); `read()` carries its own
order rule. Executed: MUT-A..F in `dv/auto_dv/mutations/gen_mut_export.md` (every one CAUGHT with its ablation
control SURVIVED; the runs predate the radix edit, so the markers were hex then and are decimal now, the mutated
statements unchanged); MUT-G / MUT-H with the event part.

## 8. Cost and retention

Cost: one `$fwrite` per record; the addendum's estimate is about 220 bytes per record (about 320 with counters),
an upper bound because `%0h` writes no leading zeros. Measured on the green runs under
`dv/auto_dv/work/tb-infra/out_t080d/` (36 fields, two flushes per run): the Zc program, 175 records,
`export_zc/gen_export.txt` 22133 bytes (about 126 bytes per record, 180 lines: two header lines, the seq=1 marker of
the early flush, 175 `R`, the seq=2 marker, the end marker) and `export_zc_counters/gen_export.txt` 29971 bytes
(about 171 bytes per record); the riscv-dv seed-7 program, 2008 records, `export_s7/gen_export.txt` 232434 bytes
(about 116 bytes per record). The addendum's Section 3 quotes the earlier 34-field build out_t080 (21144, 28982 and
219090 bytes; 2002 seed-7 records with the end marker only). With every active source on (the landing-1c build,
`gen_fu_l1c_export_s7_*`): the seed-7 program's file is 791905 bytes over 17807 lines, 2008 `R` lines at about 115
bytes each and 15766 `E` lines at about 35 bytes each (ibus 9502, misc 4587, dbus 1650, scrkey 20, alert 4, pin 3);
the event lines are 89 percent of the lines and 70 percent of the bytes, the ibus rows and the misc rows (irq_pending
and core_busy toggle often) dominating. Wall clock (VCS CPU time from the retained out_t080d sim.log files, recorded
in `dv/auto_dv/evidence/gen_tdd_export.md`): the Zc lock-step run 0.29 s without and 0.26 s with the knob, the seed-7
lock-step run 0.52 s and 0.54 s; with events on, the seed-7 export run 0.64 s against 0.54 s for the lock-step run
without the knob on the same build (landing 1c), i.e. about a tenth of a second at these counts.

Retention (a flow policy, ruled by Runtime on 2026-09-03 and quoted from the addendum's Section 3): "the flow never
deletes inside a run directory during a regression and never prunes silently; the export file is kept on purposes 1
to 3 (bring-up, component change, reproduction) and on any non-PASS verdict; on purpose-4 full regressions it is
pruned after the manifest is written for runs whose verdict is PASS or RED-OK, unless the testlist entry says
`keep_artifacts: true`; every pruned path is listed in result.yaml under `pruned_artifacts`." Runtime documents the
mechanism in `dv/auto_dv/docs/gen_runtime_api.md` Section 9. The file lives in the run directory next to `sim.log`.

## 9. At build

Done: the bus, ctrl, scrkey, irq, debug, misc and regime writers with per-row registration (T-141), the grant
counters and marker fields with `read()`'s gnt rule (MUT-G), the stamp rule (MUT-H), the bus count rules (MUT-I,
MUT-J), the registration fatal (MUT-K) and the retained runs of the regime phase, pin debug_req and pin irq_nm rows
(gen_ut_export_rows, CM8-M-3). Open: the icram writers with the RAM model's port (build step 3), the `COV_WITNESS`
command with CG-WIT-001, and a stamp rule for the misc/alert rows (first crash_dump_current_pc line against the first R
record; Critic step-2 L-4). The consumer-side helper that the Test Writer's template wraps builds its
namedtuples from `read()` (Section 2), never from a re-typed column list.
