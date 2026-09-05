# irq checker fix 2 re-runs at b9e5fad, retained

Written 2026-09-05T13:09Z by the Runtime Manager. rev60's Medium: the 3-of-3 RED-OK recorded at 69eb33f was measured on the
9c7f8f6 checker, and landing 54 replaced that checker's clock, so the irq entry's promotion condition rested on a
checker that no longer exists. This block re-measures it at b9e5fad. It stands BESIDE the 69eb33f block and edits
none of its collected records.

The record beside this file is BYTE-IDENTICAL to the served copy under `dv/auto_dv/work/runtime/done/`, which git
does not track.

| file | bytes | sha256 |
|---|---|---|
| `gen_reds2_b9e5fad.yaml` | 3406 | `ea5795b0beeb762cb8ac698e924b523fb52e00509539c12b89cfc34399d9b8c6` |

Pinned to b9e5fad36c4d7f643a02c76f333ee00bfa22bc6a, head-mode mirror, driver a detached archive of that commit
whose `gen_run.py` hashes to 7632eca5b10f840c, equal to the committed blob. Fresh output directory.

## The reds are closed at this commit: 3 of 3, measured

| run | verdict | irq_entry firings | wall_s |
|---|---|---|---|
| `gen_test_irq_basic_1207954461` | FAIL | 258 | 93.8 |
| `gen_test_irq_basic_red_1038372995` | RED-OK | 0 | 8.8 |
| `gen_test_irq_basic_red_1382184738` | RED-OK | 0 | 38.9 |
| `gen_test_irq_basic_red_552432658` | RED-OK | 0 | 10.2 |

All three red seeds read RED-OK with ZERO irq_entry firings. The difference from the 69eb33f block is what rev60
asked for: that block re-ran the two seeds that had failed for an undeclared reason and took the wave's already
RED-OK 552432658 as its third, so its "3 of 3" mixed two measurements with one carried figure. Here all three are
measured at the commit whose checker they certify.

## The 258-fire seed under the new clock

`gen_test_irq_basic_1207954461` fires 258 times at b9e5fad, the same count as at 9c7f8f6 and at 4017573. The new
clock does not move it, which is expected rather than surprising: that run is a wedged core and not a checker
measurement. Its earliest mechanism is `sva_rvfi_irq_valid_exclusive` at cycle 6591.5, which is 2659 cycles before
the grant property and 2699 before the first instruction divergence.

Counting rule: a firing is a UVM_ERROR line carrying `[irq_entry]`. A line mentioning the identifier is not a
firing, which is the rule this record's predecessor had to learn twice.

## What these runs do NOT carry

`export_origin` is null on all four. The driver is the pinned b9e5fad archive, which predates the export default,
so no record stream was written. This is stated because I told the Orchestrator these runs would write one: the
pinned driver is the right choice for a verification block, and the export run on this seed had already been
released as unnecessary by its requester.
