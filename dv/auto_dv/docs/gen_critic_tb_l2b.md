# Critic verdict: tb-infra landing 2b (commit d752fb3, diff base f146ceb)

Artifacts reviewed (committed blobs at d752fb3; sha256 first 16 hex):

- dv/auto_dv/tb/gen_protocol_props.sv  406795a16b383e42
- dv/auto_dv/tb/gen_binds.sv  aea0cf20ebfce630
- dv/auto_dv/env/gen_fcov_pkg.sv  f33383f8b031b3a1
- dv/auto_dv/env/gen_wit_bins.svh  7e83e60046d40a76
- dv/auto_dv/env/gen_checkers_pkg.sv  f2e329dfebe99346
- dv/auto_dv/env/gen_rvfi_pkg.sv  7927a36ea2e6e470
- dv/auto_dv/env/gen_env_pkg.sv  67bbe350622796c8
- dv/auto_dv/gen_tb/gen_bridge.py  98823dea9edfa86b
- dv/auto_dv/evidence/gen_tdd_step2b.md  76cd4a68dc902091
- dv/auto_dv/mutations/gen_mut_step2b.md  3d80c47fd206bc25
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  c84f4b9b17f5ce30
- dv/auto_dv/docs/gen_component_api_scoreboard.md  939c23c3cf115850
- dv/auto_dv/docs/gen_component_api_fcov.md  0ac0ddb98c39a28f
- dv/auto_dv/docs/gen_component_api_binds.md  4fa21607874cb364
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  5b758d437973ba1f
- plus the 229 added logs under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations,knobs_codegen}/gen_fu_l2b_* (manifest rows recomputed)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Review basis: docs/dv/dv_principles.md sha256 d9c27db18f511411,
DV_prompt.txt, the RISC-V specifications under tools/specs/, this clone's RTL and doc/.
Method: clean archive of d752fb3 (git archive to the scratchpad); library self-test PASS and flow self-test PASS on the
archive; two unnamed subagents (an evidence audit of the 229 logs, the manifest and the mutant records; a derivation
review of the asserts, the covergroup and the three rules), both told the fence and not to open dv/auto_dv/reviews/;
every finding below was then checked first-hand against the blobs unless marked audit-quoted. The parallel cross-model
artifact was not read before Sections 1-5 were written; the only exposure was its file name in a directory listing
(2026-09-03-claude-diff-f146ceba-d752fb36.md). Section 6 is the reconciliation, written afterwards.

CRITIC VERDICT: REQUEST-CHANGES

One medium (M-3) is an as-built claim in the scoreboard document that the code does not implement and that the same
landing's response file says is owed; an undisclosed medium cannot be recorded as owed. M-1 and M-2 are disclosed and
are recorded as owed with conditions. The engineering content of the landing (the SVA layer, the covergroup, the
three rules, the mutants) is verified and sound; the changes required are in Section 5 and are small.

## 1. What was verified

### 1.1 Evidence audit (retained logs)

- Manifest: 229 added rows in gen_manifest.md; md5 and byte size recomputed from `git show d752fb3:<path>` for every row:
  229 match, 0 mismatch, 0 rows without a file, 0 added files without a row. Working-tree and archive copies equal the
  blobs (229/229). No rtl/ file in the commit (`git diff --name-only f146ceb d752fb3 | grep '^rtl/'` = 0).
- Builds: 64 run headers, all with build_sources_sha256; 11 distinct shas, each equal to exactly one compile log's
  `sources sha256` line: 68a36e6ac32db967 (l2b/a: 11 base canaries + RM1..RM3), ea8cfe1aa2865c30 (wit/a), 8d5824cba05661e5
  (wit/b), 242f0558621c52da (wit/c), 5ca9fd98c937c26f (wit/e = shared compile = RM4), f7289c6b83086cd2 (final), and one
  per agent-side mutant (MUT-M af81efcfe78a1b84, MUT-N d089c40458b67369, WM1 3e91ae996ae27f98, MB13 776392d1e882e0ed,
  MB14 4e2d112c2159b89c). The recipe of gen_tb_local.sh applied to the clean d752fb3 export gives f7289c6b83086cd2: the
  final set (6 runs, 18:05:04-18:05:13Z) is on the committed sources.
