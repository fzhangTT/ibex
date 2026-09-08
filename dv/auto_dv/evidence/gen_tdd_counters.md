# TDD transcript: the counter model, ctr_hpm_exact and ctr_hpm_bound (bug candidates B11, B17, B20, B7)

Component: `dv/auto_dv/env/gen_counter_model.sv` (new, package `gen_counter_pkg`), wired into `gen_env` as
`env.ctr` on two ports and added to `dv/auto_dv/tb/gen_tb.f`; six instruction classifiers in
`dv/auto_dv/tb/gen_tb_pkg.sv`; four direction knobs, two unit-test knobs and two latency constants in
`dv/auto_dv/tb/gen_tb_knobs.yaml` with the files the renderer produces from it; the unit test
`dv/auto_dv/gen_tb/gen_tests/gen_ut_counters.py`; the API document
`dv/auto_dv/docs/gen_component_api_counter_model.md` rewritten to the as-built classes. Owner: tb-infra.
Written 2026-09-08T03:01:39Z.

Authority for every event rule: rtl-arch's `dv/auto_dv/evidence/gen_hpm_event_defs.md` Section 2, cited by
event row. Authority for the knob directions: the counter-rule direction ruling in
`dv/auto_dv/docs/gen_bug_log.md` Section 0.6. Build: local `gen_tb_local.sh compile`, sources sha256
first-16 `62bec5dd95834e7f`, vcs exit 0, out tree `dv/auto_dv/out_l65` (a fresh directory, the knob set
having changed). Stimulus: test-writer's three directed programs, named with their source md5 and image
crc32 in the retained census. Every verdict below is `dv/auto_dv/flow/gen_verdict.py`'s own `decide`.

## 1. What is built, and the one design decision the rest follows from

`ctr_hpm_exact` predicts mhpmcounter7 (NumJumps), 8 (NumBranches) and 9 (NumBranchesTaken).
`ctr_hpm_bound` bounds every counter by the window's cycles and bounds 11 (NumCyclesMulWait) and 12
(NumCyclesDivWait) by the documented wait cycles. Both judge the window between two ARCHITECTURAL READS of
the counter, and that is the decision the rest follows from.

A per-record rule is not soundly buildable. The event pulses of counters 7, 8 and 9 fire in the
instruction's own ID cycles (`rtl/ibex_id_stage.sv:928`, `:934`, `:941` into
`rtl/ibex_controller.sv:681-687`) while `rvfi_ext_mhpmcounters` is sampled at the record's ID exit
(`rtl/ibex_core.sv:2108-2128`), so an instruction that holds ID for one cycle does not see its own pulse
and one that holds it longer does, and the cases that differ are exactly the ones the bug candidates live
in. Both endpoints of a read window are taken at the same point of the pipeline, so that asymmetry cancels.
Section 8 shows the waveform where it is visible.

The cost is stated rather than hidden: THE CHECKER IS SILENT IN A TEST THAT NEVER READS A COUNTER, and a
program that reads a counter once cannot be judged. The API document's Section 9 carries that as a named
gap.

## 2. The four direction knobs, one sense

Per the Section 0.6 ruling, 1 follows the RTL and 0 follows the documentation on all four, the default is 1
so an ordinary run stays green, each accommodation is counted per bug, and the counts are reported at the
end of every run. An accommodation counts only where the RTL's own count ACTUALLY differed from the
documentation, so a nonzero count says the run met the candidate and a zero count says it did not.

| Knob | Bug | 1 (default) | 0 |
|---|---|---|---|
| `+gen_ctr_rtl_jumps_fencei` | B20 | fence.i counts as a jump | jal and jalr only |
| `+gen_ctr_rtl_taken_dit` | B11 | every branch counts as taken while data_ind_timing is set | taken branches only |
| `+gen_ctr_rtl_branches_wait` | B17 | counter 8 is bounded over a window that held a data access | exact everywhere |
| `+gen_ctr_rtl_wait_cycles` | B17, B7 | counters 11 and 12 keep only the one-per-cycle bound | the documented wait bound |

## 3. Which windows are left unjudged, and one deviation from the ruling stated as one

