# MUT-A..MUT-F: the record export's consumer checks (gen_export.read, gen_ut_export) proven against mutations

Format: dv/auto_dv/mutations/gen_README.md. The export (architecture Section 9, dv/auto_dv/docs/gen_rvfi_export_addendum.md)
is observation only; its consumer checks live in the Python reader `dv/auto_dv/gen_tb/gen_export.py` (`read(path,
seq)`: count, order, cycle, header and marker rules) and in the test `gen_tb/gen_tests/gen_ut_export.py` (content
checks derived from the program). Each mutation below is a source edit of the SV producer, compiled into its own
build (`dv/auto_dv/work/tb-infra/out_t080_mut_<x>`, vcs exit 0), run on the directed Zc program with hidden
referees inert (`+gen_chk_all=0`, so the ISA comparator cannot catch the same defect), then run again with the
NAMED Python rule disabled by a temporary edit (the ablation control), and every edit reverted (cmp identical,
"final: sources identical to pre-mutation" in the driver logs). Executed 2026-09-03 (T-080). Retained logs:
`dv/auto_dv/evidence/gen_tdd_logs/mutations/gen_mut_export_*` (manifest `gen_tdd_logs/gen_manifest.md`). The runs
predate the v4b radix edit (hex marker values then, decimal now); the mutated statements are the same and the line
numbers below are those of the build each mutation ran on (gen_export_pkg.sv:99 is now :100 after a comment line).

    id: MUT-A (exported field corrupted)
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:88 (gen_rvfi_monitor::sample)
    original: t.pc_rdata = vif.pc_rdata; t.pc_wdata = vif.pc_wdata;
    mutated:  t.pc_rdata = vif.pc_rdata; t.pc_wdata = vif.pc_wdata + 32'h2;
    expected_detector: gen_ut_export pc-continuity check (pc_rdata[k+1] == pc_wdata[k])
    result: CAUGHT: "AssertionError: GEN_UT_EXPORT: 153 pc discontinuities between consecutive records", verdict FAIL.
      ablation_control: continuity assert disabled -> GEN_UT_EXPORT_PASS, verdict PASS (SURVIVED).

    id: MUT-B (dropped record: records++ runs, one R line skipped)
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:122 (gen_rvfi_monitor::run_phase)
    original: if (sink != null && sink.enabled) sink.write_record(gen_export_record_line(t, cfg.export_counters));
    mutated:  if (sink != null && sink.enabled && records != 50) sink.write_record(gen_export_record_line(t, cfg.export_counters));
    expected_detector: read(): marker records == retired
    result: CAUGHT: "AssertionError: GEN_EXPORT: marker records 174 != retired 175 (the sink and the bridge disagree)".
      ablation_control (the single-rule steps are reasoning, not retained runs; retained: all rules disabled PASS, and in attempt 1 two disabled caught by continuity): records==retired rule disabled -> caught next by the order rule; order rule disabled -> caught
      by the fixture's continuity check; all three disabled -> GEN_UT_EXPORT_PASS (SURVIVED). Three independent
      catchers for a dropped record.

    id: MUT-C (two adjacent records swapped)
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:67 (member `string held`) and :122
    original: if (sink != null && sink.enabled) sink.write_record(gen_export_record_line(t, cfg.export_counters));
    mutated:  hold record 50 and write it after record 51 (see gen_mut_export_c_mutation.txt for the full line)
    expected_detector: read(): order strictly +1
    result: CAUGHT: "AssertionError: GEN_EXPORT: order 51 after 49 (line 53)".
      ablation_control (single-rule steps are reasoning, not retained runs, as for MUT-B): order rule disabled -> caught by the cycle rule; both disabled -> caught by the fixture's
      continuity check; all three disabled -> GEN_UT_EXPORT_PASS (SURVIVED).

    id: MUT-D (flush marker suppressed, $fflush still done)
    file: dv/auto_dv/env/gen_export_pkg.sv:99 (gen_export_sink::flush_export)
    original: $fwrite(fd, "# flush seq=%0h records=%0h retired=%0h markers=%0h events=%0h cycle=%0h\n", ...);
    mutated:  (the $fwrite removed)
    expected_detector: read(path, seq): a complete flush marker with that seq is required
    result: CAUGHT: "AssertionError: GEN_EXPORT: no complete flush marker with seq=2 in gen_export.txt".
      ablation_control: read() accepts end-of-file as the boundary (synthetic marker from the parsed counts) ->
      GEN_UT_EXPORT_PASS (SURVIVED).

    id: MUT-E (the record set contradicts the program: first record's pc moved)
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:88 (gen_rvfi_monitor::sample)
    original: t.pc_rdata = vif.pc_rdata; t.pc_wdata = vif.pc_wdata;
    mutated:  t.pc_rdata = (records == 0) ? vif.pc_rdata + 32'h4 : vif.pc_rdata; t.pc_wdata = vif.pc_wdata;
    expected_detector: gen_ut_export first-pc check (boot page + 0x80 from the image entry)
    result: CAUGHT: "AssertionError: GEN_UT_EXPORT: first record pc 0x80000084 != boot page + 0x80 (0x80000080)".
      ablation_control: first-pc assert disabled -> GEN_UT_EXPORT_PASS (SURVIVED).

    id: MUT-F (stale marker: only the first flush writes a marker; the test flushes twice)
    file: dv/auto_dv/env/gen_export_pkg.sv:99 (gen_export_sink::flush_export)
    original: $fwrite(fd, "# flush seq=%0h ...", flushes, records, bvif.evt_retired_count, markers, events, bvif.cycle_count);
    mutated:  if (flushes == 1) $fwrite(fd, "# flush seq=%0h ...", ...);
    expected_detector: read(path, seq=2): the marker must carry the sequence of the flush just issued
    result: CAUGHT: "AssertionError: GEN_EXPORT: no complete flush marker with seq=2 in gen_export.txt".
      ablation_control: binding disabled (any flush marker accepted) -> the stale seq=1 marker of the early flush
      (zero records) is still caught by the fixture's content checks (records-non-empty / first-pc: attempt 1,
      IndexError, gen_mut_export_f_attempt1_ablation_stdout.log); binding AND every fixture content check disabled
      -> GEN_UT_EXPORT_PASS (SURVIVED). The stale-marker defect is what read()'s binding exists for: a test with
      no content checks of its own would pass on it.

