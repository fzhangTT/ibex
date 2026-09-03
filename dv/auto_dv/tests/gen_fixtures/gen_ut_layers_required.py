"""Red fixture for the layers_required guard (committed fixture, never a testlist entry): the test declares regime knobs it wants
layers 2/3 to vary while the build has no REGIME_SET consumer for them; with layers_required left at
its default (True) setup must FAIL loud instead of running the test green with the layers off.
MODULE=gen_ut_layers_required, TOPLEVEL=gen_tb_top."""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import KNOB_IDS
from dv.auto_dv.tests.gen_test_template import GenTest


class LayersRequired(GenTest):
    name = "gen_ut_layers_required"
    schedulable = tuple(n for n in KNOB_IDS if n.startswith("knob_imem_"))   # declared, not consumable at HEAD

    def fire_check(self):
        code = int(self.h.b.evt_eot_code.value)
        self.check("fire_eot_pass_code", code == 1, f"tohost code 0x{code:08x}")


@cocotb.test()
async def gen_ut_layers_required(dut):
    await LayersRequired(dut).run()
