# gen_exclusions.el -- the coverage exclusion file (pass 14, generated from the first measured round)

Owner: rtl-arch (T-069, 2026-09-03; revised 09:22Z after the cross-model review of dca91fd,
dv/auto_dv/reviews/2026-09-03-claude-diff-42e6f28d-dca91fd2.md, and the Critic's REQUEST-CHANGES on it,
dv/auto_dv/docs/gen_critic_exclusions_v1.md; answers in dv/auto_dv/evidence/gen_critic_response_exclusions.md). Build configuration: opentitan; DUT gen_dut_top
with the gated coverage trees u_dut.u_ibex_core and u_dut.u_register_file (Q-014 / R-001).

Authority chain (every path below is committed; what each contributes):
- dv/auto_dv/evidence/gen_exclusions_draft_v2.md: the exclusion draft the file implements (Part A
  carve-out entries A.1-A.8, Part B URG mechanism, Part C the 43 arcs with classes T/P/D/R, C.2 the
  six default arms). Promoted copy of the rtl-arch working file of the same name.
- dv/auto_dv/docs/gen_critic_exclusions_draft_v2.md: the Critic's conditional approval of that
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
2. A.3 Blocks and true-arm Branch vectors in the shared modules. The draft's RTL line ranges only
   SCOPE the search: a Block is selected when it is inside an approved range AND the guard analysis
   of rule 3 (run on every module) finds it under a dead arm; statement headers (`if (`, `case (`)
   are never selected because they execute with their enclosing scope. Two kinds of range are
   explicit instead, with their cone stated in the annotation: the enum default arms (the cone is
   the enum declaration) and the case items of FSM states the k-induction proofs show are never held
   (LSU :565-603 CTX_WAIT_GNT1/GNT2/RESP, :618-623 CRX_WAIT_RESP1/RESP2; cone = the state register,
   proofs T022_LSU_NO_CTX, T022_CRX_IDLE; the held state CRX_IDLE :615-617 is NOT explicit, its
   `lsu_go_goodcap` arm is a dead guard like any other). A true-arm Branch vector is selected only when its select is constant 0 by the
   same predicate. Finally an explicit A.8 CARVE-BACK table (draft A.8 and its v1 list: module,
   signature regex or line range) is applied as the LAST filter over every emitted line, and every
   hit is reported; the selection report also lists every in-range block the predicate kept live.
3. GUARD ANALYSIS (ibex_cheriot_ex A.1 revised, and rule 2 for every shared module): the script
   computes, for every line of the module's RTL, the enclosing if / else-if / else / case arms (the file's indentation is the nesting) and
   marks a line dead when an enclosing arm requires a constant-0 term or follows a constant-1 one.
   The constants are machine-checked: the 1-bit nets and all-zero multi-bit inputs that yosys
   `opt -full` ties to zero under the wrapper tie (t022_flat.il connect list, regenerable by
   gen_t022_formal/gen_t022_regen.sh step 3) plus the decoder defaults rtl/ibex_decoder.sv:297-303
   whose only other assignments are inside (cheriot_enable_i == On) arms, the CONST0 tie-chain names,
   the *_en_cheriot / cheriot_csr_* nets of cs_registers, the opentitan parameters (util/ibex_config.py)
   and the RV32B define; enum literals are read from rtl/ibex_cheriot_pkg.sv and rtl/ibex_pkg.sv. Dead lines give Block entries and whole Condition objects; Branch vectors
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

Reference dump used today: the measured round_0 dump (dv/auto_dv/evidence/gen_round_0/, out-tree
regress_round_1/cov/full_exclusions), which pass 14 generated from. The earlier round-0 re-baseline
(regress_round_0_rebaseline/cov_unmeasured/full_exclusions, gen_smoke NOP program, -cm_glitch 0 build) was
the reference through pass 13 and is named in this file only as history. The dump is a property of the BUILD (ids, checksums, signatures), so the same file loads
against any vdb of the same RTL and flags; the first measured regression re-runs the generator against
its own dump (F-1).

## 2. Content (what is in, what is out)

