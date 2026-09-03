"""Shared base of the witness-epilogue fixtures (never testlist entries): gen_test_cmp_zcb's test with one fire-check
claiming a TRUE cycle clause, the bridge's cov_witness replaced by a recorder (the SV dispatcher routes COV_WITNESS to the
witness covergroup since landing 2b; the fixtures' fake codes must never reach its table), and the library tables patched
per fixture (WITNESS_IDS, WITNESS_GROUP_OF, WITNESS_GROUPS, the test's group, CMD, the entry's witness_ids). Program: the
gen_cmp_zcb seed-1 image."""
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


GROUP = "gen_cmp_zcb"          # the fixtures host gen_cmp_zcb's items, so that is their own group


def patch(witness_ids, table, command=True, owner_of=None):
    """Install the fixture's view of the rendered protocol: entry witness_ids, WITNESS_IDS table, the owner group of every
    id (GROUP unless owner_of says otherwise), the group index table, the test's own group, COV_WITNESS command."""
    lib.witness_ids_of = lambda name: tuple(witness_ids)
    lib.WITNESS_IDS = dict(table)
    lib.WITNESS_GROUP_OF = dict(owner_of) if owner_of is not None else {tp: GROUP for tp in table}
    lib.WITNESS_GROUPS = {g: i for i, g in enumerate(sorted({GROUP} | set(lib.WITNESS_GROUP_OF.values())))}
    lib.test_group = lambda name: GROUP
    lib.CMD = {k: v for k, v in lib.CMD.items() if k != "COV_WITNESS"}
    if command:
        lib.CMD["COV_WITNESS"] = max(lib.CMD.values()) + 1


class WitnessBase(CmpZcb):
    """fire_tp_cmp_036 additionally records a TRUE cycle clause (proxy: the report words exist), so the epilogue owes
    one witness for TP-CMP-036."""
    issued = None

    def __init__(self, dut):
        super().__init__(dut)
        self.bridge.cov_witness = self.record_witness

    async def record_witness(self, tp_item, owner_group, timeout_cycles=200):
        type(self).issued = (type(self).issued or []) + [(tp_item, owner_group)]
        self.log.info("GEN_UT_FAKE_DISPATCH COV_WITNESS %s %s recorded", tp_item, owner_group)
        return 0

    def fire_tp_cmp_036(self):
        super().fire_tp_cmp_036()
        self.check("fire_tp_cmp_036_clause", len(self.reports) > 0, "cycle clause proxy TRUE", cycle_clause_true=True)

