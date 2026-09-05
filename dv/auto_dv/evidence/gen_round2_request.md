# Round-2 request: the second measured coverage run (acceptance form)

DV Lead request to the Runtime Manager, copied to the Orchestrator. It states what round 2 selects, how many
seeds each entry runs and why, what the round costs, what each entry is expected to do, and what acceptance
means. It is submitted before the round and reviewed before dispatch.

Round 1 is the team's first measured coverage run: evidence `dv/auto_dv/evidence/gen_round_0`, regression tag
`round_1`, pinned at 4a00702, outcome 53 of 53 runs clean and 36 of 36 fcov checks passing. Its records are
`gen_round1_credit/`, `gen_round1_promotion_table.md` and `gen_round1_covergroup_set.md` at 0203c6e.

THE ONE THING THIS FORM DECIDES THAT ROUND 1 DID NOT. Round 1 ran three seeds per measured entry because
three is what the entries already declared. This form does not inherit that. It asks for a rule that ties an
entry's seed count to evidence, applies the rule per entry, and states what the answer costs.

## 1. Scope, and what the round selects

`gen_round.py --round 2` runs tier full with coverage. Tier full is a rank, not the whole testlist: the
selector keeps an entry when `C.TIER_RANK[t["tier"]] <= rank` over `{smoke: 0, targeted: 1, full: 2}`, and the
check tier is absent from that map with its own branch that only a tier of exactly `check` reaches
(gen_flow_util.py:1618-1631). Derived by CALLING the selector at 0203c6e with base seed 20260904:

| tier | entries | runs | of which measured |
|---|---|---|---|
| smoke | 17 | 47 | 36 |
| targeted | 3 | 9 | 0 |
| THE STATE AT 6407118 | 20 | 56 | 36 |

Restated at this form's own commit rather than at the one where it was first derived: 6407118 selects 20
entries over 56 runs, three more runs than 0203c6e because gen_test_irq_basic entered at tier smoke with
three seeds and measured false, so the measured set is unchanged at 12 entries over 36 runs.

RESTATED AT THIS FORM'S COMMIT by calling the selector again, which is what v2 promised and not a stored
list. Called at 9c28944 with base seed 20260904:

| tier | entries | runs | of which measured |
|---|---|---|---|
| smoke at 9c28944 | 17 | 47 | 39 |
| targeted at 9c28944 | 3 | 9 | 6 |
| THE ROUND'S PLAN AT 9c28944 | 20 | 56 | 45 |

The measured set moved from 12 entries over 36 runs to 15 over 45 because the three PMP entries flipped to
measured, which is the PMP step-1 landing v2 named in its round-2 scope. Fifteen manifests are named and all
fifteen validate: gen_fcov.py's own validate_manifest returns no error for any of them, and their declared
sets total 3171 bins.

THE 6407118 TABLE ABOVE, and not the restated one, is the state at that commit rather than the round's
plan. Round 2's entry set is whatever the selector returns
at the round's own commit, and the round-2 scope (LOG-097) expects these to land first: PMP step 1 (four
covergroups and the flip of `gen_test_pmp_csr_warl`, `gen_test_pmp_mseccfg` and `gen_test_pmp_lock` to
measured), IRQ step 1 (four covergroups, a new owning entry and its manifest), the generator fixes, the
LSU/ECC/timing shapes, and the manifest-semantics change. The selector is called again at the round's commit
and this section is restated from that call before dispatch; no stored list is used.

THE GATING CONDITION IS NOT THE MEASURED SET. gen_round indexes a round only when the regression is clean,
where clean counts fail plus timeout plus not_run over ALL selected runs. One unmeasured run can refuse the
round while contributing nothing to the coverage merge, so this form states an expected outcome for every
selected run.

## 2. Base seed, pinned

`--base-seed 20260905`, and it must be passed. Without it gen_regress sets the base from the dispatch start
time (`gen_regress.py:613-614`, `a.base_seed = int(start) & 0x7FFFFFFF`), which makes the round's seeds
unreproducible. 20260905 is chosen because it is already measured as disjoint from round 1: the round-1 form
recorded that 0 of the 36 measured seed values at base 20260904 are shared with base 20260905. Re-derive that
over the round-2 plan before dispatch, because the plan's entry set will differ.

## 3. Seed counts: the rule, and the measurement that decides it

