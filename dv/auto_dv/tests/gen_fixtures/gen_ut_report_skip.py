"""Red fixture for wait_eot's skip detection (Critic v2 N-2): the observer is faulted (eot_count() reports one store too
many once, after the first report edge), standing in for a missed edge, so the template must FAIL with
"report channel skipped a store". Program: gen_report_channel.S (three report words, then tohost 1); the fault is in
the fixture, never in the template or the program. MODULE=gen_ut_report_skip, TOPLEVEL=gen_tb_top."""
import cocotb

from gen_ut_report_channel import ReportChannel


class ReportSkip(ReportChannel):
    name = "gen_ut_report_skip"
    _fault_armed = True

    def eot_count(self):
        n = super().eot_count()
        if n >= 1 and self._fault_armed:
            self._fault_armed = False
            return n + 1
        return n


@cocotb.test()
async def gen_ut_report_skip(dut):
    await ReportSkip(dut).run()
