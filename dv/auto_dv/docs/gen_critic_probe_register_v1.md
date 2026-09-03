# Critic approval: probe register v2 (DV_prompt.txt Section 7, deliverable 5)

- Artifact: dv/auto_dv/docs/gen_probe_register.md (sha256 first 16: 0559da90b551d449), committed at
  d449af7 (T-031), version 2.
- Rulings it transcribes: dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md C8 (P1..P6)
  and A-16 (RVFI is a boundary interface, not a probe); A-01 (no per-cycle Python polling).
- Date (UTC): 2026-09-03 06:56
- Reviewer role: critic. Probe-register entries are the Critic's approval duty (DV_prompt.txt
  Section 7); this file is the recorded approval for the entries as committed.

CRITIC VERDICT: APPROVE

## Entry-by-entry check against the rulings

| Entry | Register status | My C8 ruling | Conditions carried over | Faithful |
|---|---|---|---|---|
| RVFI | boundary | A-16: define-gated DUT verification interface at the wrapper boundary, not a probe | listed for transparency only | yes |
| P1 seam nets (dummy_instr_id/wb, rf_raddr_a/b, rf_waddr_wb, rf_we_wb) | accepted (coverage and BUG-02/B7 quantification only) | ACCEPTED for coverage and the BUG-02/B7 quantification only | observation-only bind on ibex_core ports, no reference below ibex_core; the one pass/fail use named; ctr_minstret rule stays >=; LFSR rationale with RTL and doc cites; self-identifying failure on rename | yes, all four |
| P2 icache hit/miss internals | rejected | REJECTED for now | boundary derivation stated; re-apply only with URG evidence after a closure round | yes |
| P3 fill-buffer occupancy | rejected | REJECTED | ibus_outstanding derivation stated | yes |
| P4 ctrl_fsm_cs and fcov_* nets | conditional (coverage sampling only) | CONDITIONALLY ACCEPTED for coverage sampling only | never a checker input; each cross names its feature; bind via gen_binds.sv; DV_FCOV_DISABLE dependence stated; re-review when the cross list exists | yes, all five |
| P5 icache valid/ready/rdata seam | rejected for checking; not approved for coverage now | REJECTED for checking; NOT approved for coverage now | boundary derivation first; re-apply with URG evidence | yes |
| P6 CSR flops and csr_wdata_int | off (debug-only aid) | ACCEPTED as a debug-only aid | default off; knob declared once; never in a measured regression, flow refuses; message names itself as a model-versus-RTL compare; not counted as a checker | yes, all five |

The withdrawn LSU misaligned bookkeeping candidate is recorded as withdrawn with the boundary reason,
which is right. The process section matches DV_prompt.txt Section 7 (entry before use; Critic may
reject; self-identifying monitors).

## Findings

F-01 (low, open loop). The register names the P6 knob `+gen_dbg_csr_probe=1`, but gen_tb_pkg.sv
declares no PLUSARG_ for it yet and the testlist header `debug_only_plusargs` is still empty
(Runtime is waiting for TB Infra to name the knob). The flow's refusal, which P6's approval
depends on, is therefore not yet armed for this knob. Required before the P6 code is bound: declare
PLUSARG_DBG_CSR_PROBE once in gen_tb_pkg.sv and list `gen_dbg_csr_probe` in
gen_testlist.yaml debug_only_plusargs; the retained refusal run regress_t045_p6_refusal shows the
mechanism works for a listed name.

F-02 (info). The status-values paragraph enumerates boundary, accepted, conditional, rejected and
off, while process step 1 introduces `proposed`; add it to the list so the two agree.

## Fence and method record
Inputs: the register, my C8 rulings, gen_tb_pkg.sv, gen_testlist.yaml. No RTL re-read was needed:
the RTL citations in the register (rtl/ibex_dummy_instr.sv:60-75, rtl/ibex_core.sv:1867,
rtl/ibex_controller.sv:1085-1095) are the ones my C8 table verified. No fence event.
