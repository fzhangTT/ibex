# gen_exclusions.el -- the coverage exclusion file (draft form, ahead of the first measured regression)

Owner: rtl-arch (T-069, 2026-09-03). Build configuration: opentitan; DUT gen_dut_top with the gated
coverage trees u_dut.u_ibex_core and u_dut.u_register_file (Q-014 / R-001). Source of every entry:
dv/auto_dv/work/rtl-arch/gen_exclusions_draft.md v2 (Parts A, C, C.2), approved conditionally by the
Critic in dv/auto_dv/work/critic/gen_critic_exclusions_draft_v2.md; evidence classes EC-1..EC-6 and
the machine proofs in dv/auto_dv/work/rtl-arch/gen_unreachability_evidence.md with the retained
formal subset dv/auto_dv/evidence/gen_t022_formal/. The DV Lead's feature-list table F-CHERI-001
mirrors THIS file row for row (gen_exclusions_draft.md A.8 authority statement); never the reverse.

## 1. How the file is made (reproducible)

`gen_excl_select.py` turns the draft into URG entries: it parses a `urg -dump full_exclusions`
MODULE dump (`fullexclude_module.<metric>`), selects objects by the RTL line ranges, vector rules,
port lists, FSM states and assertion names that the draft names, copies each entry verbatim (id,
checksum, signature) so `-excl_strict` can verify it, and wraps every group in an ANNOTATION carrying
the A.0 justification (class, RTL location, tie chain or parameter, evidence class and pointer).
Scopes are `MODULE:` (every DUT module has exactly one instance, so MODULE and INSTANCE are the same
set and the file does not depend on the TB top name); the module and metric CHECKSUM lines are the
dump's own.

```
python3 dv/auto_dv/excl/gen_excl_select.py \
  --dump <outdir>/cov*/full_exclusions \
  --out dv/auto_dv/excl/gen_exclusions.el --report dv/auto_dv/excl/gen_exclusions_select_report.md \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass2.log \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass3.log \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass4.log
```

`--attempts` feeds back URG's attempts.log of a strict load: an object URG reports as covered is
refuted, dropped from the file and listed in the selection report ("Dropped ... refuted"). A refuted
object stays in coverage; it is a finding about the draft, never a reason to relax the load.

Reference dump used today: the round-0 re-baseline (dv/auto_dv/evidence/gen_round_0_rebaseline/,
out-tree regress_round_0_rebaseline/cov_unmeasured/full_exclusions, gen_smoke NOP program, -cm_glitch 0
build). The dump is a property of the BUILD (object ids, checksums, signatures), so the same file
loads against any vdb of the same RTL and build flags; the first measured regression re-runs the
generator against its own dump (F-1) and the ids are expected to be identical.

## 2. Content (what is in, what is out)