Not yet covered (arrive with build step (2), the event lines): MUT-G dropped event, MUT-H wrong event cycle.

## Step 2 (version 4d): MUT-G and MUT-H executed, out of tree

| Id | Mutation | Vehicle and knobs | Catch | Ablation |
|---|---|---|---|---|
| MUT-H | gen_ctrl_driver stamps the fetch_enable line with `sink.cycle() + 1` | gen_ut_export on the Zc image, `+gen_chk_all=0` (the export checks are the test's own) | FAIL: `GEN_UT_EXPORT: fetch_enable line offset -1 != 0` (the fixture's exact offset, recorded 0 on the first green) | `FETCH_EN_LINE_OFFSET = None` in the copy's test: PASS |
| MUT-G | gen_bus_driver drops the third gnt line while `grants` and the bridge's grant counter still increment (gen_agents_pkg.sv, the gnt `write_event` guarded by `grants != 3`) | gen_ut_export on the Zc image, `+gen_chk_all=0` | FAIL: `GEN_EXPORT: 153 E ibus gnt lines, marker says ibus_grants=154` (read()'s gnt-count rule; the first mutant text was malformed and did not compile, gen_mut_export_gh_batches.log) | `read()`'s gnt-count assert replaced by `pass` in the copy: PASS |

Both mutants are built from a scratch copy of dv/auto_dv (gen_tdd_logs/mutations/gen_mut_export_MUT{G,H}_*); the ablation
is a second edit of the same copy (Python only, no recompile) so the catch and the ablation run on one build. The shared
tree's gen_agents_pkg.sv / gen_export.py / gen_ut_export.py checksums are printed unchanged after each mutant.

## MUT-I, MUT-J, MUT-K: the T-141 presence rules and the writer-registration fatal (follow-up landing, 2026-09-03)

