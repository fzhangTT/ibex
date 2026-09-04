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
and the keyword can land on a continuation line. Figures at 61c1a1a, which is where two plausible definitions of the
group set stop disagreeing:

| form | at 61c1a1a | the CG-IC-006 line it explains |
|---|---|---|
| a parenthetical between the coverpoint name and the next keyword | 19 lines / 6 covergroups | cp_multiway_mismatch, before `iff` |
| `: values` where the parser requires the literal `: bins` | 11 / 7 | cp_knob |
| a bin-count phrase between a cross's component list and its colon | 0 / 0 | cr_ram_x_bits_x_way, `, 8 bins` |

Against 1483 coverpoint bullets in 207 covergroups at that commit. So the first two forms are CONVENTIONS the plan keeps
in other covergroups, all of them outside the implemented list today, and only the cross form was ever a variant: one
line in the whole plan. The plan's own working shape for the parenthetical is at the end of the guard, as
CG-DMEM-006.cp_b14_records writes it.

Every figure quoted for these counts is reproducible, and the plan states the definitions rather than leaving a reader
to guess, because three parties produced five different numbers for the same two questions.

| bullets / groups | parenthetical | commit | how the group set was defined |
|---|---|---|---|
| 1483 / 207 | 19 / 6 | 61c1a1a | either definition; they agree here |
| 1469 / 206 | 18 / 5 | fa3fb77 | the renderer's own header regex |
| 1483 / 207 | 19 / 6 | fa3fb77 | any `### CG-` header |
| 1469 / 206 | 19 / 6 | 6457c71 | the renderer's own header regex |
| 1483 / 207 | 20 / 7 | 6457c71 | any `### CG-` header |

Two mechanisms make those rows differ, and both are worth knowing. The group set: at 6457c71 and fa3fb77 the header
`### CG-DIT-004: gen_cg_dit_dummy_insert (P1; probe-gated, ...)` carried a trailing parenthetical the renderer's header
regex does not match, so that group and its 14 bullets were invisible to a count taken with the renderer's reader,
while a plain header scan saw them. v4h normalised that header, so at 61c1a1a all 208 written headers parse and the
two definitions coincide. Separately, 208 headers parse while 207 carry a coverpoint bullet, because one adopted-only
group declares none. The composition: 6457c71 and 61c1a1a both give 19 in 6 for the parenthetical form through
DIFFERENT groups, CG-IC-006's own line at the first and CG-DIT-004's at the second.

The measurement corrects this plan's own earlier claim of nine `: values` lines. That count came from a line-based
scan, which cannot see a wrapped bullet whose keyword lands on a continuation line the loader joins; three of the
twelve wrap. A count of a parser's inputs has to be taken with the parser's reader.

The decision, agreed with the plan owner: it normalises those three lines in its own touch, and WP-8 proposes no tool
change. The claim is scoped to this group and no further. Three normalised lines make CG-IC-006 render, which is all
part 1 needs; they do not make the parser accept the plan at large.

The whole-plan question is CLOSED, not open, and by a ruling wider than the two forms this plan measured. The plan
owner measured the committed parser over the whole plan and found 158 non-parsing coverpoint bullets across 65 of 208
covergroups in SEVEN families, of which the two above are only the first two; the other five are an `=` or `:` inside
an iff guard, other coverpoint shapes, a marker between a cross's components and its colon, a cross with no component
list, and other cross shapes. On that measurement it ruled neither of the two options this plan framed: not a
plan-wide sweep of 158 prose rewrites, and not a parser widened to accept seven families, which would destroy the
strictness that caught CG-IC-006's three lines in the first place. The ruling is per-group normalisation at
implementation time, verified by render, exactly as CG-IC-006 was done, at a measured median of two lines per affected
group. It is recorded in the response record beside this plan. So no WP-8 step depends on it, and this plan's earlier
framing of it as an item still to be taken is withdrawn. The earlier claims that no tool change is required and
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
and 2 part-2 cross bins. The MANIFEST total for part 1 is 29 as a SET of namable bins, because cp_knob's three bins
(none, rare, frequent) have
no rows in gen_trace_tp_bin.csv and are therefore namable in no manifest, exactly as the existing operand-only
coverpoints of other groups are. The CSV's distinct coverpoint-and-bin pairs for the group total 37, which is 29
part 1 plus 8 part 2.
Part 2 holds those 8: cp_inval_ways 2, cp_refetch 1, cp_lookups_blocked_next 1, cp_multiway_mismatch 2,
cr_ram_x_inval 2.

