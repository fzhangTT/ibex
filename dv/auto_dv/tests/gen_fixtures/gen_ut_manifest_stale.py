"""Red fixture (never a testlist entry): a rendered manifest that lags the plan by one bin must FAIL in finish() with
"differs from declare_bins()". The stale manifest is derived at import from the CURRENT committed gen_test_cmp_zcb
manifest minus its last bin, written into the run directory (never into the repository), so it cannot drift on a
re-render; the program is the gen_cmp_zcb seed-1 image."""
import cocotb

from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb
from gen_ut_witness_base import install_manifest

NAME = "gen_ut_manifest_stale"
DROPPED_BIN = install_manifest(NAME, drop_last=True)


class ManifestStale(CmpZcb):
    name = NAME


@cocotb.test()
async def gen_ut_manifest_stale(dut):
    await ManifestStale(dut).run()
