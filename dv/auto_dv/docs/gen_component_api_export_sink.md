# Component API: gen_export_sink (record and event export)

Owner: tb-infra. Status: written from the code as built (2026-09-03). Design: `dv/auto_dv/docs/
gen_rvfi_export_addendum.md` version 4a (embedded as gen_tb_architecture.md Section 9); where the code and the
addendum differ this document describes the code and says so in one sentence at the place of the difference.
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
marker and at the end. Event sources register through `register_source(name)` and gate every line through
`source_on(name)`; the header's `sources=` field lists the sources that are registered AND enabled by
`+gen_export_sources`. In this landing no writer registers a source (the bus, ctrl, scrkey and icram writers and the
step-2b writers are not connected yet), so `sources=` is empty, no `# events` row is written and `events` stays 0;
the log line at open reads `export file <path> open; sources: (none)`. The line text is formatted by functions
rendered from the yaml (`gen_export_record_line` in `dv/auto_dv/env/gen_export_record_line.svh`, one
`gen_export_line_<source>_<event>` per event row in `dv/auto_dv/env/gen_export_event_lines.svh`), whose argument
names are the field names, so the SV side cannot reorder a column. The addendum names one include
`gen_export_fields.svh` and the sink methods `line(kind, text)` and `flush()`; as built these are the two rendered
includes named above and the methods `write_record` / `write_marker` / `write_event` and `flush_export()`. The
Python reader is `dv/auto_dv/gen_tb/gen_export.py` (`read(path, seq, counters=False)`), the bridge wrapper is
`GenBridge.export_flush()` (`dv/auto_dv/gen_tb/gen_bridge.py`), and the consumer test is
`dv/auto_dv/gen_tb/gen_tests/gen_ut_export.py`.

## 2. Files and how to call it

SV: `dv/auto_dv/env/gen_export_pkg.sv` (package `gen_export_pkg`, class `gen_export_sink`; includes the rendered
`dv/auto_dv/env/gen_export_event_lines.svh`); `dv/auto_dv/env/gen_export_record_line.svh` (rendered; included inside
`gen_rvfi_pkg` after `gen_rvfi_txn`). Both includes, the `gen_tb_pkg` strings `GEN_EXPORT_RECORD_FIELDS`,
`GEN_EXPORT_COUNTER_FIELDS`, `GEN_EXPORT_SOURCES` and the functions `gen_export_source_known(s)` and
`gen_export_event_header(source)` (the `# events` rows of one source, newline-terminated), and the Python tuples
`EXPORT_RECORD_FIELDS`, `EXPORT_COUNTER_FIELDS`, `EXPORT_SOURCES`, `EXPORT_EVENTS` in `dv/auto_dv/gen_tb/gen_knobs.py`
are rendered by `dv/auto_dv/tb/gen_knobs_codegen.py` from the yaml keys `export_record_fields`,
`export_counter_fields` and `export_events` of `dv/auto_dv/tb/gen_tb_knobs.yaml` (one origin for the column order;
`dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py` asserts the renderings equal the yaml and that every event row has its
line function). Wiring (`gen_env_pkg.sv`): `gen_env` creates `sink`, and `connect_phase` sets `rvfi_mon.sink`,
`dispatch.sink` and `dispatch.bvif`; the dispatcher route is `GEN_CMD_EXPORT_FLUSH: bvif.peek_data =
sink.flush_export()`.

SV writer contract (an event source, when it lands): call `sink.register_source("ibus")` once at build or connect
time (an unknown name is `uvm_fatal GEN_EXPORT`), then per event `if (sink.source_on("ibus"))
sink.write_event(gen_export_line_ibus_gnt(cycle, addr, we, be, outstanding_after));` (no formatting cost when the
source is off). The RVFI monitor calls `sink.write_record(gen_export_record_line(t, cfg.export_counters))` per record
and `sink.write_marker("I ...")` per marker (gen_component_api_rvfi_monitor.md Section 8).