| Rule | Entries in the file | Notes |
|---|---|---|
| A.1 ibex_cheriot_ex dead arms | Blocks, Branch vectors and whole Condition objects on dead lines (counts in the selection report: CHERIOT_EX lines) | 265 dead RTL lines found by the guard analysis; the module's live logic counts |
| A.3 Blocks / true-arm Branch vectors in the shared modules | see the generated counts block | in-range AND dead-guard (or explicit cone); the in-range blocks kept live by the predicate and by the A.8 carve-back table are counted in the block below and listed in the selection report |
| A.4 Condition vectors | impossible-value vectors only (count in the selection report) | each annotation names the constant operand, its value and the impossible bit |
| A.5 Toggle | 463 port / struct-field entries | constant CHERIoT-only ports |
| A.6 FSM | 2 Fsm headers, 5 State, 12 Transition | explicit (constant analysis does not cover FSM) |
| A.7 Assert | 3 | vacuous register-file assertions |
| Class D spare-encoding arms (rows 1, 23, 33) | 3 (included since pass 14) | EC-3 fields filled from the round_0 assertion report; the .el header records the same |
| A.8 carve-backs, class R rows 37-40 | 0 | selected and removed by the carve-back filter: 7 Blocks, 3 vectors |

Totals of the current file (generated block; the numbers are written by the generator, never typed):

<!-- COUNTS-BEGIN -->
Generated by gen_excl_select.py from the run that produced this file (md5 1cfb35e2894625a8ab27b52541c041a7); do not edit by hand.

| Quantity | Value |
|---|---|
| entry lines | 1424 (3 Assert, 189 Block, 83 Branch, 667 Condition, 2 Fsm, 5 State, 463 Toggle, 12 Transition) |
| (module, metric) scopes / annotation groups | 41 / 495 |
| in-range shared-module blocks kept in coverage (no dead guard) | 21 |
| in-range blocks kept in coverage by the A.8 carve-back table | 7 |
| entries refuted by the strict-load attempts logs and dropped | 0 |
| emitted lines removed by the carve-back filter | 3 |
<!-- COUNTS-END -->

## 3. Strict-load record

Author pre-checks (urg X-2025.06-SP2 on the submit host, report-time only, no simulation; through pass 13
against regress_round_0_rebaseline/cov_unmeasured/merged.vdb and from pass 14 against the measured
regress_round_1/cov/merged.vdb; logs under gen_precheck/):

| Pass | File state | Result |
|---|---|---|
| 1 | first generation (dca91fd lineage) | UCAPI-ILOAD, 285 covered objects attempted: bare Branch/Condition headers exclude the whole object; statement headers execute with their scope |
| 2-4 | vectors only; headers skipped; vector-encoding fixes | 60, 38, 1 attempts (the --attempts inputs) |
| 8 | dca91fd file | clean (kept as the record of the reviewed commit) |
| 9-10 | cheriot_ex guard analysis, EC-3 hold-out, config guard (file recorded by rtl-arch-005) | 0 warnings, 0 errors, no attempts.log |
| 11-12 | guard analysis on every shared module, A.8 carve-back filter (Critic CR-M-1); the file of commit 4125c36 | 0 warnings, 0 errors, no attempts.log (gen_precheck_urg_pass12.log, gen_precheck_dashboard_pass12.txt) |
| 13 | this file: annotation-only regeneration for the 4125c36 re-review (term names in A.4 groups, evidence path, negation precedence, per-module scoping); sorted entry set identical to pass 12 | 0 warnings/errors, attempts file: no (gen_precheck_urg_pass13.log, gen_precheck_dashboard_pass13.txt) |
| 14 | F-1 regeneration against the round_0 dump (/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/full_exclusions) with the queued edits (L-1, DL-1, CM-18..CM-20, docs/ repoint); EC-3 filled from dv/auto_dv/evidence/gen_round_0/gen_asserts.txt (round_0). Naming: the team's "round 1" is this flow's measured round_0, because the flow counts measured rounds from zero while the run itself carries regress_tag round_1, and round_0_rebaseline named elsewhere in this file is the earlier unmeasured baseline, not this round. | urg rc 0, 0 UCAPI warnings, 0 UCAPI errors, attempts file: no, refutation iterations 1 (this last is the driver's own loop count in gen_excl_f1_pass.py, not a urg-reported figure: the strict log carries no refutation, rejection or unmatched-entry line, so zero rejections is what the log shows and the iteration count is the tool's) (gen_precheck_urg_round_0.log, gen_precheck_dashboard_round_0.txt). EC-2 evidence of this round retained with the file (B.7 rule 3): gen_precheck/gen_precheck_constfile_gen_tb_round_0.txt.gz, the measured build's constfile.txt, 369118 bytes and 7051 lines uncompressed, sha256 of the plain text d84de5fcaf2f4bdce75795477ab4519758fff2000ff725b169fe01bb5b6160f6, checked with `gzip -dc dv/auto_dv/excl/gen_precheck/gen_precheck_constfile_gen_tb_round_0.txt.gz | sha256sum`; the pass writes it gzip -n, so the same constfile always gives the same bytes. |