The DV Lead's ruling on the cut, item 3, requires that a window holding an inhibit of the counter, a write to
it or its high half, or an interrupt, NMI or debug entry be left UNJUDGED and COUNTED, never dropped. All
three are implemented with a count each in the report line. The debug entry is derived the way the scoreboard
derives it (`gen_rvfi_pkg.sv:331-332`), so the two components agree on what an entry is.

THE ENTRY ROW IS PROVED, not asserted, on the DV Lead's ruling that a zero count on stimulus that never
takes an entry is a zero without its precondition. `gen_ut_counters` gained one plusarg,
`+gen_ut_ctr_nmi_after`, which pulses one NMI after a chosen number of retirements; an NMI needs no interrupt
enable and the programs' vector tables answer it with an mret, so no program changed. Timed at 20
retirements on the B11 program it lands the entry inside the first counter read window. The pair, same
program and same seed, differing only in the pulse:

| run | exact windows judged | unjudged(entry) | collected errors |
|---|---|---|---|
| b11_default, no pulse | 3 | 0 | 0 |
| b11_nmi, one NMI at 20 retirements | 2 | 1 | 0 |

The window that held the entry moved from judged to withdrawn, which is what the row is for, and the run is
otherwise clean, so the row does its work without inventing a failure. The other six runs keep their zero as
the control.

`judged_bound_incomplete`, the DV Lead's other condition, reads 0 in all seven runs: no bound judgement on
this stimulus was made before a data access inside its window had completed. That count exists because the
data-bus port publishes a transaction only when it completes, so an access in flight at a closing read is
invisible at that moment; the component keeps its recently judged bound windows and counts one when a
later-arriving transaction turns out to overlap one, which is the only sound moment to see it.

ONE DEVIATION, raised rather than buried. Item 4 of the same ruling accepted the held-and-merged tail of my
Section 3 of my cut file, for a window whose data-bus transactions have not all completed at the closing read. It is not
built, because the reasoning behind it was wrong and the hold protected against nothing: I had assumed an
unarrived transaction would make the bound too TIGHT, and it is the other way round. A transaction that has
not been published is simply absent from the outstanding-cycle total, which makes the documented ceiling
LARGER, so the bound only ever loosens and never fires falsely. Holding the window instead would have added
a merge path on which a real miss could hide. The hold goes back in on the DV Lead's word if the reasoning is
not accepted.

## 4. Red and green, three pairs on the same stimulus with the knob as the only difference

Retained as `gen_fu_l65_counters_census.log`, produced by the census script over the run directories.

| run | knobs beyond the default | accommodations reported | collected errors | verdict |
|---|---|---|---|---|
| b20_default | none | B20 fence.i = 1 | 0 | PASS |
| b20_doc | `+gen_ctr_rtl_jumps_fencei=0` | none | 1, ctr_hpm_exact on mhpmcounter7 | FAIL |
| b11_default | none | B11 dit = 2 | 0 | PASS |
| b11_doc | `+gen_ctr_rtl_taken_dit=0` | none | 2, ctr_hpm_exact on mhpmcounter9 | FAIL |
| b17_default | the response latency pinned to 8 | B17 counter 8 = 1, counters 11 and 12 = 2 | 0 | PASS |
| b17_doc | that plus `+gen_ctr_rtl_branches_wait=0 +gen_ctr_rtl_wait_cycles=0` | none | 3, ctr_hpm_exact on 8 and ctr_hpm_bound on 11 and 12 | FAIL |
| b11_nmi | `+gen_ut_ctr_nmi_after=20` (the entry proof of Section 3) | B11 dit = 1 | 0 | PASS |

The three red runs' lines, from the retained census:

```
[ctr_hpm_exact] mhpmcounter7 advanced 1, 0 predicted: read 00000001 -> 00000002, cycles 40..56, order 10
[ctr_hpm_exact] mhpmcounter9 advanced 16, 0 predicted: read 00000000 -> 00000010, cycles 48..176, order 29
[ctr_hpm_exact] mhpmcounter9 advanced 1, 0 predicted: read 00000010 -> 00000011, cycles 176..200, order 34
[ctr_hpm_exact] mhpmcounter8 advanced 8, 1 predicted: read 00000000 -> 00000008, cycles 49..66, order 17
[ctr_hpm_bound] mhpmcounter11 advanced 6, at most 1 documented (1 multiply record(s) at 1 cycles each, and 8 of the window's 13 cycles had a data access outstanding leaving 5 free): read 00000000 -> 00000006, cycles 103..116, order 39
[ctr_hpm_bound] mhpmcounter12 advanced 43, at most 36 documented (1 divide record(s) at 36 cycles each, and 8 of the window's 49 cycles had a data access outstanding leaving 41 free): read 00000000 -> 0000002b, cycles 162..211, order 60
```