WHAT DECLARES PART 1's BINS IS NINE PER-ENTRY MANIFESTS, one per WP-8 icache ECC testlist entry, each declaring only
the bins its own entry can hit; the expectation check is per entry and validates the manifest's test against the entry
name, so no single manifest can serve them all. The union reachable today is 15 of 15 across nine entries; the nine
manifests declare the robust subset of 13 bins, robust meaning a structural bound or a measured count of at least 30
in that entry's own run; OWED are two bins, both thinly hit and closing on one route, a seed sweep at coverage
closure: cp_no_alert_case.during_invalidation (10, 9, 22) and cp_no_alert_case.masked_duplicate_copy (4, 2, 14).
Separately and NOT owed, two per-entry exclusions live in the manifest headers rather than here, since the bin is
robust elsewhere and thin only on those entries: cp_no_alert_case.uninitialised_data_ram on the two far-program
entries (9, 9) and cp_alert_pulses.one on the far probe-off entry (27). Section 7 gives the mechanism and the ninth
entry.

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

Two sample sites, not one, and this section covers the first. One sample per closed INJECTION, fired at the single
existing closure point: the line that marks an injection closed in the misc monitor's close_owed
(gen_checkers_pkg.sv:678). The never-written reads are the second site and do not pass through that point at all;
Section 5 gives their two drains and says why they cannot fire at the read. That point runs once per injection and
only after the verdict
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

DEVIATION FROM THAT SENTENCE, as built, recorded here because the re-review read the wiring above. The handle and the
one connect-phase line are as stated, but every bin INDEX is mapped inside gen_fcov_pkg behind two entry points rather
than at the monitor's call sites, so the monitor states facts in its own terms (a RAM kind, a bit count, a verdict, two
window answers) and names no coverage constant. The check is that GEN_FC_ appears zero times in gen_checkers_pkg.sv.
The reason is that those constants are localparams of the fcov package: naming them in the checkers package needs an
import, which would pull that package's whole namespace in for ten references, and the mapping belongs with the
covergroup that defines the indices. The window arithmetic went the other way for the same kind of reason: it is one
function in gen_tb_pkg, which both packages already import, so the monitor's three window queries share it and its
boundary is pinned by unit-test cases instead of being repeated three times.

Detector coverage of the window terms, stated rather than implied. The arithmetic has unit-test cases on all four
boundary positions, so a mutation of the arithmetic fails them in any run. A mutation of the SPAN ARGUMENT at a call
site, passing the window constant less one, is not caught by those cases and by nothing else this build carries: a
wrongly hit bin is invisible to a manifest, which fails only an unhit declared bin. The residual is narrower than it
sounds, because a high alert_major_internal_o is already an unconditional error in the misc monitor
(gen_checkers_pkg.sv:474), so the only major output that can legitimately be high inside a window is the bus one under
an announced corruption, but the gap is real and is named here rather than covered by a mutation that does not reach
it.

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
  GEN_ICACHE_ECC_WINDOW has passed is classified and sampled there. It cannot be sampled at the read, because the
  no-alert half of the classification is only known once the window has closed. The alert_minor_o term needs a level
  history the checkers did not keep: the monitor holds only the export edge and the pulse counters, and Section 6's
  histories are the two MAJOR outputs. So this build adds a third history of the same shape, the cycles at which
  alert_minor_o was high, pruned to the longest window any term asks about, and the drain reads that. Naming it here
  because a plan that borrowed Section 6's histories for this term would describe a build that cannot work.
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

