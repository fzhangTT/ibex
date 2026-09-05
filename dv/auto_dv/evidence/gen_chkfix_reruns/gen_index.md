# irq checker fix re-runs, retained

Written 2026-09-05T10:56Z by the Runtime Manager. tb-infra-2's checker fix landed at 9c7f8f6; this block re-runs
the three seeds whose behaviour the fix was expected to change, with the expectation filed BEFORE the runs.
tb-infra-2 and the DV Lead read it for the irq entry's promotion conditions.

The record beside this file is BYTE-IDENTICAL to the served copy under `dv/auto_dv/work/runtime/done/`, which git
does not track.

| file | bytes | sha256 |
|---|---|---|
| `gen_chkfix_reruns.yaml` | 3020 | `196378403d16e4329c10e55e997c02d169e9dffdc8105c6921faee80efed3aa7` |

Pinned to 9c7f8f63957d153d9c67cd1a61d44f88b3c94c69, head-mode mirror, driver a detached archive of that commit
whose `gen_run.py` hashes to the committed blob. Fresh output directory, since the testbench sources changed.

## The reds are closed: 3 of 3

Both seeds that previously failed for an undeclared reason now read RED-OK on the declared reason,
`fire_tp_irq_002`, with ZERO checker fires. The masking is gone.

| seed | verdict | irq_entry fires |
|---|---|---|
| gen_test_irq_basic_red_1038372995 | RED-OK | 0 |
| gen_test_irq_basic_red_1382184738 | RED-OK | 0 |

## The finding: the 258-fire seed is unchanged

`gen_test_irq_basic_1207954461` fires 258 times before the fix and 258 times after it, counted both times with
the not-taken pattern rather than by lines mentioning the identifier. Not reduced, not reshaped.

THE FIX IS DEMONSTRABLY IN THE BUILD, so this is not a stale binary: the message now carries the enable mapping,
`lines 00020 (enable bits 00040000)`, which the pre-fix message did not print.

What that new field shows, re-derived here rather than read off the message text:

- every one of the 18 distinct raised-line bitmaps has its enable bit SET in `mie 7fff0888`; all eighteen enable
  words were checked against the mask and none is unset
- `mstatus` is `00000088` throughout, so the global enable is set at the sample
- the raise-to-fire order deltas are 18 to 23, with 18 dominating at 153 of 258, then 19 at 67, 20 at 23, 21 at 7,
  22 at 3 and 23 at 5
- the raised lines are FAST lines, bits 16 upward, across eighteen distinct bitmaps, where the analysis that
  produced the masked-handler arithmetic was on line 0, the software line at bit 3

The delta range is the same family as the window the fix addresses, and the accrual still happens here while the
two red seeds went to zero on the same build. So whatever withholds these interrupts is not what the reds were
hitting. The diagnosis belongs to tb-infra-2; this record states the measurement only.

One fact kept separate because it has a different owner: the same run fires `sva_rvfi_irq_valid_exclusive` six
times, the property already ruled wrong and unchanged, and that property rather than the checker decided the run's
verdict.

## Method

Fires are counted with the not-taken pattern, not by lines mentioning the identifier, because the identifier also
appears on UVM end-of-simulation per-id tally lines. This run carries zero tally lines and both counts agree at
258, but that was checked rather than assumed.
