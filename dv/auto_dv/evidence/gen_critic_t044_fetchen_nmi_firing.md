# Critic records hand: the sva_rvfi_irq_valid_exclusive firing under a fetch-enable shape with the NMI line mix

Written 2026-09-05T09:05:48Z by the Critic, at the Orchestrator's request, so that rtl-arch's corrigendum to Section 5 of
dv/auto_dv/evidence/gen_rvfi_irq_valid_exclusive_ruling.md can cite a retained artifact. This file carries the words my
retained logs hold (dv/auto_dv/work/critic/irq1b/, README.txt there names every command); it claims nothing beyond
them. The run was a verification run of mine during the re-review of 27212cb..55ef529 (gen_critic_irq_step1.md
Section 7), not a landing's smoke, and it is not evidence about any commit's correctness.

## The run

- Build: my own compile of a detached worktree of 55ef529 with `bash dv/auto_dv/tb/gen_tb_local.sh compile`, TB-source
  identity (sources sha256, dv/auto_dv env, tb, isa, gen_tb) 1a2c9707a8a108e9, vcs exit 0. This is the identity the
  landing-46 log names for its own build.
- Program: dv/auto_dv/stim/gen_directed/gen_nmi_long_directed.S built with gen_program.py at seed 1 from that worktree
  (--gcc-opts=-Idv/auto_dv/tests/gen_programs): 220 words, crc32 0xce5633d1, entry 0x80000080.
- Run: `SEED=1 bash dv/auto_dv/tb/gen_tb_local.sh run <OUT> fetchen dv.auto_dv.gen_tb.gen_tests.gen_ut_fetch_en
  +gen_mem_image=<that vmem> +gen_mem_image_crc32=ce5633d1 +gen_mem_image_words=220 +gen_fetch_en_at_reset=0
  +gen_ut_boot_retire=800 +gen_knob_irq_regime=storm +gen_knob_irq_line_mix=with_nmi`. The NMI is raised by the
  committed driver's with_nmi arm in the same mask and event as the non-NMI lines (the raise-triggered shape); no
  take-triggered arm exists in the committed tree.

## What the run said (quoted from its sim.log as retained in fetchen_with_nmi_t044_firing.txt; line numbers are the
sim.log's)

    32:"dv/auto_dv/tb/gen_protocol_props.sv", 299: gen_tb_top.u_dut.gen_protocol_props_i.sva_rvfi_irq_valid_exclusive: started at 155000ps failed at 155000ps
    33-	Offending '(!rvfi_valid)'
    34:UVM_ERROR @ 15500: reporter [sva_rvfi_irq_valid_exclusive] GEN_PROTO sva_rvfi_irq_valid_exclusive: protocol property violated at cycle 11
    35-UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(789) @ 4398000: uvm_test_top.env.ctrl [GEN_CTRL] fetch_enable_i <= Off (FETCH_EN arg 0)
    36-UVM_INFO dv/auto_dv/env/gen_agents_pkg.sv(789) @ 4719000: uvm_test_top.env.ctrl [GEN_CTRL] fetch_enable_i <= On (FETCH_EN arg 1)

The earlier lines of the same log (quoted in Section 7's diagnosis, not retained verbatim) show the ISA model ready at
pc=80000080 mtvec=80000001 and `fetch_enable_i <= On (FETCH_EN arg 1)` at 5000 ps, so the firing at 155000 ps is
cycle 11 of the TB's cycle counter, after the release and after fetch enable, with the property's consequent
`(!rvfi_valid)` the offending term: rvfi_ext_irq_valid and rvfi_valid were both high in that cycle. The run's own
verdict (gen_verdict.decide over the logs): "verdict: FAIL / reason: assertion_failure at sim.log:33", one UVM_ERROR in
the whole run; the cocotb test itself printed GEN_UT_FETCH_EN_PASS (800 records retired by the end of the drain
window, 800 after 256 more idle cycles) and TESTS=1 PASS=1. The coverage subscriber's summary for the run: entry=60
entry_rel=60 edge=137 access=1 mie_global=1 reset=1 fetch_off=1 view misses 0.

## The control

The same build, image, seed and plusargs WITHOUT `+gen_knob_irq_line_mix=with_nmi` (run fetchen2, retained in
smokes2_summary.txt): verdict PASS, "no collected failure mechanism", 0 UVM_ERROR, entry=60 entry_rel=60 edge=122
fetch_off=1. The property fired only with the NMI mixed into the raised lines.

## What is not retained, stated plainly

The run directory lived in a scratch worktree that was removed after the re-review; the run header file, the full
sim.log and stdout.log are gone, and the lines above are the excerpt I kept before removal. A copy of the run's
vcs_simv.vdb sits in my session scratch (critic_irq1b/vdb_fetchen) and will not outlive the session; no wave was
dumped, so which line raised the notification at cycle 11 (the NMI or a regular interrupt with an empty ID stage,
rtl/ibex_core.sv:1965-1970) is not decidable from what I hold. The shape is reproducible from the recipe above on any
build of 55ef529 or later; a re-run with a dump is a compile and one run, and I can do it on request.
