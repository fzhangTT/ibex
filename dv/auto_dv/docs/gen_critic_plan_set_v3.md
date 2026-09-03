# Critic verdict: plan set v2b, third review (commit bc9dba9; T-007 part 2 and T-034 rows re-judged)

Artifacts at commit bc9dba9 (sha256 first 16 hex, lines):
- dv/auto_dv/docs/gen_test_plan.md         7b695dd5d8bb9ed2  23010 (1203 items, 226 groups, 29 expected-fail, 11 informational)
- dv/auto_dv/docs/gen_fcov_plan.md         7fe105646ce2ca41   6975 (207 covergroups, 15825 bins, 74 regression-level coverpoints)
- dv/auto_dv/docs/gen_feature_list.md      e32f77a29f7a1152  13607 (1017 IDs, 705 ACTIVE)
- dv/auto_dv/docs/gen_bug_log.md v1f       b7a0f0c73b8b59f9    269
- dv/auto_dv/tools/gen_trace_check.py      a0dbff079a0b1334     77
- dv/auto_dv/docs/gen_trace_tp_bin.csv     08db1580a560c114  24779
- dv/auto_dv/evidence/gen_critic_response_plan_set_v1.md  81111981fa6c518a  177 (Sections 1-5)
Date: 2026-09-03T10:06Z   Role: Critic   Previous: gen_critic_plan_set_v1.md (T-007 part 2, REQUEST-CHANGES: H-1, H-2, M-1..M-12,
L-1..L-8) and gen_critic_fcov_drafts_prereview_v1.md (T-034 advisory). The round-3 cross-model artifact was not read.

CRITIC VERDICT: REQUEST-CHANGES (one medium; everything else verified, see section 2)

The plan set now does what the two earlier verdicts asked. The one remaining defect is small in text and real in
effect: two expected-fail items for two different bugs share one _xfail test group, which the plan's own convention
forbids and which the flow's single-bug XFAIL attribution cannot handle. One group split closes this verdict; the
re-review is a grep of Section 3.

## 1. Findings

### M-1 (medium): gen_prv_debug_xfail mixes B1 and B2

- gen_test_plan.md:197 (Section 3) and the items: gen_prv_debug_xfail hosts TP-PRV-014 (expected-fail B1, MPRV kept on
  dret to U) and TP-PRV-035 (expected-fail B2, MPRV honoured in debug mode). Section 0 (:44-47) and C-15 say an
  expected-fail item is its own _xfail test, and the response file (Section 3 row M-12, Section 4 counts) claims
  "every expected-fail / informational item in its own _xfail / _info group". Four items break it (this pair and the
  B15 pair in L-2).
- Effect: the Test Writer's template names ONE bug per test (xfail_bug; GEN_TEST_XFAIL <Bn>) and the acceptance rule
  (plan section 4 item 5) requires the first failing line to name that bug. A two-bug test cannot; and when B1 is
  fixed while B2 stays open the test still XFAILs, so the B1 fix is never seen as an unexpected PASS.