The firings are exactly as many as the programs have disputed windows, and no more: one fence.i window; two
DIT windows, the sixteen-branch one and the check branch that follows it before the mode is cleared; and
three of B17's six windows. Each program's own PAIRED CONTROL WINDOW is judged in the same run and stays
green: the nop and call windows of B20, the mode-off window of B11, and the three separated windows of B17.
A rule that fired on everything would have failed those too.

## 5. Which of the programs' own numbers are stable, measured, because an entry may pin them

The counter rules do not depend on this, but the entries that carry the programs do: an exact expectation on
an unstable number fails for a reason that has nothing to do with the bug. Six runs of the B17 program under
`gen_ut_lockstep`, crossing two seeds with three grant-delay settings and the response latency pinned at
eight, reading the program's own delta words out of each run's export. Retained as
`gen_fu_l65_b17_gnt_probe.log`.

| grant delay | seed | gen_b17_delta |
|---|---|---|
| 1..3, the default | 1 | 8, 1, 6, 0, 43, 36, 21 |
| 1..3, the default | 7 | 8, 1, 7, 0, 43, 36, 21 |
| pinned 1 | 1 | 8, 1, 5, 0, 43, 36, 21 |
| pinned 1 | 7 | 8, 1, 7, 0, 42, 36, 21 |
| pinned 3 | 1 | 8, 1, 7, 0, 43, 36, 21 |
| pinned 3 | 7 | 8, 1, 7, 0, 43, 36, 21 |

Words 0, 1, 3 and 5 hold at 8, 1, 0 and 36 across all six, and so does the verdict word at 21, so THE FINDING
ITSELF is seed- and regime-robust. Words 2 and 4, the counter 11 and 12 windows behind the load, take 5 to 7
and 42 to 43, and pinning the grant delay does NOT stabilise them: pinned to 1 they still read 5 at seed 1
and 7 at seed 7. So the residual movement is not on the data bus at all; it is when the multiply or divide
reaches decode relative to the load's response, which the fetch side moves. An expectation on those two words
needs a range.

Two things this settled that were open. The cocotb MODULE makes no difference: the same program under
`gen_ut_lockstep` and under `gen_ut_counters` on one build gives byte-identical delta words, and so does the
landing-64 build without the counter model, so neither the module nor this component perturbs the counts.
And test-writer's independently reported word 0 of 6 does not reproduce here: word 0 is 8 in all six runs
above, on two builds and two modules with the same program source md5, and word 0 is the one word that did
not move in the sweep, so a regime difference does not explain it. That is reported to test-writer with the
table rather than resolved here.

## 6. The fire-check, and why the module does not judge the counters itself

