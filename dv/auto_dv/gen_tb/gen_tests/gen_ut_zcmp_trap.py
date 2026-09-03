"""Trapping Zcmp sequence (T-102c): arm one bus error on the program's stack window (MEM_ERR_ARM) before the core is
released, so the first cm.push store takes a store access fault on a Zcmp micro-op record. The export's records show the
trap record and the RVFI convention on it: pc_wdata == pc_rdata, the aborted Zcmp sequence restarts from its first
micro-op (observed on the first red run, T-102c; the C-1 'next sequential address' is the instruction's own pc here, not
pc + 2 and not pc + 4), and the lock-step comparator must agree (zero mismatches).
Program: dv/auto_dv/stim/gen_directed/gen_zcmp_trap_directed.S. Plusargs as gen_ut_lockstep plus +gen_export_file.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_zcmp_trap, TOPLEVEL=gen_tb_top."""
import os

import cocotb

from dv.auto_dv.gen_tb import gen_export
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_image import GenImage
from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, PLUSARGS

PASS_MARKER = "GEN_UT_ZCMP_TRAP_PASS"
ARM_BUS_ERR = CONSTANTS["GEN_MEM_ERR_ARM_KIND_ERR"]   # MEM_ERR_ARM arg3[7:0]
PUSH_BYTES = 16          # cm.push {ra, s0-s2}, spimm 0: four words below the stack top


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_zcmp_trap(dut):
    log = dut._log
    h = GenHandles(dut)
    b = GenBridge(h, log)
    img = GenImage(plus("mem_image"))
    seed = int(os.environ.get("RANDOM_SEED", "1"))
    export_path = plus("export_file")
    assert export_path, "GEN_UT_ZCMP_TRAP: +gen_export_file is required (the trap record is read from the export)"
    assert plus("fetch_en_at_reset") == "0", "GEN_UT_ZCMP_TRAP: run with +gen_fetch_en_at_reset=0"
    stack_top = int(img.sidecar["symbols"]["gen_stack_top"], 16)
    await b.start()
    for idx, word in img.sample(8, seed):
        assert await b.cmd("MEM_PEEK", (idx * 4, 0, 0, 0)) == word, "GEN_UT_ZCMP_TRAP: read-back mismatch"
    # one bus error on the first access inside the cm.push window (dbus = 1; count 1 in arg3[31:8])
    await b.cmd("MEM_ERR_ARM", (1, stack_top - PUSH_BYTES, stack_top - 4, ARM_BUS_ERR | (1 << 8)))
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=60000)
    seq = await b.export_flush()
    e = gen_export.read(export_path, seq)
    traps = [r for r in e.records if r.trap]
    zc_traps = [r for r in traps if r.ext_exp_valid]
    log.info("GEN_UT_ZCMP_TRAP records %d traps %d on Zcmp micro-ops %d", len(e.records), len(traps), len(zc_traps))
    assert zc_traps, f"GEN_UT_ZCMP_TRAP: no trap on a Zcmp micro-op record ({len(traps)} trap records)"
    for r in zc_traps:
        assert r.pc_wdata == r.pc_rdata, f"GEN_UT_ZCMP_TRAP: Zcmp trap record order {r.order} pc {r.pc_rdata:08x}: pc_wdata {r.pc_wdata:08x} != pc (the aborted sequence restarts)"
    mism = int(h.b.evt_isa_mismatch.value)
    assert mism == 0, f"GEN_UT_ZCMP_TRAP: {mism} ISA mismatches (the comparator disagrees with the record set)"
    await b.finish(timeout_cycles=5000)
    log.info(PASS_MARKER)
