# Test template API: gen_test_template.py and gen_test_lib.py

Owner: test-writer. Version 1, 2026-09-03. Files: `dv/auto_dv/tests/gen_test_template.py` (class
`GenTest`), `dv/auto_dv/tests/gen_test_lib.py` (layers, schedule, helpers, host self-test),
`dv/auto_dv/tests/gen_programs/*.S` (directed programs of the tests). Built from the TB as built:
`dv/auto_dv/gen_tb/gen_bridge.py`, `gen_handles.py`, `gen_image.py`, the rendered `gen_knobs.py`, the
bridge fields of `dv/auto_dv/tb/gen_bridge_if.sv` and the step-2b command dispatcher
(`dv/auto_dv/env/gen_env_pkg.sv`). Proof: `dv/auto_dv/evidence/gen_tdd_test_template.md`
(gen_test_boot_retire red then green). Governing rules: DV_prompt Sections 5, 6, 8; TB_CONTRACT
Sections 2 to 4; architecture C2, C9, 8.3a; gen_runtime_api.md Sections 4, 7c, 7e.

## 1. What a test is

One Python module `dv/auto_dv/tests/gen_test_<area>_<topic>.py` = one test-plan group. It defines a
`GenTest` subclass and one `@cocotb.test()` of the same name that awaits `run()`. The module
touches no DUT signal and spells no hierarchical path (`gen_handles.py` is the only one); it drives
the DUT through the program image and the bridge commands, and observes it through the bridge's
event bits and counts. Stimulus is Python or a program (C/assembly); no SV recompile per test.

```python
import cocotb
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest

class MyTest(GenTest):
    name = "gen_test_<area>_<topic>"      # == testlist entry == fcov manifest stem
    schedulable = GenTest.schedulable      # regime knobs layers 2/3 may vary (a subset per test)
    async def stimulus(self): ...          # bridge commands, waits (runs while the program runs)
    def fire_check(self): ...              # self.check("fire_tp_<area>_<nnn>", ok, "detail") per item
    plan_group = None                      # test-plan group; None: gen_<x> for gen_test_<x>
    def declare_bins(self): ...            # override only to declare a subset; default lib.plan_bins(name, plan_group)

@cocotb.test()
async def gen_test_<area>_<topic>(dut):
    await MyTest(dut).run()
```

Testlist entry: `cocotb_module: dv.auto_dv.tests.gen_test_<area>_<topic>`, `uvm_test: gen_base_test`,
`plusargs: [+gen_fetch_en_at_reset=0]` (required by the template), `pass_marker: GEN_TEST_PASS`,
`program:` block per gen_runtime_api.md Section 7e, `owner: test-writer`. Entries are staged in
`dv/auto_dv/work/test-writer/gen_testlist_entries.yaml` for Runtime.

## 2. Run order (GenTest.run)

