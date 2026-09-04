# Mutation record: step-2b agents and boundary checkers (MB1..MB4, T-090), the follow-up landing (MB5..MB11) and landing 1c (RC1..RC3, RS1, RM-L1)

Owner: tb-infra, 2026-09-03. Format: dv/auto_dv/mutations/gen_README.md. Every mutant is built OUT OF TREE (a scratch copy of
dv/auto_dv with every other clone entry symlinked; the runner prints the shared tree's file sha256 after each mutant and
the batch driver the five source shas at start and end, unchanged: gen_tdd_logs/mutations/gen_t090_oot_mutation_batches.log
for MB1..MB4 at 67b5971, gen_fu_oot_mutation_batch.log for MB3..MB11 and MUT-I/J/K on the follow-up tree, gen_fu_mb5h_*
for MB5 re-run on the landed tree). Vehicles: gen_ut_boot (boot, retire N, tohost) or the named unit test, with hidden
referees inert, `+gen_chk_all=0 +gen_chk_<row>=1` (isa rows add `+gen_chk_isa=1`) for the catch and `+gen_chk_<row>=0` for
the ablation; the model steps regardless (Section 4 of gen_tdd_step2b.md). Programs: gen_irq_directed.S (interrupts
enabled, vectored table of mrets), gen_zcmp_irq_directed.S (Zcmp loop under interrupts, handlers starting with cm.push),
the s7 riscv-dv image (the program riscv-dv generated with its seed 7, run with simulator seed 1 as every run header says; one
synchronous trap), the Zc directed image. Retained per mutant: oot compile log, catch and
ablation run headers, verdicts and stdout excerpts (gen_tdd_logs/mutations/gen_t090_MB*_* and gen_fu_MB*_*).

