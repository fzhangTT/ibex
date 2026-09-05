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
