"""gen_test_csr_trap_setup: test-plan group gen_csr_trap_setup (gen_test_plan.md Section 4.2), the trap-setup
CSRs mstatus, mie, mtvec and the read-as-zero mstatush / menvcfg / menvcfgh.

Items built (one fire-check each): TP-CSR-023 (mstatus random write/read-back against the WARL prediction,
fire_tp_csr_023), TP-CSR-024 (MPP 01/10 legalise to U and the following mret enters U-mode, observed as the
ecall cause 8 vs 11 the handler reports; pass (doc mismatch D2), fire_tp_csr_024), TP-CSR-025 (mstatus
all-ones reads back 0x0022_1888, clear reads 0, fire_tp_csr_025), TP-CSR-027 (mstatush reads 0, writes
ignored, no trap, fire_tp_csr_027), TP-CSR-028 (menvcfg/menvcfgh idem, fire_tp_csr_028), TP-CSR-029 (mie
random write/read-back under MIE_MASK, fire_tp_csr_029; its irq_pending_o clause needs the pin channel and
is not asserted), TP-CSR-030 (mie all-ones reads back MIE_MASK, fire_tp_csr_030), TP-CSR-035 (mtvec
read-back == BASE | 1 and the following ecall lands in the handler copy at BASE, observed as that copy's
marker word; the interrupt half needs an irq agent, fire_tp_csr_035), TP-CSR-036 (mtvec MODE / bits 7:2
legalised on write, fire_tp_csr_036). Not built (channels not observable or drivable from Python today, no
irq agent in the build): TP-CSR-026 (interrupt taken on MIE set; needs an irq agent and rvfi_intr) and
TP-CSR-031 (irq_pending_o / WFI wake timing; needs the irq agent, core_busy_o and per-cycle pin facts).
Canonical features covered (gen_feature_list.md Section 3): F-CSR-023 (carries the folded F-CSR-025 and
F-PRV-035), F-CSR-024, F-CSR-027, F-CSR-028, F-CSR-029 (carries the folded F-CSR-030), F-CSR-035 (carries
the folded F-CSR-036); not covered here: F-CSR-026, F-CSR-031.

Program: dv/auto_dv/tests/gen_programs/gen_csr_trap_setup_prog.py, a per-seed generator (testlist
`program: {generator: ..., seed: run}`); plan(seed) is the single source of the expected report words,
report_count() returns its k, and the fire-checks compare self.reports with it (link-address expectations
are resolved from the image sidecar). Knobs: knob_imem_gnt_delay and knob_imem_rvalid_delay (the fetch-
latency regimes the built items name); the irq knobs the items also name (irq_regime, irq_line_mix,
irq_hold) are excluded because the program has no interrupt handler and the build has no irq agent (they
belong to the blocked items). layers_required = False: the TB has no REGIME_SET consumer at HEAD (step 2b
parked), so the layers are logged not_applied; flips to the default when step 2b lands. declare_bins() takes the template default (the plan's bins for the group, checked against the
rendered manifest in finish(); the entry stays unwired until gen_fcov_pkg lands).
Checkers relied on besides the fire-checks: the always-on ISA comparator rows (isa_pc, isa_insn, isa_trap,
isa_rd, isa_mem, isa_prv, isa_pc_next, isa_csr), rvfi_proto and the bus protocol checkers.
MODULE=dv.auto_dv.tests.gen_test_csr_trap_setup, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest
from dv.auto_dv.tests.gen_programs import gen_csr_trap_setup_prog as prog

_PLANS = {}


def _plan(seed):
    if seed not in _PLANS:
        _PLANS[seed] = prog.plan(seed)
    return _PLANS[seed]


def _compare(test, item):
    """Mismatch list and count of the item's report words against the plan (symbols from the image sidecar)."""
    return prog.mismatches(_plan(test.seed), item, test.reports, test.image.sidecar.get("symbols", {}))


def _detail(n, bad, what):
    head = f"{n} {what}: {len(bad)} mismatch(es)"
    return head + (f"; first {bad[0]}" if bad else "")