No-op join of pass 14 (every Block entry against the plain report's line status before exclusions, so a
reader can see how much of the file changes a number and how much documents intent):

| Class | Entries | Meaning |
|---|---|---|
| NO-OP | 105 | the object was already uncovered-and-unreachable or already excluded in the plain report, so the entry moves no number |
| EFFECTIVE | 84 | the object was scored in the plain report and this entry removes it |
| UNRESOLVED-REPORT | 0 | entry names an object the plain report does not carry |
| UNRESOLVED-DUMP | 0 | entry names an object the dump does not carry |
| ANOMALY | 0 | entry resolves to an object whose status contradicts its class |

So an entry count is not a coverage impact: 84 of the 189 Block entries move a number and 105 record
intent. The per-entry join behind this table is retained with the file:
gen_precheck/gen_precheck_noop_join_round_0.md (sha256 6431104931c66372dc6a711dce684deff73bff47e314236150105579692ef122),
written by the pass and regenerated by any re-run of it.

Re-deriving these rows: URG appends "(x)" to an instance name in hierarchy.txt when its subtree carries
exclusions, so the strict report's rows read u_ibex_core(x) and u_register_file(x); a match on the bare
name finds nothing there and yields zeros (found by the pass-14 elcheck).

Gated rows (u_dut.u_ibex_core + u_dut.u_register_file per R-001, summed from the URG hierarchy rows
of the pass-14 plain and strict reports of the round_0 merge):

| Metric | without the file | with this file | objects removed | entries emitted | note |
|---|---|---|---|---|---|
| LINE | 3654/4359 | 3654/4158 | 201 | 189 Blocks | a Block can span several source lines; Blocks on lines VCS already marks unreachable are no-ops |
| COND | 6464/9624 | 6464/9375 | 249 | 667 vectors | most tie-chain vectors are already Unreachable by constant analysis (-cm_seqnoconst): entries for them are no-ops |
| TOGGLE | 16877/25044 | 16877/21102 | 3942 | 463 ports/fields | toggle objects are per bit and per edge |
| FSM | 38/86 | 38/74 | 12 | 12 Transition (+5 State) | URG scores transitions only; states are listed, not counted |
| BRANCH | 1831/2428 | 1831/2363 | 65 | 83 vectors | vectors already Unreachable are no-ops |
| ASSERT | 166/179 | 166/176 | 3 | 3 | the three register-file assertions; URG's top summary row nets out no-attempt assertions and DOES move for this round, 229/257 without the file to 229/254 with it, the same 3 objects (the 143/178 figure here before pass 14 was the re-baseline's and is superseded) |

URG status-token census of the pass-10 text report (the shared-module change of pass 11-12 moves 18 Blocks; the census was not redone) (modinfo.txt), per metric: LINE excluded 847 /
unreachable 1115 (baseline 1107); BRANCH excluded 244 / unreachable 373; TOGGLE excluded 828 /
unreachable 179 (baseline 190); ASSERT excluded 3; FSM excluded 18 rows. The "excluded" rows count
source lines / vector rows (several per URG object) and include objects that constant analysis had
already removed from the denominator, which is why they exceed the "objects removed" column. A
per-object join of the dump, the .el and the report (both carry line numbers) is the follow-up that
turns this census into an exact no-op list (response file, finding CM-3).

