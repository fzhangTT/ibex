# Component API: gen_binds.sv (binds home)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C10; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

AS BUILT (landing 2b, T-162): `dv/auto_dv/tb/gen_binds.sv` binds `gen_protocol_props` into `gen_dut_top` (`bind gen_dut_top
gen_protocol_props #(...) gen_protocol_props_i (.*, .ibus_intg_corrupt_i(gen_tb_top.u_ibus_if.intg_corrupt),
.dbus_intg_corrupt_i(gen_tb_top.u_dbus_if.intg_corrupt))`): every port of the wrapper by name plus the two bus interfaces'
corruption flags, no DUT internal. `dv/auto_dv/tb/gen_protocol_props.sv` is rtl-arch's gen_protocol_props_draft.sv
(T-044, companion table gen_protocol_props_table.md) kept id-for-id: 50 `P_ASSERT` properties and 20 `P_COVER` properties in
nine groups (st, ibus, dbus, icram, scrkey, irq, dbg, alert, rvfi), each assert reporting `uvm_report_error(<id>, "GEN_PROTO
<id>: protocol property violated at cycle N")` under its own id; the four draft properties that read DUT internals
(sva_irq_pending_comb, sva_dbg_entry_bound, sva_dbg_entry_seen, sva_dbg_req_withdrawn) are not bound (the irq and debug
checkers hold those rules at the boundary), the integrity rows take the driven corruption flags instead of a static
parameter, and the knobs are per group (`+gen_chk_sva_<group>`, `+gen_chk_all` precedence) rather than per property. The
stimulus-legality self-check `sva_rvalid_legal` stays inside `dv/auto_dv/tb/gen_bus_if.sv` (knob
`+gen_chk_sva_rvalid_legal`). Mutation evidence (gen_mut_step2b.md, landing 2b): agent-side MUT-M (the key responder
keeps ic_scr_key_valid_i high through a re-key; row sva_scrkey, 5) and MUT-N (instr_err_i pulses outside a response; row sva_ibus, 405), DUT-side
out-of-tree RTL mutants RM1 (core_busy_o On bits never rise; sva_st, 545), RM2 (rvfi_halt on every record; sva_rvfi, 169)
and RM3 (data_tag_o high; sva_dbus, 545), each with its group knob's ablation PASS. The plan's ids `gen_sva_ibus` /
`gen_sva_dbus` map to the groups `sva_ibus` / `sva_dbus`. The checker knobs `chk_ibus_proto`, `chk_ibus_outstanding`,
`chk_dbus_proto`, `chk_dbus_outstanding`, `chk_dbus_split`, `chk_dbus_store_intg` and `chk_isa_csr` stay rendered without a consumer (their rules are the agents' and the comparator's, not this home's; the split rule in
particular has no checker, see the landing-2c paragraph below).

The one file that contains every `bind`: protocol SVAs on the wrapper's ports (assertion
coverage), coverage modules, and the approved probe monitors. No bind forces or drives a DUT net;
error injection is entirely at the boundary.

