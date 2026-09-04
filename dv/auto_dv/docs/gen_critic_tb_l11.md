# Critic verdict: tb-infra landing 10, Slice A (commit 73ff075, diff base 6f35cae), reviewed as tb_l11

Scope (the Orchestrator's): the four Slice A covergroups gen_rvfi_record_cg, gen_mul_timing_cg, gen_rst_boot_cg and gen_sec_ctrl_inputs_cg with their
samplers and proof manifests; the renderer grammar and the re-rendered gen_fcov_groups.svh; the tb_l9 write-corner fixes in the shim; mutants
FM12-FM15; the response rows CR-8, CR-9, CR-10, A2c-1..7, CM123 and CM132. Base verdicts touched: gen_critic_tb_l8.md (4c71724506d59387) L-1..L-5,
gen_critic_tb_l9.md (e0fdf68ca1e9e4a4) M-1, M-2, L-1..L-5, I-1, gen_critic_tb_l10.md (6b26287cce66cfc9) L-1..L-5, I.

Artifacts reviewed (committed blobs at 73ff075; sha256 first 16 hex):

- dv/auto_dv/env/gen_fcov_pkg.sv  8faf5e0d8b481186
- dv/auto_dv/env/gen_fcov_groups.svh  726c32c713aa3ae7
- dv/auto_dv/tb/gen_fcov_codegen.py  0afb7fbc97a49a4e
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  975c92fae79676e3
- dv/auto_dv/env/gen_agents_pkg.sv  d3f0672de0a270fd
- dv/auto_dv/env/gen_env_pkg.sv  17450461d3c443ef
- dv/auto_dv/tb/gen_tb_top.sv  f6caea8deba4f222
- dv/auto_dv/isa/gen_isa_shim.cc  4829680de4ad27d6
- dv/auto_dv/isa/gen_ut_isa_shim.cc  5d7a5731adda12f4
- dv/auto_dv/stim/gen_directed/gen_cpuctrl_directed.S  d09c2925d6855af6
- dv/auto_dv/stim/gen_directed/gen_icache_en_directed.S  15bf464120957ab2
- dv/auto_dv/evidence/gen_tdd_fcov.md  a876cedb9caad10f
- dv/auto_dv/evidence/gen_tdd_step2b.md  46cbe5e438abd325
- dv/auto_dv/mutations/gen_mut_fcov.md  41eb03368832aa21
- dv/auto_dv/mutations/gen_mut_step2b.md  1832050c4351a80e
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  c61e6f123109bc7f
- dv/auto_dv/evidence/gen_critic_response_fcov.md  b9823dc833906a48
- dv/auto_dv/docs/gen_component_api_fcov.md  73dcd31a3e11c701
- dv/auto_dv/docs/gen_component_api_isa_shim.md  a98ee0de2d93b1d3
- dv/auto_dv/docs/gen_component_api_scoreboard.md  74b9a68f402a18f7
- dv/auto_dv/docs/gen_probe_register.md  27a0befb70a4a8db
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  d89d1fb95238228c
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l12_sources_sha256_ai.txt  b9adcdeb1cd01799
- dv/auto_dv/evidence/gen_tdd_logs/fcov/gen_fu_l12_sources_sha256_y.txt  e493e548da55b9ce
- dv/auto_dv/docs/gen_fcov_plan.md  5e96fffa8c5332df
- the 127 gen_fu_l12_* files under dv/auto_dv/evidence/gen_tdd_logs/fcov/ (manifest rows recomputed 127/127; the hand-off said 132) and the ten proof manifests gen_fcov_proof_slice5*.fcov.yaml

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, LOG-058,
gen_fcov_plan.md CG-RVFI-001 (:5741), CG-MUL-002 (:551), CG-RST-001 (:5576), CG-SEC-005 (:5475); rtl/ibex_id_stage.sv:1213-1220; Spike's csrs.cc (the rv32
half wrappers replaced here).
Method: detached git worktree of 73ff075. Build ai identity first-hand: the recipe of gen_tb_local.sh gives b9adcdeb1cd01799 under the UTF-8 sort, equal to
the 18 build-ai run headers, the compile log and the sha256 of the retained 70-line list, byte-identical to my recompute; every listed sha equals the
committed blob (audit). Library and flow self-tests PASS; gen_knobs_codegen and gen_fcov_codegen --check up to date on the tree; the codegen unit test
PASS with 29 OK lines (the five Slice A grammar cases among them); 18 covergroups rendered. The shim identity of the unit-test logs re-derived by me: the
green's shim sha (a76ec7dd3fd003bd) equals the committed gen_isa_shim.cc with one comment reverted (:1643 -> :1627), verified by sed and sha256 (L-1);
the red's shim (34559ec691021abd) is the committed T-235 shim. The canary hash of the Slice A batch (1d9e2f8d9e5927dd) compared by me with the committed
blobs: gen_rvfi_pkg.sv, not gen_fcov_pkg.sv (M-1). One unnamed subagent (an evidence audit of the 127 files, the ten manifests and the record figures,
told the fence, kept out of dv/auto_dv/reviews/), its findings re-checked in the blobs where they carry weight. EXPOSURE: none beyond the Orchestrator's
sha-and-scope message and the git log subjects naming review levels; the CM123 / CM132 rows quote artifacts I had read for tb_l9 / tb_l10. The landing-10
cross-model artifact was not read before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES. The four covergroups, their samplers and proofs, the renderer grammar and the tb_l9 write-corner fixes are built as the
plan and the RTL ask and are proven on an identified build. Two mediums in the records: three response rows and the TDD record say the mutation canary
now hashes the mutated file and that the FM12-FM15 mutant diffs are retained, and neither is true of the committed artifacts; and the FM12-FM15
ablations have no recorded run (the batch's ablation step crashed on every mutant and the retained ablation logs carry no stamp). Eight lows, two of them
adopted from the cross-model artifact after verification (Section 6).

## 1. What was verified

| item | as built | intent anchor | evidence |
|---|---|---|---|
| gen_rvfi_record_cg (CG-RVFI-001) | rec_sample: trap, intr, mode (H/S na), insn_kind (zcmp_uop / c16 / i32), rd / rs1 / rs2 / rs3 zero classes, pc_delta (plus2 / plus4 / jump_fwd / jump_back / redirect_other for mret, dret, fence.i; a trapping record na, cp_trap owns it), order_step.first, pc_continuity against the previous record with the plan's four discontinuity causes and na otherwise, valid_gap from the record cycle stamps, intr_kind, rd_source | the plan block :5741-5770, the deviation (trap -> na) stated in the API doc :249 | proofs slice5a / 5a2 PASS 30 / 30 on ai; FM12 (a 32-bit sequential record classed plus2) fails slice5a on cp_pc_delta.plus4, build 62d7aff8f43a9e23 = its compile log, original sha 8faf5e0d8b481186 = the committed sampler; 20 classifier rows in the unit test (74 cases, 0 failures) |
| gen_mul_timing_cg (CG-MUL-002) | mt_sample on the record after a multiply: cp_delta iff clean (no wb_busy, no fetch_stall), cp_prev from the record before the multiply, cp_next_dep from the successor (na at the end), cp_wb_busy / cp_dmem_delay from the data agent's completed transactions stamped on the bridge counter, cp_fetch_stall from the fetch agent's response stamps; the first retirement after reset not sampled; c.mul outside the OP condition | :551-566; the ID-entry APPROXIMATION (the previous retirement's cycle) stated in the API doc :256 | slice5b / 5b2 PASS 14 / 13; FM13 (a load before the multiply classed ALU) fails cp_prev.load; the prefix defect run and the fast run retained (cr_op_delta_clean 4 / 4) |
| gen_rst_boot_cg (CG-RST-001) | one sample per reset at the first event (or at report when fetch stayed disabled): boot_addr class, low byte, fetch_enable at the release edge, the pins pending at the release (irq lines, nm, debug_req), first_event with the maskable-entry ignore as na, hart_id class, reset_kind power_on (mid_run unreachable, stated), boot_to_req from the fetch agent's first request after the release | :5576-5605; WP-11 NOT BUILT | slice5c / 5c2 PASS 8 / 8 (fetch_en on and off, boot_to_req 62 and 2); FM14 (a high boot page classed mid) fails cp_boot_addr.high |
| gen_sec_ctrl_inputs_cg (CG-SEC-005) | events: cpuctrl_read (bits 7:6, bit 8, icache_en in debug, rvfi_ext key valid), fetch_en_change and mcounteren_w_change from the pins polled per cycle, key_req with its context from the scramble-key agent's events, key_valid_change, mcounteren_write with the pin class and the read-back effect; boot_addr_change unreachable (the TB never changes boot_addr_i), stated | :5475-5500; the API doc :278-279 | slice5d / 5d2 / 5d3 / 5d4 PASS 10 / 10 / 6 / 3 on gen_cpuctrl_directed.S (a double fault reaches all four bits-7:6 values) and the key-withheld run; FM15 (bit 7 dropped from the read-back) fails the two b7_1 bins; the first FM15 form (a bit swap) recorded as invisible to a bin checker |
| renderer grammar | wrapped bullets joined; `cp_x iff <guard> = <expr>`, `cp_x:` without an expression, `; ignore_bins x{..}: reason` not a bin, names-only bins and names-only crosses from the CSV | the plan's forms | five same-render unit cases; --check up to date on the tree (my run) and gen_fu_l12_codegen_check.log; 18 covergroups, 694 coverpoint bins, 2786 cross bins in the svh |
| tb_l9 M-1 (the written half) | gen_minstret_half_csr_t per address over one 64-bit view; write_half composes the value from the known half | Spike's rv32 wrappers replaced (csrs.cc:771-798) | row "csrw minstreth of its current value at gap 1: the low word still loses the increment due"; red 2 failures on the committed T-235 shim (34559ec691021abd = 158f5be), green 278 OK |
| tb_l9 M-2 (the writer before) | the gap-1 corners skipped when the previous step wrote minstret / minstreth (g_prev_minstret_written) | rtl/ibex_id_stage.sv:1213-1220 (the writer counted by neither side) | rows for `csrw minstret, x0; csrw minstreth, x0` at gap 1 (both words 0, the nop after counts one); the same red |
| tb_l9 L-1, A2c-2, CM123-L-8 | build y's compile log and 69-line list (e493e548da55b9ce, two files differ from 158f5be: the shim and the test); the 12b red re-run on bd75f16's shim with cbadb7f's test (76293bbdd49351b1 / 991603011f5b4f6f, 6 failures); the T-235 rows have no red as committed because the committed test does not compile against the pre-integration shim (gen_isa_set_retire_gap undeclared), stated | the tb_l9 / tb_l7 asks | the logs' stamps equal the blobs |
| tb_l10 L-1 matched controls | knob-off runs with the knob-on plusargs on ai: 27 and 13192 UVM_ERROR lines, 0 firings = the knob-on runs' non-B8 counts | tb_l10 L-1 | gen_fu_l12_b8_zcmp_dummy_off_1000_*, _popret_off_1000_* |
| record corrections (tb_l8 L-1, tb_l10 L-3, A2c-1..7) | MUT-NT2's tb7 form b74b099eeff78e04 and order 2956; MUT-SUP2 421 lines; the provenance inference stated with the four late mutants; the nmi sweep's one entry; the bound-1 observation unretained; row 130; the s7 placement sentence withdrawn; the six header notes | the batch logs | verified against gen_fu_l7 logs by the audit and by me for the tb7 / tb8 forms |

## 2. Closure of the base verdicts

- gen_critic_tb_l9.md: M-1, M-2 CLOSED; L-1 CLOSED (build y identified; the red's variant diff retained); L-2 CLOSED with one new slip (L-2 below);
  L-3, L-5, I-1 CLOSED; L-4 NOT closed: the rows say it is (M-1 below).
- gen_critic_tb_l8.md: L-1 CLOSED (the mv_res run now named); L-2 CLOSED (the check log names its tree); L-3: L-8 owed (source), L-9 / L-10
  CLOSED; L-4 routed to the plan owner (the derivation copies the plan); L-5 NOT closed: the row says it is (M-1 below).
- gen_critic_tb_l10.md: L-1 CLOSED (matched controls and the header counts), L-2, L-3 CLOSED, L-4 stated with the program owed to landing 11,
  L-5 notes CLOSED and canary NOT (M-1), I CLOSED (the check log retained). M-1 / M-2 stay owed to landing 11 as the Orchestrator ruled.

## 3. Findings

### M-1 (medium) [S4 honesty] Three DONE rows and the record claim a canary and mutant diffs that the artifacts do not carry

gen_critic_response_fcov.md CR-8 L-5, gen_critic_response_fu2a.md CR-9 L-4 and CR-10 L-5, and gen_tdd_step2b.md Section 12.1 L-4 say the Slice A
batch's `source tree untouched` line "hashes the mutated file's shared-tree copy (1d9e2f8d9e5927dd = gen_fcov_pkg.sv)" and that "each batch retains
mutant.diff (gen_fu_l12_MUTCNT_mutant.diff, gen_fu_l12_FM12..FM15_mutant.diff)". The committed gen_fcov_pkg.sv hashes 8faf5e0d8b481186 and
1d9e2f8d9e5927dd is gen_rvfi_pkg.sv (verified against the blobs), so the canary still watches the wrong file; and the only mutant diff in the tree
is gen_fu_l12_MUTCNT_mutant.diff. The mutants are identified without either (original sha = the committed blob, builds = their compile logs), so no
evidence is in doubt; the rows are. Required: the canary on the mutated file (the batch names it beside the hash), the four diffs retained, and the
four statements corrected to what the artifacts show.

### M-2 (medium) [S6 mutation-proof, retention] The FM12-FM15 ablations have no recorded run

gen_fu_l12_oot_mutation_batch_fm_sliceA.log shows the ablation step crashing for every mutant (FileNotFoundError on a hard-coded slice5a manifest path,
:42-52 and the three repeats), the ablation manifests' notes were derived afterwards (gen_fu_l12_ai_driver.log:76), and the four ablation check logs carry
no manifest, report, run or build stamp and appear in no driver or batch line; the manifest rows describe them as "the ablation manifest against the same
report", a description no log substantiates. Their bin counts equal the catch reports', so the checks were probably run by hand; a run nobody recorded is
not retained evidence. Required: the ablation step fixed and re-run under the batch (or any logged command naming manifest and report), the logs replaced,
and the batch failure narrated. The catches stand.

### L-1 (low) [S6 identity] The green unit test ran on a shim one comment away from the committed one

gen_fu_l12_ut_isa_shim.log is stamped shim a76ec7dd3fd003bd; the committed gen_isa_shim.cc is 4829680de4ad27d6, and reverting its one comment edit
(:1643 -> :1627) reproduces a76ec7dd3fd003bd exactly, as the retained red-vs-landing diff also shows. No unit-test run on the committed blob is retained;
build ai compiled the committed file and its lock-step runs are green, so the code is covered and the stamp is not. Re-run the unit test on the committed
file (the stamp line exists for that) with the next shim touch.

### L-2 (low) [S4 record] Runs cited as files that do not exist

gen_tdd_step2b.md Section 12.1 and gen_tdd_fcov.md cite gen_fu_l12_lockstep_pmc_s1_on_* / _off_* for "0 mismatches on the landing build"; the only
gen_fu_l12 pmc files are the build-y red's error list and its classification, and the ai runs exist as two verdict lines of gen_fu_l12_ai_driver.log
(:15-16) with no header, excerpt or verdict file. Retain them or cite the driver lines.

### L-3 (low) [S4 record] Figures

"2788 cross bins" (the svh has 2786: the misa pair left with the re-render); "gen_fu_l12_ut_fcov_codegen.log, 24 OK" (29 OK lines); "up to date against
plan v3i (ec1d8ea)" where the check log's own header says "plan v3h at 329902f + Slice A files" and ec1d8ea is a review-artifact commit; "the 17 run
headers re-retained" (18 carry build ai); "beside build ag (4a670252697ee80e)" with no artifact of ag; the rows' `PASS --` for the logs' `PASS -`; the
six corrected headers say "landing 9" for notes that land in landing 10 (the edits they describe were landing 9's, the notes are not).

### L-4 (low) [schema] The new manifests' anti_vacuity notes are cut at the first physical line

The manifest tool derives each note from the plan's Sample bullet but reads one physical line: slice5a's notes read "rvfi_valid is a pulse (one; the hit
is ..." (the bullet continues "cycle per retired instruction, never continuous ..."), slice5c's carry the Sample text up to "(first retired", and slice5d's
carry CG-SEC-005's first Sample line ("cpuctrl_read: rvfi_valid of a CSR op on CSR_CPUCTRLSTS with rvfi_rd_addr != 0 and") instead of its anti-vacuity
clause, which sits five lines down. The renderer now joins wrapped bullets (this landing's grammar fix); the manifest tool must do the same, and the
ten manifests re-derive.

### L-5 (low) [S2 statement] Sampler simplifications the API doc does not state

cpuctrlsts.icache_enable is tracked from csrrw forms only (a csrrs / csrrc of 0x7C0 leaves the tracked value stale, so key_req's icache_disabled
context can misclassify); the mcounteren write effect cannot classify `dropped` for csrrs / csrrc forms (mcen_new is set to the old value, so only
`applied` or na results); a TB-side counter write (gen_isa_write_csr) sets g_minstret_written and makes the next step skip the gap corners as if the
program had written (no TB write today, CM123-L-3's class). Each is a one-line statement or a small fix.

### L-6 (low) [trace] Proof-manifest bins no item owns

slice5d / 5d2 declare gen_sec_ctrl_inputs_cg.cp_key_delay.immediate and .withheld_then_valid; the coverpoint sits in the plan's "owned by no test-plan
item" table (:191) and has no CSV row. A proof may declare them; the manifest tool should mark such bins (they can credit nothing) so a promoted manifest
never carries them unmarked.

### Informational

- I-1: gen_icache_en_directed.S enters git here; no landing-10 run uses it, and its earlier use (landing 2c's MS-ICRAM catch, image crc 8dca67cf) is
  not tied to this text by any retained line. A one-line note in the record would close the loop.
- I-2: CM123-L-1..L-4 and L-9 are deferred as "source-changing" while this landing changed the shim for CR-9; the deferral is a choice, not a
  constraint, and the four one-line fixes could have ridden with the corner fix.
- I-3: the FM15 first form (a bit swap invisible to a bin checker) is recorded so nobody re-tries it: the right kind of record.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S2 derive from intent: the four samplers follow their Sample lines with the deviations
stated in the API doc (conforming; L-5 for the unstated ones). S6 trust triad: proofs on an identified build, catches identified (conforming); the
ablations unrecorded (M-2); the unit-test green one comment off the blob (L-1). S4 honesty: DONE rows on claims the artifacts contradict (M-1); the
figures of L-2, L-3. One-line verdict: FAIL on M-1 and M-2 until fixed.

## 5. Required for re-review

1. M-1: the canary on the mutated file, the four mutant diffs retained, the four statements corrected.
2. M-2: the ablation step fixed and the four ablation checks re-run under a logged command; the batch failure narrated.
3. L-1..L-6 with the same or the next touch.

CRITIC VERDICT: REQUEST-CHANGES (M-1, M-2). tb_l9 M-1 / M-2 are closed; the Slice A covergroups stand, with L-5, L-7 and L-8 owed on their samplers and records.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-6f35cae5-73ff0751.md, read after Sections 1-5 were written)

REQUEST-CHANGES: two majors, three mediums, five minors.

- Its two majors are the two halves of my M-1 (the canary hash is gen_rvfi_pkg.sv's; the FM12-FM15 mutant diffs do not exist), found independently
  from the blobs.
- Its minor on the batch tracebacks is my M-2. Level disagreement, stated: it asks how the ablation checks were run; I hold Medium because a run
  nobody recorded is not retained evidence under the team's own rule, and the record says PASS without the crash.
- Adopted and verified, as L-7 (low) [S4 record]: gen_fcov_proof_slice5d2.fcov.yaml's header says the key-withheld run makes "bit 8 and
  rvfi_ext_ic_scr_key_valid read 0"; the run's urg report shows cp_bit8_readback and cp_rvfi_ext_key_valid each with one of two bins hit
  (gen_fu_l12_urg_lockstep_cpuctrl_keyw_grpinfo.txt:7135, :7143) and the manifest declares the .one bins; the "Not reached" lists of gen_tdd_fcov.md and
  the API doc omit the .zero bins. Held at Low (the artifact: medium) because the manifest, which is what the check judges, declares what was hit and
  passes; the header sentence and the lists are prose to correct.
- Adopted and verified, folded into L-5: icache_en_tracked is initialised to 1 (gen_fcov_pkg.sv:138) while cpuctrlsts.icache_enable is 0 until software
  sets it (gen_icache_en_directed.S enables it with csrs), and :1056 assigns t.rs1_rdata[0] for every write form (a csrc 0x7C0 with mask 1 sets the
  tracker to 1 as the RTL clears the bit), against its own comment; the write predicate at :1054 has identical branches; `12'h7C0` is written twice
  where GEN_CSR_CPUCTRLSTS is used at :620 of the same file; the hart-id plusarg is re-read at :156 where cfg.hart_id exists. Held at Low (the
  artifact: medium for the tracker) because the only dependent bin, cp_key_req_context.icache_disabled, is declared by no manifest; the fix (init 0,
  the value by op form, the constants, cfg.hart_id) is required with L-5's statements.
- Adopted, as L-8 (low) [S2 plan / code]: cp_pc_delta is na on a trap record while the plan line (gen_fcov_plan.md:5763) keeps "record is a trap" in
  redirect_other; the API doc states the deviation, the plan does not, and the manifests' notes derive from the plan. Route to the plan owner: move
  trap out of redirect_other (cp_trap owns it, as the sampler says) or have the sampler follow the plan.
- Its 2788 / ec1d8ea minor is my L-3; adopted into L-3 after verification: gen_fu_l12_boot_zc_fe1_run_header.txt carries both +gen_fetch_en_at_reset=1
  and =0, so the slice5c2 result (on, boot_to_req two) rests on first-match plusarg semantics; state it beside the manifest or re-run with one value.
- Not in the artifact: L-1 (the unit-test green one comment off the committed shim), L-2 (the pmc ai runs cited as files), L-4 (the truncated notes),
  L-6 (the unowned cp_key_delay bins), I-1..I-3.
- Verdict levels agree (REQUEST-CHANGES both); the work asked for is the same records and small fixes.