Flow records (Runtime Manager, purpose-2 elcheck; times verbatim from the manifests):
- rtl-arch-003 (received 2026-09-03T08:50:30Z): refused in writing, reason `invalid request: tests must
  be a non-empty list, a comma list, or a tier word (empty only with elcheck)` (the request lacked the
  `elcheck` mapping).
What these four records are, and are not: they are the retained REQUEST records of passes 9 to 13,
carrying what their server wrote at the time. Unlike gen_elcheck_rtl_arch_009.yaml, none carries a
served block with the verdict, the received and finished stamps, the return codes and the six gated
rows; each carries the request fields and a notes paragraph quoting a return code. The stamps and
figures in the four bullets below come from their results manifests, which are not retained, so those
values are not re-derivable from this repository the way the pass-14 row's are. Raising the four to the
009 standard is a separate item, not done here.

- runtime-007 (pre-flight) and request rtl-arch-004, record retained at
  dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_004.yaml (served figures below from its results
  manifest, received
  08:58:25Z, finished 08:58:31Z): the dca91fd file, urg rc 0, 0 violations, gated row LINE 1694/4057
  COND 2547/9220 TOGGLE 1682/20596 FSM 6/74 BRANCH 798/2320 ASSERT 143/175.
- request rtl-arch-005, record retained at dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_005.yaml
  (served figures below from its results manifest, received 09:13:43Z, finished 09:13:52Z):
  the pass-10 file (sha256 e43c2dcb50ffd9a23655c11a56e01ca263b321e44cc3029db764579015636039), verdict ok,
  urg rc 0 on both merges, 0 violations, empty merge_warnings, gated row LINE 1694/4134 COND 2547/9319
  TOGGLE 1682/20596 FSM 6/74 BRANCH 798/2353 ASSERT 143/175, excluded counts 217/247/3942/12/65/3.
- request rtl-arch-006, record retained at dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_006.yaml
  (served figures below from its results manifest, received 2026-09-03T09:30:41Z, finished 2026-09-03T09:30:49Z): THIS
  file (pass 12, sha256 103eb06933839dec301bff6c9cf68dbf20f1143ae921db330a364fad5bb52e5a), verdict ok, urg rc 0 on both merges, 0 violations, empty
  merge_warnings, full_exclusions dump written, gated row LINE 1694/4154 COND 2547/9319 TOGGLE
  1682/20596 FSM 6/74 BRANCH 798/2353 ASSERT 143/175, excluded counts 197/247/3942/12/65/3: identical
  to the pass-12 pre-check: the formal record of commit 4125c36.
- request rtl-arch-007, record retained at dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_007.yaml
  (served figures below from its results manifest, received 2026-09-03T09:50:02Z, finished
  2026-09-03T09:50:08Z): THIS file (pass 13, sha256
  3a815ffc68358b5e4499af0d45106936bbd9d3173350be076805ccd8f5331839), verdict ok, urg rc 0 on both
  merges, 0 violations, empty merge_warnings, full_exclusions dump written, gated row LINE 1694/4154
  COND 2547/9319 TOGGLE 1682/20596 FSM 6/74 BRANCH 798/2353 ASSERT 143/175, excluded counts
  197/247/3942/12/65/3: identical to rtl-arch-006, as an annotation-only regeneration requires.