- Mutants (retained catch + ablation triads, 18/18 header shas equal to their compile logs). The mutated file's original
  sha256 printed by the driver equals the committed blob in every case: gen_agents_pkg.sv 8160e436ce3ecad7 and
  gen_protocol_props.sv 406795a16b383e42 (the tree line of the MUT-M / MUT-N batch), gen_fcov_pkg.sv f33383f8b031b3a1
  (WM1), gen_tb_top.sv ef3bc16a9ed47589 (MB13 / MB14), rtl/ibex_if_stage.sv 8b99f212f06aa942 (RM4), rtl/ibex_core.sv
  88b8bf3907472f1d and rtl/ibex_load_store_unit.sv 86e156efaf7ac46a (RM1..RM3, re-run). Checked first-hand.

| mutant | edit (gen_mut_step2b.md) | caught by | referee knobs | ablation |
|---|---|---|---|---|
| MUT-M | scrkey responder keeps valid high through a re-key | sva_scrkey_valid_drops (UVM_ERROR 5) | +gen_chk_all=0 +gen_chk_sva_scrkey=1 | +gen_chk_sva_scrkey=0 PASS |
| MUT-N | bus driver idle err = 1 | sva_ibus_err_with_rvalid (405) | +gen_chk_all=0 +gen_chk_sva_ibus=1 | +gen_chk_sva_ibus=0 PASS |
| RM1 | core_busy_o On bits never rise (rtl copy) | sva_st_core_busy_mubi (545) | +gen_chk_all=0 +gen_chk_sva_st=1 | +gen_chk_sva_st=0 PASS |
| RM2 | rvfi_halt = rvfi_valid (rtl copy) | sva_rvfi_halt_zero (169) | +gen_chk_all=0 +gen_chk_sva_rvfi=1 | +gen_chk_sva_rvfi=0 PASS |
| RM3 | data_tag_o = 1 (rtl copy) | sva_dbus_tag_quiet (545) | +gen_chk_all=0 +gen_chk_sva_dbus=1 | +gen_chk_sva_dbus=0 PASS |
| RM4 | dret resumes at dpc + 4 (rtl copy, ibex_if_stage.sv:247) | dbg_dret (14) `record after dret (order 4): pc 80000104 mode 3, dpc 80000100 dcsr.prv 3` | +gen_chk_all=0 +gen_chk_dbg_dret=1 | +gen_chk_dbg_dret=0 PASS |
| MB13 | crash_dump.exception_pc + 4 in gen_tb_top | crash_dump (2463, first at order 1) | +gen_chk_all=0 +gen_chk_crash_dump=1 | +gen_chk_crash_dump=0 PASS |
| MB14 | DUT fetch_enable_i tied On | fetch_en (79) `68 cycles after fetch_enable_i left On at cycle 202 (drain window 64)` | +gen_chk_all=0 +gen_chk_fetch_en=1 | +gen_chk_fetch_en=0 PASS |
| WM1 | cg.sample(idx) removed | gen_ut_witness cocotb assertion `counts 0 distinct bins, expected 1` (no UVM referee) | every checker on | +gen_fcov_en=0 PASS (bookkeeping path) |

  Assert ids and counts for MUT-M / MUT-N / RM1..RM3 are audit-quoted from the catch logs; the batch and re-run logs,
  the tree shas and the compile-log shas were checked first-hand.