| Id | Mutation (a TB-side defect at the DUT boundary) | Catching run and knobs | Catch result | Ablation |
|---|---|---|---|---|
| MB1 | gen_tb_top.sv: the fast interrupt lines are cut between the driver and the DUT (`irq_fast = '0`), the driver still raises and publishes them | gen_ut_boot on gen_irq_directed.S, `+gen_knob_irq_regime=storm +gen_knob_irq_line_mix=multi`, row irq_entry | FAIL (UVM_ERROR 66: raised, enabled lines not taken within GEN_IRQ_ENTRY_BOUND_RECORDS records; 367 entries on the connected lines) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0; the 8744 irq_pending mismatches the cut also causes stay silenced) |
| MB2 | gen_agents_pkg.sv: gen_dbg_driver publishes the request but drives `req` low | gen_ut_boot on the s7 image, `+gen_knob_debug_req_regime=storm`, row dbg_entry | FAIL (UVM_ERROR 30: 46 requests, 0 entries, 30 bound failures) | `+gen_chk_dbg_entry=0`: PASS (UVM_ERROR 0) |
| MB3 | gen_agents_pkg.sv: every bus response is marked `intg_bad` (alert expected) while none is corrupted | gen_ut_boot on the Zc image, row alert_bus; re-run on the follow-up tree (CR5-L-1) | FAIL (UVM_ERROR 159: alert_major_bus_o low in an rvalid cycle marked corrupted; 159 again on the follow-up tree) | `+gen_chk_alert_bus=0`: PASS (UVM_ERROR 0, both trees) |
| MB4 | gen_tb_top.sv: the observed irq_pending pin is inverted on the way to the checker | gen_ut_boot on the Zc image, row irq_pending; re-run on the follow-up tree (CR5-L-1) | FAIL (UVM_ERROR 541: pending 1 expected 0 every checked cycle; 541 again on the follow-up tree) | `+gen_chk_irq_pending=0`: PASS (UVM_ERROR 0, both trees) |
| MB5 | gen_rvfi_pkg.sv (monitor): an entry record's pc_rdata is reported one vector higher, so the scoreboard offers the model cause + 1 and the checker sees a cause the pins never carried | gen_ut_irq on gen_irq_directed.S, row irq_entry (T-136 cause rule) | FAIL (UVM_ERROR 5 on the follow-up tree, gen_fu_MB5_*: 2 `taken line was not pending-and-enabled` such as `entry mcause 80000014 at order 302 ... (either 00080000 both 00000000)` and 3 `cause is not an interrupt line` where the shifted vector names no line; 300 on the landing-1c tree, gen_fu_l1c_MB5_*: since landing 2a the driver releases only the taken line it is told, so the shifted cause also keeps the real line held and every later entry is judged against it) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0, both trees) |
| MB6 | gen_rvfi_pkg.sv (monitor): one legal store record (the first store after order 50) is reported with `trap` set, a DUT faulting an access nobody corrupted | gen_ut_boot on the s7 image, `+gen_chk_isa=1`, row isa_trap (T-137 conditioned arming: no announcement, the model decides) | FAIL (UVM_ERROR 1: `isa_trap dut trapped, model retired 1 trap=0 cause=00000000` at order 469, pc 80001782, a sw) | `+gen_chk_isa_trap=0`: PASS (UVM_ERROR 0) |
| MB7 | gen_rvfi_pkg.sv (scoreboard): an interrupt or debug entry inside a Zcmp sequence counts the split but leaves the partial sequence open (the pre-T-134 behaviour) | gen_ut_boot on gen_zcmp_irq_directed.S, `+gen_knob_irq_regime=sparse +gen_knob_irq_line_mix=multi +gen_chk_isa=1`, row isa_rd | FAIL (UVM_ERROR 8: `isa_rd Zcmp union: model wrote 1 registers, dut 3` at order 1148 and the appended micro-ops' registers) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| MB8 | gen_tb_top.sv: the observed alert_major_internal pin is inverted | gen_ut_boot on the Zc image, row alert_internal | FAIL (UVM_ERROR 544: `alert_major_internal_o high at cycle 0` and every cycle) | `+gen_chk_alert_internal=0`: PASS (UVM_ERROR 0) |
| MB9 | gen_tb_top.sv: the observed data_tag_o pin is inverted | gen_ut_boot on the Zc image, row data_tag_quiet | FAIL (UVM_ERROR 544: `data_tag_o high at cycle 0` and every cycle) | `+gen_chk_data_tag_quiet=0`: PASS (UVM_ERROR 0) |
| MB10 | gen_tb_top.sv: the observed alert_minor pin is inverted | gen_ut_boot on the Zc image, row alert_minor | FAIL (UVM_ERROR 544: `alert_minor_o high at cycle 0 without an announced ECC injection`) | `+gen_chk_alert_minor=0`: PASS (UVM_ERROR 0) |
| MB11 | gen_tb_top.sv: the observed double_fault_seen pin is inverted (a pulse every cycle) | gen_ut_boot on the s7 image (one synchronous trap at order 466), row double_fault | FAIL (UVM_ERROR 2: `double_fault_seen_o pulse at cycle 1754 for a first synchronous trap (order 466)`) | `+gen_chk_double_fault=0`: PASS (UVM_ERROR 0) |
| MB12 | gen_agents_pkg.sv (gen_bus_driver): a data-side integrity corruption is announced (`note_intg`) but the response word stays clean, so the DUT raises no internal NMI | gen_ut_boot on the s7 image, `+gen_knob_dmem_intg_err_rate=frequent`, row nmi_internal (landing 2a) | FAIL (UVM_ERROR 28: `no internal NMI entry within 4 records outside NMI mode of the integrity corruption announced at order N`) | `+gen_chk_nmi_internal=0`: PASS (UVM_ERROR 0) |

Exact edits (dv_principles Section 6 rule 2; line numbers in the landed tree; `/` joins the lines of a multi-line edit):

| Id | file:line | original | mutated |
|---|---|---|---|
| MB1 | `dv/auto_dv/tb/gen_tb_top.sv:171` | `assign irq_fast     = u_irq_if.fast;` | `assign irq_fast     = '0;   // MB1: the fast lines are cut between the driver and the DUT` |
| MB2 | `dv/auto_dv/env/gen_agents_pkg.sv:644` | `vif.req = 1'b1; hold_policy = policy; hold_left = (policy == 0) ? (cycles == 0 ? 1 : cycles) : 0;` | `vif.req = 1'b0; hold_policy = policy; hold_left = (policy == 0) ? (cycles == 0 ? 1 : cycles) : 0;   // MB2: request published, pin not driven` |
| MB3 | `dv/auto_dv/env/gen_agents_pkg.sv:303` | `p.err = 0; p.injected = 0; p.intg_bad = 0;` | `p.err = 0; p.injected = 0; p.intg_bad = 1;   // MB3: every response marked corrupted, none is` |
| MB4 | `dv/auto_dv/tb/gen_tb_top.sv:173` | `assign u_irq_if.pending = irq_pending;` | `assign u_irq_if.pending = ~irq_pending;   // MB4: the observed pending pin inverted` |
| MB5 | `dv/auto_dv/env/gen_rvfi_pkg.sv:115` | `t.pc_rdata = vif.pc_rdata; t.pc_wdata = vif.pc_wdata;` | `t.pc_rdata = vif.pc_rdata + (vif.intr ? 32'h4 : 32'h0); t.pc_wdata = vif.pc_wdata;   // MB5: the entry record names the next vector (cause + 1)` |
| MB6 | `dv/auto_dv/env/gen_rvfi_pkg.sv:110` and `:30` | `t.order = vif.order; t.insn = vif.insn; t.trap = vif.trap; t.halt = vif.halt; t.intr = vif.intr;` and `bit          ext_exp_valid, ext_exp_last;` | `t.trap = vif.trap \|\| (!gen_rvfi_txn::mut_done && vif.insn[6:0] == ibex_pkg::OPCODE_STORE && vif.order > 50); ... / if (t.trap && !vif.trap) gen_rvfi_txn::mut_done = 1;   // MB6: one legal store reported as a trap` and `/ static bit   mut_done = 0;` |
| MB7 | `dv/auto_dv/env/gen_rvfi_pkg.sv:314` | `seq_splits++; in_seq = 0;` | `seq_splits++;   // MB7: a split leaves the partial sequence open` |
| MB8 | `dv/auto_dv/tb/gen_tb_top.sv:178` | `assign u_misc_if.alert_major_internal = alert_major_internal;` | `assign u_misc_if.alert_major_internal = ~alert_major_internal;   // MB8: the observed alert_major_internal pin inverted` |
| MB9 | `dv/auto_dv/tb/gen_tb_top.sv:181` | `assign u_misc_if.data_tag_o           = data_tag_o;` | `assign u_misc_if.data_tag_o           = ~data_tag_o;   // MB9: the observed data_tag_o pin inverted` |
| MB10 | `dv/auto_dv/tb/gen_tb_top.sv:177` | `assign u_misc_if.alert_minor          = alert_minor;` | `assign u_misc_if.alert_minor          = ~alert_minor;   // MB10: the observed alert_minor pin inverted` |
| MB11 | `dv/auto_dv/tb/gen_tb_top.sv:180` | `assign u_misc_if.double_fault_seen    = double_fault_seen;` | `assign u_misc_if.double_fault_seen    = ~double_fault_seen;   // MB11: the observed double_fault_seen pin inverted` |
| MB12 | `dv/auto_dv/env/gen_agents_pkg.sv` (the intg_bad branch of gen_bus_driver) | `flipped[b1] = ~flipped[b1]; / if (cfg.is_data) gen_bus_err_log::note_intg(p.addr);` | `if (cfg.is_data) gen_bus_err_log::note_intg(p.addr);   // MB12: the corruption is announced, the word stays clean` (the flip removed) |

Discarded form MB1a (recorded, not counted): the irq driver publishing its levels but never driving the pins. Both runs
PASS with the rows on: gen_irq_checker reads the interface pins, so a driver that lies about its own pins is invisible to
a checker of the DUT by design; the DUT-boundary cut (MB1) is the defect class the row exists for.

Two invalid attempts before the MB1..MB4 results, kept in the T-090 batch log: (1) gen_ut_lockstep as the vehicle under
`+gen_chk_all=0` fails on its own compared-record count when the isa rows are off, so no ablation could pass; (2) with the
isa rows off the scoreboard did not build the model at all, so gen_irq_checker and gen_dbg_checker received no model
state: in that batch MB2 was PASS/PASS (uncaught) and MB1 FAIL/FAIL on the cocotb summary (a vehicle failure of the same
class as attempt 1). The second is a real isolation defect, fixed at 67b5971: the model steps and publishes in every run
and the knobs silence only the isa_* rows (gen_e_lockstep_zc_isaoff_t090 shows the lock-step test green under
+gen_chk_all=0). Tree state per mutant (Critic T-090 L-1): MB1 and MB2 ran against the 67b5971 tree (12:38-12:40Z); MB3
and MB4 first ran against the 12:34Z pre-build-e tree and were re-run on the follow-up tree with the same counts (159,
541); MB5..MB11 and MUT-I/J/K ran against the follow-up tree (batch 14:54-14:59Z, five shas printed unchanged), MB5 once
more against the landed tree; MB12 (with P13 and MUT-L) ran against the landing-2a tree (gen_fu_l2_oot_mutation_batch.log, four shas
printed unchanged), each mutant built from an out-of-tree copy of that tree after the NMI-classification edits of gen_tdd_step2b.md Section 7a (the only edits between the two;
gen_fu_mb5h_oot_mutation_batch.log).

Rows without a red, all seven named (Critic T-090 L-8): irq_masked, dbg_masked and nmi_entry have NO mutation (they need
a program that masks MIE with a line pending, enters debug with a line pending, or raises the NMI pin with the model
emulating NMI, which the shim does not yet); alert_internal, data_tag_quiet, alert_minor and double_fault now have MB8,
MB9, MB10 and MB11 (the observed pin inverted; the never-high rules see the constant high on the first cycle, the
double_fault rule sees a pulse for the first synchronous trap). Until their reds exist, irq_masked, dbg_masked and
nmi_entry are declared, not trusted, and no plan item rests on them.

## Landing 1c batch: the new rules' mutants and the re-run of MB3..MB7 on the final tree (2026-09-03)

Every mutant below was built from the final landing-1c sources (the copy whose build f is sources sha256 a056526d879ea458)
plus its one edit, out of tree (scratch mut_root/<id>); the `build` column is the mutant build's own `sources sha256`
from its compile.log (gen_fu_l1c_<id>_build_compile.log), so a reader can tell a stale base from the landed one. Driver
output: gen_tdd_logs/mutations/gen_fu_l1c_oot_mutation_batch.log; per run gen_fu_l1c_<id>_{catch,ablate}_<run>_*. A
"referee" row has no ablation knob: it is a report-time rule that is always on, so the catch run has every checker on.

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| RC1 | gen_rvfi_pkg.sv: the entry state is not published before the Zcmp fold (the CM18-H-1 hole re-opened) | gen_ut_lockstep on gen_zcmp_irq_directed.S, sparse, multi, every checker on | d2c25aa56833ce0b | FAIL (UVM_ERROR 1): `irq_entries_referee scoreboard stepped 15 interrupt entries, the irq checker saw 0` | referee (none) |
| RC2 | gen_tb_pkg.sv `gen_insn_mem_access`: a c.sw fault is armed as a load | gen_ut_lockstep on gen_dmem_err_directed.S, frequent, row isa_trap | b527978d3e2671b1 | FAIL: `isa_trap dut trapped, model retired 1 trap=0 cause=00000000` at order 387, pc 80000148, insn 0000c54c (c.sw) | `+gen_chk_isa_trap=0`: PASS (UVM_ERROR 0) |
| RC3 | gen_checkers_pkg.sv: one pulse offset (GEN_TRAP_TO_RVFI_OFFSET) for every trap kind | gen_ut_lockstep on gen_dmem_err_directed.S, frequent, row double_fault | 8220d9a84b8cff61 | FAIL (UVM_ERROR 1): `double_fault second synchronous trap (order 1164, cycle 5689) without a double_fault_seen_o pulse at cycle 5688` | `+gen_chk_double_fault=0`: PASS (UVM_ERROR 0) |
| RS1 | gen_isa_shim.cc: the armed fault keeps Spike's effective-address mtval (the tval write removed) | gen_ut_lockstep on gen_dmem_err_directed.S, frequent, row isa_rd; and the shim unit test | 30626974030122f4 | FAIL: `isa_rd rd model=x22/8000026e dut=x22/80000270` (the handler's csrr mtval) at order 418 and every later spanning fault; unit test `GEN_UT_ISA_SHIM FAIL (2 failures)`: `step tval = the second word got 0x80000186 exp 0x80000188`, `mtval CSR = the second word` (gen_fu_l1c_RS1_ut_isa_shim_red.log) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| RM-L1 | gen_agents_pkg.sv: the data-bus driver announces an injected error it does not drive (`p.err = 0`, the note kept) | gen_ut_lockstep on gen_dmem_err_directed.S, frequent, every checker on | c818ed35d2fcb20a | FAIL (UVM_ERROR 1): `bus_err_leftover 55 announced data-bus errors never consumed by a trap record (announced 56, taken 0, drain window 64 cycles)`; every isa row silent | referee (none) |
| MB3 | as above | gen_ut_boot zc, row alert_bus | abda8d372f008c86 | FAIL (UVM_ERROR 159) | PASS (0) |
| MB4 | as above | gen_ut_boot zc, row irq_pending | f4958fbe6cd44945 | FAIL (UVM_ERROR 541) | PASS (0) |
| MB5 | as above | gen_ut_irq on gen_irq_directed.S, row irq_entry | edc770bef56fee9c | FAIL (UVM_ERROR 300; see the MB5 row above for why the count grew since landing 2a) | PASS (0) |
| MB6 | as above | gen_ut_boot s7 image, row isa_trap | be2ad512fbd288fd | FAIL (UVM_ERROR 1): `isa_trap dut trapped, model retired 1` at order 469, pc 80001782 | PASS (0) |
| MB7 | as above | gen_ut_boot on gen_zcmp_irq_directed.S, sparse, multi, row isa_rd | 403ee454b9411265 | FAIL (UVM_ERROR 16): `isa_rd Zcmp union: model wrote 1 registers, dut 3` at order 1148 | PASS (0) |