- dv/auto_dv/evidence/gen_round_0/gen_regress_manifest.yaml (round_0, measured merge /proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/cov/merged.vdb): the file of pass 14 (md5 1cfb35e2894625a8ab27b52541c041a7, sha256 91dbc8c7ff9ce60b40a35e0ad289ffdb40ea597c28cbac6b21b8f8e7c3009c93), author strict load urg rc 0, 0 warnings, 0 errors, gated row LINE 3654/4158 COND 6464/9375 TOGGLE 16877/21102 FSM 38/74 BRANCH 1831/2363 ASSERT 166/176; Runtime elcheck: request rtl-arch-009, its record retained in this repository at dv/auto_dv/evidence/gen_round_0/gen_elcheck_rtl_arch_009.yaml (received 2026-09-05T01:53:02Z, finished 2026-09-05T01:57:16Z), verdict PASS, urg rc 0 with 0 UCAPI warnings and 0 UCAPI errors, no entry rejected under -excl_strict. The Runtime Manager built its invocation from the request rather than from this author's precheck artefacts, ran its own baseline and strict loads against the same merged vdb, and reports all six gated rows identical to the author's in both directions with the covered count equal on both sides of every metric; its baseline LINE row 3654/4359 equals the round's own gate row, which is the control that its extraction was right.

## 4. Refuted entries (covered in the round-0 re-baseline; dropped, kept in coverage)

0 entries of the current selection are refuted by the attempts logs in force (the COUNTS block carries the
same number); the attempts logs of passes 1-4 refuted 48 entries of the dca91fd selection and 10 of the pass-9/10
selection, and the current predicates never select those objects. Classes, all coverage-tool
semantics rather than RTL findings: always_comb default assignments and statement headers execute
with their enclosing scope; reset arms execute at reset; a ternary used as an operand has the value of
an arm, not of its select; a top-level negation is encoded by its inner value. The dca91fd A.1 sweep
("everything in u_ibex_cheriot_ex not on the live list") is gone: the review showed it excluded
reachable-but-masked logic under an unreachability claim; the guard analysis of section 1 rule 3
replaces it and the annotations now name the dead guard. The Critic's M-1 (rtl/ibex_cs_registers.sv:2130
`mstack_epc_cap_q <= mepc_cap`, live on every non-debug trap, selected by the A.3 range in dca91fd) showed
the same defect class in the shared modules; rule 2 now requires a dead guard inside the range and the
A.8 carve-back table is a last filter. The predicate also uncovered two dca91fd exclusions nobody had
flagged: cs_registers :473 `csr_rdata_int = mtvec_q` and :482 `csr_rdata_int = mepc_q`, the live RV32I
else arms of the On-gated illegal check; both are back in coverage.

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
   moved 178 -> 175 at pass 10 against the re-baseline (rtl-arch-004 and the pass-10 hierarchy); the
   measured round_0 figures are 179 -> 176 in the section 3 table. The RTL macro is `ASSERT(name,
   cheriot_enabled |-> ...)` (rtl/ibex_register_file_ff.sv:237-239), as the annotation now says.
5. Class D: URG emits no separate case-default branch vector for these case statements; the default
   arm Blocks carry the entries. All three are in since pass 14: the 2b arms were held out only until a
   measured round supplied the EC-3 attempt and failure numbers, which round_0 did.
6. MODULE scopes are exact for this DUT (one instance per module under u_dut); the assertion entries
   demonstrate it (reported under the instance path).
7. Kept in coverage although arguably dead (conservative side of the predicate and the carve-back
   filter): cs_registers :2142 `mepc_cap <= gen_scr.mstack_epc_cap_q` (dead guard `(On) && mret && nmi`,
   removed because its text matches the mstack_epc_cap_q carve-back); the SCR read-mux case items
   :2018-2048 (selector cheriot_csr_addr_i is constant 0, but the indentation-based analysis did not
   resolve that case statement); three register-file Condition vectors on the `cheriot_enabled ? rcap_r0
   / rf_shared[...]` ternaries (select constant 0, text matches the shared-net carve-backs). Candidates for
   explicit entries with their cone at the first measured regression; none is a correctness risk.
8. The entry checksums are not a load-time guard (Critic O-1, measured: changing one digit of an entry
   checksum changes no number and raises no warning). URG matches objects by id and signature, so
   -excl_strict catches a file that has gone stale against changed RTL only where the named object has
   become covered. Object ids are per-build ordinals in the same way: regenerating from the earlier
   re-baseline dump gives five entries over four ibex_if_stage Condition objects with identical
   checksums, expressions and vectors but ids 21/33/36/39 where this file has 25/37/40/43 (the pass
   self-test classifies such a difference as a renumbering and reports it). The generator re-run
   against the round's own dump, not the checksum, is what keeps the file honest.

