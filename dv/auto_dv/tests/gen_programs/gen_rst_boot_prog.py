#!/usr/bin/env python3
"""gen_rst_boot_prog: per-seed program generator of gen_test_rst_boot (test-plan group gen_rst_boot).

The program observes the boot state of the core through architectural reads and stores every RAW
observation to the EOT MMIO register (GEN_MM_EOT_ADDR, one report word per store, plan order), then
ends with tohost TOHOST_PASS. It never self-checks: the test (dv/auto_dv/tests/gen_test_rst_boot.py)
compares self.reports[i] with plan(seed).reports[i]. Every CSR read lands in a register other than x0,
so the ISA comparator sees every value (the shim gaps on cpuctrlsts bit 8 and tdata1 are T-102 rows).

Scenario (RV32IMC, every instruction 4 bytes through .option norvc so a trap handler can skip the
trapping instruction with mepc + 4):
  1. TP-RST-003: csrr mtvec before any write (expected boot page | 1); then mtvec = the program's
     256-byte aligned vector table | 1, so any unexpected trap in the read phase is counted and
     skipped instead of spinning at the empty boot page.
  2. TP-RST-006: csrr mstatus (MSTATUS_RESET) and csrr mie (0) as the first instructions after that.
  3. TP-RST-007: the M-mode-readable reset CSRs (mcause, mepc, mtval, mscratch, cpuctrlsts,
     mcountinhibit, mcounteren, mseccfg, pmpcfg*, pmpaddr* for the configured PMPNumRegions,
     tselect, tdata1) read in a seed-shuffled order, each through a read-only CSR form drawn from
     W-CSROP, before any write.
  4. Writes: one PMP entry (seed-drawn index) = NAPOT whole space, RWX, so U-mode can execute;
     mepc = one of four U-mode landing pads (seed drawn: the random mepc of TP-RST-006); mret
     (MPP = U at reset lands in U-mode).
  5. The pad computes a seed-drawn ALU result in U-mode, then reads mstatus: an M-mode CSR read is an
     illegal instruction in U-mode. The trap handler reports mcause, mstatus (MPP = U) and mepc, sets
     MPP = M, and returns to mepc + 4; the pad then reports its result from M-mode.
  6. The program reports its unexpected-trap counter (every trap from M-mode or any interrupt slot
     counts one and is skipped) and stores tohost TOHOST_PASS.
Not covered here (no program-visible channel): dcsr/dpc/dscratch0/1 (debug mode only), the ecall
through the reset mtvec (the boot page holds no vector table), pin-level and RVFI facts.

Red fixtures (the expectation never changes; exactly one item's fire-check must fail):
  TP-RST-003: the vector table is installed BEFORE the mtvec read (a write precedes the read).
  TP-RST-006: the mstatus reset read-back word is stored with MPIE toggled.
  TP-RST-007: mscratch is written with a nonzero value before the reset-read phase.
Without --red-item the item is drawn from random.Random(f"{seed}:red"); the program stream
random.Random(f"{seed}:program:rst_boot") is consumed identically in every case.

CLI: python3 gen_rst_boot_prog.py --seed N --out <file.S> [--red [--red-item TP-RST-003|TP-RST-006|TP-RST-007]]
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

STREAM = "{seed}:program:rst_boot"
RED_STREAM = "{seed}:red"
RED_ITEMS = ("TP-RST-003", "TP-RST-006", "TP-RST-007")

# gen_test_plan.md Section 4.7 "Layer-1 weight tables": W-CSROP (CSR op form).
W_CSROP = {"csrrw": 25, "csrrs": 20, "csrrc": 20, "csrrwi": 15, "csrrsi": 10, "csrrci": 10}
# A read before any write uses the read-only forms of W-CSROP (csrrs/csrrc rs1 == x0, csrrsi/csrrci uimm == 0).
READ_FORMS = {f: W_CSROP[f] for f in ("csrrs", "csrrc", "csrrsi", "csrrci")}

MSTATUS_RESET = const.MSTATUS_RESET       # MIE 0, MPIE 1, MPP U (gen_test_plan.md TP-RST-006)
MSTATUS_MPIE = 1 << 7
MSTATUS_MPP_M = 3 << 11
MSTATUS_TRAP_FROM_U = MSTATUS_MPIE        # in the handler: MIE 0, MPIE 1 (MIE was 1 after the mret), MPP U
TDATA1_RESET = 0x28001048    # doc mismatch D4 (gen_test_plan.md TP-RST-007)
MCAUSE_ILLEGAL_INSN = 2
PMP_NAPOT_RWX = 0x1F         # A = NAPOT, X W R; L = 0 so M-mode is unaffected
N_PADS = 4
PAD_OPS = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "xor": lambda a, b: a ^ b,
           "or": lambda a, b: a | b, "and": lambda a, b: a & b}
# Registers a CSR read may land in (never x0: the comparator must see every value); t6 (report address),
# s11 (unexpected-trap counter), s9/s10 (filler), a0..a2 (landing pad) and t0/t1 (trap handler) are reserved.
RD_POOL = ("t2", "t3", "t4", "t5", "a3", "a4", "a5", "a6", "a7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8")
MASK32 = 0xFFFFFFFF


def _pmp_regions():
    """PMPNumRegions of the build configuration (ibex_configs.yaml, the one origin, as the sibling generators read it)."""
    import yaml
    cfg = yaml.safe_load((ROOT / "ibex_configs.yaml").read_text())[const.CONFIG_NAME]
    assert int(cfg["PMPEnable"]) == 1, "gen_rst_boot_prog: the configuration has no PMP"
    return int(cfg["PMPNumRegions"])


NUM_PMP_REGIONS = _pmp_regions()
NUM_PMPCFG = (NUM_PMP_REGIONS + 3) // 4


def csr_addr(name):
    """CSR address by name; pmpcfg<i>/pmpaddr<i> through the shared helpers so the count is the configuration's."""
    if name.startswith("pmpaddr"):
        return const.pmpaddr(int(name[len("pmpaddr"):]))
    if name.startswith("pmpcfg"):
        return const.pmpcfg(int(name[len("pmpcfg"):]))
    return const.CSR[name]


