# Critic verdict: tb-infra landing 2b, re-review v3 (d752fb3 with the docs deltas e534438 and the CM60 delta of 61c97c1): the M-3 closure

Base verdicts: dv/auto_dv/docs/gen_critic_tb_l2b.md (6dc57b57174842d5, REQUEST-CHANGES on M-3, committed 5378002) and
gen_critic_tb_l2b_v2.md (99c9272a5bfb2a73, the first delta e534438, HELD; L-16 and L-17 raised there, relayed as CR-2Bv2-L-16 / L-17).

Artifacts reviewed (committed blobs at 61c97c1; sha256 first 16 hex):

- dv/auto_dv/docs/gen_component_api_scoreboard.md  b48fe91239432a8c
- dv/auto_dv/mutations/gen_mut_step2b.md  4905c04b3e02ef75
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  0594b7e36aa939f5
- dv/auto_dv/evidence/gen_critic_response_fcov.md  97fb1b4119519771 (the CM60 rows)
- dv/auto_dv/tb/gen_tb_knobs.yaml  ccfa81ae18dfb171; dv/auto_dv/tb/gen_tb_pkg.sv  792452e36eb09b39
- dv/auto_dv/env/gen_rvfi_pkg.sv  7927a36ea2e6e470 (the suppressed-write acceptance unchanged since d752fb3, as the doc now states)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, gen_critic_tb_l2b.md
Sections 2 and 5 (the lift conditions), gen_critic_tb_l2b_v2.md Section 7. Method: committed blobs; the deltas read as diffs f660470..61c97c1;
the drain-window derivation checked against the driver (the announcement stamped at grant, gen_agents_pkg.sv:304-306; the regime windows
gnt_delay and rvalid_delay long / random upper bound 32, gen_tb_knobs.yaml). No subagent. No cross-model artifact is specific to this delta;
the CM60 rows come from the e534438 artifact already reconciled in v2, and the artifact for 61c97c1 was not read before this file was
written.

CRITIC VERDICT (landing 2b with the deltas e534438 and 61c97c1): APPROVE. M-3 is closed; the lift conditions of gen_critic_tb_l2b.md
Section 5 are met; M-1 is closed on the code by the template touches (T-226, gen_critic_t226_v2.md) and M-2 stays owed to landing 2c
with its four mutants named.

## 1. The M-3 closure

- gen_component_api_scoreboard.md:86 now ends "integrity-error runs stay consistency-only until the suppressed-write gate lands (T-183,
  landing 2c)." with the dangling ", no longer consistency-only" of the first delta removed (CR-2B-L-16 / CM60-L-1 closed); the
  conventions row at :132 states the acceptance on the DUT's flag alone with the gate owed to 2c (unchanged from e534438, verified in
  v2). The code it describes is unchanged (gen_rvfi_pkg.sv:464-470 accepts on t.ext_rf_wr_suppress; take_intg only for the NMI mtval).
  The document and the code agree.
- The drain window (CR-2B-L-17 / CM60-L-2): GEN_BUS_ERR_DRAIN_CYCLES is 96 in the yaml, gen_tb_pkg.sv, gen_knobs.py and gen_isa_shim_map.h,
  derived in the yaml desc and at doc:146 as the second half's grant window (at most 32) plus its rvalid window (at most 32) plus 32 for
  the response-to-record lag with margin, from the grant stamp; that is the derivation my L-17 asked for (the announcement is stamped at
  the first transaction's grant, gen_agents_pkg.sv:304-306; both regime windows' long / random bound is 32). The change is a relaxation
  of the bus_err_leftover referee by 32 cycles and is the only referee relaxation in the landing; it removes a false red, never a false
  green (a leftover after 96 cycles still fails). Closed.
- Lift condition 3 (the mutation record naming the owed SVA mutants, CM60-L-3): gen_mut_step2b.md's closing paragraph names the five
  proven groups (st, ibus, dbus, scrkey, rvfi) and one owed mutant per uncovered group with its mechanism and ablation: MS-ICRAM (the
  bind feeds ic_tag_write_o with ic_tag_req_o forced to 0 on the allocation write), MS-IRQ (irq_timer_i driven X for one cycle), MS-DBG
  (debug_req_i driven X for one cycle), MS-ALERT (the alert_major_bus_o term of sva_alert_bus_iff_intg inverted). Named; the mutants
  themselves are landing 2c's (M-2 of the base verdict stays owed with these names).
- Lift condition 4 (L-1 and L-2 of the base verdict closing with M-3): L-1 (option.weight = 0 promised and not built) and L-2 (the
  provenance sentences of the 2b transcript) are not in this delta; they stay owed to 2c as the CR-2B-L rows say. I do not hold the
  lift on them: they are record items, and the blocking medium was M-3.

## 2. Status of the base verdict's findings after the two deltas

- M-3 closed (this file). M-1 (the witness protocol alignment, T-226) closed on the code by ae4b2e2, 674d026, 5bb10e7, 99cba0e and
  ac5853e (gen_critic_t226_v2.md), the end-to-end green owed with the first witness_ids entry. M-2 (four SVA groups without a catching
  mutant) owed to 2c with MS-ICRAM / MS-IRQ / MS-DBG / MS-ALERT named. L-1 .. L-15 owed to 2c per the CR-2B rows; L-16 and L-17 closed.
- One caveat carried from gen_critic_tb_l6.md M-1: the landing-6 build's source identity does not reproduce from the commit; the
  DRAIN constant's four homes are consistent in the committed tree (yaml, SV package, Python, C header) and the docs describe the
  committed value, so this delta's closure does not depend on the build.

## 3. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S4 honesty: the scoreboard document now states what the comparator
does and what is owed (conforming); S2: the drain window derived from the mechanism that stamps the announcement (conforming); S6: the
owed mutants named in the mutation record (conforming for the record; the proofs are 2c's). One-line verdict: PASS.