## 5b. In-range objects the predicate keeps in coverage (with the reason each is live)

Every one of these sits inside a draft A.3 range and is NOT excluded; the selection report prints the
same list under "live:" / "carve-back:". None carries a Class T annotation any more.

| RTL object | Why it is reachable in RV32I mode (the cone) |
|---|---|
| rtl/ibex_cs_registers.sv:473 `csr_rdata_int = mtvec_q;`, :482 `csr_rdata_int = mepc_q;` | else arms of `if ((dual) && (cheriot_enable_i == On)) illegal_csr`: every RV32I read of mtvec / mepc executes them (excluded in dca91fd; found by the predicate) |
| rtl/ibex_cs_registers.sv:682, :690, :698 `illegal_csr = 1'b1;` | else arms of the MSHWM / MSHWMB / CDBG_CTRL read cases: a read of 0xBC1/0xBC2/0xBC4 traps (draft A.8, feature CHERI off-behaviour) |
| rtl/ibex_cs_registers.sv:2018-2053 SCR read-mux items and default | `case (cheriot_csr_addr_i)`: the selector is constant 0 (cheriot_ex csr_addr_o) and the SCR literals resolve to 24..31, so only the default arm executes; the indentation-based analysis does not parse this case statement's item layout, the items stay in coverage (candidates for explicit entries at the first measured regression) |
| rtl/ibex_cs_registers.sv:2065, :2114, :2136, :2155, :2170, :2185, :2203, :2220 reset-value assignments | `if (!rst_ni)` arms execute at every reset |
| rtl/ibex_cs_registers.sv:2128, :2130 `mstack_epc_cap_q <= ...` | reset arm; `else if (mstack_en)` with mstack_en set on every non-debug trap entry (:933): live shadow-capability update (Critic CR-M-1, draft A.8) |
| rtl/ibex_cs_registers.sv:2142 `mepc_cap <= gen_scr.mstack_epc_cap_q;` | guard `(On) && csr_restore_mret_i && nmi_mode_i` is dead, but the statement text matches the mstack_epc_cap_q carve-back; kept in coverage on the conservative side |
| rtl/ibex_decoder.sv:351, :824, :856, :873 `illegal_insn = 1'b1;` | the `else` arms of the CJALR / OPCODE_CHERI / OPCODE_AUICGP checks: reached by the illegal-encoding tests (draft A.8 items 2 and 8) |
| rtl/ibex_load_store_unit.sv:575, :589, :601 `ls_fsm_ns = IDLE;`, :619, :623 `cap_rx_fsm_d = ...` | inside the never-held CTX_* / CRX_WAIT_* case items: EXCLUDED under the explicit never-held-state cone (T022_LSU_NO_CTX, T022_CRX_IDLE), listed here because the guard predicate alone would not have selected them |
| rtl/ibex_register_file_ff.sv Condition vectors on `cheriot_enabled ? rcap_r0 / rf_shared[...]` ternaries (3) | select constant 0 (excludable) but the vector text matches the shared-net carve-backs; kept in coverage on the conservative side |
| rtl/ibex_cheriot_ex.sv check_rv32 :699-737, the all-false arms of check_cheriot :753-863, err_cause_comb :922, shared_adder defaults, always_comb defaults, reset arms | no dead guard: reachable RV32I checking logic whose result is masked downstream (cross-model CM-1); counts |

## 5a. Soundness of each selection rule (why an emitted object cannot be reachable)

