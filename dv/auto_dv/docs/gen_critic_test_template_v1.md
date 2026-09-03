# Critic verdict: test template and its proof (commit 746af6f)

Artifacts at commit 746af6f (sha256 first 16 hex, lines):
- dv/auto_dv/tests/gen_test_template.py        f99d1383a0f745da  273
- dv/auto_dv/tests/gen_test_lib.py             e1d702f8bff930f0  295
- dv/auto_dv/tests/gen_fcov_manifest.py        a164dc45afc15c45  275
- dv/auto_dv/tests/gen_test_boot_retire.py     5b0ee29a930a1f22   40
- dv/auto_dv/tests/gen_programs/gen_boot_retire_red.S  e0a2b61a8d0a7f69  26
- dv/auto_dv/docs/gen_test_template_api.md     fe4a80dd644b3b8d  145
- dv/auto_dv/docs/gen_test_writer_plan.md      bc7ed1f52e888284  192
- dv/auto_dv/evidence/gen_tdd_test_template.md f1288a2f4f84670f  160
- dv/auto_dv/flow/gen_testlist.yaml (two entries added by the commit)
Date: 2026-09-03T09:38Z   Role: Critic   Check: dv-principles conformance (docs/dv/dv_principles.md read fresh) plus the
four-point artifact audit of the TDD transcript. The cross-model artifact for this commit was not read before this
verdict was written.

CRITIC VERDICT: REQUEST-CHANGES

The template's failure path is real and proven (section 3), the red fixture is a legitimate red for both
program-level checks, and the transcript's runs all exist and match. Five medium findings stand: the template's
own schedule check cannot fail, a test that records no check passes, the layer gating is a hand-typed fact whose
lag would pass silently, the manifest generator depends on files that are not committed, and the bridge
encodings are re-typed under a false safety claim.

## 1. Findings

### M-1 (medium): fire_schedule_applied is vacuous

- [S6 self-proving checks; S2 derive from intent] gen_test_template.py:239-250. `reached` is the list of phases
  with `applied_cycle` set, and `applied_cycle` is set only by apply_phase (:182), which also appends the phase to
  `self.applied` (:183). `len(reached) == len(self.applied)` is therefore true by construction; `>= 1` is true
  whenever phases exist, because the phase-0 entries are applied in setup (:177-178). The check has never had a
  way to be False with a non-empty schedule. gen_tdd_test_template.md:151 ("rejects a reached-but-unapplied one")
  is false by construction, and every logged `fire_schedule_applied ok=True` (evidence lines 41, 78) proves nothing.
- Required: derive "reached" from the trigger, independent of application: capture cycle() and retired() at
  the end-of-test edge in wait_eot and count the phases whose (kind, count) lies at or below them; compare with
  the applied list; add a red run in which a reached phase is deliberately not applied (a fixture that suppresses
  apply_phase) so the check is seen failing once. When the SV-side phase count becomes readable (plan section 6
  item 2), compare both sides.

### M-2 (medium): a test that records no fire-check result passes

