# TDD transcript: the test template proven on gen_test_boot_retire (red first, then green)

Owner: test-writer. Date: 2026-09-03 (08:21-08:31 UTC local bring-up; Runtime runs appended in
Section 4 when their manifests land). Build configuration `opentitan`, DUT `gen_dut_top`
(ibex_core + ibex_register_file_ff), TB top `gen_tb_top` at the step-2b tree (irq/dbg agents,
REGIME_SET consumer; `dv/auto_dv/env/gen_env_pkg.sv` of 08:21 UTC). Files under test:
`dv/auto_dv/tests/gen_test_template.py`, `gen_test_lib.py`, `gen_test_boot_retire.py`,
`gen_programs/gen_boot_retire_red.S`; API `dv/auto_dv/docs/gen_test_template_api.md`.

Local out-tree (not committed, retained): `dv/auto_dv/work/test-writer/out_tpl/` (compile
`compile.log`, simv 04:21:50 local = 08:21:50 UTC; runs `red_s1/`, `green_s1/`, `green_s2/`,
`green_s3/`, each with `sim.log` and `stdout.log`; `runs_summary.txt` is the driver's one line per
run). Programs: `dv/auto_dv/work/test-writer/prog_s{1,2,3}/` (riscv-dv `gen_rand_smoke`, seeds 1-3,
`seed_used` cross-checked by gen_program.py) and `prog_red/` (the red fixture; its `--spike-check`
reports `*** FAILED *** (tohost = 1)`, exit 1, by construction). The host clock is UTC-4.

## 1. Host self-test of the library (first)

```
$ python3 dv/auto_dv/tests/gen_test_lib.py --self-test
GEN_TEST_LIB self-test PASS (schedule k=4: imem_gnt_delay:same_cycle@c0,imem_rvalid_delay:short@c0,imem_outstanding_cap:cap2@c0,dmem_gnt_delay:random@c0,dmem_rvalid_delay:min1@c0,scr_key_delay:withheld_then_valid@c0,imem_rvalid_delay:min1@c1930,scr_key_delay:delayed@c20592,imem_rvalid_delay:long@c20592,dmem_gnt_delay:same_cycle@c20592,dmem_rvalid_delay:long@c21490,dmem_gnt_delay:random@c21490)
```

## 2. Red: the fire-check on the red fixture program (seed 1)

Fixture `gen_programs/gen_boot_retire_red.S`: nine instructions, then `tohost <- 3` (the FAIL code),
and a declared floor `gen_min_retired = 1000` it never reaches, so both halves of the fire-check
must fail through the Python assert. Run `red_s1` (sim.log mtime 04:29:42.05 local, md5
acb6b75d68eebdfbdf52379c9bea0299):

