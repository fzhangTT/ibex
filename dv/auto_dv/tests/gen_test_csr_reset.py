"""gen_test_csr_reset: reset values of every CSR read at boot (test-plan group gen_csr_reset).

Items (dv/auto_dv/docs/gen_test_plan.md): TP-CSR-037 (mtvec boot value, first read and again after 10
instructions), TP-CSR-105 (trap-setup and machine-information CSRs), TP-CSR-106 (trap-handling CSRs),
TP-CSR-107 (counter CSRs, doc mismatch D20), TP-CSR-108 (trigger CSRs in M-mode, doc mismatch D4),
TP-CSR-109 (custom and PMP CSRs). Canonical feature IDs (gen_feature_list.md Section 3): F-CSR-035
(F-CSR-037 folded), F-CSR-019, F-CSR-021, F-CSR-023, F-CSR-027, F-CSR-028, F-CSR-029, F-PMC-025
(alias F-CSR-050), F-CSR-032, F-CSR-038, F-CSR-039, F-CSR-042, F-CSR-047, F-PMC-020 (F-CSR-058),
F-PMC-018 (F-CSR-061), F-PMC-001 (F-CSR-062), F-PMC-007 (F-CSR-066), F-PMC-015 (F-CSR-069), F-DBG-012
(F-CSR-074), F-CSR-078, F-CSR-079, F-CSR-080, F-CSR-081, F-TRG-007 (F-CSR-082), F-CSR-085, F-CSR-092,
F-CSR-094, F-CSR-096.

Program: dv/auto_dv/tests/gen_programs/gen_csr_reset_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`): every reset-value CSR of the items is read once (mtvec twice) in a
seed-drawn order into seed-drawn registers with W-FILL fillers between the reads, and every raw
read-back is stored to the EOT MMIO register in read order (plan.k report words), then tohost 1. The
expectation of each word comes from plan(self.seed) and prog.bounds(): the specification and the Ibex
documentation for constants (RTL followed only for D4 tdata1 and D20 mhpmevent), the run's plusargs
for mtvec (+gen_boot_addr), mhartid (+gen_hart_id) and cpuctrlsts bit 8 (+gen_key_reset_valid and
the scramble-key regime), the bridge cycle count at the end-of-test store for the counters (each
retirement takes at least one cycle) and the program's own instruction index for minstret/instret.
Fire-checks: fire_tp_csr_037, _105, _106, _107, _108, _109 (one self.check per item over its words,
through fire_item).

Knobs: the items' Knobs lines (imem_gnt_delay, imem_rvalid_delay, irq_line_mix, debug_req_regime,
scr_key_delay) are declared schedulable; nothing is pinned. layers_required = False: the TB has no
REGIME_SET consumer at HEAD (step 2b parked), so the layers are logged not_applied; flips to the
default when step 2b lands (the testlist entry stays tier check, measured: false until then).

Not built (channels missing at HEAD): TP-CSR-037's ecall into the reset vector (BASE = boot page + 0
is outside the linkable program window, and the trap-target pc needs the RVFI export); TP-CSR-106's
random irq pin pattern (IRQ_SET bridge codes not rendered; mip is asserted 0 with no line driven);
TP-CSR-108's debug-mode reads of dcsr/dpc/dscratch0/1 (DBG_REQ bridge codes not rendered,
rvfi_ext_debug_mode not observable); the "within the first N retirements" ordering facts of 105/106/
109 (RVFI export). Always-on checkers relied on: the ISA comparator rows isa_pc/isa_insn/isa_trap/
isa_rd/isa_mem/isa_prv/isa_pc_next, rvfi_proto, the bus protocol checkers (ibus/dbus). declare_bins() takes the template default (the plan's bins for the group, checked against the
rendered manifest in finish(); the entry stays unwired until gen_fcov_pkg lands). MODULE=dv.auto_dv.tests.gen_test_csr_reset, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_csr_reset_prog as prog

KEY_BIT = 1 << prog.CPUCTRL_KEY_BIT


def _hex_plus(name):
    """A hex-kind plusarg (GenImage passes them as bare hex digits) or its rendered default."""
    v = lib.plus(name, lib.knob_default(name))
    return int(v, 16) if isinstance(v, str) else int(v)


def _key_valid(test):
    """cpuctrlsts.ic_scr_key_valid at the read: the responder drives +gen_key_reset_valid out of reset and
    the icache requests a key only when it is low; a withheld key (regime withheld_then_valid) returns
    after +gen_key_never_cycles, which may or may not precede the read (None = not predictable)."""
    if lib.plus_int("key_reset_valid", lib.knob_default("key_reset_valid")):
        return 1
    if lib.plus("knob_scr_key_delay", lib.knob_default("knob_scr_key_delay")) != "withheld_then_valid":
        return 1
    never = lib.plus_int("key_never_cycles", lib.knob_default("key_never_cycles"))
    rep = test._plan.find("cpuctrlsts")
    if never + 2 <= rep.idx:
        return 1
    if never + 2 > test.eot_cycle - rep.remaining:
        return 0
    return None


def _env(test):
    return {"boot_addr": _hex_plus("boot_addr"), "hart_id": _hex_plus("hart_id"),
            "key_valid": _key_valid(test), "eot_cycle": test.eot_cycle}


def _word(test, rep):
    return test.reports[rep.pos] if rep.pos < len(test.reports) else None


def _fmt(v):
    return "none" if v is None else f"0x{v:08x}"


class CsrReset(GenTest):
    name = "gen_test_csr_reset"
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_irq_line_mix", "knob_debug_req_regime",
                   "knob_scr_key_delay")
    # Bring-up flag (tier check, measured false): no REGIME_SET consumer at HEAD; back to the default with step 2b.
    layers_required = False

    def report_count(self):
        self._plan = prog.plan(self.seed)
        return self._plan.k

    def fire_check(self):
        self.fire_tp_csr_037()
        self.fire_tp_csr_105()
        self.fire_tp_csr_106()
        self.fire_tp_csr_107()
        self.fire_tp_csr_108()
        self.fire_tp_csr_109()

    def fire_item(self, item, extra=()):
        """One self.check per item: every report word of the item within prog.bounds(), plus the `extra`
        (name, ok, detail) relations; the detail names the first mismatches (expected vs actual)."""
        env = _env(self)
        reps = self._plan.by_item(item)
        bad = []
        for r in reps:
            got = _word(self, r)
            lo, hi = prog.bounds(r, env)
            if r.rule == "cpuctrl_key" and env["key_valid"] is None:
                ok = got is not None and (got & ~KEY_BIT) == 0
                self.info(item, f"cpuctrlsts bit 8 not predictable (withheld key); other bits checked; got {_fmt(got)}")
            else:
                ok = got is not None and lo <= got <= hi
            if not ok:
                exp = f"0x{lo:08x}" if lo == hi else f"[0x{lo:08x}, 0x{hi:08x}]"
                bad.append(f"{r.name} got {_fmt(got)} expected {exp}")
        n_words_bad = len(bad)
        for name, ok, detail in extra:
            if not ok:
                bad.append(f"{name}: {detail}")
        detail = f"{len(reps) - n_words_bad}/{len(reps)} read-backs in bounds, {len(extra) - (len(bad) - n_words_bad)}/{len(extra)} relations hold"
        if bad:
            detail += "; " + " | ".join(bad[:6]) + (f" | +{len(bad) - 6} more" if len(bad) > 6 else "")
        self.check(f"fire_tp_csr_{item[-3:]}", not bad, detail)

    def fire_tp_csr_037(self):
        # mtvec == {boot_addr[31:8], 8'h01} at its first read (first instruction or early) and 10 instructions later
        p = self._plan
        first, again = p.find("mtvec"), p.find("mtvec_again")
        v1, v2 = _word(self, first), _word(self, again)
        lo, hi = prog.bounds(first, _env(self))
        same = ("mtvec stable", v1 is not None and v1 == v2,
                f"first {_fmt(v1)} (retirement {first.idx}, mtvec_first={p.mtvec_first}) again {_fmt(v2)} (retirement {again.idx})")
        boot = ("mtvec first read", v1 is not None and lo <= v1 <= hi, f"mtvec {_fmt(v1)} expected 0x{lo:08x} (boot page | 1)")
        self.fire_item("TP-CSR-037", extra=(same, boot))

    def fire_tp_csr_105(self):
        self.fire_item("TP-CSR-105")

    def fire_tp_csr_106(self):
        self.fire_item("TP-CSR-106")

    def fire_tp_csr_107(self):
        # alias pairs: cycle/mcycle differ by at least the instructions between them; instret/minstret by exactly that (+-1)
        p = self._plan
        rel = []
        for a, b, kind in (("mcycle", "cycle", "cycles"), ("minstret", "instret", "instret")):
            ra, rb = sorted((p.find(a), p.find(b)), key=lambda r: r.idx)
            va, vb = _word(self, ra), _word(self, rb)
            gap = rb.idx - ra.idx
            if va is None or vb is None:
                rel.append((f"{a}/{b}", False, "report missing"))
            elif kind == "cycles":
                rel.append((f"{a}/{b}", vb - va >= gap, f"{rb.name} - {ra.name} = {vb - va}, {gap} instructions apart"))
            else:
                rel.append((f"{a}/{b}", abs((vb - va) - gap) <= 1, f"{rb.name} - {ra.name} = {vb - va}, {gap} instructions apart"))
        self.fire_item("TP-CSR-107", extra=rel)

    def fire_tp_csr_108(self):
        self.fire_item("TP-CSR-108")

    def fire_tp_csr_109(self):
        self.fire_item("TP-CSR-109")


@cocotb.test()
async def gen_test_csr_reset(dut):
    await CsrReset(dut).run()
