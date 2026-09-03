// gen_tb_pkg: the single constants home of the generated TB. The GEN_KNOBS block is rendered from
// dv/auto_dv/tb/gen_tb_knobs.yaml by gen_knobs_codegen.py (plusarg names, knob value sets, constants,
// memory map); widths, encodings and enums come from ibex_pkg; nothing here re-types them.
package gen_tb_pkg;
  import ibex_pkg::*;

  // GEN_KNOBS_BEGIN (rendered by dv/auto_dv/tb/gen_knobs_codegen.py from gen_tb_knobs.yaml; edit the yaml, not this block)
  // Plusarg names: +gen_<name>=<value>; declared once here, never as string literals elsewhere.
  parameter string PLUSARG_BUILD_CONFIG = "gen_build_config";  // string, default opentitan: build configuration name echoed in the banner (must match the compile)
  parameter string PLUSARG_SMOKE_CYCLES = "gen_smoke_cycles";  // int, default 3000: bounded run length of gen_smoke_tb_top
  parameter string PLUSARG_SMOKE_INTG_FLIP = "gen_smoke_intg_flip";  // int, default unset: smoke red-run knob
  parameter string PLUSARG_DBG_CSR_PROBE = "gen_dbg_csr_probe";  // bool, default 0 [debug-only]: probe P6 (docs/gen_probe_register.md)
  parameter string PLUSARG_MEM_IMAGE = "gen_mem_image";  // string, default unset: program image (.vmem) loaded once at time 0
  parameter string PLUSARG_MEM_IMAGE_CRC32 = "gen_mem_image_crc32";  // hex, default unset: CRC-32 over (index
  parameter string PLUSARG_MEM_IMAGE_WORDS = "gen_mem_image_words";  // int, default unset: word count from the sidecar
  parameter string PLUSARG_MEM_READBACK_WORDS = "gen_mem_readback_words";  // int, default 64: words Python reads back through MEM_PEEK and compares with the .vmem
  parameter string PLUSARG_TOHOST_ADDR = "gen_tohost_addr";  // hex, default unset: address of the program tohost word (sidecar symbol); a store there ends the test with the stored code
  parameter string PLUSARG_MEM_UNMAPPED_OK = "gen_mem_unmapped_ok";  // bool, default 0: unmapped bus access returns an error response instead of a TB error
  parameter string PLUSARG_BOOT_ADDR = "gen_boot_addr";  // hex, default 0x80000000: boot_addr_i (must match the image entry page)
  parameter string PLUSARG_ALIVE_TIMEOUT = "gen_alive_timeout";  // int, default 100000: cycles before the SV alive watchdog fatals (TB_CONTRACT Section 2)
  parameter string PLUSARG_FINISH_TIMEOUT = "gen_finish_timeout";  // int, default 20000: default finish-handshake budget in cycles (Python overrides per test)
  parameter string PLUSARG_REGIME_SCHED = "gen_regime_sched";  // string, default unset: layer-3 schedule knob:value@r<N>|c<N>
  parameter string PLUSARG_RVFI_TRACE = "gen_rvfi_trace";  // bool, default 0: write an ASCII RVFI trace file (debug only)
  parameter string PLUSARG_FCOV_EN = "gen_fcov_en";  // bool, default 1: instantiate covergroups
  parameter string PLUSARG_ICRAM_INIT = "gen_icram_init";  // enum, default random: initial contents of the icache tag/data RAM models
  parameter string PLUSARG_FETCH_EN_AT_RESET = "gen_fetch_en_at_reset";  // bool, default 1: fetch_enable_i On out of reset; 0 holds the core until a bridge FETCH_EN command (image read-back happens first)
  parameter string PLUSARG_KEY_RESET_VALID = "gen_key_reset_valid";  // bool, default 1: ic_scr_key_valid_i high out of reset (ibex_top behaviour)
  parameter string PLUSARG_SB_TRACE = "gen_sb_trace";  // bool, default 0: scoreboard per-record trace (debug only)
  parameter string PLUSARG_UT_LOCKSTEP_MIN_RATIO_PCT = "gen_ut_lockstep_min_ratio_pct";  // int, default 90: lock-step test
  parameter string PLUSARG_ISA_STRING = "gen_isa_string";  // string, default unset: model ISA string override (debug only; the default is GEN_ISA_STRING)
  parameter string PLUSARG_ISA_LOG = "gen_isa_log";  // string, default unset: model commit log path for debug
  parameter string PLUSARG_UT_BOOT_RETIRE = "gen_ut_boot_retire";  // int, default 200: retirements the boots-and-retires test waits for
  parameter string PLUSARG_IBUS_GNT_MIN = "gen_ibus_gnt_min";  // int, default unset: instruction bus grant latency low bound (cycles)
  parameter string PLUSARG_IBUS_GNT_MAX = "gen_ibus_gnt_max";  // int, default unset: instruction bus grant latency high bound
  parameter string PLUSARG_IBUS_RVALID_MIN = "gen_ibus_rvalid_min";  // int, default unset: instruction bus response latency low bound (hard floor 1)
  parameter string PLUSARG_IBUS_RVALID_MAX = "gen_ibus_rvalid_max";  // int, default unset: instruction bus response latency high bound
  parameter string PLUSARG_IBUS_MAX_OUTSTANDING = "gen_ibus_max_outstanding";  // int, default unset: grants in flight before gnt is withheld (cap GEN_IBUS_MAX_OUTSTANDING)
  parameter string PLUSARG_IBUS_ERR_RATE = "gen_ibus_err_rate";  // int, default unset: per-mille probability of instr_err_i per response
  parameter string PLUSARG_IBUS_INTG_ERR_RATE = "gen_ibus_intg_err_rate";  // int, default unset: per-mille probability of corrupting instr_rdata_i integrity
  parameter string PLUSARG_IBUS_INTG_BITS = "gen_ibus_intg_bits";  // int, default 1: bits flipped per corrupted instruction response (1 or 2)
  parameter string PLUSARG_IBUS_ERR_WINDOW = "gen_ibus_err_window";  // string, default unset: lo:hi address window where injected instruction errors apply
  parameter string PLUSARG_DBUS_GNT_MIN = "gen_dbus_gnt_min";  // int, default unset: data bus grant latency low bound
  parameter string PLUSARG_DBUS_GNT_MAX = "gen_dbus_gnt_max";  // int, default unset: data bus grant latency high bound
  parameter string PLUSARG_DBUS_RVALID_MIN = "gen_dbus_rvalid_min";  // int, default unset: data bus response latency low bound (hard floor 1)
  parameter string PLUSARG_DBUS_RVALID_MAX = "gen_dbus_rvalid_max";  // int, default unset: data bus response latency high bound
  parameter string PLUSARG_DBUS_MAX_OUTSTANDING = "gen_dbus_max_outstanding";  // int, default unset: data grants in flight (cap GEN_DBUS_MAX_OUTSTANDING)
  parameter string PLUSARG_DBUS_ERR_RATE = "gen_dbus_err_rate";  // int, default unset: per-mille probability of data_err_i per response
  parameter string PLUSARG_DBUS_INTG_ERR_RATE = "gen_dbus_intg_err_rate";  // int, default unset: per-mille probability of corrupting data_rdata_i integrity
  parameter string PLUSARG_DBUS_INTG_BITS = "gen_dbus_intg_bits";  // int, default 1: bits flipped per corrupted data response
  parameter string PLUSARG_DBUS_ERR_WINDOW = "gen_dbus_err_window";  // string, default unset: lo:hi address window where injected data errors apply
  parameter string PLUSARG_DBUS_ERR_HALF = "gen_dbus_err_half";  // enum, default any: which half of a split access an injected error hits
  parameter string PLUSARG_DBUS_ERR_STORE_PERFORM = "gen_dbus_err_store_perform";  // bool, default 1: an errored store still updates the memory model
  parameter string PLUSARG_KEY_DELAY_MIN = "gen_key_delay_min";  // int, default 1: scramble-key response delay low bound
  parameter string PLUSARG_KEY_DELAY_MAX = "gen_key_delay_max";  // int, default 20: scramble-key response delay high bound
  parameter string PLUSARG_KEY_NEVER_CYCLES = "gen_key_never_cycles";  // int, default 0: cycles the key stays withheld in the withheld_then_valid regime
  parameter string PLUSARG_IRQ_MIN_GAP = "gen_irq_min_gap";  // int, default 0: minimum cycles between interrupt events
  parameter string PLUSARG_IRQ_HOLD_MIN = "gen_irq_hold_min";  // int, default 1: interrupt line hold low bound (CYCLES policy)
  parameter string PLUSARG_IRQ_HOLD_MAX = "gen_irq_hold_max";  // int, default 50: interrupt line hold high bound
  parameter string PLUSARG_DBG_HOLD_MIN = "gen_dbg_hold_min";  // int, default 1: debug_req_i hold low bound
  parameter string PLUSARG_DBG_HOLD_MAX = "gen_dbg_hold_max";  // int, default 50: debug_req_i hold high bound
  parameter string PLUSARG_KNOB_IMEM_GNT_DELAY = "gen_knob_imem_gnt_delay";  // enum, default short: instruction grant latency regime
  parameter string PLUSARG_KNOB_IMEM_RVALID_DELAY = "gen_knob_imem_rvalid_delay";  // enum, default short: instruction response latency regime
  parameter string PLUSARG_KNOB_IMEM_ERR_RATE = "gen_knob_imem_err_rate";  // enum, default none: instr_err_i injection regime
  parameter string PLUSARG_KNOB_IMEM_INTG_ERR_RATE = "gen_knob_imem_intg_err_rate";  // enum, default none: instruction integrity corruption regime
  parameter string PLUSARG_KNOB_IMEM_OUTSTANDING_CAP = "gen_knob_imem_outstanding_cap";  // enum, default cap8: instruction grants in flight cap
  parameter string PLUSARG_KNOB_DMEM_GNT_DELAY = "gen_knob_dmem_gnt_delay";  // enum, default short: data grant latency regime
  parameter string PLUSARG_KNOB_DMEM_RVALID_DELAY = "gen_knob_dmem_rvalid_delay";  // enum, default short: data response latency regime
  parameter string PLUSARG_KNOB_DMEM_ERR_RATE = "gen_knob_dmem_err_rate";  // enum, default none: data_err_i injection regime
  parameter string PLUSARG_KNOB_DMEM_INTG_ERR_RATE = "gen_knob_dmem_intg_err_rate";  // enum, default none: data integrity corruption regime
  parameter string PLUSARG_KNOB_IRQ_REGIME = "gen_knob_irq_regime";  // enum, default quiet: interrupt event rate
  parameter string PLUSARG_KNOB_IRQ_LINE_MIX = "gen_knob_irq_line_mix";  // enum, default single: lines per interrupt event
  parameter string PLUSARG_KNOB_IRQ_HOLD = "gen_knob_irq_hold";  // enum, default until_taken: interrupt line release policy
  parameter string PLUSARG_KNOB_DEBUG_REQ_REGIME = "gen_knob_debug_req_regime";  // enum, default none: debug_req_i event rate
  parameter string PLUSARG_KNOB_SCR_KEY_DELAY = "gen_knob_scr_key_delay";  // enum, default immediate: scramble-key response regime
  parameter string PLUSARG_KNOB_ICACHE_ECC_ERR_RATE = "gen_knob_icache_ecc_err_rate";  // enum, default none: icache RAM ECC injection regime
  parameter string PLUSARG_KNOB_FETCH_ENABLE_REGIME = "gen_knob_fetch_enable_regime";  // enum, default always_on: fetch_enable_i regime
  parameter string PLUSARG_KNOB_MCOUNTEREN_WRITABLE = "gen_knob_mcounteren_writable";  // enum, default on: mcounteren_writable_i encoding
  parameter string PLUSARG_KNOB_INSTR_MIX = "gen_knob_instr_mix";  // enum, default mixed: program-side instruction mix (region marker)
  parameter string PLUSARG_KNOB_PRIV_REGIME = "gen_knob_priv_regime";  // enum, default m_only: program-side privilege regime (region marker)
  parameter string PLUSARG_KNOB_PMP_REGIME = "gen_knob_pmp_regime";  // enum, default off: program-side PMP regime (region marker)
  parameter string PLUSARG_CHK_ALL = "gen_chk_all";  // bool, default 1: master checker enable (isolation mode +gen_chk_all=0 +gen_chk_<id>=1)
  parameter string PLUSARG_CHK_IBUS_PROTO = "gen_chk_ibus_proto";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_IBUS_OUTSTANDING = "gen_chk_ibus_outstanding";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_SVA_RVALID_LEGAL = "gen_chk_sva_rvalid_legal";  // bool, default 1: TB self-check enable (stimulus legality)
  parameter string PLUSARG_CHK_DBUS_PROTO = "gen_chk_dbus_proto";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBUS_OUTSTANDING = "gen_chk_dbus_outstanding";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBUS_SPLIT = "gen_chk_dbus_split";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBUS_STORE_INTG = "gen_chk_dbus_store_intg";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ICRAM_WRITE_ECC = "gen_chk_icram_write_ecc";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ICRAM_INVAL_SWEEP = "gen_chk_icram_inval_sweep";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ICRAM_ECC_RESPONSE = "gen_chk_icram_ecc_response";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_SCRKEY_PROTO = "gen_chk_scrkey_proto";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ALERT_MINOR = "gen_chk_alert_minor";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ALERT_BUS = "gen_chk_alert_bus";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ALERT_INTERNAL = "gen_chk_alert_internal";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CRASH_DUMP = "gen_chk_crash_dump";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DOUBLE_FAULT = "gen_chk_double_fault";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CORE_BUSY = "gen_chk_core_busy";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DATA_TAG_QUIET = "gen_chk_data_tag_quiet";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_FETCH_EN = "gen_chk_fetch_en";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_IRQ_PENDING = "gen_chk_irq_pending";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_IRQ_ENTRY = "gen_chk_irq_entry";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_IRQ_MASKED = "gen_chk_irq_masked";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_NMI_ENTRY = "gen_chk_nmi_entry";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_NMI_INTERNAL = "gen_chk_nmi_internal";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBG_ENTRY = "gen_chk_dbg_entry";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBG_EXC = "gen_chk_dbg_exc";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBG_MASKED = "gen_chk_dbg_masked";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBG_DRET = "gen_chk_dbg_dret";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_DBG_TRIGGER = "gen_chk_dbg_trigger";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CTR_MCYCLE = "gen_chk_ctr_mcycle";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CTR_MINSTRET = "gen_chk_ctr_minstret";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CTR_HPM_EXACT = "gen_chk_ctr_hpm_exact";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_CTR_HPM_BOUND = "gen_chk_ctr_hpm_bound";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_PMP_DATA = "gen_chk_pmp_data";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_PMP_FETCH = "gen_chk_pmp_fetch";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_ISA = "gen_chk_isa";  // bool, default 1: ISA comparator master enable
  parameter string PLUSARG_CHK_ISA_PC = "gen_chk_isa_pc";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_INSN = "gen_chk_isa_insn";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_TRAP = "gen_chk_isa_trap";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_RD = "gen_chk_isa_rd";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_MEM = "gen_chk_isa_mem";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_PRV = "gen_chk_isa_prv";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_PC_NEXT = "gen_chk_isa_pc_next";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_ISA_CSR = "gen_chk_isa_csr";  // bool, default 1: ISA compare field enable
  parameter string PLUSARG_CHK_RVFI_PROTO = "gen_chk_rvfi_proto";  // bool, default 1: RVFI stream sanity assertions (monitor)
  parameter string PLUSARG_CHK_T022_NEVER = "gen_chk_t022_never";  // bool, default 1: rtl-arch T-022 never-arc asserts in the binds home
  parameter string PLUSARG_CHK_BRIDGE_ACCOUNTING = "gen_chk_bridge_accounting";  // bool, default 1: TB self-check enable
  // Enumerated knob value sets and defaults (DV Lead regime knobs and TB enums).
  parameter string GEN_ENUM_ICRAM_INIT_VALUES = "zero,random";
  parameter string GEN_ENUM_ICRAM_INIT_DEFAULT = "random";
  parameter string GEN_ENUM_DBUS_ERR_HALF_VALUES = "first,second,both,any";
  parameter string GEN_ENUM_DBUS_ERR_HALF_DEFAULT = "any";
  parameter string GEN_ENUM_KNOB_IMEM_GNT_DELAY_VALUES = "same_cycle,short,long,random";
  parameter string GEN_ENUM_KNOB_IMEM_GNT_DELAY_DEFAULT = "short";
  parameter string GEN_ENUM_KNOB_IMEM_RVALID_DELAY_VALUES = "min1,short,long,random";
  parameter string GEN_ENUM_KNOB_IMEM_RVALID_DELAY_DEFAULT = "short";
  parameter string GEN_ENUM_KNOB_IMEM_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_IMEM_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_IMEM_INTG_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_IMEM_INTG_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_IMEM_OUTSTANDING_CAP_VALUES = "cap1,cap2,cap4,cap8";
  parameter string GEN_ENUM_KNOB_IMEM_OUTSTANDING_CAP_DEFAULT = "cap8";
  parameter string GEN_ENUM_KNOB_DMEM_GNT_DELAY_VALUES = "same_cycle,short,long,random";
  parameter string GEN_ENUM_KNOB_DMEM_GNT_DELAY_DEFAULT = "short";
  parameter string GEN_ENUM_KNOB_DMEM_RVALID_DELAY_VALUES = "min1,short,long,random";
  parameter string GEN_ENUM_KNOB_DMEM_RVALID_DELAY_DEFAULT = "short";
  parameter string GEN_ENUM_KNOB_DMEM_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_DMEM_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_DMEM_INTG_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_DMEM_INTG_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_IRQ_REGIME_VALUES = "quiet,sparse,storm";
  parameter string GEN_ENUM_KNOB_IRQ_REGIME_DEFAULT = "quiet";
  parameter string GEN_ENUM_KNOB_IRQ_LINE_MIX_VALUES = "single,multi,fast_only,with_nmi";
  parameter string GEN_ENUM_KNOB_IRQ_LINE_MIX_DEFAULT = "single";
  parameter string GEN_ENUM_KNOB_IRQ_HOLD_VALUES = "until_taken,through_handler,pulse";
  parameter string GEN_ENUM_KNOB_IRQ_HOLD_DEFAULT = "until_taken";
  parameter string GEN_ENUM_KNOB_DEBUG_REQ_REGIME_VALUES = "none,sparse,storm";
  parameter string GEN_ENUM_KNOB_DEBUG_REQ_REGIME_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_SCR_KEY_DELAY_VALUES = "immediate,delayed,withheld_then_valid";
  parameter string GEN_ENUM_KNOB_SCR_KEY_DELAY_DEFAULT = "immediate";
  parameter string GEN_ENUM_KNOB_ICACHE_ECC_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_ICACHE_ECC_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_FETCH_ENABLE_REGIME_VALUES = "always_on,toggling";
  parameter string GEN_ENUM_KNOB_FETCH_ENABLE_REGIME_DEFAULT = "always_on";
  parameter string GEN_ENUM_KNOB_MCOUNTEREN_WRITABLE_VALUES = "on,off,invalid";
  parameter string GEN_ENUM_KNOB_MCOUNTEREN_WRITABLE_DEFAULT = "on";
  parameter string GEN_ENUM_KNOB_INSTR_MIX_VALUES = "isa_only,m_heavy,compressed_heavy,bitmanip_heavy,csr_heavy,ls_heavy,branch_heavy,mixed";
  parameter string GEN_ENUM_KNOB_INSTR_MIX_DEFAULT = "mixed";
  parameter string GEN_ENUM_KNOB_PRIV_REGIME_VALUES = "m_only,u_heavy,alternating";
  parameter string GEN_ENUM_KNOB_PRIV_REGIME_DEFAULT = "m_only";
  parameter string GEN_ENUM_KNOB_PMP_REGIME_VALUES = "off,sparse,dense,mml_on";
  parameter string GEN_ENUM_KNOB_PMP_REGIME_DEFAULT = "off";
  // TB constants (values predicted by rtl-arch T-051 where noted; bring-up confirms).
  parameter int unsigned GEN_ICACHE_NUM_FB = 4;  // icache fill buffers, the one re-typed localparam NUM_FB (rtl/ibex_icache.sv:72)
  parameter int unsigned GEN_IBUS_MAX_OUTSTANDING = GEN_ICACHE_NUM_FB * ibex_pkg::IC_LINE_BEATS;  // instruction beats in flight (NUM_FB x IC_LINE_BEATS; rtl-arch T-051 2.3)
  parameter int unsigned GEN_DBUS_MAX_OUTSTANDING = 2;  // data beats in flight, the two halves of one split access (rtl/ibex_load_store_unit.sv:403-405)
  parameter int unsigned GEN_CSR_WRITE_TO_RVFI_OFFSET = 2;  // cycles from a CSR-write commit edge to its RVFI record (v3 T-051 2.1, predicted, pinned by a directed test)
  parameter int unsigned GEN_TRAP_TO_RVFI_OFFSET = 1;  // cycles from a trap/mret/dret commit edge to its RVFI record (v3 T-051 2.1)
  parameter int unsigned GEN_IRQ_MARKER_TO_RVFI_OFFSET = 2;  // cycles from the interrupt entry commit to the rvfi_ext_irq_valid marker (v3 T-051 2.1)
  parameter int unsigned GEN_RVFI_ID_EXIT_OFFSET = 2;  // cycles from ID exit (rvfi_ext_mcycle sample point, rtl/ibex_core.sv:2102) to the record, plus the WB wait for loads/stores (v3 T-051 2.2)
  parameter int unsigned GEN_ICACHE_ECC_WINDOW = 1;  // alert_minor_o in the corrupted-rdata cycle (window 1 counted from the lookup request); invalidation write one cycle later (v3 T-051 2.4)
  parameter int unsigned GEN_IRQ_ENTRY_BOUND_RECORDS = 17;  // records between a pin edge and the interrupt entry, worst case WB + ID + 16 Zcmp micro-ops (v3 T-051 2.6)
  parameter int unsigned GEN_DBG_ENTRY_BOUND_RECORDS = 17;  // records between debug_req_i and the debug entry, same derivation (v3 T-051 2.6)
  parameter int unsigned GEN_CLK_PERIOD_NS = 10;  // TB clock period (gen_tb_top ClkHalfPeriodNs = 5); Python converts cycle budgets to ns with it
  parameter int unsigned GEN_MEM_READBACK_WORDS_DEFAULT = 64;  // default MEM_PEEK read-back sample size
  parameter int unsigned GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT = 100000;  // default alive watchdog
  parameter logic [31:0] GEN_IRQ_FAST_MASK = ((32'h1 << $bits(ibex_pkg::irqs_t) - 3) - 1) << 16;  // mie/mip fast interrupt bits 16..30 (15 fast lines); the shim installs them in gen_mie_csr_t
  // TB memory map: DM windows from gen_dut_top.sv, program window from gen_link.ld, MMIO page from the yaml.
  parameter logic [31:0] GEN_MM_BOOT_ADDR_DEFAULT = 32'h8000_0000;
  parameter logic [31:0] GEN_MM_BOOT_PAGE = 32'h8000_0000;
  parameter logic [31:0] GEN_MM_PROG_SIZE = 32'h0010_0000;
  parameter logic [31:0] GEN_MM_DM_BASE = 32'h1a11_0000;
  parameter logic [31:0] GEN_MM_DM_SIZE = 32'h0000_1000;
  parameter logic [31:0] GEN_MM_DM_HALT = 32'h1a11_0800;
  parameter logic [31:0] GEN_MM_DM_EXCEPTION = 32'h1a11_0808;
  parameter logic [31:0] GEN_MM_DM_BUDGET = 32'h0000_0800;
  parameter logic [31:0] GEN_MM_MMIO_BASE = 32'h8fff_f000;
  parameter logic [31:0] GEN_MM_MMIO_SIZE = 32'h0000_1000;
  parameter logic [31:0] GEN_MM_SIG_ADDR = 32'h8fff_f000;
  parameter logic [31:0] GEN_MM_IRQ_ACK_ADDR = 32'h8fff_f100;
  parameter logic [31:0] GEN_MM_EOT_ADDR = 32'h8fff_f104;
  parameter logic [31:0] GEN_MM_PHASE_MARK_ADDR = 32'h8fff_f108;
  // Bridge command kinds (C2); 0 is NONE.
  parameter logic [7:0] GEN_CMD_NONE = 8'd0;
  parameter logic [7:0] GEN_CMD_IRQ_SET = 8'd1;
  parameter logic [7:0] GEN_CMD_IRQ_CLR = 8'd2;
  parameter logic [7:0] GEN_CMD_NMI_PULSE = 8'd3;
  parameter logic [7:0] GEN_CMD_DBG_REQ = 8'd4;
  parameter logic [7:0] GEN_CMD_REGIME_SET = 8'd5;
  parameter logic [7:0] GEN_CMD_KEY_MODE = 8'd6;
  parameter logic [7:0] GEN_CMD_MEM_ERR_ARM = 8'd7;
  parameter logic [7:0] GEN_CMD_ICACHE_ECC_ARM = 8'd8;
  parameter logic [7:0] GEN_CMD_FETCH_EN = 8'd9;
  parameter logic [7:0] GEN_CMD_MEM_PEEK = 8'd10;
  parameter logic [7:0] GEN_CMD_MISC = 8'd11;
  // Regime knob ids and value lookup (bridge command REGIME_SET: arg0 = knob id, arg1 = value index).
  parameter int GEN_KNOB_ID_IMEM_GNT_DELAY = 0;
  parameter int GEN_KNOB_ID_IMEM_RVALID_DELAY = 1;
  parameter int GEN_KNOB_ID_IMEM_ERR_RATE = 2;
  parameter int GEN_KNOB_ID_IMEM_INTG_ERR_RATE = 3;
  parameter int GEN_KNOB_ID_IMEM_OUTSTANDING_CAP = 4;
  parameter int GEN_KNOB_ID_DMEM_GNT_DELAY = 5;
  parameter int GEN_KNOB_ID_DMEM_RVALID_DELAY = 6;
  parameter int GEN_KNOB_ID_DMEM_ERR_RATE = 7;
  parameter int GEN_KNOB_ID_DMEM_INTG_ERR_RATE = 8;
  parameter int GEN_KNOB_ID_IRQ_REGIME = 9;
  parameter int GEN_KNOB_ID_IRQ_LINE_MIX = 10;
  parameter int GEN_KNOB_ID_IRQ_HOLD = 11;
  parameter int GEN_KNOB_ID_DEBUG_REQ_REGIME = 12;
  parameter int GEN_KNOB_ID_SCR_KEY_DELAY = 13;
  parameter int GEN_KNOB_ID_ICACHE_ECC_ERR_RATE = 14;
  parameter int GEN_KNOB_ID_FETCH_ENABLE_REGIME = 15;
  parameter int GEN_KNOB_ID_MCOUNTEREN_WRITABLE = 16;
  parameter int GEN_KNOB_ID_INSTR_MIX = 17;
  parameter int GEN_KNOB_ID_PRIV_REGIME = 18;
  parameter int GEN_KNOB_ID_PMP_REGIME = 19;
  function automatic string gen_knob_name(int id);
    case (id)
      0: return "knob_imem_gnt_delay";
      1: return "knob_imem_rvalid_delay";
      2: return "knob_imem_err_rate";
      3: return "knob_imem_intg_err_rate";
      4: return "knob_imem_outstanding_cap";
      5: return "knob_dmem_gnt_delay";
      6: return "knob_dmem_rvalid_delay";
      7: return "knob_dmem_err_rate";
      8: return "knob_dmem_intg_err_rate";
      9: return "knob_irq_regime";
      10: return "knob_irq_line_mix";
      11: return "knob_irq_hold";
      12: return "knob_debug_req_regime";
      13: return "knob_scr_key_delay";
      14: return "knob_icache_ecc_err_rate";
      15: return "knob_fetch_enable_regime";
      16: return "knob_mcounteren_writable";
      17: return "knob_instr_mix";
      18: return "knob_priv_regime";
      19: return "knob_pmp_regime";
      default: return "";
    endcase
  endfunction
  function automatic string gen_knob_value(int id, int idx);
    case (id)
      0: case (idx) 0: return "same_cycle"; 1: return "short"; 2: return "long"; 3: return "random"; default: return ""; endcase
      1: case (idx) 0: return "min1"; 1: return "short"; 2: return "long"; 3: return "random"; default: return ""; endcase
      2: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      3: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      4: case (idx) 0: return "cap1"; 1: return "cap2"; 2: return "cap4"; 3: return "cap8"; default: return ""; endcase
      5: case (idx) 0: return "same_cycle"; 1: return "short"; 2: return "long"; 3: return "random"; default: return ""; endcase
      6: case (idx) 0: return "min1"; 1: return "short"; 2: return "long"; 3: return "random"; default: return ""; endcase
      7: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      8: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      9: case (idx) 0: return "quiet"; 1: return "sparse"; 2: return "storm"; default: return ""; endcase
      10: case (idx) 0: return "single"; 1: return "multi"; 2: return "fast_only"; 3: return "with_nmi"; default: return ""; endcase
      11: case (idx) 0: return "until_taken"; 1: return "through_handler"; 2: return "pulse"; default: return ""; endcase
      12: case (idx) 0: return "none"; 1: return "sparse"; 2: return "storm"; default: return ""; endcase
      13: case (idx) 0: return "immediate"; 1: return "delayed"; 2: return "withheld_then_valid"; default: return ""; endcase
      14: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      15: case (idx) 0: return "always_on"; 1: return "toggling"; default: return ""; endcase
      16: case (idx) 0: return "on"; 1: return "off"; 2: return "invalid"; default: return ""; endcase
      17: case (idx) 0: return "isa_only"; 1: return "m_heavy"; 2: return "compressed_heavy"; 3: return "bitmanip_heavy"; 4: return "csr_heavy"; 5: return "ls_heavy"; 6: return "branch_heavy"; 7: return "mixed"; default: return ""; endcase
      18: case (idx) 0: return "m_only"; 1: return "u_heavy"; 2: return "alternating"; default: return ""; endcase
      19: case (idx) 0: return "off"; 1: return "sparse"; 2: return "dense"; 3: return "mml_on"; default: return ""; endcase
      default: return "";
    endcase
  endfunction
  // Every legal +gen_* plusarg name; gen_base_test fatals on any other +gen_* argument (A-23).
  function automatic bit gen_is_known_plusarg(string name);
    case (name)
      "gen_build_config", "gen_smoke_cycles", "gen_smoke_intg_flip", "gen_dbg_csr_probe", "gen_mem_image", "gen_mem_image_crc32", "gen_mem_image_words", "gen_mem_readback_words", "gen_tohost_addr", "gen_mem_unmapped_ok", "gen_boot_addr", "gen_alive_timeout", "gen_finish_timeout", "gen_regime_sched", "gen_rvfi_trace", "gen_fcov_en", "gen_icram_init", "gen_fetch_en_at_reset", "gen_key_reset_valid", "gen_sb_trace", "gen_ut_lockstep_min_ratio_pct", "gen_isa_string", "gen_isa_log", "gen_ut_boot_retire", "gen_ibus_gnt_min", "gen_ibus_gnt_max", "gen_ibus_rvalid_min", "gen_ibus_rvalid_max", "gen_ibus_max_outstanding", "gen_ibus_err_rate", "gen_ibus_intg_err_rate", "gen_ibus_intg_bits", "gen_ibus_err_window", "gen_dbus_gnt_min", "gen_dbus_gnt_max", "gen_dbus_rvalid_min", "gen_dbus_rvalid_max", "gen_dbus_max_outstanding", "gen_dbus_err_rate", "gen_dbus_intg_err_rate", "gen_dbus_intg_bits", "gen_dbus_err_window", "gen_dbus_err_half", "gen_dbus_err_store_perform", "gen_key_delay_min", "gen_key_delay_max", "gen_key_never_cycles", "gen_irq_min_gap", "gen_irq_hold_min", "gen_irq_hold_max", "gen_dbg_hold_min", "gen_dbg_hold_max", "gen_knob_imem_gnt_delay", "gen_knob_imem_rvalid_delay", "gen_knob_imem_err_rate", "gen_knob_imem_intg_err_rate", "gen_knob_imem_outstanding_cap", "gen_knob_dmem_gnt_delay", "gen_knob_dmem_rvalid_delay", "gen_knob_dmem_err_rate", "gen_knob_dmem_intg_err_rate", "gen_knob_irq_regime", "gen_knob_irq_line_mix", "gen_knob_irq_hold", "gen_knob_debug_req_regime", "gen_knob_scr_key_delay", "gen_knob_icache_ecc_err_rate", "gen_knob_fetch_enable_regime", "gen_knob_mcounteren_writable", "gen_knob_instr_mix", "gen_knob_priv_regime", "gen_knob_pmp_regime", "gen_chk_all", "gen_chk_ibus_proto", "gen_chk_ibus_outstanding", "gen_chk_sva_rvalid_legal", "gen_chk_dbus_proto", "gen_chk_dbus_outstanding", "gen_chk_dbus_split", "gen_chk_dbus_store_intg", "gen_chk_icram_write_ecc", "gen_chk_icram_inval_sweep", "gen_chk_icram_ecc_response", "gen_chk_scrkey_proto", "gen_chk_alert_minor", "gen_chk_alert_bus", "gen_chk_alert_internal", "gen_chk_crash_dump", "gen_chk_double_fault", "gen_chk_core_busy", "gen_chk_data_tag_quiet", "gen_chk_fetch_en", "gen_chk_irq_pending", "gen_chk_irq_entry", "gen_chk_irq_masked", "gen_chk_nmi_entry", "gen_chk_nmi_internal", "gen_chk_dbg_entry", "gen_chk_dbg_exc", "gen_chk_dbg_masked", "gen_chk_dbg_dret", "gen_chk_dbg_trigger", "gen_chk_ctr_mcycle", "gen_chk_ctr_minstret", "gen_chk_ctr_hpm_exact", "gen_chk_ctr_hpm_bound", "gen_chk_pmp_data", "gen_chk_pmp_fetch", "gen_chk_isa", "gen_chk_isa_pc", "gen_chk_isa_insn", "gen_chk_isa_trap", "gen_chk_isa_rd", "gen_chk_isa_mem", "gen_chk_isa_prv", "gen_chk_isa_pc_next", "gen_chk_isa_csr", "gen_chk_rvfi_proto", "gen_chk_t022_never", "gen_chk_bridge_accounting": return 1'b1;
      default: return 1'b0;
    endcase
  endfunction
  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h8000_0000;  // literal twin of GEN_MM_BOOT_ADDR_DEFAULT (regex readers: gen_program.py, gen_smoke_run.sh)
  // GEN_KNOBS_END

  // Every time-0 banner line starts with this tag so a log scanner can grep one token.
  parameter string GEN_BANNER_TAG = "GEN_CONFIG_BANNER";

  // The first fetch is {boot_addr_i[31:8], 8'h80} (rtl/ibex_if_stage.sv:243); gen_link.ld places the
  // program entry at GEN_MM_BOOT_PAGE + 0x80 (checked by gen_program.py and gen_knobs_codegen.py).

  // RV32I NOP = addi x0, x0, 0, composed from the ibex_pkg opcode so no encoding is re-typed.
  parameter logic [31:0] GEN_RV32_NOP = {12'd0, 5'd0, 3'b000, 5'd0, OPCODE_OP_IMM};

  // Cache RAM geometry the TB models must follow (ibex_pkg).
  parameter int unsigned GEN_IC_NUM_WAYS  = IC_NUM_WAYS;
  parameter int unsigned GEN_IC_NUM_LINES = IC_NUM_LINES;
  parameter int unsigned GEN_IC_INDEX_W   = IC_INDEX_W;

  // Membership of `s` in a comma-separated value list (enum knob validation, gen_env_cfg::validate).
  function automatic bit gen_str_in_csv(string s, string csv);
    int start = 0;
    for (int i = 0; i <= csv.len(); i++) begin
      if (i == csv.len() || csv[i] == ",") begin
        if (csv.substr(start, i - 1) == s) return 1'b1;
        start = i + 1;
      end
    end
    return 1'b0;
  endfunction

  function automatic string gen_mubi_str(ibex_mubi_t v);
    if (v == IbexMuBiOn)  return "On";
    if (v == IbexMuBiOff) return "Off";
    return $sformatf("INVALID(%0b)", v);
  endfunction

endpackage
