# Component API: gen_mem_model (shared memory model, MMIO windows, image load)

Owner: tb-infra. Status: skeleton written before the code (T-031, 2026-09-03; regenerated for the v2 component sections after the Critic's review); items marked
"at build" are completed when the component lands (component SV opens after the TB architecture
review). Source: `dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md` C3.3; DV_prompt.txt deliverable 4 (TB architecture document,
component API documents). Conventions (shared by every component document): every runtime
knob is a plusarg whose name is a `parameter string` in `gen_tb_pkg` (column 2 below) and a
generated Python constant of the same value; every checker fails through `uvm_error` with its
id (or `uvm_fatal` where stated); `+gen_chk_<id>=0` disables exactly that checker,
`+gen_chk_all=0 +gen_chk_<id>=1` isolates one for mutation evidence (DV_prompt Section 8).

## 1. Purpose

One sparse word-addressed memory behind both bus agents, test equipment only. Loads the program
image, serves reads and byte-masked writes, sinks the MMIO windows (riscv-dv signature, interrupt
acknowledge, end-of-test). The image already holds the boot entry at `{boot_addr[31:8], 8'h80}`
and the `.debug_rom` section at DmHaltAddr (dv/auto_dv/stim/gen_riscv_dv_target/gen_link.ld), so
no separate boot stub or DmHaltAddr alias exists.

## 2. Files (planned) and how to call it

`dv/auto_dv/env/gen_mem_model.sv` (SV class, one instance in `gen_env`, handle in
`uvm_config_db` for both agents and the scoreboard). Image producer: `dv/auto_dv/stim/gen_program.py`
-> `prog.vmem` + `prog.sym.json` (format: `dv/auto_dv/stim/gen_elf2mem.py` docstring).

`load_vmem(path)` at time 0 ($readmemh into the sparse array), `crc32_index_word()` (IEEE CRC-32,
zlib polynomial, init 0xFFFFFFFF, final XOR, over the loaded words in ascending index order, each
fed as 8 little-endian bytes (index, word), exactly `gen_elf2mem.checksum()`, v2 XM-M3),
`verify_digest(crc32, count)` (mismatch = `uvm_fatal MEM_LOAD`), `read32(addr)` (also serves the
bridge's MEM_PEEK), `write_masked(addr, data, be)`,
`add_mmio(window, handler)`, `symbol(name)` from the sidecar (tohost, signature, entry).

## 3. Knobs

| Plusarg | gen_tb_pkg name | Meaning | Default |
|---|---|---|---|
| `+gen_mem_image=<path.vmem>` | `PLUSARG_MEM_IMAGE` | program image | required |
| `+gen_mem_image_crc32=<hex>` | `PLUSARG_MEM_IMAGE_CRC32` | CRC-32 over (index, word) pairs from the sidecar; recomputed by the model after load | required |
| `+gen_mem_readback_words=<n>` | `PLUSARG_MEM_READBACK_WORDS` | word addresses cocotb reads back through bridge MEM_PEEK commands (`cmd_arg[0]` = word address, answer in `peek_data`, edge-awaited; an SV class array is not VPI-visible, v2 XM-M4) and compares with the `.vmem` it parsed; Python `assert` on mismatch | GEN_MEM_READBACK_WORDS = 64 |
| `+gen_mem_image_words=<n>` | `PLUSARG_MEM_IMAGE_WORDS` | word count from the sidecar | required |
| `+gen_boot_addr=<hex>` | `PLUSARG_BOOT_ADDR` | boot_addr_i; must match the image's entry page (checked) | GEN_BOOT_ADDR_DEFAULT |
| `+gen_sig_addr=<hex>` | `PLUSARG_SIG_ADDR` | riscv-dv signature MMIO window base | gen_tb_pkg constant |
| `+gen_irq_ack_addr=<hex>` | `PLUSARG_IRQ_ACK_ADDR` | interrupt acknowledge register | gen_tb_pkg constant |
| `+gen_eot_addr=<hex>` | `PLUSARG_EOT_ADDR` | end-of-test register (in addition to the tohost symbol) | gen_tb_pkg constant |
| `+gen_mem_unmapped_ok=0|1` | `PLUSARG_MEM_UNMAPPED_OK` | unmapped access returns an error response instead of a TB error | 0 |

## 4. Wave-level behaviour

None of its own: reads and writes complete in the agents' response flops. Backdoor rule: the
image load is the only backdoor write and is verified twice: the SV CRC-32 digest (mismatch =
`uvm_fatal MEM_LOAD`) and a cocotb read-back of `GEN_MEM_READBACK_WORDS` word addresses drawn from
the image index set with the run seed and compared against the `.vmem` parsed by Python (mismatch =
Python `assert`, fails the cocotb test); every other change comes from bus stores.

## 5. Checkers

None: this component carries no pass/fail check (test equipment or infrastructure).

## 6. Failure path and diagnostics

`uvm_fatal MEM_LOAD` on image/digest mismatch or an unknown plusarg path; `uvm_fatal MEM_MMIO`
on a write to an MMIO window without a handler; `uvm_error MEM_UNMAPPED` (see knob).

## 7. Coverage hooks

Region hit counts (program, data, stacks, MMIO windows), first/last touched addresses (for
memory-map coverage in `gen_mem_cg`).

## 8. At build

Choose the MMIO window constants in gen_tb_pkg and the generated C header for the shim; decide N
for the sampled read-back; implement the digest exactly as gen_elf2mem.py defines it.