Exact edits of the new mutants (the re-run rows keep the edits of their first table):

| mutant | file | original | mutated |
|---|---|---|---|
| RC1 | `dv/auto_dv/env/gen_rvfi_pkg.sv` (the fold return in `write`) | `if (t.intr \|\| dbg_entry) publish_state(t, pc_a, prv, csr_n);` | the line removed (`// RC1: the entry state is not published before the fold`) |
| RC2 | `dv/auto_dv/tb/gen_tb_pkg.sv` (`gen_insn_mem_access`, quadrant 0) | `3'b110: begin is_store = 1; bytes = 4; return 1; end   // c.sw` | `3'b110: begin is_store = 0; bytes = 4; return 1; end   // RC2: a c.sw fault is armed as a load` |
| RC3 | `dv/auto_dv/env/gen_checkers_pkg.sv` (gen_misc_monitor `write_state`) | `? GEN_LSU_TRAP_TO_RVFI_OFFSET : GEN_TRAP_TO_RVFI_OFFSET);` | `? GEN_TRAP_TO_RVFI_OFFSET : GEN_TRAP_TO_RVFI_OFFSET);   // RC3: one pulse offset for every trap kind` |
| RS1 | `dv/auto_dv/isa/gen_isa_shim.cc` (after `g_proc->step(1)`) | `if (g_fault.hit && g_fault.tval != 0) g_proc->put_csr(CSR_MTVAL, g_fault.tval);` | the line removed (`// RS1: the fault keeps Spike's effective-address mtval`) |
| RM-L1 | `dv/auto_dv/env/gen_agents_pkg.sv` (gen_bus_driver, the injection branch) | `p.err = 1; p.injected = 1; injected_err++;` (the `gen_bus_err_log::note(p.addr, bvif.cycle_count)` line after it kept) | `p.err = 0; p.injected = 1; injected_err++;   // RM-L1: announced, never driven` |

