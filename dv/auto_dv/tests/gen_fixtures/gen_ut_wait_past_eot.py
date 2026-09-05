"""Fixture for wait_cycles at the end of test (committed fixture, never a testlist entry): the stimulus waits for a
cycle far beyond the program's end and then for a settle window, the shape the irq entry's last-phase hold takes when a
schedule trigger falls past the program. Both waits must answer in the end-of-test cycle, not after their budgets: a
wait that sleeps its budget past the final store hands run() a stimulus that has not finished, and with the two budgets
equal the join loses (the wave's gen_test_irq_basic_1800473338; gen_tdd_test_template.md Section 18).
MODULE=gen_ut_wait_past_eot, TOPLEVEL=gen_tb_top; program gen_report_channel.S; budget lowered to keep the run short."""
import cocotb

from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS
from gen_ut_report_channel import ReportChannel

SETTLE_CYCLES = 64        # the irq entry's PHASE_SETTLE_CYCLES: the second wait a last-phase hold makes
EOT_ANSWER_SLACK = 8      # cycles a wait may answer after the final store (the slot service wakes on the same edge)


class WaitPastEot(ReportChannel):
    name = "gen_ut_wait_past_eot"
    program_budget_cycles = CONSTANTS["GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT"] // 20

    async def stimulus(self):
        far = self.cycle() + 20 * self.program_budget_cycles
        self.far_reached = await self.wait_cycles(far, timeout_cycles=self.program_budget_cycles)
        self.far_cycle = self.cycle()
        self.settle_reached = await self.wait_cycles(self.cycle() + SETTLE_CYCLES, timeout_cycles=self.program_budget_cycles)
        self.settle_cycle = self.cycle()

    def fire_check(self):
        super().fire_check()
        self.check("fire_far_not_reached", self.far_reached is False, f"a target past the program's end reads {self.far_reached}")
        self.check("fire_far_answered_at_eot", self.far_cycle <= self.eot_cycle + EOT_ANSWER_SLACK,
                   f"answered at cycle {self.far_cycle}, end of test at {self.eot_cycle}")
        self.check("fire_settle_not_reached", self.settle_reached is False, f"a settle window past the program's end reads {self.settle_reached}")
        self.check("fire_settle_answered_at_eot", self.settle_cycle <= self.eot_cycle + EOT_ANSWER_SLACK,
                   f"answered at cycle {self.settle_cycle}, end of test at {self.eot_cycle}")


@cocotb.test()
async def gen_ut_wait_past_eot(dut):
    await WaitPastEot(dut).run()
