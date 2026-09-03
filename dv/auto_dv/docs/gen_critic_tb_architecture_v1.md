# Critic verdict: adopted TB architecture document, top half and fold-in fidelity (T-011 part 2)

Artifact under review: dv/auto_dv/docs/gen_tb_architecture.md, sha256 9e830bf1b08f34d1, 1287 lines, committed in
a4795a7 (file mtime 06:59:59Z, adopted 07:04Z per its header).
Inputs read alongside:
- TB Infra component sections v2 as I reviewed them in gen_critic_tb_arch_components_v2.md (sha256 d8202876b9bef393;
  reconstructed from my saved review copy and hash-verified, see Section 1) and the current working file
  dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md version 3 (sha256 b9a3cc16eccec313, 856 lines, 07:19:52Z).
- dv/auto_dv/work/rtl-arch/gen_arch_v2_rtl_factcheck.md (sha256 ea0f321a3b09f7ba); dv/auto_dv/docs/gen_intervention_log.md
  entries Q-014 and R-002; dv/auto_dv/flow/gen_testlist.yaml and gen_flow_const.py (working tree) for the rulings' follow-through;
  dv/auto_dv/docs/gen_bug_log.md v1a; rtl/ibex_core.sv and dv/auto_dv/tb/gen_dut_top.sv port lists.
Date: 2026-09-03 (UTC)
Role: Critic (second reviewer of the architecture as a whole; the component half is approved in
dv/auto_dv/evidence/gen_critic_tb_arch_components_v2.md)
Scope: Sections 0-5 and 7-8 (scoping answers, checking strategy, language split, stimulus, the two rulings, open
questions, DV Lead notes) and the fidelity of Section 6 to the reviewed component text.

CRITIC VERDICT: APPROVE

The document is a faithful adoption of the approved component sections with the DV Lead's rulings recorded where the
team will read them. Six low findings, none of which changes what a component author would build; the first two are
one-line text fixes and the third is the re-adoption that TB Infra's version 3 now makes due.

## 1. Fold-in fidelity (Section 6)

Method: my review copy of the v2 text (the two saved reads from T-011 part 1 v2) was concatenated and hashed:
sha256 d8202876b9bef393, identical to the hash in my v2 verdict, so the comparison base is exactly the text I approved.
Section 6 (document lines 243-1175) was then diffed against it with heading depth flattened and blank lines removed.

| Difference | Lines | Judgement |
|---|---|---|
| The v2 title line replaced by the 6.0 preamble ("The text below is ... version 2 in full; only the heading depth is shifted") | 5 | expected |
| Appended 6.12 (per-component API document list) and 6.13 (rtl-arch T-051 corrections, binding wording) | 76 | expected additions, not edits |
| Any change inside the embedded body | 0 | faithful |

6.13 carries the eight T-051 corrections verbatim from the fact-check's Section 4 and the predicted C4.8 values; I
verified those corrections in the RTL for my component v2 verdict (F-01..F-05 there). The clause "Until then this
subsection is the binding wording" is the right interim rule for a document that embeds v2 while the corrections are
being folded.

## 2. Scoping answers (Section 1)

1.1 restates the boundary interfaces consistently with C1-C3 and the probe rulings: rvalid-only-when-granted rule with
the TB self-check, GEN_IBUS_MAX_OUTSTANDING = 4 x 2, GEN_DBUS_MAX_OUTSTANDING = 2, image contract with CRC-32 and
MEM_PEEK, RVFI as a boundary interface. One defect, L-1: the scramble-key paragraph names `scramble_key_i` and
`scramble_nonce_i` (:53-54) and the static-controls paragraph names `ram_cfg_i` (:70); neither ibex_core nor gen_dut_top
has these ports (rtl/ibex_core.sv port list: only ic_scr_key_valid_i / ic_scr_key_req_o; the embedded C1 at :338-339
correctly lists them as ibex_top-only). 1.2 states the probe outcome correctly ("zero checker probes" met; P1
coverage-only plus the BUG-02 reproducer; ctr_minstret bound with dummies on). 1.3 and 1.4 match C10/C11.

## 3. Checking strategy (Section 2)

2.1 states the ISA-model decision, its evidence (two link tests) and the split between the comparator rows and the
own checkers correctly, including the C5.3a/C5.3b direction and the expected_fail rule. 2.2 states the failure paths,
the isolation knobs and the exactness classes with the 6.13 constant names (GEN_CSR_WRITE_TO_RVFI_OFFSET = 2,
GEN_TRAP_TO_RVFI_OFFSET = 1, alert_bus exact, entry bound 17). One stale phrase, L-2: 2.1 (:131) still says "core_busy
(including the WAIT_SLEEP one-cycle dip)", which 6.13 item 1 and 8.2 item 1 correct to the port-level rule.