## Landing 2b batch: the protocol SVA layer, the witness covergroup, the misc and dret rules (2026-09-03)

Built out of tree from the landing-2b sources (l2b_root, build a 68a36e6ac32db967, for MUT-M / MUT-N / RM1..RM3; wit_root, the
landed build e 5ca9fd98c937c26f, for WM1 / MB13 / MB14 / RM4) plus one edit each; `build` is the mutant build's own
`sources sha256` (gen_fu_l2b_<id>_build_compile.log; the RTL is not part of that hash, the RTL mutants' copies are recorded in
their compile.launch.log). RM1..RM3 as cited are the RE-RUN from a private rtl copy (mut_l2b_rm_rerun.log); the first run
(mut_l2b_final.log, retained as gen_fu_l2b_oot_mutation_batch_tainted.log) mutated the shared clone's rtl through a
symlinked copy and its RM rows stacked three mutations, so it proves nothing and is kept only as the incident's record.

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| MUT-M | gen_agents_pkg.sv (gen_scrkey_driver): the responder keeps ic_scr_key_valid_i high through a re-key instead of dropping it with the new request | gen_ut_boot s7 image, row sva_scrkey | af81efcfe78a1b84 | FAIL (UVM_ERROR 5) | `+gen_chk_sva_scrkey=0`: PASS (0) |
| MUT-N | gen_agents_pkg.sv (gen_bus_driver): instr_err_i pulses outside a response beat (the idle level of err is 1) | gen_ut_boot zc, row sva_ibus | d089c40458b67369 | FAIL (UVM_ERROR 405) | `+gen_chk_sva_ibus=0`: PASS (0) |
| RM1 | rtl/ibex_core.sv (out-of-tree copy): the On bits of core_busy_o never rise | gen_ut_boot zc, row sva_st | 68a36e6ac32db967 | FAIL (UVM_ERROR 545) | `+gen_chk_sva_st=0`: PASS (0) |
| RM2 | rtl/ibex_core.sv (out-of-tree copy): rvfi_halt set on every record | gen_ut_boot zc, row sva_rvfi | 68a36e6ac32db967 | FAIL (UVM_ERROR 169) | `+gen_chk_sva_rvfi=0`: PASS (0) |
| RM3 | rtl/ibex_load_store_unit.sv (out-of-tree copy): data_tag_o driven high | gen_ut_boot zc, row sva_dbus | 68a36e6ac32db967 | FAIL (UVM_ERROR 545) | `+gen_chk_sva_dbus=0`: PASS (0) |
| WM1 | gen_fcov_pkg.sv: the witness covergroup is never sampled | gen_ut_witness zc, every checker on | 3e91ae996ae27f98 | FAIL: `the first witness (TP-BIT-036) counts 0 distinct bins, expected 1` | `+gen_fcov_en=0` (bookkeeping path): PASS |
| MB13 | gen_tb_top.sv: the observed crash_dump.exception_pc offset by 4 | gen_ut_lockstep on gen_dmem_err_directed.S, frequent, row crash_dump | 776392d1e882e0ed | FAIL: `crash_dump exception_pc/exception_addr 00000004/00000000 at order 1: model mepc/mtval 00000000/00000000 ...` | `+gen_chk_crash_dump=0`: PASS (0) |
| MB14 | gen_tb_top.sv: the DUT's fetch_enable_i tied On while the TB drives Off | gen_ut_fetch_en zc, row fetch_en | 4e2d112c2159b89c | FAIL: `record at order 90, cycle 270, 68 cycles after fetch_enable_i left On at cycle 202 (drain window 64)` | `+gen_chk_fetch_en=0`: PASS (0) |
| RM4 | rtl/ibex_if_stage.sv:247 (out-of-tree copy): dret resumes one word past dpc | gen_ut_lockstep s7 image debug storm, row dbg_dret | 5ca9fd98c937c26f | FAIL (UVM_ERROR 14): `record after dret: pc ... dpc ...` | `+gen_chk_dbg_dret=0`: PASS (0) |

