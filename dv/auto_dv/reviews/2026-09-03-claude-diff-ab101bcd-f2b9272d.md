# Cross-model review - committed diff ab101bcd..f2b9272d

**Reviewer:** claude CLI 2.1.259 (Claude Code); run-reported model: claude-fable-5-1,claude-haiku-4-5-20251001; requested effort: high (the CLI does not report the effective setting); fresh session 0c43623a-870a-4b2e-9d24-227bb239357c; sandbox: bubblewrap, working directory = detached read-only checkout of commit f2b9272d35bb335145a6f9cd1a162c93961d95b4 (the live working tree is not read), filesystem read-only except this run's own output directory, scratch HOME (no access to the executing model's settings, instructions or memory), private PID namespace; network open for the model API, web tools disallowed by policy (fallback reviewer per owner ruling A-001)
**Codex unavailable because:** ERROR: You hit your spend cap set by the owner of your workspace. Ask an owner to increase your spend cap to continue.
**Wrapper:** dv/auto_dv/tools/gen_cross_review.sh blob 713e8c09 (the copy executed; equals the wrapper committed at the reviewed commit); reviewed commit f2b9272d35bb335145a6f9cd1a162c93961d95b4
**Date:** 2026-09-03
**Target:** committed diff ab101bcd..f2b9272d (echo at raw line 1)

---

TARGET: ab101bcdfc195cb769b478e71f81d28023257c10..f2b9272d35bb335145a6f9cd1a162c93961d95b4

Scope confirmed: one commit, one new file `dv/auto_dv/evidence/gen_counter_csr_anchors.md` (113 lines, ASCII, sha256 daf32811888d...). No RTL, TB, or CI change. Every RTL claim below was checked against the cited lines in this checkout.

**Claims verified (all supported at the cited lines)**

- Parameter path: `ibex_configs.yaml:59-60` (MHPMCounterNum 10, MHPMCounterWidth 32) -> `gen_dut_top.sv:43-44` (defaults 0/40), `:244-245` pass-through -> `ibex_core.sv:25-26`, `:1438-1439` -> `ibex_cs_registers.sv:21-22`. Banner at `gen_dut_top.sv:441-443`. SIM_RECIPE:50/69-71 and `gen_flow_const.py:77` as cited.
- Decode: `mhpmcounter_idx = csr_addr[4:0]` at :400; `illegal_csr_priv` :403; `illegal_csr_write` :404; default arm :702-703. `ibex_pkg.sv` has no 0xB01/0xB81/0xC01/0xC81 entry (grep confirms; :564-565, :630-631, :661-662). time/timeh therefore fall to the default arm in every mode including debug; `illegal_csr_dbg` at :402 cannot rescue them.
- Write enables gated by `csr_we_int` (:771) which includes `~illegal_csr_insn_o` (:1020-1023). Counter/event arms :845-871; no `CSR_MHPMEVENT` arm anywhere after line 700 (grep) and the case has `default:;` at :886, so mhpmevent writes are ignored for every index. mhpmevent read one-hot :1605-1611, inactive 13..31 :1615-1618.
- gen_cntrs/gen_imp/gen_unimp :1667/1670/1699-1700; unused we tie-offs :1716-1717; counter 10 spec read :1691; minstret spec read :1658 with instr_ret_spec_i = perf_instr_ret_wb_spec (`ibex_core.sv:1551`, `ibex_wb_stage.sv:206`).
- `ibex_counter.sv`: write priority over increment :44-50; high-word write keeps low word :38-41 and only `[CounterWidth-1:0]` is stored :45; bits above CounterWidth read 0 :86-90; reset 0 :69/:78.
- mcounteren/mcountinhibit: storage widths :304/:309 (13 bits); slices and bit-1 force :1556-1557, :1566-1567; comments :1555/:1565; zero-extension :1714/:1732 (10 < 29 branch); mcountinhibit reset :1725; `u_mcounteren_csr` Width 13, ShadowCopy 0, ResetValue 0, wr_en mcounteren_we :1736-1748; `mcounteren_we = mcounteren_writable_i == IbexMuBiOn` :845 (silent no-op, no trap path). U-gating :618/:632.
- Controller mtval :866-868; doc anchors `cs_registers.rst:21-25`, `:598-600`, `performance_counters.rst:69-75` match. Referenced evidence sections exist: `gen_cg_sampling_anchors.md` §21 (line 345), §47 (line 765); `gen_b8_rtl_facts.md` §4 (line 95); `gen_hpm_event_defs.md` present.