### 3.1 The rule I am asking the round to adopt

    An entry's seed count in a measured round may not exceed the number of seeds
    its fcov manifest has been measured over.

A manifest is a PER-RUN guarantee: every declared bin must be hit in every run. The round-1 declared sets were
built by REMOVING exactly the bins that missed within three seeds, so they are calibrated to three seeds by
construction. Raising the seed count without re-measuring the manifests does not make the round a better
measurement; it makes it a wager on 2895 declared bins that nobody has priced. Section 3.2 prices it.

The rule already exists for new entries, where it is stated as the 40-seed manifest measurement. This
generalises it to entries that already exist.

WHAT THE RULE NEEDS BEFORE IT CAN BE ENFORCED, and it does not exist today. I called this rule checkable in
the first version of this form and that was wrong: nothing in the tree records the number it reads. The 27
manifests under dv/auto_dv/fcov_expectations/ carry `test`, `owner`, `bins` and `anti_vacuity` and no
measurement provenance at all, so today the rule is a policy a human applies, not a gate. Two things close
that, and neither is mine:
1. A manifest field, `measured_seeds`, recording the seed count the declared set was measured over and the
   commit that measured it. The Test Writer owns the manifests and the 40-seed sweep that would fill it.
2. A comparison that refuses a measured round when an entry's testlist `seeds` exceeds its manifest's
   `measured_seeds`. That belongs in the testlist loader or in gen_regress beside the other fcov policy
   checks, and it is a FLOW item owed by the Runtime Manager's next plan, not by this form.
Until both exist, treat the per-entry counts in 3.3 and 3.5 as a decision this form records and a reviewer
checks by hand, not as one the flow enforces.

### 3.2 How much margin each declared set actually has

Round 1 passed 36 of 36 fcov checks and 8685 of 8685 bin checks, every bin HIT, none missing from any run. That
is the whole of what a pass tells you, and it is not enough to decide a seed count. The round's manifest also
records the HIT COUNT of every declared bin in every run, so the margin can be measured instead of assumed.

For each declared bin I took the SMALLEST hit count it reached across the entry's three runs. A bin whose
smallest count is 1 occurred exactly once in the thinnest run of the three: it passed, with no margin at all,
and nothing in the round establishes that it occurs in a fourth run.

| entry | declared bins | bins hit exactly once in their thinnest run | share | median smallest count |
|---|---|---|---|---|
| gen_test_csr_access | 4 | 0 | 0.0% | 47.5 |
| gen_test_isa_cti | 184 | 1 | 0.5% | 118 |
| gen_test_isa_alu | 563 | 30 | 5.3% | 33 |
| gen_test_csr_trap_setup | 146 | 12 | 8.2% | 13.5 |
| gen_test_cmp_zca | 300 | 81 | 27.0% | 5 |
| gen_test_mul_div | 196 | 55 | 28.1% | 4 |
| gen_test_isa_shift | 120 | 35 | 29.2% | 5 |
| gen_test_cmp_zcb | 96 | 32 | 33.3% | 4 |
| gen_test_bit_ratified | 617 | 276 | 44.7% | 2 |
| gen_test_cmp_zcmp_basic | 325 | 193 | 59.4% | 1 |
| gen_test_rst_boot | 6 | 4 | 66.7% | 1 |
| gen_test_mul_mul | 338 | 244 | 72.2% | 1 |
| ALL TWELVE | 2895 | 963 | 33.3% | - |

963 of the 2895 declared bins, a third of the round's per-run guarantees, were hit exactly once in their
thinnest run. 1327 of them, 45.8 percent, were hit three times or fewer. Four entries carry a median smallest
count of 1 or 2, meaning most of their declared bins have no margin, not a few.

That is the price of a seed rise, measured rather than modelled, and it is why the answer to "run more seeds"
is not simply yes. The supporting arithmetic points the same way: a bin kept because it was hit at 3 of 3
seeds has a 95 percent lower bound on its per-seed rate of only 0.368, since 0.05^(1/3) = 0.368.

### 3.3 The twelve existing measured entries

EIGHT stay at three seeds and may not rise before a re-measurement: cmp_zca, mul_div, isa_shift, cmp_zcb,
bit_ratified, cmp_zcmp_basic, rst_boot and mul_mul, every one of them between 27 and 72 percent zero-margin
bins.