| Rule | Predicate | Why it is sound | Residual risk and its check |
|---|---|---|---|
| A.3 / P Blocks (rule 2) | inside an approved range AND every enclosing arm chain has an arm whose condition is constant 0, or follows an arm whose condition is constant 1 | a statement executes only when every enclosing arm is taken; an arm whose condition is a constant-0 expression (tie compare, netlist-constant net, CONST0 tie-chain net, *_en_cheriot, opentitan parameter, RV32B define) is never taken | the constant table: netlist constants are machine-checked (yosys), CONST0 names are k-induction proved (T022_*), parameters come from util/ibex_config.py at generation; the indentation nesting is checked by the strict load (a misparse that marks a live arm dead is refuted as covered once any test executes it) |
| explicit ranges (rule 2) | enum default arms; case items of never-held FSM states | full enum encoding leaves no default value; T022_LSU_NO_CTX / T022_CRX_IDLE prove the states never held | fault injection into the state register is out of the measured regressions (B.7 rule 6) |
| A.1 ibex_cheriot_ex (rule 3) | same guard predicate with the module's own constant table | as rule 2 | reachable-but-masked logic has no dead guard and therefore counts |
| A.4 Condition vectors (rule 4) | a vector in which an operand that is constant takes the value it cannot take | URG vector bits are operand values; the constant operand never shows the other value | the encoding conventions (top-level negation / ternary) were validated by the strict load in passes 1-4; the fetch_enable_i / mcounteren_writable_i pins are excluded from the constant table by name |
| A.5 Toggle (rule 5) | explicit constant-port list | ports tied or proved constant (bucket D, T022_CORE_CHERI0/_B, T022_RF_CAP0) | a port that toggles is refuted as covered by the strict load |
| A.6 FSM, A.7 Assert (rule 6) | explicit lists | never-held states (proofs above); vacuous assertions with a constant-0 antecedent | as above |
| carve-back filter | explicit A.8 table | removes any live object the predicates might still pick; hits are reported | none (it only removes) |
| --attempts | URG-refuted objects dropped | a covered object is reachable by definition | none |

## 6. Critic final-file conditions (gen_critic_exclusions_draft_v2.md section 5) -- checklist

