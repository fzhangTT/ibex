# Response to the cross-model plan review of the RVFI record export addendum (T-080)

Responder: tb-infra, 2026-09-03. Review answered: `dv/auto_dv/reviews/2026-09-03-claude-plan-gen_rvfi_export_addendum.md`
(APPROVE-WITH-CHANGES on 4c0ba11, addendum version 2). Result: addendum version 3, delivered as the standalone
`dv/auto_dv/docs/gen_rvfi_export_addendum.md` (identical to the source `dv/auto_dv/work/tb-infra/gen_rvfi_export_addendum.md`)
for the DV Lead's re-embed into gen_tb_architecture.md Section 9. No SV or Python exists yet; every row below is
a text change to the design, validated by the reviewer's re-read, not by a run.

| Finding | Status | Where in v3 |
|---|---|---|
| [medium] "the last line must be a flush or end marker" contradicts the one-posedge window (record N+1 can reach the buffer at the ack posedge) | FIXED | Section 3 "Completeness rule": `read()` locates the LAST COMPLETE flush marker, parses only the prefix before it, ignores every byte after it, and checks the parsed R-line count against the marker's `records`; the "last line must be a marker" rule is gone for flush reads and applies only to the end marker in a post-run diagnostic read. |
| [medium] mutation plan lacks dropped-record, reordered-record and program-contradiction reds; `rvfi_order` is off under `+gen_chk_all=0` and is not the consumer | FIXED | Section 3: `read()` itself enforces `records == retired`, R-line count == `records`, `order` strictly +1, field count per line == header count, hex-only tokens. Section 5.2: MUT-A field corruption, MUT-B dropped record, MUT-C swapped records, MUT-D truncation, MUT-E program contradiction (image with a different cm.push count, or a moved boot page), each caught by `read()` or the fixture assertion with hidden referees inert and an ablation control; the statement that `rvfi_order` is not relied on. |
| [medium] "every gen_rvfi_txn field" claimed but `halt`, `ixl`, `ext_ic_scr_key_valid` missing; counters are not in `gen_rvfi_txn` | FIXED | Section 2 lists all 34 names (the three added) and names the four excluded CHERIoT-carve-out fields (`rs3_addr`, `rs3_rdata`, `*_rcap`, `mem_is_cap`) instead of claiming "every field"; Section 4 adds the `gen_rvfi_txn` extension (`ext_mhpmcounters[10]`, `ext_mhpmcountersh[10]`, sampled only when the counters knob is on). |
| [medium] abnormal ends unspecified (uvm_fatal, alive $fatal, Python timeout on the flush ack) | FIXED | Section 3 "Abnormal ends" (a)-(d): file complete only through the last `$fflush`, diagnostic only; the run fails through the collected fatal or the `GenBridge.cmd` AssertionError; `$ferror` errors fail the run; debug-only `+gen_rvfi_export_flush_every=<n>` for triage. |
| [low] write failure not covered (`$fwrite` reports nothing) | FIXED | Section 3: `$ferror(fd)` after every `$fflush` in `flush()` and before `$fclose`, `uvm_error GEN_RVFI_EXPORT` on non-zero; `read()` named as the second line of defence. |
| [low] the "same instant" argument omits its constraint | FIXED | Section 3 "Flush and the same-instant pair": `flush()` runs from the bridge's `@(vif.cmd_valid)` wake after the posedge's NBA region, never from a clocked process; dispatching at the ack posedge would break the equality by one; gen_env_pkg.sv cited. |
| [low] template-default vs per-entry knob; no retention rule; no wall-clock delta | FIXED (retention ruled by Runtime, v3a) | Section 1: opt-in per testlist entry (the template adds the knob when the test consumes records). Section 3 "Cost and retention": Runtime's ruling (2026-09-03): kept on purposes 1 to 3 and on any non-PASS verdict; pruned after the manifest on purpose-4 PASS/RED-OK runs unless `keep_artifacts: true`; pruned paths recorded in result.yaml; implemented in the landing that brings the knob. Section 5.1: the wall-clock delta with and without the knob on the Zc and the seed-7 programs is part of the TDD evidence. |
| [low] format and origin details: image path with spaces, X/Z rendering, codegen top schema, unit-test extension, API-document section numbers | FIXED | Section 2: `# image <rest of line>` header line; X/Z render as `x`/`z` and `read()` fails loud on any non-hex token. Section 4: the codegen `SCHEMA["top"]` gains `rvfi_export_fields` / `rvfi_export_counter_fields` and `gen_ut_knobs_codegen.py` asserts both renderings against the yaml and against the `gen_rvfi_txn` field set; the API update targets Sections 3 (knobs), 6 (failure path) and a new Section 8. |
| [low] `final_phase` ordering of `finish_ack` vs the end marker undocumented | FIXED | Section 3 "Close": end marker, `$fflush`, `$ferror`, `$fclose` in `extract_phase` (bottom-up, before the UVM report and before `final_phase` toggles `finish_ack`). |
| (reviewer note) the owner's "Section 8" probe-rule citation is a misreference; the addendum's Section 7 is right | noted | Section 0 keeps "DV_prompt Section 7 (modelling and checking)". |
| (carried) DV Lead v2a: one `I` line per rising edge of the `rvfi_ext_irq_valid` level | included | Section 2. |

