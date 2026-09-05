# Generator 40-seed sweeps, before and after the fixes, retained

Written 2026-09-05T08:13:10Z by the Runtime Manager. The Test Writer's generator group hands on this pair of
sweeps, and the DV Lead's transfer ruling turns the result into a hash check at the commit that lands the
generators, so the measurement and the digests it is pinned to have to be readable from the commit.

The three files beside this one are BYTE-IDENTICAL to the served records under `dv/auto_dv/work/runtime/done/`,
which git does not track. No header was added, so each sha256 is re-derivable from its source.

| file | bytes | sha256 |
|---|---|---|
| `gen_generator_sweep.yaml` | 4689 | `a7c99b29e2d06f66757872e882a58058f9162db6ccc76cb2ab413c197cf67af3` |
| `gen_generator_rerun_fix.yaml` | 4395 | `a47a25b8ac40c0a7a5deb9c744deb8f4fdcb37fffb506fd0a02be025d06f0dfe` |
| `gen_bitr40_bins.txt` | 4915 | `4252fe6cbd2dae2adde83d9f04d38e9fc112b50653dc3b667c8c846c7dcaaca1` |

Unmeasured, coverage on, no manifest row. Nothing here entered a measured merge. NEITHER SWEEP IS PINNABLE TO A
COMMIT: both ran uncommitted generator files, so the pin is to bytes.

## The two runs

