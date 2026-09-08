#!/usr/bin/env python3
"""Check every file:line the TB defect register cites, at the commit the register pins it to.

A line number is evidence only while the file holds still, and these files do not: three of them moved under
the register in a single day. So each entry below is (row, commit, path, line, must_contain), historical
citations naming the commit where the cited code was true (normally the fix's parent) and current ones taking
the register's pin, which the record states in its own header and this tool reads from there.

The table is checked BOTH ways: every entry must resolve, and every file:line the register cites must appear
in the table, so a citation added to the record without a check here fails rather than passing unexamined.

It resolves commits, so it runs in the clone rather than in a detached archive; --register points it at the
copy under verification, which may sit in one.

Usage: gen_register_cites.py [--sha COMMIT] [--register FILE] [--verbose] [--self-test]
Exit: 0 all resolve and all are covered; 1 a citation fails; 2 the run cannot decide (no checkout, or a
commit the table names is absent), which is a refusal and never a pass.
"""
import re
import sys
import pathlib
import argparse
import subprocess

R = pathlib.Path(__file__).resolve()
while not (R / 'dv/auto_dv/contract').is_dir():
    if R.parent == R:
        sys.exit('repo root not found (no dv/auto_dv/contract above this file)')
    R = R.parent

REGISTER = R / 'dv/auto_dv/evidence/gen_tb_defects.md'
CURRENT = '@CUR@'

