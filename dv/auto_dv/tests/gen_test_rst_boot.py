"""gen_test_rst_boot: reset and boot state of the core as software sees it (test-plan group gen_rst_boot).

Items built (dv/auto_dv/docs/gen_test_plan.md, area RST; canonical feature IDs through
gen_feature_list.md Section 3):
  TP-RST-003 (F-RST-004)  fire_tp_rst_003: csrr mtvec before any write reads {boot_addr_i[31:8], 8'h01}.
                           Clause not asserted: the ecall through the reset vector (the boot page carries
                           no vector table the program may write; needs the RVFI trap record).
  TP-RST-006 (F-RST-006; alias F-IRQ-065)  fire_tp_rst_006: csrr mstatus = MSTATUS_RESET and csrr mie = 0
                           as the first instructions (M-mode-only reads that do not trap); an mret with a
                           seed-drawn mepc lands in U-mode, where the pad's mstatus read traps with
                           mcause 2, mstatus in the handler 0x80 (MPP = U), mepc = the pad's trapping
                           instruction (image symbol), the pad's ALU result computed in U-mode, and the
                           program's unexpected-trap counter 0 (no interrupt taken with mie = 0).
                           Clauses BLOCKED, not asserted: "an interrupt line held high from reset" (the
                           program drives no pin; knob_irq_regime has no REGIME_SET consumer at HEAD and no
                           pin export reaches the Python side, so whether a line was high is unobserved);
                           "first record has rvfi_mode = 3" and "the record after mret has rvfi_mode = 0"
                           (RVFI record export; the U-mode landing is checked by its trap proxy only).
  TP-RST-007 (F-RST-007)  fire_tp_rst_007: reset read-back of mcause, mepc, mie, mtval, mscratch,
                           cpuctrlsts (bit 8 = scramble-key valid), mcountinhibit, mcounteren, mseccfg,
                           pmpcfg*, pmpaddr* (PMPNumRegions of ibex_configs.yaml), tselect, tdata1
                           (0x28001048, doc mismatch D4) in a seed-shuffled order through W-CSROP read-only
                           forms. Clause not asserted: dcsr/dpc/dscratch0/1 (debug-mode CSRs; need the
                           DBG_REQ bridge command).
Items of the group NOT built here (their fire-checks need pin or RVFI facts the Python side cannot
observe today: bridge counts, end-of-test code and report words are the only channels): TP-SEC-031
(F-SEC-029), TP-RST-001 (F-RST-001, F-RST-009), TP-RST-002 (F-RST-002), TP-RST-004 (F-RST-003, folded
F-RST-025), TP-RST-005 (F-CSR-020 via alias F-RST-005), TP-RST-008 (F-RST-008), TP-RST-027 (F-RVFI-003
via fold F-RST-026), TP-RVFI-036 (F-RST-009 via fold F-RVFI-033).

Program: dv/auto_dv/tests/gen_programs/gen_rst_boot_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`); the program stores every observation RAW to the EOT MMIO register and
the checks below compare self.reports[i] with plan(seed).reports[i]. Every read lands in rd != x0, so
the ISA comparator sees every value; its cpuctrlsts bit 8 and tdata1 misses are T-102 shim rows and
FAIL the flow verdict until TB Infra lands them. TB-side facts the expectations need: +gen_boot_addr
(mtvec), +gen_key_reset_valid with the scramble-key regime (cpuctrlsts bit 8), the image sidecar
symbols (mepc of the pad). W-BOOT (boot_addr_i class, hart_id_i) is a TB input the program cannot draw;
the entry runs the image's boot page.
Red fixtures: `--red --red-item <id>` (or `--red` alone, item drawn from the seed) deviates the program on
one item's intent so exactly fire_tp_rst_003 / 006 / 007 fails (generator docstring).

Knobs (the built items' Knobs lines): knob_imem_gnt_delay, knob_imem_rvalid_delay (TP-RST-003),
knob_irq_regime (TP-RST-006: lines may be driven, mie stays 0, nothing may be taken),
knob_scr_key_delay (TP-RST-007). declare_bins() is the template
default (the plan's bins of the three fire_tp items, checked against the rendered manifest in finish()).
Checkers relied on: gen_isa_compare (isa_rd / isa_csr on every CSR read and write),
gen_chk_csr_readback, gen_chk_ibus_proto / gen_chk_dbus_proto, gen_chk_irq (irq_pending_o = 0 with
mie = 0), gen_chk_rvfi_proto.
MODULE=dv.auto_dv.tests.gen_test_rst_boot, TOPLEVEL=gen_tb_top.

The cpuctrlsts bit 8 read-back is a consistency compare until the scrkey_proto checker exists. Precondition not applied: irq agent absent; TP-RST-006's interrupt-line-held clause is not programmed (register clauses only, GEN_TEST_INFO carries the label); its irq bin is excluded from the manifest (bins_not_hit).
"""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP
from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_programs import gen_rst_boot_prog as prog
from dv.auto_dv.tests.gen_test_template import GenTest