FOUR have real margin and are the pre-flight's priority: csr_access, isa_cti, isa_alu and csr_trap_setup, all
at or below 8.2 percent zero-margin bins, with median smallest counts of 47.5, 118, 33 and 13.5. A 12-seed
pre-flight over just those four costs 12 x 102.9 = about 1234 s of run time (section 4), after which the rule
in 3.1 permits them at twelve seeds. I am not asking to raise them in round 2 ahead of that measurement, and
the split above is what makes the pre-flight small enough to be worth running.

Of the four, csr_trap_setup is the one with a measured payoff rather than a hoped-for one, and it is cheap
to run: csr_trap_setup at 10.0 s per run, against csr_access at 9.7 s per run, which is the cheapest of the
four. It is not the cheapest entry in the round, which is cmp_zcb at 8.2 s per run. Section 5 gives
csr_trap_setup's 0.25-rate bin.

### 3.4 Why the seed-dependent set is not the argument for more seeds

The Test Writer classified every unmet bin of the eight tier-full manifest-naming entries over their three
seeds (gen_r1_preflight_classification.md:22-31). Stable means unhit in EVERY seed; seed-dependent means unhit
in some seed and hit in another.

| entry | declared | seeds | stable unmet | seed-dependent | union |
|---|---|---|---|---|---|
| gen_test_cmp_zcb | 110 | 3 | 6 | 8 | 14 |
| gen_test_cmp_zcmp_basic | 472 | 3 | 74 | 73 | 147 |
| gen_test_isa_alu | 602 | 3 | 6 | 33 | 39 |
| gen_test_isa_cti | 200 | 3 | 16 | 0 | 16 |
| gen_test_isa_shift | 120 | 3 | 0 | 0 | 0 |
| gen_test_mul_div | 224 | 3 | 19 | 9 | 28 |
| gen_test_mul_mul | 338 | 3 | 0 | 0 | 0 |
| gen_test_rst_boot | 8 | 3 | 2 | 0 | 2 |

A seed-dependent bin was HIT at one of the three seeds, so the MERGED report already holds it and it is already
credited; the class-B exclusion reason says exactly that. The 123 seed-dependent bins sit on four entries
(cmp_zcb 8, cmp_zcmp_basic 73, isa_alu 33, mul_div 9); the other two headings in the work list carry zero.

The bins the merge is MISSING are the 123 stable ones of the pre-flight's unmet set, which is the eight
tier-full manifest-naming entries and not the whole declared population, and the Test Writer root-caused those test by test,
each cause covering many bins: compressed branches and `jalr` with rs1 = x0 never emitted (isa_cti, 16);
data-independent timing never enabled, divide-by-zero dividend classes never produced and `c.mul` never
emitted (mul_div, 19); writer-then-x0-read orderings never placed (isa_alu, 6); a `rand` catch-all the program
deliberately avoids, which is a declaration defect (cmp_zcb, 6); the insn-by-rlist-by-spimm product the
stimulus never reaches (cmp_zcmp_basic, 57 of 74); and rst_boot's 2, of which ONE needs an owner ruling on
drivability. The pre-flight record's own Corrigenda (:126-127) withdrew the other half: cp_bit8_readback.zero
has a cause nameable from the TB and needs no ruling, and only cp_boot_addr.zero still stands as written.

Every one of those is decided by what the program generator emits. A different seed does not change it.

### 3.5 The entries that do get more seeds, and why twelve

New or newly measured entries have no per-run history, and their manifests are measured over 40 seeds before
the round under the standing rule, so the rule in 3.1 permits up to 40. I ask for TWELVE:

| entry | round-2 seeds | why |
|---|---|---|
| gen_test_pmp_csr_warl | 12 | flips to measured; new PMP covergroups, never sampled |
| gen_test_pmp_mseccfg | 12 | same |
| gen_test_pmp_lock | 12 | same |
| the new IRQ owning entry | 12 if it flips to measured, else its testlist count | new IRQ covergroups, never sampled |
| the twelve existing measured entries | 3 | sections 3.2 and 3.3 |
| LSU / ECC / timing entries, if they land | see 3.6 | the seed is the only instrument |