CITES = [
 ('T12', '1deec4c', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 377, 'end else if (dbg_entry) begin'),
 ('T12', '1deec4c', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 378, 'gen_isa_arm_async(t.ext_pre_mip'),
 ('T11', '1deec4c', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 485, 'if (t.ext_rf_wr_suppress && !is_seq) begin'),
 ('T11', '1deec4c', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 493, 'intg_first_addr = t.mem_addr'),
 ('T11', '1deec4c', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 498, 'end'),
 ('T11', '41bcbe8', 'dv/auto_dv/env/gen_checkers_pkg.sv', 467, '`uvm_error("crash_dump"'),
 ('T11', CURRENT, 'rtl/ibex_controller.sv', 416, 'mem_resp_intg_err_addr_d'),
 ('T11', CURRENT, 'rtl/ibex_load_store_unit.sv', 258, 'addr_last_d = addr_incr_req_o'),
 ('T11', '87fd39f', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 493, 'if (!is_seq && gen_bus_err_log::intg_pending'),
 ('T11', '87fd39f', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 496, 'gen_bus_err_log::intg_first_addr = t.mem_addr;'),
 ('T11', '87fd39f', 'dv/auto_dv/tb/gen_tb_pkg.sv', 763, 'static function bit peek_intg_word'),
 ('T1', CURRENT, 'dv/auto_dv/tb/gen_bridge_if.sv', 24, 'evt_cycle_target'),
 ('T1', CURRENT, 'dv/auto_dv/tb/gen_bridge_if.sv', 25, 'evt_cycle_arm'),
 ('T1', CURRENT, 'dv/auto_dv/tb/gen_bridge_if.sv', 77, 'evt_cycle_arm != evt_cycle_arm_q'),
 ('T1', CURRENT, 'dv/auto_dv/tb/gen_bridge_if.sv', 80, 'evt_cycle_hit'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 611, 'endfunction'),
 ('T5', CURRENT, 'dv/auto_dv/env/gen_checkers_pkg.sv', 568, 'fe_off_cycle = misc.cycle; fe_off_valid = 1'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 607, 'function void ack_seen'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 609, 'GEN_IRQ_HOLD_UNTIL_ACK'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 610, 'cmd_clr'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 814, 'releases the UNTIL_ACK lines'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 816, 'function void on_write'),
 ('T3', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 194, 'posedge outputs are stable'),
 ('T3', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 264, '@(negedge vif.clk)'),
 ('T3', 'e6eb3a2', 'dv/auto_dv/env/gen_rvfi_pkg.sv', 136, '@(posedge vif.clk)'),
 ('T3', 'e6eb3a2', 'dv/auto_dv/env/gen_checkers_pkg.sv', 241, '@(posedge vif.clk)'),
 ('T3', 'e6eb3a2', 'dv/auto_dv/env/gen_checkers_pkg.sv', 476, '@(posedge misc.clk)'),
 ('T3', 'e6eb3a2', 'dv/auto_dv/env/gen_fcov_pkg.sv', 1594, '@(posedge ctrl_vif.clk)'),
 ('T4', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 2181, '@(posedge ctrl_vif.rst_n)'),
 ('T4', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 2183, 'rst_pending_cls'),
 ('T4', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 2185, 'irq_rst_pins = irq_vif.lines()'),
 ('T4', CURRENT, 'dv/auto_dv/tb/gen_dbg_if.sv', 3, "logic req = 1'b0"),
 ('T4', CURRENT, 'dv/auto_dv/tb/gen_irq_if.sv', 5, 'sw'),
 ('T2', 'e6eb3a2^', 'dv/auto_dv/env/gen_agents_pkg.sv', 820, 'endfunction'),
 ('T4', CURRENT, 'dv/auto_dv/tb/gen_irq_if.sv', 9, "nm      = 1'b0"),
 ('T6', CURRENT, 'rtl/ibex_if_stage.sv', 224, 'csr_mtvec_i[31:8], 8'),
 ('T6', CURRENT, 'rtl/ibex_if_stage.sv', 228, 'irq_vec'),
 ('T5', '55ef529^', 'dv/auto_dv/env/gen_checkers_pkg.sv', 398, 'int unsigned fe_off_cycle = 0'),
 ('T5', '55ef529^', 'dv/auto_dv/env/gen_checkers_pkg.sv', 449, 'if (fe_off_cycle != 0) begin'),
 ('T5', '55ef529^', 'dv/auto_dv/env/gen_checkers_pkg.sv', 538, 'gen_fetch_en_windows::publish'),
 ('T5', '55ef529^', 'dv/auto_dv/env/gen_checkers_pkg.sv', 539, 'if (fe_on) fe_off_cycle = 0;'),
 ('T5', CURRENT, 'dv/auto_dv/env/gen_checkers_pkg.sv', 431, 'bit fe_off_valid = 0'),
 ('T5', CURRENT, 'dv/auto_dv/env/gen_checkers_pkg.sv', 482, 'if (fe_off_valid) begin'),
 ('T5', CURRENT, 'dv/auto_dv/env/gen_checkers_pkg.sv', 571, 'fe_off_valid) gen_fetch_en_windows::publish'),
 ('T5', CURRENT, 'dv/auto_dv/env/gen_checkers_pkg.sv', 572, 'fe_off_cycle = 0; fe_off_valid = 0;'),
 ('T6', '9c7f8f6^', 'dv/auto_dv/env/gen_fcov_pkg.sv', 448, "bit was  = st.is_intr ? 1'b0"),
 ('T6', '9c7f8f6^', 'dv/auto_dv/env/gen_fcov_pkg.sv', 461, '(now && was)'),
 ('T6', '9c7f8f6^', 'dv/auto_dv/env/gen_fcov_pkg.sv', 464, 'n_irq_mret_entry++'),
 ('T6', '9c7f8f6^', 'dv/auto_dv/env/gen_fcov_pkg.sv', 467, 'st.is_intr && v =='),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 452, "(st.is_intr && !st.debug_mode) ? 1'b0"),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 460, 'st.is_trap) return;'),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 479, '(st.is_intr || prev_trapped)'),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 513, 'prev_trapped = st.is_trap && !st.debug_mode'),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_fcov_pkg.sv', 2913, 'GEN_FCOV_REF'),
 ('T6', CURRENT, 'dv/auto_dv/env/gen_rvfi_pkg.sv', 198, 'after this record'),
 ('T6', CURRENT, 'rtl/ibex_if_stage.sv', 222, 'EXC_PC_EXC'),
 ('T6', CURRENT, 'rtl/ibex_if_stage.sv', 225, 'EXC_PC_IRQ'),
 ('T6', CURRENT, 'rtl/ibex_cs_registers.sv', 918, 'debug_mode_i'),
 ('T6', CURRENT, 'rtl/ibex_cs_registers.sv', 924, 'mstatus_d.mie'),
 ('T8', 'c045115', 'dv/auto_dv/tb/gen_protocol_props.sv', 133, '(instr_rvalid_i && (ibus_outstanding'),
 ('T8', 'c045115', 'dv/auto_dv/tb/gen_protocol_props.sv', 135, '(data_rvalid_i && (dbus_outstanding'),
 ('T8', 'ac2d306', 'dv/auto_dv/tb/gen_protocol_props.sv', 135, 'ibus_outstanding <= ibus_outstanding'),
 ('T8', 'ac2d306', 'dv/auto_dv/tb/gen_protocol_props.sv', 138, 'data_rvalid_i && dbus_outstanding > 0'),
 ('T9', '8ee50ea^', 'dv/auto_dv/tb/gen_bus_if.sv', 38, '- (rvalid ? 1 : 0)'),
 ('T9', '8ee50ea^', 'dv/auto_dv/tb/gen_bus_if.sv', 47, 'rvalid |-> (outstanding > 0)'),
 ('T9', '8ee50ea^', 'dv/auto_dv/tb/gen_bus_if.sv', 51, 'cov_rvalid_legal'),
 ('T9', CURRENT, 'dv/auto_dv/tb/gen_bus_if.sv', 42, '((rvalid && outstanding > 0) ? 1 : 0)'),
 ('T10', CURRENT, 'dv/auto_dv/env/gen_agents_pkg.sv', 295, 'if (vif.req) begin'),
 ('T10', CURRENT, 'dv/auto_dv/env/gen_agents_pkg.sv', 306, 'gnt_wait == 0 && pend.size() < cfg.max_outstanding'),
 ('T10', CURRENT, 'dv/auto_dv/env/gen_agents_pkg.sv', 313, "vif.gnt = 1'b1"),
 ('T10', CURRENT, 'dv/auto_dv/env/gen_agents_pkg.sv', 320, '@(posedge vif.clk)'),
 ('T10', CURRENT, 'rtl/ibex_icache.sv', 851, 'fill_rvd_arb'),
 ('T10', CURRENT, 'rtl/ibex_icache.sv', 852, 'fill_older_q'),
]


