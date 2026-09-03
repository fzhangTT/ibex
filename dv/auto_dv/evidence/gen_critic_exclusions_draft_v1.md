# Critic rulings v1: coverage-exclusion draft (T-020)

- Artifact under review: dv/auto_dv/work/rtl-arch/gen_exclusions_draft.md (sha256 first 16:
  df2f9b65594330dc; 310 lines; Parts A-D)
- Companion inputs: dv/auto_dv/work/rtl-arch/gen_cheriot_carveout.md (sha256 first 16:
  bc7b02f87735f81b; buckets A-F, gating chain G1-G8), dv/auto_dv/work/rtl-arch/gen_hierarchy_map.md
  Part C section 1 (transition audit, 43 U-arcs), dv/auto_dv/work/critic/gen_critic_feature_list_v1.md
  findings C-16..C-18 (F-CHERI-001 table)
- Standard applied: DV_prompt.txt Section 4 (every exclusion carries a written justification in
  the exclusion-file annotation; data-path toggle exclusions normally acceptable; a data bit that
  feeds control is control, decided by cone-of-influence; control-logic exclusions require an
  unreachability argument and reviewer approval; disputed exclusions stay unapplied and go to the
  owner), Section 6 (every DUT input driven at the boundary; no forces), Section 10 (honesty);
  dv_principles.md Section 4 (prune genuinely unhittable bins; no duplicate coverage) and
  Section 6 (evidence over prose)
- Date (UTC): 2026-09-03 05:37
- Reviewer role: critic (Claude Fable 5.1). Every RTL line cited below was read by the Critic;
  urg option names in Part B were checked against `urg -help` of VCS X-2025.06-SP2 on this host.
- Build configuration: opentitan; DUT = gen_dut_top (ibex_core + ibex_register_file_ff),
  cheriot_enable_i tied IbexMuBiOff. No fence event (rtl/, vendor/lowrisc_ip/ip, doc/, docs/dv,
  dv/auto_dv/work only; no network, no git).

CRITIC VERDICT: REQUEST-CHANGES

Scope of this verdict. These are rulings on the draft as the basis for the final exclusion
file. No exclusion is approved for application by this document: DV_prompt Section 4 approval
attaches to the final, machine-generated exclusion file (gen_ prefix, under dv/auto_dv/) once
T-022 (gen_unreachability_evidence.md) supplies the evidence classes named below, and before it
is first used on a measured regression (draft Part B.6 step 5). Severity counts for the changes
required in the draft: high 1 (R-1), medium 4 (R-2 nocasedef, R-3 class P granularity, R-4 A.8
gaps, R-5 strict-load and merge hygiene), low 3, info 2.

## Evidence classes (used by every ruling; T-022 reports against these names)

- EC-1 Static structural evidence: the RTL declaration or generate/parameter condition that
  makes the object unreachable, cited file:line, plus the parameter value with its source
  (ibex_configs.yaml, gen_param_resolution.md) or the gating chain item (carve-out section 0,
  G1-G8) for tie-derived constants.
- EC-2 Tool constant analysis: the VCS constant-analysis record for the object or its guarding
  term (`-cm_seqnoconst` build; `-diag noconst` constfile.txt entry naming the net, its constant
  value and definition site; URG object status "Unreachable" with `-show constvalues`). If the
  wrapper tie does not propagate into ibex_core, the `-cm_constfile` line that declares it and
  the re-run showing propagation.
- EC-3 Runtime assertion evidence: the RTL assertion that guards the object is compiled
  (INC_ASSERT defined; vendor/lowrisc_ip/ip/prim/rtl/prim_assert.sv:104-111 defines it for
  every non-Verilator, non-SYNTHESIS build; confirm in the compile log) and shows a nonzero
  attempt count and zero failures in the merged assertion coverage of EVERY measured regression.
- EC-4 DV cover-property evidence: a DV-authored SVA bound into the DUT from dv/auto_dv (never
  an RTL edit) that passes as an assertion over the full regression AND whose precondition cover
  fires a nonzero number of times for every state or condition it qualifies.
- EC-5 Strict-load evidence: `urg -elfile <file> -excl_strict` loads the final file against the
  merged measured vdb with no rejected entry (an object that any test covered cannot be
  excluded). The merged vdb contains only legal-stimulus tests (see R-5).
