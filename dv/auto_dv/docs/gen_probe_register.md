# Probe register (DV_prompt.txt Section 7 and deliverable 5)

Owner: tb-infra (entries), Critic (approval). Version 2, 2026-09-03: statuses set to the Critic's
binding rulings in `dv/auto_dv/work/critic/gen_critic_tb_arch_components_v1.md` C8. Every
internal probe the TB may read is listed here BEFORE it is used; the Critic may reject any entry.
Rule (DV_prompt Section 7): models consume only the inputs the TB drives; probing internal state is
allowed only where the starting state is genuinely unknowable from intent. No checker depends on
any probe below; every entry is coverage-only or debug-only except where the status column names
the one permitted pass/fail use. Hierarchical paths resolve only through the binds home
(`dv/auto_dv/tb/gen_binds.sv`, component API `gen_component_api_binds.md`); `<dut>` =
`gen_tb_top.u_dut`. No per-cycle Python polling exists anywhere in the TB (component sections C2,
A-01); no polling waiver is requested or granted.

Status values: `boundary` (not a probe, listed for transparency), `accepted` (with the recorded
conditions), `conditional` (accepted for the stated use only, re-review named), `rejected` (stays
in the table; re-apply only with the stated evidence), `off` (present as code, disabled by
default, never used for pass/fail, never enabled in a measured regression).

