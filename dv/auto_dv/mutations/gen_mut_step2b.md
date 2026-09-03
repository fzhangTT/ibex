# Mutation record: step-2b agents and boundary checkers (MB1..MB4, T-090), the follow-up landing (MB5..MB11) and landing 1c (RC1..RC3, RS1, RM-L1)

Owner: tb-infra, 2026-09-03. Format: dv/auto_dv/mutations/gen_README.md. Every mutant is built OUT OF TREE (a scratch copy of
dv/auto_dv with every other clone entry symlinked; the runner prints the shared tree's file sha256 after each mutant and
the batch driver the five source shas at start and end, unchanged: gen_tdd_logs/mutations/gen_t090_oot_mutation_batches.log
for MB1..MB4 at 67b5971, gen_fu_oot_mutation_batch.log for MB3..MB11 and MUT-I/J/K on the follow-up tree, gen_fu_mb5h_*
for MB5 re-run on the landed tree). Vehicles: gen_ut_boot (boot, retire N, tohost) or the named unit test, with hidden
referees inert, `+gen_chk_all=0 +gen_chk_<row>=1` (isa rows add `+gen_chk_isa=1`) for the catch and `+gen_chk_<row>=0` for
the ablation; the model steps regardless (Section 4 of gen_tdd_step2b.md). Programs: gen_irq_directed.S (interrupts
enabled, vectored table of mrets), gen_zcmp_irq_directed.S (Zcmp loop under interrupts, handlers starting with cm.push),
the seed-7 riscv-dv image (one synchronous trap), the Zc directed image. Retained per mutant: oot compile log, catch and
ablation run headers, verdicts and stdout excerpts (gen_tdd_logs/mutations/gen_t090_MB*_* and gen_fu_MB*_*).

