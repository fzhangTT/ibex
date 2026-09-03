# Transcript: the test template proven on gen_test_boot_retire (red and green fire proofs; review fixes in Section 6)

Ordering statement (cross-model review of 746af6f, medium): the template and gen_test_boot_retire
were written first and then run on both programs as fire proofs; the local green_s1 run finished
27 s before red_s1 (Section 3 and Section 2 mtimes), so Sections 2-3 are NOT a failing-check-before-
implementation transcript. They prove that both fire-checks fail when their intent is violated and
pass when it holds. The fixes of Section 6 (schedule check, zero-check guard) were done in TDD order:
the red fixtures were run against the defective template first (recorded PASS = the defect), then
the template was fixed, then the same fixtures were re-run (FAIL as intended) with their green
counterparts.

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

Committed copies of every run cited in Sections 6, 7 and 8 (stdout.log and sim.log, byte-identical, md5 per file):
dv/auto_dv/evidence/gen_tdd_logs/test_writer/gen_manifest.md; the fixture sources live under
dv/auto_dv/tests/gen_fixtures/ (gen_run_fixture.sh reproduces any row against a gen_tb build).

## 1. Host self-test of the library (first)

```
$ python3 dv/auto_dv/tests/gen_test_lib.py --self-test
GEN_TEST_LIB self-test PASS (schedule k=4: imem_gnt_delay:same_cycle@c0,imem_rvalid_delay:short@c0,imem_outstanding_cap:cap2@c0,dmem_gnt_delay:random@c0,dmem_rvalid_delay:min1@c0,scr_key_delay:withheld_then_valid@c0,imem_rvalid_delay:min1@c1930,scr_key_delay:delayed@c20592,imem_rvalid_delay:long@c20592,dmem_gnt_delay:same_cycle@c20592,dmem_rvalid_delay:long@c21490,dmem_gnt_delay:random@c21490)
```

## 2. Red fire proof: the fire-check on the red fixture program (seed 1; run after the implementation, 27 s after green_s1)

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

Retention note (Critic batch-1 v6 I-1): the md5 cells of red_s1 (Section 2) and green_s1..s3 (this table) are those of the 04:29-04:30
UTC sim.log files of the first template build; the copies retained under gen_tdd_logs/test_writer/ (gen_manifest.md rows green_s1 /
green_s2 / green_s3 / red_s1) come from the later out_head build (the 08:40 UTC working-tree build named in the manifest header) and
carry their own md5, so these four tokens match no retained blob. The rows stay as the record of the runs made; the retained copies are the evidence.

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

## 3c. Program report channel (template feature added after the landing of 746af6f)

`GenTest.expected_reports`: a directed program stores K result words to the EOT MMIO register
before its tohost store; `wait_eot()` collects them edge by edge into `self.reports` and asserts
the store counter advanced by exactly one per awaited edge. Fixture (working files, not committed):
`dv/auto_dv/work/test-writer/fixtures/gen_report_channel.S` (three words: a sum 0x6bba, a shift
0x600d0, a marker 0xc0de0003, then tohost 1; the EOT address comes from a header rendered from
`gen_knobs.MEMORY_MAP["eot_addr"]`), program `work/test-writer/prog_report/` (Spike check: 3 stores
to 0x8ffff104, exit 0), test modules `fixtures/gen_ut_report_channel.py` (green) and
`gen_ut_report_channel_red.py` (report 1 expected wrong on purpose). Build `out_head/`, seed 1:

| Run | sim.log mtime (local) | md5 | lines | cocotb |
|---|---|---|---|---|
| out_head/report_s1 | 05:14:32.14 | ca4ef0511a039624f31ae6e58a3dc073 | `GEN_TEST_REPORT idx=0 value=0x00006bba cycle=55`, `idx=1 value=0x000600d0 cycle=62`, `idx=2 value=0xc0de0003 cycle=70`, `GEN_TEST_EOT code=0x00000001 stores=4 reports=3 retired=17 cycle=82`, `fire_report_0/1/2 ok=True`, `fire_report_count ok=True reports 3 (expected 3)`, `fire_retired_floor ok=True retired 17 (floor 12)`, `gen_ut_report_channel GEN_TEST_PASS` | PASS (870.01 ns), UVM_ERROR 0 |
| out_head/report_red_s1 | 05:15:08.81 | b65e0334293c07634512d3c40cfb7b26 | `GEN_TEST_FIRE fire_report_1 ok=False report 1 0x000600d0 (expected 0x000c01a0)`, `AssertionError: GEN_TEST_FAIL gen_ut_report_channel_red: 1 fire-check failure(s): fire_report_1: ...` | FAIL (870.01 ns) |

Read: the channel delivers every word in order with its cycle, and a wrong expectation fails
through the test's own assert. It carries what the program knows architecturally; RVFI-derived
facts still need TB Infra's RVFI export (plan Section 6 item 5).

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

## 6. Review fixes of 746af6f (cross-model REQUEST-CHANGES; response rows in gen_critic_response_test_template.md)

Build `out_head/` (HEAD 0475b94 working tree, no REGIME_SET consumer), riscv-dv seed-1 program
(`prog_s1`), fixtures under `dv/auto_dv/work/test-writer/fixtures/` (working files):
`gen_ut_sched_vacuous.py` (the schedule runner returns at once, so the c200 boundary passes
unapplied; `apply_phase` is stubbed to record without a bridge command because no consumer exists at
HEAD), `gen_ut_sched_sound.py` (same stub, normal runner), `gen_ut_zero_check.py` (`fire_check()`
records nothing). Schedule supplied as `+gen_regime_sched=imem_gnt_delay:long@c0,imem_gnt_delay:short@c200`.
TDD order: the fixtures ran against the defective template FIRST, then the template was fixed, then
the same fixtures and the template's tests were re-run.

