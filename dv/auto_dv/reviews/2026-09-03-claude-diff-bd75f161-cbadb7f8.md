# Cross-model review - committed diff bd75f161..cbadb7f8

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session bc7e7193-2d8b-4390-a319-c536d0699fb4; sandbox: bubblewrap, working directory = detached read-only checkout of commit cbadb7f8dcbb66b22ad5d1a610a220b476e69fa3 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit cbadb7f8dcbb66b22ad5d1a610a220b476e69fa3
**Date:** 2026-09-03
**Target:** committed diff bd75f161..cbadb7f8 (echo at raw line 1)

---

TARGET: bd75f16155e1fc89ff4fbb0cd9be53ad6dbaa239..cbadb7f8dcbb66b22ad5d1a610a220b476e69fa3

Scope reviewed: the single commit cbadb7f (180 files, 23 modified, 157 new), from the detached checkout. Verified independently: no path outside dv/auto_dv and no rtl/ change; every changed file ASCII; every new file gen_-prefixed; 156 new logs with 156 new manifest rows; the 67 sha256 values in gen_fu_l7_sources_sha256_w.txt match the committed sources (sha256sum -c clean) and the list itself hashes to e287c87e3fdf8a97, build w; the compile_w log has no warning in any gen_ file; the run headers of the cited catch runs carry the build shas the mutation table names (MUT-SUP 10863e69, MUT-SUPB dc49aa23, MUT-SUP2 d1b45952, MUT-NT 6a5417dd, MUT-NIB 61d49617, MS-IRQ 397d3500, MS-DBG 95b30331, WM2 bcbb55ba), with the two exceptions listed below. No SV compile or simulation was run by me.

Judgement per requested item:

1. T-183 gate. The code accepts the undo only when take_intg_word finds the load's word and rd_addr is 0, otherwise an isa_rd miss; matches the CM25-M-2 / CR8-M-1 row. MUT-SUP and MUT-SUPB catch logs show exactly the gate's message (1 error each, ablation PASS); MUT-SUP2 shows 83 gate refusals plus the consequent rd mismatches, ablation PASS; the green intg_s7_allchk shows rf_wr_suppressed=83, 54 internal NMIs, UVM_ERROR 0. The RTL claim (rvfi rd fields cleared when rf_we is low; rvfi_rf_wr_suppress_wb = instr_done_wb & ~rf_we_wb_o & outstanding_load_wb & lsu_load_resp_intg_err, rtl/ibex_core.sv:2385) holds. One semantic gap found (finding 1).

2. irq checker. The per-line release (line bit cleared, expectation kept while other lines remain, order_at restarted) and the report_phase never-taken rule are as described. MUT-NT: 31 per-line bound errors on lines 00004, ablation PASS, and the retained tb batch log confirms the same mutant PASSed both runs on build 88c4cfa2 before the per-line rule. MUT-NT2 seed 3: the end-of-run message once, ablation PASS; seeds 1 and 2 PASS both ways as recorded. MUT-NIB bound 0: 54 errors, one per announcement; the tb7 batch shows bound 1 PASS both ways, so the "exactly one record" latency claim is supported. Debug-mode suspension of the count matches handle_irq (rtl/ibex_controller.sv:498).

3. intr_now / NMI window. The monitor's transaction is no longer written; the window is the irq driver's NM raises in the current and previous compared record, joined to the pin sample. All six storm_nmi seeds and the irq_storm_nmi run report nmi_preempted=0 with UVM_ERROR 0; the owed red is stated in the scoreboard doc, the TDD record Section 11 and the CM25-M-1 row.

4. SVA. sva_icram_widths now uses the bound TagSizeECC/LineSizeECC; sva_alert_minor_window uses the ICACHE_ECC_WINDOW parameter bound to GEN_ICACHE_ECC_WINDOW = 2; chk_en reads gen_tb_pkg::PLUSARG_CHK_SVA_* / PLUSARG_CHK_ALL (all nine exist, gen_tb_pkg.sv:92-103, compiled before gen_protocol_props.sv in gen_tb.f). The four mutant catch logs show the named property (sva_icram_tag_write_implies_req 397, sva_irq_pins_known 2, sva_dbg_req_known 2, sva_alert_internal_never 2851) on instance gen_tb_top.u_dut.gen_protocol_props_i, ablations PASS; the inert ibex_top form is in the rtl batch log as recorded. The DCSR constants are consumed in gen_checkers_pkg.sv:300 (the dbg_dret rule), not in gen_protocol_props.sv.

5. Shim mstack. rtl/ibex_cs_registers.sv asserts mstack_en on every csr_save_cause outside debug mode (the `else if (!debug_mode_i)` branch) and restores from it on mret only while nmi_mode_i; the controller clears nmi_mode on the first mret (rtl/ibex_controller.sv:958-960). The shim's stack_pre push on every trap with !was_debug && !s->debug_mode, and the restore gated on g_nmi_mode, match. UT 12b red log: 6 FAIL lines on the pre-2c shim; green log: PASS (0 failures), stamped.