class CsrTrapSetup(GenTest):
    name = "gen_test_csr_trap_setup"
    schedulable = ("knob_imem_gnt_delay", "knob_imem_rvalid_delay")
    # Bring-up flag: no REGIME_SET consumer exists at HEAD (step 2b parked); back to the default when it lands.
    layers_required = False

    def report_count(self):
        return _plan(self.seed).k

    def fire_check(self):
        self.fire_tp_csr_023()
        self.fire_tp_csr_024()
        self.fire_tp_csr_025()
        self.fire_tp_csr_027()
        self.fire_tp_csr_028()
        self.fire_tp_csr_029()
        self.fire_tp_csr_030()
        self.fire_tp_csr_035()
        self.fire_tp_csr_036()
        self.fire_program_integrity()

    def fire_tp_csr_023(self):
        bad, n = _compare(self, "TP-CSR-023")
        f = _plan(self.seed).facts["TP-CSR-023"]
        corners = f["mpp_written"] == {0, 1, 2, 3} and f["tw_written"] and f["mprv_written"]
        self.check("fire_tp_csr_023", n > 0 and not bad and corners,
                   _detail(n, bad, f"mstatus read-backs vs WARL model (mask 0x{prog.MST_MASK:08x}, MPP 01/10 -> 00)")
                   + f"; MPP values written {sorted(f['mpp_written'])}, TW written {f['tw_written']}, MPRV written {f['mprv_written']}")

    def fire_tp_csr_024(self):
        bad, n = _compare(self, "TP-CSR-024")
        f = _plan(self.seed).facts["TP-CSR-024"]
        self.check("fire_tp_csr_024", n > 0 and not bad and f["mpp_written"] == {0, 1, 2, 3} and f["u_rounds"] > 0,
                   _detail(n, bad, "MPP rounds (handler marker, ecall mcause 8 = U / 11 = M, mstatus read-back with MPP legalised)")
                   + f"; {f['rounds']} rounds, {f['u_rounds']} entered U-mode, MPP values written {sorted(f['mpp_written'])}")

    def fire_tp_csr_025(self):
        bad, n = _compare(self, "TP-CSR-025")
        self.check("fire_tp_csr_025", n > 0 and not bad,
                   _detail(n, bad, f"mstatus read-backs after csrrw/csrrs -1 (expect 0x{prog.MST_MASK:08x}) and csrrc -1 (expect 0)"))

    def fire_tp_csr_027(self):
        bad, n = _compare(self, "TP-CSR-027")
        self.check("fire_tp_csr_027", n > 0 and not bad,
                   _detail(n, bad, "mstatush read-backs (expect 0; last word = unexpected-trap count after the pairs, expect 0)"))

    def fire_tp_csr_028(self):
        bad, n = _compare(self, "TP-CSR-028")
        self.check("fire_tp_csr_028", n > 0 and not bad,
                   _detail(n, bad, "menvcfg/menvcfgh read-backs (expect 0; last word = unexpected-trap count after the pairs, expect 0)"))

    def fire_tp_csr_029(self):
        bad, n = _compare(self, "TP-CSR-029")
        f = _plan(self.seed).facts["TP-CSR-029"]
        all_fast = f["fast_bits"] == set(range(prog.MIE_FAST_W))
        self.check("fire_tp_csr_029", n > 0 and not bad and all_fast,
                   _detail(n, bad, f"mie read-backs vs MIE_MASK 0x{prog.MIE_MASK:08x} model")
                   + f"; fast bits written alone {len(f['fast_bits'])} of {prog.MIE_FAST_W}, op x class combinations {len(f['op_class'])}")

    def fire_tp_csr_030(self):
        bad, n = _compare(self, "TP-CSR-030")
        self.check("fire_tp_csr_030", n > 0 and not bad,
                   _detail(n, bad, f"mie read-backs after csrrw/csrrs -1 (expect MIE_MASK 0x{prog.MIE_MASK:08x}) and csrrc -1 / csrrw x0 (expect 0)"))

    def fire_tp_csr_035(self):
        bad, n = _compare(self, "TP-CSR-035")
        f = _plan(self.seed).facts["TP-CSR-035"]
        self.check("fire_tp_csr_035", n > 0 and not bad and len(f["copies"]) > 1,
                   _detail(n, bad, "mtvec read-backs (BASE | 1) and ecall landings (handler copy marker at BASE, mcause 11)")
                   + f"; handler copies used {sorted(f['copies'])} of {prog.NUM_HANDLER_COPIES}, ops {sorted(f['ops'])}")

    def fire_tp_csr_036(self):
        bad, n = _compare(self, "TP-CSR-036")
        self.check("fire_tp_csr_036", n > 0 and not bad,
                   _detail(n, bad, "mtvec read-backs vs (w & 0xFFFFFF00) | 1 for MODE 00/01/10/11 x bits 7:2 zero/nonzero and the clear attempts"))

    def fire_program_integrity(self):
        """The program ran its straight-line path: no unexpected trap, the retirement floor reached, tohost 1."""
        bad, n = _compare(self, prog.PROGRAM_ITEM)
        floor = lib.program_min_retired(self.image)
        got = self.retired()
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_program_integrity", n > 0 and not bad and got >= floor and code == lib.TOHOST_PASS,
                   _detail(n, bad, "program words (unexpected-trap count, last unexpected mcause; expect 0, 0)")
                   + f"; retired {got} (floor {floor}); tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS})")


@cocotb.test()
async def gen_test_csr_trap_setup(dut):
    await CsrTrapSetup(dut).run()