Python: `seq = await bridge.export_flush()` (issues `EXPORT_FLUSH`, default ack timeout 200 cycles, returns the
sequence number carried in `peek_data`), then `data = gen_export.read(path, seq, counters=<bool>)`. `read()` returns
`Export(header, records, markers, events, flush)`: `header` is the dict of the first line's `key=value` tokens;
`records` is a list of namedtuples whose field names are `EXPORT_RECORD_FIELDS` (plus `EXPORT_COUNTER_FIELDS` when
`counters=True`), so `data.records[0].pc_rdata` reads by name; `markers` is a list of `Marker(cycle, ext_pre_mip,
ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode)`; `events` is a list of `Event(cycle, source,
event, fields)` with `fields` a tuple in the header row's order; `flush` is `Flush(seq, records, retired, markers,
events, cycle)` from the marker. The caller states `counters` and the header must agree; the addendum let the header
alone decide the namedtuple, as built the reader asserts `counters=` equals the caller's flag. `read(path, None)`
reads to the `# end` marker (post-run diagnostics only, never the basis of a pass). `read()` has no simulator access
and every failure is an `AssertionError` whose message starts with `GEN_EXPORT:`.

### 2a. File format (version 1)

```
# gen_export v1 seed=<n> build_config=<name> counters=<0|1> sources=<csv of registered and enabled sources> fields=<csv of R field names>
# image <path as given to +gen_mem_image, rest of line, or the word none>
# events <source> <event> <csv of field names>     one row per (source, event) of every registered and enabled source
R <field values in header order>                    one line per retired record
I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req> <ext_debug_mode>   one line per rising edge of rvfi_ext_irq_valid, at the rise cycle
E <cycle> <source> <event> <field values in the row's order>   one line per boundary event
# flush seq=<s> records=<n> retired=<r> markers=<m> events=<e> cycle=<c>   written by EXPORT_FLUSH; s = the number the command returns; r = the bridge's evt_retired_count read in the same call
# end records=<n> retired=<r> markers=<m> events=<e>                       written in extract_phase
```

`fields` (every `gen_rvfi_txn` field except the CHERIoT carve-out, in this order): `order, pc_rdata, pc_wdata, insn,
trap, halt, intr, mode, ixl, rs1_addr, rs1_rdata, rs2_addr, rs2_rdata, rd_addr, rd_wdata, mem_addr, mem_rmask,
mem_wmask, mem_rdata, mem_wdata, ext_pre_mip, ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode,
ext_rf_wr_suppress, ext_ic_scr_key_valid, ext_irq_valid, ext_exp_valid, ext_exp_insn, ext_exp_last, ext_mcycle,
cycle` (34 names); with `counters=1` the 20 names `mhpmcounter3..mhpmcounter12, mhpmcounter3h..mhpmcounter12h` follow.
Not exported: `rs3_addr`, `rs3_rdata`, the `*_rcap` fields and `mem_is_cap` (constant in this configuration; the
`rvfi_cap_quiet` check owns them). Every value of an `R`, `I` or `E` line and every value of the flush and end
markers is hex without prefix and without leading zeros (`%0h`; a flag is `0` or `1`); the header's `seed=` and
`counters=` are decimal. A value with X or Z renders as `x`/`z` characters and `read()` fails on the non-hex token.
`R` lines are in retirement order (`order` ascending). The `# image` line is rest-of-line, so a path with spaces
cannot break the tokeniser. A generic event row renders the literal token `<name>` in its header row (for example
`# events pin <name> value`) and the event's own name in the `E` line. The `# events` rows are written only for
registered and enabled sources; the addendum shows one row per rendered table row, as built a file of this landing
has none.

### 2b. Completeness rule of read(path, seq), as implemented

1. The file is read whole and split on newline; fewer than three lines is `has no header`.
2. Line 1 must start with `# gen_export v1 `; its `counters=` must equal the caller's `counters` flag and its
   `fields=` must equal the comma-joined rendered `EXPORT_RECORD_FIELDS` (plus `EXPORT_COUNTER_FIELDS` when
   `counters`). Line 2 must start with `# image `.
