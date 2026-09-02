#!/usr/bin/env python3
"""Proves each ci/mcp/*.sh wrapper answers a raw JSON-RPC initialize+tools/list
handshake over stdio (the WS5 T3 gate: same probe used for the codex/Claude
native-registry evidence in docs/dv/evidence/ws5-mcp-toollist-*.txt).
Usage: python3 ci/mcp/probes/mcp_probe.py
"""
import json, os, select, subprocess, sys, time

REPO = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(os.path.abspath(__file__))
).decode().strip()

servers = {
    "siliconpilot": ["bash", "-c", f'exec "{REPO}/ci/mcp/siliconpilot-mcp.sh"'],
    "fsdb-mcp-server": ["bash", "-c", f'exec "{REPO}/ci/mcp/fsdb-mcp.sh"'],
    "verdi-cov-mcp": ["bash", "-c", f'exec "{REPO}/ci/mcp/verdi-cov-mcp.sh"'],
}

def send(proc, message):
    proc.stdin.write((json.dumps(message, separators=(",", ":")) + "\n").encode())
    proc.stdin.flush()

def read_json_line(proc, deadline):
    diagnostics = []
    while time.monotonic() < deadline:
        ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], min(1.0, deadline - time.monotonic()))
        for stream in ready:
            line = stream.readline()
            if not line:
                continue
            text = line.decode(errors="replace").rstrip()
            if stream is proc.stderr:
                if text:
                    diagnostics.append(text)
                continue
            try:
                return json.loads(text), diagnostics
            except json.JSONDecodeError:
                diagnostics.append("non-JSON stdout: " + text)
        if proc.poll() is not None:
            break
    return None, diagnostics

exit_status = 0
for name, command in servers.items():
    t0 = time.monotonic()
    proc = subprocess.Popen(command, cwd=REPO, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, bufsize=0)
    all_diagnostics = []
    try:
        deadline = time.monotonic() + 60
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                                "clientInfo": {"name": "ws5-t3-probe", "version": "1.0"}}})
        init = None
        while time.monotonic() < deadline:
            msg, diag = read_json_line(proc, deadline)
            all_diagnostics.extend(diag)
            if msg is None:
                break
            if msg.get("id") == 1:
                init = msg
                break
        if init is None or "error" in init or not init.get("result"):
            print(json.dumps({"server": name, "stage": "initialize", "response": init,
                               "elapsed_s": round(time.monotonic() - t0, 1),
                               "diagnostics": all_diagnostics[-10:]}))
            exit_status = 1
            continue
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        listed = None
        while time.monotonic() < deadline:
            msg, diag = read_json_line(proc, deadline)
            all_diagnostics.extend(diag)
            if msg is None:
                break
            if msg.get("id") == 2:
                listed = msg
                break
        if listed is None or "error" in listed:
            print(json.dumps({"server": name, "stage": "tools/list", "response": listed,
                               "elapsed_s": round(time.monotonic() - t0, 1),
                               "diagnostics": all_diagnostics[-10:]}))
            exit_status = 1
            continue
        tools_list = listed.get("result", {}).get("tools", [])
        if not tools_list:
            print(json.dumps({"server": name, "stage": "tools/list", "error": "empty tools list",
                               "response": listed, "elapsed_s": round(time.monotonic() - t0, 1),
                               "diagnostics": all_diagnostics[-10:]}))
            exit_status = 1
            continue
        print(json.dumps({
            "server": name,
            "serverInfo": init.get("result", {}).get("serverInfo"),
            "tool_count": len(tools_list),
            "tool_names": sorted(t.get("name") for t in tools_list),
            "elapsed_s": round(time.monotonic() - t0, 1),
        }))
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

sys.exit(exit_status)