`gen_ut_counters.py` reads the program's OWN measured differences back from memory through MEM_PEEK
(`+gen_ut_ctr_delta_sym`, `+gen_ut_ctr_delta_expect`). Every one of the six runs matched its expectation
exactly, at the value the RTL produces: B20 [1, 0, 2, 1], B11 [16, 0, 1], B17 [8, 1, 6, 0, 43, 36, 21] (the
last word of each is the program's own verdict against the documentation). That read-back is what makes the
green runs mean something: the program met the counter behaviour under test, so a checker with zero misses
judged that behaviour rather than nothing at all.

The module does not require the program's end-of-test code to be the pass value, because these programs are
bug reproducers that store a failing code by design; it requires only that the program reached its store, so
a run that died in its trap vector cannot pass.

## 7. The bound on counters 11 and 12, derived twice

The documented ceiling is the tighter of two sound ones, and both are needed. The first is the
instruction's own latency: `GEN_MUL_WAIT_MAX_CYCLES` = 1, because the fast multiplier runs MD_OP_MULL in one
cycle and a high form as MULL then MULH (`rtl/ibex_multdiv_fast.sv:139-232`); `GEN_DIV_WAIT_MAX_CYCLES` =
36, because the divider FSM takes MD_IDLE, MD_ABS_A, MD_ABS_B, 31 MD_COMP iterations, MD_LAST,
MD_CHANGE_SIGN and MD_FINISH (`:91`, `:426-517`), 37 cycles of which the last retires. The second is the
window's free cycles: a cycle in which a memory response was outstanding cannot be a wait cycle of the
multiply, because the multiply has not started then (`rtl/ibex_id_stage.sv:866-869` advances the state only
under `instr_executing`, which carries the outstanding-access term that `:1054-1057` leaves out of
`instr_executing_spec`).

The derivation of 36 was CONFIRMED BY MEASUREMENT before it was relied on: B17's own control window, where
the divide runs with no access outstanding, measures exactly 36. The behind-the-load window measures 43.
An earlier form of this rule used the free-cycle ceiling alone and did NOT catch B17 on counter 11, because
the record-cycle window is stretched by the load's write-back wait; that is why the latency ceiling is
there.

## 8. Waveform confirmation (LOG-103)

The retained log is `gen_fu_l65_waveform.log`, which carries the transition tables, the FSDB paths and the two runs' collected messages verbatim. In short: for B20 the window between the two reads holds exactly
one instruction, the fence.i, `perf_jump` pulses once in its decode cycle and the counter moves 1 to 2, and
the fence.i's OWN record still samples 1, which is the sample-point asymmetry Section 1 rests on. For B17
`perf_branch` stays high for the eight cycles between the load's grant and its response, one count per
cycle, and `perf_mul_wait` rises after the grant and falls in the same cycle the response arrives, so every
counted cycle was spent waiting for memory and none for the multiply.

## 9. Two defects found in my own work while building this, both fixed here

- A conditional operator on two string literals pads the shorter one to the longer one's width in
  SystemVerilog, so the first form of the bound message carried a run of blanks before its tail. Both
  affected messages now build the clause in a `string` variable. Caught by reading the retained census, not
  by a compile.
- The first form of the counters 11 and 12 rule used the free-cycle ceiling alone and passed B17 silently
  (Section 7). Caught because the accommodation count was zero in a run that plainly met the candidate,
  which is the question the direction ruling's counters exist to answer.

## 10. What of the counter model stays UNBUILT

`ctr_mcycle` and `ctr_minstret` as checkers; exact rules for counters 5, 6 and 10; bound rules for
counters 3 and 4; the `gen_counter_cg` coverage hooks; and an always-on per-record floor, which would need
the sample-point asymmetry of Section 1 modelled. The API document's Section 9 is the list of record.

## 11. Checks run on this landing

- `gen_knobs_codegen.py --check` and `gen_fcov_codegen.py --check`: up to date.
- `dv/auto_dv/tb/unit/gen_ut_knobs_codegen.py`: PASS, 0 failures.
- The compile above, vcs exit 0.
- The six runs of Section 4, the six of Section 5 and the two waves runs of Section 8.
- `gen_comment_census.py` over `dv/auto_dv/env`, `dv/auto_dv/tb` and `dv/auto_dv/gen_tb`.

## 12. What test-writer owes and what I owe

The six testlist entries these runs correspond to are written out as
`dv/auto_dv/work/tb-infra/gen_l65_testlist_entries.yaml` for test-writer to fold into
`dv/auto_dv/flow/gen_testlist.yaml`, which is test-writer's file this phase. Until they land, the runs of
Section 4 are reproducible only through the fixture command the census records.

## 13. Retained logs

Under `dv/auto_dv/evidence/gen_tdd_logs/lockstep/` with manifest rows in
`dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md`, in TWO SETS. The `gen_fu_l65_` logs were made on build
`b60a9b31cee9f9e7`, before the entry-unjudged row of Section 3 existed, and are committed and untouched: a
retained log is never reopened. The `gen_fu_l66_` logs are the same six runs and the same two waves runs
re-made on `d6dce5adfdc0d98f`, which carries that row, plus the stability probe of Section 5:
`gen_fu_l66_counters_census.log`, `gen_fu_l66_waveform.log`, `gen_fu_l66_b17_gnt_probe.log`, and for each of
b20_doc, b11_doc, b17_doc, b11_default and b11_nmi the run header, the verdict and the simulator log; the last
two are the entry-proof pair of Section 3. Every figure in this record
is from the `gen_fu_l66_` set; the two sets agree on all of them, which is the evidence that adding the row
changed no verdict.