```
Command: /localdev/fzhang/ws/ibex-challenge/dv/auto_dv/work/test-writer/out_tpl/vcs_simv +vcs+lic+wait +ntb_random_seed=1 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=.../prog_red/prog.vmem +gen_mem_image_crc32=d70f2186 +gen_mem_image_words=25 +gen_boot_addr=80000000 +gen_tohost_addr=800000c0 +gen_fetch_en_at_reset=0
Compiler version X-2025.06-SP2_Full64; Runtime version X-2025.06-SP2_Full64;  Sep  3 04:29 2026
GEN_CONFIG_BANNER tb=gen_tb_top uvm_test=gen_base_test seed=1 build_config=opentitan pinned_knobs=0 regime_sched=derived
     0.00ns INFO  GEN_TEST_SEED test=gen_test_boot_retire seed=1 image=.../prog_red/prog.vmem
   255.00ns INFO  GEN_TEST_READBACK ok words=64
   255.00ns INFO  GEN_TEST_KNOBS pinned=- drawn=dmem_gnt_delay=random dmem_rvalid_delay=min1 imem_gnt_delay=same_cycle imem_outstanding_cap=cap4 imem_rvalid_delay=long scr_key_delay=withheld_then_valid
   255.00ns INFO  GEN_TEST_SCHED source=derived k=1 sched=imem_gnt_delay:same_cycle@c0,imem_rvalid_delay:long@c0,imem_outstanding_cap:cap4@c0,dmem_gnt_delay:random@c0,dmem_rvalid_delay:min1@c0,scr_key_delay:withheld_then_valid@c0
   325.00ns INFO  GEN_TEST_RELEASE cycle=27
  1420.00ns INFO  GEN_TEST_EOT code=0x00000003 stores=1 retired=9 cycle=137
  1420.00ns INFO  GEN_TEST_FIRE fire_schedule_applied ok=True applied 6 of 6 scheduled entries (k=1, source=derived)
  1420.00ns INFO  GEN_TEST_FIRE fire_eot_pass_code ok=False tohost code 0x00000003 (pass = 1)
  1420.00ns INFO  GEN_TEST_FIRE fire_retired_floor ok=False retired 9 (floor 1000 from the program)
  1420.00ns INFO  GEN_TEST_BINS n=0 -
AssertionError: GEN_TEST_FAIL gen_test_boot_retire: 2 fire-check failure(s): fire_eot_pass_code: tohost code 0x00000003 (pass = 1) | fire_retired_floor: retired 9 (floor 1000 from the program)
** TESTS=1 PASS=0 FAIL=1 SKIP=0   1420.01   0.05   28526.73 **
UVM_ERROR :    0
UVM_FATAL :    0
CPU Time:      0.390 seconds
```

Read: the TB mechanics passed (read-back, layers, release), the program ended with code 3, and the
test failed through its own fire-check assert (both halves named), not through a TB check or a
timeout. No `GEN_TEST_PASS` line. Driver line: `red_s1 ... cocotb_pass=0 cocotb_fail=1`.

## 3. Green: riscv-dv gen_rand_smoke at seeds 1, 2, 3 (same build)

| Run | sim.log mtime (local) | md5 | seed | GEN_TEST_SCHED | EOT | fire-checks | cocotb |
|---|---|---|---|---|---|---|---|
| green_s1 | 04:29:15.15 | 9fc5222b20e310abdf29143cc6eb7a47 | 1 | k=1 (phase 0 only: imem gnt same_cycle, rvalid long, cap4; dmem gnt random, rvalid min1; key withheld_then_valid) | code 1, retired 550, cycle 4240 | schedule 6/6 applied; eot_pass_code ok; retired_floor 550 >= 300 | PASS (42450.01 ns, CPU 0.510 s) |
| green_s2 | 04:30:14.65 | 9e3c9afef63ab1883650b38166c0be09 | 2 | k=3; boundaries c18754, c20349 not reached before the end of test | code 1, retired 533, cycle 4728 | schedule 6/15 entries applied = every reached one; eot ok; 533 >= 300 | PASS (47330.01 ns, CPU 0.560 s) |
| green_s3 | 04:30:17.38 | 59ba6e8af53b653b7f29dfac7be1c3b4 | 3 | k=3; boundaries c1969 (4 knobs) and c3442 (2 knobs) applied at cycles 1970-1973 and 3443-3444 | code 1, retired 516, cycle 6787 | schedule 12/12 applied; eot ok; 516 >= 300 | PASS (67920.01 ns, CPU 0.530 s) |

Identifying lines of green_s3 (the run that exercised layer 3 at run time):