@dataclass
class Expect:
    """kind: const (value), mtvec_reset (boot page | 1), cpuctrlsts_reset (bit 8 = key valid at the
    read), symbol (address of a program symbol from the image sidecar). The test resolves the
    non-const kinds from the TB-side facts it can see."""
    kind: str
    value: object = None


@dataclass
class Report:
    name: str
    item: str
    expect: Expect


@dataclass
class CsrRead:
    name: str
    form: str
    rd: str


@dataclass
class Plan:
    seed: int
    red: bool
    red_item: str = None                             # the item whose intent the program deviates on (red only)
    red_value: int = 0                               # nonzero mscratch value of the TP-RST-007 red
    reads: list = field(default_factory=list)       # CsrRead in program order (reports 0..len-1)
    pmp_entry: int = 0
    pad: int = 0
    pad_op: str = "add"
    pad_a: int = 0
    pad_b: int = 0
    pad_result: int = 0
    fillers: dict = field(default_factory=dict)     # block name -> list of filler instruction texts
    reports: list = field(default_factory=list)     # Report in store order
    k: int = 0
    min_retired: int = 0

    def index(self, name):
        return next(i for i, r in enumerate(self.reports) if r.name == name)


def _rst007_list():
    """TP-RST-007 CSRs readable from M-mode with their reset expectation (the plan's pass criteria: every
    PMP CSR of the configured regions resets to zero, mseccfg included)."""
    out = [("mcause", Expect("const", 0)), ("mepc", Expect("const", 0)), ("mtval", Expect("const", 0)),
           ("mscratch", Expect("const", 0)), ("cpuctrlsts", Expect("cpuctrlsts_reset")),
           ("mcountinhibit", Expect("const", 0)), ("mcounteren", Expect("const", 0)), ("mseccfg", Expect("const", 0))]
    out += [(f"pmpcfg{i}", Expect("const", 0)) for i in range(NUM_PMPCFG)]
    out += [(f"pmpaddr{i}", Expect("const", 0)) for i in range(NUM_PMP_REGIONS)]
    out += [("tselect", Expect("const", 0)), ("tdata1", Expect("const", TDATA1_RESET))]
    return out


def _draw_form(rng):
    names = list(READ_FORMS)
    return rng.choices(names, weights=[READ_FORMS[n] for n in names], k=1)[0]


def _fillers(rng):
    """0..2 ALU instructions on the filler registers (TP-RST-006 'filler')."""
    out = []
    for _ in range(rng.randint(0, 2)):
        kind = rng.choice(("addi", "xori", "add"))
        if kind == "add":
            out.append("add  s9, s9, s10")
        else:
            out.append(f"{kind} s{rng.choice((9, 10))}, s{rng.choice((9, 10))}, {rng.randint(-2048, 2047)}")
    return out


