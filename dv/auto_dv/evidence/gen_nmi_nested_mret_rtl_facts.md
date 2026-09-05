# NMI mode, a nested trap inside the handler, and the trap vector

Design facts for the fix-3 NMI red on gen_ut_irq_nmi_long. No RTL change is proposed or made. Every
gating term is quoted and line-cited. Classification of the hazard in section 6 is the DV Lead's.

## 1. nmi_mode_q has exactly one clear, and no term says WHICH mret

Three assignments to nmi_mode_d exist in rtl/ibex_controller.sv. The default hold at :574. The set at
:745, reached under `if (irq_nm && !nmi_mode_q)` at :736, where `irq_nm = irq_nm_ext_i | irq_nm_int`
(:487). The clear at :959, `nmi_mode_d = 1'b0`, reached in the FLUSH state (:816) on the else branch
of exc_req_q (:952), under `if (mret_insn)` (:954) and `if (nmi_mode_q)` (:958).

No term anywhere distinguishes the NMI handler's own mret from the mret of a handler nested inside it.
The FIRST mret executed while nmi_mode_q is set clears NMI mode.

The same register steers the CSR side. `nmi_mode_o = nmi_mode_q` (:1008) drives nmi_mode_i, and
csr_restore_mret_i branches on it at rtl/ibex_cs_registers.sv:967. So that first mret also consumes
the recoverable-NMI restore: mpie from mstack (:969), mpp from mstack (:970), mepc from mstack_epc_q
(:972), mcause from mstack_cause_q (:974). The other branch (:975-978) sets mpie to 1'b1 and mpp to
PRIV_LVL_U.

## 2. mstack is captured on every trap, not only on an NMI

`mstack_en = 1'b1` (:933) sits in the csr_save_cause_i arm with no NMI qualifier. It captures
mstack_d.mpie = mstatus_q.mpie, mstack_d.mpp = mstatus_q.mpp, mstack_epc_d = mepc_q and
mstack_cause_d = mcause_q (:752-755), all pre-update values. A synchronous exception taken inside an
NMI handler therefore overwrites the frame the NMI entry wrote.

## 3. The MIE ledger through both mrets

Let M0 be mstatus.mie immediately before the NMI is taken.

1. NMI entry: `mstatus_d.mie = 1'b0` (:924), `mstatus_d.mpie = mstatus_q.mie` = M0 (:926);
   nmi_mode_d = 1 (controller:745).
2. Trap inside the handler: the same two lines run again. mie is already 0, so mpie becomes 0, and
   mstack is rewritten with the NMI's frame, so mstack.mpie becomes M0. nmi_mode_q stays 1, because a
   synchronous exception is not irq_nm (controller:487) so :736 does not re-enter.
3. The nested mret: `mstatus_d.mie = mstatus_q.mpie` = 0 (:956); nmi_mode_d = 0 (controller:959); the
   mstack branch restores mpie to M0 (:969) and mepc to mstack_epc_q (:972).
4. A csrw in the handler that sets mie to 1 takes effect here, with nmi_mode_q already 0.
5. The outer mret: `mstatus_d.mie = mstatus_q.mpie` (:956), which is M0. nmi_mode_i is now 0, so the
   else branch runs, setting mpie to 1'b1 and mpp to PRIV_LVL_U (:977-978).

The handler's csrw is discarded at step 5: MIE ends at M0, not at the value the handler wrote. When
M0 is 0 the line stays masked afterwards. When M0 is 1, MIE is 1 after the outer mret and this ledger
does NOT withhold the line.

## 4. What is takeable inside the handler after the nested mret

handle_irq is `~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q & (irq_nm | (irq_pending_i &
irq_enabled)) & !(instr_gets_expanded_i == INSTR_EXPANDED_COMMIT)` (controller:498-500), with
`irq_enabled = csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U)` (:490). irq_pending_i comes from
`irq_pending_o = |irqs_o` and `irqs_o = mip & mie_q` (cs_registers:1044-1045), so the line's own mie
CSR bit is required as well as MIE.

Because nmi_mode_q clears at the NESTED mret rather than the outer one, a held and enabled regular
line is takeable from step 4 onward, inside the handler. A fixture that expects the line to be
refused until the outer mret is expecting something the design does not do.

## 5. The trap vector is forced vectored with a 256-byte base

This is the term that decides where any of the above executes.

A software write to mtvec keeps only bits [31:8] of the written data:
`mtvec_d = csr_mtvec_init_i ? {boot_addr_i[31:8], 6'b0, 1'b0, ~(...)} : {csr_wdata_int[31:8], 6'b0,
1'b0, ~((BaseIsa == BaseIsaRV32IorCHERIoT) & (cheriot_enable_i == IbexMuBiOn))}`
(rtl/ibex_cs_registers.sv:739-743). On a non-CHERIoT configuration the final bit is 1. The comment at
:737-738 states the intent: "mtvec.MODE set to vectored" and "mtvec.BASE must be 256-byte aligned".
The readback returns the stored value, `csr_rdata_int = mtvec_q` (:473), so a csrw of 0x800000c0 reads
back as 0x80000001.