| Step | Method | What happens | Failure path |
|---|---|---|---|
| 1 | `setup()` | asserts `+gen_fetch_en_at_reset=0`; `GenBridge.start()` (alive, listener_armed, stim_active); `readback()`: `+gen_mem_readback_words` (default `GEN_MEM_READBACK_WORDS_DEFAULT`) image words drawn with the run seed are read through MEM_PEEK and compared with Python's parse of the `.vmem` (C3.3 backdoor rule); `apply_layers()`; FETCH_EN(1) releases the core | Python assert (read-back mismatch, missing plusarg) |
| 2 | `apply_layers()` | layer 2: the knobs in `schedulable` that are not pinned on the command line are drawn from the seed (`lib.draw_knobs`); layer 3: `lib.Schedule.derive` builds K phases (phase 0 at `c0` carries the layer-2 values; phases 1..K-1 at cycle boundaries drawn from the CG-REG-007 duration classes, each changing a random non-empty subset of the knobs). `+gen_regime_sched=<text>` replaces both (consumed, source `supplied`); a supplied schedule naming a pinned knob is an assert. Phase-0 entries are applied through REGIME_SET before the first fetch. Logs `GEN_TEST_KNOBS`, `GEN_TEST_SCHED`, one `GEN_TEST_PHASE` per applied entry | REGIME_SET of a knob without a consumer is a collected `uvm_error GEN_CMD_DISPATCH` (fails the run) |
| 3 | `run_schedule()` (forked) + `stimulus()` (forked) | the schedule runner arms the bridge cycle or retirement threshold of the next boundary and applies its entries when reached; it stops when the program ends first. `stimulus()` is the test's body and shares the bridge through `self.cmd()` (a lock serializes the two coroutines) | timeouts are asserts naming the awaited edge |
| 4 | `wait_eot()` | awaits the `evt_eot_seen` edge (tohost or the EOT MMIO register) within `program_budget_cycles`, records `eot_cycle`/`eot_retired`; then waits for `stimulus()` to return, lets the schedule runner finish a boundary it is applying (a boundary that passes in the end-of-test cycle itself still counts as hit and is applied), and kills the runner | assert on timeout |
| 5 | `schedule_check()` then `fire_check()` | `self.check(name, ok, detail)` counts the check, logs `GEN_TEST_FIRE <name> ok=<bool> <detail>` and collects failures. `schedule_check()` computes the reached phases from the bridge counts at the end-of-test store (`eot_cycle`, `eot_retired`: a phase is reached when its `c`/`r` boundary is at or below them), and fails when a reached phase is missing from the applied list, when a phase was applied before its boundary, or when the counts differ; with no schedulable knob it logs `GEN_TEST_LAYERS not_applied` and records no check | one `AssertionError` with every failure: `GEN_TEST_FAIL <name>: n fire-check failure(s): ...` (or `GEN_TEST_XFAIL <bug> ...` when `xfail_bug` is set) |
| 6 | `finish()` | logs `GEN_TEST_BINS n=<count> <tokens>`; refuses a run whose `fire_check()` recorded no check (`GEN_TEST_FAIL <name>: fire_check() recorded no check`); checks that the declared bins equal the test's manifest file (`lib.check_manifest_matches`: a stale or missing manifest fails the run with the differing tokens named; only a test that declares no bins and has no manifest skips); raises the collected failures BEFORE the handshake (TB_CONTRACT Section 2); `GenBridge.finish()` (stim_active 0, cmds_consumed == sent, finish_req, finish_ack edge); logs `<name> GEN_TEST_PASS` | asserts as named |

Every logged string is ASCII (`lib.check_ascii` runs over the test tree in the library self-test).

## 3. Class attributes a test sets

| Attribute | Default | Meaning |
|---|---|---|
| `name` | `gen_test_template` | test name; equals the testlist entry and the manifest stem |
| `plan_group` | `None` (gen_<x> for gen_test_<x>) | test-plan group whose bins `declare_bins()` declares by default, derived by the manifest generator's own code (`gen_fcov_manifest.plan_bins`), so the rendered manifest is proven current at every run |
| `schedulable` | `lib.REGIME_KNOBS` (all 20 regime knobs) | the knobs the test DECLARES layers 2 and 3 must vary; `lib.TIMING_ONLY_KNOBS` (bus latencies, outstanding cap, scramble-key delay) for a program with no handler for injected errors or events. Only the declared knobs the build consumes (`lib.CONSUMED_KNOBS`, Section 8) are drawn and scheduled |
| `layers_required` | `True` | a declared knob without a REGIME_SET consumer in the build fails `setup()` (`GEN_TEST_FAIL <name>: declared regime knobs ... have no REGIME_SET consumer in this build`), so a test never runs with its layers silently off; `False` is for bring-up tests only (`measured: false`, reason in the docstring) and logs `GEN_TEST_LAYERS not_applied` instead |
| `k_range` | `(1, 5)` | inclusive range of the schedule phase count K (CG-REG-007 `cp_phase_count`) |
| `duration_weights` | `lib.DEFAULT_DURATION_WEIGHTS` (short 6, medium 3, long 1) | class weights of the phase lengths (`lib.DURATION_CLASSES`) |
| `program_budget_cycles` | `GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT` | cycles the program may take to its end-of-test store; also the threshold-wait budget |
| `finish_timeout_cycles` | `None` (bridge default) | finish-handshake budget |
| `xfail_bug` | `None` | bug id (`gen_bug_log.md`) of an `_xfail` test; the failing line then starts `GEN_TEST_XFAIL <id>` so the flow's XFAIL is attributable |
| `expected_reports` | `0` | program report channel: the number of result words the directed program stores to the EOT MMIO register (`MEMORY_MAP["eot_addr"]`, `GEN_MM_EOT_ADDR`) before its final tohost store; each store toggles `evt_eot_seen` and leaves its value in `evt_eot_code`, so `wait_eot()` collects them edge by edge into `self.reports` (logged `GEN_TEST_REPORT idx=<i> value=<hex>`), asserts that no store was skipped (the store counter advances by one per awaited edge) and treats store number `expected_reports + 1` as the end of test. 0 = tohost only (riscv-dv programs) |