def plan(seed, red=False, red_item=None):
    """The per-seed plan; red_item selects the deviating item (drawn from the red stream when red and None)."""
    if red_item is not None and red_item not in RED_ITEMS:
        raise ValueError(f"gen_rst_boot_prog: red item {red_item} not in {RED_ITEMS}")
    red = bool(red) or red_item is not None
    rr = random.Random(RED_STREAM.format(seed=int(seed)))
    drawn_item = rr.choice(RED_ITEMS)
    red_value = rr.randrange(1, MASK32 + 1)
    rng = random.Random(STREAM.format(seed=int(seed)))
    p = Plan(seed=int(seed), red=red, red_item=(red_item or drawn_item) if red else None,
             red_value=red_value if red else 0)
    reports = []

    def read(name, item, expect):
        p.reads.append(CsrRead(name, _draw_form(rng), rng.choice(RD_POOL)))
        reports.append(Report(name, item, expect))

    read("mtvec", "TP-RST-003", Expect("mtvec_reset"))
    read("mstatus", "TP-RST-006", Expect("const", MSTATUS_RESET))
    read("mie", "TP-RST-006", Expect("const", 0))          # also a TP-RST-007 CSR (one observation, two items)
    rst007 = _rst007_list()
    rng.shuffle(rst007)
    for name, exp in rst007:
        read(name, "TP-RST-007", exp)
    p.pmp_entry = rng.randrange(NUM_PMP_REGIONS)
    p.pad = rng.randrange(N_PADS)
    p.pad_op = rng.choice(list(PAD_OPS))
    # sensitizing operands: never zero, never equal, high bit set in one of them
    p.pad_a = rng.randrange(1, 1 << 31) | (1 << 31)
    p.pad_b = rng.randrange(1, 1 << 31)
    p.pad_result = PAD_OPS[p.pad_op](p.pad_a, p.pad_b) & MASK32
    p.fillers = {blk: _fillers(rng) for blk in ("after_003", "after_006", "after_007", "before_mret")}
    reports.append(Report("trap_mcause", "TP-RST-006", Expect("const", MCAUSE_ILLEGAL_INSN)))
    reports.append(Report("trap_mstatus", "TP-RST-006", Expect("const", MSTATUS_TRAP_FROM_U)))
    reports.append(Report("trap_mepc", "TP-RST-006", Expect("symbol", f"gen_upad{p.pad}_trap")))
    reports.append(Report("pad_result", "TP-RST-006", Expect("const", p.pad_result)))
    reports.append(Report("unexpected_traps", "TP-RST-006", Expect("const", 0)))
    p.reports = reports
    p.k = len(reports)
    p.min_retired = _count_retired(_body(p))
    return p


def _csr_read_insn(r):
    csr = csr_addr(r.name)
    if r.form in ("csrrs", "csrrc"):
        return f"{r.form} {r.rd}, 0x{csr:03x}, x0"
    return f"{r.form} {r.rd}, 0x{csr:03x}, 0"


