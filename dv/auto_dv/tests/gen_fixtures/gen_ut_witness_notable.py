"""Red witness fixture: the entry allows TP-CMP-036 but no WITNESS_IDS table and no COV_WITNESS command are rendered;
finish() must FAIL with "witness protocol not rendered" and issue nothing."""
import cocotb

from gen_ut_witness_base import install_manifest, WitnessBase, patch

patch(("TP-CMP-036",), {}, command=False)

install_manifest("gen_ut_witness_notable")


class WitnessNoTable(WitnessBase):
    name = "gen_ut_witness_notable"


@cocotb.test()
async def gen_ut_witness_notable(dut):
    await WitnessNoTable(dut).run()
