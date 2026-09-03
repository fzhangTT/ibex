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
    def declare_bins(self): ...            # override only to declare a subset; default: the plan's bins of the
                                           #   items named by the class's fire_tp_<area>_<nnn> methods

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
| 3 | `run_schedule()` (forked) + `stimulus()` (forked) | the schedule runner arms the bridge cycle or retirement threshold of the next boundary and applies its entries when reached; it stops when the program ends first (the final store, number `expected_reports + 1`; a report store toggles the same `evt_eot_seen` and does not end a wait). `stimulus()` is the test's body and shares the bridge through `self.cmd()` (a lock serializes the two coroutines) | timeouts are asserts naming the awaited edge |
| 4 | `wait_eot()` | awaits each report store and the end-of-test store (`evt_eot_seen` edges); a store is late only when retirement stopped for `program_budget_cycles` (`GEN_TEST: ... no retirement`, the hang detector) or lagged `PROGRESS_ROUNDS_MAX` budgets while the core kept retiring (`runaway program`); every lagging budget logs `GEN_TEST_SLOW` and finish() reports `GEN_TEST_SLOW_TOTAL rounds=<n>` (slow bus regimes stretch a program several times over; fixtures gen_ut_eot_stall and gen_ut_eot_runaway are the reds); records `eot_cycle`/`eot_retired`; then waits for `stimulus()` to return, lets the schedule runner finish a boundary it is applying (a boundary that passes in the end-of-test cycle itself still counts as hit and is applied), and kills the runner | assert on timeout |
| 5 | `schedule_check()` then `fire_check()` | `self.check(name, ok, detail)` counts the check, logs `GEN_TEST_FIRE <name> ok=<bool> <detail>` and collects failures. `schedule_check()` computes the reached phases from the bridge counts at the end-of-test store (`eot_cycle`, `eot_retired`: a phase is reached when its `c`/`r` boundary is at or below them), and fails when a reached phase is missing from the applied list, when a phase was applied before its boundary, or when the counts differ; with no schedulable knob it logs `GEN_TEST_LAYERS not_applied` and records no check | one `AssertionError` with every failure: `GEN_TEST_FAIL <name>: n fire-check failure(s): ...` (or `GEN_TEST_XFAIL <bug> ...` when `xfail_bug` is set) |
| 6 | `finish()` | logs `GEN_TEST_BINS n=<count> <tokens>`; refuses a run whose `fire_check()` recorded no check (`GEN_TEST_FAIL <name>: fire_check() recorded no check`); checks that the declared bins equal the test's manifest file (`lib.check_manifest_matches`: a stale or missing manifest fails the run with the differing tokens named; only a test that declares no bins and has no manifest skips); raises the collected failures as `lib.fire_fail_line(name, failures)` (the line a red entry's `red_expect` matches) BEFORE the handshake (TB_CONTRACT Section 2); `GenBridge.finish()` (stim_active 0, cmds_consumed == sent, finish_req, finish_ack edge); logs `<name> GEN_TEST_PASS` | asserts as named |

Every logged string is ASCII (`lib.check_ascii` runs over the test tree in the library self-test).

## 3. Class attributes a test sets