| Cond. | Requirement | Status today | What closes it |
|---|---|---|---|
| F-1 | generated at the first measured regression, legal stimulus only, measured tests only (B.7), loaded with -excl_strict without a rejected entry (EC-5) | MET at pass 14: generated from the measured round_0 dump (regress_round_1/cov/full_exclusions), measured entries only, and loaded strictly against that merge with 0 rejections three times over (the author pass, the independent elcheck rtl-arch-009, the Critic's own load) | - |
| F-2 | N-1 retention; every T022_* citation resolves | MET: dv/auto_dv/evidence/gen_t022_formal/ committed; every annotation names its T022_* proof and that directory | - |
| F-3 | EC-3 attempts/failures filled for the three guarded default arms | CLOSED at pass 14: the first measured regression (round_0) supplied the numbers, the fields are filled from its assertion report, and the file carries all three arms | assertion report of the first measured regression (IbexCtrlStateValid, IbexLsuStateValid, IbexMultDivStateValid) |
| F-4 | LOG-007 decision recorded; glitch-covered tie Conditions only under -cm_glitch 0 | MET (R-002; four cheriot_enable_i conditions in; fetch_enable_i ones absent by design) | - |
| F-5 | class R rows 37-40 absent unless EC-4 passed | MET: absent | stays absent until the seven per-state covers are hit on a full measured regression |
| F-6 | every entry carries the A.0 annotation; A.1 object list reproduced, not summarised | MET: 495 annotation groups over 1424 entries (the counts block above; 381 was the pass-12 figure); every ibex_cheriot_ex group names its dead guard and constant term (cross-model HIGH); every shared-module Block sits under a dead guard or an explicit cone (Critic M-1) | closed by the Critic final-file verdict (gen_critic_excl_final.md, APPROVE) |
| F-7 | no entry outside the 43 rows, the six C.2 default arms and the A.1 object list | MET: the A.8 carve-back table is the last filter and mstack_epc_cap_q (Critic M-1) is no longer in the file; the refuted-and-dropped list narrows, never widens | closed by the Critic final-file verdict (gen_critic_excl_final.md, APPROVE) |

## 7. EC-3 fill at the first measured regression (mechanical procedure for F-3)

One run per measured round drives all of this: `dv/auto_dv/excl/gen_excl_f1_pass.py --round-dir dv/auto_dv/evidence/gen_round_<n> --pass-label <n>` (generator with the EC-3 fill, strict load with a bounded refutation loop, plain load, gated rows, Block no-op join, constfile copies, README delta); its self-test rehearses on the round-0 re-baseline.

Inputs, per the Runtime flow (dv/auto_dv/docs/gen_runtime_api.md, gen_round.py): a measured round writes
its URG report to `<out_root>/regress_round_<n>/cov/report/` (out_root from dv/auto_dv/work/runtime/
gen_site.yaml, today /proj_soc/user_dev/fzhang/ibex_dv_out) and records `coverage.report_dir` in
`dv/auto_dv/evidence/gen_round_<n>/gen_regress_manifest.yaml`; the evidence directory copies the URG report files under the
gen_ landing prefix (gen_dashboard.txt, gen_hierarchy.txt, gen_tests.txt, ...) and, from the first measured round on, gen_asserts.txt
(Runtime change of 2026-09-03 09:3xZ, gen_runtime_api.md 7d; earlier round directories are not
re-collected), so the fill cites the committed copy dv/auto_dv/evidence/gen_round_<n>/gen_asserts.txt. The file names
are constants of dv/auto_dv/flow/gen_flow_const.py (EVIDENCE_FILE_PREFIX, ROUND_EV_ASSERTS, ROUND_EV_REGRESS_MANIFEST, ROUND_EC3_ASSERTS_RE), imported by gen_excl_select.py and
gen_excl_f1_pass.py; this README spells them out for the reader only.

Fields read: in gen_asserts.txt (the committed copy of the report's asserts.txt), section "Detail Report for Assertions", the rows whose
name ends in IbexCtrlStateValid (rtl/ibex_controller.sv:1104-1106), IbexLsuStateValid
(rtl/ibex_load_store_unit.sv:821-824), IbexMultDivStateValid (rtl/ibex_multdiv_fast.sv:532-533); the
columns are `ASSERTIONS CATEGORY SEVERITY ATTEMPTS REAL SUCCESSES FAILURES INCOMPLETE`; EC-3 requires
ATTEMPTS > 0 and FAILURES == 0 for each of the three (REAL SUCCESSES is recorded too).

Command (the only way the three class-D spare-encoding groups enter the file):

```
python3 dv/auto_dv/excl/gen_excl_select.py --dump <report_dir>/../full_exclusions \
  --out dv/auto_dv/excl/gen_exclusions.el --report dv/auto_dv/excl/gen_exclusions_select_report.md \
  --attempts <the strict-load attempts logs in force> \
  --ec3-asserts dv/auto_dv/evidence/gen_round_<n>/gen_asserts.txt --ec3-round round_<n>
```

The generator accepts only `dv/auto_dv/evidence/gen_round_<n>/gen_asserts.txt` whose sibling
gen_regress_manifest.yaml records a measured merge (coverage.dashboard_txt set), and records that relative
path in the annotations and the .el header; it refuses the fill (exit non-zero, names the reason) when
the path is anywhere else, the round is unmeasured, a row is missing, ATTEMPTS is 0 or FAILURES is not 0; when it fills, each of the three annotations reads "attempts A, failures 0 in
round_<n> (gen_asserts.txt)" and the .el header line states the source. Then: strict load of the new file
against that round's merged vdb (F-1/EC-5), the round's `-dump full_exclusions` (retained by the round
under gen_round_<n>/) and its constfile.txt (retained by this pass under gen_precheck/, gzip -n) per B.7
rule 3, Critic re-review of the file.

EC-3 and EC-5 came from the first measured round at pass 14, so this file is the exclusion deliverable
in its final form for round_0; the Critic approved it there (dv/auto_dv/evidence/gen_critic_excl_final.md).
The Critic approves the file, not this README. Each later measured round re-runs the pass against its own
dump, which is what keeps F-1 true rather than the approval carrying forward.
