"""Shared base of the witness-epilogue fixtures (never testlist entries): gen_test_cmp_zcb's test with one fire-check
claiming a TRUE cycle clause, a fake dispatcher that records COV_WITNESS instead of sending it (no SV side exists), and
the library tables patched per fixture (WITNESS_IDS, CMD, the entry's witness_ids). Program: the gen_cmp_zcb seed-1 image."""
from pathlib import Path

import yaml

from dv.auto_dv.tests import gen_test_lib as lib
from dv.auto_dv.tests.gen_test_cmp_zcb import CmpZcb

FAKE_CODE = 7
SOURCE_MANIFEST = Path(__file__).resolve().parents[1].parent / "fcov_expectations" / "gen_test_cmp_zcb.fcov.yaml"
FIXTURE_HOME = Path.cwd() / "fixture_manifests"   # the run directory: derived manifests never land in the repository


def install_manifest(name, drop_last=False):
    """A fixture named `name` inherits gen_test_cmp_zcb's fire_tp items, so it needs that manifest under its own name;
    derived at import from the current committed file into the run directory (drop_last: minus its last bin, the stale
    case). Returns the dropped bin or None."""
    d = yaml.safe_load(SOURCE_MANIFEST.read_text())
    d["test"] = name
    dropped = None
    if drop_last:
        dropped = d["bins"].pop()
        d["anti_vacuity"].pop(dropped, None)
    FIXTURE_HOME.mkdir(parents=True, exist_ok=True)
    (FIXTURE_HOME / f"{name}.fcov.yaml").write_text(yaml.safe_dump(d, sort_keys=False))
    lib.FCOV_HOME = FIXTURE_HOME
    return dropped


def patch(witness_ids, table, command=True):
    """Install the fixture's view of the rendered protocol: entry witness_ids, WITNESS_IDS table, COV_WITNESS command."""
    lib.witness_ids_of = lambda name: tuple(witness_ids)
    lib.WITNESS_IDS = dict(table)
    lib.CMD = {k: v for k, v in lib.CMD.items() if k != "COV_WITNESS"}
    if command:
        lib.CMD["COV_WITNESS"] = max(lib.CMD.values()) + 1


class WitnessBase(CmpZcb):
    """fire_tp_cmp_036 additionally records a TRUE cycle clause (proxy: the report words exist), so the epilogue owes
    one witness for TP-CMP-036."""
    issued = None

    def fire_tp_cmp_036(self):
        super().fire_tp_cmp_036()
        self.check("fire_tp_cmp_036_clause", len(self.reports) > 0, "cycle clause proxy TRUE", cycle_clause_true=True)

    async def cmd(self, kind, args=(0, 0, 0, 0), timeout_cycles=200):
        if kind == "COV_WITNESS":
            type(self).issued = (type(self).issued or []) + [args[0]]
            self.log.info("GEN_UT_FAKE_DISPATCH COV_WITNESS code=%d recorded", args[0])
            return 0
        return await super().cmd(kind, args, timeout_cycles)
