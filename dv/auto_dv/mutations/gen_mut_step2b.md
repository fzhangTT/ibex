# Mutation record: step-2b agents and boundary checkers (MB1..MB4, T-090)

Owner: tb-infra, 2026-09-03. Every mutant is built OUT OF TREE (a scratch copy of dv/auto_dv with every other clone entry
symlinked; the runner prints the shared tree's file sha256 after each mutant, unchanged throughout:
gen_tdd_logs/mutations/gen_t090_oot_mutation_batches.log). Vehicle: gen_ut_boot (boot, retire N, tohost) with hidden
referees inert, `+gen_chk_all=0 +gen_chk_<row>=1` for the catch and `+gen_chk_<row>=0` for the ablation; the isa rows stay
silenced in both, the model steps regardless (Section 4 of gen_tdd_step2b.md). Programs: gen_irq_directed.S (interrupts
enabled, vectored table of mrets), the seed-7 riscv-dv image, the Zc directed image.

| Id | Mutation (a TB-side defect at the DUT boundary) | Catching run and knobs | Catch result | Ablation |
|---|---|---|---|---|
| MB1 | gen_tb_top.sv: the fast interrupt lines are cut between the driver and the DUT (`irq_fast = '0`), the driver still raises and publishes them | gen_ut_boot on gen_irq_directed.S, `+gen_knob_irq_regime=storm +gen_knob_irq_line_mix=multi`, row irq_entry | FAIL (UVM_ERROR 66: raised, enabled lines not taken within GEN_IRQ_ENTRY_BOUND_RECORDS records; 367 entries on the connected lines) | `+gen_chk_irq_entry=0`: PASS (UVM_ERROR 0; the 8744 irq_pending mismatches the cut also causes stay silenced) |
| MB2 | gen_agents_pkg.sv: gen_dbg_driver publishes the request but drives `req` low | gen_ut_boot on the seed-7 image, `+gen_knob_debug_req_regime=storm`, row dbg_entry | FAIL (UVM_ERROR 30: 46 requests, 0 entries, 30 bound failures) | `+gen_chk_dbg_entry=0`: PASS (UVM_ERROR 0) |
| MB3 | gen_agents_pkg.sv: every bus response is marked `intg_bad` (alert expected) while none is corrupted | gen_ut_boot on the Zc image, row alert_bus | FAIL (UVM_ERROR 159: alert_major_bus_o low in an rvalid cycle marked corrupted) | `+gen_chk_alert_bus=0`: PASS (UVM_ERROR 0) |
| MB4 | gen_tb_top.sv: the observed irq_pending pin is inverted on the way to the checker | gen_ut_boot on the Zc image, row irq_pending | FAIL (UVM_ERROR 541: pending 1 expected 0 every checked cycle) | `+gen_chk_irq_pending=0`: PASS (UVM_ERROR 0) |

Discarded form MB1a (recorded, not counted): the irq driver publishing its levels but never driving the pins. Both runs
PASS with the rows on: gen_irq_checker reads the interface pins, so a driver that lies about its own pins is invisible to
a checker of the DUT by design; the DUT-boundary cut (MB1) is the defect class the row exists for.

Two invalid attempts before these results, kept in the batch log: (1) gen_ut_lockstep as the vehicle under
`+gen_chk_all=0` fails on its own compared-record count when the isa rows are off, so no ablation could pass; (2) with the
isa rows off the scoreboard did not build the model at all, so gen_irq_checker and gen_dbg_checker received no model
state and MB1/MB2 could not be caught. The second is a real isolation defect, fixed in this landing: the model steps and
publishes in every run and the knobs silence only the isa_* rows (gen_e_lockstep_zc_isaoff_t090 shows the lock-step test
green under +gen_chk_all=0). Not covered: double_fault (needs a program with a second synchronous trap without mret),
alert_internal and data_tag_quiet (never-high rules; a mutation would be the wiring of an always-low pin, deferred),
irq_masked / dbg_masked (need a program masking MIE / entering debug with a pending interrupt).