## Replan review of version 3a (`dv/auto_dv/reviews/2026-09-03-claude-replan-gen_rvfi_export_addendum.md`, APPROVE-WITH-CHANGES; all nine earlier rows judged ADDRESSED)

| Finding | Status | Where in v4a |
|---|---|---|
| [medium] `read()` not bound to the flush just issued; a stale earlier marker passes when the latest is missing; MUT-D cannot fire on a stale marker | FIXED (text) | Section 2: the flush marker carries `seq=<s>`; Section 3: EXPORT_FLUSH returns the flush sequence number in `peek_data` with the ack, `read(path, seq)` accepts only a complete marker with that sequence and the matching record count, anything else is a completeness FAIL; Section 5.2: MUT-F (marker written for the first flush only, test flushes twice, `read(seq=2)` fails); Section 4: `GenBridge.export_flush()` returns the number. |
| [low] "the tohost store is the last R line" is false (the program spins after the store) | FIXED (text) | Section 5.1: assert on the last `R` line with a non-zero `mem_wmask` at the tohost address. |
| [low] MUT-A's catch mechanism missing from the 5.1 assert list; rule across Zcmp folded records and traps | FIXED (text) | Section 5.1: `pc_rdata[k+1] == pc_wdata[k]` for consecutive `R` lines with no `I` line between them and record k not a debug entry; Zcmp applied at sequence boundaries with the micro-op-internal convention recorded at the first green run before it is asserted; traps unchanged (pc_wdata is the vector). |

The record part is built (`dv/auto_dv/evidence/gen_tdd_export.md`); the event part (Section 8) and the witness command
(Section 9) are text only until the v4b re-review.

## Complete status of BOTH replan artifacts against version 4b (`dv/auto_dv/docs/gen_rvfi_export_addendum.md`)

Row prefixes: R1- = `2026-09-03-claude-replan-gen_rvfi_export_addendum.md` (review of v3a, APPROVE-WITH-CHANGES);
R2- = `2026-09-03-claude-replan-gen_rvfi_export_addendum-r2.md` (review of v4a, REQUEST-CHANGES).
Every code or retained-run claim in the R1/R2 rows below is at commit 6b3301d (T-080 landing 1a), which carries the
rs3 fields, the decimal markers, the mret/dret exclusion, the sink cycle base and the out_t080d runs; "this commit" in
the R3/R4 tables means the landing that carries this file version (the final v4b text and the exact event rows). Status words:
ADDRESSED (text and, where named, code and retained run), NOT ADDRESSED (with the reason).