THIS TABLE IS A REQUEST, NOT THE ROUND'S PLAN, and Section 7 is what the round is accepted against. The
seed counts here are what I ask the testlist to carry; the testlist does not carry them today, so Section 7's
seed column shows what the selector actually returns and every row of it reads three. Applying this table IS
the testlist touch; doing it without restating Section 7 would leave twelve-seed runs against rows that state
three, and
Section 11 accepts the round against Section 7. If the Runtime Manager lands the seed rise, Section 7 is
restated from a fresh selector call before dispatch and the acceptance follows the restated rows. AND THE
VALUES HERE ARE NOT APPLIED UNTIL THE PROVENANCE FIELD LANDS: Section 7 records that no entry is licensed
above its calibrated count while measured_seeds is absent from every manifest, so this table is a request
waiting on that field and not a path the Runtime Manager may take today.

Twelve is derived, not round. With n seeds and no hit, the 95 percent upper bound on a bin's per-seed rate is
1 - 0.05^(1/n):

| seeds | rate ruled out above | chance of missing a 0.25-rate bin |
|---|---|---|
| 3 | 0.63 | 0.42 |
| 8 | 0.31 | 0.10 |
| 12 | 0.22 | 0.032 |
| 20 | 0.14 | 0.0032 |
| 40 | 0.072 | 0.00001 |

Three seeds rule out almost nothing: a bin unhit at three seeds may still be a one-in-four bin, and one
measured case proves that happens (section 5). Twelve gives the round a conclusion it can act on: a PMP or IRQ
bin still unhit after twelve seeds has a per-seed rate below 0.22 with 95 percent confidence, so it is a
stimulus ask and the triage can be written from the round instead of owed after it. Twenty and forty tighten
the bound and cost little (section 4), so the number can rise without changing anything else in this form;
twelve is where the bound stops moving quickly per seed.

### 3.6 The one case where the seed is the only instrument

A bin whose reachability is decided by the program TEXT can be settled by sweeping the generator, which runs no
simulation at all; that is how the one measured rate in this form was obtained. A bin whose reachability is
decided by TB or DUT timing (bus error injection, ECC error rates, interrupt arrival, grant and rvalid delay
regimes) cannot be, because the generator does not decide it. If the LSU, ECC or timing entries land in this
round, their seed counts are sized to their own injection or regime rate, measured by their owner and stated
here before dispatch. I am not guessing a number for entries that do not exist yet.

### 3.7 Do not pass `--seeds N`

AND THE SEED VALUES OF 3.5 ARE NOT APPLIED BY ANY MEANS UNTIL measured_seeds LANDS, which this section
repeats because a Runtime Manager may read it without 3.5: Section 7 records that no entry is licensed above
its calibrated count while the field is absent from every manifest.

It is not a measured-only knob. `seeds_for_test` takes the override ahead of the entry's own count for every
selected entry (gen_flow_util.py:1634-1638), so the flag also multiplies the unmeasured runs, including the two
one-seed entries whose program image is a fixed assembly file and whose extra runs would compile the same
instruction stream. The lever is the per-entry `seeds` field in the testlist, which is the Runtime Manager's
file. This form requests the values; runtime-2 applies them.

## 4. What the seeds cost, measured from round 1

From the round's own manifest, `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_round_1/manifest.yaml`:

| quantity | value |
|---|---|
| regression wall clock | 362.9 s (21:54:27Z to 22:00:28Z) |
| runs | 53 |
| sum of per-run wall | 940.7 s (measured 689.3, unmeasured 251.4) |
| per-run wall | mean 17.7 s, min 6.6 s, max 69.5 s |

One extra seed across all twelve measured entries costs 229.8 s of run time. One extra seed across the three
PMP entries costs 49.2 s. So the round-2 request above adds 9 seeds on three entries, about 443 s of run time,
which at round 1's observed parallel speedup of about 2.6 is roughly three extra minutes of wall clock.

The point of this section is not that the round is affordable. It is that COST IS NOT THE CONSTRAINT, so the
seed decision has to be argued from what the round can conclude. A uniform rise to twelve seeds on all twelve
existing entries would cost about 2068 s of run time, roughly 13 minutes of wall clock at the same speedup,
and it would still be the wrong thing to do, for the reason section 3.2 measures. A 12-seed pre-flight over
the four entries with margin costs about 1234 s; over the eight without it, about 1523 s.

## 5. What seeds buy, and the only per-seed rate anyone has measured

