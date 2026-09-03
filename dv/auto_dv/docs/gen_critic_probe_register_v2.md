# Critic ruling: probe register version 3, row P-MD (commit df83749)

Artifact: dv/auto_dv/docs/gen_probe_register.md, version 3 (P-MD proposed by tb-infra at rtl-arch's request)
sha256 (first 16 hex): 898c93ada6776463   Date: 2026-09-03T09:49Z   Role: Critic
Inputs read: the P-MD row; dv/auto_dv/work/rtl-arch/gen_multdiv_bound_props.md (rows MD-1..MD-5, covers
MD-C1..MD-C4) and module gen_sva_multdiv in gen_protocol_props_draft.sv (working drafts, cited as such);
rtl/ibex_multdiv_fast.sv, rtl/ibex_ex_block.sv, rtl/ibex_core.sv; doc/03_reference/instruction_decode_execute.rst.
Previous ruling: gen_critic_probe_register_v1.md (version 2, APPROVE).

CRITIC VERDICT: APPROVE (P-MD accepted for assertion and coverage use, under the conditions in section 2)

## 1. Why the probe is admissible

- The observed quantity has no boundary image. valid_o of ibex_multdiv_fast has no port; the only boundary trace
  is the RVFI mcycle delta between a divide and a back-to-back single-cycle predecessor, valid only with no fetch
  stall, dummies off and no mcycle write. The row keeps that delta as the boundary bins (37 / 2 / 1 / 2) and the
  end-to-end check, which is the pairing dv_principles S2 asks for.
- The expectation is documented intent, not an RTL mirror: doc/03_reference/instruction_decode_execute.rst:147
  ("takes 37 cycles to compute ... only requires 2 cycles when there is a divide by 0") and :125 (MUL in 1 cycle,
  MULH-class in 2) state the bounds the properties assert. The state-sequence property (MD-4) and the
  hold-unreachability argument (MD-3, X-12) are RTL-structural; they are admissible as always-true invariants in
  shared infrastructure (S3), not as checks of DUT behaviour against intent, and their value is the loud failure on
  a change of the FSM or of the ready relation.
- Path: rtl/ibex_core.sv:863-867 instantiates ex_block_i; the generate block gen_multdiv_fast
  (rtl/ibex_ex_block.sv:165) holds the fast instance; md_state_q (:93), div_counter_q (:78) and mult_state_q are
  the named nets; md_fsm_e is a module-local typedef (:92), so the bind must mirror the encodings (the row says so).
- No checker or scoreboard consumes the nets (row text and register rule); the assertions carry their own ids and
  knobs, so the one permitted pass/fail use is named in the status column as the rule requires.

## 2. Conditions

- C-1 Pass/fail use is limited to the properties MD-1..MD-5 as listed; every property reports through the
  GEN_PROTO_ERROR macro with its own id and `+gen_chk_<id>` knob, and the failure message names the probed
  instance so a renamed or moved net reads as "probe moved", not as a DUT bug (S2).
- C-2 The mirrored encodings are guarded by behaviour, not by a comment: MD-4 (only-successor sequence) fires on any
  encoding drift, and the covers MD-C1..MD-C3 are declared bins of the divide tests, so an encoding drift that
  merely silences the properties shows up as unhit bins (fcov-expectation). Both must be in place when the bind
  lands in gen_binds.sv.
- C-3 Mutation-proof per property before measured use (trust triad rule 2): one named mutation per row from the
  table's mutation-class column, caught by the named id with the other checks off, plus the ablation control.
- C-4 MD-C4 (`MD_FINISH && !multdiv_ready_id_i`) is the expected-zero cover behind the X-12 exclusion evidence; it
  is recorded as EC-4 material for the exclusion set, and a hit is a finding against X-12, never a pass.
- C-5 The bind resolves the path only through the binds home (gen_binds.sv); no other file spells it. I check the
  landed gen_binds.sv against this row when TB Infra offers it.

## 3. Not granted

No per-cycle Python polling (none requested). No model or checker input from these nets. No use of div_counter_q
beyond the bound and sequence properties and their covers.