| Row | Finding | Status | Where |
|---|---|---|---|
| R1-M1 | `read()` not bound to the flush just issued; stale marker passes; MUT-D cannot fire on a stale marker | ADDRESSED | Section 2 marker `seq=`, Section 3 completeness rule, 5.2 MUT-F; code: `flush_export()` returns the sequence in `peek_data`, `read(path, seq)` accepts only that marker; MUT-F caught and ablated (`gen_mut_export.md`). |
| R1-L1 | "the tohost store is the last R line" is false | ADDRESSED | 5.1: every tohost store carries 1 and their count is bounded by the memory model's end-of-test count; implemented in gen_ut_export (R2 accepted the form). |
| R1-L2 | MUT-A's catch mechanism (pc continuity) missing from 5.1; rule across Zcmp and traps | ADDRESSED (R2 found the trap/mret/dret defect, fixed below) | 5.1 continuity rule: excludes Zcmp micro-op records, debug-entry boundaries, `I`-line boundaries, trap records and mret/dret records. |
| R1 prior 1..9 (v3 rows: completeness from the marker, read() owns the rules, drop/swap/contradiction mutations, all txn fields listed, abnormal ends, $ferror, same-instant constraint, opt-in knob and retention, image line / X-Z / codegen schema, extract_phase) | judged ADDRESSED by R1 | ADDRESSED | unchanged in v4b; the R1 radix and rs3 and Section-8 items are the R2 rows below. |
| R2-M1 | no `irq_pending_o` row; grant row carries no request cycle (23 + 15 marked fire-check lines) | ADDRESSED | Section 8 table: `misc irq_pending` (value, every change) and new `ibus/dbus req` rows (addr, we, be at the request rise) plus `req_cycle` on the gnt rows; yaml `export_events` and the rendered writer functions carry the rows now (`gen_export_line_ibus_req`, `..._gnt` with `req_cycle`); writers arrive with the event part. |
| R2-M2 | MUT-G's catch reads `evt_ibus_grants` from Python after the ack (not same-instant) | ADDRESSED | Section 2 flush marker gains `ibus_grants= dbus_grants=` sampled in `flush()`; 5.2 MUT-G is caught by `read()` against the marker's counts; the bridge fields arrive with the event part (Section 8 says so). |
| R2-M3 | response table must carry one row per finding of both artifacts incl. NOT ADDRESSED | ADDRESSED | this table. |
| R2-L1 | "the interface cycle counter every writer already has" is false; define one cycle base | ADDRESSED | Section 3 "One cycle base": the bridge's `cycle_count` through `sink.cycle()` for every writer; the bus driver's negedge counter is never a stamp; ctrl and scrkey interfaces need no counter. Code with the event part. |
| R2-L2 | continuity must exclude mret and dret records (plan C-1) | ADDRESSED | 5.1 text; code: gen_ut_export excludes `MRET_INSN`/`DRET_INSN` records (spec encodings, commented); re-run retained (`gen_export_s7_t080d_*` includes the seed-7 program). |
| R2-L3 | bind I lines to `markers=` as R to records and E to events | ADDRESSED | Section 2 binding rule; `read()` already asserted `len(markers) == flush.markers` (stated now). |
| R2-L4 | state every R/I/E value as %h and every marker key=value as decimal | ADDRESSED | Section 2 radix rule; code: the sink writes the flush and end markers with `%0d`, `read()` parses marker values as decimal and compares `seq` as decimal; header `seed=`/`counters=` were decimal already; re-run retained (`*_t080d_*`). |
| R2-L5 | rs3_addr/rs3_rdata need an exclusion basis or get exported; yaml comment | ADDRESSED | Exported: `gen_rvfi_txn` gained `rs3_addr`, `rs3_rdata` (sampled from the interface), the field list is 36 names, the yaml comment states the basis (rs3 feeds the draft-B ternary ops; the CHERIoT capability fields and mem_is_cap are the carve-out exclusion); re-run retained. |
| R2-L6 | the Zc program spins after its tohost store, it does not push a stack frame | ADDRESSED | 5.1 corrected: the "last store 0x8000039c" of attempt 2 was the flushed prefix ending before the tohost record (the flush came 4 cycles after the bus store, the record retired later), not a push after tohost; the transcript carries the same correction. |
| R2 prior: radix low | was NOT ADDRESSED in v4a | ADDRESSED | R2-L4. |
| R2 prior: Section 8 collision (API doc) | was fixed only in the uncommitted API doc | ADDRESSED | gen_component_api_rvfi_monitor.md: old Section 8 renumbered 9, new Section 8 "Record export"; in the landing set. |
| R2 prior: rs3 basis | was NOT ADDRESSED in v4a | ADDRESSED | R2-L5. |
| R2 prior: response section answered three of six while the v4a header claimed all folded | ADDRESSED | this table replaces the partial section; the v4b header names what it folds. |
| DV Lead round 4 (not a review row) | irq_pending_o and bus request events; COV_WITNESS command and CG-WIT-001 | ADDRESSED (text) | Section 8 rows (R2-M1); new Section 9 (COV_WITNESS, bins rendered from gen_trace_tp_bin.csv CG-WIT-001 rows, coverage only, build step 3). |

