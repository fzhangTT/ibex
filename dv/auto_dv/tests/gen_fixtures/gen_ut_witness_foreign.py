"""Red witness fixture: the entry allows TP-CMP-034 only, the fire-check claims TP-CMP-036; finish() must FAIL with
"witness for ['TP-CMP-036'] outside the entry's witness_ids" before the handshake and issue nothing."""
import cocotb

from gen_ut_witness_base import install_manifest, FAKE_CODE, WitnessBase, patch

patch(("TP-CMP-034",), {"TP-CMP-034": FAKE_CODE, "TP-CMP-036": FAKE_CODE + 1})

install_manifest("gen_ut_witness_foreign")


class WitnessForeign(WitnessBase):
    name = "gen_ut_witness_foreign"


@cocotb.test()
async def gen_ut_witness_foreign(dut):
    await WitnessForeign(dut).run()