| Step | Run | sim.log mtime (local) | md5 | Decisive lines | cocotb |
|---|---|---|---|---|---|
| pre-fix (defect shown) | prefix_sched_vacuous | 05:21:35.18 | 8f4f7bf198bcfd4982accbaaa0ebd767 | `GEN_TEST_FIRE fire_schedule_applied ok=True applied 1 of 2 scheduled entries (k=2, source=supplied)` although EOT was at cycle 1924 and c200 had passed | PASS (vacuous) |
| pre-fix (defect shown) | prefix_zero_check | 05:21:37.10 | c7b630c61b2099c5f10f8f7e5f7caab4 | no `GEN_TEST_FIRE` line at all; `gen_ut_zero_check GEN_TEST_PASS` | PASS (silent) |
| post-fix red | postfix_sched_vacuous | 05:23:06.83 | 6cf265c2cc3ce8bdf5d4eee9d16a5f7b | `fire_schedule_applied ok=False reached 2 of 2 scheduled entries by EOT (cycle 1924, retired 550), applied 1, missed ['imem_gnt_delay:short@c200']`; `AssertionError: GEN_TEST_FAIL gen_ut_sched_vacuous: 1 fire-check failure(s): ...` | FAIL |
| post-fix green | postfix_sched_sound | 05:23:10.29 | 4168f472a6da0863e0610d10d9d722e1 | `GEN_TEST_PHASE idx=1 trigger=c200 ... cycle=201 (stub, no bridge command)`; `fire_schedule_applied ok=True reached 2 of 2 ... applied 2`; `GEN_TEST_PASS` | PASS |
| post-fix red | postfix_zero_check | 05:23:13.66 | 90f37742d12c0315b97cbb139468d8dd | `AssertionError: GEN_TEST_FAIL gen_ut_zero_check: fire_check() recorded no check (a test must assert that its scenario fired)` | FAIL |
| regression | postfix_boot_green_s1 | 05:23:15.69 | 543ef81d3f16f105afea8e42c9a00e99 | `fire_eot_pass_code ok=True`, `fire_retired_floor ok=True retired 550 (floor 300 ...)`, `gen_test_boot_retire GEN_TEST_PASS` | PASS |
| regression | postfix_boot_red_s1 | 05:23:17.40 | 93f0b109146c389f1c62842b4bde3410 | `AssertionError: GEN_TEST_FAIL gen_test_boot_retire: 2 fire-check failure(s): fire_eot_pass_code ... \| fire_retired_floor ...` | FAIL |
| regression | postfix_report_s1 | 05:23:19.79 | 277468e63af9cbfae27b9e9b57524a21 | `GEN_TEST_EOT code=0x00000001 stores=4 reports=3`, `fire_report_0/1/2 ok=True`, `GEN_TEST_PASS` | PASS |

Manifest generator: `python3 dv/auto_dv/tests/gen_fcov_manifest.py --self-test` now prints the tree
it ran against (`inputs at git HEAD 0475b94; working-tree modified inputs: [gen_fcov_plan.md,
gen_test_plan.md, gen_trace_tp_bin.csv, gen_trace_check.py]`, PASS) and, pointed at the committed
versions of `gen_trace_check.py` and `gen_fcov_plan.md` (extracted with `git show HEAD:`), exits with
the named messages `GEN_FCOV_MANIFEST_INPUT_VERSION: ... defines 0 segmentable() functions ...` and
`... has no Section 1.1 ...` (fixtures/head_inputs, run 09:23 UTC). The DV Lead's plan-set landing SHA
is recorded in the response file when it lands.

## 7. Second-round fixes (cross-model AWC of 98c2ade and the Critic's v1 on 746af6f; response rows R2-* and M-*/L-*)

Where the quoted lines live (Critic L-4): every `GEN_TEST_*`, `AssertionError` and `TESTS=` line quoted
in this file is in the run's `stdout.log` (`sim_stdout.log` in Runtime's out-trees); `sim.log` holds the
UVM lines and the `Command:`/compiler stamp used for identity. The tables below identify each run by
its `stdout.log` mtime (local, UTC-4) and md5.

Build `out_head/` (HEAD 4c0ba11 working tree, no REGIME_SET consumer), riscv-dv seed-1 program
(`prog_s1`, end-of-test store at cycle 1924), fixtures under `dv/auto_dv/work/test-writer/fixtures/`.

EOT-cycle race probe (R2-4), `gen_ut_sched_sound` with `+gen_regime_sched=imem_gnt_delay:long@c0,imem_gnt_delay:short@c<N>`:

| Step | Run | stdout.log mtime | md5 | Decisive line | cocotb |
|---|---|---|---|---|---|
| pre-fix | prefix_race_c1923 | 05:45:09.46 | dd89066f42d2753b98041630e9bc1aac | `GEN_TEST_PHASE idx=1 trigger=c1923 ... cycle=1924`; `fire_schedule_applied ok=True reached 2 of 2 ... applied 2` | PASS |
| pre-fix (defect) | prefix_race_c1924 | 05:45:11.38 | a54bdd22674e1898f50f5f3085307e79 | `fire_schedule_applied ok=False reached 2 of 2 ... applied 1, missed ['imem_gnt_delay:short@c1924']` (the boundary and the end-of-test store fell in the same cycle; the runner lost the race) | FAIL (spurious) |
| pre-fix | prefix_race_c1925 | 05:45:13.45 | c3443e249d10af245d5c88dd50074e5d | `fire_schedule_applied ok=True reached 1 of 2 ... applied 1` (c1925 not reached) | PASS |
| post-fix | postfix2_race_c1924 | 05:47:54.58 | 307ee1152c449b825b4019ba3555c365 | `GEN_TEST_PHASE idx=1 trigger=c1924 ... cycle=1924`; `fire_schedule_applied ok=True reached 2 of 2 ... applied 2` | PASS |

New guards and paths (M-3, L-1) and the regressions after the second round:

| Step | Run | stdout.log mtime | md5 | Decisive line | cocotb |
|---|---|---|---|---|---|
| red (M-3) | postfix2_layers_required | 05:47:57.55 | 6ae6482152edb6eb91f43ed3c84384a7 | `AssertionError: GEN_TEST_FAIL gen_ut_layers_required: declared regime knobs imem_gnt_delay,imem_rvalid_delay,imem_err_rate,imem_intg_err_rate,imem_outstanding_cap have no REGIME_SET consumer in this build (layers_required); ...` at setup, before any fetch | FAIL |
| red (L-1) | postfix2_stim_raises | 05:48:00.50 | ac2b7282fd47a4c27f39d6432e0f3524 | `AssertionError: GEN_TEST_FAIL gen_ut_stim_raises: deliberate failure inside the forked stimulus()` (cocotb aborts the test on a failing background task) | FAIL |
| red (M-1) | postfix2_sched_vacuous | 05:48:04.31 | 488abce66a67b65ae059744b77b740ef | `fire_schedule_applied ok=False ... applied 1, missed ['imem_gnt_delay:short@c200']` | FAIL |
| green (M-1) | postfix2_sched_sound | 05:48:06.79 | 88d9cbbc99f15e96c2878375919c4a51 | `fire_schedule_applied ok=True reached 2 of 2 ... applied 2` | PASS |
| red (M-2) | postfix2_zero_check | 05:48:08.73 | 2d9870052aa3677db018c9a4ff0a9325 | `AssertionError: GEN_TEST_FAIL gen_ut_zero_check: fire_check() recorded no check ...` | FAIL |
| regression | postfix2_boot_green_s1 | 05:48:10.56 | a4e4fa6386701744352030b554403486 | `GEN_TEST_LAYERS not_applied reason=no REGIME_SET consumer for declared knobs imem_gnt_delay,... (layers_required=False, bring-up only)`; `fire_eot_pass_code ok=True`; `fire_retired_floor ok=True retired 550 (floor 300 ...)` | PASS |
| regression | postfix2_boot_red_s1 | 05:48:12.21 | 3f02fbb0cd061886a07537d2f654a387 | `AssertionError: GEN_TEST_FAIL gen_test_boot_retire: 2 fire-check failure(s): ...` | FAIL |
| regression | postfix2_report_s1 | 05:48:14.02 | ba4c1425a62e85c7bdb9ca8a7fcc3ea9 | `fire_report_count ok=True reports 3 (expected 3)` | PASS |

Host side: `gen_test_lib --self-test` PASS (`consumed knobs now: none; checked tests:
['gen_test_boot_retire.py']`; the consumed-knob parse proven on an SV fixture and on a file without
`apply_knob`; three red test sources refused by the structure check); `gen_fcov_manifest --self-test`
PASS on the DV Lead's working tree (`86 excluded coverpoints` at 09:47 UTC; 122 at 09:00 UTC: the
number follows the plan version). At the plan-set landing (HEAD bc9dba9, 09:52 UTC) the self-test
prints `inputs at git HEAD bc9dba9; working-tree modified inputs: none` and `PASS (67 bins for
gen_reg_schedule, 0 dropped; 86 excluded coverpoints)`: the generator runs from the committed tree
from that SHA on.

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

## 8. Retention landing and third fix set (cross-model AWC of 566a601; Critic v2 N-1/N-2/N-3 and v3 L-1..L-3)

Same build out_head, seed 1, run 11:19-11:22 UTC through dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh after the code
changes of this landing (structure-check rewrite, parser, layers_required rule, witness epilogue, drain log, skip-assert
message). Every line below is in the committed copy gen_tdd_logs/test_writer/gen_<run>_stdout.log.

| Run | Purpose | Decisive line (stdout.log line no.) | Result | md5 |
|---|---|---|---|---|
| ret_drain_probe | drain probe, first attempt: c0 phase shifted the program by the 40-cycle stub, so the c1924 apply ended exactly at the shifted EOT and the drain waited 0 cycles (coincidence, recorded) | 50: `19695.00ns INFO cocotb.gen_tb_top GEN_TEST_DRAIN waited cycles=0 for the runner's last boundary` | PASS, path not exercised | d32fdcc00872dfd4dc600fba8f8555af |
| ret2_drain_probe | drain probe (cross-model low, R2-4 fix b): single boundary at the EOT cycle 1924, 40-cycle stub apply; run() waited for the runner | 49: `19690.00ns INFO cocotb.gen_tb_top GEN_TEST_DRAIN waited cycles=40 for the runner's last boundary` | PASS, waited 40 cycles, applied 1 of 1 | 08123949ccf8585a76cd3bf42cfabe4d |
| ret_report_skip | red for the skip assert (Critic N-2 / v3 L-3), observer faulted once; message re-read the count | 54: `AssertionError: GEN_TEST: report channel skipped a store (0 -> 1); the program stores faster than one edge per store` | FAIL as designed | 4c155658b27c4d13c85e5a42ffa1a87a |
| ret2_report_skip | same red after the message reads the count once | 54: `AssertionError: GEN_TEST: report channel skipped a store (0 -> 2); the program stores faster than one edge per store` | FAIL as designed (0 -> 2) | b16a771fca22cd1fc8ae96ac60c542ce |
| ret2_report_s1 | report channel green after the message change | 68: `870.00ns INFO cocotb.gen_tb_top gen_ut_report_channel GEN_TEST_PASS` | PASS | e454769caaecd2261bc2edbabad397b5 |
| ret_boot_green_s1 | regression: gen_test_boot_retire seed 1 with the new check()/finish() | 62: `19290.00ns INFO cocotb.gen_tb_top gen_test_boot_retire GEN_TEST_PASS` | PASS | 3afe46bef59a8931e378e460d41c93b6 |
| ret_cmp_zcb_s1 | regression: gen_test_cmp_zcb seed 1 (declare_bins default, witness epilogue idle) | 183: `21240.00ns INFO cocotb.gen_tb_top gen_test_cmp_zcb GEN_TEST_PASS` | PASS | 906bbd6533e08ec96f57e772773672bf |
| ret_sched_vacuous | kept red: the vacuous runner still fails the schedule check | 60: `AssertionError: GEN_TEST_FAIL gen_ut_sched_vacuous: 1 fire-check failure(s): fire_schedule_applied: reached 2 of 2 scheduled entries by EOT (cycle 1924, retired 550), app` | FAIL as designed | d2a1186e94feea3cced64c7d6541795e |