- The symlink incident: the first RM1..RM3 batch (gen_fu_l2b_oot_mutation_batch_tainted.log, 17:35:45-17:37:40Z) shows the
  shared clone's rtl/ibex_core.sv hash changing under an "untouched" label after RM1 (7ef9a680c80c9bbc) and RM2 stacking on
  it; the intervention log records the taint window and the restore (gen_intervention_log.md:1274-1278); the manifest row
  labels the file "TAINTED ... the incident's record, not evidence"; the retained RM1..RM3 triads (17:41:13-17:42:00Z) sit
  inside the clean re-run window (gen_fu_l2b_oot_rtl_mutants_rerun.log 17:40:55-17:42:02Z, start and end tree shas equal
  and equal to the committed rtl blobs). MUT-M / MUT-N (17:36:05-17:36:30Z) ran before the first RM edit with the tree
  still pristine (the batch's MUTN line prints the original three shas). Honest, and cited correctly.
- T-179 chain: red 1 on wit/a (`[GEN_CMD_DISPATCH] command COV_WITNESS has no consumer yet`, gen_fu_l2b_a_ut_witness_*);
  red 2 on wit/b (`counts 2 distinct bins, expected 1`, and the referee `[wit_referee] the covergroup counts 1 distinct
  bins, the dispatcher accepted 0 distinct witnesses` in gen_fu_l2b_b_boot_zc_*); green on e / shared / final
  (`[GEN_WIT] witnesses=3 distinct=2 covergroup=2 foreign=0 out_of_range=0`, GEN_UT_WITNESS_PASS, UVM_ERROR 0); foreign
  fixture refused (`[GEN_WITNESS_FOREIGN] COV_WITNESS TP-BIT-036 (index 0) belongs to gen_bit_multicycle, issued by
  gen_bit_random`, verdict FAIL through the collected error); `+gen_fcov_en=0` PASS on the bookkeeping path; codegen 967
  checks including the repeated-bin and missing-CSV refusals and the mutated-include STALE case; `--check --root <archive>`
  up to date and a re-render of gen_wit_bins.svh equals the committed file (220 bins).
- Other counts in the transcript match the logs: 11 base canaries PASS, 16 e runs PASS, crash_dump 2466/54/0/0
  (dmem_err_dir), 535/0/6 (ebreak_r10), 2000/0/0 (s7 storm), dret checked 37 / 0, fetch_en 61/61 and 201/201.

### 1.2 Derivation of the asserts (sample)

gen_protocol_props.sv: 50 `P_ASSERT`, 20 `P_COVER`, one static width assert; nine group enables default 1, knob
`+gen_chk_sva_<grp>` over `+gen_chk_all` (props:85-97); every property reports through uvm_report_error under its own id.
Every port is a gen_dut_top port; the two integrity flags are TB interface signals reached through gen_tb_top paths
(gen_binds.sv:12-13); no DUT internal is read; gen_binds.sv is the only bind in dv/auto_dv. Filelist entries are
unconditional (gen_tb.f) and the final compile parses them.

| assert | source sentence | judgement |
|---|---|---|
| sva_ibus_req_hold, sva_dbus_req_hold | instruction_fetch.rst:53-54 / load_store_unit.rst:20-21 "must stay high until gnt is high for one cycle" | doc-derived |
| sva_ibus_addr_hold, sva_dbus_fields_hold | load_store_unit.rst:91 (after a grant the address, wdata, we, be may change), :89 (a store configures be and wdata) | doc-derived; the load exemption on wdata follows :89 and is disclosed (props:192, transcript) |
| sva_*_addr_aligned | load_store_unit.rst:23, instruction_fetch.rst:56 "Address, word aligned" | doc-derived |
| sva_*_rvalid_outstanding | load_store_unit.rst:93 "rvalid ... one or more cycles after the grant" | doc-derived (a response only while a grant is outstanding) |
| sva_*_gnt_only_with_req | load_store_unit.rst:89 "answers with gnt ... to serve the request" | doc-derived, TB-side hygiene |
| sva_*_rdata_intg, sva_dbus_store_intg | load_store_unit.rst:61-65 (inverted 39/32 Hsiao code, checked on loads and stores) | doc-derived; the TB flag exempts an intended corruption |
| sva_dbus_outstanding_max = 2, sva_dbus_no_third_request | load_store_unit.rst:74-76 (two word-aligned accesses of a misaligned one); the number from rtl/ibex_load_store_unit.sv:403-405 | RTL-derived bound, disclosed in the parameter comment (props:14) |
| sva_ibus_outstanding_max = 8 | none; NUM_FB x IC_LINE_BEATS (props:13) | RTL-derived bound, disclosed |
| sva_dbus_be_legal (ten patterns) | load_store_unit.rst:28-29 says only "set for the bytes to write/read" | RTL-derived pattern set (rtl/ibex_load_store_unit.sv:138-191), disclosed in the companion table |
| sva_*_err_with_rvalid | load_store_unit.rst:41-42 defines err only during rvalid | TB convention ("hygiene"), disclosed |
| sva_dbus_tag_quiet, sva_alert_internal_never | RTL constants for this configuration | carve-outs, disclosed inline; RM3 / none proven fireable |

Draft comparison: rtl-arch's draft (dv/auto_dv/work/rtl-arch, not committed) has 54 asserts + 20 covers; all 75 built ids
exist in the draft, none extra; the four properties that read core internals are omitted and named in the header
(props:3-5); two draft asserts (sva_dbus_split_second_addr / _be) are built as covers, disclosed inline (props:204-206) and
in the transcript. The protocol's in-order response rule (load_store_unit.rst:95) binds the TB's memory agent, which
serves in order by construction; it cannot be checked from the DUT boundary without a response id, and the layer does not
claim it (I-2).

### 1.3 The covergroup samples a TB-side fact

gen_fcov_pkg.sv:13-16 declares `gen_wit_cycle_clause_cg with function sample(int unsigned idx)`, one coverpoint over the
220 rendered bins (`bins w_tp_<area>_<nnn> = {i}`); the sample site is gen_env_pkg.sv:121
(`GEN_CMD_COV_WITNESS: bvif.peek_data = wit.witness(t.arg[0], t.arg[1])`) and gen_fcov_pkg.sv:65 (`cg.sample(idx)`):
the value sampled is the index the test's own COV_WITNESS command carried; no DUT net enters. Refusals (first-hand):
`idx >= GEN_WITNESS_COUNT` -> uvm_error GEN_CMD_DISPATCH (fcov:55); `GEN_WITNESS_GROUP_OF[idx] != owner` -> uvm_error
GEN_WITNESS_FOREIGN (fcov:60); the report referee compares the covergroup's own distinct count (get_coverage scaled) with
the dispatcher's bookkeeping and raises uvm_error wit_referee on a difference (fcov:73); it fired in the wit/b red. The
covergroup exists only with `+gen_fcov_en=1` (default 1); refusals and bookkeeping stay on without it.

### 1.4 The three rules

- dbg_dret (gen_checkers_pkg.sv:272-279): the record after a dret outside debug must have pc_rdata == the model's dpc and
  mode == dcsr.prv of the dret's published state (gen_rvfi_pkg.sv:63-66, :195-197 add dpc, pc_rdata, mode to the
  published state). Intent: cs_registers.rst (dpc is the resume address; dcsr.prv the resume privilege); RTL anchor
  rtl/ibex_if_stage.sv:247 verified. Intent-derived, mutation-proven (RM4).