WHAT THE BIN WITNESSES, corrected: the UNHIT-WAY MASKING, not a checked read that came back clean. A never-written
data line can never be the hit way, and the term chain says so rather than a comment: the only thing that makes a way
hittable is a fill, since the other two writers of tag_write_ic0 write tags INVALID
(`tag_write_ic0 = fill_grant_ic0 | inval_write_req | ecc_write_req`, rtl/ibex_icache.sv:277), and a fill writes that
way's data in the same cycle, since `data_write_ic0 = tag_write_ic0` (:283) and `data_req_ic0` includes
`fill_req_ic0` (:280) so the write lands rather than being masked by the request term. The read is then quiet WITHOUT BEING
CHECKED, by two mechanisms that are EXHAUSTIVE rather than merely listed, because `tag_hit_ic1 = |tag_match_ic1`
(:504) makes the gate the OR of the very per-way predicate the hit-data mux uses. When a way matches, the never-written
way is not among them, since the match compares the valid bit as its top bit (`== {1'b1, lookup_addr_ic1[...]}`,
:499-500, with :501 defining tag_invalid_ic1 as that same bit inverted)
and only a fill sets it, so its data is excluded from `hit_data_ecc_ic1` by the mux (:507-514) and never reaches the
decoder, which decodes the mux output alone (`.data_i(hit_data_ecc_ic1[...])` into `.err_o(data_err_ic1[...])`,
:568-573). When no way matches, `tag_hit_ic1` is zero and the data-ECC term is masked outright
(`ecc_err_ic1 = lookup_valid_ic1 & (((|data_err_ic1) & tag_hit_ic1) | (|tag_err_ic1))`, :585), whose own comment names
the ways without a valid tag as deliberately unchecked. Naming only the second mechanism, as an earlier version of
this paragraph did, is wrong whenever another way hits at that index: the term at :585 is live then, and what keeps the
never-written way out is the mux. Two consequences for the build. The sampler needs no hit-way
input for this bin and cannot compute one, since no injection means no judge ran; the masking holds by construction.
And the qualification above buys a VOLUME bound, at most one sample per line per way, rather than evidence that the
read was checked: what is qualified is the LOOKUP, that the cache was enabled and no sweep was in its grace window.

Bin precedence, stated once so the classifier is a total function. An unqualified cycle classifies as disabled_cache
when the enable term failed and during_invalidation when the sweep term failed, and those win over everything else. On
a qualified cycle with an injection, the injection cases win: unused_way_data when the verdict says another or an
invalid way, masked_duplicate_copy when the flip was masked by the OR of a duplicate copy. uninitialised_data_ram
applies only to a qualified cycle with no injection. No sample carries two of these.

Intent anchor: rtl/ibex_icache.sv:580-584 says no data-RAM initialisation is done on reset, so unused data, in
particular the ways without a valid tag, may carry incorrect ECC, which is why the never-written way's data is
never decoded at all: the mux feeds the decoder only the matching ways (:507-514 into :568-573) and, with no match at
all, the term at :585 is masked. A QUALIFIED lookup reading a never-written line and raising no alert is therefore a
real no-alert case that the DUT's own comment predicts, and not a TB artefact. The word qualified is deliberate here
and throughout: it names the lookup_actual_ic0 sense, that the cache was enabled and no sweep was in its grace window,
and never the decode sense, which is what "checked" is reserved for.

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

THE ORDER WAS NOT FOLLOWED: I BUILT BEFORE THE RED. This section's TDD line says each new observation gets a red
first, and that is not what happened. The mechanism was built, then the seventeen unit-test cases were written and
passed on working code, and only then were the reds obtained by ablating the mechanism each case tests. A case that
passes on a working build proves the classifier agrees with this plan; it does not prove the case would fail without
the mechanism. That is why every red below is a real failing run from an ablated build with its own identity, and why
none of them is narrated from a passing run.

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
- Mutation-proof, quiet windowing, and the detector is NARROWER than an earlier draft of this section implied. What
  the built cases pin is two pure functions and nothing else: gen_ic_in_window, with cases on all four boundary
  positions (the reference cycle outside, the first cycle inside, the last cycle inside, one past outside), and
  ic_major_nmi_quiet, with cases on a quiet window, a major level in the window, an internal-NMI retirement in the
  window and a window holding no retirement. No case drives a MULTI-CYCLE level history, so the accumulation of
  minor_hi and major_hi over successive cycles is exercised by the evidence runs and pinned by no unit-test case. A
  mutation of the arithmetic fails those cases in any run that reaches the self-test through GEN_CMD_FCOV_SELFTEST,
  with its ablation control; a mutation of the history accumulation would not.
  THE RESIDUAL, stated rather than covered: a mutation of the SPAN ARGUMENT at a call site, passing the window
  constant less one, is caught by NOTHING this build carries. The boundary cases test the arithmetic, not the
  constant handed to it, and a wrongly hit bin is invisible to a manifest, which fails only an unhit declared bin. The
  only independent witness would be a legitimate major alert landing inside the window, which is stimulus-dependent.
  The exposure is narrower than it sounds, because a high alert_major_internal_o is already an unconditional error in
  the misc monitor (gen_checkers_pkg.sv:474), so the only major output that can legitimately be high inside a window
  is the bus one under an announced corruption. The gap is named here so the mutation table says what it does not
  cover.
