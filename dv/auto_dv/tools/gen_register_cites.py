#!/usr/bin/env python3
"""Check every file:line the TB defect register cites, at the commit the register pins it to.

A line number is evidence only while the file holds still, and these files do not: three of them moved under
the register in a single day. So each entry below is (row, commit, path, line, must_contain), historical
citations naming the commit where the cited code was true (normally the fix's parent) and current ones taking
the register's pin commit from --sha.

The table is checked BOTH ways: every entry must resolve, and every file:line the register cites must appear
in the table, so a citation added to the record without a check here fails rather than passing unexamined.

It resolves commits, so it runs in the clone rather than in a detached archive; --register points it at the
copy under verification, which may sit in one.

Usage: gen_register_cites.py --sha <commit the register pins its current citations to> [--register FILE]
Exit: 0 all resolve and all are covered; 1 a citation fails; 2 not run inside a git checkout.
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


def register_citations(register):
    """Every file:line in the register, paired with its file. The record names a path in full once and then
    cites the same file by basename or by a bare :NNN, so a basename is resolved against the tracked tree and
    an unresolvable or ambiguous one is reported rather than guessed."""
    tracked = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, cwd=R).stdout.split()

    by_base = {}
    for path in tracked:
        by_base.setdefault(path.split('/')[-1], []).append(path)
    out, bad = [], []
    tok = re.compile(r'((?:[\w.]+/)*[\w]+\.(?:sv|py))|(?<!\[):(\d+)(?:-(\d+))?')
    for row in register.read_text(encoding='ascii').splitlines():
        if not row.startswith('| T'):
            continue
        ref = row.split('|')[1].strip()
        last = None
        for m in tok.finditer(row):
            if m.group(1):
                name = m.group(1)
                if '/' in name:
                    last = name
                else:
                    hits = by_base.get(name, [])
                    if len(hits) == 1:
                        last = hits[0]
                    else:
                        bad.append(f'{ref} names {name}, which matches {len(hits)} tracked files')
                        last = None
            elif last:
                for n in (m.group(2), m.group(3)):
                    if n:
                        out.append((ref, last, int(n)))
    return out, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sha', required=True, help='the commit the register pins its current-state citations to')
    ap.add_argument('--register', default=str(REGISTER), help='the copy of the register to check (default: the tracked one)')
    a = ap.parse_args()
    if subprocess.run(['git', 'rev-parse', '--git-dir'], capture_output=True, cwd=R).returncode:
        print('not a git checkout: this check resolves commits, so run it in the clone and point --register at '
              'the copy under verification')
        return 2
    cache, bad = {}, []
    for row, sha, path, line, want in CITES:
        sha = a.sha if sha == CURRENT else sha
        key = (sha, path)
        if key not in cache:
            r = subprocess.run(['git', 'show', f'{sha}:{path}'], capture_output=True, text=True, cwd=R)
            cache[key] = r.stdout.splitlines() if r.returncode == 0 else None
        ls = cache[key]
        if ls is None:
            bad.append(f'{row} {path}@{sha}: file not readable')
            continue
        got = ls[line - 1] if 0 < line <= len(ls) else ''
        if want not in got:
            bad.append(f'{row} {path}:{line}@{sha}: want {want!r}, line reads {got.strip()[:70]!r}')
    covered = {(row, path, line) for row, _, path, line, _ in CITES}
    cited, unresolved_names = register_citations(pathlib.Path(a.register))
    uncovered = [c for c in cited if c not in covered]
    print(f'GEN_REGISTER_CITES: {len(CITES)} citations checked at {a.sha} against {a.register} '
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
