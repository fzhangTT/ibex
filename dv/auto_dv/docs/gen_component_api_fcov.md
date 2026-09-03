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

## 8. The plan's covergroups (T-205)

Files: `dv/auto_dv/tb/gen_fcov_codegen.py` renders `dv/auto_dv/env/gen_fcov_groups.svh` from two inputs and nothing else:
`dv/auto_dv/docs/gen_trace_tp_bin.csv` (every bin a plan covergroup declares, cross bins included and already reduced by the
plan's ignore rules) and `dv/auto_dv/docs/gen_fcov_plan.md` (the SV name from the header `### CG-X-nnn: gen_cg_<name>` ->
`gen_<name>_cg`, each coverpoint's bin ORDER from its `bins a{..}, b{..}` list, each cross's component coverpoints from
`cr_x = cp_a x cp_b [x cp_c]` and its explicitly named tuples such as `div_intmin_m1{div, int_min, all_ones}`). Per group:
`covergroup gen_<name>_cg with function sample(int v_<cp>, ...)` in the plan's coverpoint order, type-based
(`option.per_instance = 0`, so urg reports `gen_<name>_cg.<cp>.<bin>`), one `bins <name> = {i}` per plan bin on consecutive
indices with a `localparam int GEN_FC_<NAME>_<CP>_<BIN>` per bin, `ignore_bins na = {-1}` (a not-applicable sample), and one
`bins <csv name> = binsof(cp_a.x) && binsof(cp_b.y)` per cross bin (the name is the components joined by `_`; the renderer splits
it by longest match with backtracking or takes the plan's explicit tuple). Bin names that are SystemVerilog keywords (`xor`,
`or`, `and`, ...) render as escaped identifiers; urg prints them plainly, so the manifests keep the plan's names. Refusals:
plan bins differing from the CSV bins of a coverpoint, a cross bin that does not split into its components, a cross without a
plan line, a group without a plan header (unit test `dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py`); `--check` fails on a stale
include. `IMPLEMENTED` in the renderer lists the groups whose samplers exist; a group renders only when it is sampled.

