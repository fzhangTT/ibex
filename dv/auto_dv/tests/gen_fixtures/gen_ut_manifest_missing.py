"""Red fixture (never a testlist entry): a test whose group has plan bins but no rendered manifest must FAIL in
finish() with "declares N bins but has no manifest". Runs the gen_cmp_zcb test (its fire_tp_cmp_* items) under another name with the seed-1 program."""
import cocotb

from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb


class ManifestMissing(CmpZcb):
    name = "gen_ut_manifest_missing"   # no dv/auto_dv/fcov_expectations/<name>.fcov.yaml exists


@cocotb.test()
async def gen_ut_manifest_missing(dut):
    await ManifestMissing(dut).run()
