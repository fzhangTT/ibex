"""gen_test_boot_retire: the boots-and-retires scenario as a real test and the proof of the template.

Program: the riscv-dv entry gen_rand_smoke at the run seed (testlist `program: {riscv_dv_test:
gen_rand_smoke, seed: run}`), or a directed program for the red run. Layers: the timing-only regime
knobs (bus latencies, outstanding cap, scramble-key delay) are drawn and scheduled by the template
when the build has a REGIME_SET consumer (gen_test_lib.CONSUMED_KNOBS is empty at HEAD, where step 2b
is parked, so none of the six TIMING_ONLY_KNOBS is drawn and the run logs GEN_TEST_LAYERS not_applied); error-injection
and event knobs stay at their yaml defaults because this program carries no expectation for them
(later groups own those). Fire-check per seed: (1) the end-of-test store carries
code 1 (the program's own pass verdict); (2) the retirement count after that store is at least the
program's retirement floor (riscv-dv +instr_cnt of the entry, or the directed program's
gen_min_retired word; the riscv-dv floor is a heuristic lower bound, generated programs branch and
retire more, observed 470-550 for instr_cnt 300); (3) every scheduled regime phase whose trigger was
reached was applied (template). Checkers relied on: the always-on TB checks (ISA comparator, rvfi_proto, bus protocol).
Group: none (template proof; testlist tier check, measured: false until the plan's smoke groups
take it over). MODULE=dv.auto_dv.tests.gen_test_boot_retire, TOPLEVEL=gen_tb_top.
"""
import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_template import GenTest



class BootRetire(GenTest):
    name = "gen_test_boot_retire"
    schedulable = lib.TIMING_ONLY_KNOBS
    # Bring-up test (tier check, measured false): it may run with the layers off while the build has no
    # REGIME_SET consumer; flips to the default (required) when TB Infra's step 2b lands.
    layers_required = False

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == lib.TOHOST_PASS, f"tohost code 0x{code:08x} (pass = {lib.TOHOST_PASS})")
        floor = lib.program_min_retired(self.image)
        got = self.retired()
        self.check("fire_retired_floor", got >= floor, f"retired {got} (floor {floor} from the program)")


@cocotb.test()
async def gen_test_boot_retire(dut):
    await BootRetire(dut).run()
