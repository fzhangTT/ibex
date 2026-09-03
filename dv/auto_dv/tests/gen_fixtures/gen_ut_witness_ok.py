"""Green witness fixture: TP-CMP-036 allowed by the entry, code 7 in the table, command present; the epilogue must issue
exactly one COV_WITNESS 7 (GEN_TEST_WITNESS id=TP-CMP-036 code=7) and the run PASSes."""
import cocotb

from gen_ut_witness_base import install_manifest, FAKE_CODE, WitnessBase, patch

patch(("TP-CMP-036",), {"TP-CMP-036": FAKE_CODE})

install_manifest("gen_ut_witness_ok")


class WitnessOk(WitnessBase):
    name = "gen_ut_witness_ok"


@cocotb.test()
async def gen_ut_witness_ok(dut):
    await WitnessOk(dut).run()
    assert WitnessOk.issued == [FAKE_CODE], f"GEN_UT: witness codes issued {WitnessOk.issued}, expected [{FAKE_CODE}]"
