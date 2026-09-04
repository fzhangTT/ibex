# gen_multdiv_bound_props.md -- divider / multiplier FSM bound for gen_sva_multdiv (F-MUL-028) and the icache RAM timing note

Committed reference (promoted 2026-09-04 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_multdiv_bound_props.md, same content apart from this paragraph); when the working
copy changes, this copy is re-promoted, and the working copy is never copied over this one without carrying this
paragraph. The working-file names below (gen_protocol_props_draft.sv, gen_protocol_props_table.md,
gen_tp_parts_rtl_factcheck.md and gen_arch_v2_rtl_factcheck.md) are this role's own gitignored sources, named as
provenance: no claim here rests on opening one, and every RTL fact is cited to its rtl/ file and line.

Owner: rtl-arch. Date: 2026-09-03. Consumer: TB Infra (binds home, next to gen_protocol_props_draft.sv;
probe register entry). Build: opentitan configuration (RV32M = RV32MSingleCycle, gen_dut_top with
u_dut.u_ibex_core). Every RTL line cited was read on 2026-09-03. No RTL edits. ASCII only.
Column meanings as in gen_protocol_props_table.md (direction, severity, mutation class, knob, exactness).

## 1. Facts (rtl/ibex_multdiv_fast.sv unless noted)

- Enable and hold: `div_en_internal = div_en_i & ~div_hold` (:99); the FSM state, counter and
  operands update only under div_en_internal (:101-115). div_en_i = div_en_id = `instr_executing ?
  div_en_dec : 0` (rtl/ibex_id_stage.sv:734), i.e. it is 1 only while the div/rem is the executing
  instruction in ID (never while a WB load/store is outstanding, :1059-1062).
- Divide path, DIT off, denominator non-zero, or DIT on (any denominator): MD_IDLE (start cycle S,
  :426-451) -> MD_ABS_A (S+1, :453-462) -> MD_ABS_B (S+2, :465-474) -> MD_COMP for div_counter 31..1
  (S+3 .. S+33, 31 cycles, :477-483, exit when `div_counter_q == 5'd1`) -> MD_LAST (S+34, :486-499)
  -> MD_CHANGE_SIGN (S+35, :502-511) -> MD_FINISH (S+36, `div_valid = 1`, :514-519). valid_o
  (:529) is therefore high exactly in cycle S+36 and never earlier; the instruction occupies ID for
  37 cycles.
- Divide-by-zero fast path, DIT off only: `md_state_d = (!data_ind_timing_i && equal_to_zero_i) ?
  MD_FINISH : MD_ABS_A` (:434, :445) -> MD_FINISH in S+1: valid_o in cycle S+1, 2 ID cycles.
  equal_to_zero_i is the ALU's `alu_is_equal_result` on the IDLE-cycle operands 0 and -op_b
  (rtl/ibex_ex_block.sv:154; :448-449 drive the ALU), i.e. denominator == 0. Under DIT the full
  path runs and div_by_zero_q suppresses only the final sign change (:408, :437).
- No other operand dependence: sign handling (ABS_A, ABS_B, CHANGE_SIGN) is always visited,
  numerator/denominator magnitude never changes the count.
- Hold: `div_hold = ~multdiv_ready_id_i` only in MD_FINISH (:518); multdiv_ready_id_i = ready_wb_i
  (rtl/ibex_id_stage.sv:976). While the divider is enabled ready_wb_i is 1 (the WB instruction has
  completed before the divide could start, gen_tp_parts_rtl_factcheck.md X-12), so a divider hold
  is unreachable in this design; row MD-3 below asserts that argument.
- Multiplier (RV32MSingleCycle, :196-240): MUL (MD_OP_MULL) completes in its first cycle
  (`mult_valid = mult_en_i` in state MULL, :202, :210-217); MULH / MULHSU / MULHU take two cycles
  (MULL with mult_valid = 0 -> MULH with mult_valid = 1, :212-215, :219-236); mult_hold =
  ~multdiv_ready_id_i (:216, :235) is unreachable by the same argument.
