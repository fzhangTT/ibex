#!/usr/bin/env python3
"""gen_rst_boot_prog: per-seed program generator of gen_test_rst_boot (test-plan group gen_rst_boot).

The program observes the boot state of the core through architectural reads and stores every RAW
observation to the EOT MMIO register (GEN_MM_EOT_ADDR, one report word per store, plan order), then
ends with tohost 1. It never self-checks: the test (dv/auto_dv/tests/gen_test_rst_boot.py) compares
self.reports[i] with plan(seed).reports[i].

Scenario (RV32IMC, every instruction 4 bytes through .option norvc so a trap handler can skip the
trapping instruction with mepc + 4):
  1. TP-RST-003: csrr mtvec before any write (expected boot page | 1); then mtvec = the program's
     256-byte aligned vector table | 1, so any unexpected trap in the read phase is counted and
     skipped instead of spinning at the empty boot page (the standalone Spike of --spike-check has
     no cpuctrlsts and traps on that read; the RTL must not).
  2. TP-RST-006: csrr mstatus (0x80) and csrr mie (0) as the first instructions after that.
  3. TP-RST-007: the M-mode-readable reset CSRs (mcause, mepc, mtval, mscratch, cpuctrlsts,
     mcountinhibit, mcounteren, mseccfg, pmpcfg0..3, pmpaddr0..15, tselect, tdata1) read in a
     seed-shuffled order, each through a read-only CSR form drawn from W-CSROP, before any write.
  4. Writes: one PMP entry (seed-drawn index) = NAPOT whole space, RWX, so U-mode can execute;
     mepc = one of four U-mode landing pads (seed drawn: the random mepc of TP-RST-006); mret
     (MPP = U at reset lands in U-mode).
  5. The pad computes a seed-drawn ALU result in U-mode, then reads mstatus: an M-mode CSR read is an
     illegal instruction in U-mode. The trap handler reports mcause, mstatus (MPP = U) and mepc, sets
     MPP = M, and returns to mepc + 4; the pad then reports its result from M-mode.
  6. The program reports its unexpected-trap counter (every trap from M-mode or any interrupt slot
     counts one and is skipped) and stores tohost 1.
Not covered here (no program-visible channel): dcsr/dpc/dscratch0/1 (debug mode only), the ecall
through the reset mtvec (the boot page holds no vector table), pin-level and RVFI facts.

red=True deviates on exactly one intent: the mstatus reset read-back word is stored with MPIE
toggled (xori 0x80), so fire_tp_rst_006 must fail while every other report stays true.

CLI: python3 gen_rst_boot_prog.py --seed N --out <file.S> [--red]
"""
import argparse
import random
from dataclasses import dataclass, field

STREAM = "{seed}:program:rst_boot"

# gen_test_plan.md Section 4.7 "Layer-1 weight tables": W-CSROP (CSR op form).
W_CSROP = {"csrrw": 25, "csrrs": 20, "csrrc": 20, "csrrwi": 15, "csrrsi": 10, "csrrci": 10}
# A read before any write uses the read-only forms of W-CSROP (csrrs/csrrc rs1 == x0, csrrsi/csrrci uimm == 0).
READ_FORMS = {f: W_CSROP[f] for f in ("csrrs", "csrrc", "csrrsi", "csrrci")}

CSR = {
    "mstatus": 0x300, "mie": 0x304, "mtvec": 0x305, "mcounteren": 0x306, "mcountinhibit": 0x320,
    "mscratch": 0x340, "mepc": 0x341, "mcause": 0x342, "mtval": 0x343,
    "mseccfg": 0x747, "tselect": 0x7A0, "tdata1": 0x7A1, "cpuctrlsts": 0x7C0,
}
for _i in range(4):
    CSR[f"pmpcfg{_i}"] = 0x3A0 + _i
for _i in range(16):
    CSR[f"pmpaddr{_i}"] = 0x3B0 + _i

MSTATUS_RESET = 0x80         # MIE 0, MPIE 1, MPP U (gen_test_plan.md TP-RST-006)
TDATA1_RESET = 0x28001048    # doc mismatch D4 (gen_test_plan.md TP-RST-007)
MCAUSE_ILLEGAL_INSN = 2
MSTATUS_MPP_M = 0x1800
PMP_NAPOT_RWX = 0x1F         # A = NAPOT, X W R; L = 0 so M-mode is unaffected
PMP_REGIONS = 16
N_PADS = 4
PAD_OPS = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "xor": lambda a, b: a ^ b,
           "or": lambda a, b: a | b, "and": lambda a, b: a & b}