Host side (11:19 UTC): `python3 dv/auto_dv/tests/gen_test_lib.py --self-test` PASS over the nine committed tests with the new
refused sources (alias base override, module-level `T.finish = _f`, `setattr`, class inside a function, direct COV_WITNESS,
`cycle_clause_true` outside a fire_* method, `layers_required = False` on a measured or unknown entry) and the parser fixture
with `function automatic void apply_knob` and commented-out tests; `check_manifest_matches` verified for every committed manifest.
No batch-1 item carries the cycle-clause marker, so no test issues a COV_WITNESS today; the epilogue's fail-loud paths (foreign id,
missing table or command) are asserted in code and documented in the API Section 9, not yet exercised in a run (needs TB Infra's
rendered WITNESS_IDS and the dispatcher row).

## 9. Landing 3: structure-check hardening, unforgeable witness record, epilogue reds (retention review of b0d6a3f, Critic v4)

Build: dv/auto_dv/work/test-writer/head_export/dv/auto_dv/work/test-writer/out_head3, compiled 12:24 UTC from a `git archive` export of HEAD
20a66cf (T-102 comparator fixes in, step 2b not yet), run with GEN_TB_PYROOT pointing at that export so the rendered knobs match the
simv while the tests come from the working tree (the clone's gen_knobs.py is mid-edit by TB Infra). Fixture manifests are derived
into the run directory (fixture_manifests/), never into the repository. Every line is in the committed copy gen_tdd_logs/test_writer/gen_<run>_stdout.log.

| Run (out_head3/<dir>) | Purpose | Decisive line (line no.) | Result | md5 (stdout.log) |
|---|---|---|---|---|
| l3c_witness_ok | green: TP-CMP-036 allowed, code 7 in the table, command present; fake dispatcher records the code | 190: `23470.00ns INFO cocotb.gen_tb_top GEN_TEST_WITNESS id=TP-CMP-036 code=7` | PASS, one COV_WITNESS 7 | cc3c7e6939828917333005a4a347b67d |
| l3c_witness_foreign | red: entry allows TP-CMP-034 only | 198: `assert not foreign, f"GEN_TEST_FAIL {self.name}: witness for {foreign} outside the entry's witness_ids {list(allowed)}"` | FAIL as designed | 199dc0e2c8b5a748a86203701508f7d9 |
| l3c_witness_notable | red: no WITNESS_IDS table, no COV_WITNESS command | 200: `AssertionError: GEN_TEST_FAIL gen_ut_witness_notable: witness protocol not rendered (CMD COV_WITNESS / WITNESS_IDS) while ['TP-CMP-036'] are due` | FAIL as designed | c23d746fdba65f8ddb0ef1da10eee50b |
| l3c_witness_noid | red: table lacks the id (GEN_TEST_FAIL prefix, no bare KeyError) | 198: `assert code is not None, f"GEN_TEST_FAIL {self.name}: the rendered WITNESS_IDS table lacks {tp}"` | FAIL as designed | 2aeda7bb94a00952fa6b18b8cd8614f6 |
| l3c_manifest_stale | red: stale manifest derived at import from the current file minus one bin | 199: `AssertionError: GEN_TEST_LIB: manifest of gen_ut_manifest_stale differs from declare_bins(): 109 in the manifest, 110 declared; not in the manifest ['gen_mul_op` | FAIL as designed | b2898ec962d67be175862ef191dc889b |
| l3c_manifest_missing | red: declared bins, no manifest | 197: `assert not declared, (f"GEN_TEST_LIB: {test_name} declares {len(declared)} bins but has no manifest "` | FAIL as designed | 7756dddfc5df36b4227034f2abb3b4c9 |
| l3c_drain_probe | drain probe anchored to the end-of-test edge: runner mid-apply at EOT on any build | 51: `20570.00ns INFO cocotb.gen_tb_top GEN_TEST_DRAIN waited cycles=40 for the runner's last boundary` | PASS, waited 40 cycles | 584341fc8ac72d22646ef965574834d1 |
| l3b_sched_vacuous | kept red: the vacuous runner (consumed set pinned in the fixture) | 62: `AssertionError: GEN_TEST_FAIL gen_ut_sched_vacuous: 1 fire-check failure(s): fire_schedule_applied: reached 2 of 2 scheduled entries by EOT (cycle 2012, retired` | FAIL as designed | 30b3ae76ff23f88c1a2ef4c4278fec58 |
| l3b_sched_sound | green counterpart | 64: `20170.00ns INFO cocotb.gen_tb_top gen_ut_sched_sound GEN_TEST_PASS` | PASS | 33db71ce7fcf12cf410c7718ed64b051 |
| l3_report_skip | kept red: skip assert | 56: `AssertionError: GEN_TEST: report channel skipped a store (0 -> 2); the program stores faster than one edge per store` | FAIL as designed | a2e622698995e5e6f785dda93fb0ce2b |
| l3_boot_green_s1 | regression: gen_test_boot_retire seed 1 on the HEAD build | 64: `20170.00ns INFO cocotb.gen_tb_top gen_test_boot_retire GEN_TEST_PASS` | PASS | 63ba67200fcb27097e0d00b950dbb2af |

Host side: `gen_test_lib.py --self-test` PASS with the third set of refused sources (import alias of GenTest, base expression,
imported base, mixin overriding finish, `self.results.append`, `self._results = []`, `self.witness_ids = ...`, `lib.WITNESS_IDS = {}`,
`setattr(self, ...)`, non-literal layers_required) and the accepted ones (AnnAssign layers_required with a measured: false entry; a
module-local mixin adding a fire_tp method); the witness CSV agrees with the marker token row by row; the fixture header equals the
rendered map; every program generator runs as a flow-style script with no PYTHONPATH. Not exercised in a run: the aliased-base
and patch refusals are lint (the self-test refuses the module); a runtime sandbox is not claimed (API Section 7).

### 9.1 Layers live on the step-2b build

Build of HEAD with TB Infra's step 2b (REGIME_SET_CONSUMED rendered, id-based dispatcher): head_export2/.../out_head4, rendered knobs
from the same export. With a real consumer the template draws layer 2 and derives the layer-3 schedule and the dispatcher applies
every REGIME_SET (no GEN_CMD_DISPATCH error), so `layers_required = False` no longer changes behaviour; the flag is dropped and the
entries flip to their plan tiers when the Orchestrator lifts the gate.

| Run (out_head4/<dir>) | Phases applied | fire_schedule_applied | Result | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|---|
| l4_boot_green_s1 | 6 | ok=True 6/6 | PASS | 0 | c7e799286c61eb6ffa94b4dbe9bcd9d5 |
| l4_rst_boot_s1 | 4 | ok=True 4/4 | PASS | 0 | 5afdbc501a492a689bf481e7f59b9e73 |
| l4_cmp_zcb_s1 | 3 | ok=True 3/3 | PASS | 0 | 10d4205321b3ddc5602fadce122937c0 |

### 9.2 Progress-based end-of-test wait (LOG-030; landing 3c)

Acceptance under live layers (wave 5 of batch 1) found the template's fixed per-store budget wrong for slow bus regimes: a program
whose prologue is long reaches its first report store several hundred thousand cycles late while the core keeps retiring. The wait
now fails only when retirement stops for one budget (the hang detector) or when a store lags PROGRESS_ROUNDS_MAX budgets while
the core retires (runaway); every lagging budget logs GEN_TEST_SLOW and finish() reports GEN_TEST_SLOW_TOTAL. Runs on the step-2b
build out_head4 (layers live) and, for the flow's failing seed, also on the current-HEAD build out_head5:

| Run | Purpose | Decisive line (line no.) | Result | UVM_ERROR | md5 (stdout.log) |
|---|---|---|---|---|---|
| l5_eot_stall | red: frozen retirement, a store that never comes (fail within one budget) | 70: `assert now_retired > last_retired, (f"GEN_TEST: end-of-test store {seen_before + 1} of {final} not seen and no retirement "` | FAIL as designed | - | 956b1ed588b0ca4208a3f4fa11327399 |
| l5_eot_runaway | red: the program self-loops after tohost and keeps retiring, a store never comes (fail after the cap) | 72: `AssertionError: GEN_TEST: end-of-test store 5 of 5 not seen within 3 x 5000 cycles (cycle 15084, retired 2150) although the core keeps retiring (runaway program)` | FAIL as designed | - | c152f8ca554c7a81ed5303fa1b1ba0a5 |
| l5_report_s1 | green: report channel unchanged | 77: `890.00ns INFO cocotb.gen_tb_top gen_ut_report_channel GEN_TEST_PASS` | PASS | 0 | ee9eb5a44eb7ee7e18869dd4796e358f |
| l5_boot_green_s1 | green: boot_retire with layers applied | 83: `42680.00ns INFO cocotb.gen_tb_top gen_test_boot_retire GEN_TEST_PASS` | PASS | 0 | ccf93bbde2d4beb9d996f066c1000504 |
| l5_combo_zcmp | cmp_zcmp_basic seed 1 under the wave-5 red's regime combination (first store at cycle 326778) | 4224: `7552340.00ns INFO cocotb.gen_tb_top gen_test_cmp_zcmp_basic GEN_TEST_PASS` | PASS | 0 | 702f627f8d5a4e6551d0ea0a2f92bcf4 |
| l5_flowred_zcmp | the wave-5 red program (seed 1, --red-item TP-CMP-039) with its schedule: EOT at cycle 756518, then the designed fire-check failure | 4218: `AssertionError: GEN_TEST_FAIL gen_test_cmp_zcmp_basic: 3 fire-check failure(s): fire_tp_cmp_039: 147 scenarios, 2394 report words checked, 1 mismatches; cm.push over 48/4` | FAIL on fire_tp_cmp_039 (RED-OK shape) | - | 7bd45da093a5ae32a5db4d10273880ce |
| l5_flowseed_zcmp | the wave-5 failing green seed 421987159 with its derived schedule: four GEN_TEST_SLOW budgets, first store at cycle 430153, EOT at 968492 | 4245: `9684970.00ns INFO cocotb.gen_tb_top gen_test_cmp_zcmp_basic GEN_TEST_PASS` | PASS | 0 | 5ca82f317356721c9d8e5a4db1a77fed |
| l6_flowseed_zcmp | the same seed on the current-HEAD build | 4245: `9684970.00ns INFO cocotb.gen_tb_top gen_test_cmp_zcmp_basic GEN_TEST_PASS` | PASS | 0 | 4d54efe30299110ed5fa50ff4ae27312 |

The two failing wave-5 runs and the local reproductions share the program source hash, the plusargs, the seed-derived schedule
and the testbench revision; the first report store of that seed's program arrives at cycle 430153 under its drawn regimes, past the
old fixed 300000-cycle budget, and the run then completes normally. The stall red and the runaway red name the cycle and retirement
counts in their failure lines.

### 9.3 Correction: the self-test's red-source loops were vacuous until landing 3d

From the fix set of 98c2ade to landing 3c the loops that were meant to prove the structure check refuses forged test sources
raised the "accepted" error inside the try block, where the following except clause caught it and matched it by the same
`why` word; they could not fail. Landing 3d records acceptance outside the except clause and asserts it afterwards. With the
loops working, one red source was accepted at the parent commit: a module-level helper that receives the test object and writes
a template-owned name through a local alias (`def _h(t): u = t; u.failures = []`, called as `_h(self)`); the call-site fixpoint
rule added in landing 3d refuses it (with that rule disabled the self-test is red), so one rule was missing and was added. Every
other listed source was refused as claimed; the claims made between those commits were not proven when they were made.

### 9.4 Landing 3e: the refused-form list is one table, proven and documented from it

`lib.REFUSED_FORMS` names the fifteen statement shapes `check_test_source` refuses. Every red source of the self-test carries
its form label; the self-test asserts that the labels proven refused equal the table and that the API doc's bullet list
(gen_test_template_api.md, after the sentence "refuses exactly these statement shapes") equals the table verbatim, so the
documentation and the proof cannot drift. Probed on this tree and listed in the API doc as passing: `for self.failures in
([],)`, `with open(p) as self.failures`, `*self.failures, = []`, attribute-chain writes through template-owned objects, template
patching through an import alias or the full dotted path. The list is frozen (LOG-024d): the `del` refusal that landed in 3d
stays, nothing is added.

Also in 3e: the harness failure line comes from `lib.fire_fail_line` (the template raises it), and the self-test synthesizes it
per recorded check name (source literals plus the GEN_TEST_FIRE names of the retained pinned-red log) to check every red entry's
red_expect the way the flow's regex meets it, then applies Runtime's `red_signature_check` to the retained log (present, harness
line matched; stale evidence reported until T-153); `FLOW_RUN_ENV` reads the flow's `gen_flow_const.JOB_ENV_SET` (one home); the
self-test names the relation between the longest CG-REG-007 duration class and the schedule runner's per-trigger wait budget
(equal today, `lib.DURATION_CLASSES`). Self-test PASS on this tree in both forms and from a clean archive of 7f78c41 (batch-1
transcript Section 10).

## 10. T-226 (LOG-057): the witness epilogue carries the issuing test's group

Why: the Critic's landing-2b verdict (M-1) found the committed epilogue sending COV_WITNESS with arg1 = 0 while the TB as built
(docs/gen_component_api_fcov.md Section 7, gen_env_pkg.sv's dispatcher row, gen_fcov_pkg.sv) expects arg1 = the issuing test's group
index and refuses another group's item with GEN_WITNESS_FOREIGN, so every group but the one at index 0 would have been refused on its
first real witness; the retained greens never exercised the path (no committed entry lists witness_ids), and the fixture base's
docstring still said "no SV side exists".

Change: the epilogue resolves the test's own plan group (lib.test_group, the manifest generator's derivation), requires the rendered
owner of every due item (lib.WITNESS_GROUP_OF) to be that group (a new GEN_TEST_FAIL before the dispatcher's refusal), and issues the
witness through GenBridge.cov_witness(tp, own group), which sends COV_WITNESS <item index> <group index> from the gen_knobs tables and
returns the covergroup's distinct-bin count; logged as GEN_TEST_WITNESS id= code= group= group_idx= bins=. gen_test_lib exposes
WITNESS_GROUP_OF / WITNESS_GROUPS beside WITNESS_IDS. The fixture base replaces the bridge's cov_witness by a recorder (the fixtures'
fake codes must never reach the SV table now that the dispatcher routes the command), patches the owner and group tables and the
test's group, and its docstring says so; a fifth fixture, gen_ut_witness_othergroup, is the red of the new owner check. The API
document's Section 9 paragraph describes the as-built form. No committed entry lists witness_ids until Runtime's witness_render
accepts them (its part of T-226); the one real witness green follows then.

Runs on out_head14 (export of 2ea81ac; sources sha 893384b8eec4e6d5; template sha d47cc7e90130fe5c, test_sha of the fixture module in each header,
e.g. 86927ab264008433 for gen_ut_witness_ok), the gen_cmp_zcb seed-1 image built from the export, the export's fixture from the export root:

| Run | Designed outcome | Decisive line | Result | md5 of the retained copy |
|---|---|---|---|---|
| t226_witness_ok | green: TP-CMP-036 allowed, code 7, owned by gen_cmp_zcb | `GEN_TEST_WITNESS id=TP-CMP-036 code=7 group=gen_cmp_zcb group_idx=0 bins=0` then GEN_TEST_PASS; the recorder saw [(TP-CMP-036, gen_cmp_zcb)] | PASS | fd498820e72ca6b290444e47ce2ff61a (stdout, in full; sim.log 909966980e2171ed28820d6a2491de0d) |
| t226_witness_foreign | red: the entry allows TP-CMP-034 only | `AssertionError: GEN_TEST_FAIL gen_ut_witness_foreign: witness for ['TP-CMP-036'] outside the entry's witness_ids ['TP-CMP-034']` | FAIL as designed, nothing issued | cfbdac4db60f1b6c4bd773d5c3b8cada |
| t226_witness_noid | red: the table lacks the id | `AssertionError: GEN_TEST_FAIL gen_ut_witness_noid: the rendered WITNESS_IDS table lacks TP-CMP-036` | FAIL as designed | 5bd474e8968dcc3d04eb1ae80e7da18d |
| t226_witness_notable | red: no table, no command | `AssertionError: GEN_TEST_FAIL gen_ut_witness_notable: witness protocol not rendered (CMD COV_WITNESS / WITNESS_IDS) while ['TP-CMP-036'] are due` | FAIL as designed | 554b3d1228bbcfffc3353ae034cf5913 |
| t226_witness_othergroup | red (new): the rendered owner of TP-CMP-036 is gen_cmp_zcmp_events | `AssertionError: GEN_TEST_FAIL gen_ut_witness_othergroup: witness for TP-CMP-036 owned by gen_cmp_zcmp_events, issued by gen_cmp_zcb: a test witnesses only its own group's items` | FAIL as designed, nothing issued | c0155e3473b39c3d753c9f29ffe37847 |
| t226_witness_othergroup_unguarded | TDD red of the check: the same fixture on the export's template with the owner assertion removed (gen_t226_unguarded_template.diff) | the template printed GEN_TEST_PASS after witnessing the foreign-owned item; the fixture's own guard then failed the run (TESTS=1 PASS=0 FAIL=1) | epilogue passed, run FAILed on the fixture guard: the check is the difference | c1797b9b984fa8cf506ed25deafc5b0e |

These fixtures prove the Python side only: the recorder returns 0, so `bins=0` in the green's GEN_TEST_WITNESS line is the recorder's value,
and its sim.log shows the witness ledger untouched (GEN_WIT witnesses=0, as expected); the SV round trip of a real witness rests on
tb-infra's gen_ut_witness entries until the first real witness green. The library self-test PASSes with the new attributes (the F_PATCH
red still refuses a test module assigning lib.WITNESS_IDS; the fixtures are not test modules). Verified from a detached archive of HEAD with the touch overlaid (dv/auto_dv/work/test-writer/head_final_selftest_t226.log names the HEAD it archived).