One bin has a measured per-seed rate. `gen_csr_trap_setup_warl_cg.cr_csr_wpat.mie_msb` was recorded as a
stimulus gap, with the reason "the program never writes this bit pattern to this CSR". The Test Writer then
instrumented the generator's `csr_write` over 40 seeds and found each run emits 180 mie writes with the
operand exactly 0x80000000 in 10 of the 40 seeds. The bin classifies the write operand, not the effective
value, and the rate is 0.25. Missing it at three seeds has probability 0.42, so it is a seed miss and the
committed reason was false.

Two things follow, and the second is the one a reviewer should press on.

First, the population of bins that look stable at three seeds and are not is NOT empty, which is the whole
case for more seeds anywhere.

Second, its size is unknown and this form does not estimate it. Six stable bins were audited over 40 seeds and
one was reclassified. That is not a rate: the six were chosen because their reasons had been written by
READING the generator rather than running it, so they are the sample most likely to be wrong, not a random
sample of that set. Anyone converting 1 of 6 into a projection over the pre-flight's 123 stable bins is reading a
biased sample as an unbiased one. The honest statement is that the population exists, its size is unmeasured,
and the cheap way to measure it is a generator sweep over the stable set rather than simulation seeds.

## 6. Pre-flight owed before any seed rise on the twelve

If the Orchestrator wants the twelve existing entries above three seeds in round 3, the manifests must be
re-measured first, and the measurement is a pre-flight rather than the round:

    gen_regress.py --tests <the measured entries carrying a manifest> --base-seed <the round's base> \
      --source head --head-sha <the landing's FULL 40-character sha> --max-parallel 8 \
      --tag r2_fcov_preflight

Coverage on, no `--purpose 4`, never indexed. Cost from section 4: a 12-seed pre-flight over the twelve is
about 2757 s of run time; a 40-seed pre-flight is about 9191 s. Derive `--tests` by calling the selector at
that commit, and use the full 40-character sha, since an abbreviated one builds and passes and then makes the
round refuse after it has pinned. The pre-flight reclassifies each declared set at the target seed count, the
bins that miss move out under the class-B reason, and only then does the rule in 3.1 permit the rise.

## 7. The measured entries and their expected outcomes

FILLED AT 9c28944. Every figure below is derived by calling the flow's own code at that commit, not read from
a record: the entry set and seed counts from select_tests and seeds_for_test, the declared counts from
gen_fcov.py's validate_manifest, and the built column by resolving each manifest's covergroups against the
rendered set in gen_fcov_groups.svh.

| entry | seeds | declared bins | covergroups built | expected fcov verdict |
|---|---|---|---|---|
| gen_test_bit_ratified | 3 | 654 | 5 of 5 | PASS, every declared bin in every run |
| gen_test_cmp_zca | 3 | 321 | 4 of 4 | PASS |
| gen_test_cmp_zcb | 3 | 87 | 2 of 2 | PASS |
| gen_test_cmp_zcmp_basic | 3 | 319 | 3 of 3 | PASS |
| gen_test_csr_access | 3 | 4 | 1 of 1 | PASS |
| gen_test_csr_trap_setup | 3 | 146 | 1 of 1 | PASS |
| gen_test_isa_alu | 3 | 563 | 5 of 5 | PASS |
| gen_test_isa_cti | 3 | 184 | 3 of 3 | PASS |
| gen_test_isa_shift | 3 | 116 | 1 of 1 | PASS |
| gen_test_mul_div | 3 | 190 | 4 of 4 | PASS |
| gen_test_mul_mul | 3 | 336 | 3 of 3 | PASS |
| gen_test_pmp_csr_warl | 3 | 178 | 3 of 3 | PASS |
| gen_test_pmp_lock | 3 | 41 | 2 of 2 | PASS |
| gen_test_pmp_mseccfg | 3 | 26 | 2 of 2 | PASS |
| gen_test_rst_boot | 3 | 6 | 3 of 3 | PASS |

EVERY MEASURED ENTRY'S COVERGROUPS ARE BUILT, which round 1 could not say: there its two Test Writer entries
included one whose six groups were unrendered, so it expected "declarations missing from the report" as a
designed outcome. No entry expects that here. A group left unrendered would be a defect and not an expected
row, because an unbuilt covergroup fails every seed.

