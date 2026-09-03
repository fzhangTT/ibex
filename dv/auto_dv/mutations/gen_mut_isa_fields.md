# MUT-004..MUT-007: per-field discrimination of the ISA comparator ids (gen_scoreboard)

Format: dv/auto_dv/mutations/README.md. These are TB-side mutations of the RVFI monitor's `sample()`
(`dv/auto_dv/env/gen_rvfi_pkg.sv`, class gen_rvfi_monitor): each corrupts ONE field of every record handed to
the scoreboard, standing in for a DUT that gets exactly that field wrong. They prove (a) that the named field
id fires and no other id does (discrimination), and (b) that `+gen_chk_isa_<field>=0` silences exactly it
(ablation). They do not replace the RTL-level bug-injection evidence per checker that the Test Writer owns
(agent_team_prompt.txt, Test Writer role); the classes of RTL defect each id catches are listed in
`dv/auto_dv/docs/gen_component_api_scoreboard.md` Section 5a.
Executed 2026-09-03 (T-068); module `dv.auto_dv.gen_tb.gen_tests.gen_ut_lockstep` on the directed Zc program
(`out_codegen/zc/prog.vmem`, 169 retirements, 10 cm.* sequences), seed 1, opentitan; one build per mutation
(`dv/auto_dv/work/tb-infra/out_t068_mut00N`, vcs exit 0, 0 errors). Runs per mutation: `isolated`
(`+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_<f>=1`: hidden referees inert), `default` (every check on:
discrimination), `ablation` (`+gen_chk_isa_<f>=0`, mutation applied: survives). Retained logs:
`dv/auto_dv/evidence/gen_tdd_logs/mutations/mut00N_*`; reverts verified by cmp ("sources identical to
pre-mutation", gen_mutations_driver_t068.log).

    id: MUT-004
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:82 (gen_rvfi_monitor::sample)
    original: t.rd_wdata = vif.rd_wdata;
    mutated:  t.rd_wdata = vif.rd_wdata ^ 32'h1;
    expected_detector: isa_rd (+gen_chk_isa_rd)
    result: CAUGHT: isolated 124 UVM_ERROR all [isa_rd]; default 124 UVM_ERROR all [isa_rd] (no other id);
      flow verdict FAIL (uvm_error). ablation_control: +gen_chk_isa_rd=0 -> UVM_ERROR 0, verdict PASS (SURVIVED).

    id: MUT-005
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:84 (gen_rvfi_monitor::sample)
    original: t.mem_wdata = vif.mem_wdata;
    mutated:  t.mem_wdata = vif.mem_wdata ^ 32'h1;
    expected_detector: isa_mem (+gen_chk_isa_mem)
    result: CAUGHT: isolated 8 UVM_ERROR all [isa_mem]; default 8 all [isa_mem] (the 8 full-word stores of the
      program, including the cm.push unions); verdict FAIL. ablation_control: +gen_chk_isa_mem=0 -> 0 errors,
      verdict PASS (SURVIVED).

    id: MUT-006
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:79 (gen_rvfi_monitor::sample)
    original: t.trap = vif.trap;
    mutated:  t.trap = ~vif.trap;
    expected_detector: isa_trap (+gen_chk_isa_trap)
    result: CAUGHT: isolated 148 UVM_ERROR all [isa_trap]; default 148 all [isa_trap] (one per compared record;
      the 21 folded micro-op records carry no compare); verdict FAIL. ablation_control: +gen_chk_isa_trap=0 ->
      0 errors, verdict PASS (SURVIVED).

    id: MUT-007
    file: dv/auto_dv/env/gen_rvfi_pkg.sv:83 (gen_rvfi_monitor::sample)
    original: t.pc_wdata = vif.pc_wdata;
    mutated:  t.pc_wdata = vif.pc_wdata + 32'h2;
    expected_detector: isa_pc_next (+gen_chk_isa_pc_next)
    result: CAUGHT: isolated 148 UVM_ERROR all [isa_pc_next]; default 148 all [isa_pc_next]; verdict FAIL.
      ablation_control: +gen_chk_isa_pc_next=0 -> 0 errors, verdict PASS (SURVIVED).

Not covered here: isa_pc, isa_insn, isa_prv (the forced-red run `lockstep_forced_red`, model without Zc/Zb,
shows isa_pc and isa_insn firing; isa_prv has never fired: no privilege change exists in either program).
Their per-field mutations follow with the first U-mode program.
