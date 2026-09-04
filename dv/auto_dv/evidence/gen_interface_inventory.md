# ibex_core interface inventory (DUT = gen_dut_top wrapper around ibex_core + ibex_register_file_ff)

Committed reference (promoted 2026-09-04 from the rtl-arch working file
dv/auto_dv/work/rtl-arch/gen_interface_inventory.md, same content apart from this paragraph); when the working
copy changes, this copy is re-promoted, and the working copy is never copied over this one without carrying this
paragraph. The working-file names below (gen_behaviour_summaries.md) are this role's own gitignored sources,
named as provenance: no claim here rests on opening one, and every RTL fact is cited to its rtl/ file and line.

Owner: rtl-arch (T-003). Build configuration: opentitan (see gen_param_resolution.md for every
parameter value). Every claim cites doc/ or file:line. Items the docs do not cover are marked
"RTL-defined, unverified against doc". Items I could not confirm by reading are marked
UNVERIFIED-n and collected in section 12. Port list source: rtl/ibex_core.sv:61-191 (all ports
read in full); register file: rtl/ibex_register_file_ff.sv:51-86.

Conventions: "cycle" = posedge clk_i. All flops in the DUT use `posedge clk_i or negedge rst_ni`
(rst_ni is an asynchronous active-low reset, doc/02_user/integration.rst:282). Widths are for
this configuration: MemDataWidth = 39, RegFileDataWidth = 32 (39 if RegFileECC = 1),
RegFileCapEccWidth = 35 (42 if RegFileECC = 1), TagSizeECC = 28, LineSizeECC = 78, IC_INDEX_W = 8,
IC_NUM_WAYS = 2.

DUT boundary after wrapping (DV_prompt.txt Section 2 ruling): the wrapper instantiates the core
and the register file, connects the 12 rf_*/dummy_* ports between them (section 4), ties
cheriot_enable_i to ibex_pkg::IbexMuBiOff, and exposes every other ibex_core port. The icache
tag/data RAM ports and the scramble-key handshake (section 5) are exposed and served by TB test
equipment.

## 1. Clock, reset, static configuration, MuBi control