## 4. Language split and stimulus (Sections 3-4)

Conformant with DV_prompt Section 9: SV/UVM owns cycle-fidelity components, Python owns orchestration and layers 2-3,
C++ owns the shim, the bridge is edge-driven and the document states "No per-cycle Python polling exists anywhere in
the TB". Per-transaction randomization in SV is justified as the Section 9 exception and documented as compliant. The
program path (4.1) matches the T-023/T-025 evidence it cites; the one-seed rule (4.2) matches SIM_RECIPE Section 5.
L-4: 4.2 names the regime knobs `+gen_<agent>_regime` / `+gen_regime_pin` / `+gen_regime_sched` while the coverage plan
uses `+gen_knob_<name>` and TB Infra's v3 has moved to `+gen_knob_<agent>_<knob>` (v3, DV Lead alignment marks); 8.3.4
already assigns the mapping to the codegen; the text here follows at re-adoption.

## 5. The two rulings (Section 5)

| Ruling | Recorded | Consistency | Follow-through seen |
|---|---|---|---|
| Measured code-coverage scope = gen_tb_top.u_dut.u_ibex_core and u_dut.u_register_file; wrapper informational | intervention log Q-014 (owner-visible) and R-002 | matches my recommendation (gen_critic_t010_dv_principles_v2.md Section 5) and the T-010 numbers (312 of 2420 wrapper toggle objects); reason (DV-authored wiring, control ports not excludable as data path) is sound | gen_testlist.yaml builds.*.cov_trees = [u_dut.u_ibex_core, u_dut.u_register_file] for both builds; the informational third +tree is not yet in the testlist (L-6) |
| -cm_glitch 0 for every measured build | R-002 (informs LOG-007/008) | matches LOG-007/008/008a and my T-040 N-2 conditions: recorded before the first measured regression, flag stated in every report header, FSM not filtered noted, baseline re-measured | gen_flow_const.py RULING_GLITCH and GLITCH_FLAGS = ("-cm_glitch", "0") in the working tree (Runtime, uncommitted at review time) |

## 6. DV Lead notes (Section 8) and open questions (Section 7)

8.1.5 fixes the checker direction per bug candidate exactly as the bug log v1a and my S-1 have it (B12 documented
behaviour with a design note; B14 downgraded pending the confirmation simulation; spec-violation rows B1/BUG-06,
B2/BUG-01, B3, B5, B15/BUG-03). 8.2 lists the eight T-051 corrections with the predicted constants. 8.3 anticipates the
plan-set alignment items that my plan-set verdict (gen_critic_plan_set_v1.md) now requires: 8.3.1 the rvfi_trap = 0
rule for ebreak-into-debug (its H-1), 8.3.3 the mapping of the requested checkers onto architecture ids (its M-11),
8.3.4 the knob-name mapping, 8.3.5 the P7 probe entry (its M-7). The plan set at HEAD does not yet apply 8.1.5 or 8.3.1;
that is the plan set's REQUEST-CHANGES, not this document's. Section 7 reproduces the pending owner questions with the
defaults in force; Q-011's note on gen_mie_csr_t matches link test 2.

## 7. Findings (all low)

L-1 Section 1.1 names ports the DUT does not have: `scramble_key_i`, `scramble_nonce_i` (:53-54) and `ram_cfg_i` (:70).
The scramble-key responder drives only `ic_scr_key_valid_i` in answer to `ic_scr_key_req_o`; key and nonce material
lives in ibex_top's RAM scrambling, outside this DUT. Delete the three names (C1 :338-339 is authoritative).

L-2 Section 2.1 (:131) "core_busy (including the WAIT_SLEEP one-cycle dip)": replace with the port-level rule of 6.13
item 1.

L-3 Version lag. TB Infra's working file is now version 3 (sha256 b9a3cc16eccec313, 07:19:52Z): it folds T-051 items
1-8 into the body (marks "(v3, T-051-n)"), my component v2 residuals N-01 (stale texts), N-02 (`evt_retired_hit` /
`evt_cycle_hit`, one toggle per threshold) and N-04 (B1 / BUG-06), the link-test-2 marks, and the DV Lead's knob-name
alignment. The adopted document embeds v2 plus 6.13. Re-adopt with v3 embedded, merge 6.13 into the body (its "binding
wording" clause then retires), and repeat the fidelity check with the method of Section 1 (hash the v3 file, diff the
embedded text with headings flattened; expect only the preamble and the appended subsections). I do not need to
re-review the v3 fold: the five checker rows it corrects come to me with their SV.

