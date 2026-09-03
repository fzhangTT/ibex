# RVFI record export (T-080 design addendum, for gen_tb_architecture.md)

Author: tb-infra, 2026-09-03. Version 2 (revised after the Test Writer's comments: counters knob, flush marker carries the bridge count, I-line debug flags, self-identifying header). Status: DRAFT for DV Lead acceptance and the Orchestrator's cross-model
replan review; no SV or Python exists yet. Consumer: Test Writer (fire-checks over per-record RVFI facts
in measured runs; asks 4 and 5). Scope rules it satisfies: RVFI is a define-gated DUT boundary interface
(probe register row RVFI, `boundary`), so the export is not a probe under DV_prompt Section 7; Python
reads a file once, never a signal per cycle (A-01); the knob is a normal plusarg, usable in measured runs.

## 1. What it is

`gen_rvfi_monitor` writes one ASCII line per `gen_rvfi_txn` (and one per interrupt marker) to a file
named by `+gen_rvfi_export=<path>` (kind string, default unset = off; a relative path is relative to
the run directory, which is the simv working directory in both `gen_run.py` and `gen_tb_local.sh`; the
Test Writer's template passes `+gen_rvfi_export=gen_rvfi_records.txt`). A bridge command `RVFI_FLUSH`
(appended to `bridge_cmds`, so existing codes keep their values) makes the monitor write a flush marker
and `$fflush` before the bridge acks, so Python parses a complete prefix of the file inside its checks,
before the finish handshake (TB_CONTRACT Section 2 ordering). The Python side is one module,
`dv/auto_dv/gen_tb/gen_rvfi_export.py`: `read(path)` returns the records and markers, verifies the
header and the last flush marker, and fails loud (AssertionError) on any format or count mismatch.

## 2. File format (version 1)

```
# gen_rvfi_export v1 seed=<n> build_config=<name> image=<path or none> counters=<0|1> fields=order,pc_rdata,pc_wdata,insn,trap,intr,mode,rs1_addr,rs1_rdata,rs2_addr,rs2_rdata,rd_addr,rd_wdata,mem_addr,mem_rmask,mem_wmask,mem_rdata,mem_wdata,ext_pre_mip,ext_post_mip,ext_nmi,ext_nmi_int,ext_debug_req,ext_debug_mode,ext_rf_wr_suppress,ext_irq_valid,ext_exp_valid,ext_exp_insn,ext_exp_last,ext_mcycle,cycle[,mhpmcounter3..mhpmcounter12,mhpmcounter3h..mhpmcounter12h]
R <order> <pc_rdata> <pc_wdata> <insn> <trap> <intr> <mode> ... <cycle> [20 counter words]   one line per retired record, fields in header order, hex without prefix, flags 0/1
I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req> <ext_debug_mode>  one line per rvfi_ext_irq_valid marker without a retirement
# flush records=<n> retired=<r> markers=<m> cycle=<c>                          written by RVFI_FLUSH; r = the bridge's evt_retired_count read in the same call
# end records=<n> retired=<r> markers=<m>                                      written in final_phase
```
The field list is rendered from one Python/SV origin: the monitor writes the header from a
`GEN_RVFI_EXPORT_FIELDS` string in `gen_tb_pkg.sv` (plus `GEN_RVFI_EXPORT_COUNTER_FIELDS` when the
counters knob is on) and `gen_rvfi_export.py` imports the same strings from `gen_knobs.py` (both
rendered from `gen_tb_knobs.yaml`, new keys `rvfi_export_fields` / `rvfi_export_counter_fields`), so a
field added on one side fails the other side's header check instead of shifting columns silently, and
the `counters=` flag plus the field list tell the reader which layout every `R` line has. Records are
written in retirement order (`rvfi_order` ascending, checked by the existing `rvfi_order` check); an
`I` line is written at the cycle its marker is seen, so it sits between the records it separates.
Values are the `gen_rvfi_txn` fields as sampled (no interpretation). The 20 counter words
(`ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]`) are appended only under `+gen_rvfi_export_counters=1`
(the PMC/DIT/BTALU fire-checks need them; the ISA/CMP/BIT groups do not), so the default line stays
about 200 bytes. The header names the seed and the image so a records file kept as evidence is
self-identifying.

## 3. Guarantees and failure behaviour

- Open: `$fopen` in `start_of_simulation_phase`; failure is `uvm_fatal GEN_RVFI_EXPORT` (never a silent
  run without a file). A run with the knob set writes the header before the first record.
- Flush: `RVFI_FLUSH` is routed by `gen_cmd_dispatch` to `gen_rvfi_monitor::flush()`, which writes the
  flush marker and calls `$fflush`; the dispatcher call completes before the bridge toggles `cmd_ack`,
  so when Python sees the ack the file on disk holds every record retired up to that cycle.
- Completeness check: `read()` requires the header, requires the last line to be a flush or end
  marker, and asserts `records == retired` FROM THE MARKER ITSELF: `flush()` reads the monitor's record
  count and the bridge's `evt_retired_count` in the same function call, so the two are sampled at one
  instant (both derive from `rvfi_valid`; the interface count and the monitor's sample settle in the
  same time step). Python's own later read of `evt_retired_count` is only a `>=` check, because the
  bridge acks one posedge after the flush and a record can retire in between. Any mismatch, a missing
  file, a truncated file or a header whose field list differs from the rendered one is a Python assert
  (collected failure).
- Close: `$fclose` in `final_phase` after the end marker.
- Without the knob nothing is written and no code path differs (the monitor's `ap` publishing is
  unchanged); with the knob the cost is one `$fwrite` of about 200 bytes per record: 2000 records
  = 0.4 MB, 1e6 records = 200 MB (a long measured test declares the knob per entry; the flow keeps
  the file in the run directory next to sim.log).
- Isolation: the export is observation only, never a checker input on the SV side; the Python
  fire-checks that read it are the Test Writer's active checks (DV_prompt Section 7).

## 4. Interfaces added

| Item | Where | Note |
|---|---|---|
| knob `rvfi_export` (string, default unset) | gen_tb_knobs.yaml -> PLUSARG_RVFI_EXPORT, gen_knobs.py | normal knob (not debug-only) |
| knob `rvfi_export_counters` (bool, default 0) | gen_tb_knobs.yaml -> PLUSARG_RVFI_EXPORT_COUNTERS | appends the 20 hpm counter words to every R line; the header's `counters=` flag records it |
| yaml keys `rvfi_export_fields`, `rvfi_export_counter_fields` -> `GEN_RVFI_EXPORT_FIELDS`, `GEN_RVFI_EXPORT_COUNTER_FIELDS` / `RVFI_EXPORT_FIELDS`, `RVFI_EXPORT_COUNTER_FIELDS` | gen_tb_pkg.sv, gen_knobs.py | one origin for the column order |
| bridge command `RVFI_FLUSH` (appended) | bridge_cmds; gen_cmd_dispatch -> gen_rvfi_monitor.flush() | ack implies flushed |
| `gen_rvfi_monitor` file writer | env/gen_rvfi_pkg.sv | header, R/I lines, flush and end markers |
| `dv/auto_dv/gen_tb/gen_rvfi_export.py` | Python reader: `read(path) -> (records, markers, flush_count)`; field access by name | ASCII only |
| `GenBridge.rvfi_flush()` | gen_bridge.py | issues RVFI_FLUSH; the test then calls `gen_rvfi_export.read()`, which returns the records and the marker's (records, retired) pair |
| API document `gen_component_api_rvfi_monitor.md` Section 8 | knob, format, guarantees, cost | |

## 5. Trust triad for the build

1. TDD: `gen_tb/gen_tests/gen_ut_rvfi_export.py` written first: boots the Zc program, issues
   `RVFI_FLUSH`, reads the file, asserts `records == evt_retired_count`, header fields equal the
   rendered list, the first record's `pc_rdata` is boot page + 0x80, every `order` increments by one,
   and every `R` line has the header's field count. Red on the T-068 tree (knob unknown: `GEN_UNKNOWN_PLUSARG`
   fatal), then green.
2. Mutation-proof (the consumer check must catch a wrong export): monitor-side mutation of one exported
   field (pc_wdata + 2, the MUT-007 form) caught by the Python check on pc continuity; a truncated file
   (write of the flush marker suppressed) caught by the completeness check; ablation: with the checks
   removed from the fixture the mutations survive. Records in `dv/auto_dv/mutations/`.
3. fcov-expectation: not applicable (unit test outside the regression); the Test Writer's tests that
   consume the file carry their own manifests.

## 6. Open points for the reviewers

- Resolved with the Test Writer (2026-09-03): `I` lines carry `ext_debug_req` and `ext_debug_mode`;
  the counters ride behind `+gen_rvfi_export_counters=1`; the flush and end markers carry the bridge's
  retired count sampled at the same instant; the header names seed and image.
- Whether the bus monitors' records (ask 4) share this knob family (`+gen_bus_export`) with the same
  header/flush/end discipline: proposed yes, as a later landing, not part of T-080.

## 7. Consumer requirements (Test Writer, 2026-09-03) and where the draft meets them

| Requirement | Where |
|---|---|
| (1) normal knob `+gen_rvfi_export=<file>`, set by the flow or the template to `<run dir>/gen_rvfi_records.txt` | Section 1 and 4: string knob, not debug-only; a relative path resolves in the run directory (the simv working directory in both drivers), an absolute path is taken as given |
| (2) one line per record and per irq marker with every field | Section 2: `R` lines carry every `gen_rvfi_txn` field; the 20 hpm counter words are appended under `+gen_rvfi_export_counters=1` (Test Writer: needed by the PMC/DIT/BTALU fire-checks, whose entries set the knob), and the header's `counters=` flag plus field list make the layout explicit; `I` lines carry the marker's cycle, mip, NMI and debug flags |
| (3) a bridge command that flushes and acks, so the file is complete before the finish handshake | Section 1 and 3: `RVFI_FLUSH`, flush marker with the record count AND the bridge's retired count sampled in the same call (the equality check lives in the marker; Python's own read after the ack is `>=`, closing the one-posedge race the Test Writer pointed out), `$fflush` before `cmd_ack` |
| (4) the same knob/command discipline for the bus monitors' per-phase records later | Section 6: proposed as `+gen_bus_export` with the same header/flush/end format, a later landing |
| a `records()` template helper parsing the file into namedtuples | Section 2 fixes the line format; the field list is the rendered `RVFI_EXPORT_FIELDS` of gen_knobs.py, so the helper can build its namedtuple from it instead of re-typing the columns |