AS BUILT (landing 2c): the instance is `gen_protocol_props_i` (paths `gen_tb_top.u_dut.gen_protocol_props_i.sva_*`,
CR-2B-L-7); the group knobs are read from `gen_tb_pkg::PLUSARG_CHK_SVA_*` and `PLUSARG_CHK_ALL` (`chk_en(name)`, CR-2B-L-6);
the icram widths are the parameters `TagSizeECC` / `LineSizeECC` the bind passes from gen_dut_top (CM43-L-1);
`sva_alert_minor_window` uses `ICACHE_ECC_WINDOW`, bound to `GEN_ICACHE_ECC_WINDOW`, raised from 1 to 2 in gen_tb_knobs.yaml
with the reason (the RAM read lands one cycle after the request and the alert one cycle after the check; landing 2b measured
1 or 2), so the misc checker and the SVA share one window (CR-2B-L-5, CM43-M-1; no icram ECC injection exists, so no run
shows the tighter window biting: stated in gen_mut_step2b.md); the header cites rtl-arch's tracked anchor file instead of
the untracked draft path and the landing tag (CM43-L-6); dcsr's prv field is read through `GEN_DCSR_PRV_BIT_LOW` /
`GEN_DCSR_PRV_BIT_HIGH` (CM43-L-3). The split rule (the second half's address and byte enables) has no checker of its own:
the two draft asserts are covers in gen_protocol_props.sv, listed in its header's exception list, and the rule is covered
only by the lock-step compare of the loaded or stored value (CR-2B-L-4). Mutation evidence for the four groups without one
in 2b (CR-2B-M-2), gen_mut_step2b.md: MS-ICRAM (out-of-tree RTL mutant of rtl/ibex_icache.sv, the tag request dropped on
the allocation write; sva_icram, 397), MS-IRQ (an X on irq_timer_i for one record; sva_irq, 2), MS-DBG (an X on debug_req_i
for one record; sva_dbg, 2), MS-ALERT (out-of-tree RTL mutant of rtl/ibex_core.sv, alert_major_internal_o tied high;
sva_alert, 2851), each with its group knob's ablation PASS.

## 2. Files and how to call it

As built: `dv/auto_dv/tb/gen_binds.sv` (the one bind) and `dv/auto_dv/tb/gen_protocol_props.sv` (the bound module), both after
`gen_dut_top.sv` in `dv/auto_dv/tb/gen_tb.f`. Planned beyond them: bound modules `gen_ibus_sva.sv`, `gen_dbus_sva.sv`,
`gen_scrkey_sva.sv`, `gen_*_cov.sv`, `gen_cover_props.sv` (rtl-arch exclusion-evidence properties;
compile hazards handled as its header lists: enum labels replaced by the 3-bit encodings if VCS
rejects hierarchical enum references, generate-scope paths `g_writeback_stage` and `gen_multdiv_fast`),
probe monitors `gen_probe_*.sv` (P1 accepted, P4 conditional, P6 off per the probe register); the TB
build never defines `DV_FCOV_DISABLE` (P4 samples RTL `fcov_*` nets),
control interface `gen_sva_ctl_if` (per-SVA enables tied to the `+gen_chk_*` knobs).

Compiled with the TB filelist; binds target `gen_tb_top.u_dut` (wrapper ports) and, for approved
probes, `u_dut.u_ibex_core.<path>`; paths appear only here (dv_principles Section 5).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_chk_<id>` | `PLUSARG_CHK_*` | each bound SVA follows the knob of the checker whose rule it duplicates | 1 |
| `+gen_chk_sva_st / _ibus / _dbus / _icram / _scrkey / _irq / _dbg / _alert / _rvfi` | `PLUSARG_CHK_SVA_*` | protocol group enables (as built, landing 2b); `+gen_chk_all=0` silences them, `+gen_chk_all=0 +gen_chk_sva_<group>=1` isolates one group | 1 |

## 4. Wave-level behaviour

SVAs sample on `posedge clk_i`, disabled while `!rst_ni`; they restate the C3 protocol rules
(request hold, one rvalid per grant, ordering, outstanding bounds, key pulse) for assertion
coverage.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `(no separate ids) SVA forms of `ibus_proto`, `dbus_proto`, `scrkey_handshake`` | an SVA form of an agent checker carries the SAME checker id and the SAME `+gen_chk_<id>` knob as the agent row; the binds home never introduces a second name for one rule | the loci of the agent checker rows | `+gen_chk_(no separate ids) SVA forms of `ibus_proto`, `dbus_proto`, `scrkey_handshake`=0` |
| `sva_rvalid_legal` | TB stimulus legality: `instr_rvalid_i`/`data_rvalid_i` only while a grant is outstanding and never in the grant cycle (rtl-arch T-022 evidence 5.2) | TB self-check, not a DUT checker | `+gen_chk_sva_rvalid_legal=0` |
| `T022_NEVER_*` | rtl-arch exclusion-evidence never-taken properties (`gen_cover_props.sv`, promoted from `dv/auto_dv/work/rtl-arch/gen_cover_props_draft.sv`): a hit means the exclusion candidate is reachable; `assert ... else $error`, collected, reported by Runtime as an exclusion-evidence failure, fails the run until rtl-arch withdraws the exclusion | exclusion evidence, not a DUT checker; knob `+gen_chk_t022_never` (default on in every tier); `T022_COVER_*` are cover-only | `+gen_chk_T022_NEVER_*=0` |

## 6. Failure path and diagnostics

SVA failures are `uvm_error` through the `gen_sva_ctl_if` reporting hook (so the log scanner sees
one mechanism); assertion coverage counts toward the assertion metric.

## 7. Coverage hooks

Assertion coverage of the SVAs; `gen_*_cov` modules bound here sample signal-level groups.

## 8. At build

Add probe binds only with a probe-register row marked approved.