Exact edits:

| mutant | file | original | mutated |
|---|---|---|---|
| WM1 | `dv/auto_dv/env/gen_fcov_pkg.sv` (`witness`) | `if (cg != null) cg.sample(idx);` | the line removed (`// WM1: the covergroup is never sampled`) |
| MB13 | `dv/auto_dv/tb/gen_tb_top.sv` | `assign u_misc_if.crash_dump = crash_dump;` | `assign u_misc_if.crash_dump = '{current_pc: ..., next_pc: ..., last_data_addr: ..., exception_pc: crash_dump.exception_pc + 32'd4, exception_addr: ...};` |
| MB14 | `dv/auto_dv/tb/gen_tb_top.sv` (the DUT instance) | `.fetch_enable_i(fetch_enable),` | `.fetch_enable_i(ibex_pkg::IbexMuBiOn),` |
| RM4 | `rtl/ibex_if_stage.sv:247` (copy) | `PC_DRET: fetch_addr_n = csr_depc_i;` | `PC_DRET: fetch_addr_n = csr_depc_i + 32'd4;` |
| MUT-M | `dv/auto_dv/env/gen_agents_pkg.sv` (gen_scrkey_driver) | `requests++;` / `vif.valid = 1'b0;` | `requests++;   // MUT-M: the responder keeps valid high through a re-key` (the drop removed) |
| MUT-N | `dv/auto_dv/env/gen_agents_pkg.sv` (gen_bus_driver idle level) | `vif.rvalid = 1'b0; vif.err = 1'b0; vif.intg_corrupt = 1'b0;` | `vif.rvalid = 1'b0; vif.err = 1'b1; vif.intg_corrupt = 1'b0;   // MUT-N: err pulses outside a response` |
| RM1 | `rtl/ibex_core.sv` (copy) | `assign core_busy_o[i] =  \|busy_bits_buf[i*NumBusySignals +: NumBusySignals];` | `assign core_busy_o[i] =  1'b0;` |
| RM2 | `rtl/ibex_core.sv` (copy) | `assign rvfi_halt       = rvfi_stage_halt      [RVFI_STAGES-1];` | `assign rvfi_halt       = rvfi_valid;` |
| RM3 | `rtl/ibex_load_store_unit.sv` (copy) | `assign data_tag_o = data_wdata_tag;` | `assign data_tag_o = 1'b1;` |

