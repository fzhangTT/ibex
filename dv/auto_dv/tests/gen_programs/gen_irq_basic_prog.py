#!/usr/bin/env python3
"""gen_irq_basic_prog.py: plain interrupt entry and return for gen_test_irq_basic.

Intent (gen_test_plan.md TP-IRQ-001..004): each of the four interrupt line classes is taken alone
through the vectored mtvec table and returned from with mret. Software is cause 3 at vector base
+ 0x0C, timer cause 7 at + 0x1C, external cause 11 at + 0x2C, and fast id n cause 16 + n at
+ 0x40 + 4n. No debug-request and no NMI shape is programmed here; the NMI line (driver bit 18) is
never armed, and mie has no bit for it.

The program does not decide WHEN an interrupt arrives: the cocotb test drives one line at a time
through the bridge's IRQ_SET command while this program spins. Each entry is therefore taken
alone, which is the precondition TP-IRQ-002 and TP-IRQ-003 state. The handler reports five raw
words per entry to GEN_MM_EOT_ADDR (vector index, mcause, mepc, mtval, mstatus), releases the held
line with a store to GEN_MM_IRQ_ACK_ADDR, counts the entry and returns with mret.

Checking is order-independent by construction: the test chooses the order it drives the lines, so
the program cannot predict it and does not try. Every report tuple is self-consistent (the vector
index it entered through determines the mcause it must carry), and the multiset of vector indices
over the run must equal the armed set. A cross-component ordering contract would be the fragile
way to check the same thing.

emit(plan) -> the RV32IMC assembly text; plan(seed) -> the expectations the test compares against.
"""

import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dv.auto_dv.tests.gen_programs import gen_prog_const as const  # noqa: E402

STREAM = "{seed}:program:irq_basic"
RED_STREAM = "{seed}:red"
RED_ITEMS = ("TP-IRQ-001", "TP-IRQ-002", "TP-IRQ-003", "TP-IRQ-004")
# the vector a red fixture deviates on: exactly one item's fire check fails by design
RED_VECTOR = {"TP-IRQ-001": 3, "TP-IRQ-002": 7, "TP-IRQ-003": 11, "TP-IRQ-004": 16}

# Line classes. The cause is the mcause low field; the vector offset is 4 * cause in vectored mode.
CAUSE_SOFTWARE = 3
CAUSE_TIMER = 7
CAUSE_EXTERNAL = 11
FAST_CAUSE_LO = 16                 # ibex_pkg CSR_MFIX_BIT_LOW
N_FAST = 15                        # $bits(irqs_t.irq_fast)
FAST_CAUSES = tuple(range(FAST_CAUSE_LO, FAST_CAUSE_LO + N_FAST))
ARMED_CAUSES = (CAUSE_SOFTWARE, CAUSE_TIMER, CAUSE_EXTERNAL) + FAST_CAUSES

MCAUSE_INTERRUPT = 0x8000_0000     # mcause bit 31 for an interrupt
MSTATUS_MIE = 1 << 3
MSTATUS_MPIE = 1 << 7
MTVEC_MODE_VECTORED = 1

# mie bits: MSIE 3, MTIE 7, MEIE 11, fast 16..30. No bit exists for the NMI, which is why an NMI
# shape cannot be armed here even by accident.
MIE_MASK = sum(1 << c for c in ARMED_CAUSES)

WORDS_PER_ENTRY = 5                # vector index, mcause, mepc, mtval, mstatus
VEC_SLOTS = FAST_CAUSE_LO + N_FAST  # 31 slots: causes 0..30
ARMED_MARK = 0xA5C3_0001           # first report word: mtvec, mie and mstatus.MIE are all in place

# Registers the handler owns for the whole run; the spin loop never writes them.
REG_EOT = "s11"                    # GEN_MM_EOT_ADDR
REG_ACK = "s10"                    # GEN_MM_IRQ_ACK_ADDR
REG_COUNT = "s9"                   # entries handled
REG_TARGET = "s8"                  # entries expected
REG_UNEXPECTED = "s7"              # unexpected-trap counter (exceptions, or an unarmed vector)
REG_SEEN = "s6"                    # mask of vectors already reported; a repeat reports nothing


@dataclass
class Entry:
    """One expected interrupt entry, keyed by the vector it must arrive through."""
    cause: int
    vector_offset: int
    mcause: int
    line: str                      # software | timer | external | fast<n>
    driver_bit: int                # gen_irq_driver level[] bit the test commands


@dataclass
class Plan:
    seed: int
    red: bool
    red_item: str
    entries: list = field(repr=False)
    k: int                         # report words the program stores
    min_retired: int
    mtvec_base_sym: str
    words_per_entry: int = WORDS_PER_ENTRY