def pin_from(register):
    """The record states its own pin, so a gate can call this check with no argument."""
    m = re.search(r'read at ([0-9a-f]{7,40})', register.read_text(encoding='ascii'))
    return m.group(1) if m else None


def tree_files(sha):
    r = subprocess.run(['git', 'ls-tree', '-r', '--name-only', sha], capture_output=True, text=True, cwd=R)
    return r.stdout.split() if r.returncode == 0 else []


def register_citations(register, sha):
    """Every file:line in the register, paired with its file. The record names a path in full once and then
    cites the same file by basename or by a bare :NNN, so a basename resolves against the CITED commit's tree,
    and a mention of a file this table cannot check (a yaml, an assembly fixture) clears the pairing rather
    than letting the next bare line number attach to the wrong path."""
    by_base = {}
    for path in tree_files(sha):
        by_base.setdefault(path.split('/')[-1], []).append(path)
    out, bad = [], []
    tok = re.compile(r'((?:[\w.]+/)*[\w]+\.[A-Za-z]\w*)|(?<!\[):(\d+)(?:-(\d+))?')
    for row in register.read_text(encoding='ascii').splitlines():
        if not row.startswith('| T'):
            continue
        ref = row.split('|')[1].strip()
        last = None
        for m in tok.finditer(row):
            if m.group(1):
                name = m.group(1)
                if not name.endswith(('.sv', '.py')):
                    last = None
                elif '/' in name:
                    last = name
                else:
                    hits = by_base.get(name, [])
                    if len(hits) == 1:
                        last = hits[0]
                    else:
                        bad.append(f'{ref} names {name}, which matches {len(hits)} files at {sha}')
                        last = None
            elif last:
                for n in (m.group(2), m.group(3)):
                    if n:
                        out.append((ref, last, int(n)))
    return out, bad


def resolve(entries, sha, verbose=False):
    """Read each cited line at its own commit. A commit that cannot be read at all is the caller's to refuse,
    not something to report as sixty bad citations."""
    cache, bad = {}, []
    for row, csha, path, line, want in entries:
        csha = sha if csha == CURRENT else csha
        key = (csha, path)
        if key not in cache:
            r = subprocess.run(['git', 'show', f'{csha}:{path}'], capture_output=True, text=True, cwd=R)
            cache[key] = r.stdout.splitlines() if r.returncode == 0 else None
        ls = cache[key]
        if ls is None:
            bad.append(f'{row} {path}@{csha}: file not readable')
            continue
        got = ls[line - 1] if 0 < line <= len(ls) else ''
        if want not in got:
            bad.append(f'{row} {path}:{line}@{csha}: want {want!r}, line reads {got.strip()[:70]!r}')
        elif verbose:
            print(f'  ok {row} {path}:{line}@{csha}  {got.strip()[:60]}')
    return bad