- Boundary visibility: valid_o has no port. The only boundary observable is RVFI record spacing:
  with the predecessor a single-cycle non-memory instruction issued back to back, no fetch stall,
  dummy_instr_en = 0 and no mcycle/mcountinhibit write, rvfi_ext_mcycle(div record) -
  rvfi_ext_mcycle(predecessor record) = 37 (full path) or 2 (div-by-zero, DIT off); the same delta
  for MUL is 1 and for MULH-class 2 (gen_arch_v2_rtl_factcheck.md 2.2, TP-MUL items). Everything
  else needs the probe below.

## 2. Probe candidate for the bind (coverage / assertion only, no checker input)

Hierarchy: `u_dut.u_ibex_core.ex_block_i.gen_multdiv_fast.multdiv_i` (rtl/ibex_core.sv:863-867
instantiates ex_block_i; rtl/ibex_ex_block.sv:165-190 generate block gen_multdiv_fast, instance
multdiv_i). Nets: md_state_q (md_fsm_e, :91-93), div_en_i, mult_en_i, operator_i (md_op_e),
equal_to_zero_i, data_ind_timing_i, multdiv_ready_id_i, valid_o, div_counter_q, mult_state_q.
Rationale for the probe register: the bound is not visible at the boundary (section 1) and the
RTL's own assertions cover only the state encoding (IbexMultDivStateValid, :532-534) and the
idle-on-ready relation (rtl/ibex_ex_block.sv sva_multdiv_fsm_idle, rtl/ibex_core.sv:2441 commented
out). Probe-register row P-MD (dv/auto_dv/docs/gen_probe_register.md, status proposed, assertion and coverage only; the Critic rules), assigned by TB Infra 2026-09-03 09:3xZ; gen_sva_multdiv is integrated in gen_binds.sv when the binds landing opens after T-068. The property reads the ID-side enable
(div_en_i) rather than the decoder, so it does not depend on an RTL decode net for its expectation.

## 3. Property table