## Replan review r3 (`2026-09-03-claude-replan-gen_rvfi_export_addendum-r3.md`, of the text at 1f8186e, REQUEST-CHANGES)

| Row | Finding | Status | Where |
|---|---|---|---|
| R3-M1 | no `irq_pending_o` row, no request cycle on gnt (carried from r2) | ADDRESSED | Section 8 rows `misc irq_pending`, `ibus/dbus req`, `req_cycle` on gnt; yaml rows rendered at 6b3301d; writers with build step (2)/(3). |
| R3-M2 | MUT-G catch not same-instant (carried from r2) | ADDRESSED (text; code with step (2)) | Section 2 marker `ibus_grants= dbus_grants=`, Section 3 flush text and rule list, 5.2 MUT-G. |
| R3-M3 | no row per r2 finding; tohost row wrong | ADDRESSED | the R1/R2 table above (at 6d16d9c) and this section. |
| R3-L1 | radix: plan `%h`/`%0d` vs build | ADDRESSED | Section 2 radix rule (this commit corrects the header sentence: `seed=`, `counters=` decimal); code at 6b3301d: `%0d` markers, decimal reader. |
| R3-L2 | no single cycle base | ADDRESSED | Section 3 "One cycle base": `sink.cycle()` for event writers; the monitor's `gen_rvfi_if.cycle` is the same count by construction (both counters cited); `sink.cycle()` at 6b3301d. |
| R3-L3 | continuity must exclude mret/dret (C-1) | ADDRESSED | 5.1 text; gen_ut_export.py excludes the two encodings; run retained at 6b3301d. |
| R3-L4 | rule list omits the I-line count | ADDRESSED | Section 3 rule list names `I` lines == `markers` (this commit); `read()` has asserted it since 1f8186e. |
| R3-L5 | rs3 attributed to the CHERIoT carve-out | ADDRESSED | rs3 exported (36 fields) at 6b3301d; Section 2 states the basis. |
| R3-L6 | "pushes a stack frame" is false | ADDRESSED | 5.1: the Zc program spins after its tohost store. |
| R3-L7 | MUT-H names no bound | ADDRESSED (text) | 5.2 MUT-H: exact relation (line cycle == `cycle_count` at the FETCH_EN ack minus one; first `R` after it; gap recorded then asserted). |
| R3-L8 | icram under step (2) while gen_icache_ram.sv defers the hooks | ADDRESSED (text) | Section 8 build order: icram moved to step (3). |
| R3-L9 | `<name>` rows: header token and reader rule unstated; a misspelled token passes | ADDRESSED (text and code, this commit) | yaml: 29 exact rows (irq_fast with an `idx` field); codegen refuses `<name>`; `read()` refuses an `E` token that is not a header row; Section 8 rules; sink API document Section 2. |
| R3-L10 (N1) | stale pre-build names and "no SV or Python exists yet" | ADDRESSED | Sections 4, 7 and 8 at 6b3301d; line 6 status, `flush_export()`, header/marker residue this commit. |
| R3-L11 (N2) | measured sizes match no retained file | ADDRESSED | Section 3 restated from the out_t080d files (22133 / 29971 / 232434 bytes; 2008 records), retained at 6b3301d. |
| R3-L12 (N4) | "require the event header lines" overstates `read()` | ADDRESSED (text and code, this commit) | `read()` now requires every rendered row of every source in `sources=`; Section 3 rule list states it as built. |
| R3-N5 | API document says the R line is still formatted with the knob absent | ADDRESSED | gen_component_api_rvfi_monitor.md corrected at 6b3301d. |