| Draft part | Entries | Form |
|---|---|---|
| A.1 u_ibex_cheriot_ex object list | 103 Blocks, 112 Branch vectors, 343 Condition vectors, 144 Toggle ports/fields of MODULE ibex_cheriot_ex | every object NOT on the live list (RV32I LSU mux arms :943-960, :970-973, :991-994, fwd merger :200-233, live ports); statement headers, reset arms and always_comb defaults are executed with cheriot off and stay in coverage; the covered ones found by the strict load were dropped (section 4) |
| A.3 Block / Branch entries in the shared modules | 124 Blocks, 4 Branch vectors | CHERIoT arm bodies (decoder, compressed decoder, controller, LSU, cs_registers, id_stage, core RVFI arm, wb_stage / register-file ternary arms); assign-ternaries that VCS folded have no object (section 5) |
| A.4 Condition vectors | 443 vectors in 20 modules | every vector in which a constant-tie operand (cheriot_enable_i == On, instr_is_cheriot*, cheriot_*, lsu_is_cap, resp_is_cap_q, wb_is_cheriot_q, ...) takes its impossible value; the classifier is in the script (const_value); the fetch_enable_i and mcounteren_writable_i comparisons are NOT constants in the real TB and are never selected |
| A.5 Toggle | 463 port / struct-field entries | the constant CHERIoT-only ports of every module (-cm_tgl portsonly); struct-typed cap ports appear as their fields |
| A.6 FSM | ls_fsm_cs: 3 states + 7 transitions; cap_rx_fsm_q: 2 states + 5 transitions | explicit entries (constant analysis does not cover FSM) |
| A.7 Assert | 3 (g_cheriot_rf.Cheriot*MSBClear) | vacuous ASSERT_IF with constant-0 antecedent |
| C class P (rows 12, 30, 32, 42-43) | Blocks :690-696 (controller), :1342-1344 and :1348-1350 (decoder); no branch/condition object exists for rows 12 (:684), 30 (:936-942) and 32 (:925-926): VCS folded the parameter select (section 5) | narrowed to the inner blocks (Critic R-3) |
| C.2 class D six default arms | Blocks controller :990-993, LSU :605-607, multdiv :522-524, id_stage :968-970, multdiv :238-240, icache :1268; the case-default branch vectors where URG emits them | explicit entries; the EC-3 attempts/failures fields read "TO BE FILLED" until the first measured regression (F-3) |
| A.8 carve-backs (ten named items and the v1 list) | 0 | never selected: the live halves of gated logic, the illegal arms, the RV32I mux arms, the EC-3 proof assertions |
| C class R rows 37-40 (Zcmp mismatched-state defaults) | 0 | OUT until EC-4 passes on a full measured regression (F-5) |

Totals (pass 8 file): 227 Block, 116 Branch vector, 769 Condition vector, 463 Toggle, 2 Fsm + 5 State +
12 Transition, 3 Assert lines in 41 (module, metric) scopes, 204 annotation groups.

## 3. Strict-load check against the round-0 re-baseline (author pre-check; Runtime's run is the record)

urg X-2025.06-SP2, `-dir regress_round_0_rebaseline/cov_unmeasured/merged.vdb -elfile gen_exclusions.el
-excl_strict -show ratios`, on the submit host (report-time only, no simulation):

| Pass | File state | Result |
|---|---|---|
| 1 | first generation | Warning UCAPI-ILOAD, 285 covered objects attempted (gen_precheck/gen_attempts_round0_rebaseline_pass1.log): bare Branch/Condition header lines exclude the WHOLE object (all arms), and `if (`/`case (` statement blocks inside the line ranges execute with their enclosing scope |
| 2-4 | vectors only for partial arms; statement headers skipped; A.1 as per-vector entries; ternary and negation vector semantics fixed | 60, 38, 1 covered attempts (logs pass2..4 kept as the --attempts inputs) |
| 5-7 | refutation feedback | an empty MODULE scope in the file made URG mis-scope the following entries (143 UCAPI-EXCOV errors on unrelated conditions); fixed by never emitting an empty scope |
| 8 | final | 0 warnings, 0 errors, no attempts.log (gen_precheck/gen_precheck_urg_pass8.log, gen_precheck_dashboard_pass8.txt) |

Gated-row totals (u_dut.u_ibex_core + u_dut.u_register_file, the R-001 scope) of the round-0
re-baseline with and without the file, as the flow computes them (Runtime pre-flight runtime-007,
below; numerators identical, only denominators move: the file removes nothing that the smoke covered):

| Metric | without (gen_round_0_rebaseline) | with gen_exclusions.el | objects removed |
|---|---|---|---|
| LINE | 1694/4351 | 1694/4057 | 294 |
| COND | 2547/9566 | 2547/9220 | 346 |
| TOGGLE | 1682/24538 | 1682/20596 | 3942 |
| FSM | 6/86 | 6/74 | 12 |
| BRANCH | 798/2418 | 798/2320 | 98 |
| ASSERT | 143/178 | 143/175 | 3 |

(The author pre-check dashboards under gen_precheck/ show URG's "Total Coverage Summary" row, which is
the informational u_dut scope: TOGGLE 1994/26958 -> 1994/23016 there includes the wrapper's own port
toggles, and its ASSERT figure 143/178 does not move because that summary already nets out
no-attempt assertions; the gated rows above are the numbers that matter and they move for every
metric, ASSERT included.)