3. Every following line that starts with `# events ` is a header row: its (source, event) must be a row of the
   rendered `EXPORT_EVENTS` with the same field list, and its source must appear in the header's `sources=`.
4. The marker is the FIRST line after the header rows that starts with `# flush ` and carries `seq=<seq in hex>`
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
   tokens, its (source, event) must be a header row, or the source's generic `<name>` row, and its value count must
   equal that row's field count; any other first token is `unknown line kind`. The cycle of each line (the `cycle`
   field of an `R` line, the first value of an `I` or `E` line) must be non-decreasing across all three kinds;
   nothing is required about the order of lines inside one cycle.
7. The parsed counts must equal the marker: `R` lines == `records`, `I` lines == `markers`, `E` lines == `events`.

Not part of `read()`: the test's own read of `evt_retired_count` after the ack is a `>=` check against the marker's
`retired` (gen_ut_export.py does this), and every program-derived check (boot pc, tohost stores, pc continuity) is
the test's. A missing file raises the Python `FileNotFoundError` from `Path.read_text()` before any rule runs.

### 2c. Event channel rows (addendum Section 8)

The yaml `export_events` table, one line function per row in `gen_export_event_lines.svh`. NOT yet connected in this
landing: the bus, ctrl, scrkey and icram writers (whose components exist) and the step-2b writers (pin, alert, misc,
regime, whose components do not exist yet); the header's `sources=` field stays empty until a writer registers. The
bridge fields `evt_ibus_grants` / `evt_dbus_grants` that the addendum names for the fixture's independent count are
not in `gen_bridge_if` yet.

| source | event | fields | writer | when |
|---|---|---|---|---|
| ibus, dbus | gnt | addr, we, be, outstanding_after | gen_bus_driver | the cycle the grant is driven (one per beat) |
| ibus, dbus | rvalid | addr, we, err, intg_injected, outstanding_after | gen_bus_driver | the cycle the response is driven (one per beat) |
| pin | irq_software, irq_timer, irq_external, irq_fast<n>, irq_nm, debug_req | value | irq / dbg drivers (step 2b) | every value change (rise and fall) |
| pin | fetch_enable, mcounteren_writable | value (MuBi encoding) | gen_ctrl_driver | every value change |
| alert | alert_minor, alert_major_bus, alert_major_internal, double_fault_seen | value | gen_misc_monitor (step 2b) | every value change (a one-cycle pulse is a rise line and a fall line) |
| misc | core_busy | value (MuBi) | gen_misc_monitor | every value change |
| misc | crash_dump | field, value | gen_misc_monitor | every change of a crash_dump_o field (current_pc, next_pc, last_data_addr, exception_pc, exception_addr) |
| icram | inject | way, index | gen_icache_ram (announcement port) | the lookup cycle of an injected ECC error (the expected-alert feed of C3.4) |
| scrkey | req, valid | value | gen_scrkey_driver | every change of ic_scr_key_req_o / ic_scr_key_valid_i |
| regime | phase | knob_id, value_idx, phase_idx | gen_cmd_dispatch (REGIME_SET consumer, step 2b) | the cycle a phase is applied |

