"""WS2 Milestone B: python-driven irq stimulus through the UVM irq agent.

cocotb owns all irq timing for this test (see testlist.yaml's cocotb_irq_python_test entry): it
triggers a global uvm_event via uvm_bridge, which an armed SV listener (core_ibex_base_test.sv)
turns into a raise-then-drop pulse driven through the real irq agent/sequencer.
"""

import os
import random

import cocotb
from cocotb.triggers import ClockCycles

from dv.cocotb.common import uvm_bridge
from dv.cocotb.common.handshake import start, finish

# Fixed independently of the +cocotb_irq_count plusarg below so the checker's own effectiveness
# can be validated by an ablation negative control (send fewer triggers without also lowering what
# the test demands) — see WS2 Milestone B report, Step 4.
_MIN_EXPECTED_HANDLER_ENTRIES = 3

# Cycles to wait before the first trigger and between subsequent ones (plus seeded jitter below):
# generously longer than a +enable_interrupt=1 program's early mstatus/mie setup and a minimal
# ISR's completion, so a trigger never races a not-yet-enabled core or a still-running handler.
_BASE_GAP_CYCLES = 3000
_JITTER_MAX_CYCLES = 2000

# Cycles to wait after the last trigger before checking handler_entry_count: covers the raise/drop
# hold (core_ibex_base_test.sv's CocotbIrqHoldCycles) plus margin for the core to reach IRQ_TAKEN.
_POST_TRIGGER_SETTLE_CYCLES = 500


@cocotb.test()
async def test_irq_from_python(dut):
    """Trigger N cocotb-driven irq pulses through the UVM irq agent; check handler entries."""
    await start(dut)

    seed = int(os.environ.get("RANDOM_SEED", "0"))
    rng = random.Random(seed)
    n = int(cocotb.plusargs.get("cocotb_irq_count", "3"))
    cocotb.log.info(f"COCOTB-IRQ: cocotb_irq_count={n} (seed={seed})")

    cocotb_if = dut.cocotb_if
    # uvm_ready means the SV listener has already armed its event handle, so no trigger from here
    # on can be lost (see core_ibex_cocotb_if.sv).
    while not cocotb_if.uvm_ready.value:
        await ClockCycles(dut.clk, 1)
    cocotb.log.info("COCOTB-IRQ: uvm_ready observed")

    for i in range(n):
        gap = _BASE_GAP_CYCLES + rng.randrange(0, _JITTER_MAX_CYCLES + 1)
        await ClockCycles(dut.clk, gap)
        cocotb.log.info(f"COCOTB-IRQ: triggering cocotb_irq_raise ({i + 1}/{n}), gap={gap}")
        uvm_bridge.trigger("cocotb_irq_raise")

    await ClockCycles(dut.clk, _POST_TRIGGER_SETTLE_CYCLES)

    # Checked here, before finish(), rather than after: the flow's log scanner
    # (ibex_log_to_trace_csv.check_ibex_uvm_log) stops treating "Error" lines as failures once it
    # has seen "RISC-V UVM TEST PASSED" in the log, to avoid false positives from the UVM report
    # summary. That banner only prints once this test's whole generated program reaches its own
    # riscv-dv signature handshake at natural completion, which happens well after our own irq
    # activity here — asserting after finish() would land past that point and be silently ignored
    # by the scanner even on a real failure. Checked here instead, it always lands well before that
    # banner, so a failure is never in the scanner's ignored window; on a real assertion failure,
    # cocotb's own uncaught-exception handling $finishes immediately, so the banner never prints at
    # all in that case, and the checker's own effectiveness is what Step 4's negative control below
    # is proving.
    count = int(cocotb_if.handler_entry_count.value)
    cocotb.log.info(
        f"COCOTB-IRQ: handler_entry_count={count} "
        f"(triggered={n}, required>={_MIN_EXPECTED_HANDLER_ENTRIES})"
    )
    # Plain ASCII only: cocotb's own failure-logging path uses an ASCII-only stream encoder here,
    # and a non-ASCII character in this message crashes that log call, which swallows the failure
    # text and leaves the flow's log-scan classifier with nothing to catch (silent false PASS).
    assert count >= _MIN_EXPECTED_HANDLER_ENTRIES, (
        f"COCOTB-IRQ-CHECK: handler_entry_count={count} is below the required "
        f"{_MIN_EXPECTED_HANDLER_ENTRIES} (triggered {n} times); irq stimulus was not serviced"
    )

    # This test's generated program (+instr_cnt=10000, plus 3 irq round-trips) takes noticeably
    # longer to reach its own riscv-dv signature handshake than Milestone A's bare hello-world
    # program did, hence the wider budget than handshake.finish()'s 2ms default.
    await finish(dut, timeout_ms=30)