Flow record (Runtime Manager, purpose-2 elcheck): dv/auto_dv/work/runtime/results/runtime-007/manifest.yaml
(pre-flight of the server path, 2026-09-03 08:52Z; out-tree regress_req_runtime-007, cov_elcheck with
the file, cov_plain without): elfile sha256 4a2a6c817d8a8c4da9d4e03e336bfe4fe9b5a839a36f0087eea9321eef162145,
urg rc 0, exclusion_violations 0, merge.log without any Warning-[ or Error-[ line, full_exclusions dump
written (12 files). rtl-arch-003 was refused in writing (the queue had no report-only request kind at
08:50Z); the re-file with the `elcheck` field, rtl-arch-004, was served at 09:0xZ:
dv/auto_dv/work/runtime/results/rtl-arch-004/manifest.yaml (out-tree regress_req_rtl-arch-004,
cov_elcheck with the file and its full_exclusions dump, cov_plain without): verdict ok, urg rc 0 on
both merges, exclusion_violations 0, merge_warnings empty, elfile sha256 recorded in full, gated rows
and excluded counts identical to runtime-007 (the table above). This manifest is the formal
strict-load record for the draft file (F-1 in draft form).

## 4. Refuted entries (covered in the round-0 re-baseline; dropped, kept in coverage)

48 entries the draft would have excluded were covered by the NOP smoke and are therefore reachable
(gen_exclusions_select_report.md, "Dropped" list, and the pass1..4 attempts logs). Classes:
- ibex_cheriot_ex: always_comb default assignments (cheriot_rf_we_raw = 0, tmp32a/b = 0, ...),
  `case (cheriot_adder_*_sel_i)` and `if (cheriot_setaddr_sel_i == ...)` statement headers, the
  reset arm `if (!rst_ni)` and reset-value assignments, the zero-value vectors of conditions on
  constant-0 internal selects (cheriot_setaddr_sel_i == X is 0 every cycle): the module's
  combinational logic runs with cheriot off; only the arm bodies and the 1-value vectors are dead.
  Correction to the draft's A.1 wording "everything except the live list": the object list is
  "every object whose value or arm requires a CHERIoT-only condition", which is what the file now holds.
- ibex_cs_registers :2014-2224: the reset arms of the cap registers (pcc_cap_q <= ..., mtvec_cap <= ...)
  and `cheriot_csr_rdata_o = 32'b0` default; `case (cheriot_csr_addr_i)` header; the PMP-illegal
  `if (...)` header at :707.
- ibex_id_stage Condition 37 `(csr_access_o & instr_executing & (param & On ? first_cycle : id_done))`:
  a ternary used as an OPERAND has the value of an arm, not of its select; the classifier now
  treats ternaries only at the top level.
- ibex_core Condition 90/91 (`instr_exec & !(On || Off)`): URG encodes a top-level negation by the
  value of the negated sub-expression; fixed in the classifier.
None of these is an RTL finding; all are coverage-tool semantics that the strict load exposed. They
are the reason F-1 requires the strict load on the measured regression itself.

## 5. Open items and notes for the reviewers

1. Assign-ternaries with a constant select (rtl/ibex_if_stage.sv:222-228, rtl/ibex_decoder.sv:202,
   rtl/ibex_controller.sv:684 and :866-868, rtl/ibex_cs_registers.sv:424-426, rtl/ibex_id_stage.sv:
   936-942, :925-926) have NO branch or condition object in the dump: VCS folded them (EC-2 by
   construction). Draft rows 4, 12 (the :684 part), 30, 32 therefore need no entry; the README says so
   instead of the file.
2. Conditions the classifier could not decide are listed in gen_exclusions_select_report.md
   ("mentioning a CHERIoT name but NOT selected"): mixed-operator parents whose constant sub-term is
   handled by URG's own sub-condition object, the `cheriot_csr_addr_i == CHERIOT_SCR_*` comparisons
   (constant ports compared with constants: value depends on the encoding; their lines are already
   Block-excluded), and the mtvec/misa ternaries on the BaseIsa parameter. Kept in coverage; the first
   measured regression's holes decide whether any is worth an explicit entry (Critic ruling per entry).
3. The seven "glitch-covered tie conditions" (Critic N-2 / F-4): the cheriot_enable_i ones
   (rtl/ibex_cheriot_ex.sv:970, rtl/ibex_cs_registers.sv:377, :1020, rtl/ibex_core.sv:1343) are in the
   file as A.4 vectors and loaded strictly under the -cm_glitch 0 build (R-002 recorded); the
   fetch_enable_i ones (rtl/ibex_core.sv:648, :649, :1414) were smoke-top ties only: in the real TB
   fetch_enable_i is a driven pin (Q-007), so they are NOT excluded.
4. The three assertion entries (MODULE ibex_register_file_ff, g_cheriot_rf.Cheriot*MSBClear) ARE
   honoured: the pass-8 asserts.txt marks all three "Excluded" (Summary: Excluded 3), the
   u_register_file hierarchy row moves from ASSERT 1/5 to 1/2 and the flow's gated row from 143/178
   to 143/175 (runtime-007). Only URG's top "Total Coverage Summary" ASSERT figure stays 143/178
   (its denominator already nets out assertions without attempts). Resolved 2026-09-03 08:58Z.
5. The class-D default-arm Blocks are in; URG emits no separate case-default branch vector for these
   case statements in this dump (the `default,` vector rule matched nothing), so the arm Blocks carry
   the class-D entries.
6. Instance names: the file uses MODULE scopes; the coverage trees u_dut.u_ibex_core and
   u_dut.u_register_file each contain exactly one instance of every module named, so the set is
   identical to INSTANCE scoping under any TB top (B.7 rule 5 satisfied without a top-name
   substitution).

## 6. Critic final-file conditions (gen_critic_exclusions_draft_v2.md section 5) -- checklist

| Cond. | Requirement | Status today | What closes it |
|---|---|---|---|
| F-1 | generated at the first measured regression, legal stimulus only, measured tests only (B.7), loaded with -excl_strict without a rejected entry (EC-5) | draft form: generated from the round-0 re-baseline dump and loaded strictly against that vdb with 0 rejections (section 3); rtl-arch-003 repeats it through the flow | re-run the generator on the first measured regression's dump; strict load there (Runtime gen_round.py --elfile) |
| F-2 | N-1 retention; every T022_* citation resolves | MET: dv/auto_dv/evidence/gen_t022_formal/ committed (Orchestrator 08:2xZ); every annotation names its T022_* proof and that directory | - |
| F-3 | EC-3 attempts/failures filled for the three guarded default arms | OPEN: annotations read "attempts N, failures 0 in <first measured regression>, TO BE FILLED" | the assertion report of the first measured regression (IbexCtrlStateValid, IbexLsuStateValid, IbexMultDivStateValid) |
| F-4 | LOG-007 decision recorded; glitch-covered tie Conditions only under -cm_glitch 0 | MET for the decision (R-002) and the four cheriot_enable_i conditions; the three fetch_enable_i conditions are deliberately absent (section 5 item 3) | - |
| F-5 | class R rows 37-40 absent unless EC-4 passed | MET: absent | stays absent until the seven per-state covers are hit on a full measured regression |
| F-6 | every entry carries the A.0 annotation; A.1 object list reproduced, not summarised | MET: 204 annotation groups, each with class, location, tie chain or parameter, EC set and pointer; A.1 is 702 explicit entries | - |
| F-7 | no entry outside the 43 rows, the six C.2 default arms and the A.1 object list | MET by construction of the selection spec (section 2); the refuted-and-dropped list narrows, never widens | - |

Pending EC-3 / EC-5 from the first measured regression, this file is the exclusion deliverable in
draft form; the Critic approves the file, not this README.
