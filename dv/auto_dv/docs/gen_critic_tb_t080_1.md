# Critic verdict: T-080 landing 1, the record part of the RVFI record and event export (commit 1f8186e, tb-infra)

Artifacts at commit 1f8186e (sha256 first 16 hex, lines):
- dv/auto_dv/env/gen_export_pkg.sv                    ef824d0d147fe971  120
- dv/auto_dv/env/gen_export_record_line.svh           71f09b3a611f8ae5    9 (rendered)
- dv/auto_dv/env/gen_export_event_lines.svh           d0c1e544a18759fc   32 (rendered)
- dv/auto_dv/gen_tb/gen_export.py                     c5a95e431db854f7  108
- dv/auto_dv/gen_tb/gen_tests/gen_ut_export.py        59c997fab839b97a  100
- dv/auto_dv/gen_tb/gen_bridge.py                     fc82ba2bf06723d5   97 (export_flush added)
- dv/auto_dv/tb/gen_tb_knobs.yaml                     740c1efaa32c2f62  216;  gen_knobs_codegen.py  bc5ea29a524d0fee  601
- dv/auto_dv/docs/gen_component_api_export_sink.md    491affe9c7274f9a  284
- dv/auto_dv/evidence/gen_tdd_export.md               55fd2622eae6097f  102
- dv/auto_dv/mutations/gen_mut_export.md              10d42e2fead853b8   69 (MUT-A..MUT-F)
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md    741d27e72b7a3b4b  337 (40 export rows, 72 gen_mut_export rows)
Also read: dv/auto_dv/docs/gen_intervention_log.md LOG-017 (commit a555d2d); the diffs of gen_rvfi_pkg.sv and gen_env_pkg.sv
in this commit. Date: 2026-09-03T10:54Z   Role: Critic.

CRITIC VERDICT: APPROVE (record part of the export; event lines and MUT-G / MUT-H are the next landing, as the transcript says)

## 1. The five questions asked

1. Mutations real and caught with hidden referees inert: YES. MUT-A..MUT-F are source edits of the SV producer (record
   field, dropped record, swapped records, suppressed marker, moved first pc, stale marker), each built into its own
   out-tree directory (compile log retained per mutation, vcs exit 0), run with +gen_chk_all=0 (the flag is on every one
   of the 12 run headers; every caught sim.log carries "ISA compare disabled by knob", so the comparator cannot be the
   catcher). Caught lines in the retained stdout logs equal the record's: 153 pc discontinuities (A), marker records 174
   != retired 175 (B), order 51 after 49 (C), no complete flush marker with seq=2 (D and F), first record pc 0x80000084
   != 0x80000080 (E). Every ablation run (named Python rule disabled) is GEN_UT_EXPORT_PASS with verdict PASS; for B, C
   and F the record lists the second and third catchers found on the way and the all-disabled survival. Reverts: each
   driver log carries "reverted: ok" per mutation and "final: sources identical to pre-mutation"; the mutation texts and
   ablation edits are retained per mutation. All 72 gen_mut_export_* files match the manifest md5.
2. Retained logs match the transcript: YES. All 40 export rows match md5 and byte count; every committed file under
   export/ is in the manifest and carries the gen_ prefix. Identifying lines found verbatim: red 1 (ImportError cannot
   import name 'gen_export', verdict FAIL cocotb_critical at stdout.log:12), red 2 (UVM_FATAL GEN_UNKNOWN_PLUSARG
   +gen_export_file, verdict FAIL uvm_fatal at sim.log:19), the three twoflush greens (records 175 / 175 / 2008 equal to
   retired, early flush seq 1 with 0 records, GEN_UT_EXPORT_PASS, verdict PASS), the counters run's R lines with 55 tokens
   (1 + 34 + 20), gen_compile_t080.log with vcs exit 0 and 0 Error lines, the two retained compile defects, the codegen log
   with 763 OK and PASS.
3. UNRETAINED labels honest, re-run set retained: YES. Section 4 labels the three test-defect attempts and the three
   single-flush greens as lost to the FORCE recompile, quotes them as driver output, and states the rule adopted (a build
   directory holding retained runs is never recompiled in place). The re-run set on the final build (three twoflush
   runs, lockstep_zc / lockstep_zc_export / lockstep_s7 / lockstep_s7_export, ut_bridge_green, boot_zc) is retained with
   sim.log, stdout.log, verdict.txt and run headers; gen_runs_summary_t080.txt lists them.
