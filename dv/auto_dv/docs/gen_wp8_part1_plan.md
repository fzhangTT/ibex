# WP-8 part 1 plan: the CG-IC-006 sampler for the samplable coverpoints, plus two observations

Scope as the Orchestrator assigned it and the plan owner sized it: the CG-IC-006 covergroup built for the coverpoints
samplable from the announced injection event, plus the two cheapest observations in the DV Lead's cost order. The other
four observations and their coverpoints stay owned, undeclared and not ignored for a part 2 called separately.

Not started: the pre-execution cross-model review of this plan gates the build, per the review policy.

## 1. What lands, with the bin count derived rather than estimated

Counted as DISTINCT bin names from dv/auto_dv/docs/gen_trace_tp_bin.csv, not as CSV rows: a bin repeats once per
test-plan item that references it, so row counts overstate bins (cp_bits has 4 rows and 2 bins). Every count below
agrees with the plan's own bin list.

| coverpoint or cross | bins | value the sampler supplies |
|---|---|---|
| cp_ram | 2 | the announced RAM kind |
| cp_bits | 2 | the announced flipped-bit count |
| cp_way | 2 | the announced way |
| cp_beat | 2 | the announced beat |
| cp_alert_pulses | 1 | the judge's verdict and pulse count for the injection |
| cp_major_nmi_quiet | 1 | NEW observation 2 below |
| cp_no_alert_case | 5 | four from the event and the tracked enable/sweep state; uninitialised_data_ram from NEW observation 1 |
| cp_knob | operand only | the knob value; no CSV rows of its own, reaches coverage through cr_bits_x_rate |
| cr_ram_x_bits_x_way | 8 | the three component coverpoints |
| cr_data_x_beat | 2 | cp_ram x cp_beat |
| cr_bits_x_rate | 4 | cp_bits x cp_knob |

Part 1 total: 29 distinct bins. Part 2 holds 8: cp_inval_ways 2, cp_refetch 1, cp_lookups_blocked_next 1,
cp_multiway_mismatch 2, cr_ram_x_inval 2.

## 2. How the part-1/part-2 split works in the renderer, checked rather than assumed

The renderer's IMPLEMENTED list is per COVERGROUP, not per coverpoint: once CG-IC-006 is in it, every plan coverpoint
renders in plan order (gen_fcov_codegen.py:148 and the comment above it). So a partial covergroup is not expressible by
selection. The split is nonetheless expressible, by a mechanism already in the renderer's output: every rendered
coverpoint carries `ignore_bins na = {-1}`, 203 such clauses in the rendered file today, and a sampler passes -1 for a
coverpoint that does not apply to a sample.

So part 1 renders all twelve coverpoints and all four crosses, samples the eight it can, and passes -1 for the four it
cannot. Their real bins stay at 0 percent, which is exactly "owned, undeclared and not ignored": owned because the plan
and the render carry them, undeclared because no test manifest names them, not ignored because no ignore_bins hides
them. dv_principles.md says a coverpoint may be built before stimulus can hit it and that 0 percent marks intent, while
only GENUINELY unhittable bins are pruned; these are hittable once part 2 exists, so the dilution is correct and
temporary. No tool change is required and none is proposed.

## 3. Observation 1: the written flag per data word (the plan's own Sample condition needs it)

The plan's Sample line reads "each injected RAM read corruption, or each lookup that read a never-written
(uninitialised) data RAM line". Nothing tracks written-ness anywhere today: written, wr_seen, initialised and uninit all
return zero hits across the RAM model, the TB package and the checkers. So as the plan stands the sampler cannot honour
its own sample condition until this exists, which is why it is in part 1 rather than deferred.

Build: one bit per data word in gen_icache_ram.sv beside the array it already stores, set on write and cleared on reset,
published in the announcement for a read of an unwritten word. It needs no routing and no new visibility, which is why
the plan owner ranked it cheapest.

Intent anchor: rtl/ibex_icache.sv:580-584 says no data-RAM initialisation is done on reset, so unused data may carry
incorrect ECC, which is why the DUT checks data ECC only on a valid hit. A lookup reading a never-written line is
therefore a real no-alert case and not a TB artefact.

## 4. Observation 2: the major-quiet windowing

cp_major_nmi_quiet asks that alert_major_internal_o, alert_major_bus_o and rvfi_ext_nmi_int stayed low across the
injection window. Position measured per signal rather than by an occurrence total, since reachability is a yes-or-no at the
sampling site that no count answers: the two major-alert outputs are
referenced in the checkers package and in the wrapper, the assertion layer and both TB tops; the interrupt-extension
signal is referenced in the checkers ZERO times but is wired at the TB top and recorded in the interface inventory. So
this is windowing plus one routing, not new visibility.

Build: extend the misc monitor's per-injection window bookkeeping, which already exists for the pulse attribution, with
a quiet flag over the same window, and route the interrupt-extension signal to where the monitor samples.

## 5. Trust triad, per new bin and per new observation

- TDD: each new observation gets a red first. For the written flag, a directed run whose program reads a line the
  program never wrote, with the flag forced false, must fail the new no-alert classification before the flag makes it
  pass. For the quiet windowing, a forced assertion of one major alert inside an injection window must fail.
- Mutation-proof: one named mutation per observation, caught by the named checker with every other Zone A check
  disabled, plus the ablation control. Written flag: a mutation that marks every word written, so the uninitialised case
  never classifies. Quiet windowing: a mutation that samples the window one cycle short, so an alert at the boundary is
  missed.
- fcov-expectation: a manifest declaring exactly the 29 part-1 bins, per test, pre-merge, with the anti-vacuity review
  the sample condition needs. The four part-2 coverpoints appear in NO manifest.

## 6. What is announced, and to whom

Every coverpoint, cross and Sample line this work touches goes to the Orchestrator and the Test Writer before it lands, per the
assignment. Part 1 changes no coverpoint LINE in the plan: the DV Lead is recording the six-and-six split and the
Sample-line qualifier in its own next touch, so the plan and the build say the same thing with no cross-role edit.

## 7. ETA

Simulation is the small part: the evidence runs reuse the existing directed programs and the local loop is about a
minute for a run set. The work is the sampler and the two observations, each with its red, its mutation and its
ablation. Estimate 2.5 to 3 hours wall, of which about 30 minutes is simulation, on the same pattern as the WP-12
landings. Report at the fold, or earlier if the shape changes.
