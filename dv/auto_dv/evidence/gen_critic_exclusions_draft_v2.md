# Critic verdict: coverage exclusion draft v2 (T-040)

Artifacts under review (all under dv/auto_dv/work/rtl-arch/):
- gen_exclusions_draft.md (v2)                 sha256 efad14a74994698e
- gen_critic_response_exclusions_v1.md         sha256 c615b5c94a146d4e
- gen_unreachability_evidence.md               sha256 b51ae892ae1f1b16 (mtime 2026-09-03 06:38:05Z; a
  same-length edit landed after my first read at 27f0a4ce0a632cad; the sections cited below were
  re-read at the current hash)
- gen_cover_props_draft.sv                     sha256 bf9bad53bc34b9f3
Date: 2026-09-03 (UTC)
Role: Critic (the reviewer other than the author that DV_prompt.txt Section 4 requires for
control-logic exclusions)
Supersedes: dv/auto_dv/work/critic/gen_critic_exclusions_draft_v1.md (T-020 rulings R-1..R-5,
E-01..E-05, evidence classes EC-1..EC-6). Those definitions stay in force and are not repeated.

CRITIC VERDICT: APPROVE

Meaning of this approval: the v2 draft is ready to become the exclusion file at the first measured
regression, pending EC-3 and EC-5 evidence. It approves the draft as the basis for the file, the
per-arc unreachability arguments, and the object-list procedure. It does not approve the final
file: that gets its own verdict once the conditions in Section 5 are met. Every high and medium
finding of v1 is addressed (Section 1). The two medium items below (N-1, N-2) are conditions on
the final file and on a pending decision, not defects in the draft text.

## 1. Disposition of the v1 rulings

Each v1 ruling, where v2 answers it, and my check of the answer against the text and the RTL.