| | before (pre-fix) | after (fixed) |
|---|---|---|
| out directory | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_gensweep2` | `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_gsfix2` |
| source root | `/proj_soc/user_dev/fzhang/ibex_dv_probe/gensweep` | `/proj_soc/user_dev/fzhang/ibex_dv_probe/gensweep_fix` |
| root's tree_sha256 | `12931fd78f31a091e7245f17e68a8bf7c9ff8eae781d5a50e4f13fad3abae018` | `642e176b04d5a6f8bc7e0f94c15b48f70524d6774bee2118165065ff157874b1` |
| root shape | archive of a commit plus three uncommitted generator files; its OWN mirror (source worktree, head_sha null, mirror_root itself) | the same shape, archived from 274a89afc40b1107ee626109c8c93b5ce5be0dc9 |
| built with `--allow-stale-mirror` | no | no |
| import path | `PYTHONPATH` equal to the root in every run's own `run_cmd.sh`, 94 of 94 | the same, 80 of 80 |

## The digests the after-sweep is pinned to

Named by the Test Writer before the runs, recomputed by the Runtime Manager INSIDE the built source root rather
than in the clone, so the check is on what actually ran. All three exact.

| generator | sha256 first-12 |
|---|---|
| `dv/auto_dv/tests/gen_programs/gen_bit_ratified_prog.py` | `14405978b07d` |
| `dv/auto_dv/tests/gen_programs/gen_cmp_zca_prog.py` | `b31555f595b4` |
| `dv/auto_dv/tests/gen_programs/gen_pmp_csr_warl_prog.py` | `964e232edfb4` |

## The seed sets are identical, which is what makes this one measurement

Both sweeps draw 40 seeds per entry from a fixed base, bit_ratified from 1909560559 and cmp_zca from 218090305.
The two sets were sorted and diffed BEFORE the second dispatch and are equal set for set. The seven bin counts
below are therefore movement over the same draws, not two samples of a distribution.

## Per bin, before and after

gen_test_bit_ratified, 617 declared bins per run. Before: 17 of 40 PASS, 23 refused by the coverage check, 24643
HIT and 37 UNHIT pooled. After: 40 of 40 PASS, 24680 HIT and 0 UNHIT pooled.

| bin | unhit before | unhit after |
|---|---|---|
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.zext_h_pos_rand` | 12 of 40 | 0 of 40 |
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.max_neg_rand` | 8 of 40 | 0 of 40 |
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.sh3add_neg_rand` | 5 of 40 | 0 of 40 |
| `gen_bit_count_cg.cr_op_result.cpop_other` | 4 of 40 | 0 of 40 |
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.andn_pos_rand` | 3 of 40 | 0 of 40 |
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.xnor_pos_rand` | 3 of 40 | 0 of 40 |
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.orn_pos_rand` | 2 of 40 | 0 of 40 |

gen_test_cmp_zca, 300 declared bins per run. Before: 25 of 40 PASS, 15 refused by the coverage check, 11985 HIT
and 15 UNHIT pooled. After: 40 of 40 PASS, 12000 HIT and 0 UNHIT pooled.

| bin | unhit before | unhit after |
|---|---|---|
| `gen_cmp_zca_cg.cr_insn_rdfull.c_swsp_x8_15` | 9 of 40 | 0 of 40 |
| `gen_cmp_zca_cg.cr_insn_rdfull.c_swsp_x3_7` | 6 of 40 | 0 of 40 |

No bin is unhit anywhere in the after sweep, in either entry. That answers the Test Writer's alignment-regression
watch as a corollary rather than as a separate check: the cmp_zca manifest declares 61 alignment legs
(`cr_insn_align` 51, `cr_op_align` 10) and every one is hit in every one of the forty.

gen_test_pmp_csr_warl was 14 runs in the before sweep (14 PASS: the four seeds the fix creates, where the
committed generator asserted and produced no program, and ten whose programs the fix leaves byte-identical). It is
HELD out of the after sweep, waiting on the flip commit.

Pooled over the 80 after-runs: UVM_ERROR 0, UVM_FATAL 0, cocotb failed 0, no fire-check failure, exit 0
everywhere. The coverage check was the only mechanism that ever refused, and after the fix it refused nothing.

## The pair is NOT a single-variable experiment, and the delta is bounded by measurement

Found and measured by the Test Writer, recorded here because the Runtime Manager's own report named only the seed
identity and the import path as the controlled axes and did not state this.

The two builds differ: `sources_sha256` `32f8789879` before against `9879ca90c6` after, because the fix root was
archived from a later HEAD than the pre-fix root. The Test Writer ran the control rather than assuming it away.
The covergroup definitions for `gen_bit_zba_zbb_ops_cg`, `gen_bit_count_cg` and `gen_cmp_zca_cg` are
byte-identical between the two roots; the set of sampler call sites naming those groups hashes identically in
both; and the only changed line naming any of them adds four irq covergroups to the same construction statement.
So the testbench delta cannot account for the bins turning over. Stated as a bounded delta, not as a single
variable.

## The mapper column: all seven bins are OUTSIDE the model-level reader's 74

Asked by the DV Lead, answered from the data rather than relayed. The 74 comes from the Test Writer's
`gen_shape_check.py`, the reader that printed "74 of 617 modelled here", NOT from its declared guard. Its own
`bit_shape_of()` was called over all 617 declared bin names: it returns 74, matching the published figure, and the
74 are three crosses and nothing else (`cr_op_eq` 23, `cr_op_same` 22, `cr_op_rd_x0` 29). It returns nothing for
every one of the seven. Six of the seven live on `cr_op_rs1` and the seventh on `gen_bit_count_cg.cr_op_result`.

Overlap with the eight bins the Test Writer found and fixed with that reader (`cr_op_eq.pack_no`, `packh_no`,
`packu_no` and `cr_op_same.max/minu/sh1add/sh2add/sh3add_rs1_eq_rs2`): NONE. Those eight are all inside the 74.
The names `max` and `sh3add` appear on both lists on DIFFERENT crosses with different second legs; they are not
the same bins, and a reader skimming names would wrongly conclude a fix failed.

Both readings are pinned to the same generator file, md5 `1bed9e902389d0fbabc68cd8ae9abd40`, so the finding is not
a version artefact.

Every one of the seven was hit in at least 28 of the 40 pre-fix runs, so none was unreachable by this stimulus and
none was declaration-class. Thin rather than rare, which is what made "fix the generator" the call.

## The two measurements of the withdrawn declared guard, by bin name

The Test Writer's committed Section 14 corrigendum cites these; retained here so the citation has a path. Both
were measured against the 40 pre-fix bit_ratified runs as the control, on the same generator the guard was reading
(`gen_bit_ratified_prog.py` md5 `1bed9e902389d0fbabc68cd8ae9abd40`). The instrument is
`gen_declared_guard.py`, which the Test Writer has since withdrawn; it is a DIFFERENT tool from the
`gen_shape_check.py` that produced the 74.

| bin | the guard says | the simulation says | reading |
|---|---|---|---|
| `gen_bit_zba_zbb_ops_cg.cr_op_rs1.zext_h_pos_rand` | 40 of 40 | 28 of 40 (12 unhit) | OVER-CLEARED. The guard resolves the bin to the generator tag `cls=pos_rand` and so reads the generator's LABEL, not the sampler's value classifier. It contains the very defect the bin had. |
| `gen_bit_count_cg.cp_single_pos.p16` | 6 of 40 | 40 of 40, 3 to 5 hits per run | FALSE ALARM about a bin that is fine. |

The guard is additionally BLIND to the other six of the seven: the two-operand ops carry no rs1-class tag on their
op record, so its `resolve()` returns nothing for `max`, `sh3add`, `andn`, `xnor` and `orn`.

Its own calibration control cannot catch either case. It flags only a resolved bin read at exactly zero that the
round report says is hit, so a 40-against-28 over-clearance and a 6-against-40 false alarm both pass it silently.

Source artifacts for both rows: the per-seed table in `gen_bitr40_bins.txt` beside this file (the simulation
column, including the missing-seed lists) and `gen_generator_sweep.yaml` (the sweep the runs belong to).

## Corrigendum (2026-09-05T08:38Z): the BEFORE half ran an INTERMEDIATE generator, and here is the delta

Raised as a Low on the generator-fixes review (rev55). The paragraph above says the pre-fix root is "an archive of
a commit plus three uncommitted generator files" and leaves a reader unable to tell WHICH uncommitted files, so the
seven-plus-two bin turnover could not be attributed to specific edits. The digests, all sha256 first-12:

| generator | pre-fix root (the BEFORE half) | parent commit de60b81 | committed at 4017573 (the AFTER half) |
|---|---|---|---|
| `gen_bit_ratified_prog.py` | `7f3ec33390c2` | `c1580d22a361` | `14405978b07d` |
| `gen_cmp_zca_prog.py` | `aaa8e29f7370` | `125ef1a1cf5d` | `b31555f595b4` |
| `gen_pmp_csr_warl_prog.py` | `964e232edfb4` | `7f062657722d` | `964e232edfb4` |

So for TWO of the three the before half ran a working state that is neither the parent's committed blob nor the
committed one. The review's correction is right, and it applies to two generators rather than three: the csr_warl
generator in the pre-fix root is ALREADY the committed blob, byte-identical at `964e232edfb4`, so its 14 runs were
on the final bytes and nothing about them is intermediate.

THE DELTA IS RETAINED RATHER THAN DESCRIBED, in `gen_prefix_delta_bit_ratified.diff` and
`gen_prefix_delta_cmp_zca.diff` beside this file, each a unified diff from the pre-fix root's file to the committed
one. They are small enough to read whole: 24 changed lines and 10.

| file | bytes | sha256 |
|---|---|---|
| `gen_prefix_delta_bit_ratified.diff` | 2212 | `09f7864cbd39f165408bc28010c0a39767f70685824a563d8196878c7fff7733` |
| `gen_prefix_delta_cmp_zca.diff` | 1372 | `e6d277bf3b2d895ac84ddaa787afb3f1687af21aee4764e87980f63986015767` |

What they contain, so the attribution is checkable rather than asserted. gen_bit_ratified_prog gains `_plain_rand`,
which rejects any draw the sampler would classify as one of six named exact values or as `byte_msb` / `half_msb`,
and routes the `pos_rand` and `neg_rand` operand classes through it; that is the six `cr_op_rs1` legs. It also gains
one directed five-bit `cpop` operand, whose result lands in no other result bin; that is
`gen_bit_count_cg.cr_op_result.cpop_other`. gen_cmp_zca_prog gains one directed `c.swsp` source register in each
register range the random draw leaves to chance; that is the two `cr_insn_rdfull` legs. Nine bins, nine edits, and
the diffs are the evidence.

A reader should still treat the pair as a comparison with a bounded second variable, per the section above: the
builds differ as well as the generators, and the covergroup and sampler control is what bounds that.

## Two failed LSF build attempts, kept

The after-sweep's build was made on the SUBMIT HOST, which is the proven recipe for a self-mirror root: the
pre-fix sweep's build directory has no LSF files either. Two LSF attempts failed first and their out-trees are
kept rather than deleted, in case anyone chases the second.

| out-tree | exit | what happened |
|---|---|---|
| `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_gensweep_fix/build/gen_tb` | 127 | the bsub line carried the CLONE's interpreter, `/localdev/.../.venv/bin/python3`, which no compute host can see. `gen_build` propagates the launcher's `sys.executable` into the job line, so launching it with the clone python is what put it there. |
| `/proj_soc/user_dev/fzhang/ibex_dv_out/regress_gsfix/build/gen_tb` | 1 | UNEXPLAINED. Empty stdout and empty `lsf.err`, after the pre-build shim linked and before any `compile.log` existed. The identical command on the submit host succeeds in 26 seconds. |

The second is close in SHAPE to LOG-099 (a fresh tree, a cocotb build, a failure that leaves no message) but is
NOT the same symptom: no compile ran at all, so there is no `Py_Initialize` error and no wrong library. That
distinction is stated here so no one asserts the link from the resemblance.
