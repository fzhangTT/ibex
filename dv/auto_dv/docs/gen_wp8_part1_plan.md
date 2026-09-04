# WP-8 part 1 plan: the CG-IC-006 sampler for the samplable coverpoints, plus two observations

Scope as the Orchestrator assigned it and the plan owner sized it: the CG-IC-006 covergroup built for the coverpoints
samplable from the announced injection event, plus the two cheapest observations in the DV Lead's cost order. The other
four observations and their coverpoints stay owned, undeclared and not ignored for a part 2 called separately.

Not started: the pre-execution cross-model review of this plan gates the build, per the review policy. The first review
of this plan returned REQUEST-CHANGES; this revision answers its ten rows and the map from row to section is Section 10.

## 1. Prerequisite: three CG-IC-006 lines of the fcov plan, normalised by the plan owner

The renderer refuses this group as the plan stood at commit 6457c71. Adding CG-IC-006 to the IMPLEMENTED tuple
(gen_fcov_codegen.py:148 is the per-covergroup loop) and rendering produces three refusals in succession:

    gen_fcov_codegen: CG-IC-006: CSV coverpoints without a plan bins line: ['cp_multiway_mismatch']
    gen_fcov_codegen: CG-IC-006.cr_ram_x_bits_x_way: no plan cross line `- cr_ram_x_bits_x_way = cp_a x cp_b`
    gen_fcov_codegen: CG-IC-006.cr_bits_x_rate: component cp_knob is not a coverpoint of the group

The three causes are punctuation, not semantics, but only ONE of them is a one-off, and the difference decides how far
this plan's tool claim may reach. Measured with the loader's own bullet-join rather than a line-based scan, over the
plan's 1469 coverpoint bullets in 206 covergroups:

Counted over the coverpoint bullets the committed regex REFUSES, on lines the loader has joined, since a bullet wraps
and the keyword can land on a continuation line:

| form | at 6457c71 | at fa3fb77 | the CG-IC-006 line |
|---|---|---|---|
| a parenthetical between the coverpoint name and the next keyword | 19 lines / 6 covergroups | 18 / 5 | cp_multiway_mismatch, before `iff` |
| `: values` where the parser requires the literal `: bins` | 12 / 8 | 11 / 7 | cp_knob |
| a bin-count phrase between a cross's component list and its colon | 1 / 1 | 0 / 0 | cr_ram_x_bits_x_way, `, 8 bins` |

So the first two forms are CONVENTIONS the plan keeps in a dozen other covergroups, all of them outside the
implemented list today, and only the cross form was ever a variant: one line in the whole plan. The plan's own working
shape for the parenthetical is at the end of the guard, as CG-DMEM-006.cp_b14_records (gen_fcov_plan.md:4141) writes
it.

That count is definition-sensitive, and this plan has now carried two wrong versions of it, so the definition is
stated rather than implied. Every figure anyone has quoted for the `: values` form is reproducible from one of three
choices:

| lines | covergroups | how it was counted |
|---|---|---|
| 12 / 8 at 6457c71, 11 / 7 after | joined bullets, the definition above |
| 11 / 7 at 6457c71, 10 / 6 after | raw lines, no join |
| 9 / 5 at 6457c71, 8 / 4 after | raw lines and a needle with a trailing space |

The join is what the loader does before matching, so the first row is the count that describes the parser. The second
row is a raw-line scan, which loses one bullet whose keyword lands on a continuation line. The third adds a needle
with a trailing space, which loses two more because two bullets END at the keyword. This plan's earlier nine was the
third row, and the figures in review row CM192-L-1 are the second.

The measurement corrects this plan's own earlier claim of nine `: values` lines. That count came from a line-based
scan, which cannot see a wrapped bullet whose keyword lands on a continuation line the loader joins; three of the
twelve wrap. A count of a parser's inputs has to be taken with the parser's reader.

The decision, agreed with the plan owner: it normalises those three lines in its own touch, and WP-8 proposes no tool
change. The claim is scoped to this group and no further. Three normalised lines make CG-IC-006 render, which is all
part 1 needs; they do not make the parser accept the plan at large, and on the counts above it plainly would need to
for the 29 remaining lines in 12 other covergroups. That whole-plan question, normalise the conventions or widen the
parser, is a separate plan-side item in the plan owner's name, to be taken once with me before the next covergroup
enters the implemented list, and no WP-8 step depends on it. The earlier claims that no tool change is required and
that part 1 changes no coverpoint line in the plan are both WITHDRAWN: the first overreached from this group to the
plan, and the second was false of the group.