- [S2 fail through a collected mechanism; S4 don't hide failures] gen_test_template.py:252-259 raises only when
  `self.failures` is non-empty. A subclass whose fire_check() body records nothing (an empty override, or checks
  guarded by a condition that never holds) logs GEN_TEST_PASS. With an empty `schedulable` set (HEAD today)
  schedule_check records nothing either (:243-246), so such a test has zero recorded checks and passes. The plan
  (gen_test_writer_plan.md section 1, "one fire-check per item") is a convention the template does not enforce.
- Required: count check() calls and fail in finish() when the count is zero ("GEN_TEST_FAIL <name>: fire_check()
  recorded no result"); once the group-to-items mapping exists, require one result per item of the group.

### M-3 (medium): the layer gating is a re-typed fact, and its lag passes silently

- [S5 single source of truth; S4 don't hide failures / silently down-scope] gen_test_lib.py:25-33: the set of
  knobs the SV dispatcher consumes is two hand-maintained tuples, both empty at 746af6f. If they lag the build
  (step 2b lands, tuples not edited), every test runs with layers 2 and 3 off, logs `GEN_TEST_LAYERS not_applied`
  and PASSES; no verdict consumes that line. DV_prompt Section 6 makes the three layers part of every test, so a
  measured regression could run with them off and stay green. Today this is honest only because every entry is
  `measured: false` and the transcript says so (sections 3b, 4, 5); the mechanism, not the prose, has to carry it.
  The API document contradicts itself: gen_test_template_api.md:60 says the default `schedulable` is the
  imem/dmem/irq/debug_req/scr_key set "with a REGIME_SET consumer today", section 8 (:133-139) and the code say
  the set is empty.
- Required: (a) the consumed set comes from the TB's single source (an attribute per knob rendered into
  gen_knobs.py by gen_knobs_codegen.py from gen_tb_knobs.yaml, or a value the SV side reports through the bridge
  or a plusarg); until then a host-side unit check that the tuples equal the dispatcher's case labels in
  dv/auto_dv/env/gen_env_pkg.sv, failing loud on drift; (b) `not_applied` is a failure for a measured run: the
  template asserts `not self.varied or self.schedule.phases` when the entry is measured (or the flow treats the
  line as a bad verdict for `measured: true`); (c) API section 3 row corrected.

### M-4 (medium): the manifest generator and its recorded self-test depend on uncommitted files

- [S5 self-sufficient code; S6 evidence over inference] gen_fcov_manifest.py:87-99 loads `segmentable` from
  dv/auto_dv/tools/gen_trace_check.py by AST. That function exists in no committed revision (0 hits at 746af6f
  and at HEAD 0475b94); it exists only in the DV Lead's modified working copy (a nested def at line 58, file
  mtime 08:07Z, still uncommitted). Rule (e) (:122-127) looks for a `# 1.1` section and the self-test (:248-250)
  asserts CG-MUL-002.cp_dmem_delay is regression-level; `# 1.1` and "regression-level" occur 0 times in the
  committed gen_fcov_plan.md (746af6f and HEAD) and only in the working copy (1 and 4). From a clean archive of
  746af6f the library self-test passes (output identical to evidence section 1) and the manifest self-test fails:
  `expected one segmentable(); found 0`. On today's working tree it prints "67 bins for gen_reg_schedule, 0
  dropped; 86 excluded coverpoints"; the committed plan (gen_test_writer_plan.md:65-67) records "122 excluded
  coverpoints", a number that reproduces nowhere I can run it.
- Manifest rule vs gen_fcov_plan.md section 0 (identical at 746af6f and HEAD): rules (a) informational items,
  (b) `- Manifest: not in manifest` items, (c) probe-gated coverpoints, (d) witness bins match the plan's
  sentence. Rule (e) is not in the plan's section 0 at this commit. The plan says the generator "expands" the isa
  auto-cross bins the way the ignore clauses do; the generator expands nothing, it validates that CSV-listed bins
  segment into declared words (fine if the CSV enumerates them, but the plan sentence and the docstring should
  say what the code does).
- Required: land the generator after (or with) the DV Lead's gen_trace_check.py and plan changes it needs;
  import the rule by a named module-level function rather than mining a nested def (a rename then fails at
  import); re-record the self-test output from the committed tree with the commit hash; align the section-0
  sentence and the docstring with the implemented rule set, rule (e) included.

### M-5 (medium): bridge encodings re-typed under a false safety claim

- [S5 single source; S1 future-proof every count] gen_test_lib.py:39-47 mirrors IRQ_LINE_BIT, IRQ_FAST_BIT0,
  IRQ_HOLD, DBG_HOLD, MEM_ERR_BUS, MEM_ERR_KIND as literals and says "a drift shows up as a collected
  GEN_CMD_DISPATCH error, never silently". False for in-range drift: a swapped hold-policy or kind code is a
  valid code, the dispatcher accepts it and the scenario is silently wrong. irq_mask (:208) re-types 15 while
  gen_knobs.CONSTANTS carries GEN_IRQ_FAST_W = 15.
- Required: derive the fast-interrupt bound from CONSTANTS now; for the codes, until gen_knobs_codegen.py renders
  them (asked of TB Infra), a host unit check that parses the SV enum or case labels and compares, so the
  "never silently" sentence becomes true; drop the sentence otherwise.

### Lows

- L-1 [S2 know your failure path and prove it once] The transcript proves the main-coroutine assert path only.
  An exception inside the forked stimulus() or run_schedule() (the timeout AssertionErrors of :116, :195-197)
  is a different path. cocotb 1.9.2 (ci/requirements-cocotb.txt) aborts the test when a background task fails
  (scheduler.py:1009 `_abort_test`, "This happens when a background task fails"), so the semantics hold; one
  red run where stimulus() raises, with the flow's FAIL verdict, closes it.
- L-2 [S5 single source] gen_test_boot_retire.py:20 `EOT_PASS_CODE = 1` re-types the tohost convention that
  gen_program.py and dv/auto_dv/stim/gen_directed/gen_zc_directed.S:146 define; define it once (gen_test_lib or a
  rendered constant) and import it.
- L-3 [S2 derive from intent] The retirement floor for a riscv-dv program is `+instr_cnt` (generated instruction
  count). Programs branch, so instr_cnt is a heuristic bound, not a spec-derived expectation; observed margins
  are wide (550/533/516 and 474-496 retired against 300). State the assumption in the docstring, and derive the
  expected count from the ISS side when a bridge field for it exists.
- L-4 Transcript labelling: sections 2-3b cite sim.log md5 and mtime (all six verified exact, section 3 below)
  but the quoted GEN_TEST lines live in stdout.log; sim.log carries none. Say which file each quote comes from.
- L-5 (Runtime, relayed) result.yaml of test-writer-005 says "sv_fatal at log line 100". No retained log of that
  run has 100 lines (sim.log 38, sim_stdout.log 77, run.log 8); the AssertionError is sim_stdout.log:62. The
  reason should name the file and the class should not call a Python assert "sv_fatal".
- L-6 [S2] wait_cycles / wait_retired / wait_event return False when the program ends first (:107-120). A test
  that ignores the return continues silently; the API should state that "did it fire" is asserted in fire_check
  from an observable, never inferred from a wait returning.

## 2. Judged as requested

- Fire-check collection: check() records and logs every result (:219-223); finish() raises one AssertionError
  with every failure before the finish handshake (:255-257); GEN_TEST_PASS is logged only after the handshake
  (:259); the testlist entries require the marker. Conforms, subject to M-1 and M-2.
- Silent-pass possibilities: M-2 (zero recorded checks), M-3 (layers off in a measured run), L-6 (ignored
  wait return). No other path found: wait_eot fails on no end-of-test store (:208-214), read-back mismatches
  fail (:151-160), a stimulus() that does not return fails (:266-269).
- Red fixture as a real intent mutation: gen_boot_retire_red.S violates both expectations independently
  (tohost 3 at :12-14; declared floor 1000 at :26 against 9 retirements) and each half of the fire-check named
  its own failure in the same run (evidence lines 42-43). For program-level checks this is the right red; the
  template's own check (schedule) has no red, see M-1. Mutation-proof is not owed here: no DUT checker is
  introduced (trust triad rule 2 applies to checkers; the always-on TB checks are named in the docstring, :11).
- Seed-driven layers and the SCHEDULABLE_KNOBS gating: layers 2 and 3 are deterministic per seed and differ
  between seeds (library self-test, re-run from the commit archive: PASS, output identical to evidence section
  1; string seeding of random.Random hashes with sha512); pinned knobs are excluded from the draw and refused in
  a supplied schedule (:79-80, :168-169). The gating itself is M-3.
- Hierarchical-path string in gen_test_boot_retire.py vs the Section 8 probe rule: there is none. grep for
  `u_dut`, `gen_tb_top.` and dotted instance paths in both test files finds only the docstring's
  `TOPLEVEL=gen_tb_top` (cocotb toplevel name, :13). Every observation goes through GenHandles bridge fields
  (`self.h.b.<field>`); the one place that spells the path is gen_handles.py:34-36, and each of the 13 fields the
  template dereferences exists in dv/auto_dv/tb/gen_bridge_if.sv. Bridge fields are TB-side (evt_retired_count
  from RVFI, the end-of-test store from the memory model), so the probe register is not engaged.
- Manifest exclusions vs fcov plan Section 0: rules (a)-(d) match; rule (e) and the segmentation rule depend on
  uncommitted text (M-4).

## 3. Evidence audit (four-point rule) of gen_tdd_test_template.md

| Claimed run | Retained artifact | md5 / mtime as claimed | Identifying line found |
|---|---|---|---|
| out_tpl/red_s1 | work/test-writer/out_tpl/red_s1/{sim,stdout}.log | acb6b75d.. 04:29:42.05 exact | EOT code 3 retired 9 cycle 137; AssertionError GEN_TEST_FAIL 2 failures; TESTS=1 PASS=0 FAIL=1 |
| out_tpl/green_s1 | .../green_s1 | 9fc5222b.. 04:29:15.15 exact | k=1; EOT code 1 retired 550 cycle 4240; GEN_TEST_PASS |
| out_tpl/green_s2 | .../green_s2 | 9e3c9afe.. 04:30:14.65 exact | k=3; EOT code 1 retired 533 cycle 4728; GEN_TEST_PASS |
| out_tpl/green_s3 | .../green_s3 | 59ba6e8a.. 04:30:17.38 exact | k=3; EOT code 1 retired 516 cycle 6787; GEN_TEST_PASS |
| out_head/green_s1 | .../out_head/green_s1 | 3711d8ca.. 04:40:45.58 exact | k=0 not_applied; EOT code 1 retired 550 cycle 1924; GEN_TEST_PASS |
| out_head/red_s1 | .../out_head/red_s1 | c35c9089.. 04:40:49.99 exact | k=0 not_applied; EOT code 3 retired 9 cycle 55; AssertionError |
| Runtime -005 red | regress_req_test-writer-005/runs/gen_test_boot_retire_red_1 | manifest status done | verdict FAIL; AssertionError GEN_TEST_FAIL; EOT code 3 retired 9 cycle 57 |
| Runtime -006 green x3 | regress_req_test-writer-006/runs/gen_test_boot_retire_{870932068,995813351,1486148200} | manifest status done | verdict PASS x3; retired 474 / 496 / 487, cycles 1817 / 1961 / 2039, not_applied |

Also present: compile.log 04:21:51 and vcs_simv 04:21:50 (out_tpl), vcs_simv 04:40:12 (out_head), prog_s1..3
and prog_red, runs_summary.txt (`red_s1 ... cocotb_pass=0 cocotb_fail=1`), manifests test-writer-003..006. The
three -006 seeds differ in every count (no duplicated content). The local host clock is UTC-4 as stated. The
only inaccuracy is L-4. The red run FAILS in the flow, so the failure mechanism is one the flow collects.

## 4. Trust triad status for gen_test_boot_retire

TDD: met (red then green, retained). Mutation-proof: not applicable (no DUT checker introduced); the template's
schedule check needs its own red (M-1). fcov-expectation: declare_bins() returns [] and both entries carry
`fcov_expectation_file: null`; honest before any covergroup exists, re-acceptance on 3 seeds owed when
gen_fcov_pkg lands (plan section 2), and the manifest generator must first be runnable from the committed tree
(M-4).

## 5. HEAD drift (not judged here)

Commit 98c2ade (09:31Z, inside HEAD 0475b94) changes the four test files (80 insertions, 40 deletions) and its
message says fire_schedule_applied now computes reached phases from the bridge counts at the end-of-test store
with a red fixture, and adds a zero-fire-check guard. Those statements touch M-1 and M-2; they are unverified
here. This verdict is on 746af6f as requested; a v2 at the current commit follows on signal, with the response
file at its committed path dv/auto_dv/evidence/gen_critic_response_test_template.md.