def _body(p):
    """The executed main path as (counted, text) pairs; counted = an instruction that retires once on
    the RTL path (li/la count 1 although they may expand to 2: a lower bound)."""
    L = []

    def ins(text, counted=True):
        L.append((counted, "  " + text))

    def note(text):
        L.append((False, "  # " + text))

    def lab(text):
        L.append((False, text))

    def emit_read(r):
        note(f"{r.name} (0x{csr_addr(r.name):03x})")
        ins(_csr_read_insn(r))
        if p.red_item == "TP-RST-006" and r.name == "mstatus":
            ins(f"xori {r.rd}, {r.rd}, 0x{MSTATUS_MPIE:x}")   # red: MPIE toggled in the stored observation
        ins(f"sw   {r.rd}, 0(t6)")

    def emit_fillers(name):
        for f in p.fillers.get(name, []):
            ins(f)

    def emit_vector_install():
        note("trap vector table (256-byte aligned; Ibex keeps MODE vectored): an unexpected trap in the")
        note("read phase is counted and skipped, never a spin at the boot page")
        ins("la   t0, gen_trap_vec")
        ins("ori  t0, t0, 1")
        ins(f"csrw 0x{csr_addr('mtvec'):03x}, t0")

    lab("_start:")
    ins("li   t6, GEN_MM_EOT_ADDR")
    ins("li   s11, 0")
    ins("li   s9, 0x5a5a")
    ins("li   s10, 0x0f0f")
    reads = {r.name: r for r in p.reads}
    if p.red_item == "TP-RST-003":
        note("red: the mtvec write precedes the read")
        emit_vector_install()
    note("TP-RST-003: mtvec before any write")
    emit_read(reads["mtvec"])
    if p.red_item != "TP-RST-003":
        emit_vector_install()
    emit_fillers("after_003")
    note("TP-RST-006: mstatus and mie at boot (M-mode-only CSR reads that must not trap)")
    emit_read(reads["mstatus"])
    emit_read(reads["mie"])
    emit_fillers("after_006")
    if p.red_item == "TP-RST-007":
        note("red: mscratch written before its reset read")
        ins(f"li   t0, 0x{p.red_value:08x}")
        ins(f"csrw 0x{csr_addr('mscratch'):03x}, t0")
    note("TP-RST-007: reset CSRs in a seed-shuffled order, before any write")
    for r in p.reads:
        if r.name not in ("mtvec", "mstatus", "mie"):
            emit_read(r)
    emit_fillers("after_007")
    note(f"PMP entry {p.pmp_entry}: NAPOT whole space, RWX, unlocked (U-mode may execute the pad)")
    ins("li   t0, 0xffffffff")
    ins(f"csrw 0x{const.pmpaddr(p.pmp_entry):03x}, t0")
    ins(f"li   t0, 0x{PMP_NAPOT_RWX << (8 * (p.pmp_entry % 4)):08x}")
    ins(f"csrw 0x{const.pmpcfg(p.pmp_entry // 4):03x}, t0")
    emit_fillers("before_mret")
    note(f"mret with mepc = landing pad {p.pad}: MPP = U at reset, so the pad runs in U-mode")
    ins(f"la   t0, gen_upad{p.pad}")
    ins(f"csrw 0x{csr_addr('mepc'):03x}, t0")
    ins("mret")
    lab("gen_after_pad:")
    ins("sw   s11, 0(t6)")
    ins(f"li   gp, {const.TOHOST_PASS}")
    ins("la   t5, tohost")
    ins("sw   gp, 0(t5)")
    lab("1:")
    ins("j    1b", counted=False)
    # landing pads (only pad p.pad executes; the trapping csrr is not counted as retired)
    for i in range(N_PADS):
        run = i == p.pad
        lab(f"gen_upad{i}:")
        ins(f"li   a0, 0x{p.pad_a:08x}", counted=run)
        ins(f"li   a1, 0x{p.pad_b:08x}", counted=run)
        ins(f"{p.pad_op:<4} a0, a0, a1", counted=run)
        lab(f".globl gen_upad{i}_trap")
        lab(f"gen_upad{i}_trap:")
        ins(f"csrr a2, 0x{csr_addr('mstatus'):03x}", counted=False)   # illegal in U-mode: the handler returns to +4 in M-mode
        ins("sw   a0, 0(t6)", counted=run)
        ins("j    gen_after_pad", counted=run)
    # trap handler: the U-mode illegal instruction is the expected trap; anything else is counted and skipped
    lab(".align 8")
    lab("gen_trap_vec:")
    ins("j    gen_exc", )
    for _ in range(31):
        ins("j    gen_unexpected_irq", counted=False)
    lab("gen_exc:")
    ins(f"csrr t0, 0x{csr_addr('mstatus'):03x}")
    ins("srli t1, t0, 11")
    ins("andi t1, t1, 3")
    ins("bnez t1, gen_exc_m")
    ins(f"csrr t0, 0x{csr_addr('mcause'):03x}")
    ins("sw   t0, 0(t6)")
    ins(f"csrr t0, 0x{csr_addr('mstatus'):03x}")
    ins("sw   t0, 0(t6)")
    ins(f"csrr t0, 0x{csr_addr('mepc'):03x}")
    ins("sw   t0, 0(t6)")
    ins("addi t0, t0, 4")
    ins(f"csrw 0x{csr_addr('mepc'):03x}, t0")
    ins(f"li   t1, 0x{MSTATUS_MPP_M:04x}")
    ins(f"csrs 0x{csr_addr('mstatus'):03x}, t1")
    ins("mret")
    lab("gen_exc_m:")
    ins("addi s11, s11, 1", counted=False)
    ins(f"csrr t0, 0x{csr_addr('mepc'):03x}", counted=False)
    ins("addi t0, t0, 4", counted=False)
    ins(f"csrw 0x{csr_addr('mepc'):03x}, t0", counted=False)
    ins("mret", counted=False)
    lab("gen_unexpected_irq:")
    ins("addi s11, s11, 1", counted=False)
    ins("mret", counted=False)
    return L


def _count_retired(body):
    return sum(1 for counted, _ in body if counted)


HEADER = """# gen_rst_boot_prog.py output: reset and boot state observations for gen_test_rst_boot
# (seed {seed}{red}). Every observation is stored RAW to GEN_MM_EOT_ADDR in plan order ({k} report
# words), then tohost {tohost}. Generated; do not edit.
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
    text = HEADER.format(seed=p.seed, red=f", red fixture {p.red_item}" if p.red else "", k=p.k, tohost=const.TOHOST_PASS)
    text += "\n".join(t for _, t in _body(p)) + "\n"
    text += FOOTER.format(min_retired=p.min_retired)
    assert all(ord(c) < 128 for c in text), "gen_rst_boot_prog: non-ASCII output"
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
    print(f"gen_rst_boot_prog seed={p.seed} red={p.red} red_item={p.red_item} k={p.k} min_retired={p.min_retired} "
          f"pad={p.pad} pmp_entry={p.pmp_entry} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