Status: MET. The three edits are not in the tree at 6457c71; the plan owner's v4g carries all three and is committed
at fa3fb77, inside a wider touch that also records the build split, the Sample-line qualifiers and the no-alert
precedence in the group's own section. So the prerequisite is closed and the build's remaining condition is the
re-review of this plan, not a plan-owner touch. Eleven `: values` lines remain in the file, none of them in this
group, and the committed rendered include is still up to date against the normalised plan, so nothing of the TB's
went stale.

Verified rather than argued, in a temp root built by `git archive HEAD` of four files with the shared tree untouched.
Positive control first: the untouched root renders `--check: up to date`, so the root reproduces HEAD exactly. The
group then renders from the plan owner's working-tree file with nothing else changed, and reports

    // CG-IC-006 (gen_ic_ecc_cg), 24 coverpoint bins, 16 cross bins

CG-IC-006 appends 66 lines, 4591 to 4657: a blank separator and a 65-line group block. The HEAD-rendered text is an
exact prefix of the new file, so no other group's rendered text changes by one byte. That result came out three times
over: from a first probe that applied only
the three line edits to HEAD's plan, and from two successive revisions of the plan owner's working-tree file as it was
still being written. So the figures do not depend on the in-flight wording around those lines, which is why no hash of
a file still being edited is quoted here.

## 2. What lands, with the bin count derived rather than estimated

Counted as DISTINCT coverpoint-and-bin PAIRS of dv/auto_dv/docs/gen_trace_tp_bin.csv, not as CSV rows and not as bin
names: a bin repeats once per test-plan item that references it, so row counts overstate bins (cp_bits has 4 rows and
2 bins), while three coverpoints of this group share the bin name `yes`, so a name count would lose two. The pair is
also the unit a manifest names, as covergroup.coverpoint.bin. Every count below agrees with the rendered group above.

| coverpoint or cross | bins | value the sampler supplies |
|---|---|---|
| cp_ram | 2 | the announced RAM kind |
| cp_bits | 2 | the announced flipped-bit count |
| cp_way | 2 | the announced way |
| cp_beat | 2 | the announced beat |
| cp_alert_pulses | 1 | the judge's verdict and pulse count for the injection |
| cp_major_nmi_quiet | 1 | NEW observation 2 below |
| cp_no_alert_case | 5 | four from the event and the tracked enable/sweep state; uninitialised_data_ram from NEW observation 1 |
| cp_knob | 3, operand only | the knob value; no CSV rows of its own, reaches coverage through cr_bits_x_rate |
| cr_ram_x_bits_x_way | 8 | the three component coverpoints |
| cr_data_x_beat | 2 | cp_ram x cp_beat |
| cr_bits_x_rate | 4 | cp_bits x cp_knob |

Two different totals, and they are not interchangeable. The RENDER total for the group is 24 coverpoint bins and 16
cross bins: 18 coverpoint bins on the eight part-1 coverpoints, 6 on the four part-2 coverpoints, 14 part-1 cross bins
and 2 part-2 cross bins. The MANIFEST total for part 1 is 29, because cp_knob's three bins (none, rare, frequent) have
no rows in gen_trace_tp_bin.csv and are therefore namable in no manifest, exactly as the existing operand-only
coverpoints of other groups are. The CSV's distinct coverpoint-and-bin pairs for the group total 37, which is 29
part 1 plus 8 part 2.
Part 2 holds those 8: cp_inval_ways 2, cp_refetch 1, cp_lookups_blocked_next 1, cp_multiway_mismatch 2,
cr_ram_x_inval 2.

## 3. How the part-1/part-2 split works in the renderer, checked rather than assumed

The renderer's IMPLEMENTED list is per COVERGROUP, not per coverpoint: once CG-IC-006 is in it, every plan coverpoint
renders in plan order (gen_fcov_codegen.py:148 and the comment above it). So a partial covergroup is not expressible by
selection. The split is nonetheless expressible, by a mechanism already in the renderer's output: every rendered
coverpoint carries `ignore_bins na = {-1}`, 203 such clauses in the rendered file today, and a sampler passes -1 for a
coverpoint that does not apply to a sample. A cross tuple whose component sits in an ignore bin is excluded, so the
four part-2 coverpoints leave their real bins at 0 with nothing hidden.

