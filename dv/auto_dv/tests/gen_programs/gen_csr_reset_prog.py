#!/usr/bin/env python3
"""gen_csr_reset_prog: per-seed program generator of gen_test_csr_reset (group gen_csr_reset, plan items
TP-CSR-037, TP-CSR-105, TP-CSR-106, TP-CSR-107, TP-CSR-108, TP-CSR-109 of dv/auto_dv/docs/gen_test_plan.md).

Layout per seed (random.Random(f"{seed}:program:csr_reset")): one lead drawn from W_EARLY opens the program
with the reads of its item(s) back to back, no filler inside a block (tp105: the 13 TP-CSR-105 reads; tp106:
the 5 TP-CSR-106 reads, then the EOT-address setup and their stores, then the 24 TP-CSR-109 reads; tp109: the
24 TP-CSR-109 reads), so the plan's "within the first N retirements" bound of the led items (RETIRE_BOUND,
Plan.bounded) holds by construction and the test asserts it from the report index. The three bounds exclude
each other in one program (13 + 5 reads exceed 16), hence one lead per seed. The very first instruction is
mtvec (TP-CSR-037), a read of the leading block or any read (W_FIRST; a tp105 lead keeps it in TP-CSR-105 so
the first retirement is one of its reads). The remaining reads follow shuffled, with W-FILL fillers and
batched report stores; mtvec is read again exactly 10 instructions after its first read. Every read lands in
rd != x0 and its RAW value is stored to GEN_MM_EOT_ADDR in read order (Plan.k words), then tohost
TOHOST_PASS. Retirement position of a read = Report.idx = retirements before its csrr, the boot stub's
j _start being retirement 0; Plan.final_idx = retirements before the tohost store (gen_min_retired = final_idx - 1).

Expectations (bounds()): constants from the RISC-V privileged specification and the Ibex documentation through
gen_prog_const and the rendered CONSTANTS (marchid; tdata1 follows the RTL, doc mismatch D4; mhpmevent follows
the RTL, D20); mtvec and mhartid from the run's plusargs; cpuctrlsts bit 8 and mip from the run's regimes
(env, resolved by the test); the counters from the program index and the bridge cycle count.

Red fixtures (--red [--red-item <id>], the item drawn from random.Random(f"{seed}:red") when not given): the
program re-targets one read of the item to a CSR whose reset value differs (RED_TARGETS), one instruction for
one, so no index or report position moves and only that item's fire-check fails; plan() keeps every expectation.

CLI: python3 gen_csr_reset_prog.py --seed N --out <file.S> [--red [--red-item TP-CSR-037|105|106|107|108|109]] [--summary]
"""
import argparse
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, MEMORY_MAP  # noqa: E402  (rendered once by the TB)
from dv.auto_dv.tests.gen_programs.gen_prog_const import (  # noqa: E402
    CONFIG_NAME, CSR, MCONFIGPTR_VALUE, MISA_VALUE, MSTATUS_RESET, TOHOST_PASS, hpmcounter, mhpmcounter, mhpmevent,
    pmpaddr, pmpcfg)

STREAM = "csr_reset"
RED_STREAM = "red"
IBEX_CONFIGS = REPO_ROOT / "ibex_configs.yaml"
MASK32 = 0xFFFFFFFF

# ---- Layer-1 weight tables (gen_test_plan.md Section 4.2 "Layer-1 weight tables") ----------------
# W-REG rd classes {x0, x1..x15, x16..x31} 10/45/45: x0 is dropped (a demoted read reports nothing).
W_REG_RD = {"lo": 45, "hi": 45}
# W-FILL filler between the instructions of a sequence {none, 1 ALU, 2..4 ALU/branch, load/store}.
W_FILL = {"none": 40, "alu1": 25, "alu2_4": 25, "ldst": 10}
# The lead: which item's reads open the program (its retirement bound is asserted on that seed).
W_EARLY = {"tp105": 40, "tp106": 30, "tp109": 30}
EARLY_BLOCKS = {"tp105": ("TP-CSR-105",), "tp106": ("TP-CSR-106", "TP-CSR-109"), "tp109": ("TP-CSR-109",)}
RETIRE_BOUND = {"TP-CSR-105": 16, "TP-CSR-106": 16, "TP-CSR-109": 40}   # plan: "within the first N retirements"
# The very first instruction: mtvec (TP-CSR-037), a read of the leading block, or any read (CG-CSR-016 cr_first_csr).
W_FIRST = {"mtvec": 30, "block": 55, "any": 15}
MTVEC_AGAIN_GAP = 10       # TP-CSR-037: instructions between the two mtvec reads

