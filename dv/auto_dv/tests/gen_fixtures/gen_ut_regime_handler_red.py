"""Red fixture of the regime-handler rule at run time (never a testlist entry; a fixture, so the structural check does not see
it): gen_test_cmp_zcb's test scheduling knob_debug_req_regime with no debug handler declared; setup() must FAIL with
"GEN_TEST_FAIL ...: schedules a regime knob its program cannot survive: knob_debug_req_regime (consumer dbg) needs a dbg
handler" before the first fetch. Program: the gen_cmp_zcb seed-1 image."""
import cocotb

from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb


class RegimeHandlerRed(CmpZcb):
    name = "gen_ut_regime_handler_red"
    schedulable = ("knob_imem_gnt_delay", "knob_debug_req_regime")


@cocotb.test()
async def gen_ut_regime_handler_red(dut):
    await RegimeHandlerRed(dut).run()
