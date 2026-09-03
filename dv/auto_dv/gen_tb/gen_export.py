"""gen_export: the Python reader of the TB's record and event export (architecture Section 9, T-080). read(path, seq)
parses the prefix of the file that ends at the flush marker carrying `seq` (the number EXPORT_FLUSH returned) and
enforces the format rules: header field list equal to the rendered EXPORT_RECORD_FIELDS (plus the counter fields
when the header says counters=1), one `# events` row per (source, event) of the enabled sources, `records ==
retired` in the marker, R-line count == records, E-line count == events, E <bus> gnt count == the marker's
<bus>_grants for each enabled bus (format version 2), per enabled bus #req - #gnt in {0, 1} (one request at most
awaits its grant) and 0 <= #gnt - #rvalid <= the bus's outstanding cap (T-141 presence rules: a dropped req or rvalid
writer is visible from the file alone), order strictly +1 across R lines,
non-decreasing cycle across all lines, field count per line equal to its header row, hex-only tokens. Every
violation is an AssertionError (the only Python-side failure mechanism). Radix: every R/I/E value is hex without
prefix; every marker key=value pair (flush, end) and the header's seed= and counters= are decimal. No simulator
access; pure file parsing; ASCII only."""
from collections import namedtuple
from pathlib import Path

from dv.auto_dv.gen_tb.gen_knobs import CONSTANTS, EXPORT_ACTIVE_SOURCES, EXPORT_COUNTER_FIELDS, EXPORT_EVENTS, EXPORT_RECORD_FIELDS

# grants in flight a bus can hold (the drivers' caps): the bound of #gnt - #rvalid at any flush
BUS_MAX_OUTSTANDING = {"ibus": CONSTANTS["GEN_IBUS_MAX_OUTSTANDING"], "dbus": CONSTANTS["GEN_DBUS_MAX_OUTSTANDING"]}

Marker = namedtuple("Marker", "cycle ext_pre_mip ext_post_mip ext_nmi ext_nmi_int ext_debug_req ext_debug_mode")
Flush = namedtuple("Flush", "seq records retired markers events ibus_grants dbus_grants cycle")
Event = namedtuple("Event", "cycle source event fields")
Export = namedtuple("Export", "header records markers events flush")
MARKER_FIELDS = Marker._fields[1:]


def _hex(tok, where):
    try:
        return int(tok, 16)
    except ValueError:
        raise AssertionError(f"GEN_EXPORT: non-hex token {tok!r} in {where}") from None


def _kv(line, prefix, where):
    assert line.startswith(prefix), f"GEN_EXPORT: expected {prefix!r} at {where}, got {line[:60]!r}"
    out = {}
    for tok in line[len(prefix):].split():
        k, _, v = tok.partition("=")
        out[k] = v
    return out