- fcov-expectation. NINE PER-ENTRY MANIFESTS, one per WP-8 icache ECC testlist entry, each stem equal to its entry
  name, each declaring only the bins its own entry can hit with an anti-vacuity note per bin. DECLARED, BOUND AND
  EXERCISED. At the landing itself nothing enforced them: the flow binds a manifest only through the entry's
  fcov_expectation_file, every WP-8 entry still carried null there, and the sweep's 27 OK counted these nine as
  present-but-unbound files. The Runtime Manager's landing-25 merge, commit 28c8c0b, commits all nine bindings, so
  each entry names its own manifest and a run of that entry is gated by it. The exercising run then ran all nine
  unmeasured with coverage on, from the committed tree at 813994b at build identity b48479a3bc6f1d9f, one fresh
  output directory and coverage database per entry: nine of nine PASS and 78 of 78 declared bins HIT, per entry 7,
  10, 10, 7, 10, 11, 9, 8 and 6. The Runtime Manager read them with its own parser of the coverage report and
  cross-checked bin by bin against the expectation checker's keyed output rather than reading a verdict line. Its
  earlier shared-root run of the same nine is a cross-check on the isolation, and this plan over-claimed it: when the
  run log committed, that per-bin agreement rested on two entries of the nine. The corrigendum log,
  gen_l25_fcov_exercised_corrigendum.log at aaff8f5, measures it on all nine, 78 declared bins compared and 78
  identical in both forms with eighteen reports each holding exactly one test, so the isolation is settled by
  measurement now and cited rather than asserted. So every declared bin here has now been enforced by a run and
  none read unhit. The run's
  record is dv/auto_dv/evidence/gen_tdd_logs/flow/gen_l25_fcov_exercised.log, committed at 8f265b2, which carries the
  verdicts, the per-entry keyed reading and the owed-bin table. The counts in the notes remain the local figures; the
  counts that record reports as NUMBERS are the six owed-bin figures, and those agree with the local ones exactly, so
  the comparison of all 78 counts waits for the per-bin figures rather than being claimed here. WHAT THE RUN DOES NOT
  ESTABLISH, in that record's own words: that a declared-but-unhit bin fails a run, since no entry missed a bin it
  declared. The failing direction is evidenced elsewhere, by the landing-23 mutation reds in
  gen_fu_l23_wp8_cov_reds.log, where a mutation drove a declared bin from HIT to UNHIT and the checker named it; that
  was a direct invocation, so what remains unexercised is a FLOW run failing on an unhit declared bin. ALL NINE ARE EXERCISABLE unmeasured: the flow's refusal keys on the measured
  flag alone and never on coverage (dv/auto_dv/flow/gen_run.py:193 takes a coverage argument, the clause at :204 reads
  "if measured and debug_only", and its docstring records the widening, since a measured run feeds the credit report
  whether coverage is on or not), which the Runtime Manager and I each evaluated on all nine entries: zero refusals
  unmeasured with coverage on, and exactly the four probe-carrying entries refused when the flag is forced. What the
  probe knob does cost is PROMOTION, not this run: _data, _data_two, _both and _far_data cannot become measured
  entries while gen_probe_ic_lookup stays in their plusargs, which is the case P6 exists for. A group manifest was
  tried first and cannot work: the expectation check validates the manifest's test against the ENTRY NAME before it
  reads coverage, so one manifest naming one test fails every entry with a protocol error before the covergroup is
  read, and no merged check across entries exists. Per-entry is also the better shape, because a declared-but-unhit
  bin then means something for the entry declaring it.
  The union reachable today is 15 of 15 across nine entries; the nine manifests declare the robust subset of 13 bins,
  robust meaning a structural bound or a measured count of at least 30 in that entry's own run; OWED are two bins,
  both thinly hit and closing on one route, a seed sweep at coverage closure: cp_no_alert_case.during_invalidation
  (10, 9, 22) and cp_no_alert_case.masked_duplicate_copy (4, 2, 14). The exercising run reproduced those six figures
  exactly, entry for entry, so both bins are hit today and both stay owed under the robustness rule, since the
  highest single-entry count is 22 and 14 against a threshold of thirty or a structural bound; both peaks are in the
  both-injection entry, which is therefore the one to sweep. Separately and NOT owed, two per-entry exclusions
  live in the manifest headers rather than here, since the bin is robust elsewhere and thin only on those entries:
  cp_no_alert_case.uninitialised_data_ram on the two far-program entries (9, 9) and cp_alert_pulses.one on the far
  probe-off entry (27). The counts are measured per entry in its own output directory through the local
  runner at that entry's own program and plusarg set, never through the flow, so no run's coverage contributed to
  another's. One entry's first measurement carried a plusarg its testlist entry does not, the lookup probe; it was
  re-measured with the probe absent and all fifteen bin counts came out identical. cp_knob's three rendered bins are in no manifest, since they have no CSV rows, and the
  four part-2 coverpoints appear in NO manifest.
  The ninth entry is what makes the union complete. There is no knob for the cache enable, it comes from the program
  writing cpuctrlsts, and the ECC directed program enables it in its first instructions, so none of the other eight
  can reach cp_no_alert_case.disabled_cache. The ninth runs the tag-injection knob against a program that never
  writes that CSR, and the bin comes out at 864: structural, since every injection in that run lands on a cycle the
  scoreboard sees as disabled. Its testlist entry is staged for the Runtime Manager, whose file the testlist is.
  A defect in the shared expectation checker is recorded as owner item LOG-084 and does NOT affect these manifests.
  Its report parser recognises only urg's per-coverpoint heading, so on a DIRECT invocation against a raw report no
  cross-bin key is produced and a cross bin's count is attributed to the group's last coverpoint, which would let a
  declared coverpoint bin read as HIT because a cross bin of that name was hit. LOG-084c narrowed the scope: the
  flow's measured path derives a variable-form report whose cross sections are named by the component tuple, so cross
  bins are keyed on the path these entries actually run through. Evidence for the owner is retained as
  gen_fu_l23_fcov_checker_cross_bins.log.