6. Docs/records. Statements checked against code and logs hold, except the record inaccuracies below. The CM43-L-7 DECLINED reasoning (different packages, full module path in manifest rows, T-218 family naming) is coherent and recorded as a decline rather than silently dropped.

7. DV never modifies RTL: confirmed (mutants out of tree, `source tree untouched` hashes equal the committed rtl/ibex_core.sv 88b8bf39 and rtl/ibex_load_store_unit.sv 86e156ef).

8. Rubrics: ai-slop-comments PASS (item-ID anchors follow the file's existing convention; no restating or history in code comments); rtl-purity PASS (no rtl/ lines); magic-numbers PASS (the new mcause and dcsr constants live in the knobs yaml home and are rendered to SV, C and Python); forces-and-hier-access PASS (no force, no hierarchical drive); assertion-integrity PASS (sva_alert_minor_window's window is unchanged in effect at ICACHE_ECC_WINDOW = 2; no assertion removed or weakened; the two split covers were already covers before this diff).

Findings:

[Medium][dv/auto_dv/env/gen_rvfi_pkg.sv:480] The gate looks up only `{t.mem_addr[31:2], 00}`. rvfi_mem_addr is the load's effective address (rtl/ibex_core.sv:2209 lsu_addr = alu_adder_result_ex), while the bus driver announces per transaction at the word-aligned bus address (data_addr_o = data_addr_w_aligned, rtl/ibex_load_store_unit.sv:722; the second half of a spanning load is at +4). A spanning load whose corrupted response is the second half sets rvfi_ext_rf_wr_suppress legitimately, but the gate finds no announcement and raises a false `isa_rd` miss. The 83 accepted loads of the s7 run do not exercise this case. - Consult both words of a spanning access (as CM25-H-2 already does for take()): try the first word, and when mem_rmask spans, the word at +4; add the spanning-load case to the gate's evidence.

[Low][dv/auto_dv/tb/gen_tb_pkg.sv:547] note_intg pushes every data-side corruption into intg_words, stores included, and nothing consumes store entries or second-half entries; they age out only past depth 256. A later lying rf_wr_suppress on a clean load of the same word is then accepted, so the gate is "a corruption of that word was announced at some point", weaker than "announced for that load". - Push only load transactions (the announcement has p.we), or stamp entries with a cycle and reject entries older than the response-to-record lag.

[Low][dv/auto_dv/mutations/gen_mut_step2b.md:172] The MUT-NT2 row cites build 2643308399b05e33, but the retained seed-3 catch run header and the tb9_s1..s3 batch logs carry 4e4a02897de732d3; 2643308399b05e33 is the tb8 batch's earlier form of the mutant. - Cite 4e4a02897de732d3 for the retained catch and name the tb8 / tb7 forms as discarded attempts.

[Low][dv/auto_dv/mutations/gen_mut_step2b.md:142] The provenance line says the four SVA mutants were built from the wit_root copy between builds v and w; MS-ICRAM's catch header carries build u (b7b1b3fe53bc65ec) and MS-ALERT's carries v exactly (cf73fd8a625e89a8). The sva_icram rule is untouched between u and w, so the evidence stands, but the statement is imprecise (same sentence in gen_tdd_step2b.md:429). - State per mutant which build the RTL copy was taken beside.

[Low][dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l7_lockstep_irq_storm_export_irq_entry_rows.txt:1] The header says 574 rows; the file holds 199 rows with no truncation note (the TDD record counts 573). - Mark the file as an excerpt with the kept count, or retain the full row set.

[Low][dv/auto_dv/evidence/gen_critic_response_fu2a.md:54] The CM43-L-3 row says the DCSR constants slice dcsr "in gen_protocol_props.sv"; the consumer is gen_checkers_pkg.sv:300. - Correct the file name.

[Low][dv/auto_dv/env/gen_checkers_pkg.sv:303] The dbg_dret error message still prints `dcsr_q[1:0]` while the compare uses GEN_DCSR_PRV_BIT_HIGH:LOW. - Use the constants in the message too.

[Low][dv/auto_dv/env/gen_checkers_pkg.sv:267] `never_taken` is counted but not reported in the GEN_IRQ_CHK summary line, so a green run's log cannot show the rule ran. - Append `never taken=%0d` to the summary.

[Low][dv/auto_dv/env/gen_checkers_pkg.sv:262] The end-of-run rule does not exclude a run that ends inside NMI mode (nmi_mode is tracked in this checker), where the DUT masks all lines; a held line at such an end is a false error. The per-entry bound has the same gap, so this is consistent rather than new. - Add `&& !nmi_mode` to both.

[Low][dv/auto_dv/tb/gen_protocol_props.sv:16] The parameter default `ICACHE_ECC_WINDOW = 1` disagrees with the yaml constant (2); the bind overrides it, so no effect, but the default documents a stale value. Also line 273's form `$past(x,1) || $past(x,ICACHE_ECC_WINDOW)` is two points, not the 1..N range the comment describes, so a future value of 3 would skip cycle 2. - Set the default to 2 (or drop it) and express the window as a range.

Final verdict: APPROVE-WITH-CHANGES
