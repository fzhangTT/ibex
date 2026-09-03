"""Red fixture (never a testlist entry): a test whose group has plan bins but no rendered manifest must FAIL in
finish() with "declares N bins but has no manifest". Runs the gen_cmp_zcb seed-1 program under another name."""
import cocotb

from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb


class ManifestMissing(CmpZcb):
    name = "gen_ut_manifest_missing"   # no dv/auto_dv/fcov_expectations/<name>.fcov.yaml exists
    plan_group = "gen_cmp_zcb"


@cocotb.test()
async def gen_ut_manifest_missing(dut):
    await ManifestMissing(dut).run()
