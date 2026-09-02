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
    # uvm_ready closes the startup race only (listener armed vs. the first trigger); it does not
    # mean a later trigger can never be dropped (see triggers_sent/triggers_received below).
    while not cocotb_if.uvm_ready.value:
        await ClockCycles(dut.clk, 1)
    cocotb.log.info("COCOTB-IRQ: uvm_ready observed")

    triggers_sent = 0
    for i in range(n):
        gap = _BASE_GAP_CYCLES + rng.randrange(0, _JITTER_MAX_CYCLES + 1)
        await ClockCycles(dut.clk, gap)
        cocotb.log.info(f"COCOTB-IRQ: triggering cocotb_irq_raise ({i + 1}/{n}), gap={gap}")
        uvm_bridge.trigger("cocotb_irq_raise")
        triggers_sent += 1

    await ClockCycles(dut.clk, _POST_TRIGGER_SETTLE_CYCLES)

    # Checked before finish(): the flow's log scanner ignores "Error" lines once it has seen
    # "RISC-V UVM TEST PASSED", which only prints after finish() would return (see report/Step 4).
    triggers_received = int(cocotb_if.trigger_received_count.value)
    cocotb.log.info(
        f"COCOTB-IRQ: triggers_sent={triggers_sent} triggers_received={triggers_received}"
    )
    # Plain ASCII only in every message below: cocotb's own failure-logging path uses an
    # ASCII-only stream encoder, and a non-ASCII character crashes that log call, which swallows
    # the failure text and leaves the flow's log-scan classifier with nothing to catch.
    assert triggers_sent == triggers_received, (
        f"COCOTB-IRQ-CHECK: triggers_sent={triggers_sent} != triggers_received={triggers_received}; "
        "a trigger was dropped (listener was still mid-pulse from a previous trigger)"
    )

    count = int(cocotb_if.handler_entry_count.value)
    # _MIN_EXPECTED_HANDLER_ENTRIES is a floor, not tied to n, so the +cocotb_irq_count=0 ablation
    # (Step 4) still fails; max(n, floor) tightens the check for n > floor instead of always
    # passing vacuously once n reaches 3.
    required = max(n, _MIN_EXPECTED_HANDLER_ENTRIES)
    cocotb.log.info(f"COCOTB-IRQ: handler_entry_count={count} (triggered={n}, required>={required})")
    if count > triggers_sent:
        cocotb.log.warning(
            f"COCOTB-IRQ-CHECK: handler_entry_count={count} exceeds triggers_sent={triggers_sent}; "
            "extra entries are not attributable to a specific python trigger"
        )
    assert count >= required, (
        f"COCOTB-IRQ-CHECK: handler_entry_count={count} is below the required "
        f"{required} (triggered {n} times); irq stimulus was not serviced"
    )

    # This test's generated program (+instr_cnt=10000, plus 3 irq round-trips) takes noticeably
    # longer to reach its own riscv-dv signature handshake than Milestone A's bare hello-world
    # program did, hence the wider budget than handshake.finish()'s 2ms default.
    await finish(dut, timeout_ms=30)