def read(path, seq, counters=False, sources="all"):
    """Records, markers and events up to (not including) the flush marker with sequence `seq`; seq=None reads to the
    end marker (post-run diagnostics only, never the basis of a pass). `sources` is the run's +gen_export_sources value:
    the header's sources= must equal the rendered active list restricted to it (format version 2)."""
    text = Path(path).read_text()
    lines = text.split("\n")
    assert len(lines) >= 3, f"GEN_EXPORT: {path} has no header"
    hdr = _kv(lines[0], "# gen_export v2 ", "line 1")
    fields = list(EXPORT_RECORD_FIELDS) + (list(EXPORT_COUNTER_FIELDS) if counters else [])
    assert hdr.get("counters") == ("1" if counters else "0"), f"GEN_EXPORT: header counters={hdr.get('counters')} but the reader expects {'1' if counters else '0'}"
    assert hdr.get("fields") == ",".join(fields), f"GEN_EXPORT: header field list differs from the rendered EXPORT_RECORD_FIELDS"
    assert lines[1].startswith("# image "), "GEN_EXPORT: line 2 is not the image line"
    enabled = [s for s in hdr.get("sources", "").split(",") if s]
    want = [s for s in EXPORT_ACTIVE_SOURCES if sources == "all" or s in sources.split(",")]
    assert enabled == want, f"GEN_EXPORT: header sources={enabled} but the rendered active sources under +gen_export_sources={sources} are {want}"
    rows = {}
    n = 2
    while n < len(lines) and lines[n].startswith("# events "):
        _, _, src, ev, flds = lines[n].split(" ", 4)
        rows[(src, ev)] = flds.split(",")
        n += 1
    known = {(s, e): list(f) for s, e, f in EXPORT_EVENTS}
    for key, flds in rows.items():
        assert key in known and known[key] == flds, f"GEN_EXPORT: event header row {key} differs from the rendered EXPORT_EVENTS"
        assert key[0] in enabled, f"GEN_EXPORT: header row for a source not in sources= ({key[0]})"
    for key in known:
        assert key[0] not in enabled or key in rows, f"GEN_EXPORT: enabled source {key[0]} lacks its rendered header row {key}"
    # locate the marker: the flush with the requested seq, else the end marker
    marker_idx = None
    for i in range(n, len(lines)):
        if seq is None and lines[i].startswith("# end "):
            marker_idx = i; break
        if seq is not None and lines[i].startswith("# flush ") and _kv(lines[i], "# flush ", f"line {i + 1}").get("seq") == str(seq):
            marker_idx = i; break
    assert marker_idx is not None, f"GEN_EXPORT: no complete flush marker with seq={seq} in {path}" if seq is not None else f"GEN_EXPORT: no end marker in {path}"
    where = f"line {marker_idx + 1}"
    mk = _kv(lines[marker_idx], "# flush " if seq is not None else "# end ", where)
    need = ("seq", "records", "retired", "markers", "events", "ibus_grants", "dbus_grants", "cycle") if seq is not None else ("records", "retired", "markers", "events", "ibus_grants", "dbus_grants")
    for k in need:   # a marker cut short by a buffer boundary is not a complete flush
        assert k in mk, f"GEN_EXPORT: marker without {k}= ({where}): truncated, not a complete marker"
    def _dec(k):   # marker key=value pairs are decimal
        assert mk[k].isdigit(), f"GEN_EXPORT: marker {k}={mk[k]!r} is not decimal ({where})"
        return int(mk[k])
    flush = Flush(_dec("seq") if seq is not None else 0, _dec("records"), _dec("retired"), _dec("markers"), _dec("events"),
                  _dec("ibus_grants"), _dec("dbus_grants"), _dec("cycle") if seq is not None else 0)
    assert flush.records == flush.retired, f"GEN_EXPORT: marker records {flush.records} != retired {flush.retired} (the sink and the bridge disagree)"
    Record = namedtuple("Record", fields)
    records, markers, events = [], [], []
    last_cycle = 0
    for i in range(n, marker_idx):
        line = lines[i]
        if not line or line.startswith("# flush "):
            continue   # earlier flush markers of the same run are allowed inside the prefix
        where = f"line {i + 1}"
        toks = line.split()
        kind = toks[0]
        if kind == "R":
            assert len(toks) == 1 + len(fields), f"GEN_EXPORT: R line with {len(toks) - 1} fields, header has {len(fields)} ({where})"
            rec = Record(*[_hex(x, where) for x in toks[1:]])
            if records:
                assert rec.order == records[-1].order + 1, f"GEN_EXPORT: order {rec.order} after {records[-1].order} ({where})"
            cyc = rec.cycle
            records.append(rec)
        elif kind == "I":
            assert len(toks) == 1 + len(Marker._fields), f"GEN_EXPORT: I line with {len(toks) - 1} fields ({where})"
            m = Marker(*[_hex(x, where) for x in toks[1:]])
            cyc = m.cycle
            markers.append(m)
        elif kind == "E":
            assert len(toks) >= 4, f"GEN_EXPORT: short E line ({where})"
            cyc = _hex(toks[1], where)
            src, ev = toks[2], toks[3]
            key = (src, ev)
            assert key in rows, f"GEN_EXPORT: E line for an unknown (source, event) {src}/{ev} ({where})"
            assert len(toks) == 4 + len(rows[key]), f"GEN_EXPORT: E {src} {ev} with {len(toks) - 4} fields, header row has {len(rows[key])} ({where})"
            events.append(Event(cyc, src, ev, tuple(_hex(x, where) for x in toks[4:])))
        else:
            raise AssertionError(f"GEN_EXPORT: unknown line kind {kind!r} ({where})")
        assert cyc >= last_cycle, f"GEN_EXPORT: cycle {cyc} after {last_cycle} ({where})"
        last_cycle = cyc
    assert len(records) == flush.records, f"GEN_EXPORT: {len(records)} R lines parsed, marker says {flush.records}"
    assert len(markers) == flush.markers, f"GEN_EXPORT: {len(markers)} I lines parsed, marker says {flush.markers}"
    assert len(events) == flush.events, f"GEN_EXPORT: {len(events)} E lines parsed, marker says {flush.events}"
    for bus, grants in (("ibus", flush.ibus_grants), ("dbus", flush.dbus_grants)):   # the drivers' own grant count (MUT-G)
        if bus in enabled:
            n = sum(1 for e in events if e.source == bus and e.event == "gnt")
            assert n == grants, f"GEN_EXPORT: {n} E {bus} gnt lines, marker says {bus}_grants={grants}"
            n_req = sum(1 for e in events if e.source == bus and e.event == "req")
            n_rv = sum(1 for e in events if e.source == bus and e.event == "rvalid")
            assert n_req - n in (0, 1), f"GEN_EXPORT: {bus}: {n_req} E req lines against {n} E gnt lines (at most one request awaits its grant; MUT-I)"
            assert 0 <= n - n_rv <= BUS_MAX_OUTSTANDING[bus], f"GEN_EXPORT: {bus}: {n} E gnt lines against {n_rv} E rvalid lines (outstanding responses must stay within 0..{BUS_MAX_OUTSTANDING[bus]}; MUT-J)"
    return Export(hdr, records, markers, events, flush)
