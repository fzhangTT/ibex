# B10 / B16 RTL facts: the two ratings marked pending rtl-arch confirmation

Owner: rtl-arch. Written 2026-09-08T02:04Z from the RTL in this clone, verified at HEAD
d04ada46f1688ec8ab7314c9f2943cacb2b30121 (the reading was taken at 9f14230e566a48b8c430ed5dca72a59c58290fd3 and
`git diff 9f14230..d04ada4 -- rtl/ doc/` is empty, so no cited RTL or documentation line moved; the bug log
reached v2b in that span and is cited here by entry id, never by line).
Files read: rtl/ibex_load_store_unit.sv, rtl/ibex_core.sv, rtl/ibex_id_stage.sv, rtl/ibex_wb_stage.sv,
rtl/ibex_controller.sv, rtl/ibex_cs_registers.sv, rtl/ibex_if_stage.sv, rtl/ibex_icache.sv, rtl/ibex_pkg.sv,
plus the debug specification in this clone (tools/specs/riscv-debug-spec/xml/core_registers.xml, an allowed
untracked local copy, docs/dv/FENCE.md).

Configuration this note is written for: opentitan (ibex_configs.yaml:41-60), so WritebackStage 1, SecureIbex 1,
DbgTriggerEn 1, BranchPredictor 0, ICache 1, and therefore MemECC = SecureIbex = 1 (rtl/ibex_top.sv:41).
In the team's testbench DbgHwBreakNum = 1 (dv/auto_dv/tb/gen_dut_top.sv:59) and cheriot_enable_i is tied to
IbexMuBiOff (`localparam ibex_mubi_t CheriotEnable = IbexMuBiOff;` dv/auto_dv/tb/gen_dut_top.sv:206, passed at
:284), so every `(cheriot_enable_i == IbexMuBiOn)` term quoted below is 0 and is named where it gates.

Also read, for Section 1.5 only: tb-infra's B16 arming-count landing of 2026-09-08 (commit e7e7a94) -- its
record dv/auto_dv/evidence/gen_tdd_b16_knob.md, the retained logs under
dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l64_b16_*, the waveform that its own
gen_fu_l64_b16_waveform.log names, and the out-tree exports named in 1.5.3. Those are tb-infra's artefacts;
this note reads them and edits none.

Scope: the two open questions the DV Lead's ratings rest on, for B16 and B10 of dv/auto_dv/docs/gen_bug_log.md
(entries B16 and B10; rating definitions in its Section 0.2). RTL is read-only; this note states behaviour and
recommends a rating. The bug log is the DV Lead's file and the rating is the DV Lead's to record.

## 1. B16: the cycle order of rd write, alert and internal NMI, and whether the merged word is consumable

The question asked: the cycle-level order between the rd write-back of the merged word, the alert assertion and
the internal NMI request; and whether a dependent instruction can retire using the written rd before the NMI
redirects. The DV Lead's P2 rating rests on the merged word "not being usable before the NMI is taken".

### 1.1 Where the integrity term is, and where it is not

The integrity check is per response beat and is combinational from the incoming response data:

    if (MemECC) begin : g_mem_rdata_ecc                                  (rtl/ibex_load_store_unit.sv:376)
      logic [1:0] ecc_err;                                                                          (:377)
      prim_secded_inv_39_32_dec u_data_intg_dec (
        .data_i     (data_rdata_buf),                                                               (:386)
        .data_o     (),                                                                             (:387)
        .err_o      (ecc_err)                                                                       (:389)
      );
      assign data_intg_err = |ecc_err;                                                              (:393)

The decoder's corrected word is discarded at :387 (`.data_o ()`), so the data the core uses is the raw,
uncorrected `data_rdata_i`. That matters for what lands in rd below.

First half of a misaligned load, state WAIT_RVALID_MIS (:503). On the first response:

    lsu_err_d = data_bus_err_i | pmp_err_q;                                                         (:514)
    rdata_update = ~data_we_q;                                                                      (:516)
    ls_fsm_ns = data_gnt_i ? IDLE : WAIT_GNT;                                                       (:518)

:514 is the whole of the first-half status. It has no `data_intg_err` term. The first beat's bytes are captured
into the merge register at :516 through

    end else if (rdata_update) begin
      rdata_q <= data_rdata_i[31:8];                                                            (:234-235)

and are merged with the second beat by

    2'b01:   rdata_w_ext = {data_rdata_i[ 7:0], rdata_q[31:8]};                                     (:272)
    2'b10:   rdata_w_ext = {data_rdata_i[15:0], rdata_q[31:16]};                                    (:273)
    2'b11:   rdata_w_ext = {data_rdata_i[23:0], rdata_q[31:24]};                                    (:274)

The register-file write valid carries the integrity term of the completing beat only:

    assign data_or_pmp_err = lsu_err_q | data_bus_err_i | pmp_err_q |
                             ((cheriot_enable_i == IbexMuBiOn) &
                              (cheriot_err_q | (resp_is_cap_q & cap_lsw_err_q)));               (:688-690)
    assign lsu_rdata_valid_o = (ls_fsm_cs == IDLE) & data_rvalid_i & ~data_or_pmp_err & ~data_we_q &
                               ~data_intg_err;                                                  (:697-698)

Every term of :697-698 for the reproducer's stimulus (data_err_i = 0 on both beats, first beat's check bits
corrupted, second beat clean): `ls_fsm_cs == IDLE` is true in the second beat's response cycle by :518;
`data_rvalid_i` is the second response; `data_or_pmp_err` is 0 because lsu_err_q came from :514 which carries no
integrity term, `data_bus_err_i` and `pmp_err_q` are 0 by the stimulus, and the two cheriot terms are 0 by the
IbexMuBiOff tie; `~data_we_q` is a load; `~data_intg_err` is the second beat, which is clean. So the write is
enabled and its data is

    assign lsu_rdata_o = data_rdata_ext;                                                            (:711)

which is the merged word of :272-274, uncorrected. In the core the write reaches the register file through

    assign rf_we_lsu     = lsu_rdata_valid   & (outstanding_load_wb  | expecting_load_resp_id);  (rtl/ibex_core.sv:1186)

in the `if (SecureIbex) begin : g_check_mem_response` arm (:1181), and the WB stage selects the LSU word with
`assign rf_wdata_wb_mux_we[1] = rf_we_lsu_i;` (rtl/ibex_wb_stage.sv:220) at the address `rf_waddr_wb_o =
rf_waddr_wb_q` (:181).