The use path consults no MODE bit. `EXC_PC_IRQ: exc_pc = {csr_mtvec_i[31:8], 1'b0, irq_vec, 2'b00}`
(rtl/ibex_if_stage.sv:225-228, non-CHERIoT branch) and `EXC_PC_EXC: exc_pc = {csr_mtvec_i[31:8],
8'h00}` (:222-224). Interrupts always vector; exceptions always land on the base.

So with a base of 0x80000000: an external NMI, whose lower_cause is 5'd31 (rtl/ibex_pkg.sv:355-356),
vectors to 0x8000007C; an internal NMI is forced to the same index by if_stage:216-218; a machine
external interrupt, lower_cause 5'd11 (pkg:353-354), vectors to 0x8000002C; and a synchronous
exception lands on 0x80000000. No trap can reach an arbitrary handler address chosen by the program.

## 6. The nested-exception hazard, stated as a fact

The comment at controller:494-495 gives the intent of the NMI-mode gate: interrupts including NMI are
ignored "while in NMI mode (nested NMIs are not supported, NMI has highest priority and cannot be
interrupted by regular interrupts)".

A synchronous exception taken inside an NMI handler is not blocked by any term in handle_irq or in the
NMI entry condition, since neither is a term on synchronous exceptions. Taking one overwrites the
mstack frame (section 2) and causes NMI mode to exit at that nested handler's mret rather than the NMI
handler's own (section 1), which also consumes the recoverable-NMI restore early.

Whether that is a constraint software must observe or a hardware defect is a classification call. It
is left to the DV Lead and is not made here.

## 7. Two reads that separate design from stimulus

Read mtvec back after the program's csrw. A value of 0x80000001 rather than the written address
confirms section 5 and means the program's intended handler never runs, in which case nothing in
sections 1 to 4 is reached at all.

Read mstatus.mie and the mie CSR immediately after each mret. Section 3 predicts mie equal to the
handler's written value between the nested and outer mrets, and equal to M0 after the outer mret.

## 8. Where an mret lands, and what the mstack restore does not affect

The jump and the CSR restore happen in the same cycle, and only one of them decides the destination.

In FLUSH under `if (mret_insn)` the controller asserts `pc_mux_o = PC_ERET` and `pc_set_o = 1'b1`
(rtl/ibex_controller.sv:955-956) and `csr_restore_mret_id_o = 1'b1` (:957) together. That restore
signal reaches the CSRs with no register in the path: rtl/ibex_id_stage.sv:691 passes it out,
rtl/ibex_core.sv:751 wires it to csr_restore_mret_id, and :1538 drives cs_registers' csr_restore_mret_i
with the same net.

The destination is a single unmuxed wire carrying the register's current value. `csr_mepc_o = mepc_q`
(rtl/ibex_cs_registers.sv:1028) is the only assignment to that port; core:1502 carries it to csr_mepc
and :620 into the IF stage, where `PC_ERET: fetch_addr_n = csr_mepc_i` (rtl/ibex_if_stage.sv:246).

So an mret lands at whatever mepc_q holds in that cycle: the value a handler's csrw left if it wrote
one, otherwise the value the trap saved. The mstack restore's own write, `mepc_en = 1'b1` and
`mepc_d = mstack_epc_q` (:971-972), is a write of mepc_d and lands at the end of that same cycle, so
it changes only later reads and CANNOT affect this jump.

Two consequences worth stating explicitly, because both have been derived the other way. A nested
handler's mret returns to its own return point, not to the frame the mstack restore is installing;
and after that mret the architectural mepc holds the outer frame, so a later mret uses the outer
return point and any handler read of mepc sees the outer frame rather than its own.

A handler that never begins executing produces no mret at all, and none of this applies to it. Where a
trap begins executing is section 5.

## 9. The documented constraint is broader than the controller comment

The controller comment at :494-495 gives the NMI-mode gate's intent as interrupts being ignored "while
in NMI mode (nested NMIs are not supported, NMI has highest priority and cannot be interrupted by
regular interrupts)". It speaks only about interrupts.

doc/03_reference/exception_interrupts.rst is broader. Line 175 states "Nesting of
interrupts/exceptions in hardware is not supported", which covers synchronous exceptions as well.
Line 176 adds that the nonstandard mstack CSRs exist "only to support recoverable NMIs" and :177 that
they are not software-accessible. Line 178 states that while handling an NMI all interrupts are
ignored independent of mstatus.MIE, and :179 separately states that nested NMIs are not supported.

So the document forbids the case in section 6 and the comment does not mention it. The classification
of that case remains the DV Lead's; this section only records that the two texts differ in scope and
which one is broader.

## 10. Not claimed

No waveform was read for any statement here; every line is from the RTL at the commit this file is
recorded against. No claim is made about which instruction in any particular fixture writes any
particular register, nor about what mtval holds at any point.
