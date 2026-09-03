# Component API: gen_fcov_pkg (CG-WIT-001, the witness covergroup)

Owner: tb-infra. Status: BUILT (landing 2b, T-179). Conventions as in every component document: knobs are plusargs named by a
`parameter string` in `gen_tb_pkg` and a Python constant of the same value; failures are `uvm_error` with an id.

## 1. Purpose

The one covergroup no DUT signal samples: `gen_wit_cycle_clause_cg` (plan id CG-WIT-001, dv/auto_dv/docs/gen_fcov_plan.md
Section 3.9) has one bin per marked test-plan item and is sampled by the bridge command `COV_WITNESS`, which a test's
epilogue issues for every fire-check result whose cycle clause held. A hit records that the owning test issued the command
for that item; the clause's truth is the host rules' (C-1: no direct `fire_tp_*` call and no COV_WITNESS outside the
template, `gen_test_lib.py`) and the dispatcher's (C-2: only the issuing test's own items are accepted).

## 2. Files and how to call it

- `dv/auto_dv/env/gen_fcov_pkg.sv`: package `gen_fcov_pkg` with the covergroup (type-based, `option.per_instance = 0`, so
  urg reports `gen_wit_cycle_clause_cg.cp_clause.<bin>`, the names the fcov manifests carry) and the component `gen_wit_cov`
  (`witness(idx, owner)`, the counters, the report line and the referee).
- `dv/auto_dv/env/gen_wit_bins.svh`: rendered by `dv/auto_dv/tb/gen_knobs_codegen.py` from the yaml key `witness_csv`
  (`dv/auto_dv/docs/gen_trace_witness_ids.csv`, columns index, tp_item, bin, test_group, marked): `GEN_WITNESS_COUNT`,
  `GEN_WITNESS_GROUP_COUNT`, `GEN_WITNESS_TP_NAMES` / `GEN_WITNESS_GROUP_NAMES` (csv strings for messages),
  `GEN_WITNESS_GROUP_OF[]` (the owning group index per row) and the macro `GEN_WIT_BINS` (one `bins w_tp_<area>_<nnn> = {i}`
  per row). The renderer refuses a CSV whose index is not the row order, a repeated tp_item or bin, a bad bin name, a
  bad group or a missing file (codegen unit test fixtures); `--check` covers the include like every rendered file.
- `dv/auto_dv/gen_tb/gen_knobs.py`: `WITNESS_IDS` (tp_item -> index; the name `gen_test_lib.py` imports), `WITNESS_BINS`,
  `WITNESS_GROUP_OF`, `WITNESS_GROUPS` (group -> index, first-appearance order), `WITNESS_COUNT`.
- Wiring: `gen_env` creates `wit` (`gen_wit_cov`) and hands it to `gen_cmd_dispatch`; the route is
  `GEN_CMD_COV_WITNESS: bvif.peek_data = wit.witness(t.arg[0], t.arg[1])`.
- Python: `await bridge.cov_witness(tp_item, owner_group)` (gen_component_api_bridge.md) returns the distinct bins hit so far
  as the covergroup counts them (`cp_clause.get_coverage() * GEN_WITNESS_COUNT / 100`, the int cast rounding to nearest); with
  `+gen_fcov_en=0` no covergroup exists and the count is the component's own bookkeeping.

## 3. Knobs

| Plusarg | `gen_tb_pkg` name | Meaning | Default |
|---|---|---|---|
| `+gen_fcov_en` | `PLUSARG_FCOV_EN` | instantiate the covergroup (0: bookkeeping only; the ablation knob of mutant WM1) | 1 |

## 4. Wave-level behaviour

The sample happens in the dispatcher's `write()`, i.e. in the `cmd_valid` wake that follows cocotb's deferred write, before
the ack; the peek word is computed in the same call, so the value the Python side reads with the ack already counts the
sample. Nothing else samples the group.

## 5. Checkers and referees

| id | rule | disable |
|---|---|---|
| `GEN_CMD_DISPATCH` (COV_WITNESS index) | an index at or beyond `GEN_WITNESS_COUNT` is a collected error | none |
| `GEN_WITNESS_FOREIGN` | the item's group (`GEN_WITNESS_GROUP_OF[idx]`) differs from arg1: a test may witness only its own items | none (red fixture gen_ut_witness_foreign) |
| `wit_referee` | at report: the covergroup's distinct-bin count equals the accepted witnesses' distinct count | none (a rendering or sampling defect) |

Report line: `GEN_WIT witnesses=<n> distinct=<d> covergroup=<c> foreign=<f> out_of_range=<o>`.

## 6. Evidence

Unit tests (dv/auto_dv/gen_tb/gen_tests/): `gen_ut_witness` (two items of the first group with two items, the first twice:
the peek counts 1, 1, 2), `gen_ut_witness_foreign` (a red fixture: one item issued with another group's index fails by
design through `GEN_WITNESS_FOREIGN`). TDD: red on the build without the dispatcher route (`command COV_WITNESS has no
consumer yet`, gen_fu_l2b_a_ut_witness_*), then a rounding defect of the distinct count (an `int` cast of a real rounds to
nearest, so `+ 0.5` double-rounded 0 to 1 and 1 to 2; gen_fu_l2b_b_ut_witness_*), then green (gen_fu_l2b_ut_witness_*).
Mutation WM1 (the covergroup never sampled): caught by gen_ut_witness (the peek stays 0), ablation `+gen_fcov_en=0` PASS
(gen_mut_step2b.md). Manifests: the bins enter a test's manifest by rule (f) of gen_fcov_manifest.py once the item's marker
token is released; the Test Writer's template issues the command from its finish() epilogue (`WITNESS_IDS`).

## 7. Protocol note for the template

`COV_WITNESS` carries the issuing test's group as arg1 because the dispatcher cannot otherwise know the running test; the
group name is the CSV's `test_group` column (`WITNESS_GROUP_OF[tp_item]` for the item's owner, `WITNESS_GROUPS` for the
index). A test that witnesses an item of another group fails, so the epilogue must pass its own group.