| Port | Dir | Width | Semantics | Source |
|---|---|---|---|---|
| clk_i | in | 1 | Single clock. No clock gating inside ibex_core (ibex_top's gate is out of scope). | rtl/ibex_core.sv:62 |
| rst_ni | in | 1 | Asynchronous active-low reset for every flop in the DUT. The controller starts in RESET (rtl/ibex_controller.sv:1032). | rtl/ibex_core.sv:63; integration.rst:282 |
| hart_id_i | in | 32 | Read combinationally by mhartid (rtl/ibex_cs_registers.sv:428-432): a change is visible on the next CSR read. Realistic driver: static per run. | integration.rst:302-303 |
| boot_addr_i | in | 32 | Sampled combinationally in the RESET and BOOT_SET controller states (the two cycles after reset release, rtl/ibex_controller.sv:582-596) to form the first PC = {boot_addr_i[31:8], 8'h80} (rtl/ibex_if_stage.sv:242-253) and mtvec = {boot_addr_i[31:8], 8'h01} (rtl/ibex_cs_registers.sv:736-743, csr_mtvec_init from rtl/ibex_if_stage.sv:256). Bits [7:0] are ignored; assertion IbexBootAddrUnaligned requires them to be 0 (rtl/ibex_if_stage.sv:932). Realistic driver: stable from before reset release until at least 2 cycles after; later changes have no effect (no other PC_BOOT use; UNVERIFIED-1 whether SLEEP wake re-uses PC_BOOT: it does not, FIRST_FETCH keeps the prefetch address, rtl/ibex_controller.sv:614-621). | exception_interrupts.rst:17-18; integration.rst:305-307 |
| cheriot_enable_i | in | 4 (ibex_mubi_t) | Tied to IbexMuBiOff (4'b1010) inside the wrapper; not a DUT input. Invalid-encoding alert path is constant 0 (rtl/ibex_core.sv:1342-1344). | DV_prompt Section 2 |
| fetch_enable_i | in | 4 (ibex_mubi_t) | Only the exact value IbexMuBiOn (4'b0101) enables fetch and execution: `instr_req_gated = instr_req_int & (fetch_enable_i == IbexMuBiOn)`, `instr_exec = (fetch_enable_i == IbexMuBiOn)` (rtl/ibex_core.sv:644-649). Any other value, valid Off or invalid encoding, halts the IF stage (halt_if, rtl/ibex_controller.sv:996-999) after the instruction in ID/WB completes. NO alert for an invalid encoding (alert expression rtl/ibex_core.sv:1350-1351 has no fetch_enable term). RTL-defined, unverified against doc: interrupt entry (IRQ_TAKEN), debug entry (DBG_TAKEN_IF) and SLEEP wake are NOT gated by fetch_enable, so CSR side effects (mepc/mcause/mstatus/dpc/dcsr) and pc_set still happen with fetch off; the handler is fetched once fetch is re-enabled (rtl/ibex_controller.sv:630-646, :704-720, :615). Realistic driver: On from reset release; toggling Off/On mid-program is legal and worth covering; never drive X. | integration.rst:323-332 |
| mcounteren_writable_i | in | 4 (ibex_mubi_t) | mcounteren CSR writes take effect only while this equals IbexMuBiOn (rtl/ibex_cs_registers.sv:845); any other encoding silently drops the write (no exception). Reads are unaffected. RTL-defined for invalid encodings (doc/03_reference/performance_counters.rst names the input as a lock only). Realistic driver: static per run, both values covered. | performance_counters.rst mcounteren section |
| core_busy_o | out | 4 (ibex_mubi_t) | Takes only IbexMuBiOn or IbexMuBiOff: each bit i is `\|{ctrl_busy, if_busy, lsu_busy}` (bits where IbexMuBiOn[i]==1) or its complement (rtl/ibex_core.sv:497-518, through prim_buf). Off only when the controller is in WAIT_SLEEP or in SLEEP with no wake condition (rtl/ibex_controller.sv:598-621), the icache has no invalidation and no outstanding fill beat (rtl/ibex_icache.sv:1304), and the LSU FSM is IDLE (rtl/ibex_load_store_unit.sv:762). Combinational from the wake inputs: an irq pin edge flips it to On in the same cycle. Doc describes ibex_top's core_sleep_o (its negation, integration.rst:333-337); the core-level encoding is RTL-defined. Checker: any value other than the two encodings is a fault. | rtl/ibex_core.sv:497-518 |

Reset behaviour at the boundary (rtl/ibex_controller.sv:582-596, rtl/ibex_cs_registers.sv:
1052-1057, :987-993): cycle 0 after rst_ni rises: controller RESET, instr_req_o = 0, pc_set to
PC_BOOT, mtvec loaded; cycle 1: BOOT_SET, instr_req_o = 1 (first fetch at {boot_addr[31:8],8'h80}
word-aligned), PC/mtvec set again; cycle 2: FIRST_FETCH; cycle 3: DECODE. priv = M, mstatus =
0x80, mie = 0, mtvec = {boot_addr[31:8], 8'h01}, dcsr = 0x40000003, cpuctrlsts = 0 (icache off,
dummy instructions off), all PMP CSRs 0. A pending debug_req_i or irq_nm_i at reset release is
taken in FIRST_FETCH before any instruction executes (RTL-defined, see gen_behaviour_summaries
CTRL-03/CTRL-41). The icache runs its 256-entry tag invalidation for at least 258 cycles after
reset (fetch proceeds uncached meanwhile, rtl/ibex_icache.sv:1208-1270).

## 2. Instruction memory interface (driven by the icache, ICache = 1)

| Port | Dir | Width | Semantics |
|---|---|---|---|
| instr_req_o | out | 1 | Request valid. Sole driver is rtl/ibex_icache.sv:1030-1036 through rtl/ibex_if_stage.sv:323. Held until instr_gnt_i (hold logic rtl/ibex_icache.sv:764-775). NOT gated by PMP (rtl/ibex_core.sv:557 direct wire; pmp.rst:27). Zero in the RESET cycle, WAIT_SLEEP and SLEEP (rtl/ibex_controller.sv:584, :600, :609), but fill beats already owned by a fill buffer complete even when req_i is low (rtl/ibex_icache.sv:249, :756-775). |
| instr_addr_o | out | 32 | Word aligned ([1:0] = 00, rtl/ibex_icache.sv:1037; assertion rtl/ibex_if_stage.sv:938). Stable while req is high and not granted (arbitration is oldest-first and a holding buffer cannot be displaced, rtl/ibex_icache.sv:842, :764-775). May be a speculative address never executed (branch-target speculation, prefetch past a taken branch, stale lines, rtl/ibex_icache.sv:700-705, :741). |
| instr_gnt_i | in | 1 | Grant; may be asserted in the request cycle or any later cycle (load_store_unit.rst:89 by reference from instruction_fetch.rst:86-87). Permanently high is legal. |
| instr_rvalid_i | in | 1 | Exactly one response per granted request, in request order, at least one cycle after the grant (responses are assigned to the oldest buffer still expecting data, rtl/ibex_icache.sv:851-852; no tags). Up to 8 granted-and-unanswered beats can be outstanding: NUM_FB = 4 fill buffers (rtl/ibex_icache.sv:72) x IC_LINE_BEATS = 2 (rtl/ibex_pkg.sv:406). RTL-defined, unverified against doc (doc gives no bound). |
| instr_rdata_i | in | 39 | [31:0] instruction word; [38:32] inverted 39/32 SECDED check bits of [31:0] (decoder rtl/ibex_if_stage.sv:259-276, vendor/lowrisc_ip/ip/prim/rtl/prim_secded_inv_39_32_dec.sv). Checked on EVERY rvalid, wanted or not, error or not: a bad codeword raises alert_major_bus_o for that cycle (rtl/ibex_if_stage.sv:282, rtl/ibex_core.sv:1353) and the beat is treated as instr_err_i inside the icache (rtl/ibex_if_stage.sv:281, :328). There is no internal NMI for instruction-side integrity errors (rtl/ibex_id_stage.sv:613 ORs only the LSU errors) - security.rst:85-87 is imprecise here. Doc lists a separate instr_rdata_intg_i[6:0] (instruction_fetch.rst:68): at ibex_core it is bits [38:32] of this port (RTL-defined at this boundary). |
| instr_err_i | in | 1 | Sampled with instr_rvalid_i, per beat (rtl/ibex_icache.sv:947-950). Effect: when the erroring word (or half of an unaligned 32-bit instruction) is consumed by ID, ExcCauseInstrAccessFault (1) with mtval = pc (+2 if only the second half erred: err_plus2, rtl/ibex_icache.sv:1194-1197, rtl/ibex_controller.sv:859-861). Errors on speculative beats of lines that hit, or on stale/never-consumed beats, are dropped (rtl/ibex_icache.sv:1020-1021). Erroring beats are never allocated into the cache (rtl/ibex_icache.sv:817). |

Protocol rules (doc: instruction_fetch.rst:41-71 signal table, protocol by reference to
load_store_unit.rst:84-95; RTL as cited):
1. req held until gnt; addr stable meanwhile (rule from doc :53-56; RTL rtl/ibex_icache.sv:764-775).
2. gnt same cycle allowed; gnt while req == 0 must NEVER be driven: the icache counts
   `fill_ext_arb & instr_gnt_i` as a completed beat (rtl/ibex_icache.sv:759-762); a bare grant
   with no arbitrating buffer is ignored, but the protocol is undefined and untested.
3. rvalid must NEVER arrive in the grant cycle or without a granted request: the icache has no
   assertion for this (its assertions are only rtl/ibex_icache.sv:1306-1335, TagHitKnown /
   TagInvalidKnown); an unexpected beat is consumed by the oldest expecting buffer, shifting all
   later responses (corrupt fetch stream), and a beat arriving in the same cycle as a freshly
   allocated buffer's speculative grant is mis-assigned (UNVERIFIED-2: possible permanent hang).
4. Every rvalid must carry correct SECDED bits, including error beats (rule 5 in section 3).
5. The agent must serve fetches that are never executed and must expect two-beat line fills in
   wrapping order when the cache is enabled (entry at word 1 fetches word 1 then word 0,
   rtl/ibex_icache.sv:830-835) and no wrap when caching is off (rtl/ibex_icache.sv:771-773).
6. Fetch timing landmarks the agent will see: first request 1 cycle after reset release; after a
   taken branch/jump/trap, a request for the target in the same cycle as pc_set if no fill buffer
   is already requesting (rtl/ibex_icache.sv:703, :1030); with the cache disabled or during the
   258-cycle reset invalidation every fetch reaches the bus.

## 3. Data memory interface (LSU)

Source read in full: rtl/ibex_load_store_unit.sv (836 lines). FSM: ls_fsm_e IDLE,
WAIT_GNT_MIS, WAIT_RVALID_MIS, WAIT_GNT, WAIT_RVALID_MIS_GNTS_DONE (+3 CHERIoT-only CTX_* states
never entered), rtl/ibex_pkg.sv:816-820, comb :411-609.

| Port | Dir | Width | Semantics |
|---|---|---|---|
| data_req_o | out | 1 | `data_req_out & ~pmp_req_err[PMP_D]` (rtl/ibex_core.sv:1063). Asserted in IDLE when the ID stage presents a request (rtl/ibex_load_store_unit.sv:468-486) and held in WAIT_GNT_MIS / WAIT_RVALID_MIS / WAIT_GNT until gnt (:490, :505, :536). A PMP-denied word never appears on the bus (the LSU takes `pmp_err_q` as a fake grant, :495, :510, :537). Never falls before a grant except by PMP denial (PMP result is combinational on the stable address). |
| data_addr_o | out | 32 | Word aligned `{addr[31:2], 2'b00}` (:719-722; assertion :830). Stable while req & ~gnt (ID operands frozen by stall_mem, rtl/ibex_id_stage.sv:1095-1096; second-half address = addr_last_q + 4 computed in the ALU, rtl/ibex_id_stage.sv:347-349, :362). |
| data_we_o | out | 1 | `lsu_we_i` (:723), sent with req. |
| data_be_o | out | 4 | Per-lane byte enable (:138-191). Word +0 1111; word +1 first 1110 then 0001; +2 1100/0011; +3 1000/0111; half +0 0011, +1 0110, +2 1100, +3 first 1000 then 0001; byte k: 1<<k. |
| data_wdata_o | out | 39 | [31:0] = lsu_wdata rotated by address offset (:200-208) so bytes land in the enabled lanes; disabled lanes carry the rotated (not zeroed) data. [38:32] = inverted 39/32 SECDED of the 32-bit rotated word (prim_secded_inv_39_32_enc, :731-735), computed over all 32 bits including disabled lanes. Driven (with valid ECC) for loads as well as stores. Doc lists a separate data_wdata_intg_o[6:0] (load_store_unit.rst:34-36): at ibex_core it is [38:32] of this port. |
| data_tag_o | out | 1 | CHERIoT capability tag; constant 0 with cheriot off (:220, :740). Carve-out. |
| data_gnt_i | in | 1 | Grant, same cycle or later (load_store_unit.rst:89). Must NEVER be asserted while data_req_o is 0: every wait state takes a bare gnt as a grant (:478, :495, :518, :537). |
| data_rvalid_i | in | 1 | One response per granted request, in order, at least one cycle after the grant. Same-cycle rvalid would be attributed to the previous access (`lsu_resp_valid_o = all_resp & (ls_fsm_cs == IDLE)`, :692-694, with control flops updated only at the following edge, :240-252); assertion NoMemResponseWithoutPendingAccess (rtl/ibex_core.sv:1390-1391, INC_ASSERT) fires. Maximum outstanding: 2, and only the two halves of one misaligned access (WAIT_RVALID_MIS_GNTS_DONE, :525-529); otherwise 1. Back-to-back: the next instruction's request may be issued in the same cycle as the previous response (rtl/ibex_id_stage.sv:1015-1019). rtl/ibex_top.sv:229-233 documents the bound of 2. |
| data_rdata_i | in | 39 | [31:0] read data; [38:32] inverted SECDED check bits, decoded every cycle (:376-393) and USED on every rvalid, for loads, stores and error responses alike (:756-757). Bad codeword on a load: RF write suppressed (:697-698), no exception, instruction retires, alert_major_bus_o pulse (rtl/ibex_core.sv:1353), internal NMI armed (mcause 0xFFFFFFE0, mtval = faulting address, rtl/ibex_controller.sv:393-448). Bad codeword on a store response: alert + NMI, store considered complete. Store response data is otherwise ignored (load_store_unit.rst:64-66: recommend a fixed value with correct check bits). |
| data_tag_i | in | 1 | CHERIoT capability tag; sampled only in CHERIoT arms (:672, :707). Unobservable with cheriot off. Carve-out; tie 0. |
| data_err_i | in | 1 | Sampled with rvalid. Error on the first half of a split access: recorded (:514), the second half is STILL issued and must be granted and answered; its data/err are ignored; the fault is reported at the final response with mtval = the original (possibly unaligned) effective address (:254-266, :520). Error on an aligned access or on the second half: mtval = the word-aligned address of that request (:258 with addr_incr_req_o). Exception: ExcCauseLoadAccessFault (5) / StoreAccessFault (7) taken from WB the cycle after the final response, mepc = PC of the load/store (rtl/ibex_controller.sv:900-927, :833-841); RF untouched; the younger instruction in ID is killed and re-executed after the handler (rtl/ibex_id_stage.sv:1033-1036). |

Misaligned splitting (:403-405): word with offset != 0, or halfword with offset 3, are split into
two word-aligned accesses (first the containing word, then +4); halfword at +1/+2 and all bytes are
single accesses. No misaligned-address exception exists for RV32 data accesses (the causes
ExcCauseLoad/StoreAddrMisaligned are CHERIoT-only, rtl/ibex_controller.sv:903, :917).
Load data realignment and sign/zero extension: :269-369 (offset from rdata_offset_q, sign from
data_sign_ext_q). At least one stall cycle per load/store (load_store_unit.rst:10).

PMP on the data side (rtl/ibex_core.sv:1580-1634, rtl/ibex_pmp.sv): channel PMP_D checks
data_addr_o with type WRITE/READ from data_we_o and privilege `priv_mode_lsu = mstatus.MPRV ?
mstatus.MPP : priv` (rtl/ibex_cs_registers.sv:998), combinationally in the address phase. A denied
word produces no bus transaction and a Load/StoreAccessFault with mtval = that word's address
(effective address for an aligned or first-half fault, word-aligned second address for a
second-half fault). RTL-defined, unverified against doc and security-relevant: when the FIRST half
of a misaligned access is denied, the permitted SECOND half is still issued on the bus (WAIT_GNT_MIS
-> WAIT_RVALID_MIS drives req with the second address, :489-531); for a store that write is
performed before the exception (see gen_behaviour_summaries MEM-13 and the owner note there).
In debug mode, addresses inside {DmBaseAddr, DmAddrMask} bypass PMP (rtl/ibex_pmp.sv:239-251).

Driver rules, data side: (1) gnt only while req; (2) rvalid only for a granted request, never in
the grant cycle, exactly once, in order; (3) always return rvalid for stores; (4) correct SECDED on
every rvalid; (5) sample addr/we/be/wdata in the grant cycle only (they may change the cycle after,
load_store_unit.rst:91); (6) merge only enabled lanes; (7) after a first-half error still serve the
second half; (8) never drive X on data_rdata_i while rvalid (the decoder sees X as an error).

## 4. Register file interface (inside the wrapper; TB monitor/probe seam, not a DUT input)

ibex_core ports (rtl/ibex_core.sv:90-102) and their ibex_register_file_ff counterparts
(rtl/ibex_register_file_ff.sv:60-86), wired as rtl/ibex_top.sv:540-559:

| ibex_core port | Dir | Width | RF port | Semantics |
|---|---|---|---|---|
| rf_raddr_a_o / rf_raddr_b_o | out | 5 | raddr_a_i / raddr_b_i | Read addresses from the decoder, valid whenever the ID instruction reads that port (rf_ren_a/b internal); combinational (same-cycle) read data (register_file.rst:10). |
| rf_rdata_a_ecc_i / rf_rdata_b_ecc_i | in | RegFileDataWidth | rdata_a_o / rdata_b_o | Read data; with RegFileECC = 0 passed straight through (rtl/ibex_core.sv:1305-1319). No write-to-read forwarding inside the RF (register_file.rst:11); the ID stage forwards WB results itself. |
| rf_waddr_wb_o, rf_we_wb_o, rf_wdata_wb_ecc_o | out | 5, 1, RegFileDataWidth | waddr_a_i, we_a_i, wdata_a_i | One write port. Write happens at the clock edge when we_a_i (rtl/ibex_register_file_ff.sv:116-127, :131-141). Two write sources arbitrated in WB: the WB flop for ALU/CSR/jump results and the LSU response for loads (rtl/ibex_wb_stage.sv:182-183, :220, :297-303; one-hot assertion :310). rf_we_wb_o with waddr 0 does occur for real instructions with rd = x0 (dropped by the RF) and for dummy instructions (stored in the dummy x0 flop, :159-171). |
| rf_wcap_ecc_wb_o | out | RegFileCapEccWidth | wcap_a_i | CHERIoT capability write data; constant (NULL_CAP vector) with cheriot off. Carve-out. |
| rf_rcap_a_ecc_i / rf_rcap_b_ecc_i | in | RegFileCapEccWidth | rcap_a_o / rcap_b_o | Constant CapWordZeroVal with cheriot off (rtl/ibex_register_file_ff.sv:227-230). Carve-out. |
| dummy_instr_id_o | out | 1 | dummy_instr_id_i | High while a dummy instruction is in ID: makes x0 read the dummy flop instead of 0 (:173, :184). |
| dummy_instr_wb_o | out | 1 | dummy_instr_wb_i | High while a dummy instruction is in WB: enables the x0 dummy flop write (:159-161); assertion DummyWriteTargetsX0 (:162). |
| (wrapper) | | | test_en_i | Unused by the FF register file (:232-233); tie 0. |
| (wrapper) | | | cheriot_enable_i | Tie IbexMuBiOff. |

Storage layout in this build (g_cheriot_rf elaborates because BaseIsa = BaseIsaRV32IorCHERIoT,
rtl/ibex_register_file_ff.sv:88-239): x1-x15 in rf_data (:116-127), x16-x31 in the 35-bit
rf_shared bank zero-extended (:131-141, x16 in rf_shared_r0_q :174-183), x0 = 0 except for dummy
instructions. Architecturally identical to a 32 x 32 file in RV32I mode (:221-224). These nets
are the natural probe for an RF-write monitor (probe register entry needed if the TB reads them).

## 5. Instruction cache RAM ports and scramble-key handshake (TB test equipment)

| Port | Dir | Width | Semantics |
|---|---|---|---|
| ic_tag_req_o | out | 2 (per way) | RAM request per way; both ways for lookups and invalidation writes, one way for an allocation write (rtl/ibex_icache.sv:269-277, :445-450). |
| ic_tag_write_o | out | 1 | 1 = write. Writes: invalidation sweep (valid bit 0) one index per cycle for 256 cycles after reset and after fence.i (:1241-1256), ECC-error invalidation (:640-644), line allocation. |
| ic_tag_addr_o | out | 8 (IC_INDEX_W) | Line index. |
| ic_tag_wdata_o | out | 28 (TagSizeECC) | {6 ECC, valid, 21 tag} inverted 28/22 SECDED (:290-302), XORed with an index-derived tweak (TweakInfection = 1, :389-425). |
| ic_tag_rdata_i | in | 28 x 2 (unpacked per way) | Read data, expected the cycle AFTER the request (IC1 samples it, :466-472, :498-514): the TB RAM must be a synchronous single-port RAM with 1-cycle read latency. |
| ic_data_req_o / ic_data_write_o / ic_data_addr_o | out | 2 / 1 / 8 | As for tags. RTL-defined: during the invalidation sweep ic_data_write_o is also 1 (`data_write_ic0 = tag_write_ic0`, :283) whenever a concurrent lookup asserts ic_data_req_o, writing ECC-encoded zeros at the inval index (harmless; a RAM model must not flag it). |
| ic_data_wdata_o | out | 78 (LineSizeECC) | Two 39-bit inverted SECDED codewords, one per 32-bit beat (:305-310), tweaked by address (:321-379). icache.rst:202-208 documents a 72-bit [71:64]+[63:0] layout: stale, the RTL is 2 x 39 (doc defect). |
| ic_data_rdata_i | in | 78 x 2 | Read data, 1-cycle latency. Data ECC checked only for the hitting way (:580-585). Any tag or data ECC error: alert_minor_o pulse (rtl/ibex_core.sv:1337), lookup treated as a miss, forced invalidation write next cycle (:591-593, :640-644); no correction. |
| ic_scr_key_req_o | out | 1 | ONE-CYCLE pulse (:1213, :1226, :1251, :1261): in OUT_OF_RESET if key not valid; on fence.i in INVAL_IDLE; on a fence.i during INVAL_CACHE (restart). Never two consecutive cycles. Doc icache.rst:100-102 describes ibex_top's level-held request (rtl/ibex_top.sv:628-655); the core-level pulse is RTL-defined. |
| ic_scr_key_valid_i | in | 1 | Level. The invalidation FSM waits in AWAIT_SCRAMBLE_KEY until it is 1 (:1229-1240); fence.i is IGNORED while waiting (icache.rst:113-116; cs_registers.rst:544-545 "guaranteed to fetch a new key" contradicts this, doc-vs-doc). Fetch is never blocked by an invalid key (pass-through); if valid never returns, nothing is ever cached and core_busy_o stays On. Software reads the registered value in cpuctrlsts[8] (rtl/ibex_cs_registers.sv:1938-1948). Realistic key agent: drop valid for a random number of cycles after each req pulse, then raise it; also cover valid tied high (no request at reset). |

The RAM contents, the scramble key and nonce never enter ibex_core (ICacheScramble only affects
ibex_top's RAM primitives). The TB RAM may be a plain array; ECC/tweak knowledge is needed only
for fault injection (alert_minor_o is otherwise unreachable).

## 6. Interrupts

| Port | Dir | Width | Semantics |
|---|---|---|---|
| irq_software_i / irq_timer_i / irq_external_i | in | 1 each | Level-sensitive (exception_interrupts.rst:61). mip mirrors the raw pins combinationally (rtl/ibex_cs_registers.sv:408-412, :494-501), NOT qualified by mie (cs_registers.rst:246 says qualified: doc defect, RTL matches the privileged spec). IDs 3 / 7 / 11; vector mtvec.BASE + 4*id. |
| irq_fast_i | in | 15 | IDs 16..30, vectors +0x40..+0x78; highest priority among maskable interrupts, lowest index first (rtl/ibex_controller.sv:503-511, :746-758; exception_interrupts.rst:53-54). |
| irq_nm_i | in | 1 | Non-maskable, level-sensitive, not in mip/mie, ID 31, vector mtvec.BASE + 0x7C, mcause 0x8000001F, mtval 0. Blocked only by debug mode, dcsr.step, nmi_mode (until the next MRET) and pipeline drain (rtl/ibex_controller.sv:487, :498-500, :736-745). Still high at the handler's MRET: re-taken immediately. |
| irq_pending_o | out | 1 | `\|(mip & mie_q)` (rtl/ibex_cs_registers.sv:1044-1045): combinational from the pins with zero latency, NOT gated by mstatus.MIE, privilege, debug mode, nmi_mode or step, EXCLUDES irq_nm_i and the internal NMI. Changes the cycle after a CSR write to mie. RTL-defined, unverified against doc (undocumented port; ibex_top uses it to wake the clock). |

Taking conditions and timing (rtl/ibex_controller.sv:490, :498-500, :700-761): an interrupt is
taken when not in debug mode, dcsr.step = 0, not in nmi_mode, and (NMI or (irq_pending_o and
(mstatus.MIE or priv == U))), the ID stage is empty and WB has drained (an outstanding load/store
response is waited for; if it errors, that exception wins), no special request, no stall. The
decision is made in DECODE with an empty pipe; the cause, mepc (= pc_if) and vector are computed
from the LIVE pins one cycle later in IRQ_TAKEN. RTL-defined: if the pin drops in that cycle no
trap is taken and the FSM returns to DECODE; a higher-priority pin appearing in that cycle wins.
A one-cycle pulse can therefore be lost; a realistic source holds the level until the handler
clears it (exception_interrupts.rst:61-62). Interrupt entry: mstatus.MIE <- 0, MPIE <- MIE, MPP <-
priv, priv <- M, mepc <- next PC, mcause per id, mtval <- 0, mstack pushed (rtl/ibex_cs_registers.sv:
918-933); the vector fetch appears on instr_addr_o in the IRQ_TAKEN cycle. Internal NMI (bus
integrity error on a load/store response): mcause 0xFFFFFFE0, mtval = faulting address, same vector,
taken at most one instruction later; an external NMI takes priority and leaves it pending
(rtl/ibex_controller.sv:393-448). In U-mode, M-level interrupts are taken regardless of MIE.

## 7. Debug

| Port | Dir | Width | Semantics |
|---|---|---|---|
| debug_req_i | in | 1 | Level-sensitive halt request (debug.rst:24-27). Taken at the next instruction boundary after the pipe drains (same drain as interrupts, debug wins over IRQ, rtl/ibex_controller.sv:474-477, :704-710), or from FIRST_FETCH/SLEEP (:640-645, :615). If the ID instruction is a special request (trap, mret, dret, wfi, CSR flush) its effects complete first and debug is entered from FLUSH using the value sampled in DECODE (:985-987): dpc then equals the trap vector / mret target. Ignored while already in debug mode; a still-high request re-halts right after dret. A pulse during FLUSH is lost (out-of-spec stimulus; the debug spec requires haltreq to be held). Entry: PC <- DmHaltAddr (0x1A110800), dpc <- pc_if (haltreq/step/trigger) or pc_id (ebreak), dcsr.cause/prv, priv <- M, icache forced off while in debug mode (rtl/ibex_cs_registers.sv:906-917, :1970-1971). Exceptions in debug mode go to DmExceptionAddr (0x1A110808) with no CSR update (rtl/ibex_controller.sv:831; rtl/ibex_cs_registers.sv:918). |

Other debug entries with no dedicated pin: ebreak with dcsr.ebreakm/ebreaku, single step
(dcsr.step; masks ALL interrupts including NMI while stepping outside debug mode, RTL-defined),
one hardware trigger (tdata1 execute bit, tdata2 address == pc_if, DbgHwBreakNum = 1). Exit: dret
(PC <- dpc, priv <- dcsr.prv). The Debug Module window {DmBaseAddr, DmAddrMask} bypasses PMP in
debug mode for fetch and data (rtl/ibex_pmp.sv:239-251; pmp.rst:65-66); the debug program buffer
and ROM are TB memory at those addresses, fetched over the normal instruction bus. Bug candidate
CTRL-33: mstatus.MPRV is still applied to debug-mode loads/stores although dcsr.mprven reads 0
(gen_behaviour_summaries.md).

## 8. Alerts, crash dump, double fault

| Port | Dir | Width | Semantics |
|---|---|---|---|
| alert_minor_o | out | 1 | `icache_ecc_error` (rtl/ibex_core.sv:1337): one-cycle pulse per icache RAM ECC error (section 5). Only reachable by TB fault injection into ic_*_rdata_i. |
| alert_major_internal_o | out | 1 | `rf_ecc_err_comb \| pc_mismatch_alert \| csr_shadow_err \| cheriot_fatal_err \| cheriot_enable_mubi_err` (:1350-1351). In this DUT csr_shadow_err = 0 (ShadowCSR = 0, :197), the two cheriot terms = 0 (tie), rf_ecc_err_comb = 0 unless the wrapper sets RegFileECC = 1 (owner question Q-A). pc_mismatch_alert fires when pc_if != pc_id + 2/4 for a sequential instruction (rtl/ibex_if_stage.sv:659-692), i.e. only under fault injection. Combinational, one cycle per offending cycle, may repeat (integration.rst:344-350). |
| alert_major_bus_o | out | 1 | `lsu_load_resp_intg_err \| lsu_store_resp_intg_err \| instr_intg_err` (:1353): bad SECDED on any rvalid on either bus, gated only by rvalid (not by "expected" state). The only alert the TB can raise through legal-looking bus stimulus. |
| crash_dump_o | out | crash_dump_t (5 x 32) | Combinational mirrors (:1325-1330): current_pc = pc_id (stale when ID empty), next_pc = pc_if, last_data_addr = lsu_addr_last (also the mtval source for LSU faults), exception_pc = mepc CSR, exception_addr = mtval CSR (both follow SW CSR writes). Field order rtl/ibex_pkg.sv:16-22. Doc gives no field definition (integration.rst:319): RTL-defined. |
| double_fault_seen_o | out | 1 | One-cycle pulse in the FLUSH cycle of a synchronous exception taken while cpuctrlsts.sync_exc_seen is already set; sets cpuctrlsts.double_fault_seen (sticky, SW-clearable). Interrupts, debug entry and exceptions in debug mode do not participate; any MRET clears sync_exc_seen (rtl/ibex_cs_registers.sv:935-945, :962-965; exception_interrupts.rst:183-195). |

## 9. RVFI (only with +define+RVFI; ports rtl/ibex_core.sv:136-181, logic :1653-2435)

Not set by the config (gen_param_resolution.md section 3.6). With WritebackStage = 1 the tracking
pipeline has 2 stages (:1655); all rvfi_* outputs are flops (:1775-1803 select the last stage).

| Signal | Width | When / what |
|---|---|---|
| rvfi_valid | 1 | One cycle per instruction, the cycle after it completes WB (`rvfi_stage_valid_d[1] = rvfi_wb_done`, :1868; `rvfi_wb_done = rvfi_stage_valid[0] & (instr_done_wb \| rvfi_stage_trap[0])`, :1890). Trapping instructions are traced although flushed (:1846-1853). Dummy instructions are NOT traced (:1864-1866) and do not advance rvfi_order (:1905). Zcmp: each expanded micro-op produces its own rvfi_valid (rvfi_id_done per micro-op); rvfi_ext_expanded_insn(_valid,_last) identify them (:2271-2282). |
| rvfi_order | 64 | Retirement count, +1 per traced instruction (:1905). |
| rvfi_insn | 32 | Raw 16-bit encoding zero-extended for a compressed instruction that was not expanded; else the 32-bit (expanded) instruction (:2263-2269). |
| rvfi_trap | 1 | ID-stage exception (illegal, ecall, ebreak-as-exception, fetch fault) or WB-stage load/store fault for this instruction (:1885-1888, :2145). ebreak that enters debug mode is not a trap (:1886). RTL-defined caveat (bug candidate for RVFI checkers): `rvfi_id_done` suppresses the ID-stage trap entry when the controller's wb_exception_o is set in the same cycle, which includes ordinary load/store errors (:1851-1853, rtl/ibex_controller.sv:336-337). |
| rvfi_halt | 1 | Always 0 (:2073, never set). |
| rvfi_intr | 1 | Set on the first instruction executed after an interrupt/NMI vector was taken (pc_set with PC_EXC and EXC_PC_IRQ, :2400-2425); NOT set for synchronous exception handlers. |
| rvfi_mode | 2 | priv_mode_id when the instruction was in ID (:2078). rvfi_ixl = 1 (:2079). |
| rvfi_rs1_addr/rdata, rvfi_rs2_addr/rdata | 5/32 | Captured in the instruction's first cycle; 0 when the port is not read (rf_ren, :2303-2319). rvfi_rs3_addr/rdata: second cycle of ternary bitmanip ops (:2316-2317). |
| rvfi_rd_addr, rvfi_rd_wdata | 5/32 | From the WB write (rf_we_wb or rf_we_lsu, :1805-1807); both 0 when rd = x0 or no write (:2339-2363). |
| rvfi_pc_rdata | 32 | pc_id (:2083). |
| rvfi_pc_wdata | 32 | `pc_set ? branch_target_ex : pc_if` captured when the instruction leaves ID (:2084). Branch and jump records carry the target (pc_set in their ID-exit cycle). Trap, mret and dret records carry pc_if = the next sequential fetch address, never the vector, mepc or dpc: they leave ID in the DECODE cycle (rtl/ibex_id_stage.sv:991, :1130; rtl/ibex_core.sv:1851-1853) and their pc_set is issued one cycle later in FLUSH (rtl/ibex_controller.sv:826-833, :953-965). A checker observes a redirect target as the next record rvfi_pc_rdata (T-053 X-1; former UNVERIFIED-3, resolved from the RTL). |
| rvfi_mem_addr | 32 | The un-split effective address from the first cycle (lsu_addr, :2207-2219), possibly misaligned. |
| rvfi_mem_rmask / rvfi_mem_wmask | 4 | From lsu_type only: word 1111, half 0011, byte 0001 (:2253-2261), NOT shifted by the address offset; wmask for stores, rmask for loads (:2085-2086); both zeroed if the instruction trapped in WB (:2156-2157). RTL-defined. |
| rvfi_mem_rdata | 32 | The final realigned/extended load data (rf_wdata_lsu at lsu_resp_valid, :2222-2233). rvfi_mem_wdata: lsu_wdata unrotated (:2211). |
| rvfi_ext_pre_mip / rvfi_ext_post_mip | 32 | mip (mie-unqualified pins) before / after the instruction, in CSR bit positions (:1809-1827); pre_mip is captured with the trap decision when the pipe empties (:1934-1977). |
| rvfi_ext_nmi, rvfi_ext_nmi_int, rvfi_ext_debug_req | 1 | Sampled at the instruction IF->ID transfer (the pin level in the cycle before its first ID cycle, :1996-2001), or the captured_* value when the event arrived while ID was empty (:1949-1957). An instruction already in ID when debug_req_i rises reports 0; outside debug mode a high debug_req_i stops new instructions entering ID (rtl/ibex_controller.sv:700-708), so the first debug-ROM record is the one that reports 1 (T-053 X-6). |
| rvfi_ext_debug_mode | 1 | debug_mode while the instruction was in ID (:2101). |
| rvfi_ext_rf_wr_suppress | 1 | Load whose RF write was suppressed by a bus-integrity error (:2379-2398). |
| rvfi_ext_mcycle, rvfi_ext_mhpmcounters[10], rvfi_ext_mhpmcountersh[10] | 64, 32 x 10 | mcycle and mhpmcounter3..12 (low/high) sampled when the instruction left ID (:2102, :2108-2127). |
| rvfi_ext_ic_scr_key_valid | 1 | cpuctrlsts.ic_scr_key_valid sampled with the instruction (:2103). |
| rvfi_ext_irq_valid | 1 | Notification with NO retired instruction when the pipeline has emptied for an interrupt (:1965-1971). It is a LEVEL, not a pulse: rises four cycles after the decision cycle (rvfi_irq_valid flop, stage[0] :1992-2002, stage[1] :2134-2141, port = stage[RVFI_STAGES] :1837, :2192-2199) and stays high until about two cycles after the handler first instruction enters ID; not generated when ID emptied before WB drained (captured_valid already set); never coincides with rvfi_valid (T-053 X-16). |
| rvfi_ext_expanded_insn_valid / _insn / _last | 1/16/1 | Zcmp micro-op marker with the original 16-bit encoding (:2271-2282). |
| rvfi_rs1_rcap, rvfi_rs2_rcap, rvfi_rd_wcap, rvfi_mem_is_cap, rvfi_mem_rcap, rvfi_mem_wcap | cap_t / 1 | CHERIoT-only, constant NULL_CAP / 0 with cheriot off (:2286-2295, :2211-2212, :2223-2225). Carve-out. |

The RVFI block reads hierarchical internals of the core (id_stage_i.controller_i.*,
if_stage_i.instr_valid_id_d, cs_registers_i.mip, load_store_unit_i.resp_is_cap_q) but stays
inside the DUT; no TB probe is needed to use it.

## 10. Ports that exist only for CHERIoT (all in the cheriot-out-of-scope carve-out)

cheriot_enable_i (tied), data_tag_o (constant 0), data_tag_i (never sampled), rf_wcap_ecc_wb_o
(constant), rf_rcap_a_ecc_i / rf_rcap_b_ecc_i (constant CapWordZeroVal), and the six rvfi_*cap /
rvfi_mem_is_cap outputs. Details and line proofs: gen_cheriot_carveout.md buckets D and E.

## 11. Cross-interface facts a realistic system driver must respect (summary)

- Both buses: req held until gnt; gnt only while req; same-cycle gnt legal; rvalid >= 1 cycle
  after gnt, exactly one per grant, strictly in order; valid inverted 39/32 SECDED on every
  rvalid; never rvalid in the grant cycle or unsolicited (no RTL defence except an INC_ASSERT on
  the data side).
- Data bus depth 2 (misaligned pair only); instruction bus depth 8; instruction fetches may be
  speculative and never executed; a PMP-denied fetch still reaches the bus, a PMP-denied data word
  never does.
- Interrupt and debug request pins are levels; a one-cycle pulse can be missed (RTL-defined).
- fetch_enable_i and mcounteren_writable_i must be exactly IbexMuBiOn to enable; every other
  value is "off" with no alert.
- ic_scr_key_valid_i is a level answering one-cycle ic_scr_key_req_o pulses; the icache RAMs need
  1-cycle synchronous read latency and must accept invalidation writes from reset.
- boot_addr_i[7:0] must be 0 and boot_addr_i stable through reset release.

## 12. Unverified items

- UNVERIFIED-1: boot_addr_i is used only in RESET/BOOT_SET (no later PC_BOOT selection); by
  reading of rtl/ibex_controller.sv:582-621, not simulated.
- UNVERIFIED-2: instruction-side rvalid in the same cycle as the grant of a newly allocated fill
  buffer's speculative request leads to a permanent stall (rtl/ibex_icache.sv:721, :779-784,
  :851-852, :894-895); from reading only.
- UNVERIFIED-3: RESOLVED 2026-09-03 (T-053 X-1): trap/mret/dret records carry pc_if, see the rvfi_pc_wdata row.
- UNVERIFIED-4: exact retirement count between the corrupted response and the internal NMI; RTL reading (T-053 X-10, rtl/ibex_controller.sv:402-438) gives up to TWO ordinary records, the doc bound "at most one instruction after" (exception_interrupts.rst:87-88) is a doc-mismatch candidate; one directed sim decides.


- UNVERIFIED-5: whether INC_ASSERT is defined in the team's VCS build (prim_assert.sv:59-111);
  the protocol assertions cited in sections 2-3 exist only under it.
Total: 5 unverified items in this document; the behaviour summaries carry their own list.
