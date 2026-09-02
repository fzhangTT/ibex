"""Handshake protocol with the SV TB: cctb_alive, cocotb_active, uvm_finished."""

import os
import cocotb
from cocotb.triggers import Timer


async def start(dut):
    """Signal cocotb process is alive and active; log the RANDOM_SEED."""
    cocotb_if = dut.cocotb_if
    seed = os.environ.get("RANDOM_SEED", "0")

    # Set cctb_alive first (100ns watchdog is waiting).
    cocotb_if.cctb_alive.value = 1
    await Timer(1, units="ns")

    # Set cocotb_active to signal stimulus is running.
    cocotb_if.cocotb_active.value = 1
    # Yield so the write actually commits before any caller-side code (e.g. a test with no
    # further awaits before finish()) can clear it back to 0 in the same write batch — otherwise
    # cocotb coalesces the two writes and the SV monitor's `wait (cocotb_active == 1)` never fires.
    await Timer(1, units="ns")

    cocotb.log.info(f"COCOTB-HELLO: alive (seed={seed})")


async def finish(dut, timeout_ms=2):
    """Clear active flag, then poll uvm_finished (1us period, timeout_ms timeout).

    Default preserves Milestone A's hello-world budget; heavier programs (e.g. a full
    +instr_cnt=10000 random-instruction test plus irq handling) need a caller-supplied budget
    covering how long that program actually takes to reach its own riscv-dv signature handshake.
    """
    cocotb_if = dut.cocotb_if
    cocotb_if.cocotb_active.value = 0

    timeout_cycles = timeout_ms * 1000  # timeout_ms / 1us
    for cycle in range(timeout_cycles):
        if cocotb_if.uvm_finished.value:
            return
        await Timer(1, units="us")

    raise TimeoutError(
        f"uvm_finished did not assert within {timeout_ms}ms timeout (polled {timeout_cycles} times)"
    )