def _driver_bit(cause):
    """gen_irq_driver level[] bit for a cause: 0 sw, 1 timer, 2 ext, 3..17 fast, 18 nm (unused)."""
    if cause == CAUSE_SOFTWARE:
        return 0
    if cause == CAUSE_TIMER:
        return 1
    if cause == CAUSE_EXTERNAL:
        return 2
    return 3 + (cause - FAST_CAUSE_LO)


def _line_name(cause):
    if cause == CAUSE_SOFTWARE:
        return "software"
    if cause == CAUSE_TIMER:
        return "timer"
    if cause == CAUSE_EXTERNAL:
        return "external"
    return f"fast{cause - FAST_CAUSE_LO}"


def plan(seed, red=False, red_item=None):
    rng = random.Random(STREAM.format(seed=seed))
    if red and red_item is None:
        red_item = random.Random(RED_STREAM.format(seed=seed)).choice(RED_ITEMS)
    entries = [Entry(cause=c,
                     vector_offset=4 * c,
                     mcause=MCAUSE_INTERRUPT | c,
                     line=_line_name(c),
                     driver_bit=_driver_bit(c))
               for c in ARMED_CAUSES]
    rng.shuffle(entries)            # the order the plan RECORDS; the test drives its own order
    # armed marker + per-entry words + the final unexpected-trap count
    k = 1 + len(entries) * WORDS_PER_ENTRY + 1
    # one entry costs the handler's stores and the mret; the spin loop retires at least one branch
    min_retired = len(entries) * 12 + 32
    return Plan(seed=seed, red=bool(red), red_item=red_item, entries=entries, k=k,
                min_retired=min_retired, mtvec_base_sym="gen_irq_vectors")


def _vector_table(p):
    """The vectored mtvec table: slot 0 is the exception entry, an armed cause jumps to its stub,
    every other slot lands on the unexpected path so a stray vector is counted, not silently taken."""
    armed = {e.cause for e in p.entries}
    out = [".balign 256", f"{p.mtvec_base_sym}:"]
    for slot in range(VEC_SLOTS):
        if slot in armed:
            out.append(f"  j gen_irq_vec_{slot}")
        else:
            out.append("  j gen_irq_unexpected")
    return out


def _stubs(p):
    """One 2-instruction stub per armed vector: it records WHICH vector was entered, which is the
    fact the mcause check is verified against."""
    out = []
    for e in sorted(p.entries, key=lambda x: x.cause):
        out += [f"gen_irq_vec_{e.cause}:",
                f"  li a3, {e.cause}",
                "  j gen_irq_common"]
    return out


def _handler(p):
    """The common handler: report the entry, release the line, count it, return.

    The five words are stored RAW; the test does the comparing. The ack store comes after the
    reports so a handler that faults mid-report cannot look like a completed entry.
    """
    red_vec = RED_VECTOR[p.red_item] if (p.red and p.red_item in RED_VECTOR) else None
    lines = ["gen_irq_common:",
             "  # only the FIRST entry through a vector reports: under a non-quiet regime the driver",
             "  # adds autonomous entries, and the report channel needs an exact count either way",
             "  li   t2, 1",
             f"  sll  t2, t2, a3",
             f"  and  t0, {REG_SEEN}, t2",
             "  bnez t0, gen_irq_repeat",
             f"  or   {REG_SEEN}, {REG_SEEN}, t2",
             "  csrr a4, mcause",
             "  csrr a5, mepc",
             "  csrr t0, mtval",
             "  csrr t1, mstatus"]
    if red_vec is not None:
        # RED FIXTURE: on ONE vector only, the reported mcause has its interrupt bit cleared, so
        # exactly that item's mcause check fails while every other item, the vector indices and the
        # entry count stay right. Pinning the deviation to one vector is what makes the red
        # attributable to a single fire_tp method.
        lines += [f"  li   t2, {red_vec}",
                  "  bne  a3, t2, gen_irq_no_red",
                  "  li   t2, 0x80000000",
                  "  xor  a4, a4, t2",
                  "gen_irq_no_red:"]
    lines += [f"  sw   a3, 0({REG_EOT})",
              f"  sw   a4, 0({REG_EOT})",
              f"  sw   a5, 0({REG_EOT})",
              f"  sw   t0, 0({REG_EOT})",
              f"  sw   t1, 0({REG_EOT})",
              f"  sw   a3, 0({REG_ACK})",
              f"  addi {REG_COUNT}, {REG_COUNT}, 1",
              "  mret",
              "",
              "gen_irq_repeat:",
              "  # an entry through a vector already reported: release the line and return, silently",
              f"  sw   a3, 0({REG_ACK})",
              "  mret",
              "",
              "gen_irq_unexpected:",
              f"  addi {REG_UNEXPECTED}, {REG_UNEXPECTED}, 1",
              "  csrr a4, mepc",
              "  addi a4, a4, 4",
              "  csrw mepc, a4",
              "  mret"]
    return lines


