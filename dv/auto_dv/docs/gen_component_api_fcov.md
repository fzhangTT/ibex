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
`cr_x = cp_a x cp_b [x cp_c]` and its explicitly named tuples such as `div_intmin_m1{div, int_min, all_ones}` or
`mstatus_csrrw{mstatus csrrw}`, comma-separated or, without commas, space-separated; a part is a bin name, a 1-bit value
(`all0{0 0 0 0}` names the bins `b<value>`) or the coverpoint's value text (`off_c0000{PMP_MODE_OFF, 0000}`), a trailing
`: comment` or `(comment)` is dropped, `a or b or c` names a set rendered as a `||` group, and `any <cp>` leaves that component
unconstrained). Per group:
`covergroup gen_<name>_cg with function sample(int v_<cp>, ...)` in the plan's coverpoint order, type-based
(`option.per_instance = 0`, so urg reports `gen_<name>_cg.<cp>.<bin>`; `option.cross_auto_bin_max = 0`, so a cross has exactly
the CSV's named bins and the plan's ignored tuples create no automatic bins), one `bins <name> = {i}` per plan bin on consecutive
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
| gen_cmp_zca_cg (CG-CMP-001) | a 16-bit retirement (rvfi_insn[1:0] != 11, no Zcmp micro-op) for every coverpoint but the straddle, which samples 32-bit retirements; the next instruction's length makes the sample one record late | 46 / 250 | gen_zca_directed.S |
| gen_cmp_zcmp_pushpop_cg (CG-CMP-006) | the last micro-op record (rvfi_ext_expanded_insn_last) of a cm.push / cm.pop / cm.popret / cm.popretz whose sequence never trapped, collected from its first micro-op | 47 / 244 | gen_zcmp_directed.S (+ the min1 / long / random regime runs) |
| gen_cmp_zcmp_mv_cg (CG-CMP-007) | the last micro-op record of a cm.mvsa01 / cm.mva01s (source word `101 011 r1s' 01/11 r2s' 10`), sampled one record late so the neighbour after is known | 29 / 134 | gen_zcmp_mv_directed.S |
| gen_csr_trap_setup_warl_cg (CG-CSR-002) | the read-back that closes a write pair on mstatus, misa, mie, mtvec, mcounteren, mstatush, menvcfg, menvcfgh: a CSR-op record with rd != x0 on the CSR of an open write | 67 / 143 | gen_csr_warl_directed.S (+ the mcounteren gate off / invalid runs) |
| gen_isa_branch_cg (CG-ISA-007) | BRANCH funct3 000 / 001 / 1xx, or c.beqz / c.bnez in the 16-bit form (`11x ... 01`), rvfi_trap == 0 | 28 / 180 | gen_branch_directed.S |
| gen_bit_sbit_cg (CG-BIT-006) | OP funct3 001 with funct7 0100100 / 0010100 / 0110100 (bclr / bset / binv), OP funct3 101 funct7 0100100 (bext), OP-IMM funct3 001 with instr[31:27] 01001 / 00101 / 01101 (bclri / bseti / binvi), funct3 101 with 01001 (bexti) | 22 / 100 | gen_sbit_directed.S |
| gen_cmp_zcb_cg (CG-CMP-005) | the 16-bit Zcb words: quadrant 00 funct3 100 (c.lbu / c.lhu / c.lh / c.sb / c.sh), quadrant 01 instr[15:10] 100111 (c.mul, c.zext.b / c.sext.b / c.zext.h / c.sext.h / c.not) | 30 / 65 | gen_zcb_directed.S |

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
Landing-4 review corrections (gen_critic_tb_l4.md). `cp_minstret_once` samples on the record AFTER the sequence: a record's
rvfi_ext_mhpmcounters[7] counts compressed retirements through its predecessor, so the counter of the record after the last micro-op
minus the counter of the first micro-op's record is the cm.*'s own count (the earlier expression measured the instruction before the
sequence: yes 193 of 290 on the slice-2 report, 290 of 290 now); a sequence at the very end of a run samples na. `cp_dmem_delay` is the
observed class of the data-bus responses whose rvalid fell after the record before the sequence and up to the last micro-op's record
(the sampler subscribes to the dbus agent's completed transactions; min1 = every response 1 cycle after grant, short = all in 2..4,
long = all >= 5, mixed otherwise, na when none fell in the window), not the regime knob. Every result-class coverpoint (mul, div,
alu_reg, zba_zbb, alu_imm, shift, bit_count) samples na on an rd = x0 record, where the RTL forces rvfi_rd_wdata to 0; `cp_addi_wrap`
is recomputed from rs1 and the immediate; `cp_divisor`'s magnitude compare negates the sign-extended operand (|INT_MIN| = 2^32).
Micro-op records (rvfi_ext_expanded_insn_valid) belong to the Zcmp collector alone: the base groups never see the synthesized
`addi sp` / `li a0, 0` words. `cp_rvfi_tags_ok` is a reduced check: pc_wdata == pc_rdata on the intermediate micro-ops and a 32-bit
synthesized word on every micro-op (the plan's per-position word compare is not implemented). The GEN_FCOV summary line prints the
"no" count of each ok-coverpoint (uop_count, order, tags, minstret_once) so a silently na sample is visible. Ruling TBQ-L4-1: HINT
encodings (c.li / c.lui / c.mv / c.add / c.slli with rd = x0, c.addi with imm 0, c.nop with nzimm) count under their form's Zca bin
(their HINT semantics are CG-CMP-003's); ruling TBQ-L4-2: the result-class coverpoints carry `iff rvfi_rd_addr != 0` in the plan, which
the na sample on rd = x0 renders.

## 9. Sampler unit test (LOG-058): gen_ut_isa_cov, FCOV_SELFTEST and FCOV_QUERY

`dv/auto_dv/gen_tb/gen_tests/gen_ut_isa_cov.py` boots a program, waits for `+gen_ut_boot_retire`, and when `+gen_ut_fcov_query`
names a counter compares it with `+gen_ut_fcov_expect` (the value the program is known to produce), then issues FCOV_SELFTEST and
requires 0 failures (marker GEN_UT_ISA_COV_PASS). Bridge commands: FCOV_SELFTEST (no args; the peek word is the failure count of
gen_isa_cov.self_test(), a vector table whose rows call the classifiers directly or push synthetic RVFI records through write():
slt eq on the whole 32-bit compare, the slti boundary case, addi_wrap positive and negative from the operands, the divisor magnitude
of negative operands, the na result class on a clz x0 record against the class on a clz ra record, minstret_once yes on a synthetic
cm.push {ra} followed by a counter move of one and na when the counter did not move); FCOV_QUERY (arg0 = index; the peek word is the
counter): 0 slt eq count, 1 Zcmp sequences, 2 minstret_once misses, 3 bit-count records, 4 bit-count rd = x0 records, 5 alu_imm records,
6 uop_count misses, 7 order misses, 8 tags misses, 9 branches, 10 move pairs, 11 CSR pairs. Runs: gen_alu_directed.S with query 0
expect 84 (the eq count the corrected classifier produces), gen_zcmp_directed.S with query 1 expect 290 and query 2 expect 0,
gen_bitcnt_directed.S with query 4 expect 91 (its rd = x0 bit-count records, equal to the report's cp_rd_x0.yes), and the boot program
for the vector table alone. A self-test run's coverage database carries the synthetic samples: no proof manifest is checked against it.

Slice 3 additions. CG-CMP-007 rides the same collector: the source word's [12:10] = 011 selects the move forms, the two micro-ops
must be `addi dst, src, 0` with the register pair of their position (r1s' / a0 then r2s' / a1 for cm.mvsa01; a0 / r1s' then a1 / r2s'
for cm.mva01s), `cp_src_values` compares the two micro-ops' rs1_rdata, `cp_uop_count_ok` needs exactly two records with the tags in
order. The neighbour coverpoints use an instruction-boundary tracker (`cur_wr` / `prev_wr`: the registers written by the instruction
in progress and by the one before it, an expansion counting as one instruction; `cur_ld`: it was a load, decoded with
gen_insn_mem_access because Ibex reports rvfi_mem_rmask on non-memory records too): `cp_hazard_src` is load_prev when the previous
instruction loaded a source register of the move, alu_prev when any other instruction wrote one (a move pair included), none
otherwise; `cp_b2b` is <first>_then_<second> when the instruction immediately before is the other move form (checked at the sequence's
end) or when the record after opens the other form (checked at the flush), the neighbour before winning when both hold. The sreg fields
map as the decoder does (s0 = x8, s1 = x9, s2..s7 = x18..x23, rtl/ibex_compressed_decoder.sv:153-165; the landing-5 review's second
high caught the x(8 + r) mapping that let only s0 / s1 pairs count as well-formed). The reserved
cm.mvsa01 with r1s' == r2s' (B4) is not in the proof program: Spike refuses it (illegal instruction) while Ibex executes two moves, so
`cr_insn_equal.cm_mvsa01_yes` cannot be hit under lock-step (gen_zcmp_mv_reserved_directed.S is the retained divergence).
CG-CSR-002 is a pair tracker per CSR: a CSR-op record on one of the eight addresses with rd != x0 returns the standing value, so it
closes an open pair (sampled then) and refreshes a shadow of the value; a write (csrrw / csrrwi always; csrrs / csrrc / csrrsi / csrrci
only with rs1 or uimm != 0, the decoder demoting the rest to reads) opens a pair with the operand (rs1_rdata or the zimm), the op, rd
and the effective written value (the operand for the rw forms, old | operand or old & ~operand for the set / clear forms, old being the
record's own rd_wdata when rd != x0, else the shadow if no write intervened since the last read-back, else unknown and the field
coverpoints sample na); a second write before any read-back replaces the pair (counted as replaced). `cp_wpat` classifies the operand
against the CSR's Ibex-writable mask (mstatus 0x00221888, mie 0x7FFF0888, mtvec 0xFFFFFF00, mcounteren bit 0 and bits 2..GEN_MHPM_COUNTER_NUM+2,
the others 0): all0, all1, msb_only, legal_only (only writable bits), illegal_only (no writable bit, and the CSR has some), rand; a CSR
without writable bits has no illegal-only class, so its mixed patterns are rand (misa_legal / misa_illegal in the trace CSV are
unreachable by construction). The field coverpoints use the effective value: MPP and the four mstatus bits; mtvec mode = [1:0], lo = [7:2]
zero / nonzero, base = boot_page when [31:8] equals boot_addr[31:8] (before low / high: the boot page has bit 31 set), low when the
value < 0x1000, i.e. mtvec[31:12] == 0 (ruling L5R-2), high on bit 31, rand otherwise; mie: all_fast when every fast bit 16..30 is set, else std_fast / std_only / fast_only by
the standard (3, 7, 11) and fast groups, ro_only when only read-only bits are set, na for 0; mcounteren: all1, a single bit in the
counter field by its name (cy, tm_ro, ir, hpm3..hpm12), hi_ro when only bits above the field are set, na otherwise. `cp_mcen_gate` is
mcounteren_writable_i as the ctrl interface drives it when the write record arrives (the sampler holds the ctrl interface; the record
follows the write's commit by GEN_CSR_WRITE_TO_RVFI_OFFSET cycles, so a pin moved inside that window is read after the move); TP-PMC-057
moves the pin between writes inside one run, which is why the knob string is not used. The pair tracker is
independent of any checker (the plan's Sample line names a gen_chk_csr_readback that does not exist in this TB): the read-back values
are compared against the model by the lock-step comparator, which is what the anti-vacuity rests on. CSR addresses, the BRANCH /
SYSTEM opcodes and the mstatus bit positions come from ibex_pkg. CG-ISA-007 decodes the 32-bit B-type immediate or the CB
offset; taken = pc_wdata != pc + len; `cp_cmp_class` precedence: both_msb_eq, intmin_zero, zero_intmin, zero_ones, ones_zero, equal,
slt_ugt, sgt_ult, rand (c.beqz / c.bnez compare against x0, rs2 = 0); `cp_offset`: self (0), max_fwd (4094, 254 for the CB forms), max_bwd
(-4096 / -256), pos_rand / neg_rand; `cp_target_align` = bit 1 of pc + imm on every record (taken or not); `cp_wrap` samples only on a
taken branch and is an address-space wrap: the 33-bit signed sum pc + sext(imm) lies outside [0, 2^32) (ruling L5R-1; the earlier
literal carry-out reading counted every backward branch), so the yes bin is reachable only by code near the ends of the map
(TP-BTALU-009) and no proof program of this component hits it. `cp_offset.self` is never hit by a proof program: a taken self-branch spins until an interrupt, and no promoted manifest
declares it.

Slice 4a additions. CG-BIT-006: the index is rs2_rdata[4:0] (register forms) or instr[24:20]; `cp_rs2_upper` samples the register
forms only (all_ones before zero: 0xFFFFFFFF has a non-zero upper field); `cp_prior_bit` reads rs1_rdata at the index; `cp_binv_twice`
is a binv / binvi whose immediately preceding record was a binv / binvi with the same rd and index (any other record in between,
an expansion included, breaks the pair). CG-CMP-005: the byte / half uimm comes from instr[5] and instr[6] as the compressed decoder
assembles it; `cp_data_sign` reads bit 7 (c.lbu) or bit 15 (c.lhu / c.lh) of rvfi_mem_rdata, the extended result; `cp_addr_align` is
rvfi_mem_addr[1:0] of the half-word forms (aligned = 00 or 10); `cp_alu_operand` applies to the five ALU forms and to c.mul (the CSV
crosses c.mul with it) with the precedence zero, all_ones, bit15_set, bit7_set, bit7_clear, so `rand` is unreachable by construction
(the five classes partition every operand); the register fields 0..7 are s0, s1, a0, a1, a2, a3, a4, a5. c.mul also samples
CG-MUL-001 (both groups count it).

Evidence (dv/auto_dv/evidence/gen_tdd_fcov.md): each proof run is a lock-step run of the named operand-walk program (every
result also compared against the model), urg on its own vdb, and `ci/check_fcov_expectations.py --report-dir` on a manifest of
every coverpoint bin of the groups (`gen_fcov_proof_slice1.fcov.yaml`, `gen_fcov_proof_slice1b.fcov.yaml`: PASS, 128 and 122
bins); red: the same manifest against a run with `+gen_fcov_en=0` (no covergroup, urg writes no grpinfo.txt, the checker fails
on the missing report, round 0's failure shape) and mutant FM1 (the checker names `gen_mul_ops_cg.cp_op.c_mul` unhit). Every
bin the promoted manifests reference for these six groups (1500) exists by name in the rendered include. Known gap, not this
component's: the checker parses only `Summary for Variable` sections of urg's text report and never a `Summary for Cross`
section, whose covered rows are component tuples (LOG-054: Runtime derives the variable form); until then the proof manifests
declare coverpoint bins and the cross coverage is read from urg's per-cross `User Defined Cross Bins` summary.
