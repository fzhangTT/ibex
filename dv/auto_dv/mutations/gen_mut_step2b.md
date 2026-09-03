# Mutation record: step-2b agents and boundary checkers (MB1..MB4, T-090) and the follow-up landing (MB5..MB11)

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
| MB5 | gen_rvfi_pkg.sv (monitor): an entry record's pc_rdata is reported one vector higher, so the scoreboard offers the model cause + 1 and the checker sees a cause the pins never carried | gen_ut_irq on gen_irq_directed.S, row irq_entry (T-136 cause rule) | FAIL (UVM_ERROR 5: `entry mcause 80000014 at order 302: taken line was not pending-and-enabled (either 00080000 both 00000000)`, one per entry; the same on the landed tree, gen_fu_MB5_*) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0) |
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