def armed_mask(p):
    """The bit per armed vector index; the spin loop exits when every one has reported."""
    m = 0
    for e in p.entries:
        m |= 1 << e.cause
    return m


def _body(p):
    b = ["_start:",
         "  # the handler's registers, set before any interrupt can be taken",
         f"  li   {REG_EOT}, GEN_MM_EOT_ADDR",
         f"  li   {REG_ACK}, GEN_MM_IRQ_ACK_ADDR",
         f"  li   {REG_COUNT}, 0",
         f"  li   {REG_UNEXPECTED}, 0",
         f"  li   {REG_SEEN}, 0",
         f"  li   {REG_TARGET}, {armed_mask(p):#x}",
         "",
         "  # vectored mtvec at a 256-byte-aligned base (TP-IRQ-001 precondition)",
         f"  la   t0, {p.mtvec_base_sym}",
         f"  ori  t0, t0, {MTVEC_MODE_VECTORED}",
         "  csrw mtvec, t0",
         "",
         "  # arm every line class this entry owns; no mie bit exists for the NMI",
         f"  li   t0, {MIE_MASK:#x}",
         "  csrw mie, t0",
         "  # the armed marker BEFORE mstatus.MIE: no interrupt can be taken until the marker is out,",
         "  # so the report stream always opens with it and every entry is taken from the spin loop",
         f"  li   t0, {ARMED_MARK:#x}",
         f"  sw   t0, 0({REG_EOT})",
         "",
         f"  li   t0, {MSTATUS_MIE:#x}",
         "  csrs mstatus, t0",
         "",
         "  # spin until every armed vector has reported once; a repeat entry does not count, so a",
         "  # non-quiet regime adds entries without changing the report count",
         "gen_irq_wait:",
         f"  bne  {REG_SEEN}, {REG_TARGET}, gen_irq_wait",
         "",
         "  # the run's own unexpected-trap count is the last report word",
         f"  sw   {REG_UNEXPECTED}, 0({REG_EOT})",
         "",
         "  la   t0, tohost",
         f"  li   t1, {const.TOHOST_PASS}",
         "  sw   t1, 0(t0)",
         "gen_irq_done:",
         "  j gen_irq_done",
         ""]
    b += _handler(p) + [""] + _stubs(p) + [""] + _vector_table(p)
    return b


HEADER = """# gen_irq_basic_prog.py output: plain interrupt entry and return for gen_test_irq_basic
# (seed {seed}{red}). Each armed line is taken alone through the vectored mtvec table; the handler
# stores {w} raw words per entry to GEN_MM_EOT_ADDR ({k} report words with the final unexpected-trap
# count), releases the line at GEN_MM_IRQ_ACK_ADDR and returns with mret, then tohost {tohost}.
# Generated; do not edit.
.include "gen_mmio_map.h"
.option norvc
.section .text
.globl _start
"""

FOOTER = """
.section .data
.align 6
.globl tohost
tohost:   .dword 0
.globl fromhost
fromhost: .dword 0
.align 2
.globl gen_min_retired
gen_min_retired: .word {min_retired}
"""


def emit(p):
    text = HEADER.format(seed=p.seed, red=f", red fixture {p.red_item}" if p.red else "",
                         w=WORDS_PER_ENTRY, k=p.k, tohost=const.TOHOST_PASS)
    text += "\n".join(_body(p)) + "\n"
    text += FOOTER.format(min_retired=p.min_retired)
    assert all(ord(c) < 128 for c in text), "gen_irq_basic_prog: non-ASCII output"
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", action="store_true", help="deviate on one item's intent (drawn from the seed unless --red-item)")
    ap.add_argument("--red-item", choices=RED_ITEMS, help="the item the red program deviates on (needs --red)")
    args = ap.parse_args()
    if args.red_item and not args.red:
        ap.error("--red-item needs --red")
    p = plan(args.seed, args.red, args.red_item)
    with open(args.out, "w") as f:
        f.write(emit(p))
    print(f"gen_irq_basic_prog seed={p.seed} red={p.red} red_item={p.red_item} k={p.k} "
          f"entries={len(p.entries)} min_retired={p.min_retired} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
