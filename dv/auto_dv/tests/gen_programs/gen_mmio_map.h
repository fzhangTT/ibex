# gen_mmio_map.h: TB MMIO register addresses for directed test programs, rendered from
# dv/auto_dv/gen_tb/gen_knobs.py MEMORY_MAP (one origin: gen_tb_knobs.yaml); gen_test_lib --self-test
# fails when this file drifts from the rendered map. Include with .include "gen_mmio_map.h"
# (gen_program.py extra arg --gcc-opts=-Idv/auto_dv/tests/gen_programs).
.set GEN_MM_SIG_ADDR, 0x8ffff000
.set GEN_MM_IRQ_ACK_ADDR, 0x8ffff100
.set GEN_MM_EOT_ADDR, 0x8ffff104
.set GEN_MM_PHASE_MARK_ADDR, 0x8ffff108
.set GEN_MM_DM_HALT, 0x1a110800
.set GEN_MM_DM_EXCEPTION, 0x1a110808
