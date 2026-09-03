#!/usr/bin/env python3
"""gen_csr_reset_prog: per-seed program generator of gen_test_csr_reset (group gen_csr_reset, plan items
TP-CSR-037, TP-CSR-105, TP-CSR-106, TP-CSR-107, TP-CSR-108, TP-CSR-109 of dv/auto_dv/docs/gen_test_plan.md).

The program reads every reset-value CSR the items name, in a random order drawn from
random.Random(f"{seed}:program:csr_reset"), into random registers (W-REG), with W-FILL filler
instructions between the reads, and stores each RAW read-back value to the EOT MMIO register
(GEN_MM_EOT_ADDR) in read order, then tohost 1. The test resolves the expectation of every report
word through bounds(): constants come from the RISC-V privileged specification and the Ibex
documentation (the RTL is followed only for the documented doc mismatches D4 and D20 of
gen_bug_log.md Section 3); pin-dependent values (mtvec, mhartid, cpuctrlsts bit 8) and the counters
are resolved against the run's plusargs and bridge counts. `red=True` deviates on exactly one intent:
the program writes mscratch (mepc when mscratch happens to be the very first read) before its reset
value is read (TP-CSR-106 precondition), replacing one filler so no instruction index moves, while
plan() keeps the reset expectation, so the test's fire-check fails.

CLI: python3 gen_csr_reset_prog.py --seed N --out <file.S> [--red] [--summary]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))
from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP  # noqa: E402  (one origin of the EOT address / boot page mask)

STREAM = "csr_reset"
CONFIG_NAME = "opentitan"
IBEX_CONFIGS = REPO_ROOT / "ibex_configs.yaml"

# ---- Layer-1 weight tables (gen_test_plan.md Section 4.2 "Layer-1 weight tables") ----------------
# W-REG rd classes {x0, x1..x15, x16..x31} 10/45/45: x0 is dropped (a demoted read reports nothing).
W_REG_RD = {"lo": 45, "hi": 45}
# W-FILL filler between the instructions of a sequence {none, 1 ALU, 2..4 ALU/branch, load/store}.
W_FILL = {"none": 40, "alu1": 25, "alu2_4": 25, "ldst": 10}
# Which read comes first: TP-CSR-037 wants mtvec as the very first instruction, TP-CSR-105 rotates its
# 13 CSRs there across seeds (CG-CSR-016 cr_mtvec_first vs mtvec_early, cr_first_csr bins).
W_FIRST = {"mtvec": 30, "tp105": 40, "any": 30}

# ---- Register plan (x0 never a read target) -----------------------------------------------------
REG_EOT = 31       # holds GEN_MM_EOT_ADDR
REG_SCRATCH = 30   # holds the address of gen_scratch (filler loads/stores); reused as t5 by the epilogue
REG_ALU_A = 29     # filler operands
REG_ALU_B = 28
REG_MTVEC2 = 27    # the second mtvec read of TP-CSR-037
POOL_LO = [1, 2] + list(range(4, 16))     # x3 (gp) carries the final tohost code
POOL_HI = list(range(16, 27))

# ---- CSR addresses (RISC-V privileged spec; Ibex custom CSRs from doc/03_reference/cs_registers.rst)
CSR = {"mstatus": 0x300, "misa": 0x301, "mie": 0x304, "mtvec": 0x305, "mcounteren": 0x306, "mstatush": 0x310,
       "menvcfg": 0x30A, "menvcfgh": 0x31A, "mvendorid": 0xF11, "marchid": 0xF12, "mimpid": 0xF13,
       "mhartid": 0xF14, "mconfigptr": 0xF15, "mscratch": 0x340, "mepc": 0x341, "mcause": 0x342, "mtval": 0x343,
       "mip": 0x344, "mcountinhibit": 0x320, "mcycle": 0xB00, "minstret": 0xB02, "mcycleh": 0xB80,
       "minstreth": 0xB82, "cycle": 0xC00, "instret": 0xC02, "tselect": 0x7A0, "tdata1": 0x7A1, "tdata2": 0x7A2,
       "cpuctrlsts": 0x7C0, "secureseed": 0x7C1, "mseccfg": 0x747, "mseccfgh": 0x757}
MHPMCOUNTER_BASE = 0xB00
MHPMCOUNTERH_BASE = 0xB80
HPMCOUNTER_BASE = 0xC00
MHPMEVENT_BASE = 0x320
PMPCFG_BASE = 0x3A0
PMPADDR_BASE = 0x3B0

# ---- Documented constants ------------------------------------------------------------------------
MSTATUS_RESET = 0x0000_0080        # cs_registers.rst:116 (MPIE=1, MPP=U)
MISA_VALUE = 0x4090_1104           # MXL=1, X (RV32BOTEarlGrey), U, M, I, C; rtl/ibex_cs_registers.sv MISA_VALUE
MARCHID_VALUE = 0x16               # cs_registers.rst:617, ibex_pkg CSR_MARCHID_VALUE
MVENDORID_VALUE = 0                # cs_registers.rst:607 (wrapper CsrMvendorId default)
MIMPID_VALUE = 0                   # cs_registers.rst:629 (wrapper CsrMimpId default)
TDATA1_RESET = 0x2800_1048         # D4: RTL value (type 2, dmode, action 1, m, u); doc says 0x2800_1000
CPUCTRL_KEY_BIT = 8                # cs_registers.rst:544 ic_scr_key_valid
BOOT_PAGE_MASK = MEMORY_MAP["boot_page_mask"]
EOT_ADDR = MEMORY_MAP["eot_addr"]
MCYCLE_SLACK = 4                   # reset-release alignment between the bridge cycle counter and mcycle
INSTRET_SKEW = 0                   # a csrr waits for the WB stage, so minstret reads exactly the retirements before it
LDST_SKEW = 2                      # loads/stores still in flight when the csrr reads their counter
RETIRE_SLACK = 2                   # gen_min_retired: the EOT store is seen on the bus before its own retirement


def build_params():
    """MHPMCounterNum and PMPNumRegions of the build configuration (ibex_configs.yaml, one origin)."""
    import yaml
    cfg = yaml.safe_load(IBEX_CONFIGS.read_text())[CONFIG_NAME]
    return {"MHPMCounterNum": int(cfg["MHPMCounterNum"]), "PMPNumRegions": int(cfg["PMPNumRegions"])}


@dataclass
class Report:
    """One report word: the csrr of `name` (address `addr`) for `item`, its expectation rule and the
    program facts the rule needs (idx = retirements before the csrr, stub included)."""
    name: str
    addr: int
    item: str
    rule: str                 # const | mtvec_boot | hart_id | mip_pins | cpuctrl_key | cycles | instret | hpm_small | count_window
    param: int = 0            # const value, or the count for count_window
    idx: int = 0
    remaining: int = 0        # instructions between the csrr and the final tohost store
    reg: int = 0
    pos: int = 0              # index in the report order


@dataclass
class Plan:
    seed: int
    red: bool
    reports: list = field(default_factory=list)
    lines: list = field(default_factory=list)   # rendered body instructions (one instruction each, except the epilogue la)
    k: int = 0
    min_retired: int = 0
    first_csr: str = ""
    mtvec_first: bool = False
    red_csr: str = ""      # the CSR the red program writes before its read (empty when green)

    def by_item(self, item):
        return [r for r in self.reports if r.item == item]

    def find(self, name):
        return next(r for r in self.reports if r.name == name)


def _reads(rng, params):
    """The read list of the six items (before ordering); names are unique."""
    n_hpm = params["MHPMCounterNum"]
    hpm = list(range(3, 3 + n_hpm))
    unimpl = list(range(3 + n_hpm, 32))
    r = []
    # TP-CSR-105: trap-setup and machine-information CSRs (mtvec is also TP-CSR-037's first read)
    for nm, v in (("mstatus", MSTATUS_RESET), ("misa", MISA_VALUE), ("mie", 0), ("mcounteren", 0), ("mstatush", 0),
                  ("menvcfg", 0), ("menvcfgh", 0), ("mvendorid", MVENDORID_VALUE), ("marchid", MARCHID_VALUE),
                  ("mimpid", MIMPID_VALUE), ("mconfigptr", 0)):
        r.append(Report(nm, CSR[nm], "TP-CSR-105", "const", v))
    r.append(Report("mtvec", CSR["mtvec"], "TP-CSR-105", "mtvec_boot"))
    r.append(Report("mhartid", CSR["mhartid"], "TP-CSR-105", "hart_id"))
    # TP-CSR-106: trap-handling CSRs; mip reads the raw pins (D1), none driven by this test
    for nm in ("mscratch", "mepc", "mcause", "mtval"):
        r.append(Report(nm, CSR[nm], "TP-CSR-106", "const", 0))
    r.append(Report("mip", CSR["mip"], "TP-CSR-106", "mip_pins"))
    # TP-CSR-107: counters (D20 for mhpmevent)
    r.append(Report("mcycle", CSR["mcycle"], "TP-CSR-107", "cycles"))
    r.append(Report("cycle", CSR["cycle"], "TP-CSR-107", "cycles"))
    r.append(Report("minstret", CSR["minstret"], "TP-CSR-107", "instret"))
    r.append(Report("instret", CSR["instret"], "TP-CSR-107", "instret"))
    r.append(Report("mcycleh", CSR["mcycleh"], "TP-CSR-107", "const", 0))
    r.append(Report("minstreth", CSR["minstreth"], "TP-CSR-107", "const", 0))
    r.append(Report("mcountinhibit", CSR["mcountinhibit"], "TP-CSR-107", "const", 0))
    # counter events (rtl/ibex_cs_registers.sv gen_mhpmcounter_incr; doc performance_counters.rst):
    # 5 loads / 6 stores follow the program's own load/store count, 7 jumps = the boot stub's j _start,
    # 9 taken branches / 10 compressed / 11 mul wait / 12 div wait = 0 (this program takes no branch,
    # is assembled norvc and has no mul/div); 3, 4, 8 are bounded by the cycle count (B17 for 8).
    exact = {7: 1, 9: 0, 10: 0, 11: 0, 12: 0}
    for n in hpm:
        nm = f"mhpmcounter{n}"
        if n in exact:
            r.append(Report(nm, MHPMCOUNTER_BASE + n, "TP-CSR-107", "const", exact[n]))
        elif n in (5, 6):
            r.append(Report(nm, MHPMCOUNTER_BASE + n, "TP-CSR-107", "count_window"))
        else:
            r.append(Report(nm, MHPMCOUNTER_BASE + n, "TP-CSR-107", "hpm_small"))
        r.append(Report(f"mhpmcounter{n}h", MHPMCOUNTERH_BASE + n, "TP-CSR-107", "const", 0))
        r.append(Report(f"mhpmevent{n}", MHPMEVENT_BASE + n, "TP-CSR-107", "const", 1 << (n - 3)))
    for n in sorted(rng.sample(unimpl, 2)):
        r.append(Report(f"mhpmcounter{n}", MHPMCOUNTER_BASE + n, "TP-CSR-107", "const", 0))
    for n in sorted(rng.sample(unimpl, 2)):
        r.append(Report(f"mhpmevent{n}", MHPMEVENT_BASE + n, "TP-CSR-107", "const", 0))
    n = rng.choice(hpm)
    r.append(Report(f"hpmcounter{n}", HPMCOUNTER_BASE + n, "TP-CSR-107", "hpm_small"))
    # TP-CSR-108: trigger CSRs in M-mode (D12 readable; D4 value)
    r.append(Report("tselect", CSR["tselect"], "TP-CSR-108", "const", 0))
    r.append(Report("tdata1", CSR["tdata1"], "TP-CSR-108", "const", TDATA1_RESET))
    r.append(Report("tdata2", CSR["tdata2"], "TP-CSR-108", "const", 0))
    # TP-CSR-109: custom and PMP CSRs
    r.append(Report("cpuctrlsts", CSR["cpuctrlsts"], "TP-CSR-109", "cpuctrl_key"))
    r.append(Report("secureseed", CSR["secureseed"], "TP-CSR-109", "const", 0))
    r.append(Report("mseccfg", CSR["mseccfg"], "TP-CSR-109", "const", 0))
    r.append(Report("mseccfgh", CSR["mseccfgh"], "TP-CSR-109", "const", 0))
    for i in range(params["PMPNumRegions"] // 4):
        r.append(Report(f"pmpcfg{i}", PMPCFG_BASE + i, "TP-CSR-109", "const", 0))
    for i in range(params["PMPNumRegions"]):
        r.append(Report(f"pmpaddr{i}", PMPADDR_BASE + i, "TP-CSR-109", "const", 0))
    return r


def _weighted(rng, table):
    names = list(table)
    return rng.choices(names, weights=[table[n] for n in names], k=1)[0]


def _alu(rng):
    a, b = REG_ALU_A, REG_ALU_B
    forms = [lambda: f"addi x{a}, x{a}, {rng.randint(-2048, 2047)}",
             lambda: f"xori x{b}, x{a}, {rng.randint(-2048, 2047)}",
             lambda: f"lui x{b}, 0x{rng.randint(1, 0xFFFFF):05x}",
             lambda: f"add x{a}, x{a}, x{b}",
             lambda: f"sub x{b}, x{a}, x{b}",
             lambda: f"xor x{a}, x{a}, x{b}",
             lambda: f"slli x{a}, x{a}, {rng.randint(1, 31)}",
             lambda: f"srli x{b}, x{b}, {rng.randint(1, 31)}",
             lambda: f"andi x{a}, x{a}, {rng.randint(-2048, 2047)}",
             lambda: f"or x{b}, x{b}, x{a}",
             lambda: f"sltu x{b}, x{a}, x{b}"]
    return rng.choice(forms)()


def _filler(rng):
    """W-FILL: filler instructions before a read (never taken branches, no mul/div, norvc)."""
    kind = _weighted(rng, W_FILL)
    if kind == "none":
        return []
    if kind == "alu1":
        return [_alu(rng)]
    if kind == "alu2_4":
        n = rng.randint(2, 4)
        out = [_alu(rng) for _ in range(n)]
        if rng.random() < 0.3:
            out[rng.randrange(n)] = f"bne x0, x0, .+8"   # conditional branch class, never taken
        return out
    if rng.random() < 0.5:
        return [f"sw x{REG_ALU_A}, 0(x{REG_SCRATCH})"]
    return [f"lw x{REG_ALU_B}, 0(x{REG_SCRATCH})"]


def _hi_lo(value):
    """lui/addi pair fields of a 32-bit constant."""
    lo = value & 0xFFF
    if lo >= 0x800:
        lo -= 0x1000
    hi = ((value - lo) >> 12) & 0xFFFFF
    return hi, lo


def plan(seed, red=False):
    rng = random.Random(f"{int(seed)}:program:{STREAM}")
    params = build_params()
    reads = _reads(rng, params)
    p = Plan(seed=int(seed), red=bool(red))
    # order: the first read per W-FIRST, the rest shuffled
    cls = _weighted(rng, W_FIRST)
    if cls == "mtvec":
        first = next(r for r in reads if r.name == "mtvec")
    elif cls == "tp105":
        first = rng.choice([r for r in reads if r.item == "TP-CSR-105"])
    else:
        first = rng.choice(reads)
    rest = [r for r in reads if r is not first]
    rng.shuffle(rest)
    order = [first] + rest
    p.first_csr = first.name
    p.mtvec_first = first.name == "mtvec"

    lines = []
    reports = []   # Report objects in store order
    free = {"lo": list(POOL_LO), "hi": list(POOL_HI)}
    pending = []
    batch = rng.randint(4, 20)

    def flush():
        for reg, rd in pending:
            lines.append((f"sw x{reg}, 0(x{REG_EOT})", rd))
            free["lo" if reg < 16 else "hi"].append(reg)
        pending.clear()

    def alloc():
        cls = _weighted(rng, W_REG_RD)
        other = "hi" if cls == "lo" else "lo"
        pool = free[cls] if free[cls] else free[other]
        reg = rng.choice(pool)
        pool.remove(reg)
        return reg

    # RED: exactly one intent violated, a TP-CSR-106 CSR written (from the non-zero x29) before its reset
    # value is read; the write replaces the third setup instruction so every instruction index is unchanged.
    red_csr = None
    if red:
        red_csr = "mscratch" if order[0].name != "mscratch" else "mepc"
    for i, rd in enumerate(order):
        if i == 1:
            hi, lo = _hi_lo(EOT_ADDR)
            lines.append((f"lui x{REG_EOT}, 0x{hi:05x}", None))
            lines.append((f"addi x{REG_EOT}, x{REG_EOT}, {lo}", None))
            lines.append((f"lui x{REG_SCRATCH}, %hi(gen_scratch)", None))
            lines.append((f"addi x{REG_SCRATCH}, x{REG_SCRATCH}, %lo(gen_scratch)", None))
            lines.append((f"lui x{REG_ALU_A}, 0x{rng.randint(1, 0xFFFFF):05x}", None))
            lines.append((f"addi x{REG_ALU_B}, x0, {rng.randint(-2048, 2047)}", None))
            third = f"xori x{REG_ALU_A}, x{REG_ALU_A}, {rng.randint(-2048, 2047)}"
            lines.append((f"csrw 0x{CSR[red_csr]:03x}, x{REG_ALU_A}" if red else third, None))
        if i > 0:
            for f in _filler(rng):
                lines.append((f, None))
        if not (free["lo"] or free["hi"]) or len(pending) >= batch:
            flush()
            batch = rng.randint(4, 20)
        reg = alloc()
        rd.reg = reg
        lines.append((f"csrr x{reg}, 0x{rd.addr:03x}", ("read", rd)))
        pending.append((reg, rd))
    flush()

    # TP-CSR-037: mtvec again exactly 10 instructions after its first read, stored with the next batch
    mtvec2 = Report("mtvec_again", CSR["mtvec"], "TP-CSR-037", "mtvec_boot", reg=REG_MTVEC2)
    p1 = next(i for i, (_, tag) in enumerate(lines) if isinstance(tag, tuple) and tag[1].name == "mtvec")
    at = p1 + 11
    while len(lines) < at:
        lines.append((_alu(rng), None))   # mtvec read late in the stream: pad so 10 instructions separate the reads
    lines.insert(at, (f"csrr x{REG_MTVEC2}, 0x{CSR['mtvec']:03x}", ("read", mtvec2)))
    q = at + 1
    while q < len(lines) and not (lines[q][1] and isinstance(lines[q][1], Report)):
        q += 1
    while q < len(lines) and lines[q][1] and isinstance(lines[q][1], Report):
        q += 1
    lines.insert(q, (f"sw x{REG_MTVEC2}, 0(x{REG_EOT})", mtvec2))

    # epilogue (end-of-test convention of gen_zc_directed.S); `la` is two instructions
    lines.append(("li gp, 1", None))
    lines.append(("la t5, tohost", None))
    final_idx = 1 + sum(2 if t.startswith("la ") else 1 for t, _ in lines)   # retirements before the tohost store
    lines.append(("sw gp, 0(t5)", None))

    # per-report facts: idx (retirements before the csrr, stub = retirement 0), loads/stores before it
    idx = 1
    loads = stores = 0
    for text, tag in lines:
        if isinstance(tag, tuple) and tag[0] == "read":
            rd = tag[1]
            rd.idx = idx
            rd.remaining = final_idx - idx
            if rd.rule == "count_window":
                rd.param = loads if rd.name == "mhpmcounter5" else stores
        if text.startswith("lw "):
            loads += 1
        elif text.startswith("sw "):
            stores += 1
        idx += 2 if text.startswith("la ") else 1
    for text, tag in lines:
        if isinstance(tag, Report):
            tag.pos = len(reports)
            reports.append(tag)
    p.reports = reports
    p.k = len(reports)
    p.lines = [text for text, _ in lines]
    p.min_retired = final_idx - RETIRE_SLACK
    p.red_csr = red_csr or ""
    return p


def bounds(rep, env):
    """Inclusive (lo, hi) of a report word. env: boot_addr, hart_id, key_valid (1, 0 or None when the
    responder timing leaves it open), eot_cycle (bridge cycle count at the end-of-test store)."""
    r = rep.rule
    if r == "const":
        return rep.param, rep.param
    if r == "mtvec_boot":
        v = (env["boot_addr"] & BOOT_PAGE_MASK) | 1      # {boot_addr[31:8], 8'h01}: vectored, BASE = boot page
        return v, v
    if r == "hart_id":
        return env["hart_id"], env["hart_id"]
    if r == "mip_pins":
        return 0, 0                                      # no interrupt line is driven in this test
    if r == "cpuctrl_key":
        if env["key_valid"] is None:
            return 0, 1 << CPUCTRL_KEY_BIT               # caller masks bit 8 (see gen_test_csr_reset)
        return env["key_valid"] << CPUCTRL_KEY_BIT, env["key_valid"] << CPUCTRL_KEY_BIT
    if r == "cycles":
        # every retirement takes at least one cycle: idx <= mcycle <= cycles left before the EOT store
        return rep.idx, env["eot_cycle"] - rep.remaining + MCYCLE_SLACK
    if r == "instret":
        return rep.idx - INSTRET_SKEW, rep.idx
    if r == "hpm_small":
        return 0, env["eot_cycle"]
    if r == "count_window":
        return max(rep.param - LDST_SKEW, 0), rep.param
    raise AssertionError(f"gen_csr_reset_prog: unknown rule {r}")


def emit(p):
    out = ["# gen_csr_reset_prog.py: generated for seed %d%s (do not edit; regenerate)" % (p.seed, " RED: %s written before its read" % p.red_csr if p.red else ""),
           "# group gen_csr_reset; %d report words; first read %s; min_retired %d" % (p.k, p.first_csr, p.min_retired),
           '.include "gen_mmio_map.h"', ".option norvc", ".section .text", ".globl _start", "_start:"]
    out += ["  " + t for t in p.lines]
    out += ["1:", "  j 1b", "", ".section .data", ".align 6", ".globl tohost", "tohost: .dword 0", ".globl fromhost",
            "fromhost: .dword 0", ".align 2", ".globl gen_min_retired", f"gen_min_retired: .word {p.min_retired}",
            ".align 2", "gen_scratch: .word 0", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--red", action="store_true")
    ap.add_argument("--summary", action="store_true", help="print the report table")
    a = ap.parse_args()
    p = plan(a.seed, a.red)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    text = emit(p)
    assert all(ord(c) < 128 for c in text), "non-ASCII in generated program"
    a.out.write_text(text)
    print(f"gen_csr_reset_prog: seed={p.seed} red={p.red} k={p.k} min_retired={p.min_retired} first={p.first_csr} "
          f"mtvec_first={p.mtvec_first} lines={len(p.lines)} out={a.out}")
    if a.summary:
        for r in p.reports:
            print(f"  {r.pos:3d} {r.item} {r.name:16s} 0x{r.addr:03x} x{r.reg:<2d} idx={r.idx:3d} rule={r.rule} param={r.param}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