| id | rule | cite | RTL locus protected | direction | severity | mutation class | knob | exactness | TB checker twin |
|---|---|---|---|---|---|---|---|---|---|
| MD-1 sva_div_full_bound | a divide/remainder start (md_state_q == MD_IDLE && div_en_i && operator_i inside {MD_OP_DIV, MD_OP_REM}) that does NOT take the fast path (!(equal_to_zero_i && !data_ind_timing_i)) reaches md_state_q == MD_FINISH with valid_o exactly 36 cycles later, and valid_o is 0 in the 35 cycles between | rtl/ibex_multdiv_fast.sv:426-519, :529 | divider iteration count (div_counter init 5'd31, exit at 5'd1), state sequence | DUT | assert | init `5'd31` -> `5'd30` (valid one cycle early); `div_counter_q == 5'd1` -> `== 5'd0` (one cycle late); MD_LAST -> MD_FINISH skipping CHANGE_SIGN | +gen_chk_sva_multdiv | exact 36 | none (RVFI delta 37 only under the section 1 conditions; ctr_hpm div_wait exact class counts 36 stalls) |
| MD-2 sva_div_zero_fast | a divide/remainder start with equal_to_zero_i && !data_ind_timing_i reaches MD_FINISH with valid_o in the next cycle | rtl/ibex_multdiv_fast.sv:434, :445 | divide-by-zero early-out | DUT | assert | force the select to MD_ABS_A (early-out lost: 37 cycles, D11 doc says 2) | +gen_chk_sva_multdiv | exact 1 | none |
| MD-2b sva_div_zero_dit_full | a divide/remainder start with equal_to_zero_i && data_ind_timing_i does NOT take the fast path (MD-1 applies) | rtl/ibex_multdiv_fast.sv:434, :445; doc/03_reference/security.rst data-independent timing | the DIT guard on the early-out (SEC_CM: CORE.DATA_REG_SW.SCA) | DUT | assert | drop `!data_ind_timing_i &&` from the select (a timing side channel under DIT) | +gen_chk_sva_multdiv | exact 36 | TP-DIT items on div latency (RVFI delta 37 under DIT) |
| MD-3 sva_div_no_hold | md_state_q == MD_FINISH implies multdiv_ready_id_i (div_hold never asserted while the divider is enabled) | rtl/ibex_multdiv_fast.sv:518; rtl/ibex_id_stage.sv:734, :976, :1059-1062 | the X-12 unreachability argument (gen_hierarchy_map.md H-D3) | DUT | assert (expected never to fire; a failure is a finding for rtl-arch, not a DUT bug by itself) | none reachable by a single RTL edit inside the divider; the negative control is the assertion disabled | +gen_chk_sva_multdiv | exact | none |
| MD-4 sva_div_seq | from MD_IDLE the only successors are MD_ABS_A or MD_FINISH; MD_ABS_A -> MD_ABS_B -> MD_COMP; MD_COMP -> MD_COMP or MD_LAST; MD_LAST -> MD_CHANGE_SIGN -> MD_FINISH -> MD_IDLE (state holds only when div_en_internal is 0) | rtl/ibex_multdiv_fast.sv:426-525 | state transition arcs (the RTL's IbexMultDivStateValid covers encoding only) | DUT | assert | any arc swap (for example MD_LAST -> MD_FINISH) | +gen_chk_sva_multdiv | exact | none |
| MD-5 sva_mul_bound | mult_en_i in state MULL with operator_i == MD_OP_MULL gives valid_o in the same cycle; with a MULH-class operator valid_o is 0 in that cycle and 1 in the next (state MULH) | rtl/ibex_multdiv_fast.sv:196-240 | single-cycle multiplier result timing | DUT | assert | `mult_valid = mult_en_i` -> 0 in MULL (MUL hangs); MULH state mult_valid -> 0 | +gen_chk_sva_multdiv | exact 0 / 1 | RVFI delta 1 / 2 under the section 1 conditions |
| MD-C1 cov_div_full_seen | cover: an MD-1 antecedent | - | - | - | cover | - | - | - | - |
| MD-C2 cov_div_zero_fast_seen | cover: an MD-2 antecedent | - | - | - | cover | - | - | - | - |
| MD-C3 cov_div_zero_dit_seen | cover: an MD-2b antecedent (needs cpuctrlsts.data_ind_timing = 1 and a zero denominator) | - | - | - | cover | - | - | - | - |
| MD-C4 cov_div_hold_attempt | cover: md_state_q == MD_FINISH && !multdiv_ready_id_i (expected 0 hits: the H-D3 / X-12 evidence for the exclusion file, class EC-4 style) | - | - | - | cover | - | - | - | - |

## 4. SV sketch (bind target: the multdiv_i instance; macros as in gen_protocol_props_draft.sv)

```
// gen_sva_multdiv: bound into u_dut.u_ibex_core.ex_block_i.gen_multdiv_fast.multdiv_i
// (ports/nets of ibex_multdiv_fast: clk_i, rst_ni, div_en_i, mult_en_i, operator_i,
//  equal_to_zero_i, data_ind_timing_i, multdiv_ready_id_i, valid_o, md_state_q, mult_state_q).
localparam int unsigned GEN_DIV_FULL_CYCLES = 36;  // MD_IDLE -> MD_FINISH, rtl/ibex_multdiv_fast.sv:426-519
localparam int unsigned GEN_DIV_ZERO_CYCLES = 1;   // MD_IDLE -> MD_FINISH fast path, :434/:445

wire div_start = (md_state_q == MD_IDLE) && div_en_i &&
                 (operator_i inside {MD_OP_DIV, MD_OP_REM});
wire div_fast  = equal_to_zero_i && !data_ind_timing_i;

`P_ASSERT(sva_div_full_bound,  div_start && !div_fast |-> !valid_o [*GEN_DIV_FULL_CYCLES] ##0 1'b1
                                                   ##1 (md_state_q == MD_FINISH) && valid_o)   // DUT
`P_ASSERT(sva_div_zero_fast,   div_start &&  div_fast |-> ##GEN_DIV_ZERO_CYCLES (md_state_q == MD_FINISH) && valid_o) // DUT
`P_ASSERT(sva_div_no_hold,     (md_state_q == MD_FINISH) |-> multdiv_ready_id_i)                // DUT (X-12 argument)
`P_ASSERT(sva_div_seq_idle,    (md_state_q == MD_IDLE) && div_en_i |=> md_state_q inside {MD_ABS_A, MD_FINISH}) // DUT
`P_ASSERT(sva_div_seq_last,    (md_state_q == MD_LAST) && div_en_i |=> (md_state_q == MD_CHANGE_SIGN))          // DUT
`P_ASSERT(sva_div_seq_sign,    (md_state_q == MD_CHANGE_SIGN) && div_en_i |=> (md_state_q == MD_FINISH))        // DUT
`P_ASSERT(sva_mul_single,      mult_en_i && (mult_state_q == MULL) && (operator_i == MD_OP_MULL) |-> valid_o)   // DUT
`P_ASSERT(sva_mulh_two,        mult_en_i && (mult_state_q == MULL) && (operator_i inside {MD_OP_MULH})
                               |-> !valid_o ##1 (mult_state_q == MULH) && valid_o)                               // DUT
`P_COVER(cov_div_full_seen,    div_start && !div_fast)
`P_COVER(cov_div_zero_fast_seen, div_start && div_fast)
`P_COVER(cov_div_zero_dit_seen, div_start && equal_to_zero_i && data_ind_timing_i)
`P_COVER(cov_div_hold_attempt, (md_state_q == MD_FINISH) && !multdiv_ready_id_i)   // expected 0 hits
```

Notes for integration: the antecedent of sva_div_full_bound holds div_en_i implicitly through the
FSM (the state cannot advance without it), so the consequent needs no `throughout`; if TB Infra
prefers a windowed form, `##[GEN_DIV_FULL_CYCLES:GEN_DIV_FULL_CYCLES]` is the same thing. The
mulh operator set: MD_OP_MULH covers MULH/MULHSU/MULHU through signed_mode_i (:219-236), so one
enum value. Mutation evidence per trust-triad rule 2: the mutations named in the table are inside
rtl/ibex_multdiv_fast.sv and are caught only by these properties (the ISA comparator sees a correct
result either way for MD-1/MD-2b timing mutations; it would ALSO catch a wrong result, so pick the
counter-init mutation for MD-1 to keep the other checkers inert).

## 5. ICache RAM timing (TB Infra ask 2)

ibex_top wraps the icache RAMs in prim_ram_1p_scr (rtl/ibex_top.sv:686-745: tag_bank / data_bank
per way, EnableParity = 0, NumAddrScrRounds = 2, rvalid_o / gnt_o / raddr_o / rerror_o left
unconnected). vendor/lowrisc_ip/ip/prim/rtl/prim_ram_1p_scr.sv: writes are delayed by one cycle
into a holding register (:124-130, wdata_q :301, :474); a read that arrives while a write to the
SAME address is pending returns the held write data through the collision path (:162-203,
:388-391), and the pending write is committed as soon as no read is incoming (:365-368); read data
is valid the cycle after req (rvalid_q, :377-385) and unscrambled combinationally on the way out
(:297-335). Net effect at the icache ports: read data the cycle after `req & ~write`, and a read
always observes the most recent write to its address, exactly what a plain prim_ram_1p with the
write at the request edge gives. The core never looks at rvalid_o, so no handshake difference is
visible either. TB Infra's plain model is therefore equivalent for everything the core can observe;
the only scr-specific behaviours (key-dependent scrambling, wr_collision_o, alert_o on MuBi faults)
are ibex_top test-equipment concerns outside the DUT. This confirms gen_interface_inventory.md
section 5 from the RTL, not by inference from the boots-and-retires run.