## 4. Instance helpers for the hooks

| Helper | Use |
|---|---|
| `await self.cmd(kind, args, timeout_cycles)` | serialized bridge command (`kind` from `gen_knobs.CMD`); returns `peek_data` |
| `await self.wait_cycles(count)` / `await self.wait_retired(count, timeout_cycles)` | arm one bridge threshold (absolute cycle or retirement count) and await its single edge; return True when the boundary was reached (including in the end-of-test cycle itself), False when the program ended before it. A False return is information for the stimulus body, never a fire-check: "did it fire" is asserted in `fire_check()` from an observable |
| `await self.wait_event("evt_irq_taken" or "evt_dbg_entered", timeout_cycles)` | await one monitor event edge, same abandon-on-EOT rule |
| `self.cycle()`, `self.retired()`, `self.eot_count()` | bridge counts (read, never polled) |
| `self.rng` | `random.Random` stream `<seed>:test` for the test's own layer-1 draws (`lib.Weighted(table).draw(self.rng)`) |
| `self.image` | `GenImage`: words, sidecar (`test`, `symbols`, `checksum`), tohost |
| `self.knobs`, `self.schedule`, `self.applied` | the layer-2 draw, the `Schedule`, the applied `Phase` list (each with `applied_cycle`) |
| `self.check(what, ok, detail)` | one fire-check result |
| `self.info(ident, detail)` | a reported, never gated observation: `GEN_TEST_RTL_OUTCOME <Bn>` (the RTL outcome an `_xfail` test logs beside its spec assert) or `GEN_TEST_INFO <id>` (an `_info` test's observation) |

Expected-fail and informational tests (DV Lead acceptance, `gen_test_plan.md` Section 0 and 0a): an
`_xfail` test sets `xfail_bug = "<Bn>"` (`gen_bug_log.md`, B1..B18), asserts the SPEC outcome through
the compare Section 0a names for that bug (B1/B2/B3/B15 through the C5.3b checker rows, whose
`uvm_error` the flow collects; B4, B5, B7, B10, B11, B13, B16, B17 through the named test-level
compare in `fire_check()`), and logs the RTL outcome with `self.info("<Bn>", ...)`; its failing line
then reads `GEN_TEST_XFAIL <Bn> ...` and the flow reports XFAIL. An `_info` test (B9, B14 items)
asserts only that its scenario fired and logs the observation with `self.info("<TP id>", ...)`.
Every test docstring cites its group, its TP items and the canonical feature IDs they cover (ALIAS
and FOLDED IDs resolved through `gen_feature_list.md` Section 3), so traceability sampling can start
from the test file.

Library functions: `lib.plus(name, default)` / `lib.plus_int` (plusargs by rendered name),
`lib.knob_is_pinned`, `lib.knob_values` (the bridge argument codes for IRQ_SET/IRQ_CLR/DBG_REQ/
MEM_ERR_ARM are NOT in the library: their authority is the step-2b dispatcher, not in the tree, and
the codegen is asked to render them into `gen_knobs.py`; tests that need them wait), `lib.program_min_retired(image)`
(riscv-dv `+instr_cnt` of the entry, or the directed program's `gen_min_retired` word),
`lib.program_symbol_word(image, symbol)`, `lib.riscv_dv_instr_cnt(test)`,
`lib.plan_bins(test, group)`, `lib.load_manifest_bins(test)`, `lib.check_manifest_matches(test, declared)`.

## 5. The regime schedule text (+gen_regime_sched)

`<knob>:<value>@c<N>` (cycle count) or `@r<N>` (retirement count), comma-separated; `<knob>` is the
plan-side name (`imem_gnt_delay`, ...; the yaml name with `knob_` is accepted); `<value>` is one of
the knob's yaml values. One schedule uses ONE trigger kind (all `c` or all `r`; a mix is refused by
`lib.Schedule`), so the runner applies boundaries in count order, which is time order. Entries at
`c0` are the layer-2 values. The derived text is logged at
`GEN_TEST_SCHED source=derived k=<K> sched=<text>`; passing that text back as
`+gen_regime_sched=<text>` reproduces the schedule (source `supplied`), and `+gen_knob_<name>=<v>`
pins a knob for the run (it is then excluded from the draw and refused in a supplied schedule).
Every applied entry is one REGIME_SET (arg0 knob id `KNOB_IDS`, arg1 value index) and one
`GEN_PHASE` line on the SV side.

## 6. Directed programs

`dv/auto_dv/tests/gen_programs/gen_<name>.S`, assembled by `gen_program.py --directed` (testlist
`program: {directed: [path]}`); conventions of `dv/auto_dv/stim/gen_directed/gen_zc_directed.S`
(`_start`, `tohost` in `.data`, end of test = store 1 pass / 3 fail); Zc encodings through
`gen_zc_insn.h`; a debug program is the program's own `.debug_rom` section. Every directed program
defines the word `gen_min_retired` (its retirement floor) so `lib.program_min_retired` has a
program-derived value; `gen_boot_retire_red.S` is the TDD red fixture (tohost 3, unreachable
floor).

Program report channel (the one Python-visible data path from a program today): a directed program
stores its result words (read-back values, computed checks, markers) to the EOT MMIO register and
ends with the tohost store; the test sets `expected_reports` and asserts `self.reports[i]` in
`fire_check()`. The register address comes from the rendered memory map (a program includes a
header rendered from `gen_knobs.MEMORY_MAP["eot_addr"]`, never a re-typed address). Words are 32
bits; a program that needs more reports stores more words. The channel carries what the program
knows architecturally; RVFI-derived facts (per-record opcode, operands, trap flags) need the RVFI
export TB Infra is asked for (plan Section 6 item 5).

## 7. Host-side checks

`python3 -m dv.auto_dv.tests.gen_test_lib --self-test` from the clone root (the module imports
`dv.auto_dv.gen_tb.gen_knobs`, so the clone root must be on `sys.path`; the script form
`python3 dv/auto_dv/tests/gen_test_lib.py --self-test` works when `ci/env.sh` has put the clone
root on `PYTHONPATH`): schedule determinism and seed dependence,
text round trip, REGIME_SET argument mapping, knob draw domain, mixed-trigger-kind refusal, riscv-dv
`+instr_cnt` lookup, the mixed-trigger-kind refusal, the consumed-knob derivation from the dispatcher source (fixture and negative case), ASCII scan of every test source and program, and the test-module structure check `lib.check_test_module` over every `gen_test_*.py`: a GenTest subclass overrides only `stimulus`, `fire_check`, `declare_bins` and `fire_*` methods (never `run`, `finish`, `check`, `setup` or any other template method), calls `self.check` at least once, and never passes a literal as the `ok` argument (three red sources are refused in the self-test). `python3 -m py_compile` on each
test module. Both run before a test is offered to Runtime. `python3 dv/auto_dv/tests/gen_fcov_manifest.py
--group <group> --test <test> [--write]` renders the test's manifest from the plan's traceability CSV
(`--self-test` checks it on gen_reg_schedule); `lib.check_manifest_matches` compares it with
`declare_bins()`.

## 8. Known limits (this version)

- `lib.CONSUMED_KNOBS` (the knobs the build's REGIME_SET dispatcher consumes) is derived, never
  hand-typed: from the rendered `gen_knobs.REGIME_SET_CONSUMED` when the codegen provides it (asked
  of TB Infra), else parsed from `gen_cmd_dispatch::apply_knob` in `dv/auto_dv/env/gen_env_pkg.sv`
  (prefix and exact-name tests, the parked step-2b idiom); the parser is the pre-codegen fallback
  only: TB Infra renders `REGIME_SET_CONSUMED` in the same commit as the re-landed dispatcher, whose
  guard uses the same rendering. At HEAD no consumer exists, so the set is empty; a test that declares knobs then
  FAILS at setup unless it is a bring-up test with `layers_required = False`, which logs
  `GEN_TEST_LAYERS not_applied`. The layers were proven on the step-2b tree (evidence Sections 2-3).
- Phase accounting is Python's (commands sent and consumed, no dispatcher error); a bridge field
  with the SV phase count is asked of TB Infra so `schedule_check` can compare both sides.
- No covergroup exists yet: entries carry `fcov_expectation_file: null`; `declare_bins()` already declares
  the plan's bins and finish() proves the rendered manifest current (red fixtures gen_ut_manifest_missing,
  gen_ut_manifest_stale under dv/auto_dv/tests/gen_fixtures/); the manifests are wired when `gen_fcov_pkg` lands.
- Bridge argument codes (IRQ hold policies, line-mask bits, DBG_REQ policies, MEM_ERR_ARM kinds) are
  not in the library: `gen_knobs_codegen.py` is asked to render them (plan Section 6 item 1); until
  then no committed test issues IRQ_SET, IRQ_CLR, NMI_PULSE, DBG_REQ or MEM_ERR_ARM.