| Attribute | Default | Meaning |
|---|---|---|
| `name` | `gen_test_template` | test name; equals the testlist entry and the manifest stem |
| (items) | the class's `fire_tp_<area>_<nnn>` methods | `declare_bins()` defaults to the plan's bins of exactly those items (`lib.fire_items`, `lib.plan_bins`, the manifest generator's own code); `gen_fcov_manifest.py --test-module <file> --test <name> --write` renders the same set, so a manifest covers the items the test checks and finish() proves it current at every run |
| `schedulable` | `lib.REGIME_KNOBS` (all 20 regime knobs) | the knobs the test DECLARES layers 2 and 3 must vary; `lib.TIMING_ONLY_KNOBS` (bus latencies, outstanding cap, scramble-key delay) for a program with no handler for injected errors or events. Only the declared knobs the build consumes (`lib.CONSUMED_KNOBS`, Section 8) are drawn and scheduled |
| `program_handlers` | `()` | the handlers the program carries, a literal tuple drawn from `lib.HANDLERS` (`"dbg"`: a debug ROM in the DM window, `"irq"`: a returning interrupt handler, the NMI vector included, `"exc"`: a trap handler for injected bus faults); with `mie_stays_zero` it gates which regime knobs may be in play (the regime-handler rule, Section 9) |
| `mie_stays_zero` | `False` | literal True when the program never enables interrupts (mstatus.MIE stays 0), so the irq knobs may be in play without a handler as long as no NMI can be driven (not knob_irq_regime and knob_irq_line_mix together): lines are driven, nothing is taken |
| `layers_required` | `True` | a declared knob without a REGIME_SET consumer in the build fails `setup()` (`GEN_TEST_FAIL <name>: declared regime knobs ... have no REGIME_SET consumer in this build`), so a test never runs with its layers silently off; `False` is for bring-up tests only (`measured: false`, reason in the docstring) and logs `GEN_TEST_LAYERS not_applied` instead |
| `k_range` | `(1, 5)` | inclusive range of the schedule phase count K (CG-REG-007 `cp_phase_count`) |
| `duration_weights` | `lib.DEFAULT_DURATION_WEIGHTS` (short 6, medium 3, long 1) | class weights of the phase lengths (`lib.DURATION_CLASSES`) |
| `program_budget_cycles` | `GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT` | the no-progress budget: cycles without a retirement (or without a report store while the core retires, times `progress_rounds_max` = `PROGRESS_ROUNDS_MAX`) before the run fails; also the threshold-wait budget |
| `finish_timeout_cycles` | `None` (bridge default) | finish-handshake budget |
| `xfail_bug` | `None` | bug id (`gen_bug_log.md`) of an `_xfail` test; the failing line then starts `GEN_TEST_XFAIL <id>` so the flow's XFAIL is attributable |
| `expected_reports` | `0` | program report channel: the number of result words the directed program stores to the EOT MMIO register (`MEMORY_MAP["eot_addr"]`, `GEN_MM_EOT_ADDR`) before its final tohost store; each store toggles `evt_eot_seen` and leaves its value in `evt_eot_code`, so `wait_eot()` collects them edge by edge into `self.reports` (logged `GEN_TEST_REPORT idx=<i> value=<hex>`), asserts that no store was skipped (the store counter advances by one per awaited edge) and treats store number `expected_reports + 1` as the end of test. 0 = tohost only (riscv-dv programs) |

## 4. Instance helpers for the hooks

| Helper | Use |
|---|---|
| `await self.cmd(kind, args, timeout_cycles)` | serialized bridge command (`kind` from `gen_knobs.CMD`); returns `peek_data` |
| `await self.wait_cycles(count)` / `await self.wait_retired(count, timeout_cycles)` | arm one bridge threshold (absolute cycle or retirement count) and await its single edge; return True when the boundary was reached (including in the end-of-test cycle itself), False when the program ended before it (the final store; report stores through the EOT register do not end the wait). A False return is information for the stimulus body, never a fire-check: "did it fire" is asserted in `fire_check()` from an observable |
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
`lib.fire_items(cls)`, `lib.plan_bins(test, items)`, `lib.load_manifest_bins(test)`, `lib.check_manifest_matches(test, declared)`.

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
`+instr_cnt` lookup, the consumed-knob derivation from the dispatcher source (fixture with the `automatic` form and commented-out tests, and the negative case), ASCII scan of every test source and program, and the test-module structure check `lib.check_test_module` over every `gen_test_*.py`: a GenTest subclass overrides only `stimulus`, `fire_check`, `declare_bins` and `fire_*` methods (never `run`, `finish`, `check`, `setup` or any other template method), calls `self.check` at least once, and never passes a literal as the `ok` argument (three red sources are refused in the self-test). `python3 -m py_compile` on each
test module. Both run before a test is offered to Runtime. `python3 dv/auto_dv/tests/gen_fcov_manifest.py
--group <group> --test <test> [--write]` renders the test's manifest from the plan's traceability CSV (`--test-module <file>` for the
items the test's fire_tp_* methods name, the acceptance form; `--group` for a whole group before a test exists; the
`[CYCLE-CLAUSE ...]` marker token keeps a marked item's CG-WIT-001 witness bin out, rule f; `--self-test` checks it on
gen_reg_schedule, TP-CSR-029 and gen_test_cmp_zcb.py); `lib.check_manifest_matches` compares it with
`declare_bins()`.


The structure check is lint: it runs in the library self-test (and before a test is offered to Runtime), never inside
the flow or the simulation; its guarantees are those of a source check (a hook cannot forge a witness record or
patch the library WITHOUT the self-test refusing the module), not a runtime sandbox. `lib.testlist_entry(name)` reads
the committed `dv/auto_dv/flow/gen_testlist.yaml` only; a developer run may name a staged-entries file through the
environment variable `GEN_TEST_STAGED_ENTRIES` (announced on stderr, never set by the flow). Every program generator
must run as a script with no PYTHONPATH from the clone root (the flow's form); the self-test runs each one so.
`dv/auto_dv/tests/gen_fixtures/gen_run_fixture.sh <OUT> <name> <module> <abs vmem> [plusargs]` runs one fixture or
test against a local build; `GEN_TB_PYROOT=<tree>` puts a tree whose `dv/auto_dv/gen_tb` matches the build (an export
of HEAD without `dv/auto_dv/tests`) before the clone on PYTHONPATH.

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

## 9. Structure rules and the witness epilogue

`lib.check_test_source` (Section 7) enforces, over every `GenTest` subclass with bases resolved through
module-level aliases (`Base = GenTest`): test classes are module-level (a class inside a function is
refused); module-level writes to a test class (`T.finish = f`, `setattr`) are refused; only the four hooks
and `fire_*` methods are defined; at least one `self.check` with a non-literal ok; `layers_required =
False` is accepted only when the class's `name` has a testlist entry with `measured: false` (committed
`gen_testlist.yaml`; a developer run may name a staged file through GEN_TEST_STAGED_ENTRIES, Section 7) or the class is in
`lib.LAYERS_OPTOUT_ALLOWLIST` with a reason (empty today); the token `COV_WITNESS` never appears in a
test; `cycle_clause_true=` is a keyword of `self.check` inside a `fire_*` method only. Each rule has a
refused red source in the self-test (three sets of red sources today; the self-test output lists them).

Regime-handler rule (LOG-050, Critic batch-1 v8 L-1): a regime knob may be in play only with the handler its events need.
`lib.KNOB_HANDLER` maps the knobs by name: knob_debug_req_regime needs `"dbg"` (a debug ROM in the DM window); the irq knobs
(knob_irq_regime, knob_irq_line_mix, knob_irq_hold) and knob_dmem_intg_err_rate (a data-side integrity error, on a load or a store
response, is an internal NMI)
need `"irq"` (a returning handler at mtvec, the NMI vector included); knob_imem_err_rate, knob_dmem_err_rate and
knob_imem_intg_err_rate need `"exc"` (a trap handler for the injected access fault). Latencies, the outstanding cap, the
scramble key and the program-side markers need nothing. `mie_stays_zero = True` exempts the irq knobs only while no NMI can be
driven: knob_irq_regime (events) and knob_irq_line_mix (`with_nmi` drives irq_nm, which MIE does not mask) may not both be in
play with active values. `lib.check_regime_handlers(path)` is the structural form: it reads every test class's `schedulable`
(a literal tuple with module-level constants resolved, `lib.TIMING_ONLY_KNOBS` or `GenTest.schedulable`), `program_handlers`
(a literal tuple drawn from `lib.HANDLERS`) and `mie_stays_zero` (a literal); an annotated, tuple-target or augmented assignment
of those names, a decorated test class, a class keyword on any GenTest-derived class (a metaclass could rewrite them, so a
nameless base carries none either) and any other value form are refused as unreadable; absent attributes take the GenTest defaults,
not a base class's own value (a conservative refusal at worst). The library self-test runs it over every committed test module
with sixteen red sources and seven green ones. `setup()` applies the values-aware form at run time before any REGIME_SET and
before the first fetch: the knobs in play are the class's `schedulable`, the pinned knobs (`+gen_knob_<name>=`), every knob of
the schedule (derived, or supplied through `+gen_regime_sched`) and, for the four per-mille fault plusargs the bus agents honour
outside the regime knobs (`+gen_ibus_err_rate`, `+gen_ibus_intg_err_rate`, `+gen_dbus_err_rate`, `+gen_dbus_intg_err_rate`), the
fault knob they inject as (`lib.RAW_FAULT_PLUSARGS`, a nonzero value counts as active), each with the values it takes; a knob whose
only value is its inactive one (`quiet`, `none`) needs nothing, and a run whose regimes the program cannot survive fails
`GEN_TEST_FAIL <name>: the run's regimes are ones its program cannot survive`. It is a structural check beside the lint, not a
16th refused form (LOG-024d keeps `REFUSED_FORMS` frozen). The template default `schedulable = lib.REGIME_KNOBS` names the irq,
dbg and fault-injection knobs, so a test that keeps it must declare all three handlers; every committed test narrows
`schedulable` instead (`lib.TIMING_ONLY_KNOBS` or a literal tuple), and gen_test_rst_boot (knob_irq_regime) and
gen_test_csr_reset (knob_irq_line_mix), each without a handler, declare `mie_stays_zero = True` (one irq knob each, so no NMI
can be drawn; a pin of the other knob fails the run at setup whenever the drawn or scheduled values of the first are active:
storm pinned on csr_reset fails only when its drawn or scheduled line mix includes with_nmi, with_nmi pinned on rst_boot only when a
drawn or scheduled regime is active).

Witness protocol (plan v2f, Critic condition C-1): `self.check(what, ok, detail, cycle_clause_true=False)`
returns a `CheckResult`; a `fire_tp_<area>_<nnn>` method passes `cycle_clause_true=True` only on the TRUE
branch of its cycle-level clause after that clause passed against the export (False on the RVFI-only
fallback or a failed clause). `finish()` runs the epilogue AFTER the failure raise and BEFORE the finish
handshake: for exactly the passed results with `cycle_clause_true`, it maps `fire_tp_x_nnn` to `TP-X-nnn`
(`lib.tp_id_of`), requires each id in the entry's `witness_ids` (`lib.witness_ids_of(name)`) and each id's
owner (`lib.WITNESS_GROUP_OF`) to be the test's own plan group (`lib.test_group(name)`), and issues
`COV_WITNESS <item index> <group index>` awaited through `GenBridge.cov_witness(tp, own group)` (indices from the
rendered `gen_knobs.WITNESS_IDS` / `WITNESS_GROUPS` tables; the dispatcher refuses an item of another group with
`GEN_WITNESS_FOREIGN`, so the epilogue passes the issuing test's group, never the item's); a foreign id, an item
another group owns, a missing table or a missing command fails the run (`GEN_TEST_FAIL <name>: witness ...`), and a
test that never reaches the epilogue witnesses nothing. Logged as `GEN_TEST_WITNESS id=<tp> code=<n> group=<g>
group_idx=<i> bins=<count>` (the count is the peek word: distinct witness bins the covergroup holds). No test issues a
witness until an entry lists `witness_ids` through Runtime's witness_render; the SV side (dispatcher row, the CG-WIT-001
covergroup, `GEN_WITNESS_FOREIGN`) is built (gen_fcov_pkg).

