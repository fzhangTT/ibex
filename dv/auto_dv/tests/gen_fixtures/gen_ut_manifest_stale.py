"""Red fixture (never a testlist entry): a rendered manifest that lags the plan by one bin must FAIL in finish()
with "differs from declare_bins()". The fixture's manifest home is this directory (gen_ut_manifest_stale.fcov.yaml,
the gen_cmp_zcb manifest minus its last bin); the program is the gen_cmp_zcb seed-1 program."""
from pathlib import Path

import cocotb

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb

lib.FCOV_HOME = Path(__file__).resolve().parent   # fixture manifests live beside the fixture, never under fcov_expectations


class ManifestStale(CmpZcb):
    name = "gen_ut_manifest_stale"


@cocotb.test()
async def gen_ut_manifest_stale(dut):
    await ManifestStale(dut).run()
