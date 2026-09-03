# T-046: second Spike library link test (architecture C5.1 prerequisite, Critic A-16)

Spike: pinned upstream 4ffd6ba860f4190ceac2716fa3c2cf139e85538f built in `tools/spike`
(`gen_t019_spike_build.md`). Source: `dv/auto_dv/work/tb-infra/gen_spike_linktest2.cc`.
Log: `dv/auto_dv/work/tb-infra/out_linktest2/linktest2.log` (98 checks, 0 failures, exit 0:
97 in the seven cases below plus one setup check that `mtvec` keeps the vectored mode bit).

Build and run (clone root, `ci/env.sh` sourced):

```
g++ -std=c++2a -I tools/spike/include dv/auto_dv/work/tb-infra/gen_spike_linktest2.cc \
    -L tools/spike/lib -lriscv -Wl,-rpath,$PWD/tools/spike/lib \
    -o dv/auto_dv/work/tb-infra/out_linktest2/gen_spike_linktest2
dv/auto_dv/work/tb-infra/out_linktest2/gen_spike_linktest2
```

## Cases and verdicts (every check of a case is in the log; a case passes only if all its checks pass)

| # | Mechanism | Checks | Verdict | Result |
|---|---|---|---|---|
| 1 | `gen_mie_csr_t : mie_csr_t` overriding the private virtual `write_mask()` (Ibex set: MSIE, MTIE, MEIE, fast 16..30), installed in `state.mie` and `state.csrmap[CSR_MIE]` after `reset()` | 21 | PASS | `csrw mie` with bit 16 sticks; `put_csr(mie, 1<<31)` rejected. With `mip` bit 16 set by `backdoor_write_with_mask` and `mstatus.MIE`, `step(1)` retires 0 (minstret delta), pc = mtvec base + 16*4, mcause 0x80000010, mepc = interrupted pc, MIE cleared; next `step(1)` retires the handler's first instruction (1). Priority rounds: pending {16,17,ext} -> 16; {17,ext} -> 17; {ext} -> 11; pending {16} with mie {ext} only -> no entry, the instruction retires, mcause unchanged. Spike's default chain (processor.cc:258-262) equals Ibex's; no emulation |
| 2 | Custom CSRs via `extension_t::get_csrs` (extension `genibex`, ISA string `..._xgenibex`) | 9 | PASS | `csrw 0x7C0` retires without trap and reads back masked (0x1FF -> 0xFF); `0x7C1` reads 0; `csrr` lands in `log_reg_write`. Two facts for the shim: extension names cannot contain `_` (the ISA parser splits on it, disasm/isa_parser.cc:331-336: `xgen_ibex` failed as "unsupported extension: ibex"); the CSRs enter `csrmap` only in a `reset()` after construction (processor.cc:80-85 registers extensions after the constructor's reset; processor.cc:170-173 adds them), so `gen_isa_reset` calls `reset()` and installs `gen_mie_csr_t` afterwards |
| 3 | `wfi` | 4 | PASS | retires 1, `in_wfi` set, pc + 4; `clear_waiting_for_interrupt()` clears it |
| 4 | `halt_request = HR_REGULAR` then `step(1)` | 7 | PASS | retires 0, `debug_mode`, `dcsr.cause` 3 (DEBUGINT), `dcsr.prv` M, `dpc` = halted pc; the step then fetches Spike's ROM entry 0x800, unbacked here, and the fetch fault inside debug mode parks pc at DEBUG_ROM_TVEC 0x808 with mcause untouched. The shim overrides pc to DmHaltAddr and must clear `halt_request` itself (`enter_debug_mode` is private, processor.h:409) |
| 5 | tdata1 write from debug mode, dret, execute trigger | 29 | PASS | from debug mode `csrw tdata1` keeps type 2, dmode, action 1 (0x28001044) and tdata2; `dret` retires 1, leaves debug mode, pc = dpc; nops retire until pc = tdata2; that step retires 0 with `dcsr.cause` 2 (HWBP), dpc = trigger address; after `dret` it re-fires until tdata2 is changed |
| 6 | `cm.push {ra}, -16` (0xB842, Zcmp) | 7 | PASS | retires 1, sp - 16, ra stored at sp_old - 4, exactly one `log_mem_write` entry (addr sp_old - 4, size 4), pc + 2 |
| 7 | `mmio_store` semantics (`addr_to_mem` NULL outside RAM) | 20 | PASS | aligned unbacked `sw`: ONE call, len 4, store access fault, mtval = EA. Misaligned `sw` to an unbacked address: `mmu_t::mmio` (mmu.cc:168-184) splits into byte calls, the first fails -> one call len 1, mtval = original EA. Misaligned `sw` across a permitted word and a denied word: 3 byte calls (2 performed, the third at the aligned second word fails), mtval = ORIGINAL EA (Ibex MEM-13 wants the aligned second word for a second-half fault); `put_csr(CSR_MTVAL, aligned)` accepted, so the shim overrides mtval after the step from its own record of the failing byte |

## Architecture consequences (folded into the v2 sections, the isa_shim skeleton and the response file)

- C5.4 / A-15: the "one full-length call" statement holds only for naturally aligned accesses; the
  per-word rule is implemented per byte, and second-word faults need the mtval override.
- C5.2 step table: debug entry = one step retiring 0 with the pc parked at DEBUG_ROM_TVEC, then
  the shim's pc override to DmHaltAddr and `halt_request` clear, then the ROM's first instruction.
- C5.1: `gen_isa_reset` = construct once, `reset()`, install `gen_mie_csr_t`, `enable_log_commits`;
  extension name `genibex`.
- Still owed before shim coding: grevi/gorci non-alias decode check (R-2 of the skeleton).
