# PMP 40-seed measurement, retained

Written 2026-09-05T05:51:36Z by the Runtime Manager. The three PMP manifests committed at 253f08e declare only
bins this measurement found hit at EVERY seed, so the every-seed rule those manifests rest on has to be
checkable from the commit. Both files are BYTE-IDENTICAL to the served records under
`dv/auto_dv/work/runtime/done/`, which git does not track; no header was added, so each sha256 is
re-derivable from its source.

Unmeasured, coverage on, no manifest row. Nothing here entered a measured merge.

| file | bytes | sha256 | source under work/runtime/done |
|---|---|---|---|
| `gen_pmp_40seed.yaml` | 3336 | `0f1f7d1e75465688517a4f6340d501a073d2eaeee4f47c319b7ffbc88c46aaa9` | `gen_pmp_40seed.yaml` |
| `gen_pmp_40seed_bins.txt` | 76162 | `ae2aa78dd82d9df2d8aa5336e99a5229cb41cd2f50ef441d42f0d60c9bc95ddb` | `gen_pmp_40seed_bins.txt` |

## The run

| | |
|---|---|
| out directory | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_pmp_40seed` |
| commit | 218e9f32316cb37cd66f1946ae36734578c9d3ff (the render commit) |
| base seed | 218090305 |
| planned / ran | 120 / 119 |
| driver | a detached archive of 218e9f3, so the flow code was committed too; the regression manifest's own git field is empty while `source.head_sha` carries the pin |

## Seeds per entry, and the one that never ran

| entry | seeds | hit at every seed | some | never |
|---|---|---|---|---|
| `gen_test_pmp_csr_warl` | 39 | 215 | 119 | 73 |
| `gen_test_pmp_lock` | 40 | 139 | 174 | 94 |
| `gen_test_pmp_mseccfg` | 40 | 175 | 81 | 151 |

The WARL denominator is 39, not 40. At seed 230969025 the COMMITTED generator
`gen_pmp_csr_warl_prog.py` asserts on its own draw, "TP-PMP-003 mml0: no reserved-bit write drawn"
(line 615, reached from `build()` at :1066), so no program was generated and the run never started.
Any every-seed claim about that entry is over 39 seeds. The Test Writer has since fixed the generator;
that fix is not part of this measurement.

The two bins called out at the time:

| bin | csr_warl | lock | mseccfg |
|---|---|---|---|
| `gen_pmp_cfg_write_cg.cp_mml.mml1` | 39/39 | 18/40 | 40/40 |
| `gen_pmp_cfg_write_cg.cp_rlb.rlb1` | 32/39 | 40/40 | 40/40 |

Neither is declarable from all three entries, and the two that are safe differ between them.

## How the per-seed counts were obtained, and the trap in the obvious method

One urg report PER TEST, selected by full path with `-tests`, 119 of them. A single merged report cannot
answer this: its per-bin TEST column caps at TEN tests with no marker, whatever `-show maxtests N` is set
to, so every bin looks inconsistently hit. That produced a false "0 bins hit at every seed" for all three
entries on the first attempt, which is what exposed it.

The bin parser is `dv/auto_dv/tools/gen_read_keyed.py parse_report`, not a new one. A parser written by
hand for this disagreed with the committed round-0 report's own COVERED/EXPECTED row on three of four
sampled covergroups; the reviewed one agrees on all 26. Each per-test report's covergroup totals are
cross-checked against that report's own `groups.txt` row before its bins are counted, and a report that
disagrees is rejected rather than counted: 119 read, 0 rejected.

## Verdicts

All 119 runs read FAIL, every one on the same rule: "declares N bins but has no manifest". At that commit
the covergroups existed and the manifests did not, so `finish()` refused each entry. The rule fires AFTER
sampling, so the coverage is real; the covergroup-presence control run's own database carries all four
covergroups with non-zero counts. The FAILs are not a defect in the measurement.

# Second block: the step-1b re-measure at 4cd3ff6

Written 2026-09-05T09:30Z by the Runtime Manager. tb-infra-2's landing 44 changed three PMP samplers, so the
manifests above rest on a measurement taken before those changes. This block re-measures the same three entries
over the SAME seeds so the pair is one before-and-after rather than two samples, and it is the measurement the
Test Writer re-renders those manifests from.

| file | bytes | sha256 |
|---|---|---|
| `gen_pmp_1b.yaml` | 6285 | `74785ccd0b617ce56679382d15e1644c4791ebccc2a342c0080624b3d9709e59` |
| `gen_pmp_1b_bins.txt` | 76162 | `b46e84e0e9d41cb78007528ed383c644f1bcfe0fce16f266ef8201909600efd3` |

Both byte-identical to the served records under `dv/auto_dv/work/runtime/done/`. The listing is the same byte
count as the first block's by coincidence of fixed-width formatting over the same 407-bin population; its content
differs on 46 lines.

Pinned to 4cd3ff6aaf22bb5f3a977b3ac2006f16ebce0060, head-mode mirror, driver a detached archive of that commit.
120 dispatched, 119 results, 119 PASS. The one absence is predicted and is the only one: csr_warl seed 230969025,
where the committed generator at that commit asserts on its own draw, so csr_warl is measured over 39 seeds.

## 1. tb-infra-2's predicted bins, reported first

Its prediction was filed BEFORE the runs, in `gen_tdd_logs/fcov/gen_fu_l44_pmp_step1b.log`. Its limit, quoted
verbatim from that file:

> AND THE PREDICTION'S LIMIT, said before the run rather than after. cross_auto_bin_max is 0, so an unnamed
> {mml1, rlb0, c1111, ignored_mml_exec} tuple is counted NOWHERE and the only visible trace of the Minor-1
> misroute is a seed's membership in cp_outcome.ignored_mml_exec. A seed that also had a legitimate
> exec-encoding sample shows nothing. So "no number moved" is a POSSIBLE AND CORRECT outcome, not a failed
> fix. The proof of these changes is the classifier reading what the RTL reads; the numbers can only falsify.

The log names TEN bins across seven prediction clauses, not seven bins; all ten are reported here by name rather
than trimmed to a count. Counts are seeds-hit out of that entry's measured seeds, before then after.

| bin | prediction | csr_warl (39) | lock (40) | mseccfg (40) |
|---|---|---|---|---|
| `gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1001_suppressed` | CANNOT MOVE | 3 to 3 | 4 to 4 | 40 to 40 |
| `gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1010_suppressed` | CANNOT MOVE | 4 to 4 | 3 to 3 | 40 to 40 |
| `gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1011_suppressed` | CANNOT MOVE | 3 to 3 | 3 to 3 | 40 to 40 |
| `gen_pmp_cfg_write_cg.cr_mml_exec_suppress.rlb0_c1101_suppressed` | CANNOT MOVE | 6 to 6 | 7 to 7 | 40 to 40 |
| `gen_pmp_cfg_write_cg.cp_outcome.ignored_mml_exec` | may LOSE only | 13 to 13 | 12 to 11 | 40 to 40 |
| `gen_pmp_cfg_write_cg.cr_lock_outcome.locked_rlb0_ignored` | may GAIN, cannot lose | 23 to 23 | 40 to 40 | 0 to 0 |
| `gen_pmp_cfg_write_cg.cr_mml_nonexec_accept.c1111_written` | must hold or rise | 3 to 3 | 15 to 15 | 40 to 40 |
| `gen_pmp_addr_write_cg.cr_self_lock.locked_rlb1_written` | becomes REACHABLE | **0 to 14** | **0 to 40** | 0 to 0 |
| `gen_pmp_addr_write_cg.cr_tor_lock.nl_tor_rlb1_written` | becomes REACHABLE | **0 to 1** | **0 to 40** | 0 to 0 |
| `gen_pmp_addr_write_cg.cr_top_lock.top_unlocked_written` | must HOLD | 39 to 39 | 40 to 40 | 40 to 40 |

EVERY CLAUSE HOLDS. The four that cannot move did not move, in any entry. The one that may only lose, lost one
seed in one entry and gained nowhere. The one that cannot lose, did not. The one that must hold or rise, held.
The one that must hold, held.

The two the raw-lock change was meant to make reachable were at ZERO in all three entries before and are hit now.
So this is a confirmation BY MOVEMENT, which the limit above says was the stronger of the two possible outcomes:
a flat result would have been correct but uninformative, and the result is not flat.

## 2. Cross legs, per the cross-operand rule

The rule: a cross bin is a per-run guarantee only when EVERY operand is, so a manifest may declare a cross bin
only where the sweep shows THAT CROSS LEG at every seed. Reported by leg, not by component coverpoint.

| entry | family cross legs | declared cross legs | all declared legs at every seed | family legs EVERY / SOME / NEVER |
|---|---|---|---|---|
| gen_test_pmp_csr_warl | 258 | 91 | yes | 99 / 103 / 56 |
| gen_test_pmp_lock | 258 | 20 | yes | 41 / 142 / 75 |
| gen_test_pmp_mseccfg | 258 | 25 | yes | 71 / 65 / 122 |

Every declared cross leg is hit at every measured seed in all three entries, so no manifest declares a cross bin
the rule forbids. Examples of legs BELOW the bar, which a manifest may NOT declare, are in the listing; the
lowest in csr_warl are `cr_tor_lock.nl_tor_rlb1_written` at 1 of 39, three `cr_mode_lrwx` legs at 1 of 39 and
`cr_reset_read.rst_mseccfg` at 1 of 39, none of them declared.

## 3. The rest

The manifests all still hold. Every declared bin is hit at every measured seed: csr_warl 179 of 179 over 39
seeds, lock 39 of 39 over 40, mseccfg 26 of 26 over 40, with the post-hoc checker reporting PASS and zero unmet
on all 119 runs. Manifest md5s at the pinned commit are `faf7e54976f4c947f85c7a2eb778513c`,
`91c204336115865799239be1ea3d5b0b` and `63b486a37ad3f121a62bf15a98613c12`, all unchanged at HEAD.

Per entry, the EVERY / SOME / NEVER split over the 407-bin family, before then after:

| entry | seeds | EVERY | SOME | NEVER |
|---|---|---|---|---|
| gen_test_pmp_csr_warl | 39 | 215 to 214 | 119 to 125 | 73 to 68 |
| gen_test_pmp_lock | 40 | 139 to 142 | 174 to 174 | 94 to 91 |
| gen_test_pmp_mseccfg | 40 | 175 to 177 | 81 to 80 | 151 to 150 |

Fifteen further bins moved and all fifteen are in the listing. Two left the every-seed set:
`gen_pmp_cfg_write_cg.cp_outcome.ignored_lock` goes 39/39 to 23/39 in csr_warl and 7/40 to 0/40 in mseccfg.
NEITHER IS DECLARED, which is why the manifests survive; that was checked against the manifests rather than
inferred from the checker's silence.

## Three things about this block a reader should not have to discover

TEN RUNS FAILED FIRST AND WERE RE-RUN, and the cause was mine. Ten csr_warl runs came back with "sim.log
missing" and no LSF output: they were the ten in flight when I killed the dispatcher to widen the batch from 10
to 40 after `busers` showed no per-user cap, so their farm jobs died with their client. They were re-run cleanly
rather than censored or reported as a smaller n. The 119 PASS figure is after that re-run, and no run here rests
on a first attempt that lost its job.

THE CHECK WAS RUN POST-HOC, NOT INLINE. The runs were dispatched without `--fcov-check`, so the check was made
afterwards through the flow's own `gen_fcov.check_test`, the exact function `gen_run`'s check path calls, against
the coverage each run had already written. `result.yaml` is untouched and still carries `fcov_check: null` in all
119; each `fcov_check.log` opens with the checker argv; and because `check_test` writes the run-artifact name
`fcov_manifest_used.yaml` itself, that file is renamed to `fcov_manifest_used.post.yaml` in every run directory.
Nothing in a run directory claims a shape the run did not have.

A CALLER DEFECT WAS FOUND AND CORRECTED BEFORE IT WAS REPORTED. The first post-hoc pass called
`gen_fcov.run_checker` directly, which takes the checker's `--vdb`/`--cm-name` branch and builds a urg report
with NO cross rewrite, so every cross bin read MISSING-FROM-REPORT: 91 of csr_warl's 179 and, by the same
mechanism, 20 of lock's 39 and 25 of mseccfg's 26. At face value that says all three measured entries fail every
seed of a measured round. What exposed it was the shape of the number, twenty-six seeds each at exactly 88 hit
and 91 unmet with zero variation, which is a structural absence rather than stimulus, and 91 equals exactly the
manifest's cross-bin count. `gen_run`'s real path is `check_test`, which runs `per_test_report` and
`derived_report` first to turn `Summary for Cross <cr>` into the variable form
`ci/check_fcov_expectations.py` can parse (LOG-054). There is no defect in the flow, the manifests or the
entries. Because of that near-miss, the census and the checker were crossed before any claim in this block: they
agree exactly, with zero declared bins below the bar, zero declared bins absent from the census, and zero unmet.

ONE METRIC DIFFERS FROM THE FIRST BLOCK. These runs omit CONDITION coverage (the build did not pass `--cond`).
It is a code-coverage metric and does not touch covergroups: the per-test report carries the same four gen_pmp
covergroups and the identical 407-bin family population. Declared here rather than left to be discovered.