KEY_KNOB = "knob_scr_key_delay"
CPUCTRLSTS_KEY_VALID_BIT = 8
MASK32 = 0xFFFFFFFF
MAX_MISMATCH_DETAIL = 3
# The key regimes from the rendered knob table; the expectation below is tied to their order (the key is
# answered within key_delay_max cycles in the first two), so any rename or new value fails here, loud.
KEY_REGIMES = lib.knob_values(KEY_KNOB)
assert KEY_REGIMES == ["immediate", "delayed", "withheld_then_valid"], \
    f"GEN_TEST_RST_BOOT: {KEY_KNOB} values changed ({KEY_REGIMES}); re-derive the cpuctrlsts bit-8 expectation"
KEY_EARLY_REGIMES = set(KEY_REGIMES[:2])


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
    request then) or when its out-of-reset request is answered by the early regimes (at most
    key_delay_max cycles, while the core is still held for the image read-back). The withheld regime
    (key_never_cycles) is not predictable without the read's cycle: None, and bit 8 is reported, not gated."""
    key_valid = lib.plus_int("key_reset_valid", lib.knob_default("key_reset_valid"))
    regimes = _knob_regimes(test, KEY_KNOB)
    unknown = regimes - set(KEY_REGIMES)
    assert not unknown, f"GEN_TEST_RST_BOOT: {KEY_KNOB} takes value(s) {sorted(unknown)} outside the knob table"
    if key_valid == 1 or regimes <= KEY_EARLY_REGIMES:
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
    """(ok, detail) over every report word of one item; the detail names the first mismatches only."""
    idxs = [i for i, r in enumerate(p.reports) if r.item == item]
    bad = []
    for i in idxs:
        rep = p.reports[i]
        got = test.reports[i] if i < len(test.reports) else None
        exp = _expected(test, rep)
        if got is None:
            bad.append(f"{rep.name} (report {i}) missing")
        elif exp is None:   # cpuctrlsts under the withheld key regime: every bit but 8 is gated
            if got & ~(1 << CPUCTRLSTS_KEY_VALID_BIT) & MASK32:
                bad.append(f"{rep.name}=0x{got:08x} (expected every bit but 8 clear)")
            test.info(item, f"{rep.name} bit8={(got >> CPUCTRLSTS_KEY_VALID_BIT) & 1} (key regime withheld, not gated)")
        elif got != exp:
            bad.append(f"{rep.name}=0x{got:08x} (expected 0x{exp:08x})")
    n = len(idxs)
    detail = f"{n - len(bad)}/{n} report words of {item} match (reports {idxs[0]}..{idxs[-1]})"
    if bad:
        detail += ": " + ", ".join(bad[:MAX_MISMATCH_DETAIL])
        if len(bad) > MAX_MISMATCH_DETAIL:
            detail += f", +{len(bad) - MAX_MISMATCH_DETAIL} more"
    return not bad and len(test.reports) >= p.k, detail


class RstBoot(GenTest):
    name = "gen_test_rst_boot"
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_irq_regime", KEY_KNOB)
    mie_stays_zero = True   # no handler: the program never writes mstatus.MIE or mie, so driven lines are never taken (TP-RST-006)
    # items of the plan group this test does not check, with the reason (two-sided against the group by the structure check)
    # bins of built items this test cannot hit (irq precondition not applied); excluded from the manifest with the reason
    bins_not_hit = {
        "gen_rst_boot_cg.cp_boot_addr.zero":
            "stimulus: the TB drives a fixed non-zero boot address; a zero boot address is not driven by any run of this entry",
        "gen_rst_boot_cg.cr_pending_first.irq_enabled_later_first_instr_retire":
            "irq agent absent: no interrupt line is driven",
        "gen_sec_ctrl_inputs_cg.cp_bit8_readback.zero":
            "stimulus: bit 8 is the registered ic_scr_key_valid_i and the TB drives the key valid out of reset (gen_key_reset_valid default 1), which this entry does not turn off, so every cpuctrlsts read returns one there; the reset expectation of this test asserts that bit",
    }
    not_built = {
        "TP-SEC-031": "alert pin behaviour at reset: needs the event export (pin records)",
        "TP-RST-001": "first fetch address: needs the bus records of the event export",
        "TP-RST-002": "boot bus facts: needs the bus records of the event export",
        "TP-RST-004": "reset pin sequencing: needs the pin records of the event export",
        "TP-RST-005": "reset pin sequencing: needs the pin records of the event export",
        "TP-RST-008": "boot bus facts: needs the bus records of the event export",
        "TP-RST-027": "reset-time bus/pin facts: needs the event export",
        "TP-RVFI-036": "RVFI record fact: needs the record export",
    }

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
        self.info("TP-RST-006", "precondition not applied: irq agent absent (step 2b); the interrupt-line-held clause is not programmed")

    def fire_tp_rst_007(self):
        p = prog.plan(self.seed)
        ok, detail = _compare(self, p, "TP-RST-007")
        # mie is read once and belongs to both items; it is gated here as well
        i = p.index("mie")
        mie_ok = i < len(self.reports) and self.reports[i] == 0
        self.check("fire_tp_rst_007", ok and mie_ok, detail + (f"; mie=0x{self.reports[i]:08x}" if i < len(self.reports) else "; mie missing"))


@cocotb.test()
async def gen_test_rst_boot(dut):
    await RstBoot(dut).run()
