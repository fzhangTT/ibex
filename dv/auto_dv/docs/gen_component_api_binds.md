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

The one file that contains every `bind`: protocol SVAs on the wrapper's ports (assertion
coverage), coverage modules, and the approved probe monitors. No bind forces or drives a DUT net;
error injection is entirely at the boundary.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_binds.sv`, bound modules `gen_ibus_sva.sv`, `gen_dbus_sva.sv`,
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

## 4. Wave-level behaviour

SVAs sample on `posedge clk_i`, disabled while `!rst_ni`; they restate the C3 protocol rules
(request hold, one rvalid per grant, ordering, outstanding bounds, key pulse) for assertion
coverage.

## 5. Checkers

| Checker id | Rule | Mutation classes it catches (example locus) | Disable knob |
|---|---|---|---|
| `sva_ibus_hold / sva_dbus_hold / sva_rvalid_once / sva_scrkey_pulse` | SVA twins of the agent checkers (same rules) | same loci as the corresponding agent checker rows | `+gen_chk_sva_ibus_hold / sva_dbus_hold / sva_rvalid_once / sva_scrkey_pulse=0` |
| `sva_rvalid_legal` | TB stimulus legality: `instr_rvalid_i`/`data_rvalid_i` only while a grant is outstanding and never in the grant cycle (rtl-arch T-022 evidence 5.2) | TB self-check, not a DUT checker | `+gen_chk_sva_rvalid_legal=0` |
| `T022_NEVER_*` | rtl-arch exclusion-evidence never-taken properties (`gen_cover_props.sv`, promoted from `dv/auto_dv/work/rtl-arch/gen_cover_props_draft.sv`): a hit means the exclusion candidate is reachable; `assert ... else $error`, collected, reported by Runtime as an exclusion-evidence failure, fails the run until rtl-arch withdraws the exclusion | exclusion evidence, not a DUT checker; knob `+gen_chk_t022_never` (default on in every tier); `T022_COVER_*` are cover-only | `+gen_chk_T022_NEVER_*=0` |

## 6. Failure path and diagnostics

SVA failures are `uvm_error` through the `gen_sva_ctl_if` reporting hook (so the log scanner sees
one mechanism); assertion coverage counts toward the assertion metric.

## 7. Coverage hooks

Assertion coverage of the SVAs; `gen_*_cov` modules bound here sample signal-level groups.

## 8. At build

Add probe binds only with a probe-register row marked approved.