## SVA groups proven and owed (the Critic's landing-2b lift condition 3, CM60-L-3)

Proven with a named mutant each in the landing-2b batch: st (MB-ST), ibus (MB-IBUS), dbus (MB-DBUS), scrkey (MB-SCRKEY) and rvfi
(MB-RVFI) through the rows above. The four groups owed to landing 2c, AS BUILT (CR-2B-M-2): one named mutant per group, each with its group knob's ablation
(`+gen_chk_all=0 +gen_chk_sva_<group>=1` for the catch, `=0` for the ablation), built out of tree from the wit_root copy: MS-ICRAM, MS-IRQ and MS-DBG beside build u (b7b1b3fe53bc65ec, 21:29Z; their run headers
carry u or the mutated TB's own sha), MS-ALERT beside build v (cf73fd8a625e89a8, 21:38Z); a copy time is retained nowhere, so "beside" is inferred from the run times and header shas
(tb_l10 L-3); the sva rules they exercise are unchanged
from u through w (e287c87e3fdf8a97), and the edits between the builds (the per-line release, the shim's mstack push, the unit test's
section 12b, documents) enter none of the mutated rules. An RTL mutant is applied to a private `cp -rL` copy of rtl/ (guard:
the copy is a real directory, never the clone's), so its build sha equals the unmutated one; the row therefore names the
mutated file and the tree file's sha256 (first 16 hex; the file is unchanged since, so today's tree sha is the original's).
The `source tree untouched` line of every batch hashes the SHARED tree's dv/auto_dv/env/gen_rvfi_pkg.sv (TB batches) or
rtl/ibex_core.sv, rtl/ibex_load_store_unit.sv and dv/auto_dv/env/gen_agents_pkg.sv (RTL batches) after the runs: it shows
the tree was not written, and the `applied to ... original sha256` line identifies the mutated file (CR-2B-L-2, CR8 fu2a L-4).
For the 2b RTL rows (CM43-L-5): RM1 and RM2 mutated rtl/ibex_core.sv (88b8bf3907472f1d), RM3 rtl/ibex_load_store_unit.sv
(86e156efaf7ac46a), RM4 rtl/ibex_if_stage.sv (8b99f212f06aa942).

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| MS-ICRAM | rtl/ibex_icache.sv (out-of-tree copy, tree sha256 7b250650b7cdc056): the tag request masked by `~tag_write_ic0`, so an allocation writes the tag RAM without a request | gen_ut_lockstep on gen_icache_en_directed.S, row sva_icram | RTL copy | FAIL (UVM_ERROR 397): `sva_icram_tag_write_implies_req` | PASS (0) |
| MS-IRQ | gen_tb_top.sv: irq_timer_i driven X for the record at order 10 | gen_ut_boot zc, row sva_irq | 397d3500efacb72e | FAIL (UVM_ERROR 2): `sva_irq_pins_known` | PASS (0) |
| MS-DBG | gen_tb_top.sv: debug_req_i driven X for the record at order 10 | gen_ut_boot zc, row sva_dbg | 95b303312b8e183c | FAIL (UVM_ERROR 2): `sva_dbg_req_known` | PASS (0) |
| MS-ALERT | rtl/ibex_core.sv:1350 (out-of-tree copy, tree sha256 88b8bf3907472f1d): alert_major_internal_o tied high | gen_ut_lockstep zc, row sva_alert | RTL copy | FAIL (UVM_ERROR 2851): `sva_alert_internal_never` | PASS (0) |

A first form of MS-ALERT (rtl/ibex_top.sv:1362, the same tie-high) was inert: gen_dut_top instantiates ibex_core, so ibex_top.sv
is not in the build; the run PASSed both ways and is not counted (recorded so that nobody re-tries it). The planned forms of
MS-IRQ / MS-DBG (an X driven by the agents) and MS-ALERT (the bind's bus term inverted) were replaced by the pin and RTL forms
above, which mutate what the assertion watches rather than the assertion's operand wiring.

## Landing 2c: the scoreboard gate, the irq checker's per-line rule and the witness referee

| mutant | what is broken | run | build | catch | ablation |
|---|---|---|---|---|---|
| MUT-SUP | gen_tb_top.sv: `rvfi_ext_rf_wr_suppress` asserted on one clean load (the Zc image's c.lwsp at order 21) | gen_ut_lockstep zc, row isa_rd | 10863e69cb52366a | FAIL (UVM_ERROR 1): `rf_wr_suppress asserted without an announced integrity corruption for 8000039c (order=21 ... rd=x28)` | PASS (0) |
| MUT-SUPB | the same lie on the Zcb image's c.lbu at order 11 | gen_ut_lockstep zcb, row isa_rd | dc49aa2390fce38a | FAIL (UVM_ERROR 1): `... for 80000200 (order=11 ... rd=x13)` | PASS (0) |
| MUT-SUP2 | gen_tb_pkg.sv: `gen_bus_err_log::note_intg` pushes the announced corruption address off by 0x100 | gen_ut_lockstep s7 image, `+gen_knob_dmem_intg_err_rate=frequent`, row isa_rd | d1b459522805596e | FAIL (421 UVM_ERROR lines counted by the retained excerpt's header: the gate's refusals and the isa_rd misses they cause, not separated; the verdict carries no UVM report): the gate refuses every real suppressed load (83 in the green run), `... for 8001c434 (order=550 ...)` first | PASS (0) |
| MUT-NT | gen_tb_top.sv: irq_external tied 0 while the driver raises and holds it | gen_ut_lockstep on the irq storm image, `+gen_knob_irq_regime=storm +gen_knob_irq_line_mix=multi`, row irq_entry | 6a5417dd8a8a03ca | FAIL (UVM_ERROR 31): `lines 00004 raised at cycle 223 (order 62) not taken within 17 records` (the per-line bound, CR8-M-5) | PASS (0) |
| MUT-NT2 | gen_tb_top.sv: irq_external withheld from the DUT from order 3572 on (the run's last records, fewer than the 17-record bound) | gen_ut_lockstep on the irq storm image, storm / multi, simulator seed 3, row irq_entry | 4e4a02897de732d3 (the retained seed-3 catch; 2643308399b05e33 (tb8) and b74b099eeff78e04 (tb7, gen_fu_l7_oot_mutation_batch_tb7.log) were the discarded forms: the tb7 mask from order 2956 fired the per-line bound, the tb8 mask from 3540 with an override plusarg that does not exist FATALed; an earlier correction here wrote 88c4cfa250b44e1e, which is MUT-NT's build, and order 2488, which no retained line carries (tb_l10 L-3)) | FAIL (UVM_ERROR 1): `lines 00004 raised at cycle 22574 (order 3700) still held and enabled at the end of the run, never taken (last order 3710)` (the end-of-run rule, CR8-M-5) | PASS (0) |
| MUT-NIB | gen_tb_pkg.sv: `GEN_NMI_INT_ENTRY_BOUND_RECORDS` lowered from 4 to 0 (the rendered constant edited in the copy) | gen_ut_lockstep s7 image, `+gen_knob_dmem_intg_err_rate=frequent`, row nmi_internal | 61d496172f9baf12 | FAIL (UVM_ERROR 54): `no internal NMI entry within 0 records outside NMI mode of the integrity corruption announced at order 497` and one per announcement | PASS (0) |
| MUT-CNT | gen_isa_shim.cc (T-235): the inhibit accounting removed (`else if (false) g_inh += retired`; the applied diff gen_fu_l12_MUTCNT_mutant.diff), so retirements under mcountinhibit.IR count like any other | gen_ut_lockstep on the gen_pmc_ctrl seed-1 image, pin on, row isa_rd | b3adc13808d94d15 | FAIL (UVM_ERROR 91): `isa_rd rd model=x6/000007f7 dut=x6/000007cf` at order 2108 (csrr instret) first | PASS (0) |
| WM2 | gen_fcov_pkg.sv: the witness bookkeeping records index 0 whatever index was sampled | gen_ut_witness zc, every checker on | bcbb55baf972c3ba | FAIL (UVM_ERROR 1): `wit_referee: the covergroup counts 2 distinct bins, the dispatcher accepted 1 distinct witnesses`; the unit test's own count asserts PASSED (`GEN_UT_WITNESS_PASS`, `witnesses=3 distinct=1 covergroup=2`), so the referee is the only catcher (CM43-L-4) | `+gen_fcov_en=0`: no referee error; the run fails on the unit test's fcov-off count assertion, because the mutant also corrupts the bookkeeping-path count; not a PASS, the attribution rests on the catch run |

MUT-NT2 needs a raise inside the masked tail: seeds 1 and 2 raised nothing after order 3572 and PASSED both runs (no verdict on the
rule; batch log gen_fu_l7_oot_mutation_batch_tb9_s1 / _s2), seed 3 did. MUT-NIB with the bound at 1 (batch log _tb7, build 16b938ccd6021cc1) PASSED both
runs; no retained line states that build's bound, so the exactly-1-record latency is the author's unretained observation (A2c-5) and the
retained evidence is the bound-0 red with its ablation; the constant stays 4.

Placement notes. MUT-SUP was first placed on the Zc image's orders 20-60, where the only loads are cm.pop micro-ops: the gate
is skipped inside a Zcmp sequence (the union compare judges those) and the catch came as `Zcmp union` instead of the gate's
message; then on the s7 image's orders 100-2000, which retire no load at all (an RVFI trace of its first 6000 records shows
stores, auipc and c.li only; its loads are the trap handler's restores, which the plain run never reaches), which the batch log
contradicts: MUTSUP_catch_s7 FAILED at order 147 on a c.li record (insn 00004f81, no load) with the gate's message for address 0 and its
ablation PASSED (build 2a24e18d9da35513, gen_fu_l7_oot_mutation_batch_tb4.log), a catch on a non-load record, discarded for a placement
whose catch exercises the announced-word lookup (A2c-3); the final placement is one plain load each of the Zc and Zcb images. Before the per-line release
(build 88c4cfa250b44e1e) MUT-NT PASSED both runs: under the storm the taken line's entry cleared the whole raise group, so the
withheld line was never owed its own entry; the per-line rule made it a catch.

## Landing 11 mutants (builds on the landing sources; the reds of the landing-10 code on b0 / b0h)

| id | mutation | vehicle | build sha256 | catch (the named check alone) | ablation |
|---|---|---|---|---|---|
| MUT-WIN | gen_protocol_props.sv: sva_alert_minor_window's slice as landing 9 committed it, `[ICACHE_ECC_WINDOW:1]` over the register that updates after the read cycle (latencies 2..3, never 1) | gen_ut_lockstep on gen_icache_ecc_directed.S, +gen_knob_icache_ecc_err_rate=frequent, row sva_alert | 6811292da6d2eb81 (build b2r) | FAIL: 431 `sva_alert_minor_window: protocol property violated` for 436 pulses, every pulse one cycle after its lookup read (gen_fu_l13_catch_h1_ecc_freq_*; with every check on gen_fu_l13_red_h1_ecc_freq_*) | PASS (0) gen_fu_l13_ablate_h1_ecc_freq_* |
| MUT-NT3 | gen_tb_top.sv: irq_external withheld from the DUT from the first NMI on (`nt3_q` latched on irq_nm) | gen_ut_irq_nmi_long on gen_nmi_long_directed.S (NM raised, then the external line 6 records into the 41-record handler), row irq_entry | af94e5065e405513 (nt3_b2) | FAIL (UVM_ERROR 1): `lines 00004 raised at cycle 1010 (order 24x) not taken within 17 records` after the handler's mret (gen_fu_l13_NT3b_catch_m1_nmi_raise_*); on the landing-10 checker (d4ed70e3c9e53b66, nt3_b0) the same run PASSED: the expectation expired inside NMI mode and was deleted unjudged (gen_fu_l13_red_m1_nt3_nmi_raise_old_entryonly_*) | PASS (0) gen_fu_l13_NT3b_ablate_m1_nmi_raise_* |
| MUT-SUP3 | gen_tb_top.sv: on the record of the clean c.lw of the spanning load's second word (order 18) rvfi_ext_rf_wr_suppress forced 1 and rd_addr / rd_wdata forced 0: the lie a DUT would tell | gen_ut_intg_span on gen_intg_span_directed.S (two corruptions armed on gen_span_buf), rows isa_rd (+gen_chk_isa=1 +gen_chk_isa_rd=1) | 5e241935603d2310 (sup3_b2) | FAIL: `rf_wr_suppress asserted without an announced integrity corruption for 800002e4 (order=18 ... rd=x0)` (gen_fu_l13_SUP3b_catch_l4_intg_span_isa_*); on the landing-10 gate (1f6d63cb2bc02b74, sup3c_b0) the same run PASSED with rf_wr_suppressed=2: the lie was accepted through the leftover second-word announcement (gen_fu_l13_red_l4_sup3_old_isa_*). A first form (the flag alone) was caught by the gate's rd_addr rule on both gates and is not the demonstration | PASS (0) gen_fu_l13_SUP3b_ablate_l4_intg_span_isa_* |
| MUT-ICE-ANN | gen_icache_ram.sv: the tag RAM corrupts a read but does not announce it | gen_ut_lockstep on gen_icache_ecc_directed.S, rate frequent, row alert_minor | 95aec3cd2c0f9bc6 (iceann_b2) | FAIL (UVM_ERROR 436): `alert_minor_o high at cycle ... without an announced ECC injection` (gen_fu_l13_ICEANN_catch_ice_ann_*) | PASS (0) gen_fu_l13_ICEANN_ablate_ice_ann_* |
| MUT-ICE-MISS | gen_icache_ram.sv: the tag RAM announces a corruption but returns the clean word | the same | 7962bf9979e367d3 (icemiss_b2) | FAIL (UVM_ERROR 862): `alert_minor_o missing within 2 cycles of the tag-RAM ECC injection at cycle ...` (862 qualified announcements, 0 pulses) (gen_fu_l13_ICEMISS_catch_ice_miss_*) | PASS (0) gen_fu_l13_ICEMISS_ablate_ice_miss_* |

Provenance: the four mutant copies were made from l11_root after every source fix (their per-file lists gen_fu_l13_<mutant>_sources_sha256.txt differ from
b2's in the mutated file only); the mutations as applied are gen_fu_l13_<mutant>_mutant.diff. The reds of the landing-10 code ran on nt3_b0 /
sup3c_b0 (the same mutations over the landing-10 checker and gate with the hook) and on b0 / b0h for the draft-B program and the crash_dump red.
Hidden referees inert: every catch run carries +gen_chk_all=0 and the named check's knob (the isa rows also need +gen_chk_isa=1: a first
MUT-SUP3 catch without it reported nothing and is not retained).
