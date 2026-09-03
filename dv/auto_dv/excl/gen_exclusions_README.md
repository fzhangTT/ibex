# gen_exclusions.el -- the coverage exclusion file (draft form, ahead of the first measured regression)

Owner: rtl-arch (T-069, 2026-09-03; revised 09:15Z after the cross-model review of dca91fd,
dv/auto_dv/reviews/2026-09-03-claude-diff-42e6f28d-dca91fd2.md; answers in
dv/auto_dv/evidence/gen_critic_response_exclusions.md). Build configuration: opentitan; DUT gen_dut_top
with the gated coverage trees u_dut.u_ibex_core and u_dut.u_register_file (Q-014 / R-001).

Authority chain (every path below is committed; what each contributes):
- dv/auto_dv/evidence/gen_exclusions_draft_v2.md: the exclusion draft the file implements (Part A
  carve-out entries A.1-A.8, Part B URG mechanism, Part C the 43 arcs with classes T/P/D/R, C.2 the
  six default arms). Promoted copy of the rtl-arch working file of the same name.
- dv/auto_dv/evidence/gen_critic_exclusions_draft_v2.md: the Critic's conditional approval of that
  draft with the evidence classes EC-1..EC-6 and the final-file conditions F-1..F-7 (section 6 here);
  gen_critic_exclusions_draft_v1.md is the earlier REQUEST-CHANGES it answers.
- dv/auto_dv/evidence/gen_unreachability_evidence.md: the k-induction proofs and constant-propagation
  evidence per arc (sections 4.1-4.3), the class-R bounded results (4.4-4.5), the retained-artefact map
  (section 8); the proofs themselves are re-runnable from dv/auto_dv/evidence/gen_t022_formal/.
- dv/auto_dv/evidence/gen_cheriot_carveout.md: the CHERIoT-only object inventory (buckets A-F) and the
  gating chain G1-G8 that the class-T annotations cite.
- dv/auto_dv/evidence/gen_param_resolution.md: every opentitan parameter value with its cite (class P
  and the tie); gen_excl_select.py re-reads the three class-P values from util/ibex_config.py at
  generation time and stops if they differ.
- dv/auto_dv/evidence/gen_hierarchy_map.md: the FSM/transition audit whose Part C rows the annotations
  quote as "row n".
- dv/auto_dv/tb/gen_dut_top.sv:206: the tie itself (CheriotEnable = IbexMuBiOff).
The DV Lead's feature-list table F-CHERI-001 mirrors THIS file row for row (draft A.8 authority
statement); never the reverse.

## 1. How the file is made (reproducible)

`gen_excl_select.py` turns the draft into URG entries: it parses a `urg -dump full_exclusions`
MODULE dump (`fullexclude_module.<metric>`), selects objects by rule, copies each entry verbatim (id,
checksum, signature, vector) so `-excl_strict` can verify it, and wraps every group in an ANNOTATION
carrying the A.0 justification (class, RTL location, tie chain or parameter, evidence class and
pointer). Scopes are `MODULE:` (every DUT module has exactly one instance, so MODULE and INSTANCE
select the same objects and the file does not depend on the TB top name); CHECKSUM lines are the
dump's own. It never emits an empty scope (URG mis-scopes the entries that follow one).

```
python3 dv/auto_dv/excl/gen_excl_select.py \
  --dump <outdir>/cov*/full_exclusions \
  --out dv/auto_dv/excl/gen_exclusions.el --report dv/auto_dv/excl/gen_exclusions_select_report.md \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass2.log \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass3.log \
  --attempts dv/auto_dv/excl/gen_precheck/gen_attempts_round0_rebaseline_pass4.log
  # add --allow-unfilled-ec3 only once the class-D EC-3 fields are filled from a measured regression
```

Selection rules, in the order the script applies them:
1. Configuration guard: `util/ibex_config.py opentitan vcs_opts` must give BranchPredictor = 0,
   BranchTargetALU = 1 and RV32B = RV32BOTEarlGrey (the class-P assumptions); otherwise the run stops.
2. A.3 Blocks and true-arm Branch vectors in the shared modules, by RTL line range from the draft;
   statement headers (`if (`, `case (`) inside a range are never selected because they execute with
   their enclosing scope.