| v1 item | Required by v1 | Where v2 does it | Check |
|---|---|---|---|
| R-1 whole-instance exclusion of u_ibex_cheriot_ex | Rejected; object list only, live objects and live ports carved back | A.1 object-list procedure; LIVE objects :943-960, :970-973, :991-994, :219-233; live and constant port lists | Verified. The four live blocks are the ones I named in v1. The constant-port list now excludes csr_mshwm_new_o (live) and keeps csr_mshwm_set_o (constant through the two-CSR chain, cs_registers.sv:879-884 gates mshwm_en by the On comparison, :1301 folds it into mshwm_en_combi; proved as T022_CSR_MSHWM0). Accepted |
| R-2a enum default arms | Unreachable only with StateValid-style assertion (EC-3) and merge hygiene | C.2 six entries, each with the guarding assertion name and attempts/failures placeholders | Verified: six entries, names match the RTL assertions and the T022_*_NAMED proofs |
| R-2b fault-injection-only default arms | Same as R-2a, conditional on boundary-only stimulus | C.2 text plus evidence 4.2 caveat that proofs have no fault-injection semantics | Verified. The caveat is honest and does not weaken the ruling: legal stimulus cannot reach the spare encodings, and the assertion stays armed |
| R-2c urg -line nocasedef | Rejected | B.5 states the option is not used | Verified |
| R-3 class P granularity | Only the dead sub-expression, not the statement | Rows 12, 30, 32, 42-43 name the dead arm (BranchPredictor=0 kills ~instr_bp_taken_i at controller.sv:684; BranchTargetALU=1 kills the MULTI_CYCLE paths at id_stage.sv:925-926 and :936-942) | Verified against rtl/ibex_controller.sv:684 and rtl/ibex_id_stage.sv:925-926, :936-942 |
| R-3 class R | Out of the file until EC-4 passes; property specified | Rows 37-40 marked out; gen_cover_props_draft.sv carries T022_NEVER_zcmp_class_change verbatim plus seven per-state covers | Verified verbatim. Evidence 4.4/5.1 corrects the premise to instr_i[15:0] only (the icache back-fills [31:16]); the correction makes the property stronger, not weaker. Accepted |
| R-4 A.8 carve-back completeness | Ten named items | A.8 lists all ten | Verified |
| R-5 hygiene rules (5.1-5.5) | Legal-stimulus merge only; measured tests separate; -excl_strict; no test-equipment code in the tree | B.7 rules 1-7 | Verified; the flow already implements 5.5 (gen_regress.py header, unmeasured vdb tree) and -excl_strict on every --elfile |
| E-01 A.5 wording | Name the config that makes the branch dead | A.5 note | Verified |
| E-02 A.6 FSM entries | Unconditional on URG's FSM extraction | A.6 | Verified against the T-010 fact that URG extracts six machines |
| E-03 spare encodings | Count them per default arm | Rows carry the counts | Verified (md_state_q spare 3'b111 only; ls_fsm_cs spare 8 of 16, matching the T022_NEVER_* properties) |
| E-04 C.3 | Class table with evidence pointers | C.3 | Verified |
| E-05 A.5 last paragraph | Remove the "coverage credit" phrasing | Rewritten | Verified |

No disputes were raised in gen_critic_response_exclusions_v1.md. Nothing in v2 reopens a v1 ruling.

## 2. Evidence audit (artifact identity, not only content)

Method applied (lesson of LOG-005): every claimed run must map to a distinct retained artifact whose
path, mtime and in-log stamp are consistent with the claimed sequence. Local times below are -0400;
UTC = local + 4 h.

| Claim | Artifact | mtime | In-artifact stamp / content | Consistent |
|---|---|---|---|---|
| Whole-DUT k-induction PASS, depth 5, 17 assertion groups (evidence 1, 4.1, 4.2) | session scratchpad t022_core5/logfile.txt | 01:54:04 | "summary: successful proof by k-induction", "DONE (PASS, rc=0)", engine smtbmc yices, basecase and induction both pass | Yes. Job file t022_core5.sby: mode prove, depth 5, async2sync. Source t022_formal_core5.v mtime 01:53:54 precedes the log; it carries 18 T022_* labels (CORE_CHERI0 and CORE_CHERI0_B are one group) = 17 groups as claimed; model/design_smt2.smt2 has 46 assert terms as claimed |
| Non-vacuity: no implicit declarations in the formal copy (evidence 2.2) | t022_core5/model/design.log | 01:54 | 0 lines matching "implicitly declared" | Yes |
| Class R bounded runs: zcmp3 UNKNOWN, zcmp3c cover unreached at depth 12, deeper run terminated (evidence 4.4, 4.5) | t022_sby_zcmp3.out, t022_sby_zcmp3c.out, t022_sby_zcmp3p.out | 01:47:55, 01:49:29, 02:15:30 | "DONE (UNKNOWN, rc=4)"; "unreached cover statements ... DONE (FAIL, rc=2)" with depth 12 in t022_zcmp3c.sby; "Keyboard interrupt or external termination signal" | Yes |
| -cm_glitch 0 trial removes the 14 URG mismatch warnings and lowers the DUT numerators (evidence 4.3, LOG-007) | dv/auto_dv/work/runtime/results/rtl-arch-001/manifest.yaml; out root regress_req_rtl-arch-001/cov/merge.log and cov/report/hierarchy.txt; build/gen_smoke/compile_cmd.sh, compile.log | manifest finished 06:07:23Z; merge.log 02:07:23 | LSF jobs 10930598/10930599 PASS; merge.log has 0 UCAPI-CSM and 0 RCGLTCH lines; u_dut row LINE 1694/4351, COND 2547/9566, BRANCH 798/2418, TGL 1994/26958, FSM 6/86, ASSERT 143/178; compile_cmd.sh line 66 carries '-cm_glitch 0'; compile.log:908 VCM-OPTIGN (fsm not filtered) | Yes, matches the evidence and LOG-007 to the digit |
| Same-seed control reproduces the baseline (LOG-008/008a) | results/rtl-arch-002/manifest.yaml; regress_req_rtl-arch-002/cov_unmeasured/merge.log and report/hierarchy.txt | 06:17:18Z; 02:18:34 | jobs 10930768/10930769 PASS; 14 UCAPI-CSM, 1 RCGLTCH; u_dut row 2397/4351, 3579/9566, 992/2418, identical to regress_t010_smoke (merge.log 01:33:11) | Yes. The control ran in the unmeasured tree because gen_smoke is check-tier (LOG-008a); the numbers are informational, which is the right label |

Result: every machine claim in the evidence file maps to a distinct artifact with a consistent stamp.
No two claimed runs share content. The formal artifacts, however, live only in a session scratchpad
(evidence 7 and 8 say so plainly). That is finding N-1.

RTL spot checks of v2 citations, re-read this session: controller.sv:684 (pc_set_o ternary),
id_stage.sv:925-926 and :936-942 (BranchTargetALU arms), cs_registers.sv:879-884 (mshwm_en,
mshwmb_en, cdbg_ctrl_en gated by the On comparison) and :1301 (mshwm_en_combi). All as cited. The
A.1 live-object line ranges were verified in T-020 and are unchanged in the RTL.

## 3. Evidence-class status accepted for the final file

| EC | Status accepted today | What still has to happen |
|---|---|---|
| EC-1 (structural, including machine-checked k-induction per the Orchestrator's ruling) | DONE for classes T, P, D, subject to N-1 retention | Retain the artifacts (N-1) |
| EC-2 (-cm_seqnoconst / URG Unreachable) | PARTIAL, as the evidence states; URG marks only directly dependent objects | Nothing further; annotated entries stay necessary |
| EC-3 (runtime assertion attempts > 0, failures 0) | NOT YET | First measured regression's assertion report; fill the C.2 placeholders |
| EC-4 (bound DV cover property) | DRAFT, not run | TB Infra binds gen_cover_props_draft.sv; class R enters the file only after the property passes on a full measured regression with all seven per-state covers hit |
| EC-5 (-excl_strict clean load) | NOT YET | First measured regression with the generated .el |
| EC-6 (cone of influence) | Not applicable (no data-path toggle exclusion proposed) | Only if such an entry appears |

## 4. Findings

N-1 (medium, retention). The formal evidence that carries EC-1 for 39 of the 43 arcs and all six
default arms exists only in a volatile session scratchpad (evidence 2.1, 7, 8: "scratch artefacts
remain in the session scratchpad (not committed)"). Under the audit rule, prose that cites a run is
not evidence once the run's artifact is gone. Required change: before the final file cites any
T022_* proof, copy into dv/auto_dv/work/rtl-arch/t022/ (working area; the Orchestrator decides
whether a subset moves to dv/auto_dv/evidence/): t022_core5.sby, t022_core5/logfile.txt,
t022_zcmp3.sby, t022_sby_zcmp3.out, t022_zcmp3c.sby, t022_sby_zcmp3c.out, gen_t022_top.sv, the
grep output showing 0 implicit declarations in t022_core5/model/design.log, and a diff or extract
of the inserted T022_* assertions (not the 630 KB flattened source). Quote the summary lines with
their SBY stamps in evidence 4.1 and 8. Until then the k-induction claims are verified by me at the
paths and stamps in Section 2 and count as EC-1, but that verification does not outlive the
scratchpad.

N-2 (medium, pending decision, not a defect). Adopting `-cm_glitch 0` for measured builds is a
coverage-measurement policy change: on the smoke it removes about one third of the line, condition
and branch numerators (glitch-only hits) with identical denominators. My ruling as reviewer of the
exclusions: acceptable in principle and recommended, because a hit that exists only in a zero-time
glitch is not exercised logic (DV_prompt.txt Section 10), and because seven of the Condition
entries in Part C are otherwise reported covered by glitches and would be rejected by -excl_strict.
Conditions: the DV Lead's decision (LOG-007) is recorded before the first measured regression; the
flag appears in every report's build-configuration statement; the seven glitch-covered tie
Conditions enter the file only if the flag is adopted, else they are dropped. The trial applied the
flag at compile time and the effect on line/condition/branch is verified above; the draft makes no
claim about toggle, which is right.

N-3 (low). Rows 30, 32, 42-43 have no netlist witness (evidence 4.2 says so). Accepted: the dead
term is an elaboration constant of the opentitan parameters, the URG Unreachable status is the
expected EC-2 witness, and if URG does not mark them the entries must be explicit and carry the
parameter argument in the A.0 annotation shape. No change to the draft.

N-4 (low, policy for TB Infra). The T022_ASSERT macro in gen_cover_props_draft.sv reports through
$error, which the flow's fail patterns collect. Ruling: keep a collected failure for every
T022_NEVER_* violation in measured regressions. TB Infra may route it through the TB's own failure
API but must not downgrade it to a warning: a reachable "unreachable" arc withdraws an exclusion
and must fail the run that found it. The hierarchical enum-label references the header lists as a
compile hazard are TB Infra's to resolve in the bind; if the labels do not resolve, mirror the
encodings in a local parameter with a comment naming the enum.

N-5 (low). Evidence 5.1 (the decoder's instruction bus is 32 bits wide and the icache back-fills
[31:16], so the class-R premise is instr_i[15:0] only) is a correct RTL reading and is already
folded into the property. Evidence 5.2 (the icache has no defence against unsolicited rvalid)
restates a feature-list fact and my T-011 ruling A-14 for TB Infra's memory model; no exclusion
consequence.

N-6 (info). The cover_props draft's non-vacuity covers (fetch-error diagnostics, BUG-07 witness)
are welcome and satisfy the anti-vacuity duty for EC-4 in advance: an EC-4 pass with those covers
unhit is not a pass.

N-7 (info). Evidence 1a records that URG's own Unreachable marking covers only 5 line rows, 54
condition vectors and 22 toggle rows of ibex_cheriot_ex. That is why the object list (A.1) stays
the mechanism; the draft says so. Consistent.

## 5. Conditions the final exclusion file must meet for its own APPROVE

F-1  Generated at the first measured regression with legal stimulus only, measured tests only
     (B.7), and loaded with -excl_strict without a rejected entry (EC-5).
F-2  N-1 retention done; each T022_* citation in an annotation resolves to a retained artifact.
F-3  EC-3 placeholders in C.2 filled from that regression's assertion report (attempts > 0,
     failures 0 for each named guarding assertion).
F-4  LOG-007 decision recorded; the seven glitch-covered tie Conditions present only under
     -cm_glitch 0.
F-5  Class R rows 37-40 absent unless EC-4 has passed on a full measured regression with the seven
     per-state covers hit.
F-6  Every entry carries the A.0 annotation (class, RTL location, config parameter or tie chain,
     evidence class and pointer); the object list of A.1 is reproduced, not summarised.
F-7  The file contains no entry outside the 43 rows, the six C.2 default arms and the A.1 object
     list without a new reviewer ruling.

## 6. Fence and method record

No fenced content was read for this review. Inputs: the four artifacts above, rtl/ibex_controller.sv,
rtl/ibex_id_stage.sv, rtl/ibex_cs_registers.sv, rtl/ibex_compressed_decoder.sv, the Runtime
Manager's request manifests and the out-tree reports named in Section 2, the intervention log
entries LOG-007/008/008a, and the formal job artifacts in the session scratchpad (team-generated,
not Ibex DV collateral). No LSF command was issued by me.

## Addendum (2026-09-03 07:37Z): N-1 retention audited

rtl-arch placed the formal retention subset at dv/auto_dv/evidence/gen_t022_formal/ (README
gen_t022_formal_README.md). Audit under the artifact rule: runs/t022_core5/logfile.txt is the original whole-core proof
(SBY stamp 1:54:04 local, "successful proof by k-induction", "DONE (PASS, rc=0)"); logs/t022_core5_rerun.out is a
regeneration from this clone (SBY stamp 3:32:49 local, file mtime 03:33:06, DONE PASS); jobs/ holds the 16 .sby files;
sources/t022_assertions_extract.txt resolves 27 distinct T022_* names (the 18 of the core5 job among them);
runs/<job>/ carry status, implicit_declarations.txt (0 for core5) and smt2_assert_count.txt; gen_t022_regen.sh gives the
recipe. This satisfies N-1 and condition F-2 in substance. At audit time the directory was untracked (git status "??"):
F-2 is met when it is committed. This verdict and its v1 are copied to dv/auto_dv/evidence/ as the cited rulings
(R-1..R-5, E-01..E-05, F-1..F-7), per the standing rule.
