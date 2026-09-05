# irq checker fix re-runs, retained

Written 2026-09-05T10:56Z by the Runtime Manager. tb-infra-2's checker fix landed at 9c7f8f6; this block re-runs
the three seeds whose behaviour the fix was expected to change, with the expectation filed BEFORE the runs.
tb-infra-2 and the DV Lead read it for the irq entry's promotion conditions.

The record beside this file is BYTE-IDENTICAL to the served copy under `dv/auto_dv/work/runtime/done/`, which git
does not track.

| file | bytes | sha256 |
|---|---|---|
| `gen_chkfix_reruns.yaml` | 6533 | `2a51db4b40c5485b4c15a1880ddeddee18cbaf019275590b61db84d7644a00c7` |

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

One fact kept separate because it has a different owner: the same run fires `sva_rvfi_irq_valid_exclusive` three
times, the property already ruled wrong and unchanged, and that property rather than the checker decided the
run's verdict.

## Corrigendum 2026-09-05T11:47Z

TWO CORRECTIONS, the first a repeat of an error closed the same hour.

THE FIRING COUNT WAS WRONG. This page and the record first said the property fires SIX times. It fires THREE.
Six lines mention the identifier and they pair up: each firing emits a VCS assertion-source line naming
`gen_protocol_props.sv:299` and then a UVM_ERROR line. Counting only the UVM_ERROR lines gives 3, which is also
what rtl-arch's ibus-signature table records for this seed. Found by tb-infra-2.

It is the same shape as the 343-against-334 count on the irq_entry fires, closed earlier the same hour, where
nine of 343 were end-of-simulation tally lines rather than fires. The rule was written down and then broken
again in a different disguise: A LINE MENTIONING AN IDENTIFIER IS NOT A FIRING.

THE SEED IS DIAGNOSED AND IT IS NOT A CHECKER DEFECT, so this page's "second mechanism" framing is superseded.
Every figure above reproduces exactly on tb-infra-2's own read. The answer is ordering: the first
model-versus-DUT instruction divergence is at 9290500, about 6443 cycles BEFORE the first fire at 15737500,
with 23387 instruction mismatches already reported and the core executing zero at `pc 0x80000022` while the
model is at `0x80000154`; a bus anomaly precedes even that. The fires are DOWNSTREAM of a fetch and execution
breakdown, and at every one of them the interrupt was takeable and a running core would have taken it. The
checker is telling the truth, and tb-infra-2's landing neither fixes nor claims this seed.

The three timing figures were re-derived here rather than adopted, and one near-miss is recorded with them:
the gap was first computed as 64470 cycles by dividing the tick difference by 100, where the tick is 10 ps
against a 10 ns clock so the divisor is 1000. Caught before it was written down.

The export run on this seed is no longer needed for the diagnosis and no slot was spent on it.

### CORRIGENDUM 2026-09-05T12:46Z: the gap is 6447 cycles, and the earliest mechanism is named

TWO CORRECTIONS to the block above, neither of which changes its conclusion.

THE GAP IS 6447, not "about 6443". The record's own ticks give it: (15737500 - 9290500) / 1000 = 6447. The
near-miss recorded above, 64470 from dividing by 100, is 6447 with the wrong divisor, so the right figure was
one step away in this page's own text. Raised by the Orchestrator against the round-2 form's re-derivation.

"A BUS ANOMALY PRECEDES EVEN THAT" IS TRUE AND IS NOT THE EARLIEST. Censusing every UVM_ERROR line of the run
(counting firings, not lines mentioning an identifier) gives, by first firing: sva_rvfi_irq_valid_exclusive at
cycle 6591.5 with 3 firings, sva_ibus_gnt_only_with_req at 9250.5 with 1, the divergent store's LSU-stage
unmapped write at 9284.5, isa_insn at 9290.5 with 23387, irq_entry at 15737.5 with 258, and
sva_ibus_outstanding_max at 26503.5 with 450021. The earliest mechanism is the RVFI property, 2659 cycles
before the bus one. rtl-arch's committed table already listed it first; one sentence of its Section 3, since
corrected, read as though the grant fired first.

ONE READING OF MINE WITHDRAWN rather than left in the record. I offered the unmapped write to 0x40000000 as a
possible route to the wedged core. It is not a separate event: order 462 at 9290500 is pc=80000154 with dut
insn=0062a023, a full-word store, and that line carries mem=40000000 with a 1111 mask, so the write at 9284500
is the same instruction six cycles earlier at the LSU stage. It is a consequence of the wrong word, not a route
to it. Established by rtl-arch and verified against both this build and the wave's.

The conclusion of the block is unaffected: the fires are downstream of a fetch and execution breakdown and the
checker is telling the truth.

## Method

Fires are counted with the not-taken pattern, not by lines mentioning the identifier, because the identifier also
appears on UVM end-of-simulation per-id tally lines. This run carries zero tally lines and both counts agree at
258, but that was checked rather than assumed.