NO ENTRY EXPECTS A FAILURE, and that is a claim this round tests rather than an assumption it makes. Nine of
the fifteen were measured in the wave at 4017573, and six of those nine were RE-RENDERED to that wave's
every-seed set after refusing on declared bins unhit at some seeds; two more, gen_test_pmp_lock and
gen_test_pmp_mseccfg, come from the PMP step-1b block. ONE OF THE NINE IS NARROWER THAN "forty fresh seeds"
AND THIS PLAN'S OWN RULE IS WHAT NARROWS IT. gen_test_bit_ratified declares 654 bins of which 37 were added
on the pair-fix block, a DIFFERENT generator from the one the wave measured, so under the Section 0 rule that
a block is evidence for the generator it measured, the wave covers 617 of its 654 and the pair-fix block
covers the other 37, whose per-bin evidence is Section E of gen_fu_binv_pairfix.log rather than the block's
index. gen_test_pmp_csr_warl IS measured at every one of forty seeds and an earlier sentence of mine said
otherwise. The census reads 40 runs with 40 coverage reports and EVERY 178 of 179 declared bins, the one
exception being a single cross leg at 39 of 40, and the manifest was re-rendered at 9c28944 to exactly those
178. So the current declared set is measured at forty seeds. The 39-of-40 figure belongs to the PMP blocks at
218e9f3 and 4cd3ff6, where the cause was a generator assert producing no program rather than any coverage
refusal, and I carried it here from a message instead of reading the census. The four that were not measured over forty seeds
are gen_test_csr_access, gen_test_csr_trap_setup, gen_test_isa_alu and gen_test_isa_cti, whose declared sets
are the round-1 sets calibrated to three seeds.

THE SEED COLUMN IS WHAT THE SELECTOR RETURNS, and the rule in 3.1 caps it rather than setting it. That cap
is not uniform and the derivation belongs here rather than in a commit message. An entry may not exceed the
seeds its manifest was measured over, so at this commit ELEVEN of the fifteen are capped at FORTY - the nine
measured over forty fresh seeds in the wave at 4017573, plus gen_test_pmp_lock and gen_test_pmp_mseccfg from
the PMP step-1b block - and the remaining FOUR are capped at THREE, those being gen_test_csr_access,
gen_test_csr_trap_setup, gen_test_isa_alu and gen_test_isa_cti, whose declared sets are the round-1 sets
calibrated to three seeds. AND THAT DERIVATION CONFLICTS WITH THE PLAN AS WRITTEN, which this form states rather than resolves in its
own favour: gen_fcov_plan.md Section 0, the "Seeds against the guarantee" rule, says the absent measured_seeds field caps an entry at the count its
current declared sets were calibrated over, and no manifest carries the field today, so under the plan's own
words all fifteen are capped at their calibrated count and NONE at forty. The blocks above are what those
entries were measured over; they are not the field the rule reads. So this paragraph is the evidence for a
future cap and not a licence for Section 3.5's twelve, and the licence arrives when the field does. THE CAP
IS APPLIED BY HAND TODAY: the plan places it in a single testlist-header value beside
fcov_manifest_required_tiers (the same Section 0 rule), and that value is absent from gen_testlist.yaml:59,
so nothing in the flow reads it and a reviewer checks this by hand until it exists. Until that lands the
rows above are the plan, and this section is restated from a fresh selector call if it does.

TWO OPEN ITEMS THIS FORM DOES NOT CLAIM. The hart_id plusargs on gen_test_csr_access and gen_test_rst_boot
are an ask of mine rather than an item any record owes, so no row above claims them and the round does not
depend on them. And the coverage criterion remains with the owner: this form does not state one.

THE FIVE UNMEASURED ENTRIES of the twenty carry a null fcov_expectation_file and are selected for their runs
rather than their coverage: gen_boot_zc, gen_test_bit_draft, gen_test_csr_reset, gen_ut_lockstep, and
gen_test_irq_basic. The irq entry is unmeasured DELIBERATELY and stays so until the six conditions below are met, which
this form records rather than re-argues, each with its status at this commit.

