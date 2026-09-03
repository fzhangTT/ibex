# Component API: gen_irq_agent (interrupt driver)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.6; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

Drives `irq_software_i`, `irq_timer_i`, `irq_external_i`, `irq_fast_i[14:0]` and `irq_nm_i`
as levels with randomized timing and hold policies; the source of every interrupt stimulus.

## 2. Files (planned) and how to call it

`dv/auto_dv/tb/gen_irq_if.sv`, `dv/auto_dv/env/gen_irq_pkg.sv` (`gen_irq_cfg`, `gen_irq_item`
{line mask (`$bits(ibex_pkg::irqs_t)` bits: `$bits(irqs_t.irq_fast)` fast + ext + sw + timer), nmi, assert_delay, hold_policy = CYCLES(n) | UNTIL_ACK |
UNTIL_TAKEN | STICKY, release_delay}, driver, monitor, sequencer, agent).

Items come from the bridge (IRQ_SET, IRQ_CLR, NMI_PULSE) or from regime-driven random
sequences; every line edge is published on `ap` with its cycle for gen_irq_checker.

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_irq_regime=quiet|sparse|storm|nested|nmi_mix` | `PLUSARG_IRQ_REGIME` | distribution set for random interrupt traffic | quiet |
| `+gen_irq_min_gap=<n>` | `PLUSARG_IRQ_MIN_GAP` | minimum cycles between random assertions | 50 |
| `+gen_irq_hold_min/max=<n>` | `PLUSARG_IRQ_HOLD_MIN/MAX` | hold length for CYCLES policy | 1 / 200 |
| `+gen_irq_ack_addr=<hex>` | `PLUSARG_IRQ_ACK_ADDR` | shared with gen_mem_model: handler store that releases UNTIL_ACK lines | gen_tb_pkg constant |

## 4. Wave-level behaviour

Lines change on the clock edge after the command. UNTIL_ACK releases the line the cycle after
the handler's store to the ack register (riscv-dv handler tail through the user-extension
`gen_plic_section`, planned); UNTIL_TAKEN releases after `rvfi_intr` of the matching cause;
a one-cycle pulse is a deliberate "may be missed" stimulus; STICKY leaves the line asserted so
software must mask it. Ibex's `mip` is read-only, so a riscv-dv `csrw mip` does not clear a level.

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

No checker in the agent (gen_irq_checker owns them). `uvm_fatal IRQ_ITEM` on an item with an
empty line mask and no nmi. Debug behind `+gen_dbg_irq=1`.

## 7. Coverage hooks

`gen_irq_cg`: lines asserted (single, multiple, fast ids), hold policies, arrival relative to
pipeline state (crosses sampled in the scoreboard), NMI during handler, interrupts in debug mode.

## 8. At build

Write the user-extension `gen_plic_section` ack store; decide the ack register protocol (write
value = cause id).