# Registers a CSR read may land in; t6 (report address), s11 (unexpected-trap counter), s9/s10
# (filler), a0..a2 (landing pad) and t0/t1 (trap handler) are reserved.
RD_POOL = ("t2", "t3", "t4", "t5", "a3", "a4", "a5", "a6", "a7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8")
MASK32 = 0xFFFFFFFF


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
    """TP-RST-007 CSRs readable from M-mode with their reset expectation (ibex_pkg PmpCfgRst /
    PmpAddrRst / PmpMseccfgRst are all zero)."""
    out = [("mcause", Expect("const", 0)), ("mepc", Expect("const", 0)), ("mtval", Expect("const", 0)),
           ("mscratch", Expect("const", 0)), ("cpuctrlsts", Expect("cpuctrlsts_reset")),
           ("mcountinhibit", Expect("const", 0)), ("mcounteren", Expect("const", 0)), ("mseccfg", Expect("const", 0))]
    out += [(f"pmpcfg{i}", Expect("const", 0)) for i in range(4)]
    out += [(f"pmpaddr{i}", Expect("const", 0)) for i in range(PMP_REGIONS)]
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


def plan(seed, red=False):
    rng = random.Random(STREAM.format(seed=int(seed)))
    p = Plan(seed=int(seed), red=bool(red))
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
    p.pmp_entry = rng.randrange(PMP_REGIONS)
    p.pad = rng.randrange(N_PADS)
    p.pad_op = rng.choice(list(PAD_OPS))
    # sensitizing operands: never zero, never equal, high bit set in one of them
    p.pad_a = rng.randrange(1, 1 << 31) | (1 << 31)
    p.pad_b = rng.randrange(1, 1 << 31)
    p.pad_result = PAD_OPS[p.pad_op](p.pad_a, p.pad_b) & MASK32
    p.fillers = {blk: _fillers(rng) for blk in ("after_003", "after_006", "after_007", "before_mret")}
    reports.append(Report("trap_mcause", "TP-RST-006", Expect("const", MCAUSE_ILLEGAL_INSN)))
    reports.append(Report("trap_mstatus", "TP-RST-006", Expect("const", MSTATUS_RESET)))   # MIE 0, MPIE 1 (MIE was 1 after mret), MPP U
    reports.append(Report("trap_mepc", "TP-RST-006", Expect("symbol", f"gen_upad{p.pad}_trap")))
    reports.append(Report("pad_result", "TP-RST-006", Expect("const", p.pad_result)))
    reports.append(Report("unexpected_traps", "TP-RST-006", Expect("const", 0)))
    p.reports = reports
    p.k = len(reports)
    p.min_retired = _count_retired(_body(p))
    return p