L-4 Section 4.2 knob names (see Section 4 above); align with the codegen names at re-adoption.

L-5 Header, citations and log references. The status field says the component sections' "v2 re-review is in progress"
(it is APPROVED, 06:59Z) and the 6.0 preamble cites dv/auto_dv/work/tb-infra/gen_critic_response_tb_arch_v1.md
(gitignored); cite the committed dv/auto_dv/evidence/gen_critic_response_tb_arch.md and, for the feature-list response,
dv/auto_dv/evidence/gen_critic_response_feature_list_v1.md (standing rule). Section 5 and 8.1 should cite the
intervention-log entries that now record the rulings (Q-014 owner-visible question, R-002 ruling); at adoption time
neither ruling was in the log, which the cross-model delta review rightly flagged.

L-7 Section 7 ("as they stand in the intervention log") lists Q-002 (revised) and Q-008..Q-013 but omits Q-001,
Q-003..Q-007 and F-001, all present in dv/auto_dv/docs/gen_intervention_log.md (lines 23-134, 323). Either list them
with their defaults or retitle the section as the TB-relevant subset. (Cross-model delta review medium: agree.)

L-8 8.2 says GEN_ICACHE_ECC_WINDOW is "1 from the corrupted-rdata cycle" while the 6.13 table and rtl-arch 2.4 put the
alert at 0 from that cycle and 1 from the lookup request; TB Infra's yaml (step 1a) and v3 carry "window 1 counted from
the lookup request". Align 8.2 to the 6.13 wording. (Cross-model delta review low: agree.)

L-6 (resolved at HEAD 7d91448) Section 5 promises the wrapper's objects "reported informationally (a third +tree in a
separate, non-gated report)". At review time the testlist carried only the two measured trees; Runtime's T-062 landing
(7d91448) added `info_trees` to the build schema (gen_flow_const.py BUILD_OPTIONAL_KEYS, gen_build.py info_trees(),
gen_flow_util refusing a tree that is both gated and informational, gen_cov_report.combine_rows for the gate row) and
gen_testlist.yaml now lists `info_trees: [u_dut]` for both builds. The document's mechanism statement is executable as
written.

## 8. Relation to the cross-model delta review (dv/auto_dv/reviews/2026-09-03-claude-plan-gen_tb_architecture.md, REQUEST-CHANGES)

| Cross-model finding | My position |
|---|---|
| High: the coverage-scope ruling is not executable as written (flow refuses two scopes until T-057) | Agree that it was not executable at adoption time; at HEAD 7d91448 the flow implements the list of gated trees with a combining rule and informational trees (L-6), so the mechanism the document describes now exists. I keep APPROVE: the ruling is what the document must record, and executability is the flow's deliverable, now landed. The document should cite 7d91448 or the API doc for the mechanism |
| Medium: neither ruling was in the intervention log | Agree; recorded since as Q-014 and R-002; the document must cite them (L-5) |
| Medium: identifier drift (+gen_chk_bus_rvalid_legal vs +gen_chk_sva_rvalid_legal; one vs per-threshold edge bits) | Agree; covered by L-3/L-4 (TB Infra's v3 and the step-1a yaml already use chk_sva_rvalid_legal and the two evt_*_hit bits); re-adoption with v3 embedded resolves it |
| Medium: Section 7 omits Q-001, Q-003..Q-007, F-001 | Agree; added as L-7 |
| Low: status and inputs stale at adoption | Agree (L-5) |
| Low: 8.2 vs 6.13 on GEN_ICACHE_ECC_WINDOW | Agree; added as L-8 |
| Low: `seed_used` exists only for riscv-dv programs | Agree, informational; the one-seed statement in 4.2 should say "seed (and seed_used for generated programs)" |
| Info: 8.3 item 4 knob count wording | Agree, informational |

Severity difference: the delta review blocks on the scope mechanism; I do not, for the reason above. Both lists go to the
DV Lead's v1a together, as the Orchestrator arranged.

## 9. Method and fence record

Fidelity was checked by reconstruction and hash, not by eye: the reviewed v2 text exists only in my saved review copy
because TB Infra's file has since moved to v3, and the reconstruction hashes to the recorded v2 sha256. The rulings were
traced to the intervention log entries and to the flow files that implement them. Port names were checked against the
module port lists. No LSF command; no fence event; no Ibex DV collateral read or recalled.
