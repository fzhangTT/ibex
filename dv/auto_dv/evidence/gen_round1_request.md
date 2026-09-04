# Round-1 request: the first measured coverage run (acceptance form)

Requester: DV Lead. Purpose 4 (Phase 1 gate or closure round). Owner directive LOG-085; manifest-scope ruling
LOG-086 (a69e285) and its addendum. Queue file: dv/auto_dv/work/runtime/requests/dv-lead-001.yaml.

Every figure below is measured at a named commit and re-derived by me, not relayed. No blank remains: the
LOG-086 detach is 18ac053, landing 38 is 9baf3f9, landing 39 is 726682a. LOG-088 (7f61cd1) detaches six more
measured entries after runtime-2's fcov pre-flight, so the round checks two entries and counts thirteen; that
ruling's testlist edit is not committed yet and section 5 says what waits on it. The scope figures were WRONG in this form's
first version, which said 103 entries and 141 runs; that is the whole testlist, not the round's selection.
runtime-2 caught it with the flow's own selector, the LOG-086 corrigendum at 7e3ecc8 records it, and every
scope figure below is re-derived by me the same way at e641b24. The testlist has not moved since the detach
at 18ac053, so the selection holds from there to the round's HEAD.

## 1. Scope, and what the round refuses

`gen_round.py --round 1` runs tier full with coverage. TIER FULL IS NOT THE WHOLE TESTLIST. The selector
(gen_flow_util.py:1609-1622) keeps an entry when `C.TIER_RANK[t["tier"]] <= rank`, over TIER_RANK
`{smoke: 0, targeted: 1, full: 2}`; the check tier is absent from that map and has its own branch at :1616,
`if tier == C.CHECK_TIER`, which only a tier of exactly `check` reaches. So tier full selects the smoke and
targeted entries and no check-tier entry. Derived at e641b24 with that selector, at base seed 20260904:

| tier | entries | runs | of which measured |
|---|---|---|---|
| smoke | 16 | 44 | 42 |
| targeted | 3 | 9 | 3 |
| THE ROUND | 19 | 53 | 45 |
| check, NOT selected | 84 | 88 | 0 |

The other way to say it: 45 measured runs (15 entries at 3 seeds) plus 8 unmeasured runs, the 8 being 2 in
smoke at one seed each and 6 in targeted.

THE ROUND'S GATING CONDITION IS NOT THE MEASURED SET. gen_round indexes a round only when the regression is
clean, where clean means zero failing runs and failing counts fail plus timeout plus not_run, over all 53.
So any one of the 8 unmeasured runs can refuse the round while contributing nothing to the coverage merge.
This request therefore states an expected outcome for all 53 runs, and for nothing outside them: an entry the
round does not select cannot pass or fail it, whatever its state in the tree.

## 2. Base seed, pinned