3. ibex_cheriot_ex (A.1, revised): a GUARD ANALYSIS of rtl/ibex_cheriot_ex.sv computes, for every
   line, the enclosing if / else-if / else / case arms (the file's indentation is the nesting) and
   marks a line dead when an enclosing arm requires a constant-0 term or follows a constant-1 one.
   The constants are machine-checked: the 1-bit nets and all-zero multi-bit inputs that yosys
   `opt -full` ties to zero under the wrapper tie (t022_flat.il connect list, regenerable by
   gen_t022_formal/gen_t022_regen.sh step 3) plus the decoder defaults rtl/ibex_decoder.sv:297-303
   whose only other assignments are inside (cheriot_enable_i == On) arms; enum literals are read from
   rtl/ibex_cheriot_pkg.sv. Dead lines give Block entries and whole Condition objects; Branch vectors
   are selected per arm (a `case (1'b1)` item on a constant-0 operator bit, an `if` arm on a
   constant-0 term, an item of a `case` on an all-zero selector whose label is not 0). Everything
   else in the module, in particular the reachable-but-masked checking logic (check_rv32 :699-737,
   the all-false arms of check_cheriot :753-863, the fall-through of err_cause_comb :922, the
   always_comb defaults and the shared adder), stays in coverage. Each annotation names the guard
   and the constant term.
4. A.4 Condition vectors in every module: a vector is selected when a constant-tie operand takes its
   impossible value (operand values in URG's source order; a top-level negation or ternary condition
   is encoded by its inner expression or select; nested negations by the operand's own value). The
   fetch_enable_i and mcounteren_writable_i comparisons are driven pins in the real TB and are never
   selected.
5. A.5 Toggle: the constant CHERIoT-only ports of every module (struct-typed ports as their fields).
6. A.6 FSM (ls_fsm_cs CTX_* states and transitions, cap_rx_fsm_q wait states and all transitions),
   A.7 Assert (the three `ASSERT(name, cheriot_enabled |-> ...)` of the register file, vacuous).
7. Class P blocks (controller :690-696, decoder :1342-1344 / :1348-1350) and class D default arms.
   The three class-D spare-encoding arms (ctrl_fsm, ls_fsm, md_state) carry EC-3 fields that only
   a measured regression can fill; they are HELD OUT of the emitted file (the header line says so)
   until `--allow-unfilled-ec3` is given with the numbers in hand (Critic F-3).
8. `--attempts`: URG's attempts.log of a strict load refutes covered objects, which are dropped and
   listed in the selection report. A refuted object stays in coverage; it is a finding about the
   draft, never a reason to relax the load.

Reference dump used today: the round-0 re-baseline (dv/auto_dv/evidence/gen_round_0_rebaseline/,
out-tree regress_round_0_rebaseline/cov_unmeasured/full_exclusions, gen_smoke NOP program, -cm_glitch 0
build). The dump is a property of the BUILD (ids, checksums, signatures), so the same file loads
against any vdb of the same RTL and flags; the first measured regression re-runs the generator against
its own dump (F-1).

## 2. Content (what is in, what is out)

| Rule | Entries in the file | Notes |
|---|---|---|
| A.1 ibex_cheriot_ex dead arms | 75 Blocks, 66 Branch vectors, 119 Condition vectors (whole objects on dead lines) | 265 dead RTL lines found by the guard analysis; the module's live logic (about 60 percent of its statements) counts |
| A.3 Blocks / true-arm Branch vectors in the shared modules | 129 Blocks (incl. class P and the three class-D 2a arms), 17 Branch vectors | CHERIoT arm bodies; assign-ternaries with a constant select have no object (section 5) |
| A.4 Condition vectors | 551 vectors in 20 modules | impossible-value vectors only |
| A.5 Toggle | 463 port / struct-field entries | constant CHERIoT-only ports |
| A.6 FSM | 2 Fsm headers, 5 State, 12 Transition | explicit (constant analysis does not cover FSM) |
| A.7 Assert | 3 | vacuous register-file assertions |
| Class D spare-encoding arms (rows 1, 23, 33) | 0 (held out) | emitted only with --allow-unfilled-ec3 after the EC-3 fields are filled |
| A.8 carve-backs, class R rows 37-40 | 0 | never selected |

Totals (pass 10 file, md5 3b67ac6f909ac21d83609c9239399e68): 204 Block, 83 Branch-vector, 670
Condition-vector, 463 Toggle, 2 Fsm + 5 State + 12 Transition, 3 Assert lines in 41 (module, metric)
scopes, 384 annotation groups; 10 entries refuted by the strict load and dropped.

## 3. Strict-load record

Author pre-checks (urg X-2025.06-SP2 on the submit host, report-time only, no simulation, against
regress_round_0_rebaseline/cov_unmeasured/merged.vdb; logs under gen_precheck/):

| Pass | File state | Result |
|---|---|---|
| 1 | first generation (dca91fd lineage) | UCAPI-ILOAD, 285 covered objects attempted: bare Branch/Condition headers exclude the whole object; statement headers execute with their scope |
| 2-4 | vectors only; headers skipped; vector-encoding fixes | 60, 38, 1 attempts (the --attempts inputs) |
| 8 | dca91fd file | clean (kept as the record of the reviewed commit) |
| 9-10 | this file (guard analysis, EC-3 hold-out, config guard) | 0 warnings, 0 errors, no attempts.log (gen_precheck_urg_pass10.log, gen_precheck_dashboard_pass10.txt) |

Gated rows (u_dut.u_ibex_core + u_dut.u_register_file per R-001, summed from the URG hierarchy rows
of the pass-10 report and of dv/auto_dv/evidence/gen_round_0_rebaseline/hierarchy.txt):

| Metric | without the file | with this file | objects removed | entries emitted | note |
|---|---|---|---|---|---|
| LINE | 1694/4351 | 1694/4134 | 217 | 204 Blocks | a Block can span several source lines; Blocks on lines VCS already marks unreachable are no-ops |
| COND | 2547/9566 | 2547/9319 | 247 | 670 vectors | most tie-chain vectors are already Unreachable by constant analysis (-cm_seqnoconst): entries for them are no-ops |
| TOGGLE | 1682/24538 | 1682/20596 | 3942 | 463 ports/fields | toggle objects are per bit and per edge |
| FSM | 6/86 | 6/74 | 12 | 12 Transition (+5 State) | URG scores transitions only; states are listed, not counted |
| BRANCH | 798/2418 | 798/2353 | 65 | 83 vectors | vectors already Unreachable are no-ops |
| ASSERT | 143/178 | 143/175 | 3 | 3 | the three register-file assertions (URG's top summary row 143/178 nets out no-attempt assertions and does not move) |

URG status-token census of the pass-10 text report (modinfo.txt), per metric: LINE excluded 847 /
unreachable 1115 (baseline 1107); BRANCH excluded 244 / unreachable 373; TOGGLE excluded 828 /
unreachable 179 (baseline 190); ASSERT excluded 3; FSM excluded 18 rows. The "excluded" rows count
source lines / vector rows (several per URG object) and include objects that constant analysis had
already removed from the denominator, which is why they exceed the "objects removed" column. A
per-object join of the dump, the .el and the report (both carry line numbers) is the follow-up that
turns this census into an exact no-op list (response file, finding M-2).

Flow records (Runtime Manager, purpose-2 elcheck): dca91fd file: runtime-007 (pre-flight) and
dv/auto_dv/work/runtime/results/rtl-arch-004/manifest.yaml (formal; urg rc 0, 0 violations, gated
row LINE 1694/4057 COND 2547/9220 TOGGLE 1682/20596 FSM 6/74 BRANCH 798/2320 ASSERT 143/175). This
file: request dv/auto_dv/work/runtime/requests/rtl-arch-005.yaml filed 09:13Z; its manifest path is
appended here when served. rtl-arch-003 was refused in writing (no report-only request kind at 08:50Z).

## 4. Refuted entries (covered in the round-0 re-baseline; dropped, kept in coverage)

10 entries of the current selection were covered by the NOP smoke and are dropped (selection report,
"Dropped"); the earlier passes refuted 48 of the dca91fd selection. Classes, all coverage-tool
semantics rather than RTL findings: always_comb default assignments and statement headers execute
with their enclosing scope; reset arms execute at reset; a ternary used as an operand has the value of
an arm, not of its select; a top-level negation is encoded by its inner value. The dca91fd A.1 sweep
("everything in u_ibex_cheriot_ex not on the live list") is gone: the review showed it excluded
reachable-but-masked logic under an unreachability claim; the guard analysis of section 1 rule 3
replaces it and the annotations now name the dead guard.

## 5. Notes for the reviewers

1. Assign-ternaries with a constant select (rtl/ibex_if_stage.sv:222-228, rtl/ibex_decoder.sv:202,
   rtl/ibex_controller.sv:684 and :866-868, rtl/ibex_cs_registers.sv:424-426, rtl/ibex_id_stage.sv:
   936-942, :925-926) have no branch or condition object in the dump: VCS folded them (EC-2 by
   construction). Draft rows 4, 12 (the :684 part), 30 and 32 need no entry.
2. Conditions the classifier could not decide are listed in gen_exclusions_select_report.md
   ("mentioning a CHERIoT name but NOT selected"): mixed-operator parents whose constant sub-term is
   handled by URG's own sub-condition object, the `cheriot_csr_addr_i == CHERIOT_SCR_*` comparisons
   (lines already Block-excluded), the mtvec/misa ternaries on the BaseIsa parameter. Kept in coverage.
3. Glitch-covered tie conditions (Critic N-2 / F-4): the cheriot_enable_i ones (rtl/ibex_cheriot_ex.sv:
   970, rtl/ibex_cs_registers.sv:377, :1020, rtl/ibex_core.sv:1343) are A.4 vectors and load strictly
   under the -cm_glitch 0 build (R-002); the fetch_enable_i ones (rtl/ibex_core.sv:648, :649, :1414)
   were smoke-top ties only and are NOT excluded.
4. The three assertion entries are applied: asserts.txt marks them Excluded and the gated ASSERT row
   moves 178 -> 175 (rtl-arch-004 and the pass-10 hierarchy); the RTL macro is `ASSERT(name,
   cheriot_enabled |-> ...)` (rtl/ibex_register_file_ff.sv:237-239), as the annotation now says.
5. Class D: URG emits no separate case-default branch vector for these case statements; the default
   arm Blocks carry the entries (the three 2a arms are in; the three 2b arms are held out, item 7 of
   section 1).
6. MODULE scopes are exact for this DUT (one instance per module under u_dut); the assertion entries
   demonstrate it (reported under the instance path).

## 6. Critic final-file conditions (gen_critic_exclusions_draft_v2.md section 5) -- checklist

| Cond. | Requirement | Status today | What closes it |
|---|---|---|---|
| F-1 | generated at the first measured regression, legal stimulus only, measured tests only (B.7), loaded with -excl_strict without a rejected entry (EC-5) | draft form: generated from the round-0 re-baseline dump and loaded strictly against that vdb with 0 rejections (pass 10; rtl-arch-005 repeats it through the flow) | re-run the generator on the first measured regression's dump; strict load there (gen_round.py --elfile) |
| F-2 | N-1 retention; every T022_* citation resolves | MET: dv/auto_dv/evidence/gen_t022_formal/ committed; every annotation names its T022_* proof and that directory | - |
| F-3 | EC-3 attempts/failures filled for the three guarded default arms | OPEN, and the file no longer carries the unfilled groups: they are held out until the first measured regression's assertion report supplies the numbers (--allow-unfilled-ec3 then emits them with the fields filled) | assertion report of the first measured regression (IbexCtrlStateValid, IbexLsuStateValid, IbexMultDivStateValid) |
| F-4 | LOG-007 decision recorded; glitch-covered tie Conditions only under -cm_glitch 0 | MET (R-002; four cheriot_enable_i conditions in; fetch_enable_i ones absent by design) | - |
| F-5 | class R rows 37-40 absent unless EC-4 passed | MET: absent | stays absent until the seven per-state covers are hit on a full measured regression |
| F-6 | every entry carries the A.0 annotation; A.1 object list reproduced, not summarised | MET: 384 annotation groups; every ibex_cheriot_ex group names its dead guard and constant term (review HIGH fixed) | - |
| F-7 | no entry outside the 43 rows, the six C.2 default arms and the A.1 object list | MET by construction of the selection rules; the refuted-and-dropped list narrows, never widens | - |

Pending EC-3 / EC-5 from the first measured regression, this file is the exclusion deliverable in
draft form; the Critic approves the file, not this README.