| Id | Mutation (a TB-side defect at the DUT boundary) | Catching run and knobs | Catch result | Ablation |
|---|---|---|---|---|
| MB1 | gen_tb_top.sv: the fast interrupt lines are cut between the driver and the DUT (`irq_fast = '0`), the driver still raises and publishes them | gen_ut_boot on gen_irq_directed.S, `+gen_knob_irq_regime=storm +gen_knob_irq_line_mix=multi`, row irq_entry | FAIL (UVM_ERROR 66: raised, enabled lines not taken within GEN_IRQ_ENTRY_BOUND_RECORDS records; 367 entries on the connected lines) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0; the 8744 irq_pending mismatches the cut also causes stay silenced) |
| MB2 | gen_agents_pkg.sv: gen_dbg_driver publishes the request but drives `req` low | gen_ut_boot on the seed-7 image, `+gen_knob_debug_req_regime=storm`, row dbg_entry | FAIL (UVM_ERROR 30: 46 requests, 0 entries, 30 bound failures) | `+gen_chk_dbg_entry=0`: PASS (UVM_ERROR 0) |
| MB3 | gen_agents_pkg.sv: every bus response is marked `intg_bad` (alert expected) while none is corrupted | gen_ut_boot on the Zc image, row alert_bus; re-run on the follow-up tree (CR5-L-1) | FAIL (UVM_ERROR 159: alert_major_bus_o low in an rvalid cycle marked corrupted; 159 again on the follow-up tree) | `+gen_chk_alert_bus=0`: PASS (UVM_ERROR 0, both trees) |
| MB4 | gen_tb_top.sv: the observed irq_pending pin is inverted on the way to the checker | gen_ut_boot on the Zc image, row irq_pending; re-run on the follow-up tree (CR5-L-1) | FAIL (UVM_ERROR 541: pending 1 expected 0 every checked cycle; 541 again on the follow-up tree) | `+gen_chk_irq_pending=0`: PASS (UVM_ERROR 0, both trees) |
| MB5 | gen_rvfi_pkg.sv (monitor): an entry record's pc_rdata is reported one vector higher, so the scoreboard offers the model cause + 1 and the checker sees a cause the pins never carried | gen_ut_irq on gen_irq_directed.S, row irq_entry (T-136 cause rule) | FAIL (UVM_ERROR 5 on the follow-up tree, gen_fu_MB5_*: 2 `taken line was not pending-and-enabled` such as `entry mcause 80000014 at order 302 ... (either 00080000 both 00000000)` and 3 `cause is not an interrupt line` where the shifted vector names no line; 300 on the landing-1c tree, gen_fu_l1c_MB5_*: since landing 2a the driver releases only the taken line it is told, so the shifted cause also keeps the real line held and every later entry is judged against it) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0, both trees) |
| MB6 | gen_rvfi_pkg.sv (monitor): one legal store record (the first store after order 50) is reported with `trap` set, a DUT faulting an access nobody corrupted | gen_ut_boot on the seed-7 image, `+gen_chk_isa=1`, row isa_trap (T-137 conditioned arming: no announcement, the model decides) | FAIL (UVM_ERROR 1: `isa_trap dut trapped, model retired 1 trap=0 cause=00000000` at order 469, pc 80001782, a sw) | `+gen_chk_isa_trap=0`: PASS (UVM_ERROR 0) |
| MB7 | gen_rvfi_pkg.sv (scoreboard): an interrupt or debug entry inside a Zcmp sequence counts the split but leaves the partial sequence open (the pre-T-134 behaviour) | gen_ut_boot on gen_zcmp_irq_directed.S, `+gen_knob_irq_regime=sparse +gen_knob_irq_line_mix=multi +gen_chk_isa=1`, row isa_rd | FAIL (UVM_ERROR 8: `isa_rd Zcmp union: model wrote 1 registers, dut 3` at order 1148 and the appended micro-ops' registers) | `+gen_chk_isa_rd=0`: PASS (UVM_ERROR 0) |
| MB8 | gen_tb_top.sv: the observed alert_major_internal pin is inverted | gen_ut_boot on the Zc image, row alert_internal | FAIL (UVM_ERROR 544: `alert_major_internal_o high at cycle 0` and every cycle) | `+gen_chk_alert_internal=0`: PASS (UVM_ERROR 0) |
| MB9 | gen_tb_top.sv: the observed data_tag_o pin is inverted | gen_ut_boot on the Zc image, row data_tag_quiet | FAIL (UVM_ERROR 544: `data_tag_o high at cycle 0` and every cycle) | `+gen_chk_data_tag_quiet=0`: PASS (UVM_ERROR 0) |
| MB10 | gen_tb_top.sv: the observed alert_minor pin is inverted | gen_ut_boot on the Zc image, row alert_minor | FAIL (UVM_ERROR 544: `alert_minor_o high at cycle 0 without an announced ECC injection`) | `+gen_chk_alert_minor=0`: PASS (UVM_ERROR 0) |
| MB11 | gen_tb_top.sv: the observed double_fault_seen pin is inverted (a pulse every cycle) | gen_ut_boot on the seed-7 image (one synchronous trap at order 466), row double_fault | FAIL (UVM_ERROR 2: `double_fault_seen_o pulse at cycle 1754 for a first synchronous trap (order 466)`) | `+gen_chk_double_fault=0`: PASS (UVM_ERROR 0) |
| MB12 | gen_agents_pkg.sv (gen_bus_driver): a data-side integrity corruption is announced (`note_intg`) but the response word stays clean, so the DUT raises no internal NMI | gen_ut_boot on the seed-7 image, `+gen_knob_dmem_intg_err_rate=frequent`, row nmi_internal (landing 2a) | FAIL (UVM_ERROR 28: `no internal NMI entry within 4 records outside NMI mode of the integrity corruption announced at order N`) | `+gen_chk_nmi_internal=0`: PASS (UVM_ERROR 0) |

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
| MB6 | as above | gen_ut_boot seed-7, row isa_trap | be2ad512fbd288fd | FAIL (UVM_ERROR 1): `isa_trap dut trapped, model retired 1` at order 469, pc 80001782 | PASS (0) |
| MB7 | as above | gen_ut_boot on gen_zcmp_irq_directed.S, sparse, multi, row isa_rd | 403ee454b9411265 | FAIL (UVM_ERROR 16): `isa_rd Zcmp union: model wrote 1 registers, dut 3` at order 1148 | PASS (0) |

Exact edits of the new mutants (the re-run rows keep the edits of their first table):

| mutant | file | original | mutated |
|---|---|---|---|
| RC1 | `dv/auto_dv/env/gen_rvfi_pkg.sv` (the fold return in `write`) | `if (t.intr \|\| dbg_entry) publish_state(t, pc_a, prv, csr_n);` | the line removed (`// RC1: the entry state is not published before the fold`) |
| RC2 | `dv/auto_dv/tb/gen_tb_pkg.sv` (`gen_insn_mem_access`, quadrant 0) | `3'b110: begin is_store = 1; bytes = 4; return 1; end   // c.sw` | `3'b110: begin is_store = 0; bytes = 4; return 1; end   // RC2: a c.sw fault is armed as a load` |
| RC3 | `dv/auto_dv/env/gen_checkers_pkg.sv` (gen_misc_monitor `write_state`) | `? GEN_LSU_TRAP_TO_RVFI_OFFSET : GEN_TRAP_TO_RVFI_OFFSET);` | `? GEN_TRAP_TO_RVFI_OFFSET : GEN_TRAP_TO_RVFI_OFFSET);   // RC3: one pulse offset for every trap kind` |
| RS1 | `dv/auto_dv/isa/gen_isa_shim.cc` (after `g_proc->step(1)`) | `if (g_fault.hit && g_fault.tval != 0) g_proc->put_csr(CSR_MTVAL, g_fault.tval);` | the line removed (`// RS1: the fault keeps Spike's effective-address mtval`) |
| RM-L1 | `dv/auto_dv/env/gen_agents_pkg.sv` (gen_bus_driver, the injection branch) | `p.err = 1; p.injected = 1; injected_err++;` (the `gen_bus_err_log::note(p.addr, bvif.cycle_count)` line after it kept) | `p.err = 0; p.injected = 1; injected_err++;   // RM-L1: announced, never driven` |
