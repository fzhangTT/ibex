# TDD transcript: the internal-NMI mtval correction moved out of the suppress-flag block (TB defect T11)

Component: `dv/auto_dv/env/gen_rvfi_pkg.sv` (the scoreboard) and `dv/auto_dv/tb/gen_tb_pkg.sv`
(`gen_bus_err_log` gains `peek_intg_word`). Owner: tb-infra. Written 2026-09-08T03:31:11Z. The defect is TB defect
register row T11, filed from the count-1 measurement of landing 64 (`gen_tdd_b16_knob.md` Section 7).

Build: local `gen_tb_local.sh compile`, sources sha256 first-16 `ec5ff5d8019e575c`, vcs exit 0, out tree
`dv/auto_dv/out_t11`. The pre-fix build it is compared against is landing 64's, `047718cec02eec6a`, in
`dv/auto_dv/out_b16knob2`. Every run below is seed 1 through `gen_run_fixture.sh`.

TWO BUILD IDENTITIES, and the difference is not a discrepancy. The evidence runs of Section 2 were made on
`ec5ff5d8019e575c`, the working tree, which also carries the undelivered landing-66 delta. The hand-off
verification assembled a tree from THIS LANDING'S LIST ALONE on a fresh archive of HEAD, so it does not
carry that delta and its identity is `5a169446edf73d4c`. Both reproduce the same four run outcomes, which is
what makes the fix independent of landing 66.

## 1. The defect, in one paragraph

The DUT's internal-NMI mtval is the LSU's last address (`rtl/ibex_controller.sv:416`,
`rtl/ibex_load_store_unit.sv:258`): for a misaligned access whose FIRST word carried the announced
corruption that is the access address, not the announced word address. The scoreboard knew that rule and
applied it, but only inside the block guarded by `rvfi_ext_rf_wr_suppress`. With the flag clear, which is
bug candidate B16, the correction never ran, the model kept the word address, and the crash_dump rule fired
once per following record until the window drained: 20 or 21 wrong-reason errors on every count-1 run.

The correction could not simply move out of that block, because the block CONSUMES the announcement there
(`take_intg_word`) as part of the suppressed-write gate's accounting, so a moved copy would find nothing.
The fix is a PEEK that leaves the announcement in place, at one site that runs for every memory record
before the take. The store branch that did the same correction for stores without the flag folds into that
one site rather than becoming a third copy: a store's corruption is never in the gate's list, so its own
write mask is the match there.

## 2. Red and green, the same four runs on both builds

| run | pre-fix, build 047718cec02eec6a | post-fix, build ec5ff5d8019e575c |
|---|---|---|
| b16_c1, the count-1 case | 21 crash_dump, 1 isa_rd | 1 isa_rd |
| b16_c2, the count-2 control | no error, cocotb PASS | no error, cocotb PASS |
| intg_store, the misaligned store | no error, cocotb PASS | no error, cocotb PASS |
| lockstep_plain | no error, cocotb FAIL | no error, cocotb FAIL |

The one intended change is the 21 crash_dump rows going away while the isa_rd row, which IS the B16 finding,
stays. The three controls do not move at all.

`intg_store` is the control that matters most, because the fix DELETED the store branch that used to carry
this correction for a misaligned store. Its run is clean on both builds, so the store path did not move.

`lockstep_plain` fails identically on both builds and it is not a regression: its cocotb assertion is
"GEN_UT_LOCKSTEP: program did not report pass", because the program it runs is test-writer's B17 reproducer,
which stores a failing end-of-test code by design. It is in the set as a fourth control on a program with
many ordinary loads and stores, and its zero UVM errors on both builds is the point.

## 3. Waveform confirmation (LOG-103)

Retained as `gen_fu_t11_waveform.log`. In the count-1 run, one cycle after the second response beat, the
DUT latches `crash_dump_o.exception_addr` = 0x800002e2, the access address, while the announced word was
0x800002e0, and `rvfi_ext_rf_wr_suppress` never rises in the window. So the record the scoreboard judges has
the flag clear and the DUT has already committed to the access address: the correction has to run for that
record, which is exactly what the fix does and what the old placement prevented.

## 4. Checks run

- `gen_knobs_codegen.py --check`: up to date (the yaml is untouched; the new function is hand-written code
  outside the rendered block).
- The compile above, vcs exit 0.
- The four runs of Section 2 on both builds, and the waves run of Section 3.

## 5. Retained logs

Under `dv/auto_dv/evidence/gen_tdd_logs/lockstep/`: `gen_fu_t11_before.log` and `gen_fu_t11_after.log`
(the two four-run tables), `gen_fu_t11_waveform.log`, and the count-1 run's own sim log on each build,
`gen_fu_t11_b16_c1_pre_sim.log` and `gen_fu_t11_b16_c1_post_sim.log`, with their manifest rows in the same
hand. This fix and the counter model's follow-on are handed together because both re-render
`dv/auto_dv/tb/gen_tb_pkg.sv`, so neither could carry that file alone.
