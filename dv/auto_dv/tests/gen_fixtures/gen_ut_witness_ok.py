"""Green witness fixture: TP-CMP-036 allowed by the entry, code 7 in the table, owned by the test's own group, command
present; the epilogue must issue exactly one cov_witness(TP-CMP-036, gen_cmp_zcb) (GEN_TEST_WITNESS id=TP-CMP-036 code=7
group=gen_cmp_zcb) and the run PASSes."""
import cocotb

from gen_ut_witness_base import install_manifest, FAKE_CODE, WitnessBase, patch

patch(("TP-CMP-036",), {"TP-CMP-036": FAKE_CODE})

install_manifest("gen_ut_witness_ok")


class WitnessOk(WitnessBase):
    name = "gen_ut_witness_ok"


@cocotb.test()
async def gen_ut_witness_ok(dut):
    await WitnessOk(dut).run()
    assert WitnessOk.issued == [("TP-CMP-036", "gen_cmp_zcb")], f"GEN_UT: witnesses issued {WitnessOk.issued}, expected [(TP-CMP-036, gen_cmp_zcb)]"