## 11. The LOG-050 regime-handler rule (Critic batch-1 v8 L-1): a structural check in the library self-test and a run-time guard

Why: the round-0 runaway (T-206) was a debug request storm drawn for a program without a debug ROM; LOG-050 rules that a test whose program
has no debug ROM does not schedule knob_debug_req_regime and one without an interrupt handler does not schedule an irq-consumer knob unless
MIE stays 0, enforced structurally in the library self-test, not as a 16th lint form (LOG-024d keeps REFUSED_FORMS at 15).

Red first: gen_t2guard_structural_red_before.log records the library before the check (HEAD f2b9272 plus T-226) accepting the fixture
gen_t2guard_red_fixture_dbg_nohandler.py.txt (a test scheduling knob_debug_req_regime with no handler) through check_test_source, and the
absence of check_regime_handlers.

Change: GenTest gains `program_handlers = ()` ("dbg": a debug ROM in the DM window; "irq": a returning interrupt handler) and
`mie_stays_zero = False`; gen_test_lib.regime_handler_violations applies the rule from gen_knobs.KNOB_CONSUMER (the yaml's
regime_set_consumer), check_regime_handlers reads a module's classes by AST (schedulable as a literal tuple, module-level constants,
lib.TIMING_ONLY_KNOBS or GenTest.schedulable; the two declarations as literals; anything else refused as unreadable) and the self-test runs it on
every committed test module plus seven red and five green sources (the template default of every regime knob counts as red without both
handlers); setup() applies the same rule at run time before the first fetch. gen_test_rst_boot and gen_test_csr_reset declare
mie_stays_zero = True (their docstrings already said MIE stays 0); gen_test_bit_draft's knob tuple became a literal so the rule can read it.
API document Section 9 and the class-attribute table describe it.

