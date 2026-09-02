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
    yield Timer(1, units="ns")

    # Set cocotb_active to signal stimulus is running.
    cocotb_if.cocotb_active.value = 1

    cocotb.log.info(f"COCOTB-HELLO: alive (seed={seed})")


async def finish(dut):
    """Clear active flag, then poll uvm_finished (1us period, 2ms timeout)."""
    cocotb_if = dut.cocotb_if
    cocotb_if.cocotb_active.value = 0

    # Poll uvm_finished within a 2ms timeout.
    timeout_cycles = 2000  # 2ms / 1us
    for cycle in range(timeout_cycles):
        if cocotb_if.uvm_finished.value:
            return
        yield Timer(1, units="us")

    raise TimeoutError(
        f"uvm_finished did not assert within 2ms timeout (polled {timeout_cycles} times)"
    )
