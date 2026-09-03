# MUT-A..MUT-F: the record export's consumer checks (gen_export.read, gen_ut_export) proven against mutations

Format: dv/auto_dv/mutations/README.md. The export (architecture Section 9, dv/auto_dv/docs/gen_rvfi_export_addendum.md)
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
