# Round-1 request: the first measured coverage run (acceptance form)

Requester: DV Lead. Purpose 4 (Phase 1 gate or closure round). Owner directive LOG-085; manifest-scope ruling
LOG-086 (a69e285) and its addendum. Queue file: dv/auto_dv/work/runtime/requests/dv-lead-001.yaml.

Every figure below is measured at a named commit and re-derived by me, not relayed. No blank remains: the
LOG-086 detach is 18ac053, landing 38 is 9baf3f9, landing 39 is 726682a. LOG-088 (7f61cd1) detaches six more
measured entries after runtime-2's fcov pre-flight. Its testlist edit committed as f60bee5, and both detaches
are now SUPERSEDED: the manifests were re-scoped instead (LOG-090, LOG-091), landed at 3142adc, and their
references restored at 1b65f86, so the round checks 12 measured entries and counts none.
The scope figures were WRONG in this form's
first version, which said 103 entries and 141 runs; that is the whole testlist, not the round's selection.
runtime-2 caught it with the flow's own selector, the LOG-086 corrigendum at 7e3ecc8 records it, and every
scope figure below is re-derived the same way at 4a00702, the commit the figures belong to. The testlist moved
after 18ac053, at f60bee5 and at 1b65f86, and the manifests moved with the re-scope landings, so nothing here
holds by inheritance from an earlier reading. The tool that wrote this section derives every figure it states,
refuses when an input differs from the commit in content it reads, and re-checks that between the derivation
and the write.

THIS VERSION SUPERSEDES THE ONE COMMITTED AT d1f6019, under LOG-091. Sections 5 and 10 are the ones that
changed in substance: the round now checks 12 measured entries rather than two, because the manifests were
re-scoped instead of detached, and acceptance is stated against that. Sections 1, 3, 4, 6 and 11 carry the
figures forward from the same derivation. Anything the d1f6019 version says about counted-only measured
entries is void.

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
| THE ROUND | 19 | 53 | 36 |
| check, NOT selected | 84 | 88 | 0 |

The other way to say it: 36 measured runs (12 entries at 3 seeds)
plus 17 unmeasured runs over 7 entries. The measured set is three
entries smaller than this form's first version stated, because gen_test_bit_draft, gen_test_csr_reset and
gen_test_pmp_csr_warl went measured false: every bin their items own sits on a covergroup that does not
exist, so they can make no per-run claim at all (section 5).

THE ROUND'S GATING CONDITION IS NOT THE MEASURED SET. gen_round indexes a round only when the regression is
clean, where clean means zero failing runs and failing counts fail plus timeout plus not_run, over all 53.
So any one of the 17 unmeasured runs can refuse the round while contributing nothing to
the coverage merge.
This request therefore states an expected outcome for all 53 runs, and for nothing outside them: an entry the
round does not select cannot pass or fail it, whatever its state in the tree.

## 2. Base seed, pinned