So part 1 renders all twelve coverpoints and all four crosses, samples the eight it can, and passes -1 for the four it
cannot. Their real bins stay at 0 percent, which is exactly "owned, undeclared and not ignored": owned because the plan
and the render carry them, undeclared because no test manifest names them, not ignored because no ignore_bins hides
them. dv_principles.md says a coverpoint may be built before stimulus can hit it and that 0 percent marks intent, while
only GENUINELY unhittable bins are pruned; these are hittable once part 2 exists, so the dilution is correct and
temporary.

## 4. Where the sample fires and what it supplies

One sample per closed injection, fired at the single existing closure point: the line that marks an injection closed in
the misc monitor's close_owed (gen_checkers_pkg.sv:678). That point runs once per injection and only after the verdict
is known, in-run from the per-cycle call at :511 and for whatever is left at the end of the run from the final pass at
:705, so every injection samples exactly once whether the run ends before or after its verdict.

The sampler reads the announced event and the verdict the monitor has already computed. It never reads
`gen_icram_events::probe_on`, `lk_cyc` or `lk_tag`: choosing between form (a) and form (b) is judge_data's business,
not the sampler's. The consequence for cp_alert_pulses is that in a measured run the value comes from form (b),
because judge_data selects the retirement verdict when the probe is off, and that an injection whose verdict is
unjudged (-1, a squashed speculative lookup, an ambiguous parse, or the run ending first) supplies -1 to
cp_alert_pulses rather than a bin. The coverpoint renders only `bins one= {0}`, since the plan's ignore clause drops
its zero and many bins, so -1 is the only correct value for an unjudged injection and for every non-injection sample.

The twelve sample() arguments are filled in the plan's coverpoint order, which the renderer fixes and the sampler
must match position for position: cp_ram, cp_bits, cp_way, cp_beat, cp_alert_pulses, cp_inval_ways, cp_refetch,
cp_major_nmi_quiet, cp_lookups_blocked_next, cp_no_alert_case, cp_multiway_mismatch, cp_knob. Positions six, seven,
nine and eleven are the part-2 coverpoints and take -1 on every part-1 sample.

The wiring is one line in the pattern the env already uses: the misc monitor takes a `gen_isa_cov` handle assigned in
gen_env_pkg's connect_phase beside the existing direct assignments (`misc_mon.sink = sink` at :241,
`dispatch.isa_cov = isa_cov` at :232), and gen_isa_cov gains the covergroup, its `new()` under `cfg.fcov_en` with the
others, and one sample entry point the monitor calls.

## 5. Observation 1: the written flag per data RAM line (the plan's own Sample condition needs it)

The plan's Sample line reads "each injected RAM read corruption, or each CHECKED lookup that read a never-written
(uninitialised) data RAM line", the checked qualifier having arrived with the plan owner's touch of Section 1. No
identifier tracks written-ness anywhere in the TB today: `tag_shadow`
(gen_tb_pkg.sv:560) tracks tag CONTENTS, and there is no data-side equivalent. Measured, so that the claim is a claim
about identifiers and not about a string: across gen_icache_ram.sv, gen_tb_pkg.sv and gen_checkers_pkg.sv the needles
`written`, `wr_seen`, `initialised` and `uninit` yield zero identifier-shaped uses (a declaration, an assignment, an
index or a comma), and the English word "written" appears five times, all in gen_tb_pkg.sv (:38, :271, :560, :562,
:602) and all inside comments: stripping comment text drops the count to zero, while the same strip leaves 311 hits
for the word `parameter`, so the strip is not eating the file. So the sampler cannot honour its own sample condition
until the flag exists, which is why it is in part 1 rather than deferred.

Build. One bit per RAM address in gen_icache_ram.sv beside the `mem [Depth]` array it already stores (:28). The
granularity is a LINE of one way, not a word: each RAM address holds a whole line (the data instance is
`.Width(LineSizeECC), .Depth(IC_NUM_LINES)` at gen_tb_top.sv:156) and the model's write port carries one whole entry,
so no sub-line write exists to distinguish words by. The array is IC_NUM_LINES = 256 bits per way and 512 bits in the
build. The fcov plan said "per-data-word" against its own bin text's "never-written data line read"; v4g settles it
per line, so the plan and this build now say the same thing and no wording is owed either way.

