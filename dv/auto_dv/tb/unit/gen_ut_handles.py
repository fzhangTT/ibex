#!/usr/bin/env python3
"""Unit test for dv/auto_dv/gen_tb/gen_handles.py (architecture C11: the only Python file that spells
hierarchical paths). Plain asserts, exit 1 on failure; TDD transcript dv/auto_dv/evidence/gen_tdd_bridge.md."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MOD = ROOT / "dv/auto_dv/gen_tb/gen_handles.py"
fails = 0
def check(what, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {what}" + (f" ({detail})" if detail and not ok else ""))
    if not ok: fails += 1

class FakeSig:
    def __init__(self, name): self._name = name; self.value = 0
class FakeScope:
    def __init__(self, name, sigs):
        self._name = name
        for s in sigs: setattr(self, s, FakeSig(s))
class FakeDut(FakeScope):
    pass

def main():
    check("module exists", MOD.is_file(), str(MOD))
    if fails: return finish()
    spec = importlib.util.spec_from_file_location("gen_handles", MOD)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    fields = list(m.BRIDGE_FIELDS)
    check("bridge field list non-trivial", len(fields) >= 25)
    for f in ("alive", "stim_active", "cmd_valid", "cmd_kind", "cmd_arg0", "cmd_seq", "cmd_ack", "cmd_ack_seq",
              "listener_armed", "cmds_consumed", "peek_data", "evt_retired_target", "evt_retired_arm",
              "evt_retired_hit", "evt_cycle_target", "evt_cycle_arm", "evt_cycle_hit", "finish_req", "finish_ack",
              "cycle_count", "evt_retired_count"):
        check(f"field {f} listed", f in fields)
    dut = FakeDut("gen_tb_top", ["clk", "rst_n"])
    dut.u_bridge_if = FakeScope("u_bridge_if", fields)
    h = m.GenHandles(dut)
    check("clk resolved", h.clk is dut.clk)
    check("bridge field resolved", h.bridge("alive") is dut.u_bridge_if.alive)
    check("attribute access", h.b.alive is dut.u_bridge_if.alive)
    # a missing field must fail loud at start-up and name the path
    dut2 = FakeDut("gen_tb_top", ["clk", "rst_n"])
    dut2.u_bridge_if = FakeScope("u_bridge_if", [f for f in fields if f != "cmd_ack"])
    try:
        m.GenHandles(dut2); check("missing handle raises", False)
    except RuntimeError as e:
        check("missing handle raises", True)
        check("message names the path", "gen_tb_top.u_bridge_if.cmd_ack" in str(e), str(e))
        check("message is ASCII", all(ord(c) < 128 for c in str(e)))
    dut3 = FakeDut("gen_tb_top", ["clk", "rst_n"])
    try:
        m.GenHandles(dut3); check("missing bridge instance raises", False)
    except RuntimeError as e:
        check("missing bridge instance raises", "u_bridge_if" in str(e))
    return finish()

def finish():
    print(f"GEN_UT_HANDLES {'FAIL' if fails else 'PASS'} ({fails} failures)")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