Control case, for completeness: if the SECOND beat is the corrupted one, `~data_intg_err` in :698 is 0 and the
write is suppressed, which is the behaviour doc/03_reference/security.rst:88 describes.

### 1.2 The order: alert first, NMI request at or before the rd write

The alert is combinational from the erroring beat:

    assign load_resp_intg_err_o  = data_intg_err & data_rvalid_i & ~data_we_q;         (rtl/ibex_load_store_unit.sv:756)
    assign alert_major_bus_o = lsu_load_resp_intg_err | lsu_store_resp_intg_err | instr_intg_err;
                                                                                       (rtl/ibex_core.sv:1353)

so with the FIRST beat corrupted the alert pulses in the first beat's response cycle. Call that cycle N.

The internal NMI is one register deep behind the same event. In the ID stage
`assign mem_resp_intg_err = lsu_load_resp_intg_err_i | lsu_store_resp_intg_err_i;` (rtl/ibex_id_stage.sv:613),
passed to the controller at :669. In the controller's `if (MemECC) begin : g_intg_irq_int` block (:393):

    end else if (mem_resp_intg_err_i) begin                                        (rtl/ibex_controller.sv:413)
      mem_resp_intg_err_addr_d        = lsu_addr_last_i;                                                          (:416)
      mem_resp_intg_err_irq_set       = 1'b1;                                                                     (:417)
    assign mem_resp_intg_err_irq_pending_d =
      (mem_resp_intg_err_irq_pending_q & ~mem_resp_intg_err_irq_clear) | mem_resp_intg_err_irq_set;
                                                                                                (:421-422)
      mem_resp_intg_err_irq_pending_q <= mem_resp_intg_err_irq_pending_d;                           (:429)
    assign irq_nm_int       = mem_resp_intg_err_irq_pending_q;                                                    (:436)

So irq_nm_int is high from cycle N+1 and stays high until `entering_nmi & !irq_nm_ext_i` clears it (:410-412,
`assign entering_nmi = nmi_mode_d & ~nmi_mode_q;` :399). It reaches the request through

    assign irq_nm = irq_nm_ext_i | irq_nm_int;                                                      (:487)
    assign irq_enabled = csr_mstatus_mie_i | (priv_mode_i == PRIV_LVL_U);                           (:490)
    assign handle_irq = ~debug_mode_q & ~debug_single_step_i & ~nmi_mode_q &
        (irq_nm | (irq_pending_i & irq_enabled)) &
        !(instr_gets_expanded_i == INSTR_EXPANDED_COMMIT);                                      (:498-500)

Every term of :498-500 in the reproducer's M-mode program: not in debug mode, dcsr.step 0, not already in NMI
mode, `irq_nm` = 1 from irq_nm_int, and no Zcmp commit micro-op in ID. `irq_enabled` does not gate it: irq_nm
sits OUTSIDE the `(irq_pending_i & irq_enabled)` parenthesis, so mstatus.MIE never masks this NMI.

The earliest cycle the rd write can happen is N+1, because :518 leaves WAIT_RVALID_MIS on the first response and
:697 requires `ls_fsm_cs == IDLE`. mem_resp_intg_err_irq_pending_q is set at the same clock edge (:429). So the
order is fixed and is not a race:

    cycle N    : first beat response, bad check bits. alert_major_bus_o pulses (core:1353). No rd write
                 (:697 needs IDLE, the FSM is in WAIT_RVALID_MIS).
    cycle N+1  : irq_nm_int and handle_irq are high (:436, :498-500). Earliest possible second-beat response,
                 i.e. earliest possible rd write of the merged word (:697-698).
    cycle M>=N+1: second beat response, rd written with the merged word.

The alert therefore precedes the rd write by at least one cycle, and the NMI request precedes it or coincides
with it. Neither is ever later than the write. This is stronger than "the alert and NMI still fire", which is
what the bug log's Notes say today.

### 1.3 One further instruction can retire on the merged word, and at most one

The redirect is a separate question from the request, and it is late. In DECODE:

    if ((enter_debug_mode || handle_irq) && (stall || id_wb_pending)) begin
      halt_if = 1'b1;                                                              (rtl/ibex_controller.sv:701)
    end
    if (!stall && !special_req && !id_wb_pending) begin                                             (:704)
      ...
      end else if (handle_irq) begin
        ctrl_fsm_ns = IRQ_TAKEN;                                                                    (:713)
        halt_if     = 1'b1;                                                                         (:719)

with

    assign id_wb_pending = instr_valid_i | ~ready_wb_i;                                             (:296)
    assign stall = stall_id_i | stall_wb_i;                                                        (:1017)
    assign id_in_ready_o = ~stall & ~halt_if & ~retain_id;                                         (:1020)

`pc_set_o` and `csr_save_cause_o` are asserted in IRQ_TAKEN (:730, :733), not in DECODE, so no redirect happens
while :704 is false. :296 makes :704 false for as long as any instruction is valid in ID. And halt_if only feeds
:1020, the acceptance of a NEW instruction; it does not clear or stall the instruction already in ID, whose
liveness is `assign instr_valid_clear_o = ~(stall | retain_id) | flush_id;` (:1027).

Nothing kills that instruction either. Its execute condition is

    assign instr_kill = instr_fetch_err_i | wb_exception | id_exception_nc | ~controller_run;
                                                                                (rtl/ibex_id_stage.sv:1033-1036)
    assign instr_executing = instr_valid_i & ~instr_kill & ~stall_ld_hz & ~outstanding_memory_access;
                                                                                                (:1059-1062)

`controller_run` is 1 throughout DECODE (`controller_run_o = 1'b1;` rtl/ibex_controller.sv:655) and the
integrity error is deliberately NOT a writeback exception:

    assign load_err_o  = data_or_pmp_err & ~data_we_q & lsu_resp_valid_o;              (rtl/ibex_load_store_unit.sv:746)
      // Integrity errors are their own category for timing reasons. load_err_o is factored directly
      // into data_req_o to enable synchronous exception on load errors without performance loss (An
    // ...
      // factored into data_req_o there would have to be a stall cycle between all back to back loads.
      // The data_intg_err signal is generated combinatorially from the incoming data_rdata_i. Were it
      // to be factored into load_err_o there would be a feedthrough path from data_rdata_i to
                                                                                                              (:748-755)
    assign wb_exception_o = load_err_q | store_err_q | load_err_i | store_err_i
                          | ((cheriot_enable_i == IbexMuBiOn) & cheriot_wb_err_i);
                                                                             (rtl/ibex_controller.sv:336-337)