- EC-6 Cone-of-influence evidence (DV_prompt Section 4): for any toggle exclusion of a data
  net, a siliconpilot cone_of_influence run with the opentitan parameters and defines applied
  (resolve_sources/rtl_analyze with the config context), showing no fan-out into control; for
  tie-derived constants the run is desirable but the tie plus EC-1/EC-2 is accepted as primary
  (the draft's two default-parameter runs are correctly discounted as not-this-build).

---------------------------------------------------------------------------------------------------
## R-1 (item 1, high) Carve-out expression for u_ibex_cheriot_ex: whole-instance exclusion REJECTED; object-list exclusion inside the instance REQUIRED

Ruling: the instance gen_tb_top.u_dut.u_ibex_core.g_cheriot_ex.u_ibex_cheriot_ex may not be
excluded as a scope for line, condition, branch or FSM coverage. The exclusion is expressed as
per-object entries (Block / Branch / Condition / Toggle) generated from `urg -dump
full_exclusions` for that instance, from which the live objects below are removed. The result
is the same "everything but the pass-through" the draft intends, but every excluded object is
named and annotated, and the live objects stay in the numbers.

Evidence for the ruling:
- Live RV32I logic inside the instance, verified: rtl/ibex_cheriot_ex.sv:943 (`lsu_req_o =
  instr_is_cheriot_i ? cheriot_lsu_req : rv32_lsu_req_i`), :945-948 (cpu_lsu_cheriot_err /
  addr / we / wdata muxes), :951-954 (lsu_cheriot_err_o, lsu_we_o, lsu_addr_o, lsu_wdata_o),
  :958 (lsu_type_o), :960 (lsu_sign_ext_o), :970-971 (rv32_addr_incr_req_o), :973
  (rv32_addr_last_o), :991-994 (csr_mshwm_set_o terms and csr_mshwm_new_o, which toggle with
  lsu_addr_o), :219-233 (fwd_data_merger nets, carve-out A1). Their RV32I arms execute on every
  load/store. Excluding them by scope hides reachable, covered objects, which is outside what
  DV_prompt Section 4 allows (an exclusion needs an unreachability argument; "covered elsewhere
  too" is not one), and the draft's own recommended `-excl_strict` would reject such a file the
  moment a load/store test is merged.
- Carve-out A.4 recommendation (2) is "exclude, then re-include the live nets by name"; URG has
  no scope-minus-objects primitive, so the only faithful encoding is the object list.

Required content of the final file for this instance:
1. Block/Branch/Condition entries for every object in the instance that carve-out A1 and
   bucket C classify UNREACH or CONST, each under one ANNOTATION_BEGIN/END carrying the
   carve-out justification text and the bucket item id.
2. Branch entries only for the CHERIoT arms of the live ternaries at :943-960 (the
   `instr_is_cheriot_i ? ... :` true-arms) and the `: 1'b0` arm at :970-971; Condition entries
   for the vectors where `instr_is_cheriot_i` or `(cheriot_enable_i != IbexMuBiOn)` takes its
   impossible value. The lines themselves and the RV32I arms stay in coverage.
3. Toggle entries (`-cm_tgl portsonly`: ports only) for every constant port. The live port list
   the draft gives is incomplete; the following ports also toggle in RV32I mode and stay in
   coverage: addr_incr_req_i, addr_last_i (:80-81), csr_rdata_i, csr_mstatus_mie_i (:93, :95),
   csr_mshwm_new_o (:994, toggles with the address; dead but not excludable under EC-5).
   Constant ports that ARE excluded include fwd_wcap_i, rf_rcap_a_i/b_i, pcc_cap_i/o,
   csr_mshwm_i/mshwmb_i, csr_mshwm_set_o (G3: constant 0), csr_rcap_i, csr_wcap_o, lsu_wcap_o
   (constant NULL_CAP, :959), lsu_is_cap_o, lsu_lc_clrperm_o, lsu_cheriot_err_o, and every
   cheriot_* port (carve-out bucket D).
4. Evidence: EC-1 (carve-out A1 + G3), EC-2 for the guarding terms (instr_is_cheriot_i,
   cheriot_exec_id_i constant 0), EC-3 (isolation assertions rtl/ibex_id_stage.sv:1297-1300 and
   rtl/ibex_load_store_unit.sv:833-834 passing), EC-5.

The same object-list rule applies to every shared module: no `MODULE:` or `INSTANCE:` scope-wide
entry anywhere in the file (the draft's A.3 already follows this; the DV Lead's F-CHERI-001
table rows in gen_critic_feature_list_v1.md C-16 do not and must be brought in line with the
draft, not the other way round).

---------------------------------------------------------------------------------------------------
## R-2 (item 2) Enum default arms and fault-injection-only arms

Ruling 2a (acceptable-in-principle, EC-1 only): a case default arm on an enum state variable
whose declared width has NO spare encoding is unreachable by construction; no fault model short
of X-propagation can select it. Verified instances: id_fsm_e (`typedef enum logic {FIRST_CYCLE,
MULTI_CYCLE}`, rtl/ibex_id_stage.sv:861; default :968-970), mult_fsm_e (`enum logic {MULL,
MULH}`, rtl/ibex_multdiv_fast.sv:142-144; default :238-240), inval_state_e (`enum logic [1:0]`,
4 values, rtl/ibex_icache.sv:193-198; `default: ;` :1268). Annotation: "no spare encoding:
<width>-bit enum, <n> named values". Entry kind: Branch (the default arm) and, where the arm has
statements, Block. No assertion evidence required.

Ruling 2b (acceptable-in-principle with EC-1 + EC-3 + EC-5): a default arm on an enum state
variable WITH spare encodings is reachable only if the state register holds a non-enum value,
which requires a fault. Verified instances: ctrl_fsm_e (`enum logic [3:0]`, 10 values, 6 spare,
rtl/ibex_pkg.sv:291-302; default rtl/ibex_controller.sv:990-993; guard `ASSERT(IbexCtrlStateValid)`
:1104-1106), ls_fsm_e (`enum logic [3:0]`, 8 values, 8 spare, rtl/ibex_pkg.sv:816-820; default
rtl/ibex_load_store_unit.sv:605-607; guard IbexLsuStateValid :821-824), md_fsm_e (`enum logic
[2:0]`, 7 values, 1 spare, rtl/ibex_multdiv_fast.sv:90-92; default :522-524; guard
IbexMultDivStateValid :532-533). For this project such an arm COUNTS AS UNREACHABLE for the
coverage gate, because: (i) DV_prompt Section 6 drives every DUT input at the boundary and
allows no force on DUT state, so no legal stimulus can load a non-enum encoding; (ii) the RTL
documents no FSM-hardening countermeasure for ibex_core (doc/03_reference/security.rst lists
Hardened PC, shadow CSRs, lockstep, ECC, dummy instructions, bus integrity; the default arms are
defensive coding with no alert or other boundary observable), so there is no DUT feature to
verify through them; (iii) the state-validity assertion, compiled and passing in every measured
run (EC-3), is the positive proof that the register never left the legal set during the runs
whose coverage is claimed. Annotation: "unreachable without fault injection into <state
register>; <n> spare encodings; guarded by <assertion name> (attempts N, failures 0 in
<regression id>)".

Ruling 2c (rejected): `urg -line nocasedef` as the mechanism for class D. The option exists
(verified in `urg -help`: "Exclude case default lines in line coverage") but it is global: it
would also remove REACHABLE default arms that are real DUT behaviour, for example the decoder's
illegal-instruction defaults (rtl/ibex_decoder.sv:877-878, :892-893 and every `default:
illegal_insn = 1'b1`), the CSR read-mux `default: illegal_csr = 1'b1`, and the Zcmp
`default: illegal_instr_o = 1'b1` (rtl/ibex_compressed_decoder.sv:832 area). Use explicit
Branch/Block entries per arm (six arms in class D).

Ruling 2d (applies to all of R-2): fault-injection runs made for trust-triad rule 2 (mutation
evidence) and any directed test that forces DUT state are never merged into a measured
regression vdb. If they were, the default arms would show as covered by illegal stimulus and
EC-5 would reject the entries. The Runtime Manager's merge script must select coverage inputs
by testlist tier, and the exclusion annotation must name the merge rule.

---------------------------------------------------------------------------------------------------
## R-3 (item 3) Part C classes

### Class T, 28 arcs (CHERIoT tie): acceptable-in-principle
Evidence: EC-1 (gating chain G1-G8 item per object, as the draft's annotation template already
requires), EC-2 (constant analysis marks the guarding term or the object Unreachable; if the
wrapper tie does not propagate, `-cm_constfile` with `<path>.cheriot_enable_i 4'b1010` and the
re-run), EC-3 (isolation assertions rtl/ibex_id_stage.sv:1297-1300, rtl/ibex_load_store_unit.sv:
833-834, rtl/ibex_cs_registers.sv:1996-1997 and the controller one-hot assertion :377-383
compiled and passing), EC-5. Granularity: per arm/term exactly as A.3/A.4 list them; the
reachable halves (illegal-instruction arms :877-878/:892-893, RV32I arms of every ternary, the
0xBC1/2/4 illegal-CSR arms) stay. Verified against the RTL for #2-#10 and #14-#28: the cited
arms are all under `(cheriot_enable_i == IbexMuBiOn)` or a G1-G8 constant. Note for #41
(rtl/ibex_wb_stage.sv:115-116, :190-196): these are condition sub-terms of live statements,
Condition entries only, never Block.

### Class P, 5 arcs (build-parameter constants): acceptable-in-principle; granularity change required (medium)
Evidence: EC-1 (parameter value: BranchPredictor=0, BranchTargetALU=1, RV32B=RV32BOTEarlGrey
from ibex_configs.yaml and gen_param_resolution.md, plus the time-0 config banner of the run),
EC-2 (procedural `if (<param>)` and `<param> ? :` are elaboration constants; URG should report
them Unreachable; otherwise explicit Branch entries), EC-5. Verified: rtl/ibex_controller.sv:684
(`BranchPredictor ? ~instr_bp_taken_i : 1'b1`) and :690-696 (`if (BranchPredictor)`);
rtl/ibex_id_stage.sv:925-926 (`!BranchTargetALU && branch_decision_i` sub-term) and :936-942
(`BranchTargetALU ? FIRST_CYCLE : MULTI_CYCLE`); rtl/ibex_decoder.sv:1342-1344 and :1348-1350
(`if (RV32B == RV32BFull)`). Granularity: for #42-#43 the case items `{7'b010_0100, 3'b110}`
(:1341) and `{7'b000_0100, 3'b110}` (:1347) ARE reached by the (illegal) bcompress/bdecompress
encodings; only the inner `if` bodies are unreachable. Exclude the inner blocks, not the case
items. For #12 also the else-path of `pc_set_o = BranchPredictor ? ...` is the live one; Branch
entry for the true-arm only.

### Class D, 6 arcs (enum default arms): acceptable-in-principle per R-2 (2a for U-I3, U-M1, U-V1; 2b for U-C1, U-L10, U-D1); `-line nocasedef` rejected (R-2c)

### Class R, 4 arcs (Zcmp mismatched-state defaults, rtl/ibex_compressed_decoder.sv:682, :773, :804, :832): needs-evidence; keep out of the file until EC-4 passes (agree with the draft)
Why reasoning alone is insufficient: cm_state_e is a 3-bit enum with 8 named values and no
spare encoding, but these defaults are NOT spare-encoding arms: they are the arms taken when a
NAMED state (say CmPopLoadReg) is paired with a different instruction class on instr_i. Their
unreachability rests on instr_i being frozen while cm_state_q != CmIdle, which depends on
rtl/ibex_if_stage.sv:808-809 (fetch_ready low during EXPANDED/COMMIT), on the icache holding
rdata_o while ready_i is low (doc/03_reference/icache.rst:246, with the explicit exception
"after an error is passed to the core there is no constraint on rdata_o"), and on
flush_expanded_i (rtl/ibex_compressed_decoder.sv:889) covering every redirect. The error
exception is closed by valid_i = fetch_valid & ~fetch_err and the RTL assertion
IbexPushPopFSMStable (`!valid_i |-> cm_state_d == cm_state_q`, :937), so the property to prove
is the valid case. Required EC-4 property (bound from dv/auto_dv): for every cycle in which
cm_state_q != CmIdle and valid_i and !flush_expanded_i, the class fields {instr_i[15:13],
instr_i[12:8], instr_i[6:5], instr_i[1:0]} equal their values in the previous cycle; plus a
cover that the antecedent fires for each of the seven non-idle states; plus EC-3 for
IbexPushPopFSMStable; plus the Phase-1 URG report showing the four arms uncovered. If the
property fails on any seed, the arcs are reachable and become test targets, as the draft says.

---------------------------------------------------------------------------------------------------
## R-4 (item 4, medium) Completeness of the A.8 carve-back list against C-16/C-17/C-18 and bucket F

A.8 names: rf_shared x16-x31 storage and enables; PMP gate RV32I arms; gen_memcap_rd RV32I arm;
*_combi CSR write muxes; branch_target_ex; instr_is_rv32lsu_id; csr_mshwm_new; the gen_scr
toggling nets; OPCODE_CHERI/AUICGP items and illegal arms; the 0xBC1/2/4 illegal-CSR arms. The
draft's A.3/A.4 entries are consistent with these (none of the C-16 live objects is excluded by
A.3; the C-16 defect is in the DV Lead's table, not here). A.8 is nevertheless incomplete as the
"deliberately not excluded" record the final file's reviewer needs. Add, by name:
1. rtl/ibex_controller.sv:827-831 (FLUSH exception entry: pc_set_o, PC_EXC, exc_pc_mux_o for
   every trap) and :833-840 (csr_save_id_o / csr_save_wb_o); only the `(On) & cheriot_wb_err_q`
   sub-terms are Condition-excluded (A.4).
2. rtl/ibex_controller.sv:866-868 RV32I arm (mtval = instruction bits), :909-914 (store access
   fault arm), :923-926 (load access fault arm) (bucket F9).
3. rtl/ibex_controller.sv:255 `illegal_insn_d` (live; the bucket-C items in :234-259 are only
   :234, :236-240, :256-257, :259).
4. rtl/ibex_id_stage.sv:1033-1036 instr_kill (bucket F11) and the live lines :1012, :1093-1096
   whose CHERIoT OR-terms are Condition-only exclusions.
5. rtl/ibex_core.sv:1350-1351 alert_major_internal_o: live terms rf_ecc_err_comb |
   pc_mismatch_alert | csr_shadow_err; only the two constant OR-terms are Condition-excluded.
6. rtl/ibex_load_store_unit.sv:650-653 (ls_fsm_cs, handle_misaligned_q, pmp_err_q, lsu_err_q
   flops) and :664-667 (resp_is_cap_q update executes on every lsu_go; line live, value constant).
7. rtl/ibex_core.sv:1851-1853 rvfi_id_done (bucket F10; RVFI-only; live and a bug candidate).
8. Bucket F13 register-file nets by name: rf_shared[*], wshared_data, we_shared_r0,
   rf_shared_r0_q, rcap_r0 (F2), we_data_r0, rf_data_r0_q; bucket F5 pass-through arms of
   gen_16_regs (rtl/ibex_decoder.sv:211-217) and the CAUICGP raddr_a mux RV32 arm (:202).
9. Bucket F15 assertions kept enabled: rtl/ibex_controller.sv:377-383 one-hot, the three
   ASSERT_IF groups (A.7 already keeps them; A.8 should list them as the proof objects EC-3 uses).
10. The live ports of u_ibex_cheriot_ex per R-1 item 3.
Also state in A.8 that gen_exclusions (the final file) is the authoritative list and that the
DV Lead's F-CHERI-001 table mirrors it row for row (gen_critic_feature_list_v1.md C-16, C-19).

---------------------------------------------------------------------------------------------------
## R-5 (mechanism, Part B) Verified points and required flow rules (medium)

Verified against `urg -help` (X-2025.06-SP2): -elfile, -elfilelist, -excl_bypass_checks,
-excl_strict ("Do not allow covered objects to be excluded"), -excl_embed, -excl_append_annotation,
-excl_propagation, -dump full_exclusions [line|fsm|cond|tgl|branch|group|assert], -line nocasedef,
-show constvalues all exist as the draft describes. Rules for the final flow:
1. `-excl_strict` is mandatory on every measured merge (EC-5). A rejected entry is a finding,
   never a reason to drop the flag.
2. `-excl_propagation` is not used: the file contains partial-arm entries whose lines are live;
   propagating line exclusions into cond/branch would over-exclude.
3. The auto-"Unreachable" set from constant analysis is an exclusion in the DV_prompt sense
   (draft B.3 says so, agreed): dump it with `-dump full_exclusions` and the annotation dump,
   review it against carve-out buckets C/D, and commit it beside the hand-annotated file so the
   closure report can state both counts (Excluded, Unreachable) from dashboard.txt.
4. RVFI entries apply only under +define+RVFI (tb-infra plans it); the file must carry the
   define dependence in the annotation.
5. Instance paths: fix once T-005 lands (draft Part D item 1); the file must not be generated
   before gen_dut_top's instance names are final.
6. Merge hygiene per R-2d: only legal-stimulus tiers enter a measured vdb.

---------------------------------------------------------------------------------------------------
## Other findings

- E-01 (low) A.5 lists csr_pcc_perm_sr_i as "constant 1" for toggle exclusion; correct per G6.
  Add the same note for rtl/ibex_core.sv rf_rcap_a/b (constant NULL_CAP, G8) which are internal
  nets, not ports, and therefore not toggle objects under portsonly: no entry needed, say so.
- E-02 (low) A.6 FSM entries are conditional on VCS extracting the ibex_pkg enums; if URG reports
  the FSM metric, the whole cap_rx_fsm_q FSM minus CRX_IDLE and the three CTX states plus their
  seven transitions are class T with EC-1/EC-2 evidence (frozen FSM: lsu_go_goodcap set only in
  the gated IDLE arm, rtl/ibex_load_store_unit.sv:449-459). Acceptable-in-principle.
- E-03 (low) Part C row #1 says "4-bit enum with 10 named values" for ctrl_fsm_e and row #23
  "4-bit enum, 8 named values" for ls_fsm_e: both verified (rtl/ibex_pkg.sv:291-302, :816-820).
  Row #33 md_fsm_e "3-bit, 7 values, one spare" verified (rtl/ibex_multdiv_fast.sv:90-92). Add
  the spare-encoding count to every class-D annotation (R-2b requires it).
- E-04 (info) The draft's honesty on the cone_of_influence runs (default parameters, wrong
  generate branch, procedural tracing gap) is the right way to record a tool result that does
  not apply; keep the paragraph, and for T-022 re-run with the opentitan context if the tool
  accepts defines/pvalues, otherwise record "not applicable" and rely on EC-1/EC-2.
- E-05 (info) Data-path toggle exclusions: none proposed yet; when URG holes appear, each needs
  EC-6 with the cone result quoted in the annotation (DV_prompt Section 4). A data bit with any
  control fan-out (sign, zero-detect, special value) is refused as a toggle exclusion.

---------------------------------------------------------------------------------------------------
## What T-022 (gen_unreachability_evidence.md) must show, per class

| Class | Count | Ruling | Evidence required before the entries enter the final file |
|---|---|---|---|
| T CHERIoT tie | 28 arcs (+ all A.3-A.7 objects) | acceptable-in-principle | EC-1 per object (G1-G8 item), EC-2 (constant-analysis record for the tie and guarding terms, or -cm_constfile + re-run), EC-3 (four isolation/one-hot assertion groups: attempts > 0, failures 0), EC-5 |
| u_ibex_cheriot_ex | 1 instance | object-list only (R-1) | dumped full_exclusions for the instance minus the live-object list in R-1; EC-2 for instr_is_cheriot_i / cheriot_exec_id_i; EC-5 |
| P build parameter | 5 arcs | acceptable-in-principle, inner-block granularity | EC-1 (parameter value + banner), EC-2 (Unreachable status) or explicit Branch/Block entries, EC-5 |
| D default arm, no spare encoding | 3 (U-I3, U-M1, U-V1) | acceptable-in-principle | EC-1 (enum declaration cite), EC-5 |
| D default arm, spare encodings | 3 (U-C1, U-L10, U-D1) | acceptable-in-principle (fault-injection-only counts as unreachable here) | EC-1 (enum cite + spare count), EC-3 (Ibex*StateValid attempts > 0, failures 0 in every measured regression), EC-5, merge-hygiene statement (R-2d) |
| R Zcmp defaults | 4 | needs-evidence; not in the file yet | EC-4 (bound stability property + per-state covers passing on the full regression), EC-3 (IbexPushPopFSMStable), Phase-1 URG showing the arms uncovered |
| Data-path toggles | 0 so far | per hole | EC-6 cone-of-influence with config context, quoted in the annotation |

Summary of changes required in the draft before the final file is generated: replace the A.1
whole-instance recommendation with the object-list procedure and the corrected live-port list
(R-1); drop `-line nocasedef` in favour of six explicit entries with enum/spare-count/assertion
annotations (R-2); narrow the class-P bcompress/bdecompress entries to the inner blocks (R-3);
complete A.8 with the ten items in R-4; add the flow rules of R-5 (strict load, no propagation,
committed auto-unreachable dump, RVFI dependence, merge hygiene). Class R stays out until EC-4
passes. REQUEST-CHANGES on the draft; the final file is approved only against T-022 evidence.