# ---- Register plan (x0 never a read target) -----------------------------------------------------
REG_EOT = 31       # holds GEN_MM_EOT_ADDR
REG_SCRATCH = 30   # holds the address of gen_scratch (filler loads/stores); reused as t5 by the epilogue
REG_ALU_A = 29     # filler operands
REG_ALU_B = 28
REG_MTVEC2 = 27    # the second mtvec read of TP-CSR-037
POOL_LO = [1, 2] + list(range(4, 16))     # x3 (gp) carries the final tohost code
POOL_HI = list(range(16, 27))

# ---- Documented constants not in gen_prog_const --------------------------------------------------
MARCHID_VALUE = CONSTANTS["GEN_CSR_MARCHID_VALUE"]    # cs_registers.rst marchid 0x16
MVENDORID_VALUE = 0                                   # cs_registers.rst (wrapper CsrMvendorId default)
MIMPID_VALUE = 0                                      # cs_registers.rst (wrapper CsrMimpId default)
TDATA1_RESET = CONSTANTS["GEN_TDATA1_IBEX_RDATA"]     # D4: the RTL value 0x2800_1048; the doc says 0x2800_1000
CPUCTRL_KEY_BIT = 8                                   # cs_registers.rst ic_scr_key_valid
KEY_BIT = 1 << CPUCTRL_KEY_BIT
# mip bits an interrupt line can drive: MSIP 3, MTIP 7, MEIP 11 (privileged spec) and the fast lines.
MIP_LINE_MASK = (1 << 3) | (1 << 7) | (1 << 11) | CONSTANTS["GEN_IRQ_FAST_MASK"]
BOOT_PAGE_MASK = MEMORY_MAP["boot_page_mask"]
EOT_ADDR = MEMORY_MAP["eot_addr"]
# The bridge cycle count and mcycle both reset with rst_n and count every cycle, so mcycle at the csrr equals the
# bridge count of that cycle, and the end-of-test store is seen `remaining` or more cycles later (one cycle per
# retirement at least). Slack: the csrr may read the counter already incremented (+1) and mcycle may take its
# first increment one cycle before the bridge (+1).
MCYCLE_SLACK = 2
# A load/store counts on its response: with one outstanding data access plus the WB stage, up to two may be
# uncounted when the csrr reads mhpmcounter5/6.
LDST_SKEW = 2

RED_TARGETS = {  # item: (the read re-targeted, the CSR read instead; its reset value differs from the expectation)
    "TP-CSR-037": ("mtvec_again", "mscratch"),
    "TP-CSR-105": ("misa", "mie"),
    "TP-CSR-106": ("mcause", "misa"),
    "TP-CSR-107": ("mcountinhibit", "misa"),
    "TP-CSR-108": ("tdata2", "misa"),
    "TP-CSR-109": ("secureseed", "misa"),
}
RED_ITEMS = tuple(RED_TARGETS)


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
    final_idx: int = 0     # retirements before the tohost store (stub included)
    first_csr: str = ""
    first_item: str = ""
    mtvec_first: bool = False
    early: str = ""        # the W_EARLY draw
    bounded: tuple = ()    # items whose RETIRE_BOUND the layout meets (asserted by the test)
    red_item: str = ""     # the item the red program deviates on (empty when green)
    red_note: str = ""

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
                  ("mimpid", MIMPID_VALUE), ("mconfigptr", MCONFIGPTR_VALUE)):
        r.append(Report(nm, CSR[nm], "TP-CSR-105", "const", v))
    r.append(Report("mtvec", CSR["mtvec"], "TP-CSR-105", "mtvec_boot"))
    r.append(Report("mhartid", CSR["mhartid"], "TP-CSR-105", "hart_id"))
    # TP-CSR-106: trap-handling CSRs; mip reads the raw pins (D1)
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
    # counter events (doc performance_counters.rst): 5 loads / 6 stores follow the program's own load/store
    # count, 7 jumps = the boot stub's j _start, 9 taken branches / 10 compressed / 11 mul wait / 12 div wait = 0
    # (this program takes no branch, is assembled norvc and has no mul/div); 3, 4, 8 are bounded by the cycle count.
    exact = {7: 1, 9: 0, 10: 0, 11: 0, 12: 0}
    for n in hpm:
        nm = f"mhpmcounter{n}"
        if n in exact:
            r.append(Report(nm, mhpmcounter(n), "TP-CSR-107", "const", exact[n]))
        elif n in (5, 6):
            r.append(Report(nm, mhpmcounter(n), "TP-CSR-107", "count_window"))
        else:
            r.append(Report(nm, mhpmcounter(n), "TP-CSR-107", "hpm_small"))
        r.append(Report(f"mhpmcounter{n}h", mhpmcounter(n, high=True), "TP-CSR-107", "const", 0))
        r.append(Report(f"mhpmevent{n}", mhpmevent(n), "TP-CSR-107", "const", 1 << (n - 3)))
    for n in sorted(rng.sample(unimpl, 2)):
        r.append(Report(f"mhpmcounter{n}", mhpmcounter(n), "TP-CSR-107", "const", 0))
    for n in sorted(rng.sample(unimpl, 2)):
        r.append(Report(f"mhpmevent{n}", mhpmevent(n), "TP-CSR-107", "const", 0))
    n = rng.choice(hpm)
    r.append(Report(f"hpmcounter{n}", hpmcounter(n), "TP-CSR-107", "hpm_small"))
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
        r.append(Report(f"pmpcfg{i}", pmpcfg(i), "TP-CSR-109", "const", 0))
    for i in range(params["PMPNumRegions"]):
        r.append(Report(f"pmpaddr{i}", pmpaddr(i), "TP-CSR-109", "const", 0))
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


