"""FCOV_SELFTEST / FCOV_QUERY (LOG-058): after the program has retired the requested count, the sampler's classifier vector table
must report 0 failures, and, when +gen_ut_fcov_query / +gen_ut_fcov_expect name a counter and a value, the counter must equal the
value the program is known to produce (gen_alu_directed.S: slt eq 84; gen_zcmp_directed.S: minstret_once misses 0 over 290 sequences;
gen_bitcnt_directed.S: the rd = x0 bit-count records). Plusargs as gen_ut_boot plus the two above.
MODULE=dv.auto_dv.gen_tb.gen_tests.gen_ut_isa_cov, TOPLEVEL=gen_tb_top."""
import cocotb
from dv.auto_dv.gen_tb.gen_bridge import GenBridge
from dv.auto_dv.gen_tb.gen_handles import GenHandles
from dv.auto_dv.gen_tb.gen_knobs import PLUSARGS
PASS_MARKER = "GEN_UT_ISA_COV_PASS"
COUNTERS = {0: "slt eq", 1: "zcmp sequences", 2: "minstret_once misses", 3: "bit-count records", 4: "bit-count rd = x0 records", 5: "alu_imm records",
            6: "uop_count misses", 7: "order misses", 8: "tags misses", 9: "branches", 10: "move pairs", 11: "csr pairs"}


def plus(name, default=None):
    return cocotb.plusargs.get(PLUSARGS[name]["plusarg"], default)


@cocotb.test()
async def gen_ut_isa_cov(dut):
    log = dut._log
    b = GenBridge(GenHandles(dut), log)
    await b.start()
    await b.cmd("FETCH_EN", (1, 0, 0, 0))
    await b.wait_retired_until(int(plus("ut_boot_retire", PLUSARGS["ut_boot_retire"]["default"])), timeout_cycles=400000)
    q = int(plus("ut_fcov_query", PLUSARGS["ut_fcov_query"]["default"]))
    if q >= 0:
        e = int(plus("ut_fcov_expect", PLUSARGS["ut_fcov_expect"]["default"]))
        got = await b.fcov_query(q)
        assert got == e, f"GEN_UT_ISA_COV: counter {q} ({COUNTERS.get(q, '?')}) is {got}, the program's known count is {e}"
        log.info("GEN_UT_ISA_COV: counter %d (%s) = %d as the program predicts", q, COUNTERS.get(q, "?"), got)
    fails = await b.fcov_selftest()
    assert fails == 0, f"GEN_UT_ISA_COV: the classifier vector table reports {fails} failure(s) (GEN_FCOV_UT lines name them)"
    log.info("GEN_UT_ISA_COV: classifier vector table 0 failures")
    await b.finish()
    log.info(PASS_MARKER)
