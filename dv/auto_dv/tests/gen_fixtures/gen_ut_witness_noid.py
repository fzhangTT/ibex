"""Red witness fixture: table and command rendered, the entry allows TP-CMP-036, but the table lacks that id; finish()
must FAIL with the GEN_TEST_FAIL prefix ("the rendered WITNESS_IDS table lacks TP-CMP-036"), never a bare KeyError."""
import cocotb

from gen_ut_witness_base import install_manifest, FAKE_CODE, WitnessBase, patch

patch(("TP-CMP-036",), {"TP-CMP-999": FAKE_CODE})

install_manifest("gen_ut_witness_noid")


class WitnessNoId(WitnessBase):
    name = "gen_ut_witness_noid"


@cocotb.test()
async def gen_ut_witness_noid(dut):
    await WitnessNoId(dut).run()