Set in the write branch beside `mem[addr] <= wdata` (:76), so it is set on ANY write the model sees, which is the
point of putting it there: the invalidation sweep and the ECC-correction write both write data words, because
`data_write_ic0 = tag_write_ic0` (rtl/ibex_icache.sv:283, with tag_write_ic0 at :277) while
`data_req_ic0 = lookup_req_ic0 | fill_req_ic0` (:280) excludes them, so such a write lands only in a cycle where a
lookup or a fill request coincides, and when it lands the model sees `req & write` and counts it. Which lines stay
never-written is therefore stimulus-dependent, and that is a DUT property rather than a TB artefact. Cleared never:
the array is initialised to zero in the model's `initial` block (:34), the only other writer, and nothing clears it
afterwards. Not on reset, because neither the model's `mem` nor the DUT's RAMs lose contents on reset and a mid-run
reset (CG-RST-001 is implemented) would otherwise flag previously written valid codewords as uninitialised. Not on
invalidation either: an invalidation clears a tag's valid bit, not the data line, and the data line's ECC stays as
written.

Published without touching the alert path. The uninitialised read does NOT go through `gen_icram_events::announce()`
and never enters `gen_icram_events::q`. That queue is capped at 256 entries with the oldest dropped
(gen_tb_pkg.sv:575), and every lookup reads both ways' data lines whether or not the cache is enabled, because
`data_req_ic0` is unconditioned on the enable and `data_banks_ic0 = tag_banks_ic0` selects all ways for a lookup
(rtl:280, :282, :274), so pushing uninitialised reads into `q` would evict injections still waiting for a form-(b)
verdict, which can take up to GEN_ICACHE_RETIRE_WINDOW = 64 cycles (gen_tb_pkg.sv:248), and those evictions would turn
into false "alert_minor_o high without an announced ECC injection" errors from attribute_pulse
(gen_checkers_pkg.sv:634). Instead the model notes the event in a separate static queue of gen_icram_events that
attribute_pulse, pending_in_window, close_owed, judge_data and report_phase never read: all five iterate `q` only, so
the new queue is unreachable from pulse attribution by construction, and that is the property the mutation in
Section 7 pins.

A separate queue needs its own drain, which the first version of this plan did not give it: the closure point of
Section 4 iterates `q`, so an uninitialised event placed outside `q` would never be sampled at all. Two drain sites,
both beside calls that already exist, and neither inside the injection closure:

- The per-cycle pass, beside `close_owed(0)` (gen_checkers_pkg.sv:511). An event whose read cycle plus
  GEN_ICACHE_ECC_WINDOW has passed is classified and sampled there, judging alert_minor_o from the per-cycle levels
  the monitor already records for the quiet windowing of Section 6. It cannot be sampled at the read, because the
  no-alert half of the classification is only known once the window has closed.
- The final pass, beside `close_owed(1)` (:705). Whatever the end of the run leaves undrained is classified there on
  the levels recorded so far, so no event is silently dropped.

The queue cannot evict, and the bound is arithmetic rather than a hope: the sample is the first checked read of a
never-written line of a way, so at most IC_NUM_LINES x IC_NUM_WAYS = 512 events exist in a whole run, each drained
within GEN_ICACHE_ECC_WINDOW cycles of its read. A queue sized 512 therefore holds every event that can ever be
pushed. Because a bound that is argued is not a bound that is checked, the model also counts pushes it cannot store
and the monitor reports that count in its GEN_MISC summary, so a nonzero eviction count is visible in every run
rather than inferred from this paragraph.

Qualification, so the bin is neither vacuous nor overlapping. Unwritten-line reads occur from the first lookup of
every run, including with the cache disabled and during the reset sweep, so the unqualified form of the Sample line,
"each lookup that read a never-written line", would hit the bin trivially and in enormous numbers. The three
qualifications below are what the sampler implements, and the first two are now in the fcov plan's own Sample line:

- Once per line. Only the FIRST checked read of a never-written line of that way samples, tracked by a second bit per
  address. A later read of a still-unwritten line carries no new information, and the bound is at most 512 samples per
  run rather than one per lookup cycle.
- Checked only. `gen_icram_events::qualified_at(cycle)` (gen_tb_pkg.sv:577) must hold at the read: the cache enabled
  per the scoreboard's cpuctrlsts tracking and no invalidation sweep within the grace window. That term is exactly
  what separates this bin from disabled_cache and during_invalidation, which are its two negations. Stated precisely,
  because the fcov plan's precedence paragraph names the RTL terms instead: `qualified_at` is the TB's observable
  proxy for `icache_enable_i` and `inval_block_cache`, the two terms of `lookup_actual_ic0` (rtl/ibex_icache.sv:266),
  built from the enable the scoreboard sees in a record and from the sweep's all-ways tag writes, each with a grace
  window, because the TB sees both states late. The classifier uses the proxy; the intent is the RTL terms.
- No injection in that cycle, and no alert owed or seen. The read cycle must carry no injection of either RAM kind,
  which is what separates the bin from unused_way_data and masked_duplicate_copy, and alert_minor_o must stay low
  across 1..GEN_ICACHE_ECC_WINDOW after the read, which is the "no alert" the coverpoint is about.

Bin precedence, stated once so the classifier is a total function. An unqualified cycle classifies as disabled_cache
when the enable term failed and during_invalidation when the sweep term failed, and those win over everything else. On
a qualified cycle with an injection, the injection cases win: unused_way_data when the verdict says another or an
invalid way, masked_duplicate_copy when the flip was masked by the OR of a duplicate copy. uninitialised_data_ram
applies only to a qualified cycle with no injection. No sample carries two of these.

Intent anchor: rtl/ibex_icache.sv:580-584 says no data-RAM initialisation is done on reset, so unused data, in
particular the ways without a valid tag, may carry incorrect ECC, which is why the DUT checks data ECC only on a valid
hit: `ecc_err_ic1 = lookup_valid_ic1 & (((|data_err_ic1) & tag_hit_ic1) | (|tag_err_ic1))` at :585. A checked lookup
reading a never-written line and raising no alert is therefore a real no-alert case that the DUT's own comment
predicts, and not a TB artefact.

## 6. Observation 2: the major-quiet windowing

cp_major_nmi_quiet asks that alert_major_internal_o, alert_major_bus_o and rvfi_ext_nmi_int stayed low across the
injection window. Position measured per signal rather than by an occurrence total, since reachability is a yes-or-no at
the sampling site that no count answers: the two major-alert outputs are already sampled every cycle by the misc
monitor's run_phase, and the interrupt-extension signal reaches the monitor inside a struct it already takes. So this
is windowing plus one new read, not new visibility.

Per-signal window semantics, which the first version of this plan left unstated.

- The two major-alert outputs are LEVELS. The term is: high in ANY cycle of 1..GEN_ICACHE_ECC_WINDOW after the
  injection cycle means not quiet, and a level that was already high before the window and is still high inside it
  counts as high, so a persistent alert is not read as quiet. GEN_ICACHE_ECC_WINDOW is 2 (gen_tb_pkg.sv:246). The
  monitor keeps the last window's worth of cycles of both levels; it samples both signals every posedge already.
- rvfi_ext_nmi_int is a PER-RETIREMENT RVFI flag, not a level, so a two-cycle window can never see it and the term
  would be vacuous over the alert window. Its term is therefore over retirements: no retirement carrying the flag
  between the injection cycle and the sample, considering at most GEN_ICACHE_RETIRE_WINDOW = 64 cycles
  (gen_tb_pkg.sv:248), the window the form-(b) judge already waits out. The value needs no second routing: the field
  is `gen_model_state.nmi_int_pend`, declared at gen_rvfi_pkg.sv:69 and set from `t.ext_nmi_int` at :207, and the
  struct is the argument of the misc monitor's write_state at gen_checkers_pkg.sv:408. The earlier wording
  "referenced ZERO times in the checkers" was true of the string only and is withdrawn: the field arrives at the
  monitor today inside a struct it already receives, and what part 1 adds is one read of it, not a route.