def _csrr(reg, addr):
    return f"csrr x{reg}, 0x{addr:03x}"


def plan(seed, red=False, red_item=None):
    """The per-seed plan; red_item selects the deviating item (drawn from the red stream when red and None)."""
    if red_item is not None and red_item not in RED_TARGETS:
        raise ValueError(f"gen_csr_reset_prog: red item {red_item} not in {RED_ITEMS}")
    red = bool(red) or red_item is not None
    rng = random.Random(f"{int(seed)}:program:{STREAM}")
    params = build_params()
    reads = _reads(rng, params)
    by_name = {r.name: r for r in reads}
    p = Plan(seed=int(seed), red=red)

    # order: the lead's block(s) open the program, the first instruction per W_FIRST, the rest shuffled
    p.early = _weighted(rng, W_EARLY)
    blocks = EARLY_BLOCKS[p.early]
    p.bounded = blocks
    lead = [r for r in reads if r.item == blocks[0]]
    cls = _weighted(rng, W_FIRST)
    if cls == "mtvec":
        first = by_name["mtvec"]
    elif cls == "block" or blocks[0] == "TP-CSR-105":
        first = rng.choice(lead)
    else:
        first = rng.choice(reads)
    used = {first.name}
    block_reads = []
    for item in blocks:
        blk = [r for r in reads if r.item == item and r.name not in used]
        rng.shuffle(blk)
        used |= {r.name for r in blk}
        block_reads.append(blk)
    rest = [r for r in reads if r.name not in used]
    rng.shuffle(rest)
    p.first_csr, p.first_item, p.mtvec_first = first.name, first.item, first.name == "mtvec"

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

    def read(rd):
        rd.reg = alloc()
        lines.append((_csrr(rd.reg, rd.addr), ("read", rd)))
        pending.append((rd.reg, rd))

    # leading block(s): reads back to back (25 free registers cover the largest block); the EOT address and the
    # first block's stores between two blocks
    read(first)
    for i, blk in enumerate(block_reads):
        for rd in blk:
            read(rd)
        if i == 0:
            hi, lo = _hi_lo(EOT_ADDR)
            lines.append((f"lui x{REG_EOT}, 0x{hi:05x}", None))
            lines.append((f"addi x{REG_EOT}, x{REG_EOT}, {lo}", None))
            flush()
    lead_end = len(lines)
    # the rest of the setup (filler operands), then the remaining reads with W-FILL and batched stores
    lines.append((f"lui x{REG_SCRATCH}, %hi(gen_scratch)", None))
    lines.append((f"addi x{REG_SCRATCH}, x{REG_SCRATCH}, %lo(gen_scratch)", None))
    lines.append((f"lui x{REG_ALU_A}, 0x{rng.randint(1, 0xFFFFF):05x}", None))
    lines.append((f"addi x{REG_ALU_B}, x0, {rng.randint(-2048, 2047)}", None))
    lines.append((f"xori x{REG_ALU_A}, x{REG_ALU_A}, {rng.randint(-2048, 2047)}", None))
    for rd in rest:
        for f in _filler(rng):
            lines.append((f, None))
        if not (free["lo"] or free["hi"]) or len(pending) >= batch:
            flush()
            batch = rng.randint(4, 20)
        read(rd)
    flush()

    # TP-CSR-037: mtvec again exactly MTVEC_AGAIN_GAP instructions after its first read; its store joins the first
    # store group after the leading blocks (a store inside them would push a led read past its bound)
    mtvec2 = Report("mtvec_again", CSR["mtvec"], "TP-CSR-037", "mtvec_boot", reg=REG_MTVEC2)
    p1 = next(i for i, (_, tag) in enumerate(lines) if isinstance(tag, tuple) and tag[1].name == "mtvec")
    at = p1 + MTVEC_AGAIN_GAP + 1
    while len(lines) < at:
        lines.append((_alu(rng), None))   # mtvec read late in the stream: pad so the gap holds
    lines.insert(at, (_csrr(REG_MTVEC2, CSR["mtvec"]), ("read", mtvec2)))
    q = max(at + 1, lead_end + (1 if at <= lead_end else 0))
    while q < len(lines) and not isinstance(lines[q][1], Report):
        q += 1
    while q < len(lines) and isinstance(lines[q][1], Report):
        q += 1
    lines.insert(q, (f"sw x{REG_MTVEC2}, 0(x{REG_EOT})", mtvec2))

    # epilogue (end-of-test convention of gen_zc_directed.S); `la` is two instructions
    lines.append((f"li gp, {TOHOST_PASS}", None))
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
    p.final_idx = final_idx
    p.min_retired = final_idx - 1   # floor at the tohost store: the instruction before it may still be in WB, unreported

    # RED: one read of the item re-targeted after every program draw, so the plan (and every index) is the green one
    if red:
        p.red_item = red_item or random.Random(f"{int(seed)}:{RED_STREAM}").choice(RED_ITEMS)
        name, instead = RED_TARGETS[p.red_item]
        i = next(i for i, (_, tag) in enumerate(lines) if isinstance(tag, tuple) and tag[1].name == name)
        rd = lines[i][1][1]
        lines[i] = (_csrr(rd.reg, CSR[instead]), lines[i][1])
        p.red_note = f"{name} read as {instead}"
    p.lines = [text for text, _ in lines]
    return p


