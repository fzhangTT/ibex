// gen_rtl_filelist.f: RTL file set for gen_dut_top, hand-derived from the .core dependency
// graph (ibex_core.core -> ibex_pkg/ibex_icache/prim cores), per SIM_RECIPE.md section 2.
// Paths are relative to the repo root; run VCS from there.

+incdir+vendor/lowrisc_ip/ip/prim/rtl
+incdir+vendor/lowrisc_ip/dv/sv/dv_utils

// Packages (dependency order)
vendor/lowrisc_ip/ip/prim/rtl/prim_util_pkg.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_count_pkg.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_mubi_pkg.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_cipher_pkg.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_pkg.sv
rtl/ibex_pkg.sv
rtl/ibex_cheriot_pkg.sv

// prim modules (generic implementations for the abstract prims)
vendor/lowrisc_ip/ip/prim_generic/rtl/prim_buf.sv
vendor/lowrisc_ip/ip/prim_generic/rtl/prim_flop.sv
vendor/lowrisc_ip/ip/prim_generic/rtl/prim_clock_gating.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_lfsr.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_count.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_fifo_sync_cnt.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_fifo_sync.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_28_22_enc.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_28_22_dec.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_39_32_enc.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_39_32_dec.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_64_57_enc.sv
vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_64_57_dec.sv

// ibex core RTL (ibex_core.core files_rtl order) + icache + register file
rtl/ibex_cheriot_ex.sv
rtl/ibex_alu.sv
rtl/ibex_branch_predict.sv
rtl/ibex_compressed_decoder.sv
rtl/ibex_controller.sv
rtl/ibex_cs_registers.sv
rtl/ibex_csr.sv
rtl/ibex_counter.sv
rtl/ibex_decoder.sv
rtl/ibex_ex_block.sv
rtl/ibex_fetch_fifo.sv
rtl/ibex_id_stage.sv
rtl/ibex_if_stage.sv
rtl/ibex_load_store_unit.sv
rtl/ibex_multdiv_fast.sv
rtl/ibex_multdiv_slow.sv
rtl/ibex_prefetch_buffer.sv
rtl/ibex_pmp.sv
rtl/ibex_wb_stage.sv
rtl/ibex_dummy_instr.sv
rtl/ibex_icache.sv
rtl/ibex_register_file_ff.sv
rtl/ibex_core.sv
