"""gen_handles: the ONLY Python file of the generated TB that spells hierarchical paths (architecture
C11). It resolves the top-level clock/reset and every field of the cocotb bridge instance
(gen_bridge_if u_bridge_if in gen_tb_top) from the cocotb TOPLEVEL handle and fails loud at start-up
on a missing handle. No DUT-internal path lives here: the bridge fields are the whole Python view.
ASCII-only messages (TB_CONTRACT Section 4)."""
import types

BRIDGE_INST = "u_bridge_if"
TOP_SIGNALS = ("clk", "rst_n")
# Python-written fields
BRIDGE_WRITE = (
    "alive", "stim_active", "cmd_valid", "cmd_kind", "cmd_arg0", "cmd_arg1", "cmd_arg2", "cmd_arg3",
    "cmd_seq", "evt_retired_target", "evt_retired_arm", "evt_cycle_target", "evt_cycle_arm", "finish_req",
)
# SV-written fields (Python reads or awaits an edge)
BRIDGE_READ = (
    "listener_armed", "cmd_ack", "cmd_ack_seq", "cmds_consumed", "peek_data", "evt_retired_hit",
    "evt_cycle_hit", "evt_irq_taken", "evt_dbg_entered", "evt_eot_seen", "evt_eot_code", "evt_eot_count",
    "evt_retired_count",
    "evt_err_count", "finish_ack", "cycle_count",
)
BRIDGE_FIELDS = BRIDGE_WRITE + BRIDGE_READ


class GenHandles:
    """Resolved handles: `h.clk`, `h.rst_n`, `h.b.<field>` for every bridge field."""

    def __init__(self, dut, bridge_inst=BRIDGE_INST):
        self.dut = dut
        top = getattr(dut, "_name", "TOPLEVEL")
        for s in TOP_SIGNALS:
            setattr(self, s, self._get(dut, s, f"{top}.{s}"))
        scope = self._get(dut, bridge_inst, f"{top}.{bridge_inst}")
        self.b = types.SimpleNamespace()
        for f in BRIDGE_FIELDS:
            setattr(self.b, f, self._get(scope, f, f"{top}.{bridge_inst}.{f}"))

    def bridge(self, name):
        return getattr(self.b, name)

    @staticmethod
    def _get(obj, attr, path):
        try:
            return getattr(obj, attr)
        except Exception as exc:  # cocotb raises AttributeError for an unknown child
            raise RuntimeError(f"GEN_HANDLES: missing handle {path} ({type(exc).__name__})") from None