4. The two RVFI facts are observations, not expectations: YES. (a) Trap record pc_wdata = pc + 4: verified in the
   retained seed-7 export (order 0x1d2: pc_rdata 80002164, pc_wdata 80002168, insn 73, trap 1; the next record's
   pc_rdata is the handler 80001700). The test's continuity rule EXCLUDES trap records (gen_ut_export.py:49), asserting
   nothing about a trap's pc_wdata; the API document states the fact with the ruling reference. (b) The tohost record
   retires after the memory model sees the bus store: handled by a 40-cycle settle before the second flush and by
   read() binding to the flush sequence (trailing bytes excluded); in the retained twoflush files no R line follows the
   seq=2 marker. Neither fact is encoded as an expected value anywhere in the sink, the reader or the test.
5. Does any change in this commit move the first RVFI record: NO. The gen_rvfi_pkg.sv diff adds the sink hand-off after
   sample(), the counter fields under the knob, and turns the interrupt marker from a level into a rising-edge event (I
   lines, not R records); gen_env_pkg.sv adds the EXPORT_FLUSH route and the sink instance; nothing touches sampling
   timing or the model start. On the final build the canary gen_boot_zc_t080 and both lock-step runs PASS with the model
   at pc 80000080, records 148, mismatches 0, folded 21 (the T-068 numbers); the first retained R line is order 1,
   pc_rdata 80000080 (boot page + 0x80, rtl/ibex_if_stage.sv:243). The red window LOG-017 records at 10:39 UTC (model
   80000080 vs DUT 80000084 at the first retirement) is exactly MUT-E's symptom (first record pc + 4), and the driver
   log shows MUT-E applied IN PLACE to the shared dv/auto_dv/env/gen_rvfi_pkg.sv at 10:39:17Z and reverted before MUT-F
   at 10:39:41Z: Runtime's re-proof compiled the shared tree inside that window. Root cause of the red window: a live
   mutation in the shared source, not a committed change (finding L-1).

## 2. Principle walk (docs/dv/dv_principles.md)

S2 fail-through-a-collected-mechanism: sink failures are uvm_fatal (missing cfg or vif, unknown source, EXPORT_FLUSH
without a file, cannot open) or uvm_error (write error after flush or at end); reader and test failures are Python
asserts; all collected by the flow (verdicts retained). S5 single source: the R-line field order, counter fields and
event table are rendered from gen_tb_knobs.yaml into both the SV writers and gen_knobs.py; the reader checks the header
against the rendered list; no hierarchical path in the sink (virtual interfaces from the config db). S4 honesty: the
UNRETAINED labels, the two RVFI facts, the "events=0 in this landing" statement and Section 8's list of what is not
built. S6 triad: red 1 and red 2 before green, six mutations with ablations, no covergroup (none owed: the export is
observation only and the API document says so). Conformance PASS apart from the lows below.

## 3. Lows (none blocking)

- L-1 (process, root cause of LOG-017): the mutation runner edits the shared TB source in place and compiles it into an
  out-tree build; a concurrent compile of the shared tree by another role sees the mutant. The standing rules after
  LOG-017 (Runtime builds served runs from committed HEAD, canary before a batch, announce before and after) remove the
  exposure for served runs; the robust fix is to build each mutant from an out-of-tree copy of the TB source, as the
  flow already does for RTL mutations (--rtl-root), so no live mutant ever exists in dv/auto_dv/. Record the root cause
  in LOG-017 and the rule in dv/auto_dv/mutations/README.md.
- L-2 [S5] gen_ut_export.py:21-22: SETTLE_CYCLES = 40 (derive from the rendered rvalid regime window maximum plus a
  named margin) and FIRST_FETCH_OFFSET = 0x80 (an RTL constant re-typed with a citation; a rendered constant or a
  gen_knobs memory-map field would remove the literal).
- L-3 The trap pc_wdata fact is already the plan's convention C-1 (rtl-arch X-1, gen_test_plan.md Section 4.3 and 4.6
  headers); the transcript and the API document call it an open ruling (F-RVFI-010). Cite C-1 so the two documents agree
  on what is settled.
- L-4 MUT-G (dropped event) and MUT-H (wrong event cycle) are owed with the event lines, as the record says; the event
  header rows and the E-line writers are rendered but no writer registers yet (sources= empty). The next landing's
  verdict starts there.