## Replan review r4 (`2026-09-03-claude-replan-gen_rvfi_export_addendum-r4.md`, of 6d16d9c, REQUEST-CHANGES)

| Row | Finding | Status | Where |
|---|---|---|---|
| R4-M1 | wildcard `<name>` rows against the plan's exact-row sunset input | ADDRESSED (this commit) | as R3-L9: exact rows in the yaml, codegen and reader; Section 8 rules. |
| R4-M2 | COV_WITNESS accepts any index; C-2 owner-only acceptance unstated | ADDRESSED (text; knob and checks with build step 3) | Section 9: `+gen_witness_ids` rendered per test from the entry's `witness_ids`; foreign id `uvm_error GEN_WITNESS_FOREIGN`; index outside the global list stays `GEN_CMD_DISPATCH`. |
| R4-M3 | six r3 findings without a row; code claims cite uncommitted runs | ADDRESSED | R3 table above (every r3 finding); the R1/R2 preamble names 6b3301d for every code and run claim. |
| R4-L1 | MUT-H bound still unnamed | ADDRESSED (text) | as R3-L7. |
| R4-L2 | Section 3 flush text lacks the grant counters and the `E gnt` rule; who increments the bridge fields | ADDRESSED (text) | Section 3 flush paragraph and rule list; Section 8 trust-triad paragraph: the bus drivers increment them in the grant beat, independent of the line writer. |
| R4-L3 | `sink.cycle()` "by every writer" is not what the R/I writer does | ADDRESSED (text) | Section 3: the monitor's `gen_rvfi_if.cycle` is the same count by construction (gen_rvfi_if.sv:24-25, gen_bridge_if.sv:48-54). |
| R4-L4 | stale pre-build text (line 6, `flush()`, residue, `%h`/`%0d`, I count) | ADDRESSED | this commit: status sentence, `flush_export()` everywhere, sink writes the marker, header wording, radix sentence, I count in the rule list. |
| R4-L5 | measured sizes match no retained file | ADDRESSED | as R3-L11; the runs are committed at 6b3301d. |
| R4-L6 | icram under step (2) | ADDRESSED (text) | as R3-L8. |
| R4-L7 | Section 9 omits the group's standing and the anti-vacuity basis | ADDRESSED (text) | Section 9: weight 0, "witnessed clauses: N of M", anti-vacuity by `check_test_source` (C-1), not the TB. |
| R4-L8 | header "every key=value is decimal" is false; header-row rule overstated | ADDRESSED (text and code, this commit) | Section 2 radix rule names `seed=` and `counters=`; `read()` per-source row requirement (R3-L12). |
| R4-L9 | lag: markers `%0h` etc. at 6d16d9c, working tree uncommitted | ADDRESSED | landed at 6b3301d (T-080 landing 1a). |