| Id | Signal(s) | Hierarchical path (via binds home) | Feature(s) served | Use | Rationale: why intent cannot supply the value | Boundary alternative | Status (Critic ruling) and conditions |
|---|---|---|---|---|---|---|---|
| RVFI | `rvfi_*` ports of ibex_core under `+define+RVFI` | `<dut>.rvfi_*` (wrapper ports) | ISA comparison of every retired instruction; all F-RVFI-* | checking (the retirement trace) | not a probe: a define-gated DUT verification interface at the module boundary, zero-cost when undefined | none | `boundary` (ACCEPTED as a boundary interface, not a probe; recorded so the register lists everything the TB reads inside gen_dut_top) |
| P1 | `dummy_instr_id`, `dummy_instr_wb`, `rf_raddr_a`, `rf_raddr_b`, `rf_waddr_wb`, `rf_we_wb` (core-to-register-file seam nets inside the wrapper; ibex_core PORTS) | `<dut>.dummy_instr_id`, `<dut>.dummy_instr_wb`, `<dut>.rf_raddr_a`, `<dut>.rf_raddr_b`, `<dut>.rf_waddr_wb`, `<dut>.rf_we_wb` | F-DIT-011, F-DIT-013 (dummy insertion rate per mask value, dummy kind, x0 write); BUG-02/B7 quantification (dummy instructions counted by minstret, F-DIT-018) | coverage; the dummy-count reproducer for the minstret bug candidate | insertion cycles come from the RTL LFSR (rtl/ibex_dummy_instr.sv:60-75) and security.rst:44-47 says only "random intervals", so intent cannot supply them; dummies are excluded from RVFI (`rvfi_stage_valid_d[0] = rvfi_id_done & ~dummy_instr_id`, rtl/ibex_core.sv:1867); the nets are ibex_core ports wired inside gen_dut_top, not RTL-internal nets | RVFI retirement-gap inference (weak); `>=` check of `minstret` | `accepted` for coverage and the BUG-02/B7 quantification only: observation-only bind in gen_binds.sv on the seam nets (no reference below ibex_core); the only pass/fail use is the dummy-count reproducer for the minstret bug candidate, reported as such; the trusted `ctr_minstret` rule with dummies on stays `>=`; the bind's failure on a renamed net identifies itself |
| P2 | icache hit/miss and fill-buffer state (`tag_hit_ic1`, `lookup_valid_ic1`, `fill_busy_q`) | `<dut>.u_ibex_core.if_stage_i.gen_icache.icache_i.{tag_hit_ic1, lookup_valid_ic1, fill_busy_q}` | icache hit/miss/allocation features | coverage | (claimed) hit/miss decided inside the cache | tag-RAM model sees every lookup (tag read of both ways on `ic_tag_req_o`); a miss is followed by an `instr_req_o` fill of that line, a hit is not; the ibus agent sees the fills | `rejected` for now: derivable at the boundary; re-apply only with URG evidence that the derived bins stay unreachable after a closure round |
| P3 | fill-buffer occupancy | `<dut>.u_ibex_core.if_stage_i.gen_icache.icache_i.{fill_busy_q, fb_fill_level}` | "buffer full" edge case (F-IMEM-008) | coverage | (claimed) occupancy is internal | equals granted-unanswered fetches, counted exactly by the ibus agent (`ibus_outstanding`); "buffer full" is `outstanding == GEN_IBUS_MAX_OUTSTANDING` | `rejected` |
| P4 | controller FSM state and the RTL's own `fcov_*` nets | `<dut>.u_ibex_core.id_stage_i.controller_i.{ctrl_fsm_cs, fcov_interrupt_taken, fcov_debug_entry_if, fcov_debug_entry_id, fcov_pipe_flush, fcov_debug_wakeup}` (rtl/ibex_controller.sv:1085-1095) | crosses "interrupt / debug request / fetch error arrives in FLUSH, WAIT_SLEEP, SLEEP, IRQ_TAKEN" | coverage sampling only | the cycle in which the controller enters a state is pipeline timing no specification defines, and FSM code coverage cannot express a cross with stimulus timing | FSM code coverage for the states themselves; boundary timing approximates the crosses | `conditional`: coverage sampling only, never a checker input; each cross names the feature it serves; bind through gen_binds.sv; the `fcov_*` nets exist only when `DV_FCOV_DISABLE` is undefined (the TB build never defines it); re-review when the cross list exists |
| P5 | icache IF-side handshake `valid_o`, `ready_i`, `rdata_o` | `<dut>.u_ibex_core.if_stage_i.gen_icache.icache_i.{valid_o, ready_i, rdata_o}` | F-FE-012 | (proposed) coverage | the ready/valid seam has no boundary port | `instr_req_o` pause length vs retirement gaps correlated with the dbus stall; the stability rule is the RTL's own assertion (assertion coverage) | `rejected` for checking; not approved for coverage now; F-FE-012 bins use the boundary derivation first; re-apply with URG evidence |
| P6 | CSR flops `mstatus_q`, `mie_q`, `mtvec_q`, `pmpcfg`/`pmpaddr`, `dcsr`, and `csr_wdata_int` | `<dut>.u_ibex_core.cs_registers_i.{...}` | debugging of read-back mismatches; F-CSR-001 internal observable | debug-only compare "model == RTL CSR state" | not needed for checking: CSR state is knowable from intent (reset values plus retired CSR writes plus trap entry/exit); F-CSR-001's checked observable is `rvfi_rd_wdata` plus the C6 read-back | the CSR observability plan (component sections C6) | `off`: accepted as a debug-only aid; knob `+gen_dbg_csr_probe=1` declared once; never enabled in a measured regression (the flow fails a measured run that has it on); the message names itself as a model-versus-RTL debug compare, not a DUT failure; not counted as a checker in the trust-triad evidence |

## Rejected or withdrawn candidates

- LSU misaligned bookkeeping (`fcov_mis_rvalid_1/2`, `fcov_mis_bus_err_1_q`, rtl/ibex_load_store_unit.sv:767-797): withdrawn by tb-infra; the dbus monitor sees both halves and the error.
- P2 and P3 above: rejected by the Critic (boundary-derivable); kept for the record.

## Process

1. A new probe is added here with all columns filled and status `proposed` before any bind
   references it.
2. The Critic records the decision (accepted / conditional / rejected / off) with its conditions in
   the status column; a rejected entry stays in the table for the record.
3. An accepted or conditional probe is bound in `gen_binds.sv` only; the failure message of any
   monitor on it identifies itself ("probe P<n> moved/renamed") so a design rename never looks like
   a DUT bug (dv_principles Section 2).
4. Every probe is coverage-only or debug-only unless its status names the one permitted pass/fail
   use (today: P1's dummy-count reproducer for BUG-02/B7).