Sampler: `gen_isa_cov` (this package), a subscriber of the RVFI monitor beside the scoreboard, samples on every record with
`rvfi_trap == 0` whose encoding the plan's condition names; RVFI reports a compressed instruction in its 16-bit form, so
c.mul is decoded from it (a decoder that only knows the 32-bit word never sees it: mutant FM1). Classifiers are partitions of
the record fields (rs1_rdata, rs2_rdata, rd_wdata, the register indices, the immediate) with the plan's bins in the plan's
order; where two plan bins can hold at once the precedence is stated in the code and here: overflow before carry / borrow
(cp_wrap), the named boundary cases before `eq` before `other` (cp_slt_case), the listed values before the relations to the
dividend before the sign classes (cp_divisor), the listed values before the byte / half-word sign classes before the sign
(CG-BIT-001 cp_rs1_class), exact values before "upper bits clear" before other (cp_rs2_upper). `rd_wdata` is forced to 0 on an
rd = x0 record (rtl/ibex_core.sv:2344-2346), so its result class is `zero`; the wrap bins are recomputed from the operands (the
ALU's carry never leaves it, rtl/ibex_alu.sv:105-107; rtl-arch gen_cg_sampling_anchors.md). `+gen_fcov_en=0` instantiates
nothing and the report line says so (`GEN_FCOV isa samples: ... (covergroups off)`).

| group (plan id) | sample condition (plan) | coverpoint bins / cross bins rendered | proof run |
|---|---|---|---|
| gen_mul_ops_cg (CG-MUL-001) | OP funct7 0000001 funct3 000..011, or c.mul (16-bit `100111 rsd' 10 rs2' 01`) | 46 / 390 | gen_muldiv_directed.S |
| gen_div_ops_cg (CG-MUL-003) | OP funct7 0000001 funct3 100..111 | 36 / 140 | gen_muldiv_directed.S |
| gen_isa_alu_reg_cg (CG-ISA-002) | OP funct7 0000000 / 0100000 (sub), funct3 not a shift; Zb funct7 values excluded | 46 / 294 | gen_muldiv_directed.S |
| gen_bit_zba_zbb_ops_cg (CG-BIT-001) | the decoder arms rtl/ibex_decoder.sv:609-624 (sh1add..packh) and OP-IMM sext.b / sext.h (:1106-1107); zext_h = pack with rs2 = x0 | 51 / 373 | gen_alu_directed.S |
| gen_isa_alu_imm_cg (CG-ISA-001) | OP-IMM funct3 not 001 / 101 | 40 / 105 | gen_alu_directed.S |
| gen_isa_shift_cg (CG-ISA-003) | OP-IMM / OP funct3 001 / 101 with funct7 0000000 / 0100000 (the Zb shift space excluded) | 31 / 101 | gen_alu_directed.S |
| gen_bit_count_cg (CG-BIT-002) | OP-IMM funct3 001 with instr[31:20] 0x600 / 0x601 / 0x602 (clz / ctz / cpop) | 52 / 147 | gen_bitcnt_directed.S |
| gen_cmp_zca_cg (CG-CMP-001) | a 16-bit retirement (rvfi_insn[1:0] != 11, no Zcmp micro-op) for every coverpoint but the straddle, which samples 32-bit retirements; the next instruction's length makes the sample one record late | 54 / 169 | gen_zca_directed.S |
| gen_cmp_zcmp_pushpop_cg (CG-CMP-006) | the last micro-op record (rvfi_ext_expanded_insn_last) of a cm.push / cm.pop / cm.popret / cm.popretz whose sequence never trapped, collected from its first micro-op | 51 / 244 | gen_zcmp_directed.S (+ the min1 / long / random regime runs) |

Slice 2 additions. CG-CMP-001 keeps one 16-bit record pending until the next record arrives (its `cp_next_len`); a Zcmp
micro-op record counts as a 16-bit successor; c.nop is c.addi with rd = x0, c.addi16sp is the c.lui encoding with rd = x2, c.jr /
c.jalr are the CR forms with rs2 = 0 (c.ebreak is a trap record and never samples); `cp_reg3` is the CIW rd' or the CL / CS / CA /
CB rs1' field, `cp_rd_full` the CI / CR rd or the c.swsp rs2 field (x0 has no bin); the coverpoint is operand-only in the trace CSV
(counted in the adopted group) and renders from the plan line because `cr_insn_reg3` needs it. CG-CMP-006 is a sequence
collector: from the first micro-op record at a pc (rvfi_ext_expanded_insn_valid) to the record with _last, it decodes the 16-bit
source word (kind, rlist, spimm; N = rlist - 3, 13 for rlist 15; stack_adj = 16 / 32 / 48 / 64 + 16 * spimm per zcmp.adoc), takes sp
from the first sp-based store or load micro-op (rs1_rdata), checks every store / load against the predicted register order
(descending) and address (sp - 4k, sp + adj - 4k), the tags (intermediate pc_wdata == pc_rdata, 32-bit synthesized words), the
micro-op count (N + 1, + 2 for popret, + 3 for popretz), the return alignment from the jalr micro-op's rs1_rdata, minstret through
rvfi_ext_mhpmcounters[7] (mhpmcounter10, NumInstrRetC: the record before the sequence against the last micro-op), the dmem delay
class from the regime knob in force (`knob_dmem_rvalid_delay`: min1 / short / long, random = mixed) and dummy_instr_en from the model's
cpuctrlsts bit 2 (`gen_isa_read_csr`); a trapping micro-op or a record of another pc abandons the sequence (counted). The wrap bins
(`push_below_zero`, `pop_above_max`) need a stack around address 0 or 2^32 and are not exercised by the proof programs.

Evidence (dv/auto_dv/evidence/gen_tdd_fcov.md): each proof run is a lock-step run of the named operand-walk program (every
result also compared against the model), urg on its own vdb, and `ci/check_fcov_expectations.py --report-dir` on a manifest of
every coverpoint bin of the groups (`gen_fcov_proof_slice1.fcov.yaml`, `gen_fcov_proof_slice1b.fcov.yaml`: PASS, 128 and 122
bins); red: the same manifest against a run with `+gen_fcov_en=0` (no covergroup, urg writes no grpinfo.txt, the checker fails
on the missing report, round 0's failure shape) and mutant FM1 (the checker names `gen_mul_ops_cg.cp_op.c_mul` unhit). Every
bin the promoted manifests reference for these six groups (1500) exists by name in the rendered include. Known gap, not this
component's: the checker parses only `Summary for Variable` sections of urg's text report and never a `Summary for Cross`
section, whose covered rows are component tuples (LOG-054: Runtime derives the variable form); until then the proof manifests
declare coverpoint bins and the cross coverage is read from urg's per-cross `User Defined Cross Bins` summary.
