"""gen_test_csr_reset: reset values of every CSR read at boot (test-plan group gen_csr_reset).

Items built, 6 of 6 (dv/auto_dv/docs/gen_test_plan.md; canonical feature IDs through gen_feature_list.md
Section 3; every word is checked by the fire-check named, through fire_item over prog.bounds()):
  TP-CSR-037 (F-CSR-035, F-CSR-037 folded)  fire_tp_csr_037: mtvec == {boot_addr[31:8], 8'h01} at its first read
      and again 10 instructions later (unchanged); on the seeds that draw mtvec first, that read is the first
      program retirement. Clause not built: the ecall into the reset vector (BASE = boot page + 0 is outside the
      linkable program window; the trap target needs the RVFI export).
  TP-CSR-105 (F-CSR-019, F-CSR-021, F-CSR-023, F-CSR-027, F-CSR-028, F-CSR-029, F-PMC-025 alias F-CSR-050)
      fire_tp_csr_105: the 13 words (mstatus MSTATUS_RESET, misa MISA_VALUE, mie/mcounteren/mstatush/menvcfg/
      menvcfgh 0, mvendorid/mimpid 0, marchid, mhartid = +gen_hart_id, mconfigptr, mtvec); on the seeds whose
      program leads with this item (Plan.bounded) the 13 reads sit within the first 16 retirements and the first
      program retirement is one of them.
  TP-CSR-106 (F-CSR-032, F-CSR-038, F-CSR-039, F-CSR-042, F-CSR-047)  fire_tp_csr_106: mscratch/mepc/mcause/
      mtval 0; mip 0 when the run's interrupt regime is quiet (knob_irq_regime is not schedulable here and the
      test issues no IRQ_SET, so a quiet regime makes the declared knob_irq_line_mix inert: gen_fcov_plan.md
      cr_regime_x_mix), otherwise only the bits no line drives are gated and the word is reported; within the
      first 16 retirements on the leading seeds. Clause not built: the random irq pin pattern (IRQ_SET bridge
      codes not rendered).
  TP-CSR-107 (F-PMC-020 F-CSR-058, F-PMC-018 F-CSR-061, F-PMC-001 F-CSR-062, F-PMC-007 F-CSR-066, F-PMC-015
      F-CSR-069)  fire_tp_csr_107: mcycle/cycle between the retirements before the read and the bridge cycles
      left before the end-of-test store; minstret/instret exactly the retirements before the read; mcycleh/
      minstreth/mcountinhibit 0; mhpmcounter3..(2+MHPMCounterNum) small or exact (jumps 1: the boot stub; taken
      branches, compressed, mul/div waits 0; loads/stores the program's own count), their h halves 0, mhpmevent
      one-hot 1 << (n - 3) (D20), the unimplemented samples 0; the cycle/mcycle and instret/minstret pairs
      ordered by the instructions between them.
  TP-CSR-108 (F-DBG-012 F-CSR-074, F-CSR-078, F-CSR-079, F-CSR-080, F-CSR-081, F-TRG-007 F-CSR-082)
      fire_tp_csr_108: tselect 0, tdata1 0x2800_1048 (D4), tdata2 0 in M-mode. Clause not built: the debug-mode
      reads of dcsr/dpc/dscratch0/1 (DBG_REQ bridge codes not rendered; rvfi_ext_debug_mode not observable).
  TP-CSR-109 (F-CSR-085, F-CSR-092, F-CSR-094, F-CSR-096)  fire_tp_csr_109: secureseed/mseccfg/mseccfgh 0,
      pmpcfg*/pmpaddr* 0 (PMPNumRegions of ibex_configs.yaml), cpuctrlsts = key_valid << 8 where key_valid comes
      from +gen_key_reset_valid and the scramble-key regimes of the run (the pinned value, or the layer-2 draw
      in self.knobs plus every scheduled phase value): valid when the key is valid through reset or every regime
      answers the out-of-reset request within key_delay_max cycles (immediate, delayed) while the core is still
      held for the image read-back; under withheld_then_valid the responder answers key_never_cycles + 1 cycles
      after the request and cpuctrlsts registers it a cycle later, but neither cycle is visible here, so bit 8
      is reported and the other bits gated; within the first 40 retirements on the leading seeds.

Retirement positions: Report.idx (retirements before the csrr; the boot stub's j _start is retirement 0) is a
program fact anchored on the DUT by eot_retired, the bridge count at the end-of-test store, within one of the
program's Plan.final_idx (RVFI reports a retirement from the WB stage, so the instruction before the store may
not be counted yet when its bus write is seen; the store itself may be counted by the time Python samples), and
by every report word matching; "within the first N retirements" is idx < N. The three bounds exclude each other in one program
(13 + 5 reads exceed 16), so the generator leads with one draw per seed (W_EARLY: TP-CSR-105; TP-CSR-106 then
TP-CSR-109; TP-CSR-109) and the fire-check of an item not led reports its positions without gating them.

Comparator: every read lands in rd != x0, so the ISA comparator sees every value; its rows for mstatus,
marchid, tdata1, cpuctrlsts bit 8 and mcycle/mhpm* are T-102 shim gaps that FAIL the flow verdict through
uvm_error until TB Infra lands them; the program dodges no read and this test's own words are checked here.

Program: dv/auto_dv/tests/gen_programs/gen_csr_reset_prog.py at the run seed (testlist `program:
{generator: ..., seed: run}`), plan.k report words then tohost TOHOST_PASS; red fixtures `--red
[--red-item <id>]` re-target one read of the item so exactly its fire-check fails (generator docstring).
Knobs: the items' Knobs lines (imem_gnt_delay, imem_rvalid_delay, irq_line_mix, debug_req_regime,
scr_key_delay) are declared schedulable; nothing is pinned. layers_required = False (bring-up opt-out, API doc Section 3; entry measured: false since d58bdeb). declare_bins() is
the template default (the plan's bins of the six fire_tp items, checked against the rendered manifest in
finish(); the entry stays unwired until gen_fcov_pkg lands). Always-on checkers relied on: the ISA comparator
rows isa_pc/isa_insn/isa_trap/isa_rd/isa_mem/isa_prv/isa_pc_next, rvfi_proto, the bus protocol checkers
(ibus/dbus). MODULE=dv.auto_dv.tests.gen_test_csr_reset, TOPLEVEL=gen_tb_top.

T-102 status: TB Infra's d0c0d15 and 50256f0 fixed the comparator conventions and the shim's CSR legalization (marchid, tdata1, cpuctrlsts bit 8), so the flow verdict is expected PASS from acceptance wave 4 on; the mcycle/cycle, mhpmcounter* and cpuctrlsts bit 8 read-backs are consistency compares against DUT-synchronised model state until the ctr_* and scrkey_proto checkers exist (Critic gen_critic_tb_t102.md), so TP-CSR-107/108's counter clauses count as checked for consistency, not value-verified.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_csr_reset_prog as prog

MASK32 = 0xFFFFFFFF
KEY_KNOB = "knob_scr_key_delay"
IRQ_KNOB = "knob_irq_regime"
MAX_DETAIL = 6
# The regimes from the rendered knob table; the expectations are tied to their order (the first two key regimes
# answer within key_delay_max cycles; the first irq regime drives no line), so a rename or new value fails loud.
KEY_REGIMES = lib.knob_values(KEY_KNOB)
assert KEY_REGIMES == ["immediate", "delayed", "withheld_then_valid"], \
    f"GEN_TEST_CSR_RESET: {KEY_KNOB} values changed ({KEY_REGIMES}); re-derive the cpuctrlsts bit-8 expectation"
KEY_EARLY_REGIMES = set(KEY_REGIMES[:2])
IRQ_REGIMES = lib.knob_values(IRQ_KNOB)
assert IRQ_REGIMES[0] == "quiet", f"GEN_TEST_CSR_RESET: {IRQ_KNOB} values changed ({IRQ_REGIMES}); re-derive the mip expectation"
IRQ_QUIET = IRQ_REGIMES[0]


def _hex_plus(name):
    """A hex-kind plusarg (GenImage passes them as bare hex digits) or its rendered default."""
    v = lib.plus(name, lib.knob_default(name))
    return int(v, 16) if isinstance(v, str) else int(v)


def _knob_regimes(test, knob):
    """Every value the knob takes in this run: the pinned value, or the layer-2 draw plus every scheduled
    phase value (the read's cycle is not visible, so all of them may apply)."""
    if lib.knob_is_pinned(knob):
        return {lib.plus(knob)}
    vals = {test.knobs.get(knob, lib.knob_default(knob))}
    if test.schedule is not None:
        vals |= {p.value for p in test.schedule.phases if p.knob == knob}
    return vals


def _key_valid(test):
    """cpuctrlsts.ic_scr_key_valid at the read: 1 when the key is valid through reset or every regime of the run
    answers early; None (reported, not gated) when a withheld regime may apply."""
    if lib.plus_int("key_reset_valid", lib.knob_default("key_reset_valid")) == 1:
        return 1
    regimes = _knob_regimes(test, KEY_KNOB)
    unknown = regimes - set(KEY_REGIMES)
    assert not unknown, f"GEN_TEST_CSR_RESET: {KEY_KNOB} takes value(s) {sorted(unknown)} outside the knob table"
    return 1 if regimes <= KEY_EARLY_REGIMES else None


def _irq_quiet(test):
    """No interrupt line is driven when every irq regime of the run is quiet (the line mix is then inert)."""
    regimes = _knob_regimes(test, IRQ_KNOB)
    unknown = regimes - set(IRQ_REGIMES)
    assert not unknown, f"GEN_TEST_CSR_RESET: {IRQ_KNOB} takes value(s) {sorted(unknown)} outside the knob table"
    return regimes == {IRQ_QUIET}


def _env(test):
    return {"boot_addr": _hex_plus("boot_addr"), "hart_id": _hex_plus("hart_id"), "key_valid": _key_valid(test),
            "irq_quiet": _irq_quiet(test), "eot_cycle": test.eot_cycle}


def _word(test, rep):
    return test.reports[rep.pos] if rep.pos < len(test.reports) else None


def _fmt(v):
    return "none" if v is None else f"0x{v:08x}"


class CsrReset(GenTest):
    name = "gen_test_csr_reset"
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay", "knob_irq_line_mix", "knob_debug_req_regime",
                   "knob_scr_key_delay")
    # Bring-up opt-out while no REGIME_SET consumer exists (API doc Section 3; entry measured: false).
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
        """One self.check per item: every report word of the item within prog.bounds() on its gated bits, plus the
        `extra` (name, ok, detail) relations; the detail names the first mismatches (expected vs actual)."""
        env = _env(self)
        reps = self._plan.by_item(item)
        bad = []
        for r in reps:
            got = _word(self, r)
            lo, hi, care, note = prog.bounds(r, env)
            ok = got is not None and lo <= (got & care) <= hi
            if care != MASK32:
                self.info(item, f"{r.name} {note}; got {_fmt(got)}, gated bits 0x{care:08x}")
            if not ok:
                exp = f"0x{lo:08x}" if lo == hi else f"[0x{lo:08x}, 0x{hi:08x}]"
                bad.append(f"{r.name} got {_fmt(got)} expected {exp}" + (f" on bits 0x{care:08x}" if care != MASK32 else ""))
        n_words_bad = len(bad)
        for name, ok, detail in extra:
            if not ok:
                bad.append(f"{name}: {detail}")
        detail = (f"{len(reps) - n_words_bad}/{len(reps)} read-backs in bounds, "
                  f"{len(extra) - (len(bad) - n_words_bad)}/{len(extra)} relations hold")
        if bad:
            detail += "; " + " | ".join(bad[:MAX_DETAIL]) + (f" | +{len(bad) - MAX_DETAIL} more" if len(bad) > MAX_DETAIL else "")
        self.check(f"fire_tp_csr_{item[-3:]}", not bad, detail)

    def fire_anchor(self):
        """(ok, detail): the bridge retirement count at the tohost store is within one of the program's count before
        it (the instruction before the store may still be in WB, unreported; the store itself may be counted by the
        sample), which ties every Report.idx to a DUT retirement."""
        fi, er = self._plan.final_idx, self.eot_retired
        return er is not None and fi - 1 <= er <= fi + 1, f"eot retired {er} vs program {fi}"

    def fire_position(self, item):
        """The plan's "within the first N retirements" relation of `item` when the program leads with it (Plan.bounded,
        first retirement in the item for TP-CSR-105); an item not led this seed reports its positions."""
        p = self._plan
        idxs = [r.idx for r in p.by_item(item)]
        bound = prog.RETIRE_BOUND[item]
        anchored, anchor = self.fire_anchor()
        span = f"reads at retirements {min(idxs)}..{max(idxs)}"
        if item not in p.bounded:
            self.info(item, f"{span}; bound {bound} not scheduled this seed (lead {p.early}); {anchor}")
            return ()
        first_ok = item != "TP-CSR-105" or p.first_item == item
        ok = max(idxs) < bound and first_ok and anchored
        return ((f"first {bound} retirements", ok, f"{span}, first read {p.first_csr} ({p.first_item}); {anchor}"),)

    def fire_tp_csr_037(self):
        # mtvec == {boot_addr[31:8], 8'h01} at its first read and again 10 instructions later; first retirement when drawn so
        p = self._plan
        first, again = p.find("mtvec"), p.find("mtvec_again")
        v1, v2 = _word(self, first), _word(self, again)
        lo, hi, _, _ = prog.bounds(first, _env(self))
        anchored, anchor = self.fire_anchor()
        rel = [("mtvec stable", v1 is not None and v1 == v2,
                f"first {_fmt(v1)} (retirement {first.idx}) again {_fmt(v2)} (retirement {again.idx})"),
               ("mtvec first read", v1 is not None and lo <= v1 <= hi, f"mtvec {_fmt(v1)} expected 0x{lo:08x} (boot page | 1)")]
        if p.mtvec_first:
            rel.append(("mtvec first retirement", first.idx == 1 and anchored, f"mtvec at retirement {first.idx}; {anchor}"))
        else:
            self.info("TP-CSR-037", f"mtvec not drawn first this seed (first read {p.first_csr}, mtvec at retirement {first.idx})")
        self.fire_item("TP-CSR-037", extra=tuple(rel))

    def fire_tp_csr_105(self):
        self.fire_item("TP-CSR-105", extra=self.fire_position("TP-CSR-105"))

    def fire_tp_csr_106(self):
        self.fire_item("TP-CSR-106", extra=self.fire_position("TP-CSR-106"))

    def fire_tp_csr_107(self):
        # alias pairs: cycle/mcycle differ by at least the instructions between them; instret/minstret by exactly that
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
                rel.append((f"{a}/{b}", vb - va == gap, f"{rb.name} - {ra.name} = {vb - va}, {gap} instructions apart"))
        self.fire_item("TP-CSR-107", extra=tuple(rel))

    def fire_tp_csr_108(self):
        self.fire_item("TP-CSR-108")

    def fire_tp_csr_109(self):
        self.fire_item("TP-CSR-109", extra=self.fire_position("TP-CSR-109"))


@cocotb.test()
async def gen_test_csr_reset(dut):
    await CsrReset(dut).run()
