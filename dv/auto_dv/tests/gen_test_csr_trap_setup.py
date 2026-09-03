"""gen_test_csr_trap_setup: test-plan group gen_csr_trap_setup (gen_test_plan.md Section 4.2), the trap-setup
CSRs mstatus, mie, mtvec and the read-as-zero mstatush / menvcfg / menvcfgh.

Items built (one fire-check each): TP-CSR-023 (mstatus random write/read-back against the WARL prediction,
fire_tp_csr_023), TP-CSR-024 (MPP 01/10 legalise to U and the following mret enters U-mode, observed as the
ecall cause 8 vs 11 the handler reports; pass (doc mismatch D2), fire_tp_csr_024), TP-CSR-025 (mstatus
all-ones reads back 0x0022_1888, clear reads 0, fire_tp_csr_025), TP-CSR-027 (mstatush reads 0, writes
ignored, no trap, fire_tp_csr_027), TP-CSR-028 (menvcfg/menvcfgh idem, fire_tp_csr_028), TP-CSR-029 (mie
random write/read-back under MIE_MASK, fire_tp_csr_029; its irq_pending_o clause needs the pin channel and
is not asserted), TP-CSR-030 (mie all-ones reads back MIE_MASK, fire_tp_csr_030), TP-CSR-035 (mtvec
read-back == BASE | 1 for every base class the plan names, low / high / boot, and the following ecall lands in
the installed handler copy, observed as that copy's marker word; fire_tp_csr_035), TP-CSR-036 (mtvec MODE /
bits 7:2 legalised on write, fire_tp_csr_036).
Clauses dropped inside the built items, each with the missing component: TP-CSR-035 interrupt vectoring
(BASE + 4 * id) and the low_irq_sw / high_irq_fast bins need an irq agent; TP-CSR-035 ecall landing on the
boot base needs memory at the boot page's first 0x80 bytes, which gen_link.ld does not map (the boot class is
exercised as write and read-back, then a handler copy is installed before the ecall); the low base is the
program's .debug_rom copy in the DM window, the only memory below bit 31 in the TB map; TP-CSR-035's
rvfi_pc_rdata clause is observed through the handler copy's marker word (the program report channel), not
RVFI. TP-CSR-026 (interrupt taken on MIE set) and TP-CSR-031 (irq_pending_o / WFI wake timing) form the plan group
gen_csr_trap_setup_irq, hosted by an interrupt-enabled test; every item of this test's group is built here.
Canonical features covered (gen_feature_list.md Section 3): F-CSR-023 (carries the folded F-CSR-025 and
F-PRV-035), F-CSR-024, F-CSR-027, F-CSR-028, F-CSR-029 (carries the folded F-CSR-030), F-CSR-035 (carries
the folded F-CSR-036); not covered here: F-CSR-026, F-CSR-031.

Program: dv/auto_dv/tests/gen_programs/gen_csr_trap_setup_prog.py, a per-seed generator (testlist
`program: {generator: ..., seed: run}`); plan(seed) is the single source of the expected report words,
report_count() returns its k, and the fire-checks compare self.reports with it (link-address expectations
are resolved from the image sidecar). Red fixtures: `--red --red-item TP-CSR-0nn` deviates the program on that
item's intent (the seed draws the item without --red-item); exactly that fire_tp method fails. Knobs:
knob_imem_gnt_delay and knob_imem_rvalid_delay (the fetch-latency regimes the built items name); the irq knobs
the items also name (irq_regime, irq_line_mix, irq_hold) are excluded because the program has no interrupt
handler and the build has no irq agent (they belong to the blocked clauses).
declare_bins() takes the template default (the plan's bins of the items the fire_tp methods name, checked
against the rendered manifest in finish()).
Checkers relied on besides the fire-checks: the always-on ISA comparator rows (isa_pc, isa_insn, isa_trap,
isa_rd, isa_mem, isa_prv, isa_pc_next, isa_csr), rvfi_proto and the bus protocol checkers. T-102 (comparator
mret target and privilege rows, the shim's mstatus XS mask) is TB Infra's: the flow verdict FAILs through
uvm_error on this program until it lands, and no program clause is bent around it.
MODULE=dv.auto_dv.tests.gen_test_csr_trap_setup, TOPLEVEL=gen_tb_top.

Precondition not applied: irq agent absent; TP-CSR-023's pending-disabled-irq case and TP-CSR-029's irq-pins-high case are not programmed (register clauses only, GEN_TEST_INFO carries the label). Their irq bins are excluded from the manifest (bins_not_hit).
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
    # bins of built items this test cannot hit (irq precondition not applied); excluded from the manifest with the reason
    bins_not_hit = {
        "gen_prv_trap_vector_cg.cp_cause.irq_fast": "irq agent absent: no interrupt is taken in this test",
        "gen_prv_trap_vector_cg.cp_cause.irq_sw": "irq agent absent: no interrupt is taken in this test",
        "gen_prv_trap_vector_cg.cr_base_cause.high_irq_fast": "irq agent absent: no interrupt is taken in this test",
        "gen_prv_trap_vector_cg.cr_base_cause.low_irq_sw": "irq agent absent: no interrupt is taken in this test",
    }
    # every item of the plan group is built (two-sided against the group by the structure check)
    not_built = {}

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
        self.info("TP-CSR-023", "precondition not applied: irq agent absent (step 2b); the pending-disabled-irq case is not programmed")

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
        self.info("TP-CSR-029", "precondition not applied: irq agent absent (step 2b); the irq-pins-high case is not programmed")

    def fire_tp_csr_030(self):
        bad, n = _compare(self, "TP-CSR-030")
        self.check("fire_tp_csr_030", n > 0 and not bad,
                   _detail(n, bad, f"mie read-backs after csrrw/csrrs -1 (expect MIE_MASK 0x{prog.MIE_MASK:08x}) and csrrc -1 / csrrw x0 (expect 0)"))

    def fire_tp_csr_035(self):
        bad, n = _compare(self, "TP-CSR-035")
        f = _plan(self.seed).facts["TP-CSR-035"]
        bases = f["bases"] == set(prog.BASE_CLASSES) and prog.LOW_COPY in f["copies"] and len(f["copies"] & set(prog.HIGH_COPIES)) > 1
        self.check("fire_tp_csr_035", n > 0 and not bad and bases,
                   _detail(n, bad, "mtvec read-backs (BASE | 1) and ecall landings (handler copy marker at BASE, mcause 11)")
                   + f"; base classes {sorted(f['bases'])} of {list(prog.BASE_CLASSES)}, handler copies used {sorted(f['copies'])}"
                   + f" of {prog.NUM_HANDLER_COPIES}, ops {sorted(f['ops'])}")

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