**Findings**

[Medium][dv/auto_dv/evidence/gen_counter_csr_anchors.md:29] Omitted Ibex behaviour the shim needs: the instruction that writes minstret is itself counted after the write. The CSR write happens when the instruction completes ID/EX (`ibex_id_stage.sv:747`, csr_op_en on instr_id_done), and its retirement increment arrives one cycle later from WB (`ibex_wb_stage.sv:208`, `ibex_core.sv:1549`), so `csrw minstret, V` leaves minstret at V+1 after the writer retires. The "write wins over increment" rule at `ibex_counter.sv:44-47` applies only to an increment in the same cycle and does not swallow the writer's own count. The ISS convention (and the priv-spec statement that an explicit write takes precedence over the writer's increment) yields V, and the shim derives `retired` from the model's minstret delta (`gen_isa_shim.cc:431,465-466`) while minstret is not synced from RVFI (`gen_rvfi_pkg.sv:443-444` sync only mcycle and hpm). - Add a row to section 2 and a line to section 10 stating the ordering with these anchors, and note the shim consequence (either sync minstret or special-case a minstret write step). Spike source is not in this tree, so the ISS side is stated from convention, not verified here.

[Low][dv/auto_dv/evidence/gen_counter_csr_anchors.md:39] "no effect" / "no-op" for a mhpmcounterXh write (3..12) is imprecise: `we` is asserted (`ibex_counter.sv:35`), so `counter_d = counter_load[31:0]` (old value) takes priority over `counter_upd` (:44-47) and an event increment in that cycle is dropped. The stored value is unchanged, but the counter is not "as if the write never happened". Practically invisible to the shim (hpm counters are synced per record), but the note is the source of truth. - Reword to "value held; an increment in the write cycle is lost" and cite :44-47.

[Low][dv/auto_dv/evidence/gen_counter_csr_anchors.md:6] The note's question list is `dv/auto_dv/work/test-writer/batch3/gen_pmc_ctrl/README_state.md`, which is under the gitignored `work/` tree (`dv/auto_dv/.gitignore:4`) and is not in this commit, so section 9's "claims confirmed or corrected" cannot be reproduced from the committed tree. - Quote the four claims verbatim in section 9 (they are already paraphrased) or point at a committed copy.

[Info][dv/auto_dv/evidence/gen_counter_csr_anchors.md:81] "any write form traps in every mode" for the 0xCxx aliases: `csr_wr` (:1011) is derived from `csr_op_i`, and the decoder demotes CSRRS/CSRRC with rs1 = x0 to `CSR_OP_READ` (`ibex_decoder.sv:257`), so `csrrs rd, cycle, x0` is a legal read. - Say "any op with a non-zero write source" or "CSRRW, or CSRRS/CSRRC with rs1 != x0".

**Rubric results (Zone A set)**

- ai-slop-comments: `{"status": "PASS"}` (no filtered file types touched; the added text is a documentation file under `dv/auto_dv/evidence/`, outside the rubric's filters; content is information-dense, no history narration or restatement).
- rtl-purity: `{"status": "PASS"}` (no `rtl/` change).
- magic-numbers: `{"status": "PASS"}` (no `.sv/.py/.sh` change; the values in the note are RTL anchors with citations, which is the note's purpose).
- forces-and-hier-access: `{"status": "PASS"}` (no TB code added).
- assertion-integrity: `{"status": "PASS"}` (no assertion or checker touched).

Fence: the note reads only files in this clone plus doc anchors FENCE.md permits; no out-of-fence source is cited.

Final verdict: APPROVE-WITH-CHANGES