- Where the two windows disagree, the bin is not claimed. A sample that closes before any retirement has been seen
  supplies -1 to cp_major_nmi_quiet rather than yes, so an early closure (a probe-on evidence run, where form (a)
  decides at once) cannot record a quiet that no retirement window supports. In practice this makes the bin a
  measured-run bin, which is stated here rather than discovered later.

Build: extend the misc monitor's per-injection window bookkeeping, which already exists for the pulse attribution,
with the recorded levels and the retirement flag over the two windows, and classify at the sample point of Section 4.
The classification is a pure function of the recorded values, which is what makes the Section 7 detector possible.

## 7. Trust triad, per new observation, with the detector named for each red and each mutation

The general rule for a coverage observation: a manifest fails an UNHIT declared bin, so a manifest is the detector for
a red that suppresses a bin and cannot be the detector for a mutation that makes a bin hit WRONGLY. The latter needs a
classifier check. This build uses `GEN_FCOV_UT` (gen_fcov_pkg.sv:1667) for the second kind: it compares a
classifier's return value against an expected index and raises uvm_error("GEN_FCOV_UT") on a mismatch, and a directed
test reaches it in a run through the existing bridge command GEN_CMD_FCOV_SELFTEST (gen_env_pkg.sv:123), so a
classifier fault is a failing run and not only a failing offline check.

- TDD, written flag. Red: a directed run whose program reads a line the program never wrote, with a manifest
  declaring cp_no_alert_case.uninitialised_data_ram. With the flag absent the classifier cannot return that bin, the
  declared bin goes unhit, and the fcov-expectation check fails the run. The named detector is the manifest check on
  that bin. A second red covers the precedence rules as classifier cases: GEN_FCOV_UT cases asserting that an
  unqualified cycle returns disabled_cache or during_invalidation, that a qualified cycle with an injection returns
  the injection case, and that only a qualified injection-free cycle returns uninitialised_data_ram.
- TDD, quiet windowing. Red: GEN_FCOV_UT cases over recorded values, asserting that a level high in the last cycle of
  the alert window is not quiet, that a level high before and through the window is not quiet, and that a retirement
  carrying the internal-NMI flag inside the retire window is not quiet. No DUT output is forced. The earlier plan's
  "a forced assertion of one major alert" is WITHDRAWN: forcing alert_major_internal_o trips the forces rubric and
  also the unconditional check at gen_checkers_pkg.sv:474, which raises uvm_error("alert_internal") on any high cycle.
  Where a run-level red is wanted rather than a classifier case, the legitimate stimulus is a bus integrity
  corruption: the bus agent's corruption raises alert_major_bus_o, and the alert_bus check expects exactly that
  (`exp = (ibus.rvalid && ibus.intg_corrupt) || (dbus.rvalid && dbus.intg_corrupt)` at :482), so the alert is legal
  and the quiet term must read it as not quiet. Its coincidence with an injection window is stimulus-dependent, so it
  rides as evidence when it lands and the classifier cases carry the gate.
- Mutation-proof, written flag. Named mutation: the write branch marks every address written from the initial block,
  so the uninitialised case never classifies. Detector: the same manifest check, on the declared bin, with every
  other Zone A check disabled, plus the ablation control. Second named mutation: the uninitialised event is pushed
  into `gen_icram_events::q` instead of its own queue, which is the fault Section 5 designs against. Its detector is
  NOT the alert_minor check: that check only fires once the 256-deep `q` actually evicts a pending injection, which
  needs more than 256 events inside one 64-cycle verdict window and is therefore stimulus-dependent. The detector is
  deterministic instead, a GEN_FCOV_UT case asserting that `gen_icram_events::q.size()` is unchanged across an
  uninitialised event and that the bypass queue's size rose by one, which fails on the mutation in any run that
  reaches one uninitialised read.
- Mutation-proof, quiet windowing. Named mutation: the window is sampled one cycle short, so an alert at the boundary
  is missed and the quiet bin is hit wrongly. No manifest can catch a wrongly hit bin, so the detector is a
  GEN_FCOV_UT case on the boundary cycle, run through GEN_CMD_FCOV_SELFTEST, with its ablation control.
- fcov-expectation. A manifest declaring exactly the 29 part-1 bins, per test, pre-merge, with the anti-vacuity review
  the sample condition needs. cp_knob's three rendered bins are in no manifest, since they have no CSV rows. The four
  part-2 coverpoints appear in NO manifest.

