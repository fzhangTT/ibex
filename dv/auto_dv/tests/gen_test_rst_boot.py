"""gen_test_rst_boot: reset and boot state of the core as software sees it (test-plan group gen_rst_boot).

Items built (dv/auto_dv/docs/gen_test_plan.md, area RST; canonical feature IDs through
gen_feature_list.md Section 3):
  TP-RST-003 (F-RST-004)  fire_tp_rst_003: csrr mtvec before any write reads {boot_addr_i[31:8], 8'h01};
                           the ecall through the reset vector is not built (the boot page carries no
                           vector table the program may write; needs the RVFI trap record).
  TP-RST-006 (F-RST-006; alias F-IRQ-065)  fire_tp_rst_006: csrr mstatus = 0x80 and csrr mie = 0 as the
                           first instructions (M-mode-only reads that do not trap); an mret with a
                           seed-drawn mepc lands in U-mode, where the pad's mstatus read traps with
                           mcause 2, mstatus in the handler 0x80 (MPP = U), mepc = the pad's trapping
                           instruction (image symbol), the pad's ALU result computed in U-mode, and the
                           program's unexpected-trap counter 0 (no interrupt taken with mie = 0).
  TP-RST-007 (F-RST-007)  fire_tp_rst_007: reset read-back of mcause, mepc, mie, mtval, mscratch,
                           cpuctrlsts (bit 8 = scramble-key valid), mcountinhibit, mcounteren, mseccfg,
                           pmpcfg0..3, pmpaddr0..15, tselect, tdata1 (0x28001048, doc mismatch D4) in a
                           seed-shuffled order through W-CSROP read-only forms; dcsr/dpc/dscratch0/1 are
                           debug-mode CSRs and need the DBG_REQ bridge command (not built).
Items of the group NOT built here (their fire-checks need pin or RVFI facts the Python side cannot
observe today: bridge counts, end-of-test code and report words are the only channels): TP-SEC-031
(F-SEC-029), TP-RST-001 (F-RST-001, F-RST-009), TP-RST-002 (F-RST-002), TP-RST-004 (F-RST-003, folded
F-RST-025), TP-RST-005 (F-CSR-020 via alias F-RST-005), TP-RST-008 (F-RST-008), TP-RST-027 (F-RVFI-003
via fold F-RST-026), TP-RVFI-036 (F-RST-009 via fold F-RVFI-033).

Program: dv/auto_dv/tests/gen_programs/gen_rst_boot_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`); the program stores every observation RAW to the EOT MMIO register and
the checks below compare self.reports[i] with plan(seed).reports[i]. TB-side facts the expectations
need: +gen_boot_addr (mtvec), +gen_key_reset_valid with the scramble-key regime (cpuctrlsts bit 8), the
image sidecar symbols (mepc of the pad). W-BOOT (boot_addr_i class, hart_id_i) is a TB input the
program cannot draw; the entry runs the image's boot page.

Knobs (the built items' Knobs lines): knob_imem_gnt_delay, knob_imem_rvalid_delay (TP-RST-003),
knob_irq_regime (TP-RST-006: lines may be driven, mie stays 0, nothing may be taken),
knob_scr_key_delay (TP-RST-007). layers_required = False: the TB has no REGIME_SET consumer at HEAD
(step 2b parked), so the layers are logged not_applied; flips to the default when step 2b lands.
declare_bins() returns [] because no covergroup exists yet (the manifest is wired when gen_fcov_pkg
lands). Checkers relied on: gen_isa_compare (isa_rd / isa_csr on every CSR read and write),
gen_chk_csr_readback, gen_chk_ibus_proto / gen_chk_dbus_proto, gen_chk_irq (irq_pending_o = 0 with
mie = 0), gen_chk_rvfi_proto.
MODULE=dv.auto_dv.tests.gen_test_rst_boot, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_rst_boot_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

KEY_KNOB = "knob_scr_key_delay"
CPUCTRLSTS_KEY_VALID_BIT = 8


def _plus_hex(name):
    """A hex-kind plusarg (+gen_boot_addr=80000000) or its rendered default."""
    v = lib.plus(name, lib.knob_default(name))
    return int(v, 16) if isinstance(v, str) else int(v)


def _knob_regimes(test, knob):
    """Every value the knob takes in this run: the pinned value, or the layer-2 draw plus every
    scheduled phase value (the read's cycle is not visible, so all of them may apply)."""
    if lib.knob_is_pinned(knob):
        return {lib.plus(knob)}
    vals = {test.knobs.get(knob, lib.knob_default(knob))}
    if test.schedule is not None:
        vals |= {p.value for p in test.schedule.phases if p.knob == knob}
    return vals


def _cpuctrlsts_reset(test):
    """cpuctrlsts at the read: bits 7:0 and 31:9 are 0; bit 8 is the registered ic_scr_key_valid_i.
    The key is valid at the read when the TB drives it valid through reset (the icache raises no
    request then) or when its out-of-reset request is answered by the immediate/delayed regimes
    (at most key_delay_max cycles, while the core is still held for the image read-back). The
    withheld_then_valid regime (key_never_cycles) is not predictable without the read's cycle: the
    value then carries None and bit 8 is reported, not gated."""
    key_valid = lib.plus_int("key_reset_valid", lib.knob_default("key_reset_valid"))
    regimes = _knob_regimes(test, KEY_KNOB)
    if key_valid == 1 or regimes <= {"immediate", "delayed"}:
        return 1 << CPUCTRLSTS_KEY_VALID_BIT
    return None


def _expected(test, rep):
    e = rep.expect
    if e.kind == "const":
        return int(e.value)
    if e.kind == "mtvec_reset":
        return (_plus_hex("boot_addr") & MEMORY_MAP["boot_page_mask"]) | 1
    if e.kind == "cpuctrlsts_reset":
        return _cpuctrlsts_reset(test)
    if e.kind == "symbol":
        syms = test.image.sidecar.get("symbols", {})
        assert e.value in syms, f"GEN_TEST_RST_BOOT: program image defines no symbol {e.value}"
        return int(syms[e.value], 16)
    raise AssertionError(f"GEN_TEST_RST_BOOT: unknown expectation kind {e.kind}")


def _compare(test, p, item):
    """(ok, detail) over every report word of one item: expected vs actual per word, mismatches named."""
    idxs = [i for i, r in enumerate(p.reports) if r.item == item]
    lines, bad, info = [], [], []
    for i in idxs:
        rep = p.reports[i]
        got = test.reports[i] if i < len(test.reports) else None
        exp = _expected(test, rep)
        if got is None:
            bad.append(f"{rep.name}: report {i} missing")
            continue
        if exp is None:   # cpuctrlsts under the withheld key regime: gate every bit but 8
            mask = ~(1 << CPUCTRLSTS_KEY_VALID_BIT) & 0xFFFFFFFF
            ok = (got & mask) == 0
            info.append(f"{rep.name} bit8={(got >> CPUCTRLSTS_KEY_VALID_BIT) & 1} (key regime withheld, not gated)")
        else:
            ok = got == exp
        lines.append(f"{rep.name}=0x{got:08x}" + ("" if ok else f" (expected 0x{exp:08x})" if exp is not None else " (expected other bits 0)"))
        if not ok:
            bad.append(lines[-1])
    for m in info:
        test.info(item, m)
    n = len(idxs)
    detail = (f"{n - len(bad)}/{n} report words match" + (": " + ", ".join(bad) if bad else "")
              + f" [reports {idxs[0]}..{idxs[-1]}: " + " ".join(lines) + "]")
    return not bad and len(test.reports) >= p.k, detail


class RstBoot(GenTest):
    name = "gen_test_rst_boot"
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_irq_regime", KEY_KNOB)
    # Bring-up (tier check, measured false): no REGIME_SET consumer at HEAD; flips to the default when
    # TB Infra's step 2b lands.
    layers_required = False

    def report_count(self):
        return prog.plan(self.seed).k

    def fire_check(self):
        self.fire_tp_rst_003()
        self.fire_tp_rst_006()
        self.fire_tp_rst_007()

    def fire_tp_rst_003(self):
        p = prog.plan(self.seed)
        i = p.index("mtvec")
        exp = _expected(self, p.reports[i])
        got = self.reports[i] if i < len(self.reports) else None
        self.check("fire_tp_rst_003", got == exp,
                   f"csrr mtvec before any write 0x{got:08x} (expected boot page | 1 = 0x{exp:08x}, +gen_boot_addr 0x{_plus_hex('boot_addr'):08x})"
                   if got is not None else f"report {i} (mtvec) missing")

    def fire_tp_rst_006(self):
        ok, detail = _compare(self, prog.plan(self.seed), "TP-RST-006")
        self.check("fire_tp_rst_006", ok, detail)

    def fire_tp_rst_007(self):
        p = prog.plan(self.seed)
        ok, detail = _compare(self, p, "TP-RST-007")
        # mie is read once and belongs to both items; it is gated here as well
        i = p.index("mie")
        mie_ok = i < len(self.reports) and self.reports[i] == 0
        self.check("fire_tp_rst_007", ok and mie_ok, detail + (f"; mie=0x{self.reports[i]:08x}" if i < len(self.reports) else "; mie missing"))

    def declare_bins(self):
        return []   # no covergroup exists yet (TB Infra build step 3); the manifest is wired then


@cocotb.test()
async def gen_test_rst_boot(dut):
    await RstBoot(dut).run()