Runs on out_head14 (export of 2ea81ac, sources sha 893384b8eec4e6d5):
| Run | Designed outcome | Decisive line | Result | md5 of the retained copy |
|---|---|---|---|---|
| t2guard_regime_handler_red | red: a fixture (gen_ut_regime_handler_red, gen_test_cmp_zcb's test scheduling knob_debug_req_regime, no handler) fails in setup() before GEN_TEST_RELEASE | `AssertionError: GEN_TEST_FAIL gen_ut_regime_handler_red: schedules a regime knob its program cannot survive: knob_debug_req_regime (consumer dbg) needs a dbg handler the program does not declare` | FAIL as designed, no release, no fetch | 03208734a505949a2bff51576ff12d50 |
| t2guard_csr_reset_1028791296 | green: the declared test (mie_stays_zero = True, irq_line_mix schedulable) on the guarded template | GEN_TEST_PASS, 88 reports, retired 243, EOT cycle 4203, GEN_TEST_BINS n=68, UVM_ERROR 0 | PASS | 47df188c5bdfb69c0df2fafd40496405 (stdout in full; sim.log a014f59a2644fdb7488a8f919f3d5a21) |

After the change the same structural fixture is refused: "class T schedules a regime knob its program cannot survive: knob_debug_req_regime
(consumer dbg) needs a dbg handler the program does not declare" (the self-test's first red source is that fixture's body). Verified from a
detached archive of HEAD with the touch overlaid (dv/auto_dv/work/test-writer/head_final_selftest_guard.log names the HEAD).

## 12. The CM77 touch: the lint reaches attribute chains rooted at self; Section 10 and API-doc wording; a self-found doc regression

Red first: gen_t2cm77_lint_red_before.log (the lint of 04cf523 accepting a test class whose stimulus() assigns self.bridge.cov_witness = fake,
and self.bridge.cmd = fake). Change: in check_test_source's class-method walk an assignment whose target is a pure attribute chain rooted at
self with a template-owned first attribute is refused as F_OVERRIDE reaching further (the fifteen refused forms stay fifteen; the F_OVERRIDE
sentence in lib and the API doc bullet name the new reach); a subscript anywhere in the target stays the item-assignment rule's case, which
the existing red sources still exercise. Two red sources join the self-test's F_OVERRIDE list (self.bridge.cov_witness = _f in stimulus(),
self.bridge.h.b = _f); the fixture base is not a test module, so its recorder stays legal. After the change the same source is refused:
"class T rebinds self.bridge.cov_witness at line 7; a template method reached through a template-owned attribute is read-only for a test".
Also in this touch: Section 10's control row and bins=0 sentence (CM77-m-2 / m-3), the fixture base docstring (CM77-i-1), the API document's
two witness paragraphs (CM77-i-2 / i-3), and the id-free wording of the library's comments (the frozen-list and regime-handler comments state
the rule, not the log entry). Self-found while applying CM77-i-2: the LOG-050 touch's API document came from the head_export14 staging root
(an archive of 2ea81ac, before T-226) and so 674d026 dropped T-226's rewritten Section 9 witness paragraph; restored here (row SF-TT-1).
Rule for the staging root: re-archive HEAD after every commit before copying a staged file over the tree.