def bounds(rep, env):
    """(lo, hi, care, note) of a report word: the word passes when lo <= (got & care) <= hi; care < MASK32 and the
    note name the bits the run's regimes leave open. env: boot_addr, hart_id, key_valid (1, 0 or None when the
    responder timing is not visible), irq_quiet (bool), eot_cycle (bridge cycle count at the end-of-test store)."""
    r = rep.rule
    if r == "const":
        return rep.param, rep.param, MASK32, ""
    if r == "mtvec_boot":
        v = (env["boot_addr"] & BOOT_PAGE_MASK) | 1      # {boot_addr[31:8], 8'h01}: vectored, BASE = boot page
        return v, v, MASK32, ""
    if r == "hart_id":
        return env["hart_id"], env["hart_id"], MASK32, ""
    if r == "mip_pins":
        if env["irq_quiet"]:
            return 0, 0, MASK32, ""
        return 0, 0, MASK32 & ~MIP_LINE_MASK, "irq regime not quiet: line bits reported, the others gated"
    if r == "cpuctrl_key":
        if env["key_valid"] is None:
            return 0, 0, MASK32 & ~KEY_BIT, "scramble key withheld: bit 8 reported, the others gated"
        v = env["key_valid"] << CPUCTRL_KEY_BIT
        return v, v, MASK32, ""
    if r == "cycles":
        # one cycle per retirement at least: idx <= mcycle <= bridge cycles left before the end-of-test store
        return rep.idx, env["eot_cycle"] - rep.remaining + MCYCLE_SLACK, MASK32, ""
    if r == "instret":
        return rep.idx, rep.idx, MASK32, ""   # exactly the retirements before the csrr (it is not retired yet)
    if r == "hpm_small":
        return 0, env["eot_cycle"], MASK32, ""
    if r == "count_window":
        return max(rep.param - LDST_SKEW, 0), rep.param, MASK32, ""
    raise AssertionError(f"gen_csr_reset_prog: unknown rule {r}")


def emit(p):
    red = f" RED {p.red_item}: {p.red_note}" if p.red else ""
    out = [f"# gen_csr_reset_prog.py: generated for seed {p.seed}{red} (do not edit; regenerate)",
           f"# group gen_csr_reset; {p.k} report words; lead {p.early} (bounded {', '.join(p.bounded)}); first read "
           f"{p.first_csr}; final_idx {p.final_idx}",
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
    ap.add_argument("--red", action="store_true", help="deviate the program on one item's intent")
    ap.add_argument("--red-item", choices=RED_ITEMS, default=None, help="the item (implies --red; drawn from the seed when absent)")
    ap.add_argument("--summary", action="store_true", help="print the report table")
    a = ap.parse_args()
    p = plan(a.seed, a.red, a.red_item)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    text = emit(p)
    assert all(ord(c) < 128 for c in text), "non-ASCII in generated program"
    a.out.write_text(text)
    print(f"gen_csr_reset_prog: seed={p.seed} red={p.red} red_item={p.red_item or '-'} k={p.k} final_idx={p.final_idx} "
          f"lead={p.early} bounded={','.join(p.bounded)} first={p.first_csr} mtvec_first={p.mtvec_first} lines={len(p.lines)} out={a.out}")
    if a.summary:
        for r in p.reports:
            print(f"  {r.pos:3d} {r.item} {r.name:16s} 0x{r.addr:03x} x{r.reg:<2d} idx={r.idx:3d} rule={r.rule} param={r.param}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