```
Command: .../out_tpl/vcs_simv +vcs+lic+wait +ntb_random_seed=3 +UVM_TESTNAME=gen_base_test +UVM_VERBOSITY=UVM_LOW +UVM_NO_RELNOTES +gen_build_config=opentitan +gen_mem_image=.../prog_s3/prog.vmem +gen_mem_image_crc32=f7013dee +gen_mem_image_words=28943 +gen_boot_addr=80000000 +gen_tohost_addr=800027c0 +gen_fetch_en_at_reset=0
Compiler version X-2025.06-SP2_Full64; Runtime version X-2025.06-SP2_Full64;  Sep  3 04:30 2026
GEN_CONFIG_BANNER tb=gen_tb_top uvm_test=gen_base_test seed=3 build_config=opentitan pinned_knobs=0 regime_sched=derived
   645.00ns INFO  GEN_TEST_SCHED source=derived k=3 sched=imem_gnt_delay:random@c0,imem_rvalid_delay:long@c0,imem_outstanding_cap:cap1@c0,dmem_gnt_delay:random@c0,dmem_rvalid_delay:long@c0,scr_key_delay:delayed@c0,imem_gnt_delay:long@c1969,imem_rvalid_delay:short@c1969,scr_key_delay:withheld_then_valid@c1969,dmem_rvalid_delay:random@c1969,imem_gnt_delay:short@c3442,imem_rvalid_delay:min1@c3442
 19755.00ns INFO  GEN_TEST_PHASE idx=1 trigger=c1969 knob=imem_gnt_delay value=long cycle=1970
 19765.00ns INFO  GEN_TEST_PHASE idx=1 trigger=c1969 knob=imem_rvalid_delay value=short cycle=1971
 19775.00ns INFO  GEN_TEST_PHASE idx=1 trigger=c1969 knob=scr_key_delay value=withheld_then_valid cycle=1972
 19785.00ns INFO  GEN_TEST_PHASE idx=1 trigger=c1969 knob=dmem_rvalid_delay value=random cycle=1973
 34485.00ns INFO  GEN_TEST_PHASE idx=2 trigger=c3442 knob=imem_gnt_delay value=short cycle=3443
 34495.00ns INFO  GEN_TEST_PHASE idx=2 trigger=c3442 knob=imem_rvalid_delay value=min1 cycle=3444
 67920.00ns INFO  GEN_TEST_EOT code=0x00000001 stores=1 retired=516 cycle=6787
 67920.00ns INFO  GEN_TEST_FIRE fire_schedule_applied ok=True applied 12 of 12 scheduled entries (k=3, source=derived)
 67920.00ns INFO  GEN_TEST_FIRE fire_eot_pass_code ok=True tohost code 0x00000001 (pass = 1)
 67920.00ns INFO  GEN_TEST_FIRE fire_retired_floor ok=True retired 516 (floor 300 from the program)
 67920.00ns INFO  GEN_TEST_BINS n=0 -
 67920.00ns INFO  gen_test_boot_retire GEN_TEST_PASS
UVM_ERROR :    0
UVM_FATAL :    0
** TESTS=1 PASS=1 FAIL=0 SKIP=0   67920.01   0.19   351633.79 **
```

The SV side logged one `[GEN_PHASE]` line per applied REGIME_SET (6 for seed 1, 12 for seed 3), no
`GEN_CMD_DISPATCH` error. The three seeds drew three different layer-2 sets and schedules (the
`GEN_TEST_KNOBS` / `GEN_TEST_SCHED` lines differ), so the one-seed rule is visible per seed.

## 3b. Same test on the HEAD tree (no REGIME_SET consumer), after the consumer gate

At 08:27 UTC TB Infra reset the shared TB files to HEAD plus its T-068 edits and parked step 2b, so
a fresh build has no REGIME_SET consumer (a REGIME_SET is a collected `GEN_CMD_DISPATCH` error
there). `gen_test_lib.SCHEDULABLE_KNOBS` is therefore gated to the knobs the build consumes (empty
at HEAD; the tuples to restore are named in the file), and the template logs the layers as not
applied instead of failing on a consumer-less command. Fresh compile `out_head/` (08:40 UTC,
0 errors, `vcs_simv` 04:40 local), same two programs, seed 1:

| Run | sim.log mtime (local) | md5 | GEN_TEST lines | cocotb |
|---|---|---|---|---|
| out_head/green_s1 | 04:40:45.58 | 3711d8ca4e9293347f3ac3a199c2d299 | `GEN_TEST_KNOBS pinned=- drawn=-`, `GEN_TEST_SCHED source=derived k=0 sched=-`, `GEN_TEST_EOT code=0x00000001 stores=1 retired=550 cycle=1924`, `GEN_TEST_LAYERS not_applied reason=no schedulable knob for this test (schedulable=-)`, `fire_eot_pass_code ok=True`, `fire_retired_floor ok=True retired 550 (floor 300 from the program)`, `gen_test_boot_retire GEN_TEST_PASS` | PASS (19290.01 ns), UVM_ERROR 0 |
| out_head/red_s1 | 04:40:49.99 | c35c9089f9778e2c19f49e9580a5cb84 | `GEN_TEST_EOT code=0x00000003 stores=1 retired=9 cycle=55`, `fire_eot_pass_code ok=False`, `fire_retired_floor ok=False retired 9 (floor 1000 from the program)`, `AssertionError: GEN_TEST_FAIL gen_test_boot_retire: 2 fire-check failure(s): ...` | FAIL (600.01 ns), UVM_ERROR 0 |

Read: with all knobs at their yaml defaults (short/short/cap8, key immediate) the same program
finishes at cycle 1924 instead of 4240 (Section 3, seed 1 with long rvalid latency and cap4 drawn),
which is the timing regime doing its work. The fire-check verdicts are unchanged.

## 4. Runtime runs (purpose 1, LSF through the flow)

Requests `test-writer-001.yaml` (red) and `test-writer-002.yaml` (green) filed 08:30 UTC were
REFUSED by Runtime at 08:47 UTC on a YAML parse error in their `notes:` line (an unquoted
`(T-058): ` colon inside a plain scalar; `dv/auto_dv/work/runtime/results/test-writer-001/manifest.yaml`
and `-002/manifest.yaml` record the refusal, not a run). Re-filed 08:49 UTC with block-scalar notes
and `yaml.safe_load` checked: `test-writer-003.yaml` (red, `gen_test_boot_retire_red`, seed 1,
expected verdict FAIL) and `test-writer-004.yaml` (green, `gen_test_boot_retire`, 3 seeds, expected
PASS). Both were accepted and served at 08:56 UTC (`dv/auto_dv/work/runtime/results/test-writer-003/manifest.yaml`,
`-004/manifest.yaml`) but every run is NOT_RUN: the flow's fresh compile of the gen_tb working tree
failed (`build/gen_tb/compile.log` line 626, `Error-[TFAFTC] Too few arguments to function/task call`,
`dv/auto_dv/env/gen_rvfi_pkg.sv:183` calling `gen_isa_step_dpi` against TB Infra's in-progress T-068
edit of `dv/auto_dv/isa/gen_isa_dpi_pkg.sv`; not a test defect: the same modules compiled and ran in
Sections 2, 3 and 3b on consistent trees). Re-filed as `test-writer-005.yaml` (red) and
`test-writer-006.yaml` (green), held by Runtime until its compile precheck was green again.

Served 09:03 UTC (received 09:03:28Z, both `--local`, concurrent, build gen_tb ok in 23 s each;
manifests `dv/auto_dv/work/runtime/results/test-writer-005/manifest.yaml` and
`test-writer-006/manifest.yaml`; out-trees `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_req_test-writer-005`
and `-006`; regress command `gen_regress.py --tests <test> --seed-list 1 | --seeds 3 --no-coverage
--local --purpose 1`):