def _csr_read_insn(r):
    csr = CSR[r.name]
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
        note(f"{r.name} (0x{CSR[r.name]:03x})")
        ins(_csr_read_insn(r))
        if p.red and r.name == "mstatus":
            ins(f"xori {r.rd}, {r.rd}, 0x80")          # red: MPIE toggled in the stored observation
        ins(f"sw   {r.rd}, 0(t6)")

    def emit_fillers(name):
        for f in p.fillers.get(name, []):
            ins(f)

    lab("_start:")
    ins("li   t6, GEN_MM_EOT_ADDR")
    ins("li   s11, 0")
    ins("li   s9, 0x5a5a")
    ins("li   s10, 0x0f0f")
    reads = {r.name: r for r in p.reads}
    note("TP-RST-003: mtvec before any write")
    emit_read(reads["mtvec"])
    note("trap vector table (256-byte aligned; Ibex keeps MODE vectored): installed right after the mtvec")
    note("read so an unexpected trap in the read phase is counted and skipped, never a spin at the boot page")
    ins("la   t0, gen_trap_vec")
    ins("ori  t0, t0, 1")
    ins(f"csrw 0x{CSR['mtvec']:03x}, t0")
    emit_fillers("after_003")
    note("TP-RST-006: mstatus and mie at boot (M-mode-only CSR reads that must not trap)")
    emit_read(reads["mstatus"])
    emit_read(reads["mie"])
    emit_fillers("after_006")
    note("TP-RST-007: reset CSRs in a seed-shuffled order, before any write")
    for r in p.reads:
        if r.name not in ("mtvec", "mstatus", "mie"):
            emit_read(r)
    emit_fillers("after_007")
    note(f"PMP entry {p.pmp_entry}: NAPOT whole space, RWX, unlocked (U-mode may execute the pad)")
    ins("li   t0, 0xffffffff")
    ins(f"csrw 0x{CSR[f'pmpaddr{p.pmp_entry}']:03x}, t0")
    ins(f"li   t0, 0x{PMP_NAPOT_RWX << (8 * (p.pmp_entry % 4)):08x}")
    ins(f"csrw 0x{CSR[f'pmpcfg{p.pmp_entry // 4}']:03x}, t0")
    emit_fillers("before_mret")
    note(f"mret with mepc = landing pad {p.pad}: MPP = U at reset, so the pad runs in U-mode")
    ins(f"la   t0, gen_upad{p.pad}")
    ins(f"csrw 0x{CSR['mepc']:03x}, t0")
    ins("mret")
    lab("gen_after_pad:")
    ins("sw   s11, 0(t6)")
    ins("li   gp, 1")
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
        ins(f"csrr a2, 0x{CSR['mstatus']:03x}", counted=False)   # illegal in U-mode: the handler returns to +4 in M-mode
        ins("sw   a0, 0(t6)", counted=run)
        ins("j    gen_after_pad", counted=run)
    # trap handler: the U-mode illegal instruction is the expected trap; anything else is counted and skipped
    lab(".align 8")
    lab("gen_trap_vec:")
    ins("j    gen_exc", )
    for _ in range(31):
        ins("j    gen_unexpected_irq", counted=False)
    lab("gen_exc:")
    ins(f"csrr t0, 0x{CSR['mstatus']:03x}")
    ins("srli t1, t0, 11")
    ins("andi t1, t1, 3")
    ins("bnez t1, gen_exc_m")
    ins(f"csrr t0, 0x{CSR['mcause']:03x}")
    ins("sw   t0, 0(t6)")
    ins(f"csrr t0, 0x{CSR['mstatus']:03x}")
    ins("sw   t0, 0(t6)")
    ins(f"csrr t0, 0x{CSR['mepc']:03x}")
    ins("sw   t0, 0(t6)")
    ins("addi t0, t0, 4")
    ins(f"csrw 0x{CSR['mepc']:03x}, t0")
    ins(f"li   t1, 0x{MSTATUS_MPP_M:04x}")
    ins(f"csrs 0x{CSR['mstatus']:03x}, t1")
    ins("mret")
    lab("gen_exc_m:")
    ins("addi s11, s11, 1", counted=False)
    ins(f"csrr t0, 0x{CSR['mepc']:03x}", counted=False)
    ins("addi t0, t0, 4", counted=False)
    ins(f"csrw 0x{CSR['mepc']:03x}, t0", counted=False)
    ins("mret", counted=False)
    lab("gen_unexpected_irq:")
    ins("addi s11, s11, 1", counted=False)
    ins("mret", counted=False)
    return L


def _count_retired(body):
    return sum(1 for counted, _ in body if counted)


HEADER = """# gen_rst_boot_prog.py output: reset and boot state observations for gen_test_rst_boot
# (seed {seed}{red}). Every observation is stored RAW to GEN_MM_EOT_ADDR in plan order ({k} report
# words), then tohost 1. Generated; do not edit.
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
    text = HEADER.format(seed=p.seed, red=", red fixture" if p.red else "", k=p.k)
    text += "\n".join(t for _, t in _body(p)) + "\n"
    text += FOOTER.format(min_retired=p.min_retired)
    assert all(ord(c) < 128 for c in text), "gen_rst_boot_prog: non-ASCII output"
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--red", action="store_true")
    args = ap.parse_args()
    p = plan(args.seed, args.red)
    with open(args.out, "w") as f:
        f.write(emit(p))
    print(f"gen_rst_boot_prog seed={p.seed} red={p.red} k={p.k} min_retired={p.min_retired} pad={p.pad} "
          f"pmp_entry={p.pmp_entry} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