- crash_dump (gen_checkers_pkg.sv:374-396): exception_pc / exception_addr against the model's mepc / mtval at every record,
  with LATE (equals the previous record's CSRs) and EARLY (equals the next record's) accepted by name and counted. The
  design documents define crash_dump_o only as "signals that can be captured on reset to aid crash debugging"
  (doc/02_user/integration.rst:319); the field meaning comes from rtl/ibex_core.sv:1329-1330 (verified). An RTL-anchored
  mirror with named tolerances; see L-9.
- fetch_en (gen_checkers_pkg.sv:398-407, :465-470): no record later than GEN_FETCH_EN_DRAIN_CYCLES = 64 after the TB-driven
  fetch_enable_i left On. The documented behaviour exists (integration.rst:323-328: "pause fetching new instructions and
  immediately halt once any in-flight instructions in the ID/EX and WB stages have finished"); the rule cites the RTL
  only and the bound has no stated derivation (L-9). Mutation-proven (MB14 at 68 cycles).

### 1.5 Weakening scan

`git diff f146ceb d752fb3 -- dv/auto_dv/env dv/auto_dv/tb dv/auto_dv/isa`: every removed line is a counter or report line
extended, a struct extended, a comment rewrite, or the literal 5 -> CAUSE_LOAD_ACCESS (same value). No compare removed, no
tolerance widened, no new skip path, no default flipped, no error demoted.

## 2. Findings

### M-3 (medium, undisclosed) [S2 derive from intent; S4 honesty over green] The scoreboard document claims an acceptance condition the code does not have

- Location: dv/auto_dv/docs/gen_component_api_scoreboard.md, the conventions table row "suppressed register write" (line
  132, ADDED by this landing as the CM25-L-5 fix): "accepted only with an announced corruption (`gen_bus_err_log::note_intg`)";
  and line 86 (pre-existing, kept): "NMI-enabled and integrity-error runs are full lock-step compares, no longer
  consistency-only".
- Evidence: gen_rvfi_pkg.sv:464-470 at d752fb3 undoes the model's write and skips the rd compare whenever
  `t.ext_rf_wr_suppress` is set; `gen_bus_err_log::take_intg()` is consulted only for the NMI mtval (gen_rvfi_pkg.sv:352);
  no announced-corruption condition exists on the suppression. The landing's own response file says so:
  gen_critic_response_fu2a.md row CM25-M-2 / CR8-M-1 (T-183) "OWED to 2c ... Until then integrity runs are
  consistency-only, as ruled". The table is introduced as what "the comparator adopts" (doc:126-127), not as intent.
- Why medium: the document of record for the scoreboard states, as built, the very rule whose absence is T-183 and the
  reason LOG-037c ruled integrity runs consistency-only. A reader of the doc believes the T-183 gap is closed. Under the
  T-102 precedent an owed medium needs the mechanism disclosed where the reader looks; a claim of the opposite is the
  case that cannot be owed.
- Required: row 132 states the as-built rule (accepted on the DUT's flag; T-183 owed to 2c with the red and mutant named,
  as the response file already does) and line 86 stops calling integrity-error runs full lock-step compares until T-183
  lands. No code change is requested here.

### M-1 (medium, disclosed; owed with conditions) The witness protocol as built differs from the plan, and the committed template, the flow and the plan are not aligned to it

- As built: COV_WITNESS arg0 = the item's CSV index, arg1 = the issuing test's group index; the SV side accepts any item of
  that group (fcov:52-66); the entry's witness_ids are enforced Python-side by the template (gen_test_template.py:379-381);
  no `+gen_witness_ids` plusarg exists (gen_tb_pkg.sv declares no PLUSARG_WITNESS_IDS). Disclosed in
  gen_component_api_fcov.md Section 7, gen_component_api_bridge.md:34-38, gen_knobs.py:296, gen_bridge.py cov_witness,
  and the transcript ("Protocol note for the template").
- Not aligned: (a) the plan still specifies the plusarg form: gen_test_plan.md:106-107 (rule C-2, "+gen_witness_ids=
  <comma-separated indices>"), :844 (WP-2), gen_fcov_plan.md:6701-6706 (CG-WIT-001 Sample line: "the dispatcher accepts
  only indices of the running test's rendered set"); gen_runtime_api.md carries the same. (b) Runtime's flow dies for any
  testlist entry that lists witness_ids because the TB declares no SV_PLUSARG_WITNESS_IDS (gen_flow_util.py:752-758
  `witness_render`); no committed entry lists witness_ids today, so the path is dormant. (c) The committed template's
  epilogue sends `COV_WITNESS (code, 0, 0, 0)` (gen_test_template.py:387): arg1 = 0 = group gen_bit_multicycle, so every
  other group's first real witness would be refused with GEN_WITNESS_FOREIGN and fail the run. The retained greens do not
  exercise that path: gen_ut_witness calls bridge.cov_witness(item, group) directly (gen_ut_witness.py:30-35), and the
  template fixtures fake the dispatcher ("a fake dispatcher that records COV_WITNESS instead of sending it (no SV side
  exists)", gen_ut_witness_base.py:1-3, :50-54 - a docstring that is now stale).
- Judgement: the as-built guarantee (a test cannot witness an id outside its entry's set) still holds through C-1
  (check_test_source refuses the token outside the template) + the template's own assert + the SV group check; it is a
  different division of labour from the plan's C-2, not a weaker one, provided the three deliverables are aligned. The
  landing disclosed the change to the Test Writer, so the medium is owed, with these conditions: the DV Lead's next plan
  part restates C-2, WP-2 and the CG-WIT-001 Sample line to the as-built protocol (arg1 = group; the entry's set enforced
  by the template and C-1); the Test Writer's template passes WITNESS_GROUPS[its group] as arg1 and its fixtures'
  docstring is corrected; Runtime's witness_render stops requiring the plusarg or the plan reinstates it; until all three
  land no testlist entry lists witness_ids and no witness bin is credited (LOG-046 already keeps them unscored). Owner of
  the record: the Orchestrator's log (a cross-team item); tb-infra's part is done.

### M-2 (medium, owed with conditions) [S6 mutation-proof] Four of the nine SVA groups have no catching mutant

- Caught: st (RM1), ibus (MUT-N), dbus (RM3), scrkey (MUT-M), rvfi (RM2). Not caught: icram (7 asserts, props:225-233),
  irq (sva_irq_pins_known), dbg (sva_dbg_req_known), alert (sva_alert_internal_never, sva_alert_bus_iff_intg,
  sva_alert_minor_window, sva_alerts_known). The transcript says "every group knob's ablation PASS", which is true and
  does not claim a catch per group; the mutation record lists the five. Disclosed by omission, not by statement.
- Owed: one catching mutant per uncaught group in gen_mut_step2b.md, from the private rtl copy where the row is a DUT
  rule (for example alert_major_internal_o tied high for sva_alert_internal_never; alert_major_bus_o tied low under an
  injected corruption for sva_alert_bus_iff_intg; an ic_tag_write without ic_tag_req for the icram rows), with the
  referee knobs inert and the group's ablation. The record should state which groups are proven and which are owed.

### L-1 (low) [S4] `option.weight = 0` is promised and not built

gen_rvfi_export_addendum.md:338 ("`option.weight = 0` is rendered on it as defence in depth") and gen_fcov_plan.md:84,
:274 say the witness covergroup carries option.weight = 0; gen_fcov_pkg.sv:13-16 sets option.per_instance = 0 only. The
mechanism of record is Runtime's exclusion by covergroup name, so the score is unaffected; the claim is still false.
Required: add the line or correct the three sentences.

### L-2 (low) [S6 mutation record] Two inaccurate provenance sentences

gen_tdd_step2b.md:348 "The mutants above were built from wit/e's sources" is wrong for MUT-M, MUT-N, RM1..RM3 (l2b/a
68a36e6ac32db967, 17:35-17:42Z, before wit/e's compile at 17:53Z) and for WM1 (17:48Z; its "source tree untouched" line
c4e742249c7d0fc3 is the sha256 of gen_rvfi_pkg.sv at f146ceb, the pre-landing blob). gen_mut_step2b.md:103-104 states the
split correctly. The "source tree untouched" line of the wit_root batch hashes a file other than the mutated one and is
unlabeled (my fu2a L-4, persisting); the proof sits in the "applied to ... original sha256" lines, which are correct.
Required: fix the sentence; label what the tree line hashes. Also gen_mut_step2b.md says "seed-7" where the headers say
seed=1 with the s7 program (I-1).

### L-3 (low) [S6 evidence over prose] "a `wit_referee` error in every run" (gen_tdd_step2b.md:344-345) is not what the retained wit/b logs show

gen_fu_l2b_b_ut_witness_* has 0 UVM_ERROR lines (the cocotb assertion failed first); the referee fired in the retained
gen_fu_l2b_b_boot_zc_* and, per the driver log only, in lockstep_zc and the foreign fixture. Required: say which runs.

### L-4 (low) [S5] The split rule has no active checker and the two documents point at each other

props:204-206 says "the split rule belongs to the dbus_split checker"; gen_component_api_binds.md:30-31 says chk_dbus_split
"stay[s] rendered without a consumer (their rules are the agents' and the comparator's)"; no split rule exists in
gen_agents_pkg.sv or gen_checkers_pkg.sv (grep). The header's "except" list (props:3-7) does not mention the two asserts
turned covers. Required: name the owner and landing of the second-half address / byte-enable rule, or state that it is
covered only by the lock-step compare; add the two covers to the header's exception list.

### L-5 (low) [S5] ICACHE_ECC_WINDOW is passed and unused; two windows for one rule

props:15 declares ICACHE_ECC_WINDOW = 1 (passed by gen_binds.sv:7) and no property uses it; sva_alert_minor_window
(props:270) hard-codes `$past(icram_lookup_read, 1) || $past(icram_lookup_read, 2)` while GEN_ICACHE_ECC_WINDOW = 1
(gen_tb_pkg.sv:236) bounds the misc checker's rule. Required: use the parameter or drop it and state why the SVA window
is 2.

### L-6 (low) [S5 single source] Knob names rebuilt as string literals

props:90-91 forms `{"gen_chk_sva_", grp, "=%d"}` and "gen_chk_all=%d" while gen_tb_pkg.sv:93-101 declares
PLUSARG_CHK_SVA_* once. Required: read the names from the constants home.

### L-7 (low) [S5] Wrong instance name in the binds document

gen_component_api_binds.md:15 names the bound instance `u_gen_protocol_props`; gen_binds.sv:10 and every catch log say
`gen_protocol_props_i` (paths gen_tb_top.u_dut.gen_protocol_props_i.sva_*).

### L-8 (low) [S4] The fu2a response table carries no row for my lows

gen_critic_response_fu2a.md answers CR8-H-1 and CR8-M-1..M-6 (all statuses verified against the code and logs: the DONE
items are the 1c items I approved in gen_critic_tb_l1c.md; the OWED items name a fix and a red each) but none of my fu2a
L-1..L-12 / I-1..I-2. L-4 persists (L-2 above). Required: one status row per low (DONE / OWED / DECLINED with the reason),
as the fu1 response did.

### L-9 (low) [S2] Anchors for the two misc rules

crash_dump: state that the design documents do not define the fields (integration.rst:319) and that the mirror's meaning
is the RTL's (rtl/ibex_core.sv:1329-1330), so the rule is an RTL-anchored mirror with named tolerances. fetch_en: cite
integration.rst:323-328 as the intent and derive the 64-cycle bound (pipeline drain plus the longest outstanding
response the agent can hold) instead of citing rtl/ibex_core.sv:644-656 alone.

### Informational

- I-1: "gen_ut_boot seed-7" / "seed-7 debug storm" in gen_mut_step2b.md denote the s7 program; every l2b header carries
  seed=1. Name the program, not a seed.
- I-2: the protocol's in-order response rule (load_store_unit.rst:95) constrains the memory side; the TB agent serves
  in order by construction, so no boundary property can or should claim it. Stated for the record.
- I-3: PASS verdict templates are byte-identical across runs (five groups of 7-17 members) and carry no run identity;
  pre-existing convention, the identity lives in the headers.
- I-4: the fu2a response's DONE rows for 1c are consistent with gen_critic_tb_l1c.md; its OWED rows (t.intr local flag,
  T-183 announced-corruption condition, CR8-M-5 end-of-run never-taken rule, L-7 debug-mode suspension, T-189 decidability
  statement, L-4 shim literals, L-6 NMI classification from the nmi_either window) each name the fix and a red; the list
  is honest as a list. M-3 is the one place where a document contradicts it.

## 3. Answers to the Orchestrator's questions

1. Intent derivation of the asserts: the handshake, stability, alignment, response and integrity rows derive from
   load_store_unit.rst:89-95 / :61-65 and instruction_fetch.rst:53-64, :86-87; the numeric bounds (8, 2), the byte-enable
   pattern set and the two never-fire rows are RTL-derived and say so in comments or the companion table. No assert reads
   a DUT internal; none is disabled by default; none is a tautology. Acceptable, with the four uncaught groups owed (M-2).
2. The covergroup samples the test's own COV_WITNESS index, a TB-side fact; the refusals and the referee are collected
   uvm_errors and each is proven to fire in a retained run (Section 1.3).
3. The as-built arg1 = group deviation is disclosed in tb-infra's component documents, the bridge, gen_knobs.py and the
   transcript; it is not reflected in the plan, the flow or the committed template, and the template as committed would
   be refused for every group but index 0 (M-1, owed with the three named conditions).
4. Mutation evidence: nine mutants, each caught by the named row with the referees inert and an ablation PASS, build
   shas equal to compile logs, mutated files' originals equal to the committed blobs; RM1..RM3 cited from the clean re-run
   with the tainted batch labelled as an incident record (Section 1.1). Two provenance sentences are wrong (L-2).
5. The 2c owed list is honest as a list (I-4). The scoreboard document contradicts it on T-183 (M-3), which is why the
   verdict is REQUEST-CHANGES rather than APPROVE with owed mediums.

## 4. Holds and principles

- T-183 (rf_wr_suppress on the DUT flag) stays owed; LOG-037c (integrity runs consistency-only) stands; the T-137 lift of
  LOG-051 is unaffected (bus-error arming only).
- LOG-046 (witness bins unscored; no SV covergroups before 2b) is now partly overtaken: CG-WIT-001 exists in SystemVerilog
  and is red-green-mutation proven; crediting still waits on M-1's alignment.
- dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S1 no stimulus change; S2 M-3 (doc claims an intent rule
  the code lacks), L-9 (anchors); S4 M-3, L-1, L-3; S5 L-4..L-7; S6 M-2 (four groups without a catch), L-2 (record accuracy).
  One-line verdict: FAIL on M-3 until the two sentences are corrected; the code conforms.

## 5. Required changes for re-review

1. M-3: gen_component_api_scoreboard.md row 132 and line 86 corrected to the as-built rule and the T-183 owed status.
2. M-1 conditions recorded in the Orchestrator's log with owners (DV Lead plan text; Test Writer template arg1 and fixture
   docstring; Runtime witness_render); no entry lists witness_ids until then.
3. M-2: the mutation record states the five proven and four owed SVA groups, with the owed mutants named for 2c.
4. Lows L-1..L-9 may close in 2c; L-1 and L-2 are one-line edits and should close with M-3.
A docs-only touch that closes M-3 (and records M-1 / M-2 as above) lifts this REQUEST-CHANGES; I will re-review it as a
delta on the same file.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-f146ceba-d752fb36.md, read after Sections 1-5 were written)