As rendered, the yaml carries the `ibus`/`dbus` `gnt` and `rvalid` rows, `icram inject` and `regime phase` as fixed
rows, and ONE generic `<name>` row with the single field `value` for each of `pin`, `alert`, `misc` and `scrkey`
(functions `gen_export_line_pin_any(cycle, name, value)` and so on, the event token passed as a string), so the
per-event rows of the table above are the names those writers pass; the addendum's `misc crash_dump` row with the
two fields `field, value` is `misc <name> value` as built (one line per changed field, the field name as the event
token).

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
  with or without a retirement in that cycle). `E` lines (when the writers land): written in the cycle of the event
  in the active region, drivers at the negedge and monitors at the posedge, so within one cycle the order is driver
  lines, then the record line, then monitor lines; `read()` requires non-decreasing cycles and nothing more about
  intra-cycle order. With the file knob absent the monitor still formats the `R` line string and the sink discards
  it; the addendum states that no code path differs without the knob, as built the formatting runs and only the
  write is skipped.
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
knob). The consumer checks are the tests'. As built in `gen_ut_export.py`: the header field list equals the
rendered list; the marker's `records` equals its `retired` and the parsed `R` count (through `read()`); `order`
increments by one and every line has its header's field count (through `read()`); two flushes are issued and the
early flush's records are a prefix of the final one; the bridge's `evt_retired_count` read after the ack is `>=`
the marker's `retired`; the first record's `pc_rdata` is the boot page + 0x80; every `R` store to the tohost
address carries the value 1 and their count does not exceed the memory model's independent `evt_eot_count`; pc
continuity `pc_rdata[k+1] == pc_wdata[k]` between consecutive records with no `I` line between them, skipping
trap records (this RTL reports `pc + 4` as the `pc_wdata` of a trap record, ruling F-RVFI-010), debug-mode changes
and Zcmp micro-op records that are not the sequence's last. The addendum's count of `cm.push` / `cm.pop`
encodings in `ext_exp_insn` is not among the built checks.

## 6. Failure path and diagnostics

- `uvm_fatal GEN_EXPORT`: `cfg` or `bridge_vif` missing from `uvm_config_db` (build); `+gen_export_sources` names a
  source outside `GEN_EXPORT_SOURCES` (build; the message lists the known set); `register_source` with an unknown
  name; the export file cannot be opened (`$fopen` returns 0; never a silent run without a file); `EXPORT_FLUSH`
  issued without `+gen_export_file`.
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
order rule. Records: `dv/auto_dv/mutations/gen_mut_export.md`, which TB Infra writes after the mutation runs finish
(not present yet).

## 8. Cost and retention

Cost: one `$fwrite` per record; the addendum's estimate is about 220 bytes per record (about 320 with counters),
an upper bound because `%0h` writes no leading zeros. Measured on the green runs under
`dv/auto_dv/work/tb-infra/out_t080/`: the Zc program, 175 records, `export_zc/gen_export.txt` 21144 bytes (about
120 bytes per record, 179 lines: two header lines, 175 `R`, one flush marker, the end marker) and
`export_zc_counters/gen_export.txt` 28982 bytes (about 165 bytes per record); the riscv-dv seed-7 program, 2002
records, `lockstep_s7_export/gen_export.txt` 219090 bytes (about 109 bytes per record, end marker only: that test
issues no flush). Events (none written yet) are estimated at about 100 bytes each; on the seed-7 program the bus
rows would add about 3500 lines. The wall-clock delta with and without the knob that the addendum's Section 5 asks
for is not recorded in an evidence file yet.

Retention (a flow policy, ruled by Runtime on 2026-09-03 and quoted from the addendum's Section 3): "the flow never
deletes inside a run directory during a regression and never prunes silently; the export file is kept on purposes 1
to 3 (bring-up, component change, reproduction) and on any non-PASS verdict; on purpose-4 full regressions it is
pruned after the manifest is written for runs whose verdict is PASS or RED-OK, unless the testlist entry says
`keep_artifacts: true`; every pruned path is listed in result.yaml under `pruned_artifacts`." Runtime documents the
mechanism in `dv/auto_dv/docs/gen_runtime_api.md` Section 9. The file lives in the run directory next to `sim.log`.

## 9. At build

Open items of this landing: connect the bus, ctrl, scrkey and icram writers (register the source, gate with
`source_on`, one line function call per event) and add the bridge grant counters, then the step-2b sources with
their components, each with its own red run; write `dv/auto_dv/mutations/gen_mut_export.md` from the mutation runs;
record the wall-clock delta. The consumer-side helper that the Test Writer's template wraps builds its namedtuples
from `read()` (Section 2), never from a re-typed column list.
