"""Red witness fixture: the entry allows TP-CMP-036 and the table has it, but the rendered owner table says another group
owns it (gen_cmp_zcmp_events); finish() must FAIL with "witness for TP-CMP-036 owned by gen_cmp_zcmp_events, issued by
gen_cmp_zcb" before the handshake and issue nothing (the host refuses before the dispatcher's GEN_WITNESS_FOREIGN would)."""
import cocotb

from gen_ut_witness_base import install_manifest, FAKE_CODE, WitnessBase, patch

patch(("TP-CMP-036",), {"TP-CMP-036": FAKE_CODE}, owner_of={"TP-CMP-036": "gen_cmp_zcmp_events"})

install_manifest("gen_ut_witness_othergroup")


class WitnessOtherGroup(WitnessBase):
    name = "gen_ut_witness_othergroup"


@cocotb.test()
async def gen_ut_witness_othergroup(dut):
    await WitnessOtherGroup(dut).run()
    assert WitnessOtherGroup.issued is None, f"GEN_UT: witnesses issued {WitnessOtherGroup.issued}, expected none"