## 8. What is announced, to whom, and what else WP-8 contains

Every coverpoint, cross and Sample line this work touches goes to the Orchestrator and the Test Writer before it
lands, per the assignment, and the three normalised lines of Section 1 plus the Sample-line qualifiers are the plan
owner's own touch, announced the same way, and it is committed at fa3fb77: the group's section carries the
checked-lookup qualification, the written-flag description per line, the no-alert precedence order, the per-signal
quiet windowing and a build-split paragraph of its own. The split it records is EIGHT sampled and FOUR passing
not-applicable, which is the state after part 1 builds two of the six observations that were unbuilt when the split
was first sized six-and-six by observability alone. One wording item is owed back to it, the word-versus-line
granularity of Section 5, which v4g has since taken; nothing in that section now disagrees with this plan.

WP-8 in gen_test_plan.md is wider than this covergroup, and this plan is not all of it. That row assigns TB Infra the
three exact export rows `icram lookup`, `icram tag_write` and `icram fill_write`, announced by gen_icache_ram like
`icram inject`, and names the witness-table digest guard as a joint TB Infra, Runtime and Test Writer item. The three
export formatters exist (gen_export_event_lines.svh:83-91) and gen_icache_ram.sv carries no export reference at all,
so that half is unbuilt. It is neither part 1 nor part 2 of this covergroup split: part 1 is the sampler and the two
observations, part 2 is the four remaining observations and their coverpoints, and the export rows and the digest
guard are a separate assignment on the same work package, still gating the 17 TP-IC items the row names.

## 9. ETA

Simulation is the small part: the evidence runs reuse the existing directed programs and the local loop is about a
minute for a run set. The work is the sampler and the two observations, each with its red, its mutation and its
ablation. Estimate 2.5 to 3 hours wall, of which about 30 minutes is simulation, on the same pattern as the WP-12
landings, and the clock starts when the plan owner's prerequisite touch lands. Report at the fold, or earlier if the
shape changes.

## 10. Where each review row is answered

| row | answered in |
|---|---|
| C-1, the unbuildable pair of constraints | Section 1: the prerequisite named and met at fa3fb77, the tool claim scoped to this group with the two conventions measured, both sentences withdrawn, the refusals and the successful render reproduced |
| H-1, the announcement flooding the event queue | Section 5, "Published without touching the alert path": a separate queue, with the five functions that read `q` only |
| H-2, anti-vacuity of uninitialised_data_ram | Section 5, "Qualification" and "Bin precedence": first read per line, `qualified_at`, injection-free, and the precedence order; sweep writes counted as writes |
| M-1, cleared on reset | Section 5, "Cleared never": initial block only, not on reset, not on invalidation |
| M-2, window semantics per signal | Section 6: levels over 1..GEN_ICACHE_ECC_WINDOW with a persistent level not quiet, the NMI flag over the retire window through `gen_model_state.nmi_int_pend`, the "referenced ZERO times" wording withdrawn |
| M-3, unnamed trust-triad detectors | Section 7: a detector named per red and per mutation, GEN_FCOV_UT for wrongly hit bins, no forced DUT output |
| M-4, sample timing and probe-off judging | Section 4: the closure point, form (b) in measured runs, -1 when unjudged, and the sampler reading no probe state |

## 11. Where each row of the re-review is answered

| row | answered in |
|---|---|
| CM192-M-1, the bypass queue had no drain point | Section 5: two drain sites beside the existing per-cycle and final passes, the 512-event arithmetic bound, and an eviction count in the GEN_MISC summary |
| CM192-L-1, the `: values` counts | Section 1: the counts re-measured on joined bullets at both commits, with the three-way reconciliation that shows which definition produces which figure |
| CM192-L-2, the second mutation's detector was stimulus-dependent | Section 7: replaced by a GEN_FCOV_UT case on the two queue sizes |
| CM192-L-3, stale status sentences and the appended line count | Section 1: the prerequisite cited at fa3fb77, the granularity sentence dropped, 66 lines |
| L-1, the zero-hits sentence | Section 5, first paragraph: an identifier claim with the measurement and its control |
| L-2, cp_knob's three bins | Section 2: the render total and the manifest total stated separately |
| L-3, the WP-8 row of the test plan | Section 8: the export rows and the digest guard placed outside this split |