## 13. The CM80 touch: the regime-handler rule by knob, the NMI hole closed, the run-time check over pins and the supplied schedule

Red first: gen_t2cm80_structural_red_before.log records the library of c030317 accepting the reviewer's probes (knob_irq_regime with
knob_irq_line_mix under mie_stays_zero; knob_dmem_intg_err_rate and knob_imem_err_rate with no handler; a decorated test class) and refusing
an annotated `schedulable: tuple = ...` only by accident (the attribute skipped, the template default refused instead).

Change (gen_test_lib.py, gen_test_template.py, gen_test_template_api.md): the rule maps knobs to handlers by name (lib.KNOB_HANDLER: dbg for
the debug regime; irq for the three irq knobs and knob_dmem_intg_err_rate, whose load integrity error is an internal NMI; exc for the two
err_rate knobs and knob_imem_intg_err_rate, injected access faults), names each knob's inactive value (quiet, none), and is values-aware:
lib.regime_handler_violations(knobs, handlers, mie_stays_zero, values) needs nothing for a knob whose only value is inactive, and exempts the
irq knobs under mie_stays_zero only while no NMI can be driven (knob_irq_regime and knob_irq_line_mix not both in play with active values;
with_nmi drives irq_nm, which MIE does not mask). The structural reader refuses annotated, tuple or chained assignments of the three names
and decorated test classes; absent attributes take the GenTest defaults (noted). setup() runs the values-aware form over the class's
schedulable, every pinned regime knob and every knob of the schedule (derived or supplied through +gen_regime_sched) before any REGIME_SET
and before the first fetch. Self-test: thirteen red sources, seven green ones, and the values-aware unit cases (quiet + with_nmi accepted,
storm + with_nmi refused, storm + single accepted, storm + with_nmi with the irq handler accepted).