## 8. What is announced, to whom, and what else WP-8 contains

Every coverpoint, cross and Sample line this work touches goes to the Orchestrator and the Test Writer before it
lands, per the assignment, and the three normalised lines of Section 1 plus the Sample-line qualifiers are the plan
owner's own touch, announced the same way, and it is committed at fa3fb77: the group's section carries the
checked-lookup qualification, the written-flag description per line, the no-alert precedence order, the per-signal
quiet windowing and a build-split paragraph of its own. The split it records is EIGHT sampled and FOUR passing
not-applicable, which is the state after part 1 builds two of the six observations that were unbuilt when the split
was first sized six-and-six by observability alone. One wording item WAS owed back to it, the word-versus-line
granularity of Section 5, and v4g took it at fa3fb77; nothing in that section disagrees with this plan.

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
| L-1, the zero-hits sentence | Section 5, first paragraph: an identifier claim with the measurement and its control |
| L-2, cp_knob's three bins | Section 2: the render total and the manifest total stated separately |
| L-3, the WP-8 row of the test plan | Section 8: the export rows and the digest guard placed outside this split |

## 11. Where each row of the re-review is answered

| row | answered in |
|---|---|
| CM192-M-1, the bypass queue had no drain point | Section 5: two drain sites beside the existing per-cycle and final passes, the 512-event arithmetic bound, and an eviction count in the GEN_MISC summary |
| CM192-L-1, the `: values` counts | Section 1: the counts re-measured on joined bullets, anchored at 61c1a1a where two definitions of the group set agree, with the reconciliation table that makes every figure anyone quoted reproducible |
| CM192-L-2, the second mutation's detector was stimulus-dependent | Section 7: replaced by a GEN_FCOV_UT case on the two queue sizes |
| CM192-L-3, stale status sentences and the appended line count | Section 1: the prerequisite cited at fa3fb77, the granularity sentence dropped, 66 lines |
