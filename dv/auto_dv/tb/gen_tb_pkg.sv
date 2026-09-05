// gen_tb_pkg: the single constants home of the generated TB. The GEN_KNOBS block is rendered from
// dv/auto_dv/tb/gen_tb_knobs.yaml by gen_knobs_codegen.py (plusarg names, knob value sets, constants,
// memory map); widths, encodings and enums come from ibex_pkg; nothing here re-types them.
package gen_tb_pkg;
  import ibex_pkg::*;

  // Zero irqs_t so the rendered GEN_IRQ_FAST_W can take the fast-line count from the struct member's width.
  localparam ibex_pkg::irqs_t GEN_IRQS_ZERO = '0;

  // GEN_KNOBS_BEGIN (rendered by dv/auto_dv/tb/gen_knobs_codegen.py from gen_tb_knobs.yaml; edit the yaml, not this block)
  // Plusarg names: +gen_<name>=<value>; declared once here, never as string literals elsewhere.
  parameter string PLUSARG_BUILD_CONFIG = "gen_build_config";  // string, default opentitan: build configuration name echoed in the banner (must match the compile)
  parameter string PLUSARG_SMOKE_CYCLES = "gen_smoke_cycles";  // int, default 3000: bounded run length of gen_smoke_tb_top
  parameter string PLUSARG_SMOKE_INTG_FLIP = "gen_smoke_intg_flip";  // int, default unset: smoke red-run knob, bit of the SECDED-encoded NOP word to flip (absent = no corruption)
  parameter string PLUSARG_DBG_CSR_PROBE = "gen_dbg_csr_probe";  // bool, default 0 [debug-only]: probe P6 (docs/gen_probe_register.md), debug only, never in a measured run
  parameter string PLUSARG_MEM_IMAGE = "gen_mem_image";  // string, default unset: program image (.vmem) loaded once at time 0
  parameter string PLUSARG_MEM_IMAGE_CRC32 = "gen_mem_image_crc32";  // hex, default unset: CRC-32 over (index, word) pairs from the .sym.json sidecar, recomputed after load
  parameter string PLUSARG_MEM_IMAGE_WORDS = "gen_mem_image_words";  // int, default unset: word count from the sidecar
  parameter string PLUSARG_MEM_READBACK_WORDS = "gen_mem_readback_words";  // int, default 64: words Python reads back through MEM_PEEK and compares with the .vmem
  parameter string PLUSARG_TOHOST_ADDR = "gen_tohost_addr";  // hex, default unset: address of the program tohost word (sidecar symbol); a store there ends the test with the stored code
  parameter string PLUSARG_MEM_UNMAPPED_OK = "gen_mem_unmapped_ok";  // bool, default 0: unmapped bus access returns an error response instead of a TB error
  parameter string PLUSARG_BOOT_ADDR = "gen_boot_addr";  // hex, default 0x80000000: boot_addr_i (must match the image entry page)
  parameter string PLUSARG_HART_ID = "gen_hart_id";  // hex, default 0x0: hart_id_i (architecture C1)
  parameter string PLUSARG_ALIVE_TIMEOUT = "gen_alive_timeout";  // int, default 100000: cycles before the SV alive watchdog fatals (TB_CONTRACT Section 2)
  parameter string PLUSARG_FINISH_TIMEOUT = "gen_finish_timeout";  // int, default 20000: finish-handshake budget in cycles used by GenBridge.finish() when the test passes none
  parameter string PLUSARG_REGIME_SCHED = "gen_regime_sched";  // string, default unset: layer-3 schedule knob:value@r<N>|c<N>,... (consumed when supplied, else derived from RANDOM_SEED and echoed)
  parameter string PLUSARG_RVFI_TRACE = "gen_rvfi_trace";  // bool, default 0 [debug-only]: print every RVFI record (debug only)
  parameter string PLUSARG_FCOV_EN = "gen_fcov_en";  // bool, default 1: instantiate covergroups
  parameter string PLUSARG_ICRAM_INIT = "gen_icram_init";  // enum, default random: initial contents of the icache tag/data RAM models
  parameter string PLUSARG_FETCH_EN_AT_RESET = "gen_fetch_en_at_reset";  // bool, default 1: fetch_enable_i On out of reset; 0 holds the core until a bridge FETCH_EN command (image read-back happens first)
  parameter string PLUSARG_KEY_RESET_VALID = "gen_key_reset_valid";  // bool, default 1: ic_scr_key_valid_i high out of reset (ibex_top behaviour)
  parameter string PLUSARG_SB_TRACE = "gen_sb_trace";  // bool, default 0 [debug-only]: scoreboard per-record trace (debug only)
  parameter string PLUSARG_ISA_PC_NEXT_MASK_B13 = "gen_isa_pc_next_mask_b13";  // bool, default 1: isa_pc_next masks bit 0 of rvfi_pc_wdata on jalr records (bug candidate B13, rtl-arch R11); 0 = the raw rule, for the expected-fail test of the odd-target report
  parameter string PLUSARG_ISA_STRING = "gen_isa_string";  // string, default unset [debug-only]: model ISA string override (debug only; the default is GEN_ISA_STRING)
  parameter string PLUSARG_ISA_LOG = "gen_isa_log";  // string, default unset [debug-only]: model commit log path (debug only)
  parameter string PLUSARG_EXPORT_FILE = "gen_export_file";  // string, default unset: record/event export file (relative to the run directory); absent = no export
  parameter string PLUSARG_EXPORT_COUNTERS = "gen_export_counters";  // bool, default 0: append the hpm counter words to every R line of the export
  parameter string PLUSARG_EXPORT_SOURCES = "gen_export_sources";  // string, default all: comma-separated event sources written to the export (all = every source with a registered writer)
  parameter string PLUSARG_EXPORT_FLUSH_EVERY = "gen_export_flush_every";  // int, default 0 [debug-only]: flush the export file every n records for triage of abnormal ends (0 = only on EXPORT_FLUSH)
  parameter string PLUSARG_UT_BOOT_RETIRE = "gen_ut_boot_retire";  // int, default 200: retirements the boots-and-retires test waits for
  parameter string PLUSARG_UT_FCOV_QUERY = "gen_ut_fcov_query";  // int, default -1: gen_ut_isa_cov: the sampler counter index to compare (FCOV_QUERY), -1 for none
  parameter string PLUSARG_UT_FCOV_EXPECT = "gen_ut_fcov_expect";  // int, default 0: gen_ut_isa_cov: the value the program is known to produce for that counter
  parameter string PLUSARG_UT_ROWS_SET = "gen_ut_rows_set";  // enum, default regime_nmi: gen_ut_export_rows: the pin row exercised beside regime phase (irq_nm through NMI_PULSE, or debug_req through DBG_REQ)
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
  parameter string PLUSARG_KNOB_IMEM_GNT_DELAY = "gen_knob_imem_gnt_delay";  // enum, default short: instruction grant latency regime (windows: regime_windows.gnt_delay)
  parameter string PLUSARG_KNOB_IMEM_RVALID_DELAY = "gen_knob_imem_rvalid_delay";  // enum, default short: instruction response latency regime (windows: regime_windows.rvalid_delay)
  parameter string PLUSARG_KNOB_IMEM_ERR_RATE = "gen_knob_imem_err_rate";  // enum, default none: instr_err_i injection regime (rates: regime_windows.rate_per_mille)
  parameter string PLUSARG_KNOB_IMEM_INTG_ERR_RATE = "gen_knob_imem_intg_err_rate";  // enum, default none: instruction integrity corruption regime (rates: regime_windows.rate_per_mille)
  parameter string PLUSARG_KNOB_IMEM_OUTSTANDING_CAP = "gen_knob_imem_outstanding_cap";  // enum, default cap8: instruction grants in flight cap (regime_windows.outstanding_cap)
  parameter string PLUSARG_KNOB_DMEM_GNT_DELAY = "gen_knob_dmem_gnt_delay";  // enum, default short: data grant latency regime (windows: regime_windows.gnt_delay)
  parameter string PLUSARG_KNOB_DMEM_RVALID_DELAY = "gen_knob_dmem_rvalid_delay";  // enum, default short: data response latency regime (windows: regime_windows.rvalid_delay)
  parameter string PLUSARG_KNOB_DMEM_ERR_RATE = "gen_knob_dmem_err_rate";  // enum, default none: data_err_i injection regime (rates: regime_windows.rate_per_mille)
  parameter string PLUSARG_KNOB_DMEM_INTG_ERR_RATE = "gen_knob_dmem_intg_err_rate";  // enum, default none: data integrity corruption regime (rates: regime_windows.rate_per_mille)
  parameter string PLUSARG_KNOB_IRQ_REGIME = "gen_knob_irq_regime";  // enum, default quiet: interrupt event rate
  parameter string PLUSARG_KNOB_IRQ_LINE_MIX = "gen_knob_irq_line_mix";  // enum, default single: lines per interrupt event
  parameter string PLUSARG_KNOB_IRQ_HOLD = "gen_knob_irq_hold";  // enum, default until_taken: interrupt line release policy
  parameter string PLUSARG_KNOB_DEBUG_REQ_REGIME = "gen_knob_debug_req_regime";  // enum, default none: debug_req_i event rate
  parameter string PLUSARG_KNOB_SCR_KEY_DELAY = "gen_knob_scr_key_delay";  // enum, default immediate: scramble-key response regime
  parameter string PLUSARG_KNOB_ICACHE_ECC_ERR_RATE = "gen_knob_icache_ecc_err_rate";  // enum, default none: icache tag-RAM ECC injection regime (rates: regime_windows.rate_per_mille): the tag RAM models flip one bit of a lookup read at the rate and announce it through gen_icram_events; the misc monitor expects alert_minor_o within GEN_ICACHE_ECC_WINDOW of every qualified injection
  parameter string PLUSARG_KNOB_ICACHE_DATA_ECC_ERR_RATE = "gen_knob_icache_data_ecc_err_rate";  // enum, default none: icache data-RAM ECC injection regime (rates: regime_windows.rate_per_mille): the data RAM models flip bits of a lookup read at the rate and announce it through gen_icram_events with the injected way's stored tag state; the misc monitor owes a pulse only when the way was valid and was the way the lookup hit; the lookup tag comes from the P9 probe in evidence runs and from the retirement stream in measured runs
  parameter string PLUSARG_KNOB_ICACHE_ECC_BITS = "gen_knob_icache_ecc_bits";  // enum, default one: bits flipped per icache ECC injection on both RAM kinds: one, or two distinct positions (a detected two-bit error alerts and invalidates as a one-bit error does)
  parameter string PLUSARG_KNOB_FETCH_ENABLE_REGIME = "gen_knob_fetch_enable_regime";  // enum, default always_on: fetch_enable_i regime
  parameter string PLUSARG_KNOB_MCOUNTEREN_WRITABLE = "gen_knob_mcounteren_writable";  // enum, default on: mcounteren_writable_i encoding
  parameter string PLUSARG_KNOB_INSTR_MIX = "gen_knob_instr_mix";  // enum, default mixed: program-side instruction mix (region marker)
  parameter string PLUSARG_KNOB_PRIV_REGIME = "gen_knob_priv_regime";  // enum, default m_only: program-side privilege regime (region marker)
  parameter string PLUSARG_KNOB_PMP_REGIME = "gen_knob_pmp_regime";  // enum, default off: program-side PMP regime (region marker)
  parameter string PLUSARG_CHK_ALL = "gen_chk_all";  // bool, default 1: master checker enable (isolation mode +gen_chk_all=0 +gen_chk_<id>=1)
  parameter string PLUSARG_CHK_IBUS_PROTO = "gen_chk_ibus_proto";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_IBUS_OUTSTANDING = "gen_chk_ibus_outstanding";  // bool, default 1: checker enable
  parameter string PLUSARG_CHK_SVA_ST = "gen_chk_sva_st";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_st_*)
  parameter string PLUSARG_CHK_SVA_IBUS = "gen_chk_sva_ibus";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_ibus_*)
  parameter string PLUSARG_CHK_SVA_DBUS = "gen_chk_sva_dbus";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_dbus_*)
  parameter string PLUSARG_CHK_SVA_ICRAM = "gen_chk_sva_icram";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_icram_*)
  parameter string PLUSARG_CHK_SVA_SCRKEY = "gen_chk_sva_scrkey";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_scrkey_*)
  parameter string PLUSARG_CHK_SVA_IRQ = "gen_chk_sva_irq";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_irq_*)
  parameter string PLUSARG_CHK_SVA_DBG = "gen_chk_sva_dbg";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_dbg_*)
  parameter string PLUSARG_CHK_SVA_ALERT = "gen_chk_sva_alert";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_alert_*)
  parameter string PLUSARG_CHK_SVA_RVFI = "gen_chk_sva_rvfi";  // bool, default 1: protocol SVA group enable, gen_binds.sv (gen_protocol_props ids sva_rvfi_*)
  parameter string PLUSARG_CHK_SVA_B8 = "gen_chk_sva_b8";  // bool, default 0: the B8 probe assertion sva_b8_dummy_in_expansion (gen_b8_probe.sv bound into ibex_if_stage, LOG-067): off by default because the DUT fails it on every dummy insertion inside a Zcmp expansion; the reproducer runs enable it
  parameter string PLUSARG_PROBE_IC_LOOKUP = "gen_probe_ic_lookup";  // bool, default 0 [debug-only]: the P9 probe (docs/gen_probe_register.md, LOG-079): gen_ic_lookup_probe.sv bound into ibex_icache publishes the lookup tag the DUT compares, so the misc monitor derives the hit way for data-RAM ECC injections; read-only, off by default, debug only (never in a measured run)
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
  parameter string GEN_ENUM_UT_ROWS_SET_VALUES = "regime_nmi,regime_dbg";
  parameter string GEN_ENUM_UT_ROWS_SET_DEFAULT = "regime_nmi";
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
  parameter string GEN_ENUM_KNOB_ICACHE_DATA_ECC_ERR_RATE_VALUES = "none,rare,frequent";
  parameter string GEN_ENUM_KNOB_ICACHE_DATA_ECC_ERR_RATE_DEFAULT = "none";
  parameter string GEN_ENUM_KNOB_ICACHE_ECC_BITS_VALUES = "one,two";
  parameter string GEN_ENUM_KNOB_ICACHE_ECC_BITS_DEFAULT = "one";
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
  // Numeric meaning of the latency/rate/cap regimes (yaml regime_windows); 0 = unknown group or value.
  function automatic bit gen_regime_window(string group, string value, output int unsigned lo, output int unsigned hi);
    lo = 0; hi = 0;
    if (group == "gnt_delay" && value == "same_cycle") begin lo = 0; hi = 0; return 1'b1; end
    if (group == "gnt_delay" && value == "short") begin lo = 1; hi = 3; return 1'b1; end
    if (group == "gnt_delay" && value == "long") begin lo = 4; hi = 32; return 1'b1; end
    if (group == "gnt_delay" && value == "random") begin lo = 0; hi = 32; return 1'b1; end
    if (group == "rvalid_delay" && value == "min1") begin lo = 1; hi = 1; return 1'b1; end
    if (group == "rvalid_delay" && value == "short") begin lo = 2; hi = 4; return 1'b1; end
    if (group == "rvalid_delay" && value == "long") begin lo = 5; hi = 32; return 1'b1; end
    if (group == "rvalid_delay" && value == "random") begin lo = 1; hi = 32; return 1'b1; end
    return 1'b0;
  endfunction
  function automatic bit gen_regime_scalar(string group, string value, output int unsigned v);
    v = 0;
    if (group == "dbg_event_mean" && value == "none") begin v = 0; return 1'b1; end
    if (group == "dbg_event_mean" && value == "sparse") begin v = 5000; return 1'b1; end
    if (group == "dbg_event_mean" && value == "storm") begin v = 200; return 1'b1; end
    if (group == "irq_event_mean" && value == "quiet") begin v = 0; return 1'b1; end
    if (group == "irq_event_mean" && value == "sparse") begin v = 2000; return 1'b1; end
    if (group == "irq_event_mean" && value == "storm") begin v = 100; return 1'b1; end
    if (group == "outstanding_cap" && value == "cap1") begin v = 1; return 1'b1; end
    if (group == "outstanding_cap" && value == "cap2") begin v = 2; return 1'b1; end
    if (group == "outstanding_cap" && value == "cap4") begin v = 4; return 1'b1; end
    if (group == "outstanding_cap" && value == "cap8") begin v = 8; return 1'b1; end
    if (group == "rate_per_mille" && value == "none") begin v = 0; return 1'b1; end
    if (group == "rate_per_mille" && value == "rare") begin v = 2; return 1'b1; end
    if (group == "rate_per_mille" && value == "frequent") begin v = 50; return 1'b1; end
    return 1'b0;
  endfunction
  // TB constants (values predicted by rtl-arch T-051 where noted; bring-up confirms). A derived constant
  // keeps its SV expression; its _PY twin is the literal Python and C use (gen_tb_top fatals when they differ).
  parameter int unsigned GEN_ICACHE_NUM_FB = 4;  // icache fill buffers, the one re-typed localparam NUM_FB (rtl/ibex_icache.sv:72)
  parameter int unsigned GEN_IBUS_MAX_OUTSTANDING = GEN_ICACHE_NUM_FB * ibex_pkg::IC_LINE_BEATS;  // instruction beats in flight (NUM_FB x IC_LINE_BEATS; rtl-arch T-051 2.3)
  parameter int unsigned GEN_IBUS_MAX_OUTSTANDING_PY = 8;  // rendered from rtl/ibex_pkg.sv (ibus_max_outstanding)
  parameter int unsigned GEN_DBUS_MAX_OUTSTANDING = 2;  // data beats in flight, the two halves of one split access (rtl/ibex_load_store_unit.sv:403-405)
  parameter int unsigned GEN_CSR_WRITE_TO_RVFI_OFFSET = 2;  // cycles from a CSR-write commit edge to its RVFI record (v3 T-051 2.1, predicted, pinned by a directed test)
  parameter int unsigned GEN_TRAP_TO_RVFI_OFFSET = 1;  // cycles from a trap/mret/dret commit edge to its RVFI record (v3 T-051 2.1)
  parameter int unsigned GEN_FETCH_EN_DRAIN_CYCLES = 64;  // cycles after fetch_enable_i leaves On within which the pipeline's in-flight instructions may still retire; a record later than that is a fetch_en failure
  parameter int unsigned GEN_LSU_TRAP_TO_RVFI_OFFSET = 0;  // cycles from a load/store fault's commit edge to its RVFI record: the fault is seen in WB, so its record and the controller's save edge share a cycle
  parameter int unsigned GEN_IRQ_MARKER_TO_RVFI_OFFSET = 2;  // cycles from the interrupt entry commit to the rvfi_ext_irq_valid marker (v3 T-051 2.1)
  parameter int unsigned GEN_RVFI_ID_EXIT_OFFSET = 2;  // cycles from ID exit (rvfi_ext_mcycle sample point, rtl/ibex_core.sv:2102) to the record, plus the WB wait for loads/stores (v3 T-051 2.2)
  parameter int unsigned GEN_ICACHE_ECC_WINDOW = 2;  // alert_minor_o within 1..2 cycles counted from the lookup request that returns corrupted data (the RAM read lands one cycle after the request, the alert one cycle after the check): 1 is the latency observed on every retained injection run (gen_tdd_step2b.md Section 14, every pulse at 1), 2 the declared bound, not observed; no run had alert_minor_o high before the injection hook existed; the misc checker and the protocol SVA use the same value
  parameter int unsigned GEN_ICACHE_ECC_GRACE_CYCLES = 16;  // cycles after a cpuctrlsts.icache_enable write record or after the last invalidation-sweep tag write during which a tag-RAM ECC injection is not owed an alert_minor_o pulse: a lookup made while the cache is disabled or invalidating reads the tag RAM but is not checked (rtl/ibex_icache.sv:266), and the TB learns both states late (the write from its record, the sweep from its all-ways tag writes)
  parameter int unsigned GEN_ICRAM_UNINIT_Q_DEPTH = ibex_pkg::IC_NUM_LINES * ibex_pkg::IC_NUM_WAYS;  // bound of the never-written data-line report queue: every data line of every way is reported at most once, so this depth holds every event a run can produce and the queue cannot evict; a drop is a TB defect and the misc monitor counts it
  parameter int unsigned GEN_ICRAM_UNINIT_Q_DEPTH_PY = 512;  // rendered from rtl/ibex_pkg.sv (icram_lines_x_ways)
  parameter int unsigned GEN_ICACHE_RETIRE_WINDOW = 64;  // cycles after a data-RAM ECC injection within which the misc monitor waits for the retirement that reveals the lookup tag through its pc (form b, the measured-run judge: the first retirement whose pc index equals the injected index); an injection with no such retirement is reported unjudged (a squashed speculative lookup)
  parameter int unsigned GEN_IRQ_ENTRY_BOUND_RECORDS = 17;  // records between a pin edge and the interrupt entry, worst case WB + ID + 16 Zcmp micro-ops (v3 T-051 2.6)
  parameter int unsigned GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES = 2;  // cycles a record costs beyond its bus waits: the pipeline's own fetch-to-retire stages, the WB and ID pair the record bound is derived from
  parameter int unsigned GEN_IRQ_DRAIN_MARGIN_CYCLES = 40;  // margin on the interrupt-entry drain cap: the finish handshake and the last record's write-back after the drain's final retirement
  parameter int unsigned GEN_DBG_ENTRY_BOUND_RECORDS = 17;  // records between debug_req_i and the debug entry, same derivation (v3 T-051 2.6)
  parameter int unsigned GEN_CLK_PERIOD_NS = 10;  // TB clock period (gen_tb_top ClkHalfPeriodNs = 5); Python converts cycle budgets to ns with it
  parameter int unsigned GEN_MEM_READBACK_WORDS_DEFAULT = 64;  // default MEM_PEEK read-back sample size (+gen_mem_readback_words)
  parameter int unsigned GEN_ALIVE_TIMEOUT_CYCLES_DEFAULT = 100000;  // default alive watchdog (+gen_alive_timeout)
  parameter int unsigned GEN_FINISH_TIMEOUT_CYCLES_DEFAULT = 20000;  // default finish-handshake budget (+gen_finish_timeout)
  parameter int unsigned GEN_IRQ_FAST_W = $bits(GEN_IRQS_ZERO.irq_fast);  // fast interrupt lines (width of ibex_pkg::irqs_t.irq_fast)
  parameter int unsigned GEN_IRQ_FAST_W_PY = 15;  // rendered from rtl/ibex_pkg.sv (irq_fast_w)
  parameter logic [31:0] GEN_IRQ_FAST_MASK = ((32'h1 << GEN_IRQ_FAST_W) - 1) << 16;  // mie/mip fast interrupt bits 16..16+GEN_IRQ_FAST_W-1 (platform-specific interrupts start at bit 16); the shim installs them in gen_mie_csr_t
  parameter logic [31:0] GEN_IRQ_FAST_MASK_PY = 2147418112;  // rendered from rtl/ibex_pkg.sv (irq_fast_mask)
  parameter logic [31:0] GEN_CSR_MARCHID_VALUE = ibex_pkg::CSR_MARCHID_VALUE;  // marchid the DUT reports (rtl/ibex_pkg.sv CSR_MARCHID_VALUE); the shim installs it as a read-only CSR
  parameter logic [31:0] GEN_CSR_MARCHID_VALUE_PY = 22;  // rendered from rtl/ibex_pkg.sv (csr_marchid_value)
  parameter logic [11:0] GEN_CSR_CPUCTRLSTS = ibex_pkg::CSR_CPUCTRLSTS;  // custom CSR address cpuctrlsts (rtl/ibex_pkg.sv); the shim's masked CSR with the ic_scr_key_valid status bit
  parameter logic [11:0] GEN_CSR_CPUCTRLSTS_PY = 1984;  // rendered from rtl/ibex_pkg.sv (csr_addr_cpuctrlsts)
  parameter logic [11:0] GEN_CSR_SECURESEED = ibex_pkg::CSR_SECURESEED;  // custom CSR address secureseed (rtl/ibex_pkg.sv); reads 0 in the shim
  parameter logic [11:0] GEN_CSR_SECURESEED_PY = 1985;  // rendered from rtl/ibex_pkg.sv (csr_addr_secureseed)
  parameter int unsigned GEN_MHPM_COUNTER_NUM = 10;  // MHPMCounterNum of the build (Runtime's -pvalue; gen_tb_top fatals when u_dut.MHPMCounterNum differs); the shim's mhpmevent values and the counter sync use it
  parameter logic [31:0] GEN_INSN_MRET = 807403635;  // mret encoding (privileged spec); plan C-1: its RVFI pc_wdata is pc + 4, so isa_pc_next and the export continuity rule skip it
  parameter logic [31:0] GEN_INSN_DRET = 2065694835;  // dret encoding (debug spec); plan C-1 as for mret
  parameter logic [31:0] GEN_TDATA1_IBEX_RDATA = 671092808;  // tdata1 read value with execute = 0: type 2, dmode 1, action 1, m and u (rtl/ibex_cs_registers.sv:1848-1864); bit 2 is the stored execute flag; the codegen verifies this literal against the RTL assign at every render
  parameter int unsigned GEN_CPUCTRLSTS_SYNC_EXC_SEEN_BIT = 6;  // cpuctrlsts.sync_exc_seen bit (cpu_ctrl_sts_part_t, rtl/ibex_cs_registers.sv:239-246); the shim sets and clears it from the model's traps
  parameter int unsigned GEN_CPUCTRLSTS_DOUBLE_FAULT_SEEN_BIT = 7;  // cpuctrlsts.double_fault_seen bit (cpu_ctrl_sts_part_t, rtl/ibex_cs_registers.sv:239-246)
  parameter int unsigned GEN_CPUCTRLSTS_ICACHE_ENABLE_BIT = 0;  // cpuctrlsts.icache_enable bit (cpu_ctrl_sts_part_t, rtl/ibex_cs_registers.sv:239-246); the scoreboard publishes the written value to gen_icram_events for the ECC-injection qualification
  parameter int unsigned GEN_CPUCTRLSTS_DATA_IND_TIMING_BIT = 1;  // cpuctrlsts.data_ind_timing bit (cpu_ctrl_sts_part_t, rtl/ibex_cs_registers.sv:239-246); the fcov sampler tracks it from the cpuctrlsts write records for the divider's DIT class (CG-MUL-004)
  parameter int unsigned GEN_CPUCTRLSTS_DUMMY_INSTR_EN_BIT = 2;  // cpuctrlsts.dummy_instr_en bit (cpu_ctrl_sts_part_t, rtl/ibex_cs_registers.sv:239-246); the Zcmp collector reads it from the model
  parameter int unsigned GEN_DCSR_PRV_BIT_LOW = 0;  // dcsr.prv field low bit (rtl/ibex_pkg.sv dcsr_t prv[1:0]); the dbg_dret rule compares the record's mode with it
  parameter int unsigned GEN_DCSR_PRV_BIT_HIGH = 1;  // dcsr.prv field high bit (rtl/ibex_pkg.sv dcsr_t prv[1:0])
  parameter int unsigned GEN_CAUSE_NMI_EXTERNAL = 2147483679;  // mcause of an external NMI entry (irq_ext, rtl/ibex_cs_registers.sv:905-945); the shim writes it when it emulates the entry
  parameter int unsigned GEN_CAUSE_NMI_INTERNAL = 4294967264;  // mcause of an internal NMI entry (irq_int, an integrity error; rtl/ibex_cs_registers.sv:905-945)
  parameter int unsigned GEN_MEM_ERR_ARM_KIND_ERR = 1;  // MEM_ERR_ARM arg3[7:0] kind: bus error response (gen_bus_driver::arm_err)
  parameter int unsigned GEN_BUS_ERR_LOG_DEPTH = 256;  // TB-local bound of the announced data-bus error queue (gen_bus_err_log), not a DUT property
  parameter int unsigned GEN_BUS_ERR_DRAIN_CYCLES = 96;  // cycles an announced data-bus error may still await its trap record at the end of the run before the leftover referee counts it: the announcement is stamped at the first transaction's grant, the second half of a split access then waits its own grant window (at most 32, regime_windows.gnt_delay), its response the rvalid window (at most 32), and 32 more cover the response-to-record lag with margin; a longer window must raise it
  parameter int unsigned GEN_NMI_INT_ENTRY_BOUND_RECORDS = 4;  // TB-side bound: records outside NMI mode and outside debug mode within which an announced data-side integrity corruption must produce the internal NMI entry; the RTL path is the pending bit set at the response and taken at the next handle_irq window (rtl/ibex_controller.sv:391-430, :498), the value is tuned from the observed 2-3 records (landing 2a / 2c)
  parameter int unsigned GEN_MEM_ERR_ARM_KIND_INTG = 2;  // MEM_ERR_ARM arg3[7:0] kind: integrity corruption of the response
  parameter int unsigned GEN_ISA_FAULT_KIND_FETCH = 0;  // gen_isa_arm_fault kind: instruction fetch (shim fault_hits)
  parameter int unsigned GEN_ISA_FAULT_KIND_LOAD = 1;  // gen_isa_arm_fault kind: load
  parameter int unsigned GEN_ISA_FAULT_KIND_STORE = 2;  // gen_isa_arm_fault kind: store
  // TB memory map: DM windows from gen_dut_top.sv, program window from gen_link.ld, MMIO page from the yaml.
  parameter logic [31:0] GEN_MM_BOOT_ADDR_DEFAULT = 32'h8000_0000;
  parameter logic [31:0] GEN_MM_BOOT_PAGE_MASK = 32'hffff_ff00;
  parameter logic [31:0] GEN_MM_BOOT_RESET_OFFSET = 32'h0000_0080;
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
  parameter logic [31:0] GEN_MM_SIG_SIZE = 32'h0000_0100;
  parameter logic [31:0] GEN_MM_IRQ_ACK_ADDR = 32'h8fff_f100;
  parameter logic [31:0] GEN_MM_IRQ_ACK_SIZE = 32'h0000_0004;
  parameter logic [31:0] GEN_MM_EOT_ADDR = 32'h8fff_f104;
  parameter logic [31:0] GEN_MM_EOT_SIZE = 32'h0000_0004;
  parameter logic [31:0] GEN_MM_PHASE_MARK_ADDR = 32'h8fff_f108;
  parameter logic [31:0] GEN_MM_PHASE_MARK_SIZE = 32'h0000_0004;
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
  parameter logic [7:0] GEN_CMD_EXPORT_FLUSH = 8'd12;
  parameter logic [7:0] GEN_CMD_COV_WITNESS = 8'd13;
  parameter logic [7:0] GEN_CMD_FCOV_SELFTEST = 8'd14;
  parameter logic [7:0] GEN_CMD_FCOV_QUERY = 8'd15;
  function automatic string gen_cmd_name(logic [7:0] kind);
    case (kind)
      8'd1: return "IRQ_SET";
      8'd2: return "IRQ_CLR";
      8'd3: return "NMI_PULSE";
      8'd4: return "DBG_REQ";
      8'd5: return "REGIME_SET";
      8'd6: return "KEY_MODE";
      8'd7: return "MEM_ERR_ARM";
      8'd8: return "ICACHE_ECC_ARM";
      8'd9: return "FETCH_EN";
      8'd10: return "MEM_PEEK";
      8'd11: return "MISC";
      8'd12: return "EXPORT_FLUSH";
      8'd13: return "COV_WITNESS";
      8'd14: return "FCOV_SELFTEST";
      8'd15: return "FCOV_QUERY";
      default: return $sformatf("UNKNOWN(%0d)", kind);
    endcase
  endfunction
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
  parameter int GEN_KNOB_ID_ICACHE_DATA_ECC_ERR_RATE = 15;
  parameter int GEN_KNOB_ID_ICACHE_ECC_BITS = 16;
  parameter int GEN_KNOB_ID_FETCH_ENABLE_REGIME = 17;
  parameter int GEN_KNOB_ID_MCOUNTEREN_WRITABLE = 18;
  parameter int GEN_KNOB_ID_INSTR_MIX = 19;
  parameter int GEN_KNOB_ID_PRIV_REGIME = 20;
  parameter int GEN_KNOB_ID_PMP_REGIME = 21;
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
      15: return "knob_icache_data_ecc_err_rate";
      16: return "knob_icache_ecc_bits";
      17: return "knob_fetch_enable_regime";
      18: return "knob_mcounteren_writable";
      19: return "knob_instr_mix";
      20: return "knob_priv_regime";
      21: return "knob_pmp_regime";
      default: return "";
    endcase
  endfunction
  // REGIME_SET consumer per knob (yaml regime_set_consumer): the dispatcher refuses a knob without a run-time consumer.
  function automatic string gen_knob_consumer(int id);
    case (id)
      0: return "bus";
      1: return "bus";
      2: return "bus";
      3: return "bus";
      4: return "bus";
      5: return "bus";
      6: return "bus";
      7: return "bus";
      8: return "bus";
      9: return "irq";
      10: return "irq";
      11: return "irq";
      12: return "dbg";
      13: return "scrkey";
      14: return "none";
      15: return "none";
      16: return "none";
      17: return "none";
      18: return "none";
      19: return "program";
      20: return "program";
      21: return "program";
      default: return "";
    endcase
  endfunction
  function automatic bit gen_knob_regime_set_consumed(int id);
    case (id)
      0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13: return 1'b1;
      default: return 1'b0;
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
      15: case (idx) 0: return "none"; 1: return "rare"; 2: return "frequent"; default: return ""; endcase
      16: case (idx) 0: return "one"; 1: return "two"; default: return ""; endcase
      17: case (idx) 0: return "always_on"; 1: return "toggling"; default: return ""; endcase
      18: case (idx) 0: return "on"; 1: return "off"; 2: return "invalid"; default: return ""; endcase
      19: case (idx) 0: return "isa_only"; 1: return "m_heavy"; 2: return "compressed_heavy"; 3: return "bitmanip_heavy"; 4: return "csr_heavy"; 5: return "ls_heavy"; 6: return "branch_heavy"; 7: return "mixed"; default: return ""; endcase
      20: case (idx) 0: return "m_only"; 1: return "u_heavy"; 2: return "alternating"; default: return ""; endcase
      21: case (idx) 0: return "off"; 1: return "sparse"; 2: return "dense"; 3: return "mml_on"; default: return ""; endcase
      default: return "";
    endcase
  endfunction
  // Record and event export (architecture Section 9): the header's field lists, the event sources and rows.
  parameter string GEN_EXPORT_RECORD_FIELDS = "order,pc_rdata,pc_wdata,insn,trap,halt,intr,mode,ixl,rs1_addr,rs1_rdata,rs2_addr,rs2_rdata,rs3_addr,rs3_rdata,rd_addr,rd_wdata,mem_addr,mem_rmask,mem_wmask,mem_rdata,mem_wdata,ext_pre_mip,ext_post_mip,ext_nmi,ext_nmi_int,ext_debug_req,ext_debug_mode,ext_rf_wr_suppress,ext_ic_scr_key_valid,ext_irq_valid,ext_exp_valid,ext_exp_insn,ext_exp_last,ext_mcycle,cycle";
  parameter string GEN_EXPORT_COUNTER_FIELDS = "mhpmcounter3,mhpmcounter4,mhpmcounter5,mhpmcounter6,mhpmcounter7,mhpmcounter8,mhpmcounter9,mhpmcounter10,mhpmcounter11,mhpmcounter12,mhpmcounter3h,mhpmcounter4h,mhpmcounter5h,mhpmcounter6h,mhpmcounter7h,mhpmcounter8h,mhpmcounter9h,mhpmcounter10h,mhpmcounter11h,mhpmcounter12h";
  parameter string GEN_EXPORT_SOURCES = "ibus,dbus,pin,alert,misc,icram,scrkey,regime";
  parameter string GEN_EXPORT_ACTIVE_SOURCES = "ibus,dbus,pin,alert,misc,scrkey,regime";  // sources with a writer in this build (yaml export_active_sources)
  function automatic bit gen_export_source_active(string s);
    case (s)
      "ibus", "dbus", "pin", "alert", "misc", "scrkey", "regime": return 1'b1;
      default: return 1'b0;
    endcase
  endfunction
  function automatic bit gen_export_source_known(string s);
    case (s)
      "ibus", "dbus", "pin", "alert", "misc", "icram", "scrkey", "regime": return 1'b1;
      default: return 1'b0;
    endcase
  endfunction
  // The `# events <source> <event> <fields>` header rows of one source, newline-terminated.
  function automatic string gen_export_event_header(string source);
    case (source)
      "ibus": return "# events ibus req addr,we,be\n# events ibus gnt addr,we,be,req_cycle,outstanding_after\n# events ibus rvalid addr,we,err,intg_injected,outstanding_after\n";
      "dbus": return "# events dbus req addr,we,be\n# events dbus gnt addr,we,be,req_cycle,outstanding_after\n# events dbus rvalid addr,we,err,intg_injected,outstanding_after\n";
      "pin": return "# events pin irq_software value\n# events pin irq_timer value\n# events pin irq_external value\n# events pin irq_fast idx,value\n# events pin irq_nm value\n# events pin debug_req value\n# events pin fetch_enable value\n# events pin mcounteren_writable value\n";
      "alert": return "# events alert alert_minor value\n# events alert alert_major_bus value\n# events alert alert_major_internal value\n# events alert double_fault_seen value\n";
      "misc": return "# events misc irq_pending value\n# events misc irq_entry order,cause,decidable\n# events misc core_busy value\n# events misc crash_dump_current_pc value\n# events misc crash_dump_next_pc value\n# events misc crash_dump_last_data_addr value\n# events misc crash_dump_exception_pc value\n# events misc crash_dump_exception_addr value\n";
      "icram": return "# events icram inject way,index\n# events icram lookup index\n# events icram tag_write way,index,valid\n# events icram fill_write way,index\n";
      "scrkey": return "# events scrkey req value\n# events scrkey valid value\n";
      "regime": return "# events regime phase knob_id,value_idx,phase_idx\n";
      default: return "";
    endcase
  endfunction
  parameter string GEN_EXPORT_ROWS = "ibus/req,ibus/gnt,ibus/rvalid,dbus/req,dbus/gnt,dbus/rvalid,pin/irq_software,pin/irq_timer,pin/irq_external,pin/irq_fast,pin/irq_nm,pin/debug_req,pin/fetch_enable,pin/mcounteren_writable,alert/alert_minor,alert/alert_major_bus,alert/alert_major_internal,alert/double_fault_seen,misc/irq_pending,misc/irq_entry,misc/core_busy,misc/crash_dump_current_pc,misc/crash_dump_next_pc,misc/crash_dump_last_data_addr,misc/crash_dump_exception_pc,misc/crash_dump_exception_addr,icram/inject,icram/lookup,icram/tag_write,icram/fill_write,scrkey/req,scrkey/valid,regime/phase";  // every (source, event) row, yaml order
  // The `# events <source> <event> <fields>` header row of ONE (source, event), newline-terminated; empty when unknown.
  function automatic string gen_export_row_header(string source, string ev);
    case ({source, "/", ev})
      "ibus/req": return "# events ibus req addr,we,be\n";
      "ibus/gnt": return "# events ibus gnt addr,we,be,req_cycle,outstanding_after\n";
      "ibus/rvalid": return "# events ibus rvalid addr,we,err,intg_injected,outstanding_after\n";
      "dbus/req": return "# events dbus req addr,we,be\n";
      "dbus/gnt": return "# events dbus gnt addr,we,be,req_cycle,outstanding_after\n";
      "dbus/rvalid": return "# events dbus rvalid addr,we,err,intg_injected,outstanding_after\n";
      "pin/irq_software": return "# events pin irq_software value\n";
      "pin/irq_timer": return "# events pin irq_timer value\n";
      "pin/irq_external": return "# events pin irq_external value\n";
      "pin/irq_fast": return "# events pin irq_fast idx,value\n";
      "pin/irq_nm": return "# events pin irq_nm value\n";
      "pin/debug_req": return "# events pin debug_req value\n";
      "pin/fetch_enable": return "# events pin fetch_enable value\n";
      "pin/mcounteren_writable": return "# events pin mcounteren_writable value\n";
      "alert/alert_minor": return "# events alert alert_minor value\n";
      "alert/alert_major_bus": return "# events alert alert_major_bus value\n";
      "alert/alert_major_internal": return "# events alert alert_major_internal value\n";
      "alert/double_fault_seen": return "# events alert double_fault_seen value\n";
      "misc/irq_pending": return "# events misc irq_pending value\n";
      "misc/irq_entry": return "# events misc irq_entry order,cause,decidable\n";
      "misc/core_busy": return "# events misc core_busy value\n";
      "misc/crash_dump_current_pc": return "# events misc crash_dump_current_pc value\n";
      "misc/crash_dump_next_pc": return "# events misc crash_dump_next_pc value\n";
      "misc/crash_dump_last_data_addr": return "# events misc crash_dump_last_data_addr value\n";
      "misc/crash_dump_exception_pc": return "# events misc crash_dump_exception_pc value\n";
      "misc/crash_dump_exception_addr": return "# events misc crash_dump_exception_addr value\n";
      "icram/inject": return "# events icram inject way,index\n";
      "icram/lookup": return "# events icram lookup index\n";
      "icram/tag_write": return "# events icram tag_write way,index,valid\n";
      "icram/fill_write": return "# events icram fill_write way,index\n";
      "scrkey/req": return "# events scrkey req value\n";
      "scrkey/valid": return "# events scrkey valid value\n";
      "regime/phase": return "# events regime phase knob_id,value_idx,phase_idx\n";
      default: return "";
    endcase
  endfunction
  // Every legal +gen_* plusarg name; gen_base_test fatals on any other +gen_* argument (A-23).
  function automatic bit gen_is_known_plusarg(string name);
    case (name)
      "gen_build_config", "gen_smoke_cycles", "gen_smoke_intg_flip", "gen_dbg_csr_probe", "gen_mem_image", "gen_mem_image_crc32", "gen_mem_image_words", "gen_mem_readback_words", "gen_tohost_addr", "gen_mem_unmapped_ok", "gen_boot_addr", "gen_hart_id", "gen_alive_timeout", "gen_finish_timeout", "gen_regime_sched", "gen_rvfi_trace", "gen_fcov_en", "gen_icram_init", "gen_fetch_en_at_reset", "gen_key_reset_valid", "gen_sb_trace", "gen_isa_pc_next_mask_b13", "gen_isa_string", "gen_isa_log", "gen_export_file", "gen_export_counters", "gen_export_sources", "gen_export_flush_every", "gen_ut_boot_retire", "gen_ut_fcov_query", "gen_ut_fcov_expect", "gen_ut_rows_set", "gen_ibus_gnt_min", "gen_ibus_gnt_max", "gen_ibus_rvalid_min", "gen_ibus_rvalid_max", "gen_ibus_max_outstanding", "gen_ibus_err_rate", "gen_ibus_intg_err_rate", "gen_ibus_intg_bits", "gen_ibus_err_window", "gen_dbus_gnt_min", "gen_dbus_gnt_max", "gen_dbus_rvalid_min", "gen_dbus_rvalid_max", "gen_dbus_max_outstanding", "gen_dbus_err_rate", "gen_dbus_intg_err_rate", "gen_dbus_intg_bits", "gen_dbus_err_window", "gen_dbus_err_half", "gen_dbus_err_store_perform", "gen_key_delay_min", "gen_key_delay_max", "gen_key_never_cycles", "gen_irq_min_gap", "gen_irq_hold_min", "gen_irq_hold_max", "gen_dbg_hold_min", "gen_dbg_hold_max", "gen_knob_imem_gnt_delay", "gen_knob_imem_rvalid_delay", "gen_knob_imem_err_rate", "gen_knob_imem_intg_err_rate", "gen_knob_imem_outstanding_cap", "gen_knob_dmem_gnt_delay", "gen_knob_dmem_rvalid_delay", "gen_knob_dmem_err_rate", "gen_knob_dmem_intg_err_rate", "gen_knob_irq_regime", "gen_knob_irq_line_mix", "gen_knob_irq_hold", "gen_knob_debug_req_regime", "gen_knob_scr_key_delay", "gen_knob_icache_ecc_err_rate", "gen_knob_icache_data_ecc_err_rate", "gen_knob_icache_ecc_bits", "gen_knob_fetch_enable_regime", "gen_knob_mcounteren_writable", "gen_knob_instr_mix", "gen_knob_priv_regime", "gen_knob_pmp_regime", "gen_chk_all", "gen_chk_ibus_proto", "gen_chk_ibus_outstanding", "gen_chk_sva_st", "gen_chk_sva_ibus", "gen_chk_sva_dbus", "gen_chk_sva_icram", "gen_chk_sva_scrkey", "gen_chk_sva_irq", "gen_chk_sva_dbg", "gen_chk_sva_alert", "gen_chk_sva_rvfi", "gen_chk_sva_b8", "gen_probe_ic_lookup", "gen_chk_sva_rvalid_legal", "gen_chk_dbus_proto", "gen_chk_dbus_outstanding", "gen_chk_dbus_split", "gen_chk_dbus_store_intg", "gen_chk_icram_write_ecc", "gen_chk_icram_inval_sweep", "gen_chk_icram_ecc_response", "gen_chk_scrkey_proto", "gen_chk_alert_minor", "gen_chk_alert_bus", "gen_chk_alert_internal", "gen_chk_crash_dump", "gen_chk_double_fault", "gen_chk_core_busy", "gen_chk_data_tag_quiet", "gen_chk_fetch_en", "gen_chk_irq_pending", "gen_chk_irq_entry", "gen_chk_irq_masked", "gen_chk_nmi_entry", "gen_chk_nmi_internal", "gen_chk_dbg_entry", "gen_chk_dbg_exc", "gen_chk_dbg_masked", "gen_chk_dbg_dret", "gen_chk_dbg_trigger", "gen_chk_ctr_mcycle", "gen_chk_ctr_minstret", "gen_chk_ctr_hpm_exact", "gen_chk_ctr_hpm_bound", "gen_chk_pmp_data", "gen_chk_pmp_fetch", "gen_chk_isa", "gen_chk_isa_pc", "gen_chk_isa_insn", "gen_chk_isa_trap", "gen_chk_isa_rd", "gen_chk_isa_mem", "gen_chk_isa_prv", "gen_chk_isa_pc_next", "gen_chk_isa_csr", "gen_chk_rvfi_proto", "gen_chk_t022_never", "gen_chk_bridge_accounting": return 1'b1;
      default: return 1'b0;
    endcase
  endfunction
  // A bool knob needs an explicit =0/=1 (a bare +gen_<bool> would otherwise be a silent no-op).
  function automatic bit gen_is_bool_plusarg(string name);
    case (name)
      "gen_dbg_csr_probe", "gen_mem_unmapped_ok", "gen_rvfi_trace", "gen_fcov_en", "gen_fetch_en_at_reset", "gen_key_reset_valid", "gen_sb_trace", "gen_isa_pc_next_mask_b13", "gen_export_counters", "gen_dbus_err_store_perform", "gen_chk_all", "gen_chk_ibus_proto", "gen_chk_ibus_outstanding", "gen_chk_sva_st", "gen_chk_sva_ibus", "gen_chk_sva_dbus", "gen_chk_sva_icram", "gen_chk_sva_scrkey", "gen_chk_sva_irq", "gen_chk_sva_dbg", "gen_chk_sva_alert", "gen_chk_sva_rvfi", "gen_chk_sva_b8", "gen_probe_ic_lookup", "gen_chk_sva_rvalid_legal", "gen_chk_dbus_proto", "gen_chk_dbus_outstanding", "gen_chk_dbus_split", "gen_chk_dbus_store_intg", "gen_chk_icram_write_ecc", "gen_chk_icram_inval_sweep", "gen_chk_icram_ecc_response", "gen_chk_scrkey_proto", "gen_chk_alert_minor", "gen_chk_alert_bus", "gen_chk_alert_internal", "gen_chk_crash_dump", "gen_chk_double_fault", "gen_chk_core_busy", "gen_chk_data_tag_quiet", "gen_chk_fetch_en", "gen_chk_irq_pending", "gen_chk_irq_entry", "gen_chk_irq_masked", "gen_chk_nmi_entry", "gen_chk_nmi_internal", "gen_chk_dbg_entry", "gen_chk_dbg_exc", "gen_chk_dbg_masked", "gen_chk_dbg_dret", "gen_chk_dbg_trigger", "gen_chk_ctr_mcycle", "gen_chk_ctr_minstret", "gen_chk_ctr_hpm_exact", "gen_chk_ctr_hpm_bound", "gen_chk_pmp_data", "gen_chk_pmp_fetch", "gen_chk_isa", "gen_chk_isa_pc", "gen_chk_isa_insn", "gen_chk_isa_trap", "gen_chk_isa_rd", "gen_chk_isa_mem", "gen_chk_isa_prv", "gen_chk_isa_pc_next", "gen_chk_isa_csr", "gen_chk_rvfi_proto", "gen_chk_t022_never", "gen_chk_bridge_accounting": return 1'b1;
      default: return 1'b0;
    endcase
  endfunction
  parameter logic [31:0] GEN_BOOT_ADDR_DEFAULT = 32'h8000_0000;  // literal twin of GEN_MM_BOOT_ADDR_DEFAULT (regex readers: gen_program.py, gen_smoke_run.sh)
  // GEN_KNOBS_END

  // The interrupt-entry drain's cycle cap, COMPUTED from a run's effective bus maxima rather than frozen: the four
  // gen_{i,d}bus_{gnt,rvalid}_max plusargs overwrite the regime windows with only a lower clamp, so a constant taken
  // from the defaults would be wrong for any run that widens one. Worst legitimate per-record cost is the slower
  // bus's grant plus response wait plus the pipeline's own stages, times the DRAIN'S LENGTH, which is the
  // entry bound plus one record because the drain runs while the count is at or below the bound. The margin
  // is left to the finish handshake and the last write-back, so the extra record is not borrowed from it.
  function automatic int unsigned gen_irq_drain_cap_cycles(int unsigned i_gnt_max, int unsigned i_rvalid_max,
                                                           int unsigned d_gnt_max, int unsigned d_rvalid_max);
    int unsigned ibus_cost = i_gnt_max + i_rvalid_max;
    int unsigned dbus_cost = d_gnt_max + d_rvalid_max;
    int unsigned per_record = (ibus_cost > dbus_cost ? ibus_cost : dbus_cost) + GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES;
    return per_record * (GEN_IRQ_ENTRY_BOUND_RECORDS + 1) + GEN_IRQ_DRAIN_MARGIN_CYCLES;
  endfunction

  // Below the knobs region because the generator emits functions from its own templates and not from the yaml: this is
  // the window arithmetic all three CG-IC-006 window queries share, in one place so its boundary is unit-testable. A
  // cycle counts when it lies in ref+1 .. ref+span, the reference cycle itself excluded since the ECC check lands the
  // cycle after the read.
  function automatic bit gen_ic_in_window(int unsigned hit_cycle, int unsigned ref_cycle, int unsigned span);
    return hit_cycle > ref_cycle && (hit_cycle - ref_cycle) <= span;
  endfunction
  // ICache RAM model announcements (C3.4): the tag RAM models push their ECC injections here (one flipped bit of a lookup read,
  // at knob_icache_ecc_err_rate's rate) and gen_misc_monitor consumes them as the alert_minor_o expectation: a pulse needs an
  // injection within GEN_ICACHE_ECC_WINDOW, and a QUALIFIED injection owes a pulse. Qualified = the cache is enabled per the
  // scoreboard's cpuctrlsts tracking and no invalidation sweep is within GEN_ICACHE_ECC_GRACE_CYCLES: a lookup made while the
  // cache is disabled or invalidating reads the tag RAM but is not checked (rtl/ibex_icache.sv:266), and the TB sees both
  // states late (the enable from its record, the sweep from its all-ways tag writes).
  // gen_irq_view: the irq checker's own per-cycle sampled view of the interrupt pins, and the mie history it
  // judges against, published so a covergroup judges a cycle from the SAME samples rather than keeping a
  // second history with its own timestamp convention. Written by gen_irq_checker, read by the coverage class;
  // it lives here because gen_fcov_pkg compiles before gen_checkers_pkg and cannot hold a handle to it.
  parameter int unsigned GEN_IRQ_VIEW_SAMPLES = 256;   // cycles of pin samples kept; a read older than this fails and the caller says so
  parameter int unsigned GEN_IRQ_VIEW_MIE = 64;        // mie updates kept, the depth the checker used before this was shared
  class gen_irq_view;
    typedef struct { int unsigned cycle; logic [18:0] pins; bit pending; } smp_t;
    typedef struct { int unsigned eff_cycle; logic [31:0] mie; } mie_t;
    static smp_t q [$];
    static mie_t m [$];
    static function void clear();
      q.delete(); m.delete();
    endfunction
    static function void push_sample(int unsigned c, logic [18:0] pins, bit pending);
      q.push_back('{c, pins, pending});
      while (q.size() > GEN_IRQ_VIEW_SAMPLES) void'(q.pop_front());
    endfunction
    static function void push_mie(int unsigned eff_cycle, logic [31:0] mie);
      m.push_back('{eff_cycle, mie});
      while (m.size() > GEN_IRQ_VIEW_MIE) void'(m.pop_front());
    endfunction
    // the sampled pins of one cycle; 0 when that cycle has aged out of the window
    static function bit sample_at(int unsigned c, output logic [18:0] pins, output bit pending);
      for (int i = q.size() - 1; i >= 0; i--)
        if (q[i].cycle == c) begin pins = q[i].pins; pending = q[i].pending; return 1'b1; end
      return 1'b0;
    endfunction
    static function logic [31:0] mie_at(int unsigned c);
      logic [31:0] v = 32'h0;
      foreach (m[i]) if (m[i].eff_cycle <= c) v = m[i].mie;
      return v;
    endfunction
  endclass

  // gen_fetch_en_windows: closed fetch_enable_i Off windows, published by gen_misc_monitor which already
  // holds the Off cycle for its own drain check, so a covergroup consumes the window instead of detecting it
  // a second time from the same pin. A window is published when fetch_enable returns to On.
  parameter int unsigned GEN_FETCH_EN_WINDOW_MIN_CYCLES = 20;   // CG-IRQ-011 ev_off: windows shorter than this are not sampled
  class gen_fetch_en_windows;
    typedef struct { int unsigned off_cycle; int unsigned on_cycle; } win_t;
    static win_t q [$];
    static int unsigned published = 0, skipped_short = 0;
    static function void clear();
      q.delete(); published = 0; skipped_short = 0;
    endfunction
    static function void publish(int unsigned off_cycle, int unsigned on_cycle);
      if (on_cycle < off_cycle + GEN_FETCH_EN_WINDOW_MIN_CYCLES) begin skipped_short++; return; end
      q.push_back('{off_cycle, on_cycle});
      published++;
    endfunction
    static function bit take(output int unsigned off_cycle, output int unsigned on_cycle);
      win_t w;
      if (q.size() == 0) return 1'b0;
      w = q.pop_front(); off_cycle = w.off_cycle; on_cycle = w.on_cycle;
      return 1'b1;
    endfunction
  endclass

  class gen_icram_events;
    // an injection: kind inject (tag RAM) or inject_data (data RAM), the beat and the bits of the flip, every way's stored valid bit and
    // tag at the read (un-tweaked), and, once judged, the hit way and the verdicts (a: the P9 probe's tag; b: the retiring pc's tag)
    typedef struct { int unsigned cycle; int unsigned way; int unsigned index; string kind; bit qualified; bit seen; bit judged;
                     int unsigned beat; int unsigned bits; bit valid_w [GEN_IC_NUM_WAYS]; logic [31:0] tag_w [GEN_IC_NUM_WAYS];
                     int hit_way; int verdict; int verdict_b; int unsigned pulse_cycle; bit rose; bit closed;
                     bit en_ok; bit sweep_ok; bit sampled; } evt_t;   // rose: a flipped bit was 0 before (visible through the OR of duplicate copies)
    static evt_t q [$];
    static int unsigned inject_rate = 0;       // per mille per tag read, from knob_icache_ecc_err_rate (gen_env sets it; 0 = off)
    static int unsigned injected = 0;
    static int unsigned inject_rate_data = 0;  // per mille per data read, from knob_icache_data_ecc_err_rate
    static int unsigned inject_bits = 1;       // bits flipped per injection, from knob_icache_ecc_bits
    static int unsigned injected_data = 0;
    static logic [GEN_IC_TAG_ECC_W-1:0] tag_shadow [GEN_IC_NUM_WAYS][GEN_IC_NUM_LINES];   // the tag RAM contents as written (the DUT's tweaked words)
    static bit probe_on = 0; static int unsigned lk_cyc [$]; static logic [31:0] lk_tag [$];   // the lookup tag per cycle from the P9 probe
    static bit          icache_en = 0;         // cpuctrlsts.icache_enable as last written (reset value 0), with the record's cycle
    static int unsigned icache_en_cycle = 0;
    static bit          inval_seen = 0;        // an invalidation-sweep write seen: all ways at index 0, then consecutive indices on consecutive cycles (rtl/ibex_icache.sv INVAL_CACHE)
    static int unsigned last_inval_cycle = 0;
    static int unsigned last_tag_write_cycle = 0, tag_writes_this_cycle = 0;
    static int unsigned last_allways_cycle = 0; static int last_allways_index = -1;   // the previous all-ways write: a sweep continues it, an ECC correction does not
    static function void announce(int unsigned cycle, int unsigned way, int unsigned index, string kind, bit qualified = 1'b0,
                                  int unsigned beat = 0, int unsigned bits = 1, bit rose = 1'b1);
      evt_t e;
      e.cycle = cycle; e.way = way; e.index = index; e.kind = kind; e.qualified = qualified; e.seen = 1'b0; e.judged = 1'b0;
      e.beat = beat; e.bits = bits; e.hit_way = -1; e.verdict = -2; e.verdict_b = -2; e.pulse_cycle = 0; e.rose = rose; e.closed = 1'b0;
      e.en_ok = enabled_at(cycle); e.sweep_ok = sweep_clear_at(cycle); e.sampled = 1'b0;
      for (int w = 0; w < GEN_IC_NUM_WAYS; w++) begin e.valid_w[w] = shadow_valid(w, index); e.tag_w[w] = shadow_tag(w, index); end
      q.push_back(e);
      while (q.size() > 256) void'(q.pop_front());
    endfunction
    // Never-written data-RAM reads live in a queue of their OWN, never in q: the pulse attribution, the deferral and the
    // closure all iterate q, and every lookup reads both ways' data lines whether the cache is enabled or not, so an
    // unwritten-line read entering q would evict injections still waiting for their retirement verdict.
    typedef struct { int unsigned cycle; int unsigned way; int unsigned index; bit drained; } uninit_t;
    static uninit_t uq [$];
    static int unsigned uninit_reads = 0, uninit_dropped = 0;
    static function void note_uninit_read(int unsigned cycle, int unsigned way, int unsigned index);
      uninit_t e;
      uninit_reads++;
      if (uq.size() >= GEN_ICRAM_UNINIT_Q_DEPTH) begin uninit_dropped++; return; end
      e.cycle = cycle; e.way = way; e.index = index; e.drained = 1'b0;
      uq.push_back(e);
    endfunction
    // the two terms of the qualification, separately: cp_no_alert_case distinguishes disabled_cache from during_invalidation,
    // and the conjunction below is the same predicate qualified_at always applied
    static function bit enabled_at(int unsigned cycle);
      return icache_en && cycle >= icache_en_cycle + GEN_ICACHE_ECC_GRACE_CYCLES;
    endfunction
    static function bit sweep_clear_at(int unsigned cycle);
      return !(inval_seen && cycle < last_inval_cycle + GEN_ICACHE_ECC_GRACE_CYCLES);
    endfunction
    static function bit qualified_at(int unsigned cycle);
      return enabled_at(cycle) && sweep_clear_at(cycle);
    endfunction
    static function void note_icache_en(bit en, int unsigned cycle);
      icache_en = en; icache_en_cycle = cycle;
    endfunction
    // the DUT's tag tweak: the index at every beat's offset in the tag word (rtl/ibex_icache.sv gen_ecc_tag_tweak); stored words carry it
    static function logic [GEN_IC_TAG_ECC_W-1:0] tag_tweak(int unsigned index);
      logic [GEN_IC_TAG_ECC_W-1:0] t = '0;
      for (int i = 0; i < IC_LINE_BEATS; i++) t |= GEN_IC_TAG_ECC_W'(index) << (i * (IC_INDEX_W + IC_TAG_ECC_SIZE));
      return t;
    endfunction
    static function void note_tag_init(int unsigned way, int unsigned index, logic [GEN_IC_TAG_ECC_W-1:0] word); tag_shadow[way][index] = word; endfunction
    static function bit shadow_valid(int unsigned way, int unsigned index);   // the stored valid bit, un-tweaked
      logic [GEN_IC_TAG_ECC_W-1:0] w = tag_shadow[way][index] ^ tag_tweak(index); return w[IC_TAG_SIZE-1];
    endfunction
    static function logic [31:0] shadow_tag(int unsigned way, int unsigned index);   // the stored tag, un-tweaked
      logic [GEN_IC_TAG_ECC_W-1:0] w = tag_shadow[way][index] ^ tag_tweak(index); return 32'(w[IC_TAG_SIZE-2:0]);
    endfunction
    static function void note_lookup(int unsigned cycle, logic [31:0] tag);   // the P9 probe: the tag compared in this cycle
      probe_on = 1; lk_cyc.push_back(cycle); lk_tag.push_back(tag);
      if (lk_cyc.size() > 128) begin void'(lk_cyc.pop_front()); void'(lk_tag.pop_front()); end
    endfunction
    static function void q_set_hit(int unsigned cycle, int unsigned way, int hit_way);   // the judged hit way written back to the announcement
      foreach (q[i]) if (q[i].cycle == cycle && q[i].way == way && q[i].kind == "inject_data") q[i].hit_way = hit_way;
    endfunction
    static function bit lookup_tag_at(int unsigned cycle, output logic [31:0] tag);
      foreach (lk_cyc[i]) if (lk_cyc[i] == cycle) begin tag = lk_tag[i]; return 1'b1; end
      return 1'b0;
    endfunction
    static function void note_tag_write(int unsigned cycle, int unsigned ways, int unsigned index, int unsigned way, logic [GEN_IC_TAG_ECC_W-1:0] word);   // called by every tag RAM on its write
      tag_shadow[way][index] = word;
      if (cycle != last_tag_write_cycle) begin last_tag_write_cycle = cycle; tag_writes_this_cycle = 0; end
      tag_writes_this_cycle++;
      if (tag_writes_this_cycle >= ways) begin   // an all-ways write: the sweep (index 0, or the index after the previous one a cycle later) or an ECC correction of one lookup
        if (index == 0 || (last_allways_index >= 0 && cycle == last_allways_cycle + 1 && int'(index) == last_allways_index + 1)) begin inval_seen = 1; last_inval_cycle = cycle; end
        last_allways_cycle = cycle; last_allways_index = int'(index);
      end
    endfunction
  endclass

  // TB-injected data-bus errors (word addresses) and integrity corruptions announced by gen_bus_driver. The scoreboard arms
  // the model's fault only for an announced word, so a DUT fault on an access nobody corrupted fails as isa_trap (T-137);
  // the irq checker accepts an NMI-vector entry without a pin NMI only after an announced corruption (internal NMI).
  class gen_bus_err_log;
    typedef struct { logic [31:0] word; int unsigned cycle; } ann_t;
    static ann_t words [$];   // announced error words with the cycle of the grant (note() runs there, conservative for the drain window); the integrity announcements (note_intg / take_intg) are a separate one-slot counter, not in this queue; bounded to GEN_BUS_ERR_LOG_DEPTH (TB-local queue bound, not a DUT property)
    static int unsigned announced = 0, taken = 0;
    static int unsigned intg_announced = 0;   // data-side integrity corruptions: each raises the DUT's internal NMI (irq checker)
    static logic [31:0] intg_first_addr = '0;  // address of the corruption that set the DUT's pending bit (its mtval), until consumed
    static bit          intg_pending = 0;
    static logic [31:0] intg_words [$];   // announced corruptions by word: the suppressed-write record they explain consumes one (T-183)
    static function void note_intg(logic [31:0] addr, bit we = 1'b0);
      intg_announced++;
      if (!intg_pending) begin intg_pending = 1; intg_first_addr = addr; end
      if (!we) intg_words.push_back({addr[31:2], 2'b00});   // the gate's list holds loads only: a store's corruption never suppresses a write
      while (intg_words.size() > GEN_BUS_ERR_LOG_DEPTH) void'(intg_words.pop_front());
    endfunction
    static function bit take_intg_word(logic [31:0] addr);   // an announced corruption of that word, consumed
      logic [31:0] w = {addr[31:2], 2'b00};
      foreach (intg_words[i]) if (intg_words[i] == w) begin intg_words.delete(i); return 1'b1; end
      return 1'b0;
    endfunction
    static function logic [31:0] take_intg();   // the internal-NMI entry consumes the pending bit (rtl/ibex_controller.sv:407-411)
      intg_pending = 0; return intg_first_addr;
    endfunction
    static function void note(logic [31:0] addr, int unsigned cycle);
      ann_t a; a.word = {addr[31:2], 2'b00}; a.cycle = cycle;
      words.push_back(a); announced++;
      while (words.size() > GEN_BUS_ERR_LOG_DEPTH) void'(words.pop_front());
    endfunction
    // one announcement is one event: a trap consumes the oldest entry of each word its access touches; the result says
    // which words were announced (bit 0: the first word, bit 1: the second word of a spanning access), 0 for none
    static function logic [1:0] take(logic [31:0] addr, int unsigned bytes);
      logic [31:0] w0 = {addr[31:2], 2'b00};
      bit spans_two = (int'(addr[1:0]) + bytes) > 4;
      logic [1:0] hit = 2'b00;
      hit[0] = take_word(w0);
      if (spans_two) hit[1] = take_word(w0 + 4);
      return hit;
    endfunction
    static function bit take_word(logic [31:0] w);
      foreach (words[i]) if (words[i].word == w) begin
        words.delete(i); taken++; return 1'b1;
      end
      return 1'b0;
    endfunction
    // announcements older than the drain window at the end of the run: an injected error the DUT never trapped on
    static function int unsigned leftover(int unsigned now);
      int unsigned n = 0;
      foreach (words[i]) if (words[i].cycle + GEN_BUS_ERR_DRAIN_CYCLES < now) n++;
      return n;
    endfunction
  endclass

  // A load or store in either encoding with its access size (RVFI reports a compressed instruction in its 16-bit form;
  // Zcmp micro-op records carry the expanded 32-bit form). Zcb: c.lbu/c.lhu/c.lh/c.sb/c.sh (funct6 1000xx, quadrant 0).
  function automatic bit gen_insn_mem_access(logic [31:0] insn, output bit is_store, output int unsigned bytes);
    is_store = 0; bytes = 0;
    if (insn[1:0] == 2'b11) begin
      if (insn[6:0] != ibex_pkg::OPCODE_LOAD && insn[6:0] != ibex_pkg::OPCODE_STORE) return 0;
      is_store = (insn[6:0] == ibex_pkg::OPCODE_STORE); bytes = 32'h1 << insn[13:12]; return 1;
    end
    case (insn[1:0])
      2'b00: case (insn[15:13])
        3'b010: begin bytes = 4; return 1; end                 // c.lw
        3'b110: begin is_store = 1; bytes = 4; return 1; end   // c.sw
        3'b100: case (insn[12:10])
          3'b000: begin bytes = 1; return 1; end               // c.lbu
          3'b001: begin bytes = 2; return 1; end               // c.lhu / c.lh
          3'b010: begin is_store = 1; bytes = 1; return 1; end // c.sb
          3'b011: begin is_store = 1; bytes = 2; return 1; end // c.sh
          default: return 0;
        endcase
        default: return 0;
      endcase
      2'b10: case (insn[15:13])
        3'b010: begin bytes = 4; return 1; end                 // c.lwsp
        3'b110: begin is_store = 1; bytes = 4; return 1; end   // c.swsp
        default: return 0;
      endcase
      default: return 0;
    endcase
  endfunction

  // Every time-0 banner line starts with this tag so a log scanner can grep one token.
  parameter string GEN_BANNER_TAG = "GEN_CONFIG_BANNER";

  // The first fetch is {boot_addr_i[31:8], 8'h80} (rtl/ibex_if_stage.sv:243); gen_link.ld places the
  // program entry at GEN_MM_BOOT_PAGE + GEN_MM_BOOT_RESET_OFFSET (checked by gen_program.py and gen_knobs_codegen.py).

  // RV32I NOP = addi x0, x0, 0, composed from the ibex_pkg opcode so no encoding is re-typed.
  parameter logic [31:0] GEN_RV32_NOP = {12'd0, 5'd0, 3'b000, 5'd0, OPCODE_OP_IMM};

  // Cache RAM geometry the TB models must follow (ibex_pkg).
  parameter int unsigned GEN_IC_NUM_WAYS  = IC_NUM_WAYS;
  parameter int unsigned GEN_IC_NUM_LINES = IC_NUM_LINES;
  parameter int unsigned GEN_IC_TAG_ECC_W = IC_TAG_SIZE + IC_TAG_ECC_SIZE;   // the tag RAM word: tag with its valid bit, then the ECC bits
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