- Required: split into gen_prv_debug_mprv_dret_xfail (TP-PRV-014) and gen_prv_debug_mprven_xfail (TP-PRV-035) (names
  are the DV Lead's); regenerate Section 3 and the counts; correct the response row to the real count.

### Lows

L-1 Informational count. The plan has 11 informational items (TP-ISA-051, TP-ISA-057, TP-EXC-065, TP-DBG-011, TP-IMEM-040,
  TP-DMEM-062, TP-DMEM-063, TP-IC-038, TP-SEC-010, TP-SEC-011, TP-RVFI-039); the response file and the request say 5 (the
  bug-tied ones). Section 1's count table has no informational row. Add the row with both numbers.
L-2 gen_csr_debug_csr_xfail hosts TP-CSR-075 and TP-CSR-076, both B15. Same bug, so attribution holds, but the
  convention says one item per _xfail test; split it with M-1 or amend the convention to "one bug per _xfail test".
L-4 Regime groups CG-REG-003 / CG-REG-004 credit the irq and debug regimes on the driver's first assertion edge (stimulus),
  not on a DUT response under the regime; acceptable for a regime-ran proof because the DUT response is covered by the
  IRQ / DBG groups, but the Sample line should say so.
L-5 One Phase-2 stimulus line (gen_test_plan.md:22782, "all instr_mix values over the regression") uses the regression
  wording that C-16 bans for fire-checks; it is a stimulus statement, so no defect, but the phrase invites the old reading.

## 2. Verified at bc9dba9

- gen_trace_check.py, run by me from a clean archive of the commit (docs and tools only): PASS; features 1017
  (705 ACTIVE), TP items 1203, covergroups 207, bins 15825/15825 (49 adopted), ACTIVE->TP 705/705, ACTIVE->bin
  705/705, coverpoints 2278 of which 74 regression-level (listed in fcov Section 1.1, reported not failed).
- H-1: the six fire-checks now key on rvfi_trap = 0 plus the DmHaltAddr fetch (TP-DBG-022/028/046/067, TP-TRG-020;
  TP-DBG-027 keeps rvfi_trap == 1 only for its exception-path variant); CG-DBG-003's Sample states both paths
  correctly (rtl/ibex_core.sv:1885-1886); CG-DBG-006 carries ebreak_dbg x one_trap as an ignore with the reason
  (gen_fcov_plan.md:3187), the former ebreakdbg_trap bin is gone.
- H-2: REG groups credit the first regime-relevant event (bus grant / errored beat / injection / retired mcounteren
  write; CG-REG-007 one instant); the tautological guards are replaced by decoded-op conditions; CG-CSR-017
  cp_alert_int RETIRED, CG-PMP-005 sampled per check event, CG-PMP-012 gated on a live redirection source, CG-DBG-012
  req0_mode0 marked witness / not in manifest, CG-PMC-008 iff-guarded, CG-SEC-001 and CG-CHERI-001 zero bins carry
  activity qualifiers; CG-PRV-001 samples privilege-transition events.
- M-1: F-DBG-044, F-IRQ-051, F-DBG-059 rewritten (FLUSH -> DBG_TAKEN_IF, core_busy_o stays On; F-DBG-059 port-level).
- M-2 / M-12 (except the medium above): 29 expected-fail items over B1-B5, B7, B8, B10, B11, B13, B15, B16, B17 match
  Section 1.1 row for row; B12 items pass with the note; B14 items informational; 25 of 29 expected-fail and all 11
  informational items sit alone in an _xfail / _info group.
- M-3: TP-CSR-074 never writes bit 13 (readback rule predicts 0); TP-CSR-075 expected-fail B15; TP-CSR-108 reads no B3
  CSR (pass, doc mismatch D4); TP-CSR-066 dummy_instr_en = 0 precondition.
- M-4: no fire-check uses regression-level wording (the three remaining matches are the convention text itself and one
  Phase-2 stimulus line, L-5).
- M-5: adoption policy in fcov Section 0 (:47), 49 adopted bins counted separately, 18 "coincides with" marks.
- M-6: 74 regression-level coverpoints owned by groups in Section 1.1; the checker reports the count (decided
  alternative, accepted).
- M-7: 182 ignore_bins with reasons; probe-pending marks on the four groups (5 marks); "(B3 evidence)" / "(B5
  evidence)" on the CG-CSR-008 and CG-DBG-007 rows.
- M-11: Section 0a concordance (plan id -> architecture ids -> knobs) with the test-level compares named for the bug
  candidates without a C5.3b row.
- Conventions sampled against the RTL (6 of 16): C-1 (rtl/ibex_core.sv:2084 `pc_set ? branch_target_ex : pc_if`;
  pc_set in FLUSH at rtl/ibex_controller.sv:826-833 and :953-965), C-4 (rtl/ibex_core.sv:648 gating; rtl/ibex_icache.sv
  :249, :756, :1030-1031, :1304), C-6 (rtl/ibex_cs_registers.sv:924; rtl/ibex_controller.sv:490, :498-500), C-9
  (rtl/ibex_id_stage.sv:1059-1062; rtl/ibex_wb_stage.sv:212-215), C-12 (rtl/ibex_core.sv:2263-2267, :2156-2157,
  :2164), C-13 (rtl/ibex_core.sv:1965-1971 and the three stage copies). All six read as the plan states them.
- Expected-fail and informational items cannot go green without the DUT: every one of the 29 fire-checks asserts a
  per-seed count of observed DUT events (retirements, RVFI records, read-backs, alert pulses) and names a spec-direction
  checker or test-level compare; every informational fire-check asserts that its scenario fired (C-15).
- Bug log v1f carries B16..B19 (B19 = BUG-11), D20, D21 and S4 as the response says.

## 3. What closes this verdict

The M-1 group split (and, if the DV Lead prefers, the L-2 one) with the counts and the response row corrected. I re-check
Section 3 and the two items on that commit; nothing else is re-opened.