so `wb_exception` is 0 for this event and `instr_kill` stays 0.

A dependent instruction cannot get the load data by forwarding, so it waits in ID and then reads the register
file:

    // If instruction is read register that writeback is writing forward writeback data to read
    // data. Note this doesn't factor in load data as it arrives too late, such hazards are
    // resolved via a stall (see above).                                       (rtl/ibex_id_stage.sv:1114-1116)
    assign rf_rdata_a_fwd = rf_rd_a_wb_match & rf_write_wb_i ? rf_wdata_fwd_wb_i : rf_rdata_a_i;    (:1117)
    assign stall_ld_hz = outstanding_load_wb_i & (rf_rd_a_hz | rf_rd_b_hz);                         (:1120)

and the forwarded value is the flopped ALU result, not the memory word, by the WB stage's own statement
`// The flopped rf_wdata_wb_q is used rather than rf_wdata_wb_o as the latter includes read data from memory
that returns too late to be used on the forwarding path.` with
`assign rf_wdata_fwd_wb_o = wb_is_cheriot_q ? cheriot_rf_wdata_q : rf_wdata_wb_q;`
(rtl/ibex_wb_stage.sv:212-215). `outstanding_load_wb_o = wb_valid_q & ((wb_instr_type_q == WB_INSTR_LOAD) | ...)`
(:193-194) drops in the cycle after the load leaves WB, because `wb_done = (wb_instr_type_q == WB_INSTR_OTHER
&& ...) | lsu_resp_valid_i` (:115-116) and `wb_valid_d = (en_wb_i & ready_wb_o) | (wb_valid_q & ~wb_done)`
(:107).

Putting those together, with the load's second response at cycle M:

    cycle M    : rd written with the merged word (:697-698 / core:1186). stall_ld_hz is still 1 for the
                 dependent instruction, because outstanding_load_wb_i is still 1 (wb_stage:193).
    cycle M+1  : outstanding_load_wb_i is 0, stall_ld_hz is 0, outstanding_memory_access is 0
                 (id_stage:1015-1016), so instr_executing is 1 and the dependent instruction executes,
                 reading rf_rdata_a_i, the register file, which now holds the merged word.
    cycle M+2  : that instruction has left ID, id_wb_pending is 0, :704 is true and the FSM goes to IRQ_TAKEN,
                 which is the first cycle pc_set_o is asserted (:729).

So the answer to the question asked is yes: one instruction can consume the merged word and retire before the
NMI redirects. The count is AT MOST one ID entry, never two, because ID is not refilled once the load is
outstanding:

    assign stall_mem = instr_valid_i & (outstanding_memory_access |
                                        ((lsu_req_dec | cheriot_lsu_req_dec) & ~lsu_req_done_i));
                                                                                (rtl/ibex_id_stage.sv:1095-1096)
    assign outstanding_memory_access = (outstanding_load_wb_i | outstanding_store_wb_i) &
                                       ~lsu_resp_valid_i;                                       (:1015-1016)

The load itself stays in ID until its SECOND request is granted, by
`assign lsu_req_done = (lsu_go | (ls_fsm_cs != IDLE)) & (ls_fsm_ns == IDLE);`
(rtl/ibex_load_store_unit.sv:632) with the ID stage's own reason recorded in its comment at
rtl/ibex_id_stage.sv:1089-1090 ("or which is unaligned and waiting to issue a second request (needs to stay in
ID for the address calculation)"). So which of the two counts applies is decided by the bus, and both are
reachable:

- ONE, when the second request is granted at or before the first response cycle N. Either the second grant
  arrives with the first response (`ls_fsm_ns = data_gnt_i ? IDLE : WAIT_GNT;` :518) or it arrived earlier and
  the FSM is in WAIT_RVALID_MIS_GNTS_DONE (:546), whose first-response arm also sets `ls_fsm_ns = IDLE;` (:561)
  with `lsu_err_d = data_bus_err_i;` (:555, again no integrity term). Either way lsu_req_done is 1 at cycle N,
  where handle_irq is still 0, so stall_mem is 0 and `id_in_ready_o` (rtl/ibex_controller.sv:1020) is 1 for that
  one cycle: the next instruction is written into ID at the end of N and is the single entry that then retires.
- ZERO, when the second request is granted later than N. Then :518 sends the FSM to WAIT_GNT (:533) and
  lsu_req_done stays 0 at N, so stall_mem holds `stall` high through N; from N+1 halt_if is asserted by
  :701 and holds :1020 low for the rest of the event. No instruction is ever accepted into ID, and the redirect
  follows the load's retirement with nothing in between.

The consumption is therefore possible but not guaranteed, and the discriminator is the second beat's grant
timing, not the program.

Two consequences worth recording because they are not in the entry today:

- If that one instruction is a STORE of the loaded register, it is performed on the bus with the corrupted
  word before the redirect. Its request is allowed because `assign lsu_req = instr_executing ? data_req_allowed
  & lsu_req_dec : 1'b0;` (rtl/ibex_id_stage.sv:732) and `assign data_req_allowed = ~outstanding_memory_access;`
  (:1019) are both satisfied at M+1. So the corruption can reach memory, not only a register.
- If that one entry is a Zcmp expansion, more than one architectural update follows, because handle_irq is
  masked while the expansion commits (`!(instr_gets_expanded_i == INSTR_EXPANDED_COMMIT)`, :500). That is the
  "more with a Zcmp sequence" clause of the earlier X-10 reading, and it applies here too.

### 1.4 What the NMI handler can see

Detectability is not in doubt. The handler gets mcause from `irq_nm_int_cause = NMI_INT_CAUSE_ECC`
(rtl/ibex_controller.sv:437) selected in IRQ_TAKEN by

    if (irq_nm && !nmi_mode_q) begin
      exc_cause_o = irq_nm_ext_i ? ExcCauseIrqNm :
                    '{irq_ext: 1'b0, irq_int: 1'b1, lower_cause: irq_nm_int_cause};             (:737-739)
      if (irq_nm_int & !irq_nm_ext_i) begin
        csr_mtval_o = irq_nm_int_mtval;                                                         (:741-742)