`--base-seed 20260904`, ruled by the Orchestrator. Without it gen_regress defaults the base to the
dispatch's start time, which makes the round's seeds unreproducible. Re-derived by me over the round's own
53-run plan at e641b24: 53 distinct seed values and 53 distinct entry-and-seed pairs, zero collisions, the
same list on a second call, and 0 of the 45 measured values shared with base 20260905, so the base is
load-bearing. (runtime-2's equivalent figures were 141 and 141 because they covered the whole testlist.)

## 3. Seed counts, and why three

Every measured entry carries `seeds: 3` in the testlist, which gives the 36 measured runs. Three is the
round-1 baseline I am asking for: it is what the entries already declare, it gives every measured entry a
program-image spread (see section 4), and it keeps the LSF bill at 53 runs.

DO NOT pass `--seeds N`. It is not a measured-only knob: `seeds_for_test` (gen_flow_util.py:1625-1629) takes
the override ahead of the entry's own count, for every selected entry. Derived over this selection, `--seeds
3` makes the plan 57 runs with the same 36 measured, the extra runs being the two
one-seed smoke entries going to three; `--seeds 5` makes it 95 runs with 60 measured.
If round 2 wants more measured seeds, the lever
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
3. An entry's pinned knobs NARROW the draw rather than randomize it. The 12 measured entries pin none: every
   one carries only `+gen_fetch_en_at_reset=0` and the banner reads `pinned=-`. So no stress axis is off for
   the measured set, and none is pinned on either.

Two of the round's entries run at one seed, gen_boot_zc and gen_ut_lockstep, both smoke and both unmeasured,
and for them the seed is inert: each carries `program: {directed: [dv/auto_dv/stim/gen_directed/
gen_zc_directed.S], seed: 1}`, a fixed assembly image with the program seed pinned, so a second run seed
would compile the same instruction stream. One is the boots-and-retires milestone on that program and the
other the lock-step comparator against the Spike shim over it. The check tier's own seed shape is not this
round's concern, since the round does not select it.

## 5. The measured entries and their expected outcomes

All 12 measured entries run, all 12 contribute coverage, and ALL OF THEM ARE CHECKED against their manifest.
There is no counted-only measured entry in this round. That is the result of the re-scope, and it is worth
stating against what this form first promised: two checked entries and thirteen counted-only.

HOW IT GOT HERE, in one paragraph. LOG-086 and LOG-088 detached thirteen measured entries from their
manifests, seven whose declarations sat on covergroups that do not exist and six the pre-flight measured
unmet. That traded thirteen expectation failures for thirteen POLICY failures:
gen_regress.fcov_policy_failures fails a measured entry on smoke or targeted with a null reference, which I
measured as 39 of the round's 53 runs. LOG-090 adopted the reading that a manifest declares what a test
guarantees PER RUN, so an over-declared manifest is a plan defect rather than a policy problem, and LOG-091
took the manifest route: the plan marks the coverpoints of the unbuilt covergroups out of manifests, the tests
carry bins_not_hit exclusions with a reason per bin, and the references come back. That landed jointly as
3142adc, with the references restored at 1b65f86.

CHECKED against their manifests (12 entries, 36 runs, 2895 declared bins, 8685 bin checks):

| entry | seeds | declared bins | expected |
|---|---|---|---|
| gen_test_bit_ratified | 3 | 617 | PASS, expectation met |
| gen_test_isa_alu | 3 | 563 | PASS, expectation met |
| gen_test_mul_mul | 3 | 338 | PASS, expectation met |
| gen_test_cmp_zcmp_basic | 3 | 325 | PASS, expectation met |
| gen_test_cmp_zca | 3 | 300 | PASS, expectation met |
| gen_test_mul_div | 3 | 196 | PASS, expectation met |
| gen_test_isa_cti | 3 | 184 | PASS, expectation met |
| gen_test_csr_trap_setup | 3 | 146 | PASS, expectation met |
| gen_test_isa_shift | 3 | 120 | PASS, expectation met |
| gen_test_cmp_zcb | 3 | 96 | PASS, expectation met |
| gen_test_rst_boot | 3 | 6 | PASS, expectation met |
| gen_test_csr_access | 3 | 4 | PASS, expectation met |

THE EXPECTATION IS MEASURED, NOT ARGUED. runtime-2 re-flew every measured run at the round's own seeds at
3142adc, tag r1_fcov_reflight2, and that manifest reports fcov checked 36, pass 36, unmet 0, unverifiable 0.
It is the same 36-run shape the round will run, with the re-scoped manifests as the only difference from the
earlier pre-flight, so the expectations in the table above are observed rather than predicted.

THREE ENTRIES ARE NOT MEASURED THIS ROUND, and the reason is a rule rather than a convenience.
gen_test_bit_draft, gen_test_csr_reset and gen_test_pmp_csr_warl declare 15 of 15, 68 of 68 and 266 of 266
bins on covergroups that do not exist, so after the marks they have nothing left to guarantee. A measured
entry with an empty declared set is not a pass: the checker returns unverifiable (gen_fcov.py:330) and the
manifest generator refuses to render such a manifest at all. Crediting coverage no entry has claimed is what
the trust-triad policy refuses, so those three run unmeasured, their manifest files are gone until their
covergroups are built, and the round record names them.

ONE CHECKED ENTRY IS FOUR BINS WIDE. gen_test_csr_access keeps 4 of its 80 declarations
(gen_csr_trap_setup_warl_cg.cp_csr.mie, cp_wpat.all0, cr_csr_wpat.mie_all0 and cp_rd.x0), the other 76 being
on unbuilt covergroups. It stays a checked measured entry because the re-flight decides that on evidence
rather than anticipation, and the round record must not list it as checked without saying how narrow its claim
is.

WHAT THE RE-SCOPE DID NOT DO, measured rather than assumed, because a clean result invites exactly the wrong
inference. Re-scoping changed what each test CLAIMS per run; it changed nothing about what the round COVERS.
Read from this wave's own merged report with the checker-independent parser (4268 bins), all 66 removed bins
are still present, 25 of them are hit somewhere in the run and 41 are not. So the round leaves 41 of them
uncovered, not 66, and no sentence here may say the re-scope closed a bin. 6 of those hits are worth naming,
and they are the ones unmet at EVERY seed of their own entry rather than the most-hit:
gen_cmp_imm_edges_cg.cp_cj_off.self at 398 merged hits; gen_cmp_zca_cg.cr_insn_next.c_lui_n16 at 139 merged
hits; gen_cmp_zca_cg.cr_insn_align.c_jalr_half at 83 merged hits; gen_cmp_zca_cg.cr_insn_next.c_add_n16 at 35
merged hits; gen_csr_trap_setup_warl_cg.cr_csr_wpat.mie_msb at 6 merged hits;
gen_cmp_zca_cg.cr_insn_next.c_mv_n16 at 5 merged hits. Each was unmet at all three seeds of its OWN entry and
is reached by another entry in the same run, which is a fact from the report and holds whatever the cause
turns out to be. WHY each went unmet is under audit BY MEASUREMENT and the round record must not lean on those
causes yet: the Test Writer instrumented the csr_trap_setup generator over 40 seeds and found that its mie MSB
write operand occurs in 10 of them, so gen_csr_trap_setup_warl_cg.cr_csr_wpat.mie_msb is seed-dependent at
roughly one run in four rather than a stimulus gap, and the reason it carries today is wrong. The other five
are being audited the same way. That one correction moves the reason classes to 46 stimulus and 20
seed-dependent without moving any measured figure above, since 47 bins were still unmet at every seed and 19
at some.

WHAT THE RE-SCOPE COST AND DID NOT COST. It removed 758 declarations on covergroups that do not exist, 631
over the seven measured entries and 127 over the two unmeasured targeted ones, and 246 declarations on built
covergroups the tests do not guarantee per run. Of those 246, exactly 123 were unmet at every one of the three
pre-flight seeds and 123 at some seeds only, with no bin counted twice: the two halves are disjoint. The first
half is a defect record, each bin carrying a stimulus or declaration cause, and the second is a semantics
record, each bin stating that the test does not guarantee it per run. Neither half removes coverage: those
bins stay PLANNED in the traceability and are credited from the merged report whenever a run hits them. The
round record states the two halves separately because their futures differ, and it must not read as though
excluding a check closed a bin.

## 6. The unmeasured runs (17), and what the round does not select

The round's 7 unmeasured entries, 17 runs, every one of them able to refuse the round:

- gen_boot_zc and gen_ut_lockstep, both smoke at 1 seed: PASS. Neither declares anything, so neither carries
  an expectation check.
- gen_test_pmp_mseccfg and gen_test_pmp_lock, targeted at 3 seeds each: PASS with no expectation check. Every
  bin their items owned sat on a covergroup that does not exist, so the marks emptied their declaration and
  their manifest files are gone until those covergroups are built.
- gen_test_bit_draft, gen_test_csr_reset and gen_test_pmp_csr_warl at 3 seeds each: PASS with no expectation
  check. These three were MEASURED until the re-scope and are the round's only loss of credited coverage. For
  the same reason as the two above they can make no per-run claim, and crediting coverage nothing has claimed
  is what the trust-triad policy refuses. Section 5 names them and so must the round record.

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
unmeasured, and with `+gen_chk_sva_b8` it returns the LOG-067 refusal. The 12 measured
entries carry exactly one plusarg each, `+gen_fetch_en_at_reset=0`, which is how they pin nothing (section 4).

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

The round is accepted when all 53 runs are clean, the merge and the fcov checks complete, the 12 checked
entries meet their expectations on all 36 of their runs, and the credit report and promotion table are
regenerated at the round's
commit. A failing run of either SELECTED tier refuses the index, so one of the 17 unmeasured runs is a round-1
blocker and not a footnote. A check-tier failure is not: the round does not select that tier, and a
check-tier regression is graded on its own.

## 11. The round's HEAD, and what must still be true of it

Read from the flow rather than described: gen_round.py assigns `a.pinned_sha = M.head_sha()` for a measured
round, refuses without `--canary-build`, and calls `check_canary_build(a.canary_build, a.pinned_sha)`, which
accepts only a head-mode build of exactly that commit with a covergroup declared. So a measured round pins
the live HEAD at dispatch and the regression runs from it, recorded as head_sha in the round manifest.

ROUND_HEAD is therefore two facts, not one commit:

1. The last landing that changes a file the SV build reads is landing 39, 726682a, and the
   identity it sets, bc0cd7778e382b13, still holds. Checked two ways at the round's commit: a diff of 726682a
   against HEAD over dv/auto_dv/tb, dv/auto_dv/env, dv/auto_dv/isa and rtl is empty, and
   gen_build_identity.py --expect exits 0. Two later landings change sources the build does NOT read and so
   cannot move the identity: 04a4808, the plan marks and the first manifest re-scope, and 3142adc, the
   second re-scope of the manifests and the test modules.
2. The round is pinned to whatever HEAD is at dispatch, which will be this form's commit or a later
   records-only one. The load-bearing property is not which commit that is but that its build identity still
   equals landing 39's.

Both facts are checked with commands rather than asserted, at 4a00702: a diff of 726682a against it over the
four build paths is empty across 31 commits, every one of them records, rulings, reviews, manifests or tests,
and gen_build_identity.py --expect exits 0 on bc0cd7778e382b13. The Orchestrator should re-run that diff at
dispatch, because more records commits may land before the canary: a manifest or testlist edit changes what
the round checks but not the build identity, while anything under those four paths changes the identity and
makes the canary stale.
