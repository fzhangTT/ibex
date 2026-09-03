# RVFI record export (T-080 design addendum, for gen_tb_architecture.md Section 9)

Author: tb-infra, 2026-09-03. Version 3a (v3 plus Runtime's retention ruling and the debug-only landing rule, text only): version 2a plus the cross-model plan review's findings
(`dv/auto_dv/reviews/2026-09-03-claude-plan-gen_rvfi_export_addendum.md`, APPROVE-WITH-CHANGES; rows answered in
`dv/auto_dv/evidence/gen_critic_response_rvfi_export.md`). Status: text for the DV Lead's re-embed and the
Orchestrator's approval; no SV or Python exists yet. Consumer: Test Writer (fire-checks over per-record RVFI facts
in measured runs; asks 4 and 5). Scope rules it satisfies: RVFI is a define-gated DUT boundary interface (probe
register row RVFI, `boundary`), so the export is not a probe under DV_prompt Section 7 (modelling and checking);
Python reads a file once, never a signal per cycle (A-01); the knob is a normal plusarg, usable in measured runs.

## 1. What it is

`gen_rvfi_monitor` writes one ASCII line per `gen_rvfi_txn` and one per interrupt-marker rising edge to a file
named by `+gen_rvfi_export=<path>` (kind string, default unset = off; a relative path is relative to the run
directory, which is the simv working directory in both `gen_run.py` and `gen_tb_local.sh`). The knob is OPT-IN
per testlist entry: an entry whose test reads records sets `+gen_rvfi_export=gen_rvfi_records.txt` (the Test
Writer's template adds it when the test declares that it consumes records); an entry without it writes nothing
and runs no export code. A bridge command `RVFI_FLUSH` (appended to `bridge_cmds`, so existing codes keep their
values) makes the monitor write a flush marker and `$fflush` before the bridge acks, so Python parses a complete
prefix of the file inside its checks, before the finish handshake (TB_CONTRACT Section 2 ordering). The Python
side is one module, `dv/auto_dv/gen_tb/gen_rvfi_export.py`: `read(path)` returns the records and markers of the
prefix ending at the last complete flush marker, enforces the format rules of Section 3, and fails loud
(AssertionError, the only Python-side failure mechanism) on any violation.

## 2. File format (version 1)

```
# gen_rvfi_export v1 seed=<n> build_config=<name> counters=<0|1> fields=<comma-separated field names>
# image <path as given to +gen_mem_image, rest of line, or the word none>
R <field values in header order, hex without prefix, flags 0/1>            one line per retired record
I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req> <ext_debug_mode>   one line per RISING EDGE of rvfi_ext_irq_valid, at the rise cycle
# flush records=<n> retired=<r> markers=<m> cycle=<c>                          written by RVFI_FLUSH; r = the bridge's evt_retired_count read in the same call
# end records=<n> retired=<r> markers=<m>                                      written in extract_phase (Section 3)
```

`fields` (every `gen_rvfi_txn` field, in this order): `order, pc_rdata, pc_wdata, insn, trap, halt, intr, mode,
ixl, rs1_addr, rs1_rdata, rs2_addr, rs2_rdata, rd_addr, rd_wdata, mem_addr, mem_rmask, mem_wmask, mem_rdata,
mem_wdata, ext_pre_mip, ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode, ext_rf_wr_suppress,
ext_ic_scr_key_valid, ext_irq_valid, ext_exp_valid, ext_exp_insn, ext_exp_last, ext_mcycle, cycle`; with
`counters=1` the 20 names `mhpmcounter3..mhpmcounter12, mhpmcounter3h..mhpmcounter12h` follow. Not exported:
`rs3_addr`, `rs3_rdata`, the `*_rcap` capability fields and `mem_is_cap` (CHERIoT carve-out, constant in this
configuration; the `rvfi_cap_quiet` check owns them). The two field lists have one origin: yaml keys
`rvfi_export_fields` / `rvfi_export_counter_fields` in `gen_tb_knobs.yaml`, rendered as
`GEN_RVFI_EXPORT_FIELDS` / `GEN_RVFI_EXPORT_COUNTER_FIELDS` (gen_tb_pkg.sv, the header the monitor writes) and
`RVFI_EXPORT_FIELDS` / `RVFI_EXPORT_COUNTER_FIELDS` (gen_knobs.py, the header `read()` requires), so a field added
on one side fails the other side's header check instead of shifting columns silently; the codegen's top-level
schema and `gen_ut_knobs_codegen.py` are extended for the two keys (Section 4). The `image` header line is
rest-of-line, so a path with spaces cannot break the tokeniser. Values are written with `%h`/`%0d`; a value
with X or Z renders as `x`/`z` characters and `read()` fails loud on any non-hex token (an X on RVFI is a DUT or
TB defect, never something to interpret). `R` lines are written in retirement order (`rvfi_order` ascending).
`I` lines: `rvfi_ext_irq_valid` is a LEVEL (rtl-arch T-053 rule X-16, plan convention C-13: it rises four cycles
after the interrupt decision and stays high until about two cycles after the handler's first instruction enters
ID), so exactly one `I` line per rising edge, at the rise cycle, never one per high cycle; the monitor's
`ap_irq` publication and `irq_markers` count follow the same rule (the step-2a monitor publishes on every high
cycle without a retirement, a defect corrected in this landing; it never fired, irq_markers=0 in every retained
run). The 20 counter words (`ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]`, today sampled into `gen_rvfi_if`
but not into `gen_rvfi_txn`) are added to `gen_rvfi_txn` and appended to every `R` line only under
`+gen_rvfi_export_counters=1` (the PMC/DIT/BTALU fire-checks need them; the ISA/CMP/BIT groups do not), so the
default line stays about 220 bytes.

## 3. Guarantees, completeness rule and failure behaviour

- Open: `$fopen` in `start_of_simulation_phase`; failure is `uvm_fatal GEN_RVFI_EXPORT` (never a silent run
  without a file). The two header lines are written before the first record.
- Flush and the same-instant pair: `RVFI_FLUSH` is routed by `gen_cmd_dispatch` to `gen_rvfi_monitor::flush()`,
  which reads its own record count and the bridge's `evt_retired_count`, writes the flush marker with both,
  calls `$fflush`, then checks `$ferror(fd)` (a non-zero code is `uvm_error GEN_RVFI_EXPORT`). Design constraint
  that makes `records == retired` exact: `flush()` runs from the bridge's `@(vif.cmd_valid)` wake
  (gen_env_pkg.sv, gen_bridge::run_phase), which follows cocotb's deferred write, i.e. after the NBA region of
  the posedge in which the interface counted the last retirement and after the monitor's active-region
  `records++` of that posedge; it is never called from a clocked process, and dispatching it at the ack posedge
  would break the equality by one. The dispatcher call completes before the bridge toggles `cmd_ack` one posedge
  later.
- Completeness rule (`read()`): locate the LAST COMPLETE flush marker (or the end marker in a post-run read);
  parse only the prefix before it and ignore every byte after it (at the ack posedge the monitor may already
  have written record N+1 into the buffer, which a buffer-full flush can put on disk); require the header, the
  image line, `records == retired` from the marker itself, the number of parsed `R` lines equal to `records`,
  `order` strictly +1 across `R` lines, the field count of every line equal to the header's, and hex-only
  tokens. Python's own read of `evt_retired_count` after the ack is a `>=` check against the marker's `retired`.
  Every violation, a missing file or a header whose field list differs from the rendered one is a Python
  assert (collected failure). No "last line must be a marker" rule exists for flush reads.
- Close: the end marker and `$fclose` (after `$fflush` and `$ferror`) are written in `extract_phase`
  (bottom-up, before the UVM report and before `gen_base_test::final_phase` toggles `finish_ack`), so the file
  is complete before Python is released from the finish handshake.
- Abnormal ends: (a) `uvm_fatal` anywhere (UVM `$finish`es before extract/final): no end marker, no `$fclose`;
  the file holds everything through the last `$fflush` plus whatever the simulator's buffer reached the OS; the
  run FAILS through the collected fatal; if Python was waiting on an ack it raises the `GenBridge.cmd` timeout
  as well; the file is diagnostic only. (b) the alive watchdog `$fatal`: as (a). (c) a Python `with_timeout` on
  the `RVFI_FLUSH` ack: `GenBridge.cmd` raises AssertionError (test FAIL); the file state is that of the last
  completed flush. (d) `$ferror` after a flush: `uvm_error GEN_RVFI_EXPORT`, the run FAILS; `read()` is the
  second line of defence. A debug-only knob `+gen_rvfi_export_flush_every=<n>` (default 0 = off, refused in
  measured runs like every debug-only knob) `$fflush`es every n records for triage of abnormal ends.
- Cost and retention: with the knob absent no code path differs (the monitor's `ap` publishing is unchanged).
  With the knob on the cost is one `$fwrite` of about 220 bytes per record (about 320 with counters): 2000
  records = 0.4 MB, 1e6 records = 220 MB. The TDD evidence (Section 5) records the wall-clock delta with and
  without the knob on the Zc program and the riscv-dv seed-7 program. Retention: the file lives in the run
  directory next to sim.log. Retention is a flow policy, ruled by Runtime (2026-09-03): the flow never deletes
  inside a run directory during a regression and never prunes silently; the export file is kept on purposes 1 to 3
  (bring-up, component change, reproduction) and on any non-PASS verdict; on purpose-4 full regressions it is
  pruned after the manifest is written for runs whose verdict is PASS or RED-OK, unless the testlist entry says
  `keep_artifacts: true`; every pruned path is listed in result.yaml under `pruned_artifacts`. Runtime implements
  and documents this (gen_runtime_api.md Section 9) in the landing that brings the export knob; until then files
  stay.
- Isolation: the export is observation only, never a checker input on the SV side; the Python fire-checks that
  read it are the Test Writer's active checks (DV_prompt Section 7).

## 4. Interfaces added

| Item | Where | Note |
|---|---|---|
| knob `rvfi_export` (string, default unset) | gen_tb_knobs.yaml -> PLUSARG_RVFI_EXPORT, gen_knobs.py | normal knob (not debug-only), opt-in per testlist entry |
| knob `rvfi_export_counters` (bool, default 0) | gen_tb_knobs.yaml -> PLUSARG_RVFI_EXPORT_COUNTERS | appends the 20 hpm counter words to every R line; the header's `counters=` flag records it |
| knob `rvfi_export_flush_every` (int, default 0, debug_only; plusarg `gen_rvfi_export_flush_every`) | gen_tb_knobs.yaml; Runtime's loader reads the rendered gen_knobs.py table and refuses the testlist unless `debug_only_plusargs` equals it, so the landing that adds this knob carries Runtime's one-line testlist change in the same commit | periodic $fflush for triage of abnormal ends |
| yaml top-level keys `rvfi_export_fields`, `rvfi_export_counter_fields` | gen_tb_knobs.yaml; codegen `SCHEMA["top"]` extended; rendered `GEN_RVFI_EXPORT_FIELDS`, `GEN_RVFI_EXPORT_COUNTER_FIELDS` / `RVFI_EXPORT_FIELDS`, `RVFI_EXPORT_COUNTER_FIELDS`; `gen_ut_knobs_codegen.py` asserts both renderings equal the yaml lists and that every name is a `gen_rvfi_txn` field | one origin for the column order |
| `gen_rvfi_txn` extension | env/gen_rvfi_pkg.sv | `ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]` sampled from the interface only when the counters knob is on |
| bridge command `RVFI_FLUSH` (appended) | bridge_cmds; gen_cmd_dispatch -> gen_rvfi_monitor.flush() | ack implies flushed; flush() never runs from a clocked process |
| `gen_rvfi_monitor` file writer | env/gen_rvfi_pkg.sv | header lines, R/I lines, flush marker with the same-instant pair, `$ferror`, end marker and `$fclose` in extract_phase; one I line per rising edge |
| `dv/auto_dv/gen_tb/gen_rvfi_export.py` | Python reader: `read(path) -> (records, markers, flush)`; field access by name from `RVFI_EXPORT_FIELDS`; enforces Section 3 | ASCII only |
| `GenBridge.rvfi_flush()` | gen_bridge.py | issues RVFI_FLUSH; the test then calls `read()` |
| API document `gen_component_api_rvfi_monitor.md` | Section 3 (the three knobs), Section 6 (failure path: GEN_RVFI_EXPORT fatal/error, the completeness rule), a new Section 8 "RVFI record export" (format, guarantees, cost) | |

## 5. Trust triad for the build

1. TDD: `gen_tb/gen_tests/gen_ut_rvfi_export.py` written first: boots the Zc program, issues `RVFI_FLUSH`,
   calls `read()`, asserts the header fields equal the rendered list, `records == retired` from the marker, the
   `R`-line count equals `records`, `order` increments by one, every line has the header's field count, the first
   record's `pc_rdata` is boot page + 0x80, and the Zc program's known content (the count of `cm.push` /
   `cm.pop` encodings in `ext_exp_insn` of the folded records, and the tohost store as the last `R` line with
   `mem_wmask` F at the tohost address). Red on the T-068 tree (knob unknown: `GEN_UNKNOWN_PLUSARG` fatal), then
   green. The wall-clock delta with and without the knob is recorded from the same two programs.
2. Mutation-proof (the consumer check must catch a wrong file), every row with hidden referees inert
   (`+gen_chk_all=0`) and an ablation control (the named `read()` rule or fixture assertion disabled in the
   fixture, the mutation applied, PASS):
   - MUT-A field corruption: the monitor writes `pc_wdata + 2` (the MUT-007 form) -> caught by the fixture's pc
     continuity check between consecutive `R` lines.
   - MUT-B dropped record: `records++` runs but one `R` line is skipped -> caught by `read()`: `R`-line count !=
     `records`, and `order` gap.
   - MUT-C reordered records: two adjacent `R` lines swapped -> caught by `read()`: `order` not strictly +1.
   - MUT-D truncation: the flush marker's `$fflush` suppressed / marker not written -> caught by `read()`: no
     complete flush marker, or the marker's `records` differs from the parsed count.
   - MUT-E program contradiction (red fixture): the image swapped for one with a different `cm.push` count, or
     `+gen_boot_addr` moved so the first `R` line's `pc_rdata` is not boot page + 0x80 -> caught by the fixture's
     content assertions, not by `read()` (this is the "record set contradicts the program" red the Orchestrator
     asked for).
   Records in `dv/auto_dv/mutations/` (MUT-009..). The existing `rvfi_order` check is NOT relied on (it is off
   under `+gen_chk_all=0`); `read()` carries its own order rule.
3. fcov-expectation: not applicable (check-tier unit test outside the regression, per the standing ruling); the
   Test Writer's tests that consume the file carry their own manifests.

## 6. Resolved points

- DV Lead (2026-09-03, v2a): one `I` line per rising edge of the `rvfi_ext_irq_valid` level.
- Test Writer (2026-09-03, v2): `I` lines carry `ext_debug_req` and `ext_debug_mode`; counters behind
  `+gen_rvfi_export_counters=1`; the flush marker carries the bridge's retired count sampled at the same instant;
  the header names seed and image.
- Cross-model plan review (2026-09-03, v3): completeness from the marker not from line position; `read()` owns
  the count/order/field-count rules; drop, swap and program-contradiction mutations; every `gen_rvfi_txn` field
  listed or its exclusion stated; abnormal ends specified; `$ferror`; the same-instant constraint stated with its
  citation; opt-in knob, retention proposal and wall-clock measurement; image line rest-of-line, X/Z fail loud,
  codegen schema and unit test extension named; end marker in `extract_phase`.
- Runtime (2026-09-03): retention policy by purpose with `keep_artifacts: true` and `pruned_artifacts` in
  result.yaml (Section 3); the debug-only knob lands together with Runtime's testlist line (Section 4).
- Still open: whether the bus monitors' records (ask 4) share this knob family (`+gen_bus_export`) with the same
  header/flush/end discipline: proposed yes, as a later landing, not part of T-080.

## 7. Consumer requirements (Test Writer, 2026-09-03) and where the text meets them

| Requirement | Where |
|---|---|
| (1) normal knob `+gen_rvfi_export=<file>` set per entry to `<run dir>/gen_rvfi_records.txt` | Sections 1 and 4: string knob, not debug-only, opt-in per entry; a relative path resolves in the run directory |
| (2) one line per record and per irq marker with every field | Section 2: every `gen_rvfi_txn` field is listed (34 names) with the four CHERIoT-carve-out fields excluded by name; the 20 hpm counter words under `+gen_rvfi_export_counters=1`; `I` lines carry cycle, mip, NMI and debug flags, one per rising edge |
| (3) a bridge command that flushes and acks, so the file is complete before the finish handshake | Sections 1 and 3: `RVFI_FLUSH`, flush marker with the same-instant (records, retired) pair, `$fflush` and `$ferror` before `cmd_ack`; `read()` parses the prefix before the last complete marker |
| (4) the same knob/command discipline for the bus monitors' per-phase records later | Section 6: proposed as `+gen_bus_export`, a later landing |
| a `records()` template helper parsing the file into namedtuples | Section 2 fixes the line format; the helper builds its namedtuple from `RVFI_EXPORT_FIELDS` (+ counter fields when the header says `counters=1`) instead of re-typing the columns; `read()` is the enforcing layer the helper wraps |