What the witness guarantee rests on, truthfully: the fact of record is the SV witness ledger (gen_fcov_pkg), which samples
only on a `COV_WITNESS <item index> <group index>` command the template's epilogue issues for a passed fire-check whose
cycle clause held, with the item allowed by the committed testlist entry and the group the issuing test's own; a Python
test cannot produce that record by itself. The Python side keeps the record template-private (`_results`, filled by `check()`; allowed ids
read in the epilogue from the committed entry of the class's name; codes from the rendered table; an id the table lacks
fails with the GEN_TEST_FAIL prefix), and `check_test_source` is defense in depth, a source lint that refuses exactly these statement shapes (the library
self-test's red list, `lib.REFUSED_FORMS`: at least one refused red source per line, and the self-test fails when this
list and the table differ):

- a template method other than the four hooks overridden in the test class (directly, through an aliased base, an
  import alias, a mixin, a class-body assignment of the method name, or an instance rebinding from a method or helper,
  e.g. self.cmd = f), or an attribute reached through a template-owned name rebound from a method (an attribute chain
  rooted at self, e.g. self.bridge.cov_witness = f)
- check() with a literal outcome
- fire_check() that records no check
- fire_tp_* items out of step with the plan group: a fire_tp_* method fire_check() never calls, a check name that
  does not start with its item's id, not_built missing or not a literal dict, an item both built and declared not
  built, an item neither built nor declared
