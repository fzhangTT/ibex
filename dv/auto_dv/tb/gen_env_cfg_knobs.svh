// Rendered by dv/auto_dv/tb/gen_knobs_codegen.py from dv/auto_dv/tb/gen_tb_knobs.yaml; do not edit.
// Included inside class gen_env_cfg (dv/auto_dv/env/gen_env_pkg.sv): fields, parse_plusargs(),
// validate(), pinned_count(). Types: string/enum -> string, int -> int unsigned, hex -> logic [31:0],
// bool -> bit. `<name>_set` records that the plusarg was supplied (pinning, optional knobs).

  string build_config = "opentitan";
  bit build_config_set = 1'b0;
  int unsigned smoke_cycles = 3000;
  bit smoke_cycles_set = 1'b0;
  int unsigned smoke_intg_flip = 0;
  bit smoke_intg_flip_set = 1'b0;
  bit dbg_csr_probe = 1'b0;
  string mem_image = "";
  bit mem_image_set = 1'b0;
  logic [31:0] mem_image_crc32 = 32'h0;
  bit mem_image_crc32_set = 1'b0;
  int unsigned mem_image_words = 0;
  bit mem_image_words_set = 1'b0;
  int unsigned mem_readback_words = 64;
  bit mem_readback_words_set = 1'b0;
  logic [31:0] tohost_addr = 32'h0;
  bit tohost_addr_set = 1'b0;
  bit mem_unmapped_ok = 1'b0;
  logic [31:0] boot_addr = 32'h80000000;
  bit boot_addr_set = 1'b0;
  int unsigned alive_timeout = 100000;
  bit alive_timeout_set = 1'b0;
  int unsigned finish_timeout = 20000;
  bit finish_timeout_set = 1'b0;
  string regime_sched = "";
  bit regime_sched_set = 1'b0;
  bit rvfi_trace = 1'b0;
  bit fcov_en = 1'b1;
  string icram_init = "random";
  bit icram_init_set = 1'b0;
  bit fetch_en_at_reset = 1'b1;
  bit key_reset_valid = 1'b1;
  string isa_string = "";
  bit isa_string_set = 1'b0;
  string isa_log = "";
  bit isa_log_set = 1'b0;
  int unsigned ut_boot_retire = 200;
  bit ut_boot_retire_set = 1'b0;
  int unsigned ibus_gnt_min = 0;
  bit ibus_gnt_min_set = 1'b0;
  int unsigned ibus_gnt_max = 0;
  bit ibus_gnt_max_set = 1'b0;
  int unsigned ibus_rvalid_min = 0;
  bit ibus_rvalid_min_set = 1'b0;
  int unsigned ibus_rvalid_max = 0;
  bit ibus_rvalid_max_set = 1'b0;
  int unsigned ibus_max_outstanding = 0;
  bit ibus_max_outstanding_set = 1'b0;
  int unsigned ibus_err_rate = 0;
  bit ibus_err_rate_set = 1'b0;
  int unsigned ibus_intg_err_rate = 0;
  bit ibus_intg_err_rate_set = 1'b0;
  int unsigned ibus_intg_bits = 1;
  bit ibus_intg_bits_set = 1'b0;
  string ibus_err_window = "";
  bit ibus_err_window_set = 1'b0;
  int unsigned dbus_gnt_min = 0;
  bit dbus_gnt_min_set = 1'b0;
  int unsigned dbus_gnt_max = 0;
  bit dbus_gnt_max_set = 1'b0;
  int unsigned dbus_rvalid_min = 0;
  bit dbus_rvalid_min_set = 1'b0;
  int unsigned dbus_rvalid_max = 0;
  bit dbus_rvalid_max_set = 1'b0;
  int unsigned dbus_max_outstanding = 0;
  bit dbus_max_outstanding_set = 1'b0;
  int unsigned dbus_err_rate = 0;
  bit dbus_err_rate_set = 1'b0;
  int unsigned dbus_intg_err_rate = 0;
  bit dbus_intg_err_rate_set = 1'b0;
  int unsigned dbus_intg_bits = 1;
  bit dbus_intg_bits_set = 1'b0;
  string dbus_err_window = "";
  bit dbus_err_window_set = 1'b0;
  string dbus_err_half = "any";
  bit dbus_err_half_set = 1'b0;
  bit dbus_err_store_perform = 1'b1;
  int unsigned key_delay_min = 1;
  bit key_delay_min_set = 1'b0;
  int unsigned key_delay_max = 20;
  bit key_delay_max_set = 1'b0;
  int unsigned key_never_cycles = 0;
  bit key_never_cycles_set = 1'b0;
  int unsigned irq_min_gap = 0;
  bit irq_min_gap_set = 1'b0;
  int unsigned irq_hold_min = 1;
  bit irq_hold_min_set = 1'b0;
  int unsigned irq_hold_max = 50;
  bit irq_hold_max_set = 1'b0;
  int unsigned dbg_hold_min = 1;
  bit dbg_hold_min_set = 1'b0;
  int unsigned dbg_hold_max = 50;
  bit dbg_hold_max_set = 1'b0;
  string knob_imem_gnt_delay = "short";
  bit knob_imem_gnt_delay_set = 1'b0;
  string knob_imem_rvalid_delay = "short";
  bit knob_imem_rvalid_delay_set = 1'b0;
  string knob_imem_err_rate = "none";
  bit knob_imem_err_rate_set = 1'b0;
  string knob_imem_intg_err_rate = "none";
  bit knob_imem_intg_err_rate_set = 1'b0;
  string knob_imem_outstanding_cap = "cap8";
  bit knob_imem_outstanding_cap_set = 1'b0;
  string knob_dmem_gnt_delay = "short";
  bit knob_dmem_gnt_delay_set = 1'b0;
  string knob_dmem_rvalid_delay = "short";
  bit knob_dmem_rvalid_delay_set = 1'b0;
  string knob_dmem_err_rate = "none";
  bit knob_dmem_err_rate_set = 1'b0;
  string knob_dmem_intg_err_rate = "none";
  bit knob_dmem_intg_err_rate_set = 1'b0;
  string knob_irq_regime = "quiet";
  bit knob_irq_regime_set = 1'b0;
  string knob_irq_line_mix = "single";
  bit knob_irq_line_mix_set = 1'b0;
  string knob_irq_hold = "until_taken";
  bit knob_irq_hold_set = 1'b0;
  string knob_debug_req_regime = "none";
  bit knob_debug_req_regime_set = 1'b0;
  string knob_scr_key_delay = "immediate";
  bit knob_scr_key_delay_set = 1'b0;
  string knob_icache_ecc_err_rate = "none";
  bit knob_icache_ecc_err_rate_set = 1'b0;
  string knob_fetch_enable_regime = "always_on";
  bit knob_fetch_enable_regime_set = 1'b0;
  string knob_mcounteren_writable = "on";
  bit knob_mcounteren_writable_set = 1'b0;
  string knob_instr_mix = "mixed";
  bit knob_instr_mix_set = 1'b0;
  string knob_priv_regime = "m_only";
  bit knob_priv_regime_set = 1'b0;
  string knob_pmp_regime = "off";
  bit knob_pmp_regime_set = 1'b0;
  bit chk_all = 1'b1;
  bit chk_ibus_proto = 1'b1;
  bit chk_ibus_outstanding = 1'b1;
  bit chk_sva_rvalid_legal = 1'b1;
  bit chk_dbus_proto = 1'b1;
  bit chk_dbus_outstanding = 1'b1;
  bit chk_dbus_split = 1'b1;
  bit chk_dbus_store_intg = 1'b1;
  bit chk_icram_write_ecc = 1'b1;
  bit chk_icram_inval_sweep = 1'b1;
  bit chk_icram_ecc_response = 1'b1;
  bit chk_scrkey_proto = 1'b1;
  bit chk_alert_minor = 1'b1;
  bit chk_alert_bus = 1'b1;
  bit chk_alert_internal = 1'b1;
  bit chk_crash_dump = 1'b1;
  bit chk_double_fault = 1'b1;
  bit chk_core_busy = 1'b1;
  bit chk_data_tag_quiet = 1'b1;
  bit chk_fetch_en = 1'b1;
  bit chk_irq_pending = 1'b1;
  bit chk_irq_entry = 1'b1;
  bit chk_irq_masked = 1'b1;
  bit chk_nmi_entry = 1'b1;
  bit chk_nmi_internal = 1'b1;
  bit chk_dbg_entry = 1'b1;
  bit chk_dbg_exc = 1'b1;
  bit chk_dbg_masked = 1'b1;
  bit chk_dbg_dret = 1'b1;
  bit chk_dbg_trigger = 1'b1;
  bit chk_ctr_mcycle = 1'b1;
  bit chk_ctr_minstret = 1'b1;
  bit chk_ctr_hpm_exact = 1'b1;
  bit chk_ctr_hpm_bound = 1'b1;
  bit chk_pmp_data = 1'b1;
  bit chk_pmp_fetch = 1'b1;
  bit chk_isa = 1'b1;
  bit chk_isa_pc = 1'b1;
  bit chk_isa_insn = 1'b1;
  bit chk_isa_trap = 1'b1;
  bit chk_isa_rd = 1'b1;
  bit chk_isa_mem = 1'b1;
  bit chk_isa_prv = 1'b1;
  bit chk_isa_pc_next = 1'b1;
  bit chk_isa_csr = 1'b1;
  bit chk_rvfi_proto = 1'b1;
  bit chk_t022_never = 1'b1;
  bit chk_bridge_accounting = 1'b1;

  function void parse_plusargs();
    string s; int unsigned u; logic [31:0] h;
    if ($value$plusargs({PLUSARG_BUILD_CONFIG, "=%s"}, s)) begin build_config = s; build_config_set = 1'b1; end
    if ($value$plusargs({PLUSARG_SMOKE_CYCLES, "=%d"}, u)) begin smoke_cycles = u; smoke_cycles_set = 1'b1; end
    if ($value$plusargs({PLUSARG_SMOKE_INTG_FLIP, "=%d"}, u)) begin smoke_intg_flip = u; smoke_intg_flip_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBG_CSR_PROBE, "=%d"}, u)) dbg_csr_probe = (u != 0);
    if ($value$plusargs({PLUSARG_MEM_IMAGE, "=%s"}, s)) begin mem_image = s; mem_image_set = 1'b1; end
    if ($value$plusargs({PLUSARG_MEM_IMAGE_CRC32, "=%h"}, h)) begin mem_image_crc32 = h; mem_image_crc32_set = 1'b1; end
    if ($value$plusargs({PLUSARG_MEM_IMAGE_WORDS, "=%d"}, u)) begin mem_image_words = u; mem_image_words_set = 1'b1; end
    if ($value$plusargs({PLUSARG_MEM_READBACK_WORDS, "=%d"}, u)) begin mem_readback_words = u; mem_readback_words_set = 1'b1; end
    if ($value$plusargs({PLUSARG_TOHOST_ADDR, "=%h"}, h)) begin tohost_addr = h; tohost_addr_set = 1'b1; end
    if ($value$plusargs({PLUSARG_MEM_UNMAPPED_OK, "=%d"}, u)) mem_unmapped_ok = (u != 0);
    if ($value$plusargs({PLUSARG_BOOT_ADDR, "=%h"}, h)) begin boot_addr = h; boot_addr_set = 1'b1; end
    if ($value$plusargs({PLUSARG_ALIVE_TIMEOUT, "=%d"}, u)) begin alive_timeout = u; alive_timeout_set = 1'b1; end
    if ($value$plusargs({PLUSARG_FINISH_TIMEOUT, "=%d"}, u)) begin finish_timeout = u; finish_timeout_set = 1'b1; end
    if ($value$plusargs({PLUSARG_REGIME_SCHED, "=%s"}, s)) begin regime_sched = s; regime_sched_set = 1'b1; end
    if ($value$plusargs({PLUSARG_RVFI_TRACE, "=%d"}, u)) rvfi_trace = (u != 0);
    if ($value$plusargs({PLUSARG_FCOV_EN, "=%d"}, u)) fcov_en = (u != 0);
    if ($value$plusargs({PLUSARG_ICRAM_INIT, "=%s"}, s)) begin icram_init = s; icram_init_set = 1'b1; end
    if ($value$plusargs({PLUSARG_FETCH_EN_AT_RESET, "=%d"}, u)) fetch_en_at_reset = (u != 0);
    if ($value$plusargs({PLUSARG_KEY_RESET_VALID, "=%d"}, u)) key_reset_valid = (u != 0);
    if ($value$plusargs({PLUSARG_ISA_STRING, "=%s"}, s)) begin isa_string = s; isa_string_set = 1'b1; end
    if ($value$plusargs({PLUSARG_ISA_LOG, "=%s"}, s)) begin isa_log = s; isa_log_set = 1'b1; end
    if ($value$plusargs({PLUSARG_UT_BOOT_RETIRE, "=%d"}, u)) begin ut_boot_retire = u; ut_boot_retire_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_GNT_MIN, "=%d"}, u)) begin ibus_gnt_min = u; ibus_gnt_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_GNT_MAX, "=%d"}, u)) begin ibus_gnt_max = u; ibus_gnt_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_RVALID_MIN, "=%d"}, u)) begin ibus_rvalid_min = u; ibus_rvalid_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_RVALID_MAX, "=%d"}, u)) begin ibus_rvalid_max = u; ibus_rvalid_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_MAX_OUTSTANDING, "=%d"}, u)) begin ibus_max_outstanding = u; ibus_max_outstanding_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_ERR_RATE, "=%d"}, u)) begin ibus_err_rate = u; ibus_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_INTG_ERR_RATE, "=%d"}, u)) begin ibus_intg_err_rate = u; ibus_intg_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_INTG_BITS, "=%d"}, u)) begin ibus_intg_bits = u; ibus_intg_bits_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IBUS_ERR_WINDOW, "=%s"}, s)) begin ibus_err_window = s; ibus_err_window_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_GNT_MIN, "=%d"}, u)) begin dbus_gnt_min = u; dbus_gnt_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_GNT_MAX, "=%d"}, u)) begin dbus_gnt_max = u; dbus_gnt_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_RVALID_MIN, "=%d"}, u)) begin dbus_rvalid_min = u; dbus_rvalid_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_RVALID_MAX, "=%d"}, u)) begin dbus_rvalid_max = u; dbus_rvalid_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_MAX_OUTSTANDING, "=%d"}, u)) begin dbus_max_outstanding = u; dbus_max_outstanding_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_ERR_RATE, "=%d"}, u)) begin dbus_err_rate = u; dbus_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_INTG_ERR_RATE, "=%d"}, u)) begin dbus_intg_err_rate = u; dbus_intg_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_INTG_BITS, "=%d"}, u)) begin dbus_intg_bits = u; dbus_intg_bits_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_ERR_WINDOW, "=%s"}, s)) begin dbus_err_window = s; dbus_err_window_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_ERR_HALF, "=%s"}, s)) begin dbus_err_half = s; dbus_err_half_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBUS_ERR_STORE_PERFORM, "=%d"}, u)) dbus_err_store_perform = (u != 0);
    if ($value$plusargs({PLUSARG_KEY_DELAY_MIN, "=%d"}, u)) begin key_delay_min = u; key_delay_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KEY_DELAY_MAX, "=%d"}, u)) begin key_delay_max = u; key_delay_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KEY_NEVER_CYCLES, "=%d"}, u)) begin key_never_cycles = u; key_never_cycles_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IRQ_MIN_GAP, "=%d"}, u)) begin irq_min_gap = u; irq_min_gap_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IRQ_HOLD_MIN, "=%d"}, u)) begin irq_hold_min = u; irq_hold_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_IRQ_HOLD_MAX, "=%d"}, u)) begin irq_hold_max = u; irq_hold_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBG_HOLD_MIN, "=%d"}, u)) begin dbg_hold_min = u; dbg_hold_min_set = 1'b1; end
    if ($value$plusargs({PLUSARG_DBG_HOLD_MAX, "=%d"}, u)) begin dbg_hold_max = u; dbg_hold_max_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IMEM_GNT_DELAY, "=%s"}, s)) begin knob_imem_gnt_delay = s; knob_imem_gnt_delay_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IMEM_RVALID_DELAY, "=%s"}, s)) begin knob_imem_rvalid_delay = s; knob_imem_rvalid_delay_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IMEM_ERR_RATE, "=%s"}, s)) begin knob_imem_err_rate = s; knob_imem_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IMEM_INTG_ERR_RATE, "=%s"}, s)) begin knob_imem_intg_err_rate = s; knob_imem_intg_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IMEM_OUTSTANDING_CAP, "=%s"}, s)) begin knob_imem_outstanding_cap = s; knob_imem_outstanding_cap_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_DMEM_GNT_DELAY, "=%s"}, s)) begin knob_dmem_gnt_delay = s; knob_dmem_gnt_delay_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_DMEM_RVALID_DELAY, "=%s"}, s)) begin knob_dmem_rvalid_delay = s; knob_dmem_rvalid_delay_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_DMEM_ERR_RATE, "=%s"}, s)) begin knob_dmem_err_rate = s; knob_dmem_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_DMEM_INTG_ERR_RATE, "=%s"}, s)) begin knob_dmem_intg_err_rate = s; knob_dmem_intg_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IRQ_REGIME, "=%s"}, s)) begin knob_irq_regime = s; knob_irq_regime_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IRQ_LINE_MIX, "=%s"}, s)) begin knob_irq_line_mix = s; knob_irq_line_mix_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_IRQ_HOLD, "=%s"}, s)) begin knob_irq_hold = s; knob_irq_hold_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_DEBUG_REQ_REGIME, "=%s"}, s)) begin knob_debug_req_regime = s; knob_debug_req_regime_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_SCR_KEY_DELAY, "=%s"}, s)) begin knob_scr_key_delay = s; knob_scr_key_delay_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_ICACHE_ECC_ERR_RATE, "=%s"}, s)) begin knob_icache_ecc_err_rate = s; knob_icache_ecc_err_rate_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_FETCH_ENABLE_REGIME, "=%s"}, s)) begin knob_fetch_enable_regime = s; knob_fetch_enable_regime_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_MCOUNTEREN_WRITABLE, "=%s"}, s)) begin knob_mcounteren_writable = s; knob_mcounteren_writable_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_INSTR_MIX, "=%s"}, s)) begin knob_instr_mix = s; knob_instr_mix_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_PRIV_REGIME, "=%s"}, s)) begin knob_priv_regime = s; knob_priv_regime_set = 1'b1; end
    if ($value$plusargs({PLUSARG_KNOB_PMP_REGIME, "=%s"}, s)) begin knob_pmp_regime = s; knob_pmp_regime_set = 1'b1; end
    if ($value$plusargs({PLUSARG_CHK_ALL, "=%d"}, u)) chk_all = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_IBUS_PROTO, "=%d"}, u)) chk_ibus_proto = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_IBUS_OUTSTANDING, "=%d"}, u)) chk_ibus_outstanding = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_SVA_RVALID_LEGAL, "=%d"}, u)) chk_sva_rvalid_legal = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBUS_PROTO, "=%d"}, u)) chk_dbus_proto = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBUS_OUTSTANDING, "=%d"}, u)) chk_dbus_outstanding = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBUS_SPLIT, "=%d"}, u)) chk_dbus_split = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBUS_STORE_INTG, "=%d"}, u)) chk_dbus_store_intg = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ICRAM_WRITE_ECC, "=%d"}, u)) chk_icram_write_ecc = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ICRAM_INVAL_SWEEP, "=%d"}, u)) chk_icram_inval_sweep = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ICRAM_ECC_RESPONSE, "=%d"}, u)) chk_icram_ecc_response = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_SCRKEY_PROTO, "=%d"}, u)) chk_scrkey_proto = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ALERT_MINOR, "=%d"}, u)) chk_alert_minor = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ALERT_BUS, "=%d"}, u)) chk_alert_bus = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ALERT_INTERNAL, "=%d"}, u)) chk_alert_internal = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CRASH_DUMP, "=%d"}, u)) chk_crash_dump = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DOUBLE_FAULT, "=%d"}, u)) chk_double_fault = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CORE_BUSY, "=%d"}, u)) chk_core_busy = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DATA_TAG_QUIET, "=%d"}, u)) chk_data_tag_quiet = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_FETCH_EN, "=%d"}, u)) chk_fetch_en = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_IRQ_PENDING, "=%d"}, u)) chk_irq_pending = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_IRQ_ENTRY, "=%d"}, u)) chk_irq_entry = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_IRQ_MASKED, "=%d"}, u)) chk_irq_masked = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_NMI_ENTRY, "=%d"}, u)) chk_nmi_entry = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_NMI_INTERNAL, "=%d"}, u)) chk_nmi_internal = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBG_ENTRY, "=%d"}, u)) chk_dbg_entry = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBG_EXC, "=%d"}, u)) chk_dbg_exc = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBG_MASKED, "=%d"}, u)) chk_dbg_masked = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBG_DRET, "=%d"}, u)) chk_dbg_dret = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_DBG_TRIGGER, "=%d"}, u)) chk_dbg_trigger = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CTR_MCYCLE, "=%d"}, u)) chk_ctr_mcycle = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CTR_MINSTRET, "=%d"}, u)) chk_ctr_minstret = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CTR_HPM_EXACT, "=%d"}, u)) chk_ctr_hpm_exact = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_CTR_HPM_BOUND, "=%d"}, u)) chk_ctr_hpm_bound = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_PMP_DATA, "=%d"}, u)) chk_pmp_data = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_PMP_FETCH, "=%d"}, u)) chk_pmp_fetch = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA, "=%d"}, u)) chk_isa = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_PC, "=%d"}, u)) chk_isa_pc = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_INSN, "=%d"}, u)) chk_isa_insn = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_TRAP, "=%d"}, u)) chk_isa_trap = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_RD, "=%d"}, u)) chk_isa_rd = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_MEM, "=%d"}, u)) chk_isa_mem = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_PRV, "=%d"}, u)) chk_isa_prv = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_PC_NEXT, "=%d"}, u)) chk_isa_pc_next = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_ISA_CSR, "=%d"}, u)) chk_isa_csr = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_RVFI_PROTO, "=%d"}, u)) chk_rvfi_proto = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_T022_NEVER, "=%d"}, u)) chk_t022_never = (u != 0);
    if ($value$plusargs({PLUSARG_CHK_BRIDGE_ACCOUNTING, "=%d"}, u)) chk_bridge_accounting = (u != 0);
  endfunction

  // Enumerated knobs must hold one of their yaml values; msg names the first offender.
  function bit validate(output string msg);
    if (!gen_str_in_csv(icram_init, GEN_ENUM_ICRAM_INIT_VALUES)) begin msg = {"+", PLUSARG_ICRAM_INIT, "=", icram_init, " not in ", GEN_ENUM_ICRAM_INIT_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(dbus_err_half, GEN_ENUM_DBUS_ERR_HALF_VALUES)) begin msg = {"+", PLUSARG_DBUS_ERR_HALF, "=", dbus_err_half, " not in ", GEN_ENUM_DBUS_ERR_HALF_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_imem_gnt_delay, GEN_ENUM_KNOB_IMEM_GNT_DELAY_VALUES)) begin msg = {"+", PLUSARG_KNOB_IMEM_GNT_DELAY, "=", knob_imem_gnt_delay, " not in ", GEN_ENUM_KNOB_IMEM_GNT_DELAY_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_imem_rvalid_delay, GEN_ENUM_KNOB_IMEM_RVALID_DELAY_VALUES)) begin msg = {"+", PLUSARG_KNOB_IMEM_RVALID_DELAY, "=", knob_imem_rvalid_delay, " not in ", GEN_ENUM_KNOB_IMEM_RVALID_DELAY_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_imem_err_rate, GEN_ENUM_KNOB_IMEM_ERR_RATE_VALUES)) begin msg = {"+", PLUSARG_KNOB_IMEM_ERR_RATE, "=", knob_imem_err_rate, " not in ", GEN_ENUM_KNOB_IMEM_ERR_RATE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_imem_intg_err_rate, GEN_ENUM_KNOB_IMEM_INTG_ERR_RATE_VALUES)) begin msg = {"+", PLUSARG_KNOB_IMEM_INTG_ERR_RATE, "=", knob_imem_intg_err_rate, " not in ", GEN_ENUM_KNOB_IMEM_INTG_ERR_RATE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_imem_outstanding_cap, GEN_ENUM_KNOB_IMEM_OUTSTANDING_CAP_VALUES)) begin msg = {"+", PLUSARG_KNOB_IMEM_OUTSTANDING_CAP, "=", knob_imem_outstanding_cap, " not in ", GEN_ENUM_KNOB_IMEM_OUTSTANDING_CAP_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_dmem_gnt_delay, GEN_ENUM_KNOB_DMEM_GNT_DELAY_VALUES)) begin msg = {"+", PLUSARG_KNOB_DMEM_GNT_DELAY, "=", knob_dmem_gnt_delay, " not in ", GEN_ENUM_KNOB_DMEM_GNT_DELAY_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_dmem_rvalid_delay, GEN_ENUM_KNOB_DMEM_RVALID_DELAY_VALUES)) begin msg = {"+", PLUSARG_KNOB_DMEM_RVALID_DELAY, "=", knob_dmem_rvalid_delay, " not in ", GEN_ENUM_KNOB_DMEM_RVALID_DELAY_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_dmem_err_rate, GEN_ENUM_KNOB_DMEM_ERR_RATE_VALUES)) begin msg = {"+", PLUSARG_KNOB_DMEM_ERR_RATE, "=", knob_dmem_err_rate, " not in ", GEN_ENUM_KNOB_DMEM_ERR_RATE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_dmem_intg_err_rate, GEN_ENUM_KNOB_DMEM_INTG_ERR_RATE_VALUES)) begin msg = {"+", PLUSARG_KNOB_DMEM_INTG_ERR_RATE, "=", knob_dmem_intg_err_rate, " not in ", GEN_ENUM_KNOB_DMEM_INTG_ERR_RATE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_irq_regime, GEN_ENUM_KNOB_IRQ_REGIME_VALUES)) begin msg = {"+", PLUSARG_KNOB_IRQ_REGIME, "=", knob_irq_regime, " not in ", GEN_ENUM_KNOB_IRQ_REGIME_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_irq_line_mix, GEN_ENUM_KNOB_IRQ_LINE_MIX_VALUES)) begin msg = {"+", PLUSARG_KNOB_IRQ_LINE_MIX, "=", knob_irq_line_mix, " not in ", GEN_ENUM_KNOB_IRQ_LINE_MIX_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_irq_hold, GEN_ENUM_KNOB_IRQ_HOLD_VALUES)) begin msg = {"+", PLUSARG_KNOB_IRQ_HOLD, "=", knob_irq_hold, " not in ", GEN_ENUM_KNOB_IRQ_HOLD_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_debug_req_regime, GEN_ENUM_KNOB_DEBUG_REQ_REGIME_VALUES)) begin msg = {"+", PLUSARG_KNOB_DEBUG_REQ_REGIME, "=", knob_debug_req_regime, " not in ", GEN_ENUM_KNOB_DEBUG_REQ_REGIME_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_scr_key_delay, GEN_ENUM_KNOB_SCR_KEY_DELAY_VALUES)) begin msg = {"+", PLUSARG_KNOB_SCR_KEY_DELAY, "=", knob_scr_key_delay, " not in ", GEN_ENUM_KNOB_SCR_KEY_DELAY_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_icache_ecc_err_rate, GEN_ENUM_KNOB_ICACHE_ECC_ERR_RATE_VALUES)) begin msg = {"+", PLUSARG_KNOB_ICACHE_ECC_ERR_RATE, "=", knob_icache_ecc_err_rate, " not in ", GEN_ENUM_KNOB_ICACHE_ECC_ERR_RATE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_fetch_enable_regime, GEN_ENUM_KNOB_FETCH_ENABLE_REGIME_VALUES)) begin msg = {"+", PLUSARG_KNOB_FETCH_ENABLE_REGIME, "=", knob_fetch_enable_regime, " not in ", GEN_ENUM_KNOB_FETCH_ENABLE_REGIME_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_mcounteren_writable, GEN_ENUM_KNOB_MCOUNTEREN_WRITABLE_VALUES)) begin msg = {"+", PLUSARG_KNOB_MCOUNTEREN_WRITABLE, "=", knob_mcounteren_writable, " not in ", GEN_ENUM_KNOB_MCOUNTEREN_WRITABLE_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_instr_mix, GEN_ENUM_KNOB_INSTR_MIX_VALUES)) begin msg = {"+", PLUSARG_KNOB_INSTR_MIX, "=", knob_instr_mix, " not in ", GEN_ENUM_KNOB_INSTR_MIX_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_priv_regime, GEN_ENUM_KNOB_PRIV_REGIME_VALUES)) begin msg = {"+", PLUSARG_KNOB_PRIV_REGIME, "=", knob_priv_regime, " not in ", GEN_ENUM_KNOB_PRIV_REGIME_VALUES}; return 1'b0; end
    if (!gen_str_in_csv(knob_pmp_regime, GEN_ENUM_KNOB_PMP_REGIME_VALUES)) begin msg = {"+", PLUSARG_KNOB_PMP_REGIME, "=", knob_pmp_regime, " not in ", GEN_ENUM_KNOB_PMP_REGIME_VALUES}; return 1'b0; end
    msg = "";
    return 1'b1;
  endfunction

  // Regime knobs supplied on the command line (pinned), for the banner and CG-REG cp_pinned_count.
  function int unsigned pinned_count();
    int unsigned c = 0;
    if (knob_imem_gnt_delay_set) c++;
    if (knob_imem_rvalid_delay_set) c++;
    if (knob_imem_err_rate_set) c++;
    if (knob_imem_intg_err_rate_set) c++;
    if (knob_imem_outstanding_cap_set) c++;
    if (knob_dmem_gnt_delay_set) c++;
    if (knob_dmem_rvalid_delay_set) c++;
    if (knob_dmem_err_rate_set) c++;
    if (knob_dmem_intg_err_rate_set) c++;
    if (knob_irq_regime_set) c++;
    if (knob_irq_line_mix_set) c++;
    if (knob_irq_hold_set) c++;
    if (knob_debug_req_regime_set) c++;
    if (knob_scr_key_delay_set) c++;
    if (knob_icache_ecc_err_rate_set) c++;
    if (knob_fetch_enable_regime_set) c++;
    if (knob_mcounteren_writable_set) c++;
    if (knob_instr_mix_set) c++;
    if (knob_priv_regime_set) c++;
    if (knob_pmp_regime_set) c++;
    return c;
  endfunction