and mtval from `irq_nm_int_mtval = mem_resp_intg_err_addr_q` (:438), captured at :416 from `lsu_addr_last_i`.
In the first-beat case that capture happens at cycle N, and the LSU's own address register is only advanced at
the next edge, because in WAIT_RVALID_MIS `addr_update = data_gnt_i & ~(data_bus_err_i | pmp_err_q);`
(rtl/ibex_load_store_unit.sv:520) with `addr_last_d = addr_incr_req_o ? data_addr_w_aligned : data_addr;`
(:258) and `addr_last_q <= addr_last_d;` under addr_update (:263-264). So mtval names the load's own effective
address (the unaligned 4n+2 captured at the initial grant, :480), not the second word. Together with mepc from
`csr_save_if_o = 1'b1;` in IRQ_TAKEN (:732) the handler can name both the corrupted access and the resume point,
and therefore the one instruction that ran in between.

RVFI reports the write rather than a suppression, which is what makes the case testable:
`rvfi_rf_wr_suppress_wb = instr_done_wb & ~rf_we_wb_o & outstanding_load_wb & lsu_load_resp_intg_err;`
(rtl/ibex_core.sv:2384-2385) is 0 here, because at the completing beat lsu_load_resp_intg_err is 0 (the second
beat is clean) and rf_we_wb_o is asserted.

### 1.5 Measured, in tb-infra's B16 knob runs of 2026-09-08 (landing 64, commit e7e7a94)

Sections 1.1 to 1.4 were written as a static reading. While this note was being written tb-infra built the
arming-count knob the B16 entry asks for and ran it, so the reading can be graded against runs and against
a waveform. Its record is dv/auto_dv/evidence/gen_tdd_b16_knob.md (tb-infra's file, not this role's) with
the retained logs under dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l64_b16_*. Program
gen_intg_span_directed.S, the load `lw x11, 2(x10)` at 0x80000118 with x10 = 0x800002e0, so beats at
0x800002e0 and 0x800002e4 and exactly one corruption armed on the first.

#### 1.5.1 The order of Section 1.2, measured from the waveform

Section 1.2 derives the order of the alert, the internal NMI request and the rd write from the RTL alone.
All three are now measured on one run, and the derivation holds on every leg. Read from the FSDB that
gen_fu_l64_b16_waveform.log names, dv/auto_dv/out_b16waves/runs/l64_c1/waves.fsdb against
dv/auto_dv/out_b16waves/build/gen_tb/vcs_simv.daidir, seed 1, arm count 1. Times are that log's own 10 ps
unit; the rising edges in this window fall at 49500, 50500, ... 55500.

| event | what was sampled | committing edge |
|---|---|---|
| corrupted FIRST beat | data_rvalid_i high 49000-50000, data_rdata_i 0101111111 | 49500 |
| alert asserted | alert_major_bus_o high 49000-50000, one cycle wide, coincident with the response | 49500 |
| internal NMI requested | irq_nm_int and handle_irq both rise AT this edge | 49500 |
| rd written | lsu_rdata_valid, rf_we_lsu and rf_we_wb high into the edge; rf_wdata_wb 22220111 into rf_waddr_wb 0b | 54500 |
| NMI taken | nmi_mode_q rises, handle_irq falls with it | 55500 |

Against Section 1.2's cycle names, where N is the cycle in which the corrupted response is sampled: the
alert is combinational within N, irq_nm_int is high from the start of N+1 exactly as stated, the rd write
commits five cycles later, and the NMI is entered one cycle after the write.

Three things this pins that the static reading could only derive:

- The alert is exactly one cycle wide and exactly coincident with the corrupted response window. That is
  the combinational path of rtl/ibex_core.sv:1353 measured, and it agrees independently with the
  testbench's exact same-cycle property sva_alert_bus_iff_intg
  (dv/auto_dv/tb/gen_protocol_props.sv:285-286), which passed in the run.
- The NMI request precedes the rd write by a margin, not a hair. State the ORDER as the fact and the
  five-cycle MARGIN as run-specific: the lead is the second beat's response latency, so it varies with the
  bus, while the order cannot invert, because :697 needs the FSM in IDLE and the FSM cannot leave
  WAIT_RVALID_MIS before the first response that sets the pending flag.
- The leak is measured at the register-file WRITE PORT, not inferred from a trace field: rf_wdata_wb
  carries the merged word into the load's destination register at that edge.

#### 1.5.2 From the retained logs

From gen_fu_l64_b16_c1_seed1_sim.log:34 and its assertion summary at :72, and the green control
gen_fu_l64_b16_c2_seed1_*:

- The register write happens with the merged word: `[isa_rd] rd model=x11/22221111 dut=x11/22220111
  (order=8 pc=80000118 insn=00252583 ... mem=800002e2 ...)`. Section 1.1.
- The alert fires exactly once: `sva_alert_bus_seen, 141 attempts, 1 match`.
- `sva_irq_nmi_seen, 141 attempts, 0 match` in the same summary is NOT evidence about the internal NMI:
  that cover watches the external pin `irq_nm_i` (dv/auto_dv/tb/gen_protocol_props.sv:274), and the
  internal NMI has no top-level pin. Read as an NMI absence it would contradict 1.5.1, which is why it is
  named here.

From the retained sweep log gen_fu_l64_b16_sweep16.log, whose name invites one misreading worth stating:
it is SIXTEEN RUNS, eight count-1 seeds plus eight count-2 controls, not sixteen seeds.

- Suppression is 0 in all eight count-1 runs and 1 in all eight count-2 controls. That is Section 1.4's
  ext_rf_wr_suppress statement AND Section 1.1's control case (a corrupted SECOND beat does suppress the
  write) each measured eight of eight.
- The count-1 verdicts partition two seeds from six: the register comparison fires in seeds 1 and 5 only,
  the other six reporting crash_dump alone. See 1.5.4 for what that partition means, which is not what an
  earlier draft of this section said.

#### 1.5.3 The record gap, and the state of its evidence