def missing_commits(sha):
    out = []
    for c in sorted({(sha if c == CURRENT else c) for _, c, _, _, _ in CITES}):
        r = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', c + '^{commit}'],
                           capture_output=True, text=True, cwd=R)
        if r.returncode:
            out.append(c)
    return out


def _self_test(sha):
    """Two negative fixtures with their control: a moved line must be caught by the resolution half, an
    uncarried citation by the coverage half, and an absent pin must be refused rather than reported as bad."""
    import tempfile
    ok = True

    control = resolve(CITES, sha)
    good = not control
    ok = ok and good
    print(f'SELF-TEST {"ok  " if good else "BAD "} the table resolves at the pin: {len(control)} failure(s), want 0')

    moved = [(r, c, p, l + 3, w) for r, c, p, l, w in CITES[:1]] + list(CITES[1:])
    hits = resolve(moved, sha)
    good = len(hits) == 1
    ok = ok and good
    print(f'SELF-TEST {"ok  " if good else "BAD "} a moved line fails: {len(hits)} failure(s), want 1')

    with tempfile.TemporaryDirectory() as d:
        copy = pathlib.Path(d) / 'gen_tb_defects.md'
        text = REGISTER.read_text(encoding='ascii')
        text = text.replace('| T1 | ', '| T1 | dv/auto_dv/tb/gen_bridge_if.sv:999 ', 1)
        copy.write_text(text, encoding='ascii')
        cited, names = register_citations(copy, sha)
        covered = {(r, p, l) for r, _, p, l, _ in CITES}
        uncovered = [c for c in cited if c not in covered]
        good = len(uncovered) == 1 and not names
        ok = ok and good
        print(f'SELF-TEST {"ok  " if good else "BAD "} a citation the table does not carry fails: '
              f'{len(uncovered)} uncovered, want 1')

    absent = missing_commits('0000000')
    good = absent == ['0000000']
    ok = ok and good
    print(f'SELF-TEST {"ok  " if good else "BAD "} an absent pin is refused, not reported as bad citations: '
          f'{absent}, want the pin alone')

    print('gen_register_cites --self-test:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sha', default=None,
                    help='the commit the register pins its current citations to (default: the pin in the record)')
    ap.add_argument('--register', default=str(REGISTER), help='the copy of the register to check')
    ap.add_argument('--verbose', action='store_true', help='print every citation as it is checked')
    ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args()
    if subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, cwd=R).returncode:
        print('not a git checkout: this check resolves commits, so run it in the clone and point --register at '
              'the copy under verification')
        return 2
    register = pathlib.Path(a.register)
    sha = a.sha or pin_from(register)
    if sha is None:
        print(f'{register}: the record states no pin and no --sha was given')
        return 2
    absent = missing_commits(sha)
    if absent:
        print('cannot decide: this checkout does not carry ' + ', '.join(absent) +
              '; the citations are unchecked rather than wrong')
        return 2
    if a.self_test:
        return _self_test(sha)
    bad = resolve(CITES, sha, a.verbose)
    cited, unresolved_names = register_citations(register, sha)
    covered = {(row, path, line) for row, _, path, line, _ in CITES}
    uncovered = [c for c in cited if c not in covered]
    print(f'GEN_REGISTER_CITES: {len(CITES)} citations checked at {sha} against {a.register} '
          f'(historical ones at their own commit)')
    for b in bad:
        print('  BAD ' + b)
    for b in unresolved_names:
        print('  UNRESOLVED NAME ' + b)
    for row, path, line in uncovered:
        print(f'  UNCHECKED {row} cites {path}:{line} and this table does not carry it')
    ok = not bad and not uncovered and not unresolved_names
    print('GEN_REGISTER_CITES: ' + ('PASS' if ok else f'FAIL, {len(bad)} unresolved, {len(uncovered)} unchecked'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
