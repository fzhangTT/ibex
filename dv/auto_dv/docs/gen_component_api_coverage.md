# Component API: gen_fcov_pkg and gen_*_cov (functional coverage implementation)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C7; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Implements the DV Lead's coverage plan: class-based covergroups sampled by the scoreboard and
monitors with transaction arguments, plus bound signal-level coverage modules; every group in an
isolated `gen_` namespace with per-test expectation manifests.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_fcov_pkg.sv` (all `gen_<feature>_cg`), `dv/auto_dv/tb/gen_*_cov.sv` (bound
via gen_binds.sv), manifests `dv/auto_dv/fcov_expectations/<test>.fcov.yaml`.

Sampling on monitor events only (RVFI record, bus grant/response, irq edge, alert pulse, regime
change), never on a free-running clock; each sampling condition is a named `gen_smp_<name>` event
reviewed for vacuity. Per-test verification with `ci/check_fcov_expectations.py --vdb <vdb>
--cm-name test_<test>_<seed>` keyed `<cg>.<cp>.<bin>`.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_fcov_en=0|1` | `PLUSARG_FCOV_EN` | instantiate covergroups (off for pure debug runs) | 1 |

## 4. Wave-level behaviour

None (sampling only).

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

None; the fcov-expectation checker fails the run on declared-but-unhit bins (exit 2) or protocol
error (exit 1).

## 7. Coverage hooks

Bins derive ranges from `ibex_pkg` parameters (`PMP_MAX_REGIONS`, `IC_*`, `$bits(irqs_t.irq_fast)`,
`MHPMCounterNum`); `gen_regime_cg` covers layer 3; `gen_csr_cg` carries the sweep-frequency and
write-to-read-gap bins of the CSR observability plan (A-19); no RTL covergroups exist to collide with.
Code-coverage scope is the DV Lead's recorded decision implemented in Runtime's gen_cm_hier.cfg (A-21),
not restated here.

## 8. At build

Implement each group from the approved coverage plan; anti-vacuity review per sampling event.