- module-level assignment or setattr() over the test class, the library or the template
- the test class defined inside a function
- the COV_WITNESS command issued from test code
- cycle_clause_true outside a fire_tp_* method
- layers_required = False without a measured: false testlist entry, or a non-literal value
- a base class that is not GenTest by name: an unresolvable expression or an imported name
- the verdict record (_results, results, failures, checks, witness_ids, applied, schedule, reports; reads of reports
  excepted) called into, aliased, bound by a walrus or tuple target, passed to a callee, captured by a lambda,
  item-assigned or deleted
- assignment through self to a template-assigned attribute
- getattr(), setattr(), vars(), __dict__ or type() on the test object
- self passed to a module-level helper that touches a template-owned name, directly, through an alias inside the
  helper, or through an attribute chain rooted at the parameter
- self escaping as a bare name: an alias, a loop target or a keyword argument

Everything else passes; the lint is not a guarantee. The guarantee is architectural: the committed testlist ids, the
fire-check codes and the SV witness ledger. Shapes known to pass today, each an indirection-free statement or a patch
outside the enumerated names: `for self.failures in ([],)`, `with open(p) as self.failures`, `*self.failures, = []` (the same target
forms naming a template method are refused: the instance-rebinding check reaches tuple, starred, for, with and comprehension
targets in methods and helpers); an alias of a
template-owned attribute and a write through it (`b = self.bridge` then `b.cov_witness = None`; the escape rule covers the bare test
object and the verdict record, not `bridge`), the same one transformation away in a helper (`_h(self.bridge)` with `def _h(b):
b.cov_witness = f`, `b = t.bridge` inside a helper, `setattr(t.bridge, 'cov_witness', f)` inside a helper), a dunder call
(`self.__setattr__('bridge', None)`, `self.bridge.__setattr__(...)`) and a subscript inside a chain (`self.bridge.cmds[0].x = 1`, in
methods and helpers); template patching through an import alias or the full dotted path, exec/importlib, objects reached through
containers or return values, and helpers in other modules given an attribute rather than the test object (`forge(self)` with an
imported `forge` is refused as an escape, `forge(self.bridge)` passes). The refused-form list is frozen: a new refusal is a
structural check beside the lint, not a new form; those shapes are caught only by the SV ledger and review, and the self-test
carries the alias shape as a known-passing source so this paragraph stays checkable. The developer-variable guard in `__init__`
recognises a flow run by a `/runs/` run directory or the `GEN_DV_FLOW_RUN` environment marker (`lib.FLOW_RUN_ENV`, exported by
every flow job script); a flow layout without either is not covered. Fixtures gen_ut_witness_ok / _foreign / _notable /
_noid / _othergroup prove the five epilogue paths with a Python-side recorder in place of the bridge's cov_witness.

`run()` logs `GEN_TEST_DRAIN waited cycles=<n>` when the schedule runner was mid-apply at the end of test
(fixture gen_ut_drain_probe holds the runner 40 cycles across the end of test).
- The schedule runner's cycle triggers are absolute cycle counts and unaffected by slow bus regimes; a retirement-trigger
  schedule would need the same progress rule as the end-of-test wait and is not emitted today (schedules carry one trigger
  kind, `c`).
