#!/usr/bin/env python3
"""Proves ci/mcp/fsdb-mcp.sh opens a real FSDB session and returns real waveform
data (not a stub). Zone A: point it at an FSDB your OWN runs produced, e.g. one
under dv/auto_dv/'s out-tree (docs/dv/SIM_RECIPE.md section 6).
Usage: python3 ci/mcp/probes/fsdb_probe.py <wrapper> <design_db> <fsdb_file> <logfile> <tb_top>
  <tb_top> is the name of YOUR TB top module in the dumped hierarchy.

Two fsdb-mcp-server 0.2.6 protocol quirks handled here (not wrapper/config defects):
- the underlying fsdb-digger/PyNPI library writes a stray non-JSON diagnostic line
  ("logDir = ...") directly to stdout on session open, interleaved with the JSON-RPC
  stream -- skip any line that doesn't parse as JSON.
- fastmcp resolves concurrent tool calls out of send order (a fast call sent after a
  slow one can answer first) -- responses are matched by their "id" field, not by
  arrival order, with unmatched ids buffered for later.
"""
import json
import queue
import subprocess
import sys
import threading
import time

WRAPPER, DESIGN_DB, FSDB_FILE, LOGFILE, TB_TOP = sys.argv[1:6]

proc = subprocess.Popen(
    [WRAPPER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, bufsize=1,
)

out_q = queue.Queue()


def reader():
    for line in proc.stdout:
        out_q.put(line)
    out_q.put(None)


threading.Thread(target=reader, daemon=True).start()

log_lines = []


def log(s):
    print(s)
    log_lines.append(s)


def send(obj):
    line = json.dumps(obj)
    log(f">>> {line}")
    proc.stdin.write(line + "\n")
    proc.stdin.flush()


pending = {}  # id -> parsed response, for ids that arrived before we asked for them


def wait_for_id(want_id, timeout):
    deadline = time.time() + timeout
    if want_id in pending:
        return pending.pop(want_id)
    while time.time() < deadline:
        remaining = deadline - time.time()
        try:
            line = out_q.get(timeout=max(remaining, 0.01))
        except queue.Empty:
            break
        if line is None:
            log("<<< [stdout EOF]")
            return None
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            log(f"<<< [non-JSON, skipped] {line}")
            continue
        log(f"<<< {line}")
        if obj.get("id") == want_id:
            return obj
        if "id" in obj:
            pending[obj["id"]] = obj
    log(f"<<< [TIMEOUT after {timeout}s waiting for id={want_id}]")
    return None


def call(method, params, req_id, timeout):
    t0 = time.time()
    send({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
    resp = wait_for_id(req_id, timeout)
    log(f"    [elapsed {time.time()-t0:.1f}s]")
    return resp


def notify(method, params):
    send({"jsonrpc": "2.0", "method": method, "params": params})


def tool_payload(resp):
    """Unwrap {"result": {"content": [{"type":"text","text": "<json>"}], ...}} -> parsed dict."""
    text = resp["result"]["content"][0]["text"]
    return json.loads(text)


failure = None  # first mandatory-result validation failure; drives the exit status

try:
    call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                         "clientInfo": {"name": "ws5-fsdb-probe", "version": "0.2"}}, 1, 60)
    notify("notifications/initialized", {})

    tl = call("tools/list", {}, 2, 60)
    if tl and "result" in tl:
        names = sorted(t["name"] for t in tl["result"]["tools"])
        log(f"    [tool_count={len(names)}] {names}")

    log(f"=== design_db={DESIGN_DB}")
    log(f"=== fsdb_file={FSDB_FILE}")

    create_resp = call("tools/call", {"name": "create_fsdb_session",
                                       "arguments": {"design_db": DESIGN_DB, "fsdb_file": FSDB_FILE}},
                        3, 90)
    create_payload = tool_payload(create_resp) if create_resp else None
    log(f"=== create_fsdb_session payload: {json.dumps(create_payload)}")

    max_time = None
    if create_payload and create_payload.get("success"):
        fi = create_payload["data"]["file_info"]
        max_time = fi["max_time"]
        log(f"    [file_info min_time={fi['min_time']} max_time={fi['max_time']} scale_unit={fi['scale_unit']}]")
    else:
        failure = failure or "create_fsdb_session: no successful session in payload"

    scope_resp = call("tools/call", {"name": "get_child_modules", "arguments": {"scope": "", "max_results": 50}},
                       4, 60)
    scope_payload = tool_payload(scope_resp) if scope_resp else None
    log(f"=== get_child_modules(scope='') payload: {json.dumps(scope_payload)}")

    top_scope = None
    if scope_payload and scope_payload.get("success") and scope_payload["data"].get("child_scopes"):
        for m in scope_payload["data"]["child_scopes"]:
            if m["name"] == TB_TOP:
                top_scope = m["full_path"]
                break
    else:
        failure = failure or "get_child_modules: empty or unsuccessful scope list"
    if top_scope is None:
        failure = failure or f"get_child_modules: {TB_TOP} not found among child_scopes"
    log(f"    [top_scope={top_scope}]")

    sig_resp = call("tools/call", {"name": "get_internal_signals",
                                    "arguments": {"signal_patterns": ["clk"], "scope": top_scope or "",
                                                   "name_regex": ".*clk.*", "max_results": 20}},
                     5, 60)
    sig_payload = tool_payload(sig_resp) if sig_resp else None
    log(f"=== get_internal_signals(scope={top_scope!r}, pattern='clk') payload: {json.dumps(sig_payload)}")

    clk_path = None
    if sig_payload and sig_payload.get("success"):
        sigs = sig_payload["data"].get("signals", [])
        if sigs:
            clk_path = sigs[0].get("full_name") or sigs[0].get("full_path") or sigs[0].get("name")
    else:
        sigs = []
    if not sigs:
        failure = failure or "get_internal_signals: empty or unsuccessful signal list"
    if clk_path is None and top_scope:
        clk_path = f"{top_scope}.clk"
        log(f"    [no match from get_internal_signals; falling back to {clk_path}]")
    log(f"    [clk_path={clk_path}]")

    sample_time = "500000ns"
    if max_time is not None:
        log(f"    [max_time={max_time} (10ps units) ~= {max_time*10/1e6:.3f} us; using sample_time={sample_time}]")

    if clk_path:
        sample_resp = call("tools/call", {"name": "sample_signals_at_time",
                                           "arguments": {"signal_names": [clk_path], "sample_time": sample_time}},
                            6, 60)
        sample_payload = tool_payload(sample_resp) if sample_resp else None
        log(f"=== sample_signals_at_time(signal_names=[{clk_path!r}], sample_time={sample_time!r}) payload: {json.dumps(sample_payload)}")
        if not (sample_payload and sample_payload.get("success")
                and sample_payload["data"].get(clk_path) not in (None, "")):
            failure = failure or "sample_signals_at_time: no real sampled value returned"
    else:
        failure = failure or "sample_signals_at_time: no clk_path resolved to sample"

    if clk_path:
        tr_resp = call("tools/call", {"name": "get_time_range",
                                       "arguments": {"signal_names": [clk_path], "start_time": "0ns", "end_time": "50ns"}},
                        8, 60)
        tr_payload = tool_payload(tr_resp) if tr_resp else None
        log(f"=== get_time_range(signal_names=[{clk_path!r}], start_time='0ns', end_time='50ns') payload: {json.dumps(tr_payload)}")
        tr_data = tr_payload["data"] if tr_payload and tr_payload.get("success") else None
        clk_transitions = tr_data["signals"].get(clk_path, {}).get("transitions") if tr_data else None
        if not (tr_data and tr_data.get("total_transitions", 0) > 0 and clk_transitions):
            failure = failure or "get_time_range: no real transitions (total_transitions/clk_path transitions empty)"
    else:
        failure = failure or "get_time_range: no clk_path resolved to query"

    close_resp = call("tools/call", {"name": "close_fsdb_session", "arguments": {}}, 7, 30)
    log(f"=== close_fsdb_session payload: {json.dumps(tool_payload(close_resp) if close_resp else None)}")

    log("--- done, terminating ---")
finally:
    try:
        proc.stdin.close()
    except Exception:
        pass
    try:
        proc.wait(timeout=15)
    except Exception:
        proc.kill()
    err = proc.stderr.read()
    if err.strip():
        log("--- stderr (trimmed) ---")
        for l in err.strip().splitlines()[-15:]:
            log(l)

with open(LOGFILE, "w") as f:
    f.write("\n".join(log_lines) + "\n")

if failure:
    print(f"FAIL: {failure}", file=sys.stderr)
    sys.exit(1)