The artifact's verdict is APPROVE-WITH-CHANGES (one medium, seven lows; rubric magic-numbers FAIL). Mine is
REQUEST-CHANGES on M-3, which the artifact does not carry; the two verdicts agree on everything both examined.

Its findings against mine:

- Its medium (sva_alert_minor_window hand-codes a two-cycle window while ICACHE_ECC_WINDOW is passed and unused) is my
  L-5. I keep it low: the misc checker holds the tighter documented window (<= GEN_ICACHE_ECC_WINDOW), so the looser SVA
  window cannot produce a false green; the defect is single-source (S5). Its fix (express the window through the
  parameter, or raise the constant with the reason) is the same as mine.
- Its low on plusarg names re-typed as literals is my L-6; adopted addition: the rendered cfg.chk_sva_* mirror has no
  consumer, so two parsers own one knob (the literal names verified first-hand; the unconsumed cfg mirror is the
  artifact's observation, not re-verified here).
- Adopted, verified: sva_icram_widths pins 28 / 78 as literals (props:235-237) and the parameter defaults repeat them
  (props:17-18); derive them from ibex_pkg as gen_dut_top does (L-10).
- Adopted, verified: dcsr_q[1:0] hand-slices dcsr.prv with no named authority (gen_checkers_pkg.sv:276); name the field
  once (L-11).
- Adopted, verified: wit_referee has no mutation evidence of its own (WM1 ended in the cocotb assertion before
  report_phase; the referee's firing is shown only in the wit/b red, Section 1.3); a referee-targeted mutant with the
  Python assert inert is owed (L-12; add it to the M-2 list of owed mutants).
- Adopted, verified: RM1..RM3 share build 68a36e6ac32db967 because the rtl copy is outside the sources hash; record the
  mutated rtl file's sha per RM row (the re-run log prints the originals) (L-13; complements my L-2).
- Adopted in part: the props header cites dv/auto_dv/work/rtl-arch paths that are not tracked at this commit (verified:
  the draft is gitignored) and "(landing 2b)" at props:206 narrates history; keep the deviation list, drop the untracked
  provenance and the landing tag (L-14).
- Adopted, verified: two modules share the basename gen_ut_witness_foreign.py (dv/auto_dv/gen_tb/gen_tests/ and
  dv/auto_dv/tests/gen_fixtures/) and the retained-log names do not say which; rename one or state the module path in the
  manifest rows (L-15).

Mine that the artifact does not carry: M-3 (the scoreboard document's as-built claim of an announced-corruption condition
the code lacks), M-1 (the plan / flow / template not aligned to arg1 = group; the committed template sends arg1 = 0),
M-2 (four SVA groups without a catching mutant), L-1 (option.weight = 0 promised, not built), L-2, L-3, L-4, L-7, L-8, L-9.
The artifact's evidence statements (229 rows, nine mutants with FAIL catch and PASS ablation, the tainted batch disclosed
and only the re-run cited, codegen up to date) agree with Section 1.1.

Adopted items are marked adopted and verified where I re-derived them from the blobs; L-14's unconsumed-cfg point is
carried as the artifact's.