| # | condition | status |
|---|---|---|
| a | the irq_entry checker item classified and fixed | fixed at b9e5fad; rev60 APPROVE-WITH-CHANGES with rows owed; the Critic's re-verdict REQUEST-CHANGES confined to one records sentence; OPEN on the gating record: gen_critic_irq_checker_fix.md for 65b7cb0..b9e5fad still reads REQUEST-CHANGES confined to M-3, and the only record of the lift is a clause in the Critic's form verdict at 55d784a, which is not that artifact. The append to the gating record is requested; this row says CLOSED and names that record when it lands. rev60's rows are owed inside fix 3 |
| b | its red fixture RED-OK at three of three rather than masked | CLOSED at 67c6ac1: the three seeds re-run on a b9e5fad build read 3 of 3 RED-OK with zero irq_entry firings, beside the earlier block with its records untouched |
| c | the fixed cocotb timeout in the stimulus path replaced by a seed-independent bound | CLOSED: fixed at 6b894ab, rev64 APPROVE-WITH-CHANGES at 348e4ae with its rows at 2c63b83, no re-review owed |
| d | a fresh forty-seed sweep at the fix commit with its manifest rendered FROM that sweep | open |
| e | a regime-independent end-of-test expectation covering the case a per-record bound cannot judge | open, and LOAD-BEARING rather than provisional: the storm-regime vacuity closes only by that reconciliation |
| f | no run of the entry wedges the core | open: one wave run diverges from the model 6447 cycles before its first checker fire (the cited record read 6443; the figure here is re-derived from the run, and the corrigendum landed at 29daef3 where gen_chkfix_reruns/gen_index.md:80-85 now reads 6447), with 23387 instruction mismatches already reported and the core executing zeros |

CONDITION (b) HAD REOPENED ITSELF UNDER THIS PLAN'S OWN RULE, which is worth keeping rather than quietly
dropping now that it is closed. Section 0 says a block is evidence for what it measured and no other; the
reds had been measured on one build and the fix had moved, so that evidence certified a build the round would
not run, and the re-run at 67c6ac1 is what closed it. That is not the manifest rule by analogy: a red
measures the CHECKER against the stimulus, so a checker change alters the thing that was measured even though
the stimulus is byte-identical, which is the same reasoning reaching a different half of the pair.

CONDITION (f) IS NOT A FOOTNOTE TO (a). A wedged run's coverage measures nothing and its failures mask every
other signal in it, so no promotion can rest on a run set containing one. Whether the wedge is a design
finding or a testbench one is being classified and does not change the condition.

Three of the six are open at this commit, and the round runs the entry unmeasured, exactly as the wave did.

## 8. Standing gates, named

Unchanged from round 1 and enforced by the Runtime Manager: P6 (no debug_only knob in a measured run),
LOG-067 (the B8 probe knob off in every measured run), LOG-077 (an ICache ECC error rate at rare or frequent
only with the alert-minor checker on), and the fcov_expectation_file loader rule (non-null under
fcov_expectations, stem equal to the entry name for a measured entry).

## 9. The canary requirement

A measured round pins the live HEAD at dispatch and refuses without `--canary-build`, accepting only a
head-mode build of exactly that commit with a covergroup declared. The canary is built with the FULL
40-character sha: an abbreviated one builds and passes the canary check and then makes the round refuse after
it has pinned.

## 10. What the credit tool will read

`gen_round_credit.py` reads the round's regression manifest and sim logs against the plan, and its record for
this round is written with `--label`-free explicit paths and `--heading-id`, as round 1's was. The heading id
for round 2 is added to the HEADINGS table in the same landing that writes the record, so the record cannot
name a heading the tool does not carry.

## 11. Acceptance

The numbers in this form are checked by dv/auto_dv/tools/gen_round_form_check.py, which parses each claim
it covers out of this document and recomputes it from the round's committed regression manifest, the
pre-flight record or arithmetic; it covers the claims listed in its run_checks and not every numeral here,
and it says so.

The round is accepted when every selected run is clean, the merge and the fcov checks complete, every measured
entry meets the expectation stated for it in section 7 on all of its runs, and the credit report, promotion
table and covergroup set are regenerated at the round's commit under the round-2 record label. A failing run
of either selected tier refuses the index, so an unmeasured run is a round blocker and not a footnote. A
check-tier failure is not: the round does not select that tier.

The round does NOT claim the functional gate. The gate's functional condition has two parts, both required,
and the second is traceability completeness confirmed by a reviewer other than the author. This form governs
the first part's measurement only.
