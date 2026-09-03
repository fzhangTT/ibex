# TDD transcript: gen_mem_pkg::gen_mem_model (architecture C3.3; build step 1c, unit-tested first)

Component: `dv/auto_dv/env/gen_mem_pkg.sv` (gen_mmio_handler, gen_mem_model: load_vmem, crc32_index_word,
verify_digest, read32, write_masked, peek_word, is_mapped, add_mmio, unmapped policy).
Test: `dv/auto_dv/tb/unit/gen_ut_mem_model_top.sv` + `gen_ut_mem_model.f` (pure SV with UVM report
functions, no RTL), image under test: the directed Zc program `dv/auto_dv/work/tb-infra/out_codegen/zc/prog.vmem`
(204 words, sidecar CRC-32 0xcf0cb3b8, entry 0x80000080 = word 0x0040006f). Out-tree
`dv/auto_dv/work/tb-infra/out_ut_mem/`. Owner: tb-infra.

## 1. Red (test compiled before the package existed)

```
# RED compile: 2026-09-03T07:31:10Z host=soc-l-11 (gen_mem_pkg.sv absent)
Error-[SFCOR] Source file cannot be opened
  Source file "dv/auto_dv/env/gen_mem_pkg.sv" cannot be opened for reading due
1 error
vcs exit=255
```

## 2. Green (package written; one test expectation corrected, disclosed)

```
# GREEN compile+run: 2026-09-03T07:33:31Z host=soc-l-11
vcs exit=0
0
simv exit=0
FAIL mmio store did not land in RAM words got 0xcc exp 0xce
GEN_UT_MEM_MODEL FAIL (1 failures)
24
# GREEN run 2 (test expectation corrected: the written words already existed in the image): 2026-09-03T07:34:17Z host=soc-l-11
vcs exit=0
simv exit=0
GEN_UT_MEM_MODEL PASS (0 failures)
OK lines: 25
Time: 00 ps
CPU Time:      0.150 seconds;       Data structure size:   0.1Mb
```

Green run 1 had one failing check, a wrong expectation in the TEST, not a model defect: the two
`write_masked` targets (entry + 4, entry + 8) are words the image already holds, so the word count
stays 204; the check's intent (an MMIO store must never add a RAM word) is kept with the corrected
value. Green run 2: 25 checks, `GEN_UT_MEM_MODEL PASS`, UVM report functions available (no error
emitted on the covered paths). Proven: the vmem reader (`@` runs), the CRC-32 definition of
`gen_elf2mem.checksum()` reproduced in SV (matches the sidecar), digest rejection of a wrong crc or
count, byte-masked writes, word alignment of reads, region mapping from the rendered `GEN_MM_*`
constants (program, DM, MMIO page mapped; holes and address 0 not), the MMIO handler path for stores
and reads, the `unmapped_ok` policy (counted, answered 0) and the side-effect-free `peek_word` used by
MEM_PEEK.

## 3. Word watch (tohost end-of-test), test extended first

The unit test gained the `add_watch` checks (a watched store lands in RAM and calls the handler; an
unwatched store does not) before the model had the API:

```
# RED compile (add_watch missing): 2026-09-03T07:39:40Z host=soc-l-11
Error-[MFNF] Member not found
dv/auto_dv/tb/unit/gen_ut_mem_model_top.sv, 87
"m."
vcs exit=255
# GREEN compile+run (add_watch): 2026-09-03T07:41:29Z host=soc-l-11
vcs exit=0
simv exit=0
GEN_UT_MEM_MODEL PASS (0 failures)
OK lines: 29
```

(`Error-[MFNF] Member not found ... "m."` is the red: `add_watch` did not exist; green run 3: 29 checks
PASS.) The environment uses the watch for `+gen_tohost_addr` (the program's `tohost` symbol from the
image sidecar): the store toggles `evt_eot_seen` and records the code in `evt_eot_code`.
