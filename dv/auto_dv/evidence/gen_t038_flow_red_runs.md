# T-038 evidence: real red runs through the flow (Critic P-01) and the verdict rules (P-02, P-09)

Owner: runtime. Date: 2026-09-03 (06:14 to 06:17 UTC). Build configuration: `opentitan`. Build under
test: the coverage build of `regress_t027_smoke_recheck` (`<out root>/regress_t027_smoke_recheck/
build/gen_smoke`, unchanged simv). Every run below went through `gen_run.py --lsf` on the `regress`
queue; out-tree `<out root>/t038_red/<name>/` (out root `/proj_soc/user_dev/fzhang/ibex_dv_out`).
The four verdict paths reachable today were each produced by a REAL failing (or passing) simulation,
not by fabricated text; the log excerpts below are pinned verbatim as `gen_verdict.py --self-test`
cases (`REAL_FATAL`, `REAL_GREEN`, `REAL_COCOTB`), so the scanner is tied to the true formats.

## 1. Commands

```
B=<out root>/regress_t027_smoke_recheck/build/gen_smoke ; O=<out root>/t038_red
gen_run.py --build-dir $B --test gen_smoke --seed 7 --run-dir $O/fatal    --no-coverage --measured no --lsf --plusarg +gen_smoke_cycles=1
gen_run.py --build-dir $B --test gen_smoke --seed 7 --run-dir $O/timeout1 --no-coverage --measured no --lsf --timeout-s 1
gen_run.py --build-dir $B --test gen_smoke --seed 7 --run-dir $O/timeout5 --no-coverage --measured no --lsf --timeout-s 5
gen_run.py --build-dir $B --test gen_smoke --seed 7 --run-dir $O/nomarker --no-coverage --measured no --lsf --pass-marker GEN_NEVER_PRINTED
gen_run.py --build-dir $B --test gen_smoke --seed 7 --run-dir $O/green    --no-coverage --measured no --lsf
```

`--plusarg` replaces a same-name testlist plusarg (VCS `$value$plusargs` takes the first occurrence;
the first attempt appended `+gen_smoke_cycles=1` after the testlist's `=3000` and the smoke ran 3000
cycles). `--pass-marker` overrides the testlist marker for red-run evidence only.

## 2. Results (result.yaml of each run)

| Run | LSF job / host | Verdict | reason | exit code | $finish | marker | banner |
|---|---|---|---|---|---|---|---|
| fatal (`+gen_smoke_cycles=1`, retires nothing) | 10930762 / soc-c-10 | FAIL | `sv_fatal at log line 20` | 0 | yes | no | yes |
| timeout1 (`--timeout-s 1`) | 10930764 / soc-c-05 | TIMEOUT | `per-run timeout expired; simulator killed before sim.log existed` | 124 | no | no | no |
| timeout5 (`--timeout-s 5`, control: the smoke finishes in time) | 10930761 / soc-c-20 | PASS | end marker and config banner present | 0 | yes | yes | yes |
| nomarker (`--pass-marker GEN_NEVER_PRINTED`) | 10930763 / soc-c-03 | FAIL | `end-of-test marker 'GEN_NEVER_PRINTED' not found` | 0 | yes | no | yes |
| green (control) | 10930765 / soc-c-20 | PASS | `no collected failure mechanism; end marker and config banner present` | 0 | yes | yes | yes |

Real log text (verbatim, `t038_red/fatal/sim.log` lines 18-23):

```
GEN_SMOKE: max_cycles=1 boot_addr=0x80000000
GEN_SMOKE: retired=0 alerts=0 core_busy=On irq_pending=0 data_tag_o=0
Fatal: "/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_smoke_tb_top.sv", 386: gen_smoke_tb_top: at time 55000 ps
GEN_SMOKE_FAIL: no RVFI retirement observed
$finish called from file "/localdev/fzhang/ws/ibex-challenge/dv/auto_dv/tb/gen_smoke_tb_top.sv", line 386.
$finish at simulation time                 5500
```

The `$fatal` run exits 0 and prints `$finish`: exactly the case SIM_RECIPE Section 5 warns about
(VCS can exit 0 after a fatal); the verdict comes from the `Fatal:` line (pattern `sv_fatal`), which
the scanner reports with `evidence` set to that line. The timeout run (`timeout -k 20 1` inside the
job) killed the simv during start-up: `exit_code` 124, `lsf.out` has `GEN_RUN_EXIT rc=124`, no
`sim.log` exists, and the verdict is TIMEOUT (before this task a missing sim.log was reported as
FAIL "sim.log missing" even when the timeout had fired). The missing-marker run shows the
marker rule alone deciding: a clean, finished simulation with the wrong marker is FAIL.

## 3. Verdict rules after P-02 and P-09 (gen_verdict.py, pinned by the self-test)

- The marker must be the last whole token of a line (`GEN_SMOKE_PASS` printed alone by SV, or at
  the end of a cocotb log line); a message that quotes the marker does not count.
- PASS requires: no collected failure mechanism; the marker (or `$finish` when the test has no
  marker); the time-zero banner line `GEN_CONFIG_BANNER build_config=opentitan`; and (`$finish`
  seen OR exit code 0); and an exit code in {0, 124}; and no crash signature (`Segmentation
  fault|Killed|core dumped|Aborted|Bus error|Illegal instruction`) in `lsf.err`, `run.log` or
  `sim_stdout.log`. Any other combination is FAIL with a reason that names the rule
  (`unexplained exit code <rc>`, `crash signature in stderr: ...`, `config banner ... not found`).
- The full banner block is copied into `result.yaml` (`banner`), the per-run proof of the
  elaborated configuration.
- `python3 gen_verdict.py --self-test`: 20 cases, 5 of them the real excerpts above plus the real
  cocotb lines of job 10930476; the former case "marker but no finish = PASS" is now two cases:
  PASS with exit code 0, FAIL with an unknown exit code.

## 4. Not yet reachable (stated, not hidden)

UVM_ERROR / UVM_FATAL red runs and an RTL assertion failure need a UVM test class and a DUT
assertion trigger; the smoke top has neither. Under `+define+UVM` an RTL assertion failure becomes a
`uvm_report_error` (prim_assert), so the `UVM_ERROR` count and message-line patterns are the ones to
prove first when the real TB lands; the self-test carries the expected formats (`UVM_ERROR :    2`,
`UVM_ERROR @ 100: ...`) as fabricated placeholders until then, marked as such by their names.

## 5. LSF accounting

Jobs 10930761 to 10930765 (this file) plus 10930755 (first attempt, discarded: the operator plusarg
did not override; the verdict module was missing an import and the run crashed before writing a
result; both fixed before the runs above). `bjobs -w` after the runs: no unfinished job.