`--base-seed 20260904`, ruled by the Orchestrator. Without it gen_regress defaults the base to the
dispatch's start time, which makes the round's seeds unreproducible. Re-derived by me over the round's own
53-run plan at e641b24: 53 distinct seed values and 53 distinct entry-and-seed pairs, zero collisions, the
same list on a second call, and 0 of the 45 measured values shared with base 20260905, so the base is
load-bearing. (runtime-2's equivalent figures were 141 and 141 because they covered the whole testlist.)

## 3. Seed counts, and why three

Every measured entry carries `seeds: 3` in the testlist, which gives the 45 measured runs. Three is the
round-1 baseline I am asking for: it is what the entries already declare, it gives every measured entry a
program-image spread (see section 4), and it keeps the LSF bill at 53 runs.

DO NOT pass `--seeds N`. It is not a measured-only knob: `seeds_for_test` (gen_flow_util.py:1625-1629) takes
the override ahead of the entry's own count, for every selected entry. Derived over this selection, `--seeds
3` makes the plan 57 runs with the same 45 measured, the four extra runs being the two one-seed smoke entries
going to three; `--seeds 5` makes it 95 runs with 75 measured. If round 2 wants more measured seeds, the lever
is the per-entry `seeds` field, not the round flag.

## 4. Randomization sources, per entry

Measured from the run banners rather than read off the testlist, because the drawn set cannot be read off
the testlist:

1. The seed regenerates the program image. Every measured entry carries `program: {seed: run}`, so the
   instruction stream differs per seed. runtime-2 measured gen_test_rst_boot at two of its own round-1
   seeds: different program sha256, different crc32, 249 words against 297.
2. The seed draws every regime knob the entry has not pinned. The banner reads `regime_sched=derived`; the
   same entry drew imem_gnt_delay random against same_cycle, imem_rvalid_delay random against long,
   irq_regime quiet against sparse, and its grant count moved from 174 to 250.
3. An entry's pinned knobs NARROW the draw rather than randomize it. The 15 measured entries pin none: every
   one carries only `+gen_fetch_en_at_reset=0` and the banner reads `pinned=-`. So no stress axis is off for
   the measured set, and none is pinned on either.

Two of the round's entries run at one seed, gen_boot_zc and gen_ut_lockstep, both smoke and both unmeasured,
and for them the seed is inert: each carries `program: {directed: [dv/auto_dv/stim/gen_directed/
gen_zc_directed.S], seed: 1}`, a fixed assembly image with the program seed pinned, so a second run seed
would compile the same instruction stream. One is the boots-and-retires milestone on that program and the
other the lock-step comparator against the Spike shim over it. The check tier's own seed shape is not this
round's concern, since the round does not select it.

## 5. The measured entries and their expected outcomes

All 15 measured entries run and all 15 contribute coverage. What moved twice today is how many of them can be
CHECKED against their manifest, and the second move is measured rather than structural.

LOG-086 detached nine entries on a structural ground: a manifest declaring a covergroup that does not exist
FAILS the run at every seed. Seven of the nine are measured and became counted-only; the other two are the
unmeasured targeted entries of section 6.

LOG-088 then detached six more, on evidence. runtime-2 flew the eight surviving checked entries as a
pre-flight before dispatch, and 18 of those 24 runs came back with declared bins unhit. Re-derived by me from
the pre-flight's own manifest rather than from the relay
(/proj_soc/user_dev/fzhang/ibex_dv_out/regress_r1_fcov_preflight/manifest.yaml, tag r1_fcov_preflight, status
done, head-mode source root .../ibex_dv_mirror_head/726682a, coverage on, base seed 20260904): fcov totals
checked 24, pass 6, unmet 18, unverifiable 0. THE PRE-FLIGHT RAN THE ROUND'S OWN SEEDS. I derived each
entry's three seeds from the testlist at base 20260904 and compared them entry by entry with the manifest's:
all eight match. So this is a prediction of the round, not an analogy to it, and dispatching the eight
unchanged would have produced a refused round with no record.

| entry | declared | unmet per seed | unmet, union | unmet at EVERY seed | round 1 |
|---|---|---|---|---|---|
| gen_test_isa_shift | 120 | 0/0/0 | 0 | 0 | CHECKED |
| gen_test_mul_mul | 338 | 0/0/0 | 0 | 0 | CHECKED |
| gen_test_cmp_zcb | 110 | 8/8/10 | 14 | 6 | counted-only |
| gen_test_cmp_zcmp_basic | 472 | 112/119/116 | 147 | 74 | counted-only |
| gen_test_isa_alu | 602 | 19/22/24 | 39 | 6 | counted-only |
| gen_test_isa_cti | 200 | 16/16/16 | 16 | 16 | counted-only |
| gen_test_mul_div | 224 | 22/23/24 | 28 | 19 | counted-only |
| gen_test_rst_boot | 8 | 2/2/2 | 2 | 2 | counted-only |

The union and every-seed columns are mine, computed over the three per-run unmet sets, and they carry the
finding LOG-088 hands me for after the round. Over the six failing entries there are 246 distinct unmet bins
and the split is exactly even: 123 are unmet at EVERY seed and 123 at some seeds only. The even half that is
stable cannot be seed luck. It is a declaration or a stimulus defect, and the examples read that way:
gen_isa_branch_cg.cp_op.c_beqz and c_bnez unmet in every isa_cti run (the compressed branch forms never
appear), gen_div_timing_cg.cp_dit.on in every mul_div run (data-independent timing is never turned on),
gen_rst_boot_cg.cp_boot_addr.zero and gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero in every rst_boot run. The
seed-dependent half is the other question, whether a manifest states what a run guarantees or what a round
accumulates; the flow's check is per run today, so under the current rule those bins do not belong in a
per-run declaration at all. Both questions are first items after the round record is reviewed, not round-1
work.

CHECKED against their manifests (2 entries, 6 runs): gen_test_isa_shift and gen_test_mul_mul, 458
declarations between them, all distinct, over 4 covergroups (gen_isa_shift_cg, gen_mul_ops_cg,
gen_mul_timing_cg, gen_cmp_zcb_cg), every one rendered in dv/auto_dv/env/gen_fcov_groups.svh. Expected: PASS
with the expectation MET, on all three of each entry's round seeds. That expectation is measured, not argued:
those are the six passing runs of the pre-flight, at the seeds the round will use.

COUNTED-ONLY (13 measured entries, 39 runs): the seven of LOG-086 (gen_test_bit_draft, gen_test_bit_ratified,
gen_test_cmp_zca, gen_test_csr_access, gen_test_csr_reset, gen_test_csr_trap_setup, gen_test_pmp_csr_warl)
plus the six of LOG-088 in the table above. Expected: PASS with NO expectation check. For the LOG-086 seven
that holds at 18ac053 already; for the LOG-088 six it holds once runtime-2's field edit is committed, and
until then the round must not be dispatched, because each of those six fails all three of its seeds.

One correction to the relay, and one to my own first version. gen_test_pmc_ctrl reads `tier: check`,
`measured: false`, `fcov_expectation_file: null` at e641b24, so it is not in the round at ALL: the tier keeps
it out before the measured flag is read. The measured set is 15 and now splits 2 checked plus 13
counted-only, and the "seven plus gen_test_pmc_ctrl" wording of the relay and of the 18ac053 subject is right
in count and wrong in composition.

WHAT THE DETACHES COST AND DO NOT COST: they remove the per-entry expectation CHECK for thirteen entries, and
they remove no coverage. Those runs still sample every covergroup they hit, and round-1 credit reads the
merged coverage report and the plan rather than the manifests, which I verified for the pmc case: the eight
CG-PMC groups sit in my traceability CSV as 1019 PLANNED bin rows, none of them rendered, and my credit
report names neither them nor their 204 declarations.

WHAT THE DETACHES MOVE, re-derived by me and not taken from the relay. Before LOG-086, at ede678c, 27 entries
named a manifest and the declared set was 3902 distinct bins, 3167 of them on built covergroups. After it, at
18ac053, 18 entries name a manifest and the declared set is 2066 bins, ALL on built covergroups. LOG-088's
six move it again, and that figure is a PROJECTION until runtime-2 commits: with the six fields nulled inside
an archive of 7f61cd1, exactly the edit the ruling directs, gen_covergroup_set.py reports 5 covergroups, 471
distinct referenced bins and 12 manifests, every group rendered. So 1595 further distinct bins leave the
declared set, all of them on covergroups that DO exist. I will re-derive it on the committed testlist and the
round record will carry that figure, not this one.

Two consequences the round record must state plainly. First, any percentage taken over the DECLARED set moves
for bookkeeping and not because coverage fell: the withdrawn bins are still sampled by the runs that hit them
and still credited, since credit reads the merged report and the plan. A reader comparing declared-set
percentages across rounds will otherwise read a bookkeeping change as a regression. Second, the round's
expectation evidence is now six runs over two entries, and 246 unmet declarations over six others are a
round-1 finding about the declarations rather than about the DUT.

## 6. The unmeasured runs (8), and what the round does not select

The round's four unmeasured entries, 8 runs, every one of them able to refuse the round:

- gen_boot_zc (smoke, 1 seed) and gen_ut_lockstep (smoke, 1 seed): PASS. No manifest, no expectation check.
- gen_test_pmp_mseccfg and gen_test_pmp_lock (targeted, 3 seeds each): PASS with no expectation check, their
  manifest fields nulled at 18ac053; their manifests declare 77 of 77 and 50 of 50 bins on unbuilt
  covergroups, which is why they are in LOG-086's nine.

Coverage is on for all of them, which matters for one entry that is NOT in the round and would otherwise be
read as a round-1 risk. gen_regress.py:615 sets `coverage = not a.no_coverage and not a.repro`, and
gen_round.py:40-58 builds that argv with neither flag on any branch, the measured branch passing --tier full
--purpose 4; each run then takes --cov-dir (:110-113), an unmeasured one the build's unmeasured vdb. So no
round-1 run is coverage-off.

WHAT THE ROUND DOES NOT SELECT, and therefore what this request states no expectation for: every check-tier
entry, 84 of them at 88 runs. That includes the red fixtures and the standing guard
gen_ut_lockstep_icache_ecc_fcov_red, gen_test_pmc_ctrl, the three storm-regime entries, and the two entries
this afternoon's landings fixed. Those fixes stand on their own and a check-tier regression is what exercises
them; the round neither proves nor needs them. For the record, since the earlier version of this form claimed
their outcomes: the storm entries were a TB livelock in the debug-request driver rather than a timeout bound,
fixed at 1deec4c; gen_ut_intg_store was an end-of-run read race in the TEST, fixed at landing 38, 9baf3f9;
and gen_ut_lockstep_icache_ecc_tag_two is fixed at landing 39, 726682a, whose allowance is keyed on the alert
window against the last observed cycle rather than on landing 37's retirement proxy, which the Critic
rejected and this form does not cite. The RTL is why the proxy failed: at rtl/ibex_icache.sv:585,
`ecc_err_ic1 = lookup_valid_ic1 & (((|data_err_ic1) & tag_hit_ic1) | (|tag_err_ic1))`, the DATA half carries
`& tag_hit_ic1` and the TAG half carries no hit or consumption term at all, so a corrupt tag word raises the
error on EVERY valid lookup whether or not its way hits. Its consumed-versus-retired probe is still owed and
is not a round-1 item. LOG-087 rules the guard's coverage-off NOT_RUN by design, so a coverage-off check-tier
gate run fails on the guard; that is a separate run from this round and not a blocker for it.

## 7. Standing gates, named

- P6: a debug_only plusarg enabled in a measured run is refused (gen_run.py measured_refusal at :224-244, on
  the measured flag alone with no coverage term). The testlist declares seven such knobs.
- LOG-067: gen_chk_sva_b8 off in every measured run; the canary reports both B8 probe defaults false.
- LOG-077: a measured run with +gen_knob_icache_ecc_err_rate at rare or frequent counts only with
  +gen_chk_alert_minor on.

All three are one function, so I put all 19 round entries through it rather than reading the entries: at
e641b24, `measured_refusal(entry, [], testlist, entry's measured flag, coverage=True)` returns None for every
one, 0 refusals over 19. Two controls prove the call is live rather than vacuous: the same call on
gen_test_rst_boot with `+gen_dbg_csr_probe=1` returns the P6 refusal and returns None when the run is
unmeasured, and with `+gen_chk_sva_b8` it returns the LOG-067 refusal. The 15 measured entries carry exactly
one plusarg each, `+gen_fetch_en_at_reset=0`, which is how they pin nothing (section 4).

## 8. The canary requirement

The flow refuses a measured dispatch without a head-mode canary build at the round's HEAD (LOG-046a).
runtime-2's canary at b105c09 read identity 3ecd04b3f9dc0734, covergroups_declared true, both B8 probe
defaults false, and the dispatch gate accepted it at rc 0 while refusing a wrong pinned sha at rc 2, so the
accept is a measured result rather than a default. The canary for this round is rebuilt at ROUND_HEAD, and it
must not report that identity: landing 39 edits dv/auto_dv/env/gen_checkers_pkg.sv, which gen_tb.f names at
line 26, so the identity moves with it. Recomputed from archives of the two commits with the committer's own
tool (gen_build_identity.py --root, the filelist_digest over gen_rtl.f and gen_tb.f and the 117 sources they
name), landing 39 at 726682a reads bc0cd7778e382b13, its parent 3cabc7e reads 6a1d73dfb815cfc7, and landing
38 at 9baf3f9 reads 6a1d73dfb815cfc7 as well, each checked with --expect at rc 0 rather than read off a
neighbour. That is how section 11's claim stands: landing 38 left the build identity where it was, landing
39 moved it, and `git log 9baf3f9..726682a -- dv/auto_dv/tb dv/auto_dv/env dv/auto_dv/isa rtl` lists
landing 39 alone. A canary reporting 3ecd04b3f9dc0734 is a stale build, not this round's.

## 9. What the credit tool will read

gen_round_credit.py reads the round's regression manifest, the merged coverage report and the plan; it does
not read the fcov manifests. Section 1.8's carve-outs still apply: TP-IRQ-079 and TP-SEC-025 stay
COUNTED-ONLY until the NMI-pre-empted evidence is retained, and the NMI timing knob's two bins stay
counted-only for round 1 by LOG-085.

## 10. Acceptance

The round is accepted when all 53 runs are clean, the merge and the fcov checks complete, the two checked
entries meet their expectations on all six of their runs, and the credit report and promotion table are regenerated at the round's
commit. A failing run of either SELECTED tier refuses the index, so one of the 8 unmeasured runs is a round-1
blocker and not a footnote. A check-tier failure is not: the round does not select that tier, and a
check-tier regression is graded on its own.

## 11. The round's HEAD, and what must still be true of it

Read from the flow rather than described: gen_round.py assigns `a.pinned_sha = M.head_sha()` for a measured
round, refuses without `--canary-build`, and calls `check_canary_build(a.canary_build, a.pinned_sha)`, which
accepts only a head-mode build of exactly that commit with a covergroup declared. So a measured round pins
the live HEAD at dispatch and the regression runs from it, recorded as head_sha in the round manifest.

ROUND_HEAD is therefore two facts, not one commit:

1. The last SOURCE landing is landing 39, 726682a. It is what sets the build identity the canary must
   report, and nothing committed after it changes a file the build reads.
2. The round is pinned to whatever HEAD is at dispatch, which will be this form's commit or a later
   records-only one. The load-bearing property is not which commit that is but that its build identity still
   equals landing 39's.

Both facts are checked with commands rather than asserted. For the first,
`git diff --name-only 726682a HEAD -- dv/auto_dv/tb dv/auto_dv/env dv/auto_dv/isa rtl` is empty at 7f61cd1,
over five commits that are all records, rulings and reviews. For the second, gen_build_identity.py reads
bc0cd7778e382b13 at 726682a and 6a1d73dfb815cfc7 at both 9baf3f9 and landing 39's parent, so landing 38 left
the identity where it was and landing 39 moved it once (section 8). The Orchestrator should re-run that first
command at dispatch, because the ruling of LOG-088 still owes a testlist edit and more records commits may
land before the canary: a testlist edit changes the round's selection but not the build identity, while
anything under those four paths changes the identity and makes the canary stale.