Out of tree as above (scratch mut_root/MUTI, MUTJ, MUTK; batch log gen_tdd_logs/mutations/gen_fu_oot_mutation_batch.log
prints the shared tree's five source shas at start and end, unchanged). Vehicle for MUT-I / MUT-J: gen_ut_export on the Zc
image with `+gen_chk_all=0` (the format rules are read()'s, no UVM knob applies); the ablation is a Python-side edit of
gen_export.py that turns the one rule off, on the same mutated build. MUT-K has no ablation knob: a fatal; the same build
without the mutation is every green run of the landing.

| Id | Mutation | Catching run | Catch result | Ablation |
|---|---|---|---|---|
| MUT-I | gen_agents_pkg.sv:291 (gen_bus_driver): the E req line is never written (`req_stamp` still taken) | gen_ut_export zc | FAIL: `AssertionError: GEN_EXPORT: ibus: 0 E req lines against 154 E gnt lines (at most one request awaits its grant; MUT-I)` | gen_export.py rule `n_req - n in (0, 1)` replaced by `pass`: PASS |
| MUT-J | gen_agents_pkg.sv:275 (gen_bus_driver): the E rvalid line is never written | gen_ut_export zc | FAIL: `AssertionError: GEN_EXPORT: ibus: 154 E gnt lines against 0 E rvalid lines (outstanding responses must stay within 0..8; MUT-J)` | gen_export.py rule `0 <= n - n_rv <= BUS_MAX_OUTSTANDING[bus]` replaced by `pass`: PASS |
| MUT-K | gen_agents_pkg.sv:405 (gen_scrkey_driver): `sink.register_row("scrkey", "req"); sink.register_row("scrkey", "valid");` removed | gen_ut_boot zc WITHOUT `+gen_export_file`, and once more with it | FAIL both: `UVM_FATAL gen_export_pkg.sv(100) @ 0: sink [GEN_EXPORT] emitted row scrkey/req has no registered writer in this build (export_active_sources lists scrkey)` | none (fatal); the unmutated build's runs pass |

Exact edits: MUT-I original `if (ev_on()) begin / req_stamp = sink.cycle(); / sink.write_event(cfg.is_data ? gen_export_line_dbus_req(req_stamp, vif.addr, req_we(), req_be()) : gen_export_line_ibus_req(req_stamp, vif.addr, req_we(), req_be())); / end`, mutated `if (ev_on()) begin / req_stamp = sink.cycle();   // MUT-I: the req writer is silent / end`; MUT-J original `if (ev_on()) sink.write_event(cfg.is_data ? gen_export_line_dbus_rvalid(sink.cycle(), p.addr, p.we, p.err, p.intg_bad, pend.size()) : gen_export_line_ibus_rvalid(...));`, mutated `;   // MUT-J: the rvalid writer is silent`; MUT-K as in the table.
The MUT-G row's citation of gen_mut_export_gh_batches.log is now backed by the retained file (with the checksum lines).

## MUT-L: the misc stamp rule of gen_ut_export (landing 2a, Critic step-2 L-4)

| Id | Mutation | Catching run | Catch result | Ablation |
|---|---|---|---|---|
| MUT-L | gen_checkers_pkg.sv (gen_misc_monitor::write_changes): the `misc crash_dump_current_pc` line carries the PREVIOUS sample's value (`ev_init ? cd_cur_q : current_pc`), so the line for a pc appears one change late with a correct stamp | gen_ut_export zc, `+gen_chk_all=0` | FAIL: `AssertionError: GEN_UT_EXPORT: crash_dump_current_pc line offset -5 != 2 (record cycle 70, line cycle 75)` | gen_ut_export.py `MISC_CURRENT_PC_LINE_OFFSET = None`: PASS |

Two forms discarded and recorded: (1) the stamp shifted by one (`c + 1`) is caught, but its ablation FAILS too, on read()'s
non-decreasing-cycle rule (the other rows of the same posedge keep stamp c), so the proof was not the stamp rule's; (2) the
misc monitor sampling at the negedge is not a defect (the value-stamp pairs are identical) and passed both runs. The stale
value is the class the rule owns: a right-ordered file whose misc row lags the record it describes.

## MUT-I, MUT-J, MUT-K re-run on the landing-1c tree (CM18-M-2, 2026-09-03)

Built out of tree from the final landing-1c sources (the copy's build f, sources sha256 a056526d879ea458) plus the one
edit each; the mutant builds' own `sources sha256`: MUT-I 85a0229e7139b2dc, MUT-J 2add9023a38be7f1, MUT-K 1b2501fd1b7197e3
(gen_fu_l1c_MUT{I,J,K}_build_compile.log). The reader's messages no longer carry the mutant ids (CR7-L-7; the ids live
here). MUT-I catch on gen_ut_export zc: FAIL `AssertionError: GEN_EXPORT: ibus: 0 E req lines against 154 E gnt lines (at
most one request awaits its grant)`, ablation (the rule replaced by `pass`) PASS; MUT-J catch: FAIL `AssertionError:
GEN_EXPORT: ibus: 154 E gnt lines against 0 E rvalid lines (outstanding responses must stay within 0..8)`, ablation PASS;
MUT-K: `UVM_FATAL gen_export_pkg.sv(100) @ 0 ... emitted row scrkey/req has no registered writer in this build
(export_active_sources lists scrkey)` on gen_ut_boot zc both without and with `+gen_export_file` (gen_fu_l1c_MUTK_catch_*).
The gen_mut_export.md MUT-K row's anchor is gen_agents_pkg.sv:405 (CS3-D).
