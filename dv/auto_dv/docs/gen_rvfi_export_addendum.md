# Record and event export (T-080 design addendum, for gen_tb_architecture.md Section 9)

Author: tb-infra, 2026-09-03. Version history: 4c = the text committed at 4c4b9b8 (exact rows, C-2 owner set); 4c.1 = the text
at 50256f0 (Section 9 aligned to plan v2h and the rulings, three icram rows); 4d = THIS text, the step-2 landing (event writers
for every source but icram, file format version 2 with the grant counters, the active-source list, the r5 Part-2 rows D1..D6).
Version 4c (the Orchestrator's name for the r4 round): answers the replan reviews r2, r3 and r4 (`dv/auto_dv/reviews/2026-09-03-claude-replan-gen_rvfi_export_addendum-r2.md`, `-r3.md`, `-r4.md`, all REQUEST-CHANGES; r2: irq_pending and bus request events, grant counters sampled into the flush marker, one cycle base, mret/dret excluded from continuity, I lines bound to markers=, hex/decimal radix rule, rs3 exported, the Zc statement corrected) and the DV Lead's round-4 asks (COV_WITNESS, Section 9), plus the as-built alignment after the record part landed (rendered include and method names, read() signature, the generic <name> event rows, measured sizes and wall clock); the response table in `dv/auto_dv/evidence/gen_critic_response_rvfi_export.md` carries one row per finding of both replan artifacts. Version 4a (v4 plus the v3a replan review's remaining medium and two lows: read() bound to the flush sequence just issued, MUT-F stale marker, the last-store assertion, the pc-continuity rule). Version 4: version 3a (record lines, reviewed) plus the EVENT channel the DV Lead's plan round-3 decision requires (Section 8: bus, pin, alert, misc, icache-RAM, key and regime events as `E` lines in the same file, same discipline) and the knob family renamed to `+gen_export_*` because the file now carries more than RVFI records. Earlier: version 3a folded Runtime's retention ruling; version 3 answered the plan review; base: version 2a plus the cross-model plan review's findings
(`dv/auto_dv/reviews/2026-09-03-claude-plan-gen_rvfi_export_addendum.md`, APPROVE-WITH-CHANGES; rows answered in
`dv/auto_dv/evidence/gen_critic_response_rvfi_export.md`). Status: the record part (Sections 1 to 5: sink, R and I lines, markers, reader) is BUILT and landed
(1f8186e, 6b3301d) and the text names it as built; the event channel (Section 8) and the witness command (Section 9) are
text until their build steps. Consumer: Test Writer (fire-checks over per-record RVFI facts
in measured runs; asks 4 and 5). Scope rules it satisfies: RVFI is a define-gated DUT boundary interface (probe
register row RVFI, `boundary`), so the export is not a probe under DV_prompt Section 7 (modelling and checking);
Python reads a file once, never a signal per cycle (A-01); the knob is a normal plusarg, usable in measured runs.

## 1. What it is

One writer, `gen_export_sink` (env component owning the file descriptor, the header, the flush and end markers),
receives one ASCII line per `gen_rvfi_txn` and one per interrupt-marker rising edge from `gen_rvfi_monitor`, and
one line per boundary EVENT (Section 8) from the bus drivers, the pin drivers, the misc monitor, the icache RAM
models, the key responder and the regime dispatcher; the file is named by `+gen_export_file=<path>` (kind string, default unset = off; a relative path is relative to the run
directory, which is the simv working directory in both `gen_run.py` and `gen_tb_local.sh`). The knob is OPT-IN
per testlist entry: an entry whose test reads records sets `+gen_export_file=gen_export.txt` (the Test
Writer's template adds it when the test declares that it consumes records); an entry without it writes nothing
and runs no export code. A bridge command `EXPORT_FLUSH` (appended to `bridge_cmds`, so existing codes keep their
values) makes the sink write a flush marker and `$fflush` before the bridge acks, so Python parses a complete
prefix of the file inside its checks, before the finish handshake (TB_CONTRACT Section 2 ordering). The Python
side is one module, `dv/auto_dv/gen_tb/gen_export.py`: `read(path, seq, counters=False)` returns the records, markers
and events of the prefix ending at the flush marker with sequence `seq`, requires the header's `counters=` flag to
agree with the caller, enforces the format rules of Section 3 (including the I-line count), and fails loud
(AssertionError, the only Python-side failure mechanism) on any violation.

## 2. File format (version 2)

```
# gen_export v2 seed=<n> build_config=<name> counters=<0|1> sources=<csv: the rendered active sources enabled by the knob, in yaml order> fields=<comma-separated R field names>
# image <path as given to +gen_mem_image, rest of line, or the word none>
# events <source> <event> <comma-separated field names>                        one line per (source, event) row of the rendered event table (Section 8)
R <field values in header order, hex without prefix, flags 0/1>            one line per retired record
I <cycle> <ext_pre_mip> <ext_post_mip> <ext_nmi> <ext_nmi_int> <ext_debug_req> <ext_debug_mode>   one line per RISING EDGE of rvfi_ext_irq_valid, at the rise cycle
E <cycle> <source> <event> <field values in the row's order>                   one line per boundary event (Section 8)
# flush seq=<s> records=<n> retired=<r> markers=<m> events=<e> ibus_grants=<g> dbus_grants=<h> cycle=<c>   written by EXPORT_FLUSH; s = the flush sequence number the command returns; r, g, h = the bridge's evt_retired_count / evt_ibus_grants / evt_dbus_grants read in the same call (version 2: the grant fields are present on both markers and required by read())art)
# end records=<n> retired=<r> markers=<m> events=<e> ibus_grants=<g> dbus_grants=<h>   written in extract_phase (Section 3)
```

`fields` (every `gen_rvfi_txn` field, 36 names in this order): `order, pc_rdata, pc_wdata, insn, trap, halt, intr,
mode, ixl, rs1_addr, rs1_rdata, rs2_addr, rs2_rdata, rs3_addr, rs3_rdata, rd_addr, rd_wdata, mem_addr, mem_rmask,
mem_wmask, mem_rdata, mem_wdata, ext_pre_mip, ext_post_mip, ext_nmi, ext_nmi_int, ext_debug_req, ext_debug_mode,
ext_rf_wr_suppress, ext_ic_scr_key_valid, ext_irq_valid, ext_exp_valid, ext_exp_insn, ext_exp_last, ext_mcycle,
cycle`; with `counters=1` the 20 names `mhpmcounter3..mhpmcounter12, mhpmcounter3h..mhpmcounter12h` follow. `rs3`
is exported because the draft-B ternary ops (Zbt cmov/cmix/fsl/fsr) read a third operand and the plan's ISA items
name it. Not exported, with the basis: the `*_rcap` capability fields and `mem_is_cap` are the CHERIoT carve-out
("cheriot-out-of-scope", DV_prompt Section 2), constant in this configuration and owned by the `rvfi_cap_quiet`
check. Radix rule: every value of an `R`, `I` or `E` line is hex without prefix (`%0h`); `seed=` and `counters=` in the
header and every `key=value` pair of the flush and end markers are decimal (`%0d`); `build_config=`, `sources=` and
`fields=` are a name and comma-separated name lists. Binding rule: the flush marker binds `I` lines to
`markers=` exactly as `R` lines to `records=` and `E` lines to `events=`, and `read()` checks all three counts. The field lists have one origin: yaml keys
`export_record_fields`, `export_counter_fields` and the `export_events` table in `gen_tb_knobs.yaml`, rendered as
`GEN_EXPORT_RECORD_FIELDS` / `GEN_EXPORT_COUNTER_FIELDS` and two includes, `dv/auto_dv/env/gen_export_record_line.svh`
(the `R` writer function `gen_export_record_line(t, counters)`, included in gen_rvfi_pkg) and
`dv/auto_dv/env/gen_export_event_lines.svh` (one writer function per event row, `gen_export_line_<source>_<event|any>`,
whose argument names ARE the field names, so the SV side cannot reorder a column; included in gen_export_pkg), and as `EXPORT_RECORD_FIELDS` / `EXPORT_COUNTER_FIELDS` / `EXPORT_EVENTS`
(gen_knobs.py, the header `read()` requires), so a field added on one side fails the other side's header check
instead of shifting columns silently; the codegen's top-level schema and `gen_ut_knobs_codegen.py` are extended
for the three keys (Section 4). The `image` header line is
rest-of-line, so a path with spaces cannot break the tokeniser. Under the radix rule a value
with X or Z renders as `x`/`z` characters and `read()` fails loud on any non-hex token (an X on RVFI is a DUT or
TB defect, never something to interpret). `R` lines are written in retirement order (`rvfi_order` ascending).
`I` lines: `rvfi_ext_irq_valid` is a LEVEL (rtl-arch T-053 rule X-16, plan convention C-13: it rises four cycles
after the interrupt decision and stays high until about two cycles after the handler's first instruction enters
ID), so exactly one `I` line per rising edge, at the rise cycle, never one per high cycle; the monitor's
`ap_irq` publication and `irq_markers` count follow the same rule (the step-2a monitor publishes on every high
cycle without a retirement, a defect corrected in this landing; it never fired, irq_markers=0 in every retained
run). The 20 counter words (`ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]`, today sampled into `gen_rvfi_if`
but not into `gen_rvfi_txn`) are added to `gen_rvfi_txn` and appended to every `R` line only under
`+gen_export_counters=1` (the PMC/DIT/BTALU fire-checks need them; the ISA/CMP/BIT groups do not), so the
default line stays about 220 bytes.

## 3. Guarantees, completeness rule and failure behaviour

- Open: `$fopen` in `start_of_simulation_phase`; failure is `uvm_fatal GEN_EXPORT` (never a silent run
  without a file). The header (the `gen_export` line, the `image` line and one `# events` row per rendered event
  row of every registered and enabled source) is written before the first record.
- One cycle base for every line: the stamp is the bridge's `cycle_count` (gen_bridge_if, counted at the posedge),
  read through `sink.cycle()` at write time by every event writer; the monitor's `R` and `I` lines carry
  `gen_rvfi_if.cycle`, the same count by construction (both counters reset on `rst_n` and increment at every posedge,
  gen_rvfi_if.sv:24-25 and gen_bridge_if.sv:48-54), so no line has a second base. A driver acting at the negedge stamps
  the cycle whose posedge just passed, the same base as the monitor's record cycle. The bus driver's local negedge
  counter (one ahead of the posedge counters) is never used for a stamp; gen_ctrl_if and gen_scrkey_if have no
  counter of their own and need none.
- Flush and the same-instant pair: `EXPORT_FLUSH` is routed by `gen_cmd_dispatch` to `gen_export_sink::flush_export()`,
  which reads the sink's record, marker and event counts and the bridge's `evt_retired_count`, `evt_ibus_grants` and
  `evt_dbus_grants` (the two grant counters are incremented by the bus drivers in the grant beat, independently of the
  line writer, the counts-on-both-sides pattern of `cmds_consumed`; they arrive with build step (2) of Section 8),
  writes the flush marker with all of them, calls `$fflush`, then checks `$ferror(fd)` (a non-zero code is `uvm_error GEN_EXPORT`). Design constraint
  that makes `records == retired` exact: `flush_export()` runs from the bridge's `@(vif.cmd_valid)` wake
  (gen_env_pkg.sv, gen_bridge::run_phase), which follows cocotb's deferred write, i.e. after the NBA region of
  the posedge in which the interface counted the last retirement and after the monitor's active-region
  `records++` of that posedge; it is never called from a clocked process, and dispatching it at the ack posedge
  would break the equality by one. The dispatcher call completes before the bridge toggles `cmd_ack` one posedge
  later.
- Completeness rule (`read(path, seq)`): the flush command returns a flush sequence number `s` (the sink counts
  flushes; the bridge hands the number back in `peek_data` with the ack, the way MEM_PEEK returns a word), and
  `read()` accepts ONLY a complete flush marker carrying that `seq=<s>`: a missing marker for `s`, an earlier
  marker in its place, or a marker with another sequence is a completeness FAIL, so a test that flushes more than
  once can never pass on a stale earlier marker (v3a review medium). `read()` parses only the prefix before that
  marker and ignores every byte after it (at the ack posedge the monitor may already
  have written record N+1 into the buffer, which a buffer-full flush can put on disk); require the header, the
  image line and, for every source named in `sources=`, every one of its rendered `# events` rows (a row for a
  source outside `sources=` is a FAIL), `records == retired` from the marker itself, the number of parsed `R`
  lines equal to `records`, the number of `I` lines equal to `markers`, the number of `E` lines equal to `events`,
  per enabled bus the number of `E <bus> gnt` lines equal to the marker's `ibus_grants=` / `dbus_grants=`, the header's
  `sources=` equal to the rendered active list restricted to the run's `+gen_export_sources` (version 2),
  `order` strictly +1 across `R` lines,
  non-decreasing `cycle` across all lines, the field count of every line equal to its header row's, every `E`
  (source, event) pair present in the header table, and hex-only tokens. Python's own read of `evt_retired_count` after the ack is a `>=` check against the marker's `retired`. A post-run diagnostic read (`read(path, seq=None)`) uses the end marker and is never the basis of a pass.
  Every violation, a missing file or a header whose field list differs from the rendered one is a Python
  assert (collected failure). No "last line must be a marker" rule exists for flush reads.
- Close: the end marker and `$fclose` (after `$fflush` and `$ferror`) are written in `extract_phase`
  (bottom-up, before the UVM report and before `gen_base_test::final_phase` toggles `finish_ack`), so the file
  is complete before Python is released from the finish handshake.
- Abnormal ends: (a) `uvm_fatal` anywhere (UVM `$finish`es before extract/final): no end marker, no `$fclose`;
  the file holds everything through the last `$fflush` plus whatever the simulator's buffer reached the OS; the
  run FAILS through the collected fatal; if Python was waiting on an ack it raises the `GenBridge.cmd` timeout
  as well; the file is diagnostic only. (b) the alive watchdog `$fatal`: as (a). (c) a Python `with_timeout` on
  the `EXPORT_FLUSH` ack: `GenBridge.cmd` raises AssertionError (test FAIL); the file state is that of the last
  completed flush. (d) `$ferror` after a flush: `uvm_error GEN_EXPORT`, the run FAILS; `read()` is the
  second line of defence. A debug-only knob `+gen_export_flush_every=<n>` (default 0 = off, refused in
  measured runs like every debug-only knob) `$fflush`es every n records for triage of abnormal ends.
- Cost and retention: with the knob absent the monitor neither formats nor hands over a line (`sink.enabled`
  guards the call) and the `ap` publishing is unchanged. Measured on the record part (build out_t080d, 36 fields): the Zc
  program's 175 records make a 22133-byte file (126 bytes per record; 29971 bytes = 171 per record with the
  counters), the seed-7 program's 2008 records 232434 bytes (116 per record); 1e6 records are therefore about
  115-170 MB. Wall clock (retained runs, build out_t080d): VCS CPU time 0.29 s without and 0.26 s with the knob on the Zc
  lock-step run, 0.52 s and 0.54 s on the seed-7 run, i.e. within a few tens of milliseconds at these record counts. Retention: the file lives in the run
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
| knob `export_file` (string, default unset) | gen_tb_knobs.yaml -> PLUSARG_EXPORT_FILE, gen_knobs.py | normal knob (not debug-only), opt-in per testlist entry |
| knob `export_counters` (bool, default 0) | gen_tb_knobs.yaml -> PLUSARG_EXPORT_COUNTERS | appends the 20 hpm counter words to every R line; the header's `counters=` flag records it |
| knob `export_flush_every` (int, default 0, debug_only; plusarg `gen_export_flush_every`) | gen_tb_knobs.yaml; Runtime's loader reads the rendered gen_knobs.py table and refuses the testlist unless `debug_only_plusargs` equals it, so the landing that adds this knob carries Runtime's one-line testlist change in the same commit | periodic $fflush for triage of abnormal ends |
| yaml top-level keys `export_record_fields`, `export_counter_fields`, `export_events` | gen_tb_knobs.yaml; codegen `SCHEMA["top"]` extended; rendered `GEN_EXPORT_RECORD_FIELDS`, `GEN_EXPORT_COUNTER_FIELDS`, the include `env/gen_export_record_line.svh` and `env/gen_export_event_lines.svh` (writer functions) and `EXPORT_RECORD_FIELDS`, `EXPORT_COUNTER_FIELDS`, `EXPORT_EVENTS` in gen_knobs.py; `gen_ut_knobs_codegen.py` asserts the renderings equal the yaml, that every record field is a `gen_rvfi_txn` member and that the include declares one writer function per event row | one origin for the column order |
| knob `export_sources` (string, default `all`) | gen_tb_knobs.yaml -> PLUSARG_EXPORT_SOURCES | comma-separated subset of the event sources of Section 8; a name outside the rendered source list is `uvm_fatal GEN_EXPORT`; records and markers are always written when the file knob is set |
| `gen_rvfi_txn` extension | env/gen_rvfi_pkg.sv | `ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]` sampled from the interface on every record (the comparator syncs the model from them); appended to the R line only when the counters knob is on |
| yaml top-level key `export_active_sources` (version 4d) | gen_tb_knobs.yaml; codegen `SCHEMA["top"]`; rendered `EXPORT_ACTIVE_SOURCES` (gen_knobs.py, the attribute Runtime copies into build_manifest.yaml `export_sources_emitted`), `GEN_EXPORT_ACTIVE_SOURCES` and `gen_export_source_active()` (gen_tb_pkg.sv) | the sources whose writers are instanced in the build (today every source but icram); the sink derives the header's `sources=` from this list intersected with `+gen_export_sources`, refuses a writer registering an inactive source and an active source without a writer (both `uvm_fatal GEN_EXPORT`), so Runtime's header-versus-manifest cross-check holds by construction; with a restricting knob the header is a subset of the emitted set |
| bridge fields `evt_ibus_grants`, `evt_dbus_grants` (version 4d) | tb/gen_bridge_if.sv, incremented by the bus drivers in the grant beat | the export's independent grant count, sampled into both markers by the sink; `read()` requires `E <bus> gnt` count == `<bus>_grants` for every enabled bus (MUT-G) |
| bridge command `EXPORT_FLUSH` (appended) | bridge_cmds; gen_cmd_dispatch -> gen_export_sink.flush_export() | ack implies flushed; flush_export() never runs from a clocked process; the flush sequence number returns in `peek_data` |
| `gen_export_sink` (new env component) | env/gen_env_pkg.sv (or its own gen_export_pkg.sv) | owns the fd: header lines, flush marker with the same-instant counts, `$ferror`, end marker and `$fclose` in extract_phase; `write_record` / `write_marker` / `write_event` for every writer |
| `gen_rvfi_monitor` R/I writer | env/gen_rvfi_pkg.sv | one R line per record through the rendered writer function, one I line per rising edge |
| event writers (built, version 4d) | gen_agents_pkg (bus drivers: req / gnt / rvalid; key responder: req / valid; ctrl driver: fetch_enable / mcounteren_writable; irq driver: the irq lines; dbg driver: debug_req), gen_checkers_pkg::gen_misc_monitor (alert and misc rows), gen_cmd_dispatch (regime phase); gen_icache_ram announcements not yet | one call of the rendered writer function per event through `sink.write_event`, stamped with `sink.cycle()`; the pin, alert and misc writers also emit the level at reset release, so a consumer knows the starting value |
| `dv/auto_dv/gen_tb/gen_export.py` | Python reader: `read(path, seq, counters=False) -> Export(header, records, markers, events, flush)`; field access by name from `EXPORT_RECORD_FIELDS` and `EXPORT_EVENTS`; enforces Section 3 | ASCII only |
| `GenBridge.export_flush()` | gen_bridge.py | issues EXPORT_FLUSH and returns the flush sequence number from `peek_data`; the test passes it to `read(path, seq)` |
| API documents | `gen_component_api_rvfi_monitor.md` Sections 3, 6 and a new Section 8 (record lines); a new `gen_component_api_export_sink.md` (the sink, the event table, the knobs, guarantees, cost); one sentence in each writer's API document naming its event rows | |

## 5. Trust triad for the build

1. TDD: `gen_tb/gen_tests/gen_ut_export.py` written first: boots the Zc program, issues `EXPORT_FLUSH`,
   calls `read()`, asserts the header fields equal the rendered list, `records == retired` from the marker, the
   `R`-line count equals `records`, `order` increments by one, every line has the header's field count, the first
   record's `pc_rdata` is boot page + 0x80, and the Zc program's known content (the count of `cm.push` /
   `cm.pop` encodings in `ext_exp_insn` of the folded records (NOT implemented in the first landing: the count is
   not derivable from the image without a decoder, so the tohost-store rule below carries the program-derived
   content check), and the tohost stores: every `R` line storing to the tohost
   address carries the value 1 and their count does not exceed the memory model's independent end-of-test count
   (the bridge's `evt_eot_count`), which is the program-independent form ("last store" is not: the riscv-dv programs
   store tohost repeatedly, and the Zc program spins after its store while a flush taken too early ends the prefix
   before the store's record, which is what the first green attempt saw), plus the pc-continuity rule that MUT-A's catch depends
   on: for consecutive `R` lines k and k+1 with no `I` line between them, record k not a debug entry, not a
   trap record and not an mret or dret record (their `pc_wdata` is the next sequential address, plan convention
   C-1, not the return target), `pc_rdata[k+1] == pc_wdata[k]`; across a Zcmp sequence the rule is applied to the sequence's boundary records
   (the record before the first micro-op, the last micro-op, the record after) and the micro-op-internal pc
   convention of RVFI is recorded at the first green run before it is asserted; TRAP records are excluded: the
   first green run showed that this RTL reports `pc_wdata = pc + 4` on a trap record (riscv-dv seed 7, order 466,
   ecall at 0x80002164, `pc_wdata` 0x80002168, handler at 0x80001700), not the handler address, the open ruling
   F-RVFI-010 that the comparator also honours by skipping `isa_pc_next` on trap records), and for the event channel: the number of `E ibus gnt` lines equals the
   ibus agent's grant count (bridge field `evt_ibus_grants`), every `E dbus rvalid` line with `we=1` has a matching
   `R` store record within the bus latency window, and every `E pin` line the fixture caused through the bridge
   (`fetch_enable` through FETCH_EN; an IRQ_SET/IRQ_CLR pair once the irq driver exists) appears with the
   commanded value. Red on the T-068 tree (knob unknown: `GEN_UNKNOWN_PLUSARG` fatal), then
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
   - MUT-F stale marker: the sink writes the marker for the first flush only, the test flushes twice ->
     caught by `read(path, seq=2)`: no complete marker with `seq=2` (the earlier `seq=1` marker present does not
     satisfy it).
   - MUT-G dropped event: the ibus driver skips one `gnt` line while its `grants` counter still increments ->
     caught by `read()`: the E-line `ibus gnt` count differs from the marker's `ibus_grants=`, which `flush_export()` samples
     from the bridge in the same call as the other counts (same-instant; a Python-side read after the ack is NOT
     used, since fetches continue in the spin loop after EOT).
   - MUT-H wrong event cycle: the ctrl driver stamps its `fetch_enable` line with `cycle + 1` -> caught by the
     fixture's correlation check: the line's `cycle` relates to the bridge's `cycle_count` that Python reads right after
     `Edge(cmd_ack)` (the stated sample point) by a fixed offset, recorded at the first green run and asserted exactly
     since: 0 on every run of build out_t080s2/a (`FETCH_EN_LINE_OFFSET` in gen_ut_export.py; the a-priori "minus one" of
     version 4c was wrong and is withdrawn), and the first `R` record's `cycle` is greater than the line's. A
     `cycle + 1` stamp breaks the equality.
   Records: `dv/auto_dv/mutations/gen_mut_export.md` (ids MUT-A..F, executed; MUT-G/H with the event part). The existing `rvfi_order` check is NOT relied on (it is off
   under `+gen_chk_all=0`); `read()` carries its own order rule.
3. fcov-expectation: not applicable (check-tier unit test outside the regression, per the standing ruling); the
   Test Writer's tests that consume the file carry their own manifests.

## 6. Resolved points

- DV Lead (2026-09-03, v2a): one `I` line per rising edge of the `rvfi_ext_irq_valid` level.
- Test Writer (2026-09-03, v2): `I` lines carry `ext_debug_req` and `ext_debug_mode`; counters behind
  `+gen_export_counters=1`; the flush marker carries the bridge's retired count sampled at the same instant;
  the header names seed and image.
- Cross-model replan review of v4a (2026-09-03, REQUEST-CHANGES, v4b): irq_pending and bus request events; grant
  counters sampled into the flush marker (MUT-G); the complete two-artifact response table; one cycle base; mret/dret
  excluded from continuity; I lines bound to markers=; radix rule; rs3 exported with its basis; the Zc statement
  corrected; the API-document section collision resolved in the committed document (old Section 8 renumbered 9).
- DV Lead round 4 (2026-09-03, v4b): irq_pending_o and bus request rows confirmed; COV_WITNESS and CG-WIT-001 in Section 9.
- Cross-model replan review of v3a (2026-09-03, APPROVE-WITH-CHANGES, v4a): `read()` bound to the flush sequence
  just issued (MUT-F stale marker); last-store assertion by `mem_wmask`, not by line position; the pc-continuity
  rule stated for MUT-A.
- Cross-model plan review (2026-09-03, v3): completeness from the marker not from line position; `read()` owns
  the count/order/field-count rules; drop, swap and program-contradiction mutations; every `gen_rvfi_txn` field
  listed or its exclusion stated; abnormal ends specified; `$ferror`; the same-instant constraint stated with its
  citation; opt-in knob, retention proposal and wall-clock measurement; image line rest-of-line, X/Z fail loud,
  codegen schema and unit test extension named; end marker in `extract_phase`.
- Runtime (2026-09-03): retention policy by purpose with `keep_artifacts: true` and `pruned_artifacts` in
  result.yaml (Section 3); the debug-only knob lands together with Runtime's testlist line (Section 4).
- DV Lead (2026-09-03, plan round 3 medium 2, v4): the bus/pin EVENT channel is part of T-080 (Section 8), a
  Phase-1 prerequisite; the plan v2c carries an RVFI-only fallback rule until it lands. It supersedes the earlier
  "later landing" note for the bus monitors' records (Test Writer ask 4): per-phase statistics derive from the
  `E` lines with their cycle stamps and the regime phase events.

## 7. Consumer requirements (Test Writer, 2026-09-03) and where the text meets them

| Requirement | Where |
|---|---|
| (1) normal knob naming the file, set per entry to a run-directory path (asked as `+gen_rvfi_export=<file>`; settled in v4 as `+gen_export_file=<file>`, suggested value `gen_export.txt`, because the file also carries event lines) | Sections 1 and 4: string knob, not debug-only, opt-in per entry; a relative path resolves in the run directory |
| (2) one line per record and per irq marker with every field | Section 2: every `gen_rvfi_txn` field is listed (36 names, rs3 included) with the CHERIoT capability fields and mem_is_cap excluded by name; the 20 hpm counter words under `+gen_export_counters=1`; `I` lines carry cycle, mip, NMI and debug flags, one per rising edge |
| (3) a bridge command that flushes and acks, so the file is complete before the finish handshake | Sections 1 and 3: `EXPORT_FLUSH`, flush marker with the same-instant (records, retired) pair, `$fflush` and `$ferror` before `cmd_ack`; `read()` parses the prefix before the marker carrying the issued sequence number |
| (4) the same knob/command discipline for the bus monitors' per-phase records | Section 8: `E` lines in the same file, same flush rule, regime phase events give the phase boundaries |
| a `records()` template helper parsing the file into namedtuples | Section 2 fixes the line format; the helper builds its namedtuple from `EXPORT_RECORD_FIELDS` (+ counter fields when the header says `counters=1`) instead of re-typing the columns; `read()` is the enforcing layer the helper wraps |

## 8. Event channel (version 4, DV Lead decision of 2026-09-03)

Why: about 130 Phase-1 fire-checks assert bus or pin cycle facts (the rvalid cycle of an alert, an ibus grant
against a retirement, a driver's rise and fall cycles, dbus timestamps) that the record lines cannot carry.
Every event below is already known to an agent, driver or monitor; no new DUT observation is involved and no
probe is added. The `cycle` stamp is the one cycle base of Section 3 (the bridge's `cycle_count` through
`sink.cycle()`) and is what correlates an `E` line with the `R` and `I` records.

Line: `E <cycle> <source> <event> <fields...>`. One writer function per row, rendered into
`env/gen_export_event_lines.svh` from the yaml `export_events` table; the header repeats the table (`# events` lines)
so `read()` builds one namedtuple type per (source, event). Sources are enabled by `+gen_export_sources`
(default `all`); a disabled source writes nothing and the header's `sources=` names the enabled set.

| source | event | fields | writer | when |
|---|---|---|---|---|
| ibus, dbus | req | addr, we, be | gen_bus_driver | the first cycle a request is seen (its rise); with the following gnt line's `req_cycle` this gives the cycles the request was held with gnt withheld, and its absence is the "no request" fact (TP-PMP-082 class) |
| ibus, dbus | gnt | addr, we, be, req_cycle, outstanding_after | gen_bus_driver | the cycle the grant is driven (one per beat); `req_cycle` is the cycle of the matching req line |
| ibus, dbus | rvalid | addr, we, err, intg_injected, outstanding_after | gen_bus_driver | the cycle the response is driven (one per beat) |
| pin | irq_software, irq_timer, irq_external, irq_nm, debug_req (fields: value); irq_fast (fields: idx, value: the fast line index, so no line count is re-typed) | see event | irq / dbg drivers (step 2b) | every value change (rise and fall) |
| pin | fetch_enable, mcounteren_writable | value (MuBi encoding) | gen_ctrl_driver | every value change |
| alert | alert_minor, alert_major_bus, alert_major_internal, double_fault_seen | value | gen_misc_monitor (step 2b) | every value change (a one-cycle pulse is a rise line and a fall line) |
| misc | irq_pending, core_busy, crash_dump_current_pc, crash_dump_next_pc, crash_dump_last_data_addr, crash_dump_exception_pc, crash_dump_exception_addr (one row each) | value | gen_misc_monitor | every value change (irq_pending_o is the DUT output pin, 26 marked items assert it in a named cycle; core_busy as the MuBi encoding) |
| icram | inject | way, index | gen_icache_ram (announcement port) | the lookup cycle of an injected ECC error (the expected-alert feed of C3.4) |
| icram | lookup | index | gen_icache_ram (announcement port) | the cycle a lookup reads the tag and data RAMs of every way at `index` (plan round 7 WP-8: TP-IC-002/004/008/011) |
| icram | tag_write | way, index, valid | gen_icache_ram (announcement port) | the cycle a tag RAM write lands: a fill writes `valid` = 1, an invalidation writes 0 (TP-IC-004/008/011 and the fill items) |
| icram | fill_write | way, index | gen_icache_ram (announcement port) | the cycle a data RAM fill write lands (TP-IC-015/023/024/030/031/057) |
| scrkey | req, valid | value | gen_scrkey_driver | every change of ic_scr_key_req_o / ic_scr_key_valid_i |
| regime | phase | knob_id, value_idx, phase_idx | gen_cmd_dispatch (REGIME_SET consumer, step 2b) | the cycle a phase is applied |

Rules: every row names ONE event exactly (no wildcard rows: sunset input (2) of gen_test_plan.md Section 0; the
codegen refuses an event token `<name>`), rendering one function per row, `gen_export_line_<source>_<event>`; the
header carries one `# events` row per rendered row of every registered and enabled source and `read()` requires all
of them and refuses an `E` line whose (source, event) is not a header row, so a misspelled or unlisted event token is
a FAIL, never a silent miss; the writer functions
take the fields as named arguments in the row's order, so the SV side cannot reorder a column; the three RAM-port rows
(lookup, tag_write, fill_write) carry the RAM model's own port facts and their field sets are final when the
announcement port is built in step (3), any change being a yaml change the codegen unit test and the header check see; a source whose component does not exist yet (irq/dbg drivers, misc monitor, regime dispatcher,
all step 2b) has its rows rendered and its writer functions present but unused until the component lands, and
the header's `sources=` lists only sources with a registered writer instance; `read()` accepts an absent source.
Ordering: `E` lines are written in the cycle of the event in the active region (drivers act at the negedge,
monitors sample at the posedge), so within one cycle the order is driver lines, then the record line, then
monitor lines; `read()` requires non-decreasing cycles and nothing more about intra-cycle order. Cost: about 100
bytes per event; on the seed-7 program (2002 retirements) the bus rows add about 3500 lines, the pin and alert
rows a handful; the wall-clock delta is measured as for the record lines. Trust triad: MUT-G (dropped event) and
MUT-H (wrong event cycle) in Section 5, plus the fixture's independent-count check against the bridge's grant
counters (`evt_ibus_grants`, `evt_dbus_grants`: two new bridge fields incremented by the bus drivers in the grant
beat, independent of the line writer, the same "counts on both sides" pattern as `cmds_consumed`; they arrive with
build step (2) below, not with the record part).

Build order inside T-080: (1) sink, header, R/I lines, flush and end markers, `read()`, red then green (landed 1f8186e
and 6b3301d); (2) THIS landing (version 4d): the writers of every source whose component exists after the step-2b
re-application (bus, ctrl, scrkey, pin, alert, misc, regime), the grant counters, file format version 2, the
active-source list, MUT-G and MUT-H; (3) icram (gen_icache_ram.sv:6 defers its announcement hooks; the rows are rendered
and inactive) and the witness command of Section 9, each with its own red. The plan's RVFI-only fallback rule applies to
items whose source is inactive.

## 9. Witness command for the plan's sunset (DV Lead round 4; aligned to plan v2h and the Orchestrator's rulings, version 4c)

A test whose cycle-level clause passed against the export records the fact for coverage. Protocol (plan v2h Section 0,
Critic gen_critic_plan_witness_v1.md C-1..C-5): the template's `finish()` epilogue, before the finish handshake, issues one
bridge command `COV_WITNESS <index>` (appended to `bridge_cmds`; arg0 = index, args 1..3 zero) for every `fire_<tp_id>`
whose result record has `cycle_clause_true` set; no other code may issue it (host structure check `check_test_source`,
C-1). The index is the ROW ORDER (0-based) of `dv/auto_dv/docs/gen_trace_witness_ids.csv` (columns index, tp_item, bin,
test_group, marked; 220 rows; committed 7ac3744), the single rendering source: the codegen reads it like `gen_dut_top.sv`
and `gen_link.ld` and renders `GEN_WIT_IDS` (SV: tp_item and bin per index, in file order) and `WITNESS_IDS`
(gen_knobs.py: tp_item -> index, the table the template reads through gen_test_lib). Dispatch (`gen_cmd_dispatch`): an
index outside the list is a collected `uvm_error GEN_CMD_DISPATCH`. Owner-only acceptance (C-2): the FLOW renders the
running test's set into the plusarg `+gen_witness_ids=<comma-separated indices>` (yaml knob `witness_ids`, string,
default empty = no index accepted) from the testlist entry's `witness_ids` (TP ids) through the CSV at the pinned commit
(Orchestrator's ruling; Runtime implements the rendering), and an index inside the list but outside that set is a
collected `uvm_error GEN_WITNESS_FOREIGN` with no sample. Digest guard (plan WP-8): every rendering of the CSV carries
its sha256 prefix (`GEN_WIT_DIGEST` in SV, `WITNESS_DIGEST` in gen_knobs.py); the flow passes
`+gen_witness_digest=<prefix>` from the CSV it rendered the set from, and the dispatcher refuses a mismatch with a
collected `uvm_error GEN_WITNESS_DIGEST` before it accepts any index, so a stale rendering against a newer plan fails
loud. Covergroup: `gen_wit_cycle_clause_cg` (the architecture's C7 naming rule for plan id CG-WIT-001, plan name
gen_cg_wit_cycle_clause; declared in `gen_fcov_pkg`, one instance in `gen_env`, handle `wit_cg`; URG lists it under
that type name), single coverpoint `cp_clause` with one bin `w_<tp_id lower case>` per CSV row in file order, sampled
by the command. `option.weight = 0` is rendered on it as defence in depth; Runtime's exclusion of the group BY NAME at
merge and report time is the mechanism of record (Orchestrator's ruling), so it never enters the functional-group
score and is reported beside it as "witnessed clauses: N of M marked items" (Critic C-4, DV Lead W-1,
gen_fcov_plan.md Section 1). Coverage only: no checker reads it. The bins are excluded from a test's manifest while
its item carries the plan's marker token and become must-hit when the token is removed (gen_test_plan.md Section 0,
sunset: decided from the rendered exact event rows of Section 8 and Runtime's export_sources). The anti-vacuity claim
rests on the host structure check, not on the TB: the dispatcher cannot tell a true clause from a hand-issued command,
it refuses foreign indices and stale digests. Everything in this section lands with build step 3 together with the
covergroup; none of it exists in SV or Python at version 4c.
