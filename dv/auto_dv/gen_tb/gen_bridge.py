"""gen_bridge: the Python side of the cocotb-to-UVM bridge (architecture C2). Every wait is an edge
trigger on a single-bit SV field with a caller-sized timeout; nothing here polls a counter (A-01).
Command codes and the clock period come from the rendered gen_knobs.py (one origin). Failures are
Python asserts (the only Python-side failure mechanism, TB_CONTRACT Section 3); messages are ASCII."""
import cocotb
from cocotb.triggers import Edge, with_timeout

from dv.auto_dv.gen_tb.gen_knobs import CMD, PLUSARGS


def knob_default(name):
    """A rendered TB constant (dv/auto_dv/gen_tb/gen_knobs.py CONSTANTS)."""
    from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS
    return CONSTANTS[name]


def finish_timeout_cycles():
    """+gen_finish_timeout when supplied, else its default (rendered from GEN_FINISH_TIMEOUT_CYCLES_DEFAULT)."""
    p = PLUSARGS["finish_timeout"]
    return int(cocotb.plusargs.get(p["plusarg"], p["default"]))


class GenBridge:
    def __init__(self, handles, log):
        self.h = handles
        self.log = log
        self.sent = 0
        self.seq = 0
        self.period_ns = knob_default("GEN_CLK_PERIOD_NS")

    async def _edge(self, sig, cycles, what):
        try:
            await with_timeout(Edge(sig), cycles * self.period_ns, "ns")
        except Exception as exc:  # cocotb SimTimeoutError
            raise AssertionError(f"GEN_BRIDGE: no edge on {what} within {cycles} cycles ({type(exc).__name__})") from None

    async def start(self, timeout_cycles=2000):
        """alive first (watchdog), then wait for the SV listener, then declare stimulus active."""
        b = self.h.b
        b.alive.value = 1
        if not (b.listener_armed.value.is_resolvable and int(b.listener_armed.value) == 1):
            await self._edge(b.listener_armed, timeout_cycles, "listener_armed")
        b.stim_active.value = 1
        self.log.info("GEN_BRIDGE started: listener armed, stim_active=1")

    async def cmd(self, kind, args=(0, 0, 0, 0), timeout_cycles=200):
        """Issue one command; returns peek_data (meaningful for MEM_PEEK)."""
        b = self.h.b
        code = CMD[kind]
        self.seq = (self.seq + 1) & 0xFFFF
        a = list(args) + [0] * (4 - len(args))
        b.cmd_kind.value = code
        b.cmd_arg0.value = a[0] & 0xFFFFFFFF
        b.cmd_arg1.value = a[1] & 0xFFFFFFFF
        b.cmd_arg2.value = a[2] & 0xFFFFFFFF
        b.cmd_arg3.value = a[3] & 0xFFFFFFFF
        b.cmd_seq.value = self.seq
        b.cmd_valid.value = 0 if int(b.cmd_valid.value) else 1
        await self._edge(b.cmd_ack, timeout_cycles, f"cmd_ack for {kind} seq {self.seq}")
        ack_seq = int(b.cmd_ack_seq.value)
        assert ack_seq == self.seq, f"GEN_BRIDGE: cmd_ack_seq {ack_seq} != sent seq {self.seq} ({kind})"
        self.sent += 1
        return int(b.peek_data.value)

    async def wait_cycles_until(self, target_cycle, timeout_cycles=None):
        """Arm the cycle threshold and await its single hit edge."""
        b = self.h.b
        b.evt_cycle_target.value = target_cycle & 0xFFFFFFFF
        b.evt_cycle_arm.value = 0 if int(b.evt_cycle_arm.value) else 1
        budget = timeout_cycles if timeout_cycles is not None else target_cycle + 100
        await self._edge(b.evt_cycle_hit, budget, f"evt_cycle_hit for cycle {target_cycle}")

    async def wait_retired_until(self, target_count, timeout_cycles):
        b = self.h.b
        b.evt_retired_target.value = target_count & 0xFFFFFFFF
        b.evt_retired_arm.value = 0 if int(b.evt_retired_arm.value) else 1
        await self._edge(b.evt_retired_hit, timeout_cycles, f"evt_retired_hit for {target_count} retirements")

    async def finish(self, timeout_cycles=None):
        """Own checks first, then drop stim_active, then the finish handshake (TB_CONTRACT Section 2);
        the budget is the caller's, else +gen_finish_timeout, else its rendered default."""
        b = self.h.b
        consumed = int(b.cmds_consumed.value)
        assert consumed == self.sent, f"GEN_BRIDGE: cmds_consumed {consumed} != sent {self.sent}"
        b.stim_active.value = 0
        budget = timeout_cycles if timeout_cycles is not None else finish_timeout_cycles()
        b.finish_req.value = 1
        await self._edge(b.finish_ack, budget, "finish_ack")
        self.log.info("GEN_BRIDGE finished: %d commands sent and consumed, %d retirements counted",
                      self.sent, int(b.evt_retired_count.value))