Measured from the run directories' RVFI export, which is out-tree and NOT retained
(dv/auto_dv/out_b16knob/c1_s1..c1_s8/gen_export.txt, tb-infra's output for its eight count-1 seeds). The
Orchestrator ruled on 2026-09-08 that those eight files stay un-retained, so this table is a measurement
whose inputs a reader cannot re-derive from the tree; everything else in Section 1.5 rests on retained
files. It is kept rather than dropped because it is the only measurement of the consumption window.

| seed | records between the load and the NMI record | second beat's grant cycle | first bad response cycle |
|---|---|---|---|
| c1_s1 | 0 | 45 | 44 |
| c1_s2 | 0 | 40 | 39 |
| c1_s3 | 1 | 41 | 41 |
| c1_s4 | 1 | 43 | 45 |
| c1_s5 | 1 | 37 | 37 |
| c1_s6 | 0 | 40 | 39 |
| c1_s7 | 1 | 45 | 45 |
| c1_s8 | 1 | 41 | 42 |

What that grades, in both directions:

- The count is 0 or 1 and never 2, in eight of eight. Section 1.3's bound holds.
- Section 1.3's discriminator predicts which: one record when the second beat is granted at or before the
  first corrupted response cycle, none when it is granted later. It agrees 8 of 8, with five ones and three
  zeros, so it is graded in both directions rather than only where it predicts the common case.
- The internal NMI is real and immediate: the record after the gap carries `ext_nmi_int = 1` with
  `intr = 1`, at pc 0x8000027c in every seed.

Instrument caution, because two of this section's cycle numbers look inconsistent and are not. The export's
own cycle counter and the FSDB do NOT share an origin: for seed 1 the export puts the corrupted response
and the second grant at 44 and 45, while 1.5.1 puts the same two events at 49500 and 50000, which is
cycles 49 and 50 by that file's edges. Both are right about their own origin and they agree on the only
thing that classifies the seed, that the second grant follows the corrupted response by one cycle. Quote
the RELATION, never the absolute number, when crossing from one instrument to the other.

#### 1.5.4 Two qualifications the runs add, one of them a correction to this section

- The SLOT is measured and the CONSUMPTION is not. The intervening record in the five gap-of-one seeds is
  the same one every time, order 9 at pc 0x8000011c, insn 0x0001 (c.nop), rd x0. This program puts a nop
  after the load, not a dependent instruction, so Section 1.3's consequences about a dependent instruction
  and about a dependent store reaching memory stay static readings. Closing them needs one directed variant
  with a dependent load-use instruction, and separately a dependent store, in that slot, run at a
  gap-of-one seed (3, 4, 5, 7 or 8).
- rd receives the CLEAN merged word 0x22221111 in six of the eight seeds, and a wrong word only in c1_s1
  (0x22220111) and c1_s5 (0x22221911). AN EARLIER DRAFT OF THIS SECTION EXPLAINED THAT AS "the injection
  landed in the seven check bits alone", WHICH IS WRONG, and landing 64's own account is right: of the 39
  bits of the first response ({intg[6:0], word[31:0]}) only 16 can change the merged value. The terms:
  `rdata_q` is declared `logic [31:8]` (rtl/ibex_load_store_unit.sv:91) and captures `data_rdata_i[31:8]`
  (:235), and at this program's offset of 2 the merge is `{data_rdata_i[15:0], rdata_q[31:16]}` (:273), so
  the only first-beat bits reaching rd are word[31:16]. The other 23 positions, the seven check bits AND
  word[15:0], raise the integrity error and leave the merged word clean. So the rule is "any bit the offset
  does not merge in", not "check bits only". The count is offset-specific and would be cited wrongly
  otherwise: it is the width of the first-beat slice the offset selects, `rdata_q[31:8]` at offset 1,
  `[31:16]` at offset 2, `[31:24]` at offset 3 (:272-274), so 24, 16 or 8 data-bit positions of 39.
  WHAT FOLLOWS, and it is why the wording matters: the register VALUE is not a reliable witness for this
  class, because a data-bit corruption in the unmerged half is as invisible in rd as a check-bit one. The
  reliable witness is the missing suppression, which is eight of eight. Landing 64 reaches the same
  conclusion from the other side, its module assertion firing 8 of 8 against the register comparison
  firing 2 of 8. Section 1.1's "uncorrected" is right either way.

#### 1.5.5 One TB defect in these logs, so their errors are not misread

The count-1 runs each carry 20 or 21 crash_dump errors, and they are NOT B16 evidence: landing 64 records
them as a testbench defect. The scoreboard's correction of the model's expected internal-NMI mtval for a
misaligned access runs only inside the suppressed-write block (dv/auto_dv/env/gen_rvfi_pkg.sv:485-498, the
correction at :493), and in the first-beat class ext_rf_wr_suppress is 0, so that block is never entered
and the model's expectation stays the announced word address. The DUT-side value in those messages is
still the core's own, which is what 1.5.3 and Section 1.4 use: the message prints the observed pair first
(dv/auto_dv/env/gen_checkers_pkg.sv:467-468), and for seed 1 it reads `exception_addr 800002e2`, the
load's unaligned effective address. Worth noting that the same scoreboard's comment at
gen_rvfi_pkg.sv:491-492 derives that mtval rule from the same two lines Section 1.4 cites
(rtl/ibex_controller.sv:416 and rtl/ibex_load_store_unit.sv:258), independently of this note.


### 1.6 The premise the rating rests on, corrected

The DV Lead's rating note says the P2 rating "rests on the merged word not being usable before the NMI is
taken". That premise is FALSE as stated: Section 1.3 shows one instruction, and with a Zcmp entry more than
one architectural update, consuming the merged word before the redirect, and a dependent store propagating it
to memory. The rating nonetheless survives, on two different terms:

- The corruption is always reported, and reported no later than the write. Section 1.2 fixes the order from
  the RTL rather than leaving it to a race: the alert is one cycle earlier than the earliest write and the NMI
  request is never later.
- The consumption window is bounded at one ID entry by :1095-1096 with :1020, so ONE instruction of padding
  after a misaligned load (any instruction that does not read the loaded register) is a sufficient software
  workaround: that padding instruction becomes the single entry that retires, and the redirect at :704 happens
  before the consumer can execute. The other workaround is the plain one, two aligned loads and a merge in
  place of one misaligned load.

Recommended rating: P2, the deciding term being `stall_mem` at rtl/ibex_id_stage.sv:1095-1096 feeding
`id_in_ready_o` at rtl/ibex_controller.sv:1020, which bounds the consumption window at one ID entry and so
makes a single padding instruction (or an aligned two-load sequence) the workaround that Section 0.2's P2
definition names, while the order fixed in Section 1.2 keeps the event detected.

Argument against, recorded rather than hidden: a reader who counts misaligned loads as an architectural feature
that software must give up can reach P1 through Section 0.2's "cannot avoid without giving up a feature" clause.
Section 0.2's P2 wording ("adding a delay, using another instruction sequence") is the closer match and is why
the recommendation is P2, but the choice between those two clauses is the owner's, and the facts above are the
same either way. P3 is not available: rd is architectural state, not a trace or status field.

## 2. B10: whether a debugger can disambiguate the wrong dcsr.cause, and second-order effects

### 2.1 The cause mux mixes an IF-stage observable with an ID-stage entry reason

The trigger comparator is combinational on the fetch-stage address, with no instruction-validity, privilege or
debug-mode qualifier:

    // Breakpoint matching
    // We match against the next address, as the breakpoint must be taken before execution
    for (genvar i = 0; i < DbgHwBreakNum; i++) begin : g_dbg_trigger_match
      assign trigger_match[i] = tmatch_control_q[i] & (pc_if_i[31:0] == tmatch_value_q[i]);
                                                                     (rtl/ibex_cs_registers.sv:1869-1872)
    end
    assign trigger_match_o = |trigger_match;                                                       (:1874)

Its two terms are the armed execute bit `tmatch_control_q[i]` (written only in debug mode: `tmatch_control_we[i]
= (i[DbgHwNumLen-1:0] == tselect_q) & csr_we_int & debug_mode_i & ...`, :1777) and the fetch address. The cause
mux gives that signal the top priority:

    assign debug_cause_d = trigger_match_i                    ? DBG_CAUSE_TRIGGER :
                           ebrk_insn_prio & ebreak_into_debug ? DBG_CAUSE_EBREAK  :
                           debug_req_i                        ? DBG_CAUSE_HALTREQ :
                           do_single_step_d                   ? DBG_CAUSE_STEP    :
                                                                DBG_CAUSE_NONE ;
                                                                          (rtl/ibex_controller.sv:519-523)
      debug_cause_q <= debug_cause_d;                                                               (:529)
    assign debug_cause_o = debug_cause_q;                                                           (:533)

with DBG_CAUSE_EBREAK = 3'h1 and DBG_CAUSE_TRIGGER = 3'h2 (rtl/ibex_pkg.sv:389-390).

The write into dcsr and dpc happens in one cycle from two different sources:

    csr_save_cause_i: begin                                                (rtl/ibex_cs_registers.sv:893)
      unique case (1'b1)
        csr_save_if_i: begin
          exception_pc = pc_if_i;                                                                   (:896)
        csr_save_id_i: begin
          exception_pc = pc_id_i;                                                                   (:899)
      ...
      if (debug_csr_save_i) begin                                                                   (:910)
        dcsr_d.cause = debug_cause_i;                                                                (:914)
        depc_d       = exception_pc;                                                                 (:916)

so dcsr.cause comes from debug_cause_q, registered from the PREVIOUS cycle's pc_if comparison, while dpc comes
from whichever stage the FSM selects in the SAME cycle.

An ebreak that forces debug entry is the only entry path that selects the ID stage. It runs
DECODE -> FLUSH -> DBG_TAKEN_ID: `special_req_pc_change = mret_insn | dret_insn | exc_req_d | exc_req_wb;`
(rtl/ibex_controller.sv:290) with `exc_req_d = (ecall_insn | ebrk_insn | illegal_insn_d | instr_fetch_err ...` (:268) and
`ebrk_insn = ebrk_insn_i & instr_valid_i;` (:231) put the FSM in FLUSH via :664-677; in FLUSH the
`ebrk_insn_prio:` arm (:874) with `if (debug_mode_q | ebreak_into_debug) begin` (:875) sets
`ctrl_fsm_ns = DBG_TAKEN_ID;` (:882); and DBG_TAKEN_ID (rtl/ibex_controller.sv:785) writes

    if (ebreak_into_debug && !debug_mode_q) begin                                                   (:799)
      csr_save_cause_o = 1'b1;                                                                      (:802)
      csr_save_id_o    = 1'b1;                                                                      (:803)
      debug_csr_save_o = 1'b1;                                                                      (:806)

so dpc = pc_id, the ebreak's own address, and dcsr.cause = the value debug_cause_d had in the FLUSH cycle.
Every other entry path takes dpc from pc_if: DBG_TAKEN_IF asserts `csr_save_if_o = 1'b1;` (:773) with
`debug_csr_save_o = 1'b1;` (:774) and `csr_save_cause_o = 1'b1;` (:776).

### 2.2 What pc_if holds in the FLUSH cycle

The address compared at :1872 in the FLUSH cycle is the address of the instruction AFTER the ebreak. Two terms
fix it. First the ebreak is retained in ID, so pc_id does not move: DECODE sets `retain_id = 1'b1;` (:668) under
special_req, which makes `instr_valid_clear_o = ~(stall | retain_id) | flush_id` (:1027) zero, and the IF/ID
register only reloads pc_id on a write (`pc_id_o <= pc_if_o;` rtl/ibex_if_stage.sv:613, :629). Second the fetch
address does not move either: FLUSH sets `halt_if = 1'b1;` (:818), so :1020 gives id_in_ready_o = 0, so in the
opentitan config's `g_no_branch_predictor` arm

    assign if_instr_addr  = fetch_addr;                                       (rtl/ibex_if_stage.sv:806)
    assign fetch_ready = id_in_ready_i & ~stall_dummy_instr &
                         !(instr_gets_expanded inside {INSTR_EXPANDED, INSTR_EXPANDED_COMMIT});  (:808-809)
    assign pc_if_o     = if_instr_addr;                                                             (:420)

fetch_ready is 0, and the icache output address register holds, because
`assign output_addr_en = branch_i | (ready_i & valid_o);` (rtl/ibex_icache.sv:1136) with
`assign addr_o = {output_addr_q, 1'b0};` (:1193) and ready_i wired to fetch_ready
(rtl/ibex_if_stage.sv:316-319). So with tdata2 = A and the ebreak at A-4 (A-2 for c.ebreak), trigger_match_o is
1 during FLUSH, :519 wins the mux over :520, and dcsr.cause is written 2 while dpc is written A-4. That is the
entry as B10 describes it.

### 2.3 The disambiguation the question asks for: dpc against tdata2, always decisive

A debugger can always separate the two cases with registers it already reads, and the separation is exact
rather than heuristic:

- On a GENUINE trigger entry, dpc == tdata2 necessarily. The entry is via DBG_TAKEN_IF, which saves pc_if
  (:773 with :896), and pc_if is held from the DECODE cycle by `halt_if = 1'b1;` in the enter-debug branch
  (:710) exactly as in Section 2.2; and trigger_match_o required `pc_if_i[31:0] == tmatch_value_q[i]`
  (rtl/ibex_cs_registers.sv:1872). Same address, same cycle-held value.
- On this false entry, dpc != tdata2 necessarily, because dpc is the ebreak's address (:803 with :899) and the
  match was on the next address. The two cannot coincide: if tdata2 held the ebreak's own address the trigger
  would have matched before the ebreak was accepted into ID (`timing : match before execution`, hardwired 0 at
  rtl/ibex_cs_registers.sv:1853), the entry would have been the genuine DBG_TAKEN_IF one and the ebreak would
  never have executed.

So `dcsr.cause == 2 && dpc != tdata2` identifies the defect with certainty, for any number of armed triggers.
The `hit` bit that a debugger would otherwise consult is not implemented (`1'b0, // hit : not supported`,
:1851), so cause is the only report and dpc is the only discriminator; there is no third observable to
contradict either.

### 2.4 Second-order effects, each one checked against the RTL

- The trigger CSRs are not modified. tdata1 and tdata2 are written only under `csr_we_int & debug_mode_i`
  (:1777, :1779), and nothing on this path writes them.
- No trigger fire is lost. trigger_match_o is a pure function of the armed bit and pc_if (:1872), it is
  recomputed every cycle and holds no state; after the debugger advances past the ebreak and resumes, pc_if
  becomes A, the match recurs and the entry is the genuine one with dpc = A. Nothing consumes or arms down the
  trigger.
- No fire is doubled in the RTL sense. The false report and the later genuine one are two distinct debug
  entries with different dpc values, and the second is the correct one.
- dpc is right. :803 with :899 gives the ebreak's own address, which is what the debug specification requires
  for an ebreak entry.
- mepc, mcause, mtval and mstatus are untouched, because the debug arm of :910 excludes them: the trap CSR
  writes sit in the `else if (!debug_mode_i)` arm at :918-935.
- The privilege report is right: `dcsr_d.prv = priv_lvl_q;` (:913) is written from the same arm.
- The FLUSH-cycle trigger match does NOT redirect the entry. The trigger is not a priority entry
  (`assign enter_debug_mode_prio_d = (debug_req_i | do_single_step_d) & ~debug_mode_q & ...`, :474-475; the
  trigger enters only through `assign enter_debug_mode = enter_debug_mode_prio_d | (trigger_match_i &
  ~debug_mode_q) & ...`, :476-477) and FLUSH only diverts to DBG_TAKEN_IF on
  `if (enter_debug_mode_prio_q && !(ebrk_insn_prio && ebreak_into_debug))` (:985). So the ebreak path wins and
  dpc still comes from ID. The RTL's own comment at :470-472 states the intent: a trigger match must be
  ignored where control flow changes such that the matching instruction is no longer executed. The defect is
  that the match is dropped for the ENTRY decision but not for the CAUSE record.
- The same mux masks HALTREQ and STEP the same way (:521, :522 sit below :519). Those entries are not affected
  in the same way, though, because they save dpc from pc_if (:773 with :896), so a coincident match means
  dpc == tdata2 and the instruction at dpc has not executed: cause 2 is then a defensible report of a real
  pending match rather than a misreport. The exposure is specific to the one path that saves dpc from ID.

No second-order effect on execution, on architectural state outside dcsr.cause, or on the trigger mechanism
was found.

### 2.5 What the specification settles, and what it does not

tools/specs/riscv-debug-spec/xml/core_registers.xml:29-41 gives the cause priority table with trigger (2)
ABOVE ebreak (1), which read alone would license cause 2. Its own note at :43-52 rules that reading out for
this case: "an execute trigger with timing=after on an ebreak instruction is lower priority than the ebreak
itself because the trigger will fire after the ebreak instruction." The table orders causes that belong to ONE
instruction. Here they belong to two different instructions, and Ibex's trigger is timing=0, match before
execution (rtl/ibex_cs_registers.sv:1853), so the match on A belongs to the instruction at A, which has not
executed and is not this entry's dpc. Cause 1 is the correct value for an entry whose dpc is the ebreak, and
B10 is a genuine defect rather than a licensed priority choice.

### 2.6 Recommended rating

Recommended rating: P3, the deciding term being `csr_save_id_o` at rtl/ibex_controller.sv:803 selecting
`exception_pc = pc_id_i` (rtl/ibex_cs_registers.sv:899) while the cause comes from a pc_if comparison
(:1872), which makes dpc != tdata2 an exact and always-available discriminator for the false report and
leaves execution, dpc, the trap CSRs and the trigger mechanism itself correct, so only a debug status field is
wrong. That is Section 0.2's P3 clause, and it is the rating B5 already carries for the parallel case of a
debug status field that never reports (dcsr.nmip hardwired 0).

Argument against, recorded: the current P2 rests on "avoid arming a trigger on the instruction after an
ebreak", which is a real workaround, so P2 is defensible. The reason to prefer P3 is that Section 0.2's P2
examples are all changes to the program under test (a delay, another instruction sequence, a CSR write, a mode
turned off), whereas here nothing about the program needs to change: the debugger reads a register it already
has. Not P1 under any reading: the misreport is detectable from dpc and has no effect on execution or state.

## 3. What this note does not determine

- B10 has NOT been observed in simulation. The bug log's B10 entry is "No test yet" and nothing in the tree at
  d04ada4 runs it, so all of Section 2 is a static reading: the FLUSH-cycle account in 2.2 and the (cause, dpc)
  pair in 2.3 are derived from the quoted terms, not measured. The reproducer is specified (B10's numbered
  steps in the bug log entry) and under LOG-103 its evidence bar is a retained red and green run plus a
  waveform confirmation.
- B16 HAS been observed, and Section 1.2's ordering is now measured rather than derived (1.5.1), as are the
  register write, the alert, the missing suppression, the NMI and the record count. What is NOT measured is a
  dependent instruction CONSUMING the merged word: the slot exists in five of eight seeds and holds a c.nop in
  all five. A program that puts a dependent load-use instruction, and separately a dependent store, in that
  slot would settle Section 1.3's two consequences; nothing in the tree does that today, and the cheapest form
  under LOG-103 is named in 1.5.4.
- Section 1.5.3's per-seed table rests on out-tree run directories that the Orchestrator ruled on 2026-09-08
  stay un-retained, so that one table is a measurement a reader cannot re-derive from the tree. Every other
  measurement in Section 1.5 rests on a retained log or on the waveform those logs name.
- The exact number of records a Zcmp entry after a corrupted misaligned load can add is not derived here.
  Section 1.3 states only that :500 masks handle_irq while the expansion commits, so it is more than one.
- What a particular debugger does with `dcsr.cause == 2 && dpc != tdata2` is a software question. This note
  states that the discriminator exists and is exact, not that any given debugger consults it.
- Whether the owner reads misaligned loads as a feature software must give up (Section 1.6's P1 argument) is a
  judgement on Section 0.2's wording, not an RTL fact.

## 4. Anchors

| Fact | Anchor |
|---|---|
| Per-beat integrity check; corrected word discarded | rtl/ibex_load_store_unit.sv:376-393 (`.data_o ()` at :387) |
| First-half status has no integrity term | rtl/ibex_load_store_unit.sv:514 |
| First beat captured and merged | rtl/ibex_load_store_unit.sv:234-235, :272-274, :516 |
| FSM leaves WAIT_RVALID_MIS on the first response | rtl/ibex_load_store_unit.sv:518 |
| rd write valid, all terms | rtl/ibex_load_store_unit.sv:688-690, :697-698, :711 |
| rd write reaches the register file | rtl/ibex_core.sv:1181, :1186; rtl/ibex_wb_stage.sv:181, :220 |
| Alert, combinational on the erroring beat | rtl/ibex_load_store_unit.sv:756; rtl/ibex_core.sv:1353 |
| Internal NMI pending, one register deep | rtl/ibex_id_stage.sv:613; rtl/ibex_controller.sv:413-417, :421-422, :429, :436 |
| handle_irq, all terms; MIE does not gate the NMI | rtl/ibex_controller.sv:487, :490, :498-500 |
| Redirect gated on the pipeline draining | rtl/ibex_controller.sv:296, :701, :704, :713, :730, :733, :1017, :1020, :1027 |
| Integrity error is not a writeback exception | rtl/ibex_load_store_unit.sv:746, :748-755; rtl/ibex_controller.sv:336-337 |
| Instruction in ID is not killed | rtl/ibex_id_stage.sv:1033-1036, :1059-1062; rtl/ibex_controller.sv:655 |
| No load-data forwarding; consumer stalls then reads the RF | rtl/ibex_id_stage.sv:1111-1120; rtl/ibex_wb_stage.sv:107, :115-116, :193-194, :212-215 |
| ID is refilled at most once while the load is outstanding | rtl/ibex_id_stage.sv:1015-1016, :1089-1090, :1095-1096; rtl/ibex_load_store_unit.sv:518, :533, :546, :555, :561, :632 |
| A dependent store may issue at M+1 | rtl/ibex_id_stage.sv:732, :1019 |
| NMI mcause and mtval; mtval is the load's own address | rtl/ibex_controller.sv:416, :437, :438, :737-742; rtl/ibex_load_store_unit.sv:258, :263-264, :480, :520 |
| RVFI reports no suppression for the first-beat class | rtl/ibex_core.sv:2384-2385 |
| Trigger comparator, both terms, on pc_if | rtl/ibex_cs_registers.sv:1777, :1779, :1869-1872, :1874 |
| tdata1 hardwired fields: hit not supported, timing before execution | rtl/ibex_cs_registers.sv:1851, :1853 |
| Cause mux and its register | rtl/ibex_controller.sv:519-523, :529, :533; rtl/ibex_pkg.sv:389-390 |
| dcsr.cause and dpc written from different sources | rtl/ibex_cs_registers.sv:893-902, :910-917 |
| ebreak path to DBG_TAKEN_ID; dpc from ID | rtl/ibex_controller.sv:231, :268, :290, :664-677, :874-882, :785, :799-806 |
| Every other entry takes dpc from pc_if | rtl/ibex_controller.sv:773-776 |
| pc_if and pc_id hold through FLUSH | rtl/ibex_controller.sv:668, :818, :1020, :1027; rtl/ibex_if_stage.sv:420, :613, :629, :806, :808-809, :316-319; rtl/ibex_icache.sv:1136, :1193 |
| Trigger is not a priority debug entry | rtl/ibex_controller.sv:470-472, :474-475, :476-477, :985 |
| Trap CSRs are excluded on a debug save | rtl/ibex_cs_registers.sv:913, :918-935 |
| Debug specification cause priority and its ebreak note | tools/specs/riscv-debug-spec/xml/core_registers.xml:29-41, :43-52 |
| Configuration | ibex_configs.yaml:41-60; rtl/ibex_top.sv:41; dv/auto_dv/tb/gen_dut_top.sv:59, :206, :284 |
| B16 measured: rd write, alert, suppression, NMI, record count | dv/auto_dv/evidence/gen_tdd_b16_knob.md (tb-infra, commit e7e7a94); dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l64_b16_c1_seed1_sim.log:34, :35, :72 and its verdict.txt; the green control gen_fu_l64_b16_c2_seed1_*; the sweep gen_fu_l64_b16_sweep16.log; the waveform gen_fu_l64_b16_waveform.log and the FSDB it names; out-tree, not retained: dv/auto_dv/out_b16knob/c1_s1..c1_s8/gen_export.txt |
| The merged slice, and which response bits can change rd | rtl/ibex_load_store_unit.sv:91, :235, :272-274 |
| The crash_dump errors in those runs are a TB defect | dv/auto_dv/env/gen_rvfi_pkg.sv:485-498 (:493), :491-492; dv/auto_dv/env/gen_checkers_pkg.sv:467-468 |
| The NMI cover watches the external pin, not the internal NMI | dv/auto_dv/tb/gen_protocol_props.sv:274; the alert cover and its exact property :285-286, :289 |