| Request | Test, seed (source) | Program (word count, crc32) | Flow verdict and reason | Evidence line (result.yaml) | cocotb / UVM |
|---|---|---|---|---|---|
| -005 (red) | gen_test_boot_retire_red, 1 (run) | directed gen_boot_retire_red.S (25, 0xd70f2186) | FAIL, `sv_fatal at log line 100` (the flow's collected-mechanism class for the `GEN_*_FAIL` token; the token is the test's own `GEN_TEST_FAIL` tag) | `AssertionError: GEN_TEST_FAIL gen_test_boot_retire: 2 fire-check failure(s): fire_eot_pass_code: tohost code 0x00000003 (pass = 1) \| fire_retired_floor: retired 9 (floor 1000 from the program)` | TESTS=1 PASS=0 FAIL=1; marker_seen False; UVM_ERROR 0, UVM_FATAL 0 |
| -006 (green) | gen_test_boot_retire, 870932068 (run) | riscv-dv gen_rand_smoke (28959, 0x0cd43174) | PASS, `no collected failure mechanism; end marker and config banner present` | `GEN_TEST_EOT code=0x00000001 stores=1 retired=474 cycle=1817`; `fire_retired_floor ok=True retired 474 (floor 300 from the program)`; `gen_test_boot_retire GEN_TEST_PASS` | TESTS=1 PASS=1; UVM_ERROR 0, UVM_FATAL 0; wall 3.6 s |
| -006 (green) | gen_test_boot_retire, 995813351 (run) | riscv-dv gen_rand_smoke (29151, 0x9dceaeee) | PASS, same reason | `GEN_TEST_EOT code=0x00000001 stores=1 retired=496 cycle=1961`; `fire_retired_floor ok=True retired 496 (floor 300 from the program)`; `gen_test_boot_retire GEN_TEST_PASS` | TESTS=1 PASS=1; UVM_ERROR 0, UVM_FATAL 0; wall 3.8 s |
| -006 (green) | gen_test_boot_retire, 1486148200 (run) | riscv-dv gen_rand_smoke (29151, 0xd7b0c3ad) | PASS, same reason | `GEN_TEST_EOT code=0x00000001 stores=1 retired=487 cycle=2039`; `fire_retired_floor ok=True retired 487 (floor 300 from the program)`; `gen_test_boot_retire GEN_TEST_PASS` | TESTS=1 PASS=1; UVM_ERROR 0, UVM_FATAL 0; wall 4.2 s |

Every run logs `GEN_TEST_KNOBS pinned=- drawn=-`, `GEN_TEST_SCHED source=derived k=0 sched=-` and
`GEN_TEST_LAYERS not_applied ...`: the tree at 09:03 UTC has no REGIME_SET consumer (Section 3b),
so these runs prove the fire-checks and the flow's verdict path, not the layers. Per-run logs:
`<out-tree>/runs/<test>_<seed>/{sim.log, sim_stdout.log, result.yaml, run_cmd.sh}`; the seeds are
the flow's derived seeds for `seeds: 3` (`scope.base_seed` in the regression manifest reproduces
them).

## 5. Limitations recorded

- Layer 3 at run time was exercised on seed 3 only in this set (seed 1 drew K=1; seed 2's boundaries
  lay beyond the program's end): the schedule's duration classes (CG-REG-007) are longer than a
  300-instruction program. The REG tests will size programs to the classes; the template's
  schedule check accepts unreached phases by design and rejects a reached-but-unapplied one.
- The phase count on the SV side (`[GEN_PHASE]` lines) is not readable from Python; the
  fire-check counts Python's own applied entries and relies on the flow's log scan for a
  dispatcher error (asked of TB Infra: a bridge field with the SV count).
- No covergroup exists yet, so no bin is declared or checked in these runs.
- On the HEAD tree (Section 3b, and Runtime's runs until step 2b re-lands) layers 2 and 3 are not
  applied at all: every knob stays at its yaml default and the run says so (`GEN_TEST_LAYERS
  not_applied`). The three-layer randomization of the boot test is therefore proven on the step-2b
  build only; it is re-proven on the landed tree by re-running the three seeds when
  `gen_test_lib.SCHEDULABLE_KNOBS` is restored.