Runs on out_head14 (export of 2ea81ac), gen_test_csr_reset seed 1028791296 (mie_stays_zero = True, knob_irq_line_mix schedulable, no handler):

| Run | Plusargs | Designed outcome | Decisive line | md5 of the excerpt |
|---|---|---|---|---|
| t2cm80_csr_reset_sched_dbg_storm | +gen_regime_sched=debug_req_regime:storm@c0 | refused before the first fetch (no GEN_TEST_RELEASE) | `AssertionError: GEN_TEST_FAIL gen_test_csr_reset: the run's regimes are ones its program cannot survive: knob_debug_req_regime needs a dbg handler the program does not declare` | 6ca8e40c9340854616d8bb23db09ed34 |
| t2cm80_csr_reset_pin_storm_nmi | +gen_knob_irq_regime=storm +gen_knob_irq_line_mix=with_nmi | refused before the first fetch | `AssertionError: GEN_TEST_FAIL gen_test_csr_reset: the run's regimes are ones its program cannot survive: knob_irq_regime with knob_irq_line_mix: mie_stays_zero exempts the irq knobs only while no NMI can be driven, but events flow and with_` | 32e12bce22388692257fdd7f1cf576e4 |
| t2cm80_csr_reset_pin_storm_single | +gen_knob_irq_regime=storm +gen_knob_irq_line_mix=single | allowed (no NMI line), PASS | GEN_TEST_PASS | c69c88bb321d693c6aacc6accb543a71 |
| t2cm80_csr_reset_pin_quiet_nmi | +gen_knob_irq_regime=quiet +gen_knob_irq_line_mix=with_nmi | allowed (no events), PASS | GEN_TEST_PASS | 22b61c70561df1c28ebadead20fded01 |
| t2cm80_csr_reset_green | none | PASS | GEN_TEST_PASS | 7a2687c8aef9d010363de9ef269cfb6a |

The first version of the run-time check read pins from self.pinned, which lists only the schedulable knobs, so the storm + with_nmi pins
passed it (a run of this probe set before the fix); the check now reads pins of every regime knob. Verified from a detached archive of HEAD
with the touch overlaid (dv/auto_dv/work/test-writer/head_final_selftest_cm80.log names the HEAD).

## 14. The CM85 touch: the helper branch of the lint reaches attribute chains; the API document's residual list corrected

Red first: gen_t2cm85_helper_chain_red_before.log records the lint of 99cba0e accepting a module-level helper `def _h(t): t.bridge.cov_witness = _f`
called with self from stimulus() while refusing the direct `t.bridge = None` in the same helper. Change: the helper branch of check_test_source
walks pure attribute chains rooted at a test-bound parameter and refuses one whose first attribute is template-owned, the same reach the
class-body rule gained in the CM77 touch; the F_HELPER sentence (lib and the API doc bullet, which the self-test compares verbatim) names it,
and a red source joins the F_HELPER list. The refusal messages of both branches say "an attribute reached through a template-owned name is
read-only for a test" (they fire for non-methods too), and the F_OVERRIDE sentence separates the method overrides from the attribute rebinding.
The API document's "Shapes known to pass today" paragraph no longer lists the four attribute-chain writes the lint refuses, names the five
witness fixtures, and states the frozen-list rule instead of a log id. After the change the same helper source is refused: "helper _h rebinds
t.bridge.cov_witness at line 5; an attribute reached through a template-owned name is read-only for a test". Verified from a detached archive
of HEAD with the touch overlaid (dv/auto_dv/work/test-writer/head_final_selftest_cm85.log names the HEAD); the shared tree's self-test is red
at this time on gen_test_csr_access's manifest, stale against the DV Lead's in-progress plan edits, not on this touch.
