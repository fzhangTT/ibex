# Critic verdict: tb-infra landing 11 (commit f28d09b, diff base f1bc4d9), reviewed as tb_l12

Scope (the Orchestrator's): the rows CR-10 and CR-11 (my tb_l10 and tb_l11), CM132 and CM138 (the landing-9 and landing-10 cross-model reviews), the icache
tag-RAM ECC injection hook behind a knob, the CM123 items, the CR-8 L-8 rewrite, the Slice-A-1 renderer rule, the findings L11-F1..F3. This is the
recorded re-review of gen_critic_tb_l10.md (6b26287cce66cfc9, REQUEST-CHANGES: M-1, M-2) and gen_critic_tb_l11.md (5139a74711c9cf00, REQUEST-CHANGES:
M-1, M-2), whose mediums stood until this landing.

Artifacts reviewed (committed blobs at f28d09b; sha256 first 16 hex):

- dv/auto_dv/tb/gen_protocol_props.sv  cc5d1ddb77610244
- dv/auto_dv/tb/gen_icache_ram.sv  fec0e52bd3eaa79f
- dv/auto_dv/tb/gen_tb_pkg.sv  64d598fc81f3e2ef
- dv/auto_dv/tb/gen_tb_top.sv  491e8a61c5d9db5f
- dv/auto_dv/env/gen_checkers_pkg.sv  c7317468536735fb
- dv/auto_dv/env/gen_rvfi_pkg.sv  2d8e5d5829c15e86
- dv/auto_dv/env/gen_fcov_pkg.sv  51315dd2b793c8a2
- dv/auto_dv/env/gen_env_pkg.sv  4d66d34ae4af7377
- dv/auto_dv/isa/gen_isa_shim.cc  59672952dc4fbfc8
- dv/auto_dv/isa/gen_isa_shim.h  545b3320af2be2f2
- dv/auto_dv/isa/gen_ut_isa_shim.cc  c1c3950de0cccd63
- dv/auto_dv/tb/gen_fcov_codegen.py  5da97b718782a2bb
- dv/auto_dv/tb/unit/gen_ut_fcov_codegen.py  1c0bc1dfdd4c5e2f
- dv/auto_dv/tb/gen_tb_knobs.yaml  cd03033573519f0e
- dv/auto_dv/gen_tb/gen_tests/gen_ut_intg_span.py  3b5ae69d80c79e8d
- dv/auto_dv/gen_tb/gen_tests/gen_ut_irq_nmi_long.py  2b4bb513231038c9
- dv/auto_dv/gen_tb/gen_tests/gen_ut_boot_fe1.py  6407fb9689163153
- dv/auto_dv/stim/gen_directed/gen_icache_ecc_directed.S  3cbeb83684a67946
- dv/auto_dv/stim/gen_directed/gen_intg_span_directed.S  f2f2e5cd1b9a9b5e
- dv/auto_dv/stim/gen_directed/gen_nmi_long_directed.S  c18b6aa0c87d75b0
- dv/auto_dv/stim/gen_directed/gen_minstret_draftb_directed.S  cda936c4f090eddb
- dv/auto_dv/stim/gen_directed/gen_minstret_zcmp_directed.S  c689d80d32a69e34
- dv/auto_dv/evidence/gen_tdd_step2b.md  0822060324719809
- dv/auto_dv/evidence/gen_tdd_fcov.md  a202f3630411331f
- dv/auto_dv/mutations/gen_mut_step2b.md  49c8b2c0a7d1a21f
- dv/auto_dv/mutations/gen_mut_fcov.md  fffc7548a0d8c736
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  604598a19f11e3d8
- dv/auto_dv/evidence/gen_critic_response_fcov.md  b9d4fc9327c97f84
- dv/auto_dv/docs/gen_component_api_misc_monitor.md  9d695b9a5f4a4705
- dv/auto_dv/docs/gen_component_api_irq_checker.md  d3d1ddd4de45b70b
- dv/auto_dv/docs/gen_component_api_scoreboard.md  26d2bde8eb8a2439
- dv/auto_dv/docs/gen_component_api_isa_shim.md  273b39785b396137
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  52850487d8b715ee
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l13_sources_sha256_b2.txt  4a82f30c23f3ce3d
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l13_sources_sha256_shared_out_l12.txt  7a083655868cb9c9
- the 273 gen_fu_l13_* files under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,fcov,mutations}/ (manifest rows recomputed 273/273) and the six re-noted retained copies

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411; rtl/ibex_icache.sv:266
(lookup_actual gated by icache_enable and the invalidation), :540-562 and :585 (the tag ECC check in IC1, alert on any way of a checked lookup), :644 and
rtl/ibex_core.sv:1337 (alert_minor_o = ecc_err_ic1); rtl/ibex_controller.sv:416 and rtl/ibex_load_store_unit.sv:258 (the internal-NMI mtval); rtl/ibex_id_stage.sv
:1213-1220; IEEE 1800 sampled-value semantics (a register q <= d sampled at the same edge equals $past(d, 1)).
Method: detached git worktree of f28d09b. Build identity first-hand: the recipe of gen_tb_local.sh on the tree gives 7a083655868cb9c9 under the UTF-8
sort, equal to the shared-tree canary compile log and to the sha256 of gen_fu_l13_sources_sha256_shared_out_l12.txt (73 lines, byte-identical to my
recompute); build b2 (4a82f30c23f3ce3d, 36 headers, its compile log, its 72-line list) equals the committed tree in every compiled file and omits only
gen_ut_boot_fe1.py, a cocotb module written after the compile (stated in Section 14; I-1). Library and flow self-tests PASS; both codegen --check up
to date; the fcov codegen unit test PASS with 31 OK lines and the knobs codegen unit test PASS. The window slice, the expectation rule, the gate, the
shim corners and the hook were read in the diff and the rules re-derived; the MUT-WIN offending expression, the b2r sources sha, the mutant rows' build
shas, the failure counts, the duplicated Section 13, the latency histogram and the canary hash were re-checked by me in the blobs and logs. One unnamed
subagent (an evidence audit of the 273 files, told the fence, kept out of dv/auto_dv/reviews/), its findings re-checked where they carry weight.
EXPOSURE: none beyond the Orchestrator's sha-and-scope message and the git log subjects naming review levels; the CM132 / CM138 rows quote artifacts I
had read for tb_l10 / tb_l11. The landing-11 cross-model artifact was not read before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: APPROVE. The four mediums of tb_l10 and tb_l11 are closed by source fixes with reds on the old code and greens on an identified build:
the window slice now covers cycles 1..2 and an injection hook makes alert_minor_o reachable, an expectation survives NMI and debug mode, the mutation
canary watches the mutated file and the FM12-FM15 ablations are stamped. Nine lows, three adopted from the cross-model artifact after verification
(Section 6); two of the six mine are the doubled-count and hand-copied-sha errors this team has now repeated across three landings.

## 1. What was verified

| item | as built | anchor / intent | evidence |
|---|---|---|---|
| tb_l10 M-1 window (CM132-H-1) | gen_protocol_props.sv: `lookup_hist[ICACHE_ECC_WINDOW-1:0]`, `alert_minor_o |-> |lookup_hist[ICACHE_ECC_WINDOW-1:0]`, the register comment says bit k = the read k+1 cycles before at the sample | sampled lookup_hist[0] = $past(read, 1): the window is now 1..2 (my tb_l10 M-1 derivation) | red on the true old form: b0h (the landing-10 props, Offending `(|lookup_hist[ICACHE_ECC_WINDOW:1])`, 4 window failures, rate rare); red on b2r (a `|lookup_hist[1]` variant, 215 failures at rate frequent, 9 at rare, all pulses at latency 1); green on b2: 436 pulses, 0 failures, 0 missing (rate frequent), 16 / 0 / 0 (rare); ablation `+gen_chk_all=0` PASS |
| the injection hook | gen_icache_ram.sv: a TAG RAM flips exactly one bit of a lookup read at the regime's rate_per_mille and announces (cycle, way, index, qualified) to gen_icram_events; data RAMs never inject (their ECC is checked only on a hit, invisible from the boundary); knob default none | rtl/ibex_icache.sv:585 (any way's tag error on a checked lookup raises the alert), :266 (a lookup while disabled or invalidating is unchecked) | MUT-ICE-ANN (corrupt without announcing): 436 `alert_minor_o high ... without an announced ECC injection`, ablation PASS; MUT-ICE-MISS (announce without corrupting): 862 `alert_minor_o missing within 2 cycles`, ablation PASS; mutant diffs retained; the mutant builds' lists differ from b2's in gen_icache_ram.sv only |
| the misc monitor's two halves | a pulse needs an injection within GEN_ICACHE_ECC_WINDOW (one pulse per injection cycle); a QUALIFIED injection owes a pulse: the cache enabled per the scoreboard's cpuctrlsts tracking and no invalidation-sweep tag write within GEN_ICACHE_ECC_GRACE_CYCLES (16); the summary prints injections judged / qualified / missing and a latency histogram | the RTL lines above; the TB sees the enable and the sweep late (stated) | the two mutants; the greens' histograms 0 / 436 / 0 and 0 / 16 / 0 |
| tb_l10 M-2 expectations (CM132-M-1) | gen_checkers_pkg.sv: an expired expectation in NMI mode or debug mode is neither judged nor deleted; its order_at restarts, so the bound runs again when the mask lifts | the DUT masks every line in NMI mode (rtl/ibex_controller.sv:498) and in debug mode | MUT-NT3 (irq_external withheld from the first NMI on) on gen_nmi_long_directed.S (a 41-record handler, the line raised 6 records in): on the landing-10 checker PASS (the expectation deleted unjudged: the hole shown), on b2 `lines 00004 raised at cycle 1010 (order 242) not taken within 17 records`, ablation PASS; greens entries=2 and the with-NMI storm |
| tb_l10 L-4 / CM132-L-4 gate (both words) | gen_rvfi_pkg.sv: `a0 = take(mem_addr); a1 = spans && take(mem_addr + 4); announced = a0 || a1` | tb_l7 L-1, tb_l10 L-4 | MUT-SUP3 (the flag and cleared rd fields forced on the clean c.lw of the second word): on the landing-10 gate PASS with rf_wr_suppressed=2 (the lie accepted through the leftover word), on b2 `rf_wr_suppress asserted without an announced integrity corruption for 800002e4 (order=18 ... rd=x0)`, ablation `+gen_chk_isa_rd=0` PASS; green rf_wr_suppressed=1 |
| CM123-L-1..L-4, L-9 (the shim and the gap) | the gap update at the top of write() for every record; the carry corner on `cur`; both corners and the writer mark require g_in_step; the .h comments split; the :451 comment names minstret as the model's own | tb_l9 / CM123 | unit rows: 4 FAIL on the committed 73ff075 shim (4829680de4ad27d6 = the blob), 293 OK on the landing shim (59672952dc4fbfc8 = the blob); gen_minstret_zcmp_directed.S green on both codes (the fold reached the update), gen_minstret_draftb_directed.S red on the old code (L11-F1) |
| L11-F1 | the draft-B compare path never steps the model, so its retirement was uncounted: gen_isa_count_retire(1) bumps Spike's counter unless IR inhibits | rtl/ibex_id_stage.sv:1213-1220 (only minstret writers are excluded) | red model 3 / DUT 4 (build b0), green 0 mismatches (b2) |
| L11-F2 | the model's internal-NMI mtval for a misaligned load whose first half is corrupted is the access address, not the announced word | rtl/ibex_controller.sv:416 `mem_resp_intg_err_addr_d = lsu_addr_last_i`; rtl/ibex_load_store_unit.sv:258 (verified) | red 21 crash_dump errors on b0h (800002e2 against 800002e0), green on b2 |
| L11-F3 | the first hook's flip mask accumulated (a block-local initialised variable is static); the landed hook flips one bit | a TB finding, honestly recorded | b0h run kept (missing=2); the first hook's source is not in the tree (L-6) |
| tb_l11 M-1 / M-2 (CM138-Ma-1 / Ma-2 / m-4) | the batch canary hashes the mutated file's shared-tree copy (`gen_fcov_pkg.sv sha256 51315dd2b793c8a2` = the committed blob, verified); FM12-FM15 mutant diffs retained; the mkablation cause found and fixed; every catch and ablation check stamped with manifest path and md5, report, build, mutant, time | tb_l11 M-1 / M-2 | gen_fu_l13_FM1x_check.log FAIL on the hidden bin, _ablation_check.log PASS (29 / 13 / 7 / 8), no traceback in the batch log; the three DONE rows rewritten to admit the landing-10 claim was wrong |
| tb_l11 lows | L-1 the green unit test on the committed shim; L-2 the pmc runs retained as files; L-3 2786 / v3i 2572fe8 / 18 headers; L-4 the notes carry the whole wrapped clause (verified on slice5a and slice5d); L-5 icache_en tracked from 0 by op form, GEN_CSR_CPUCTRLSTS (0 literals left), cfg.hart_id, mcen_new by op, the TB write no longer marks the next step (unit rows red / green); L-6 unowned proof bins marked in their notes; L-7 the slice5d2 header rewritten; L-8 the DV Lead ruled: a trap record samples redirect_other (slice5a / 5a2 30 bins) | tb_l11 | the blobs and the check logs |
| CR-8 L-8 comment rewrite | 0 comment lines in gen_fcov_pkg.sv still carry a review or landing id (my grep for H-1(, L5R-, landing-N, LOG-0nn, Critic) | the intent-only comment rule | verified |
| Slice-A-1 renderer rule | a bin listed before the `; ignore` clause and named in it leaves the comparison and renders nothing; unit case red on the landing-10 renderer, green now; the include unchanged, --check up to date; 2786 cross bins in the svh | the DV Lead's question | gen_fu_l13_ut_fcov_codegen.log |

## 2. Closure of the base verdicts

- gen_critic_tb_l10.md: M-1 CLOSED, M-2 CLOSED, L-1..L-5 CLOSED (L-3's figures corrected, the canary now right, the notes named), L-6 CLOSED
  (the SVA layer header records the C10 exception, P8 in the register, LOG-076 on the knob name). The REQUEST-CHANGES of tb_l10 is lifted.
- gen_critic_tb_l11.md: M-1, M-2 CLOSED; L-1..L-8 CLOSED. The REQUEST-CHANGES of tb_l11 is lifted.
- gen_critic_tb_l9.md: nothing new owed (CM123 L-1..L-4, L-9 closed here).

## 3. Findings

### L-1 (low) [S4 record] Doubled failure counts, again

Section 14, the MUT-WIN row and the CM132-H-1 row say sva_alert_minor_window "FAILS 431 times in the frequent run and 19 in the rare run"; the
excerpt headers count `UVM_ERROR lines counted by grep: 215, of them sva_alert_minor_window: 215` and 9, and the UVM summaries say 215 and 9. 431
and 19 are 2n + 1: the VCS failure line, the UVM_ERROR line and the summary line per firing, the same doubling CM132-L-1 corrected for the B8
probe in this very landing's records. Required: the counts from the header's "of them" field, and a rule in the record: a firing count is the
assertion's own line count, never a grep over the token.

### L-2 (low) [S6 identity] MUT-WIN is not the landing-9 slice

The row, Section 14 and the CM132-H-1 row call b2r "the landing-9 slice `[ICACHE_ECC_WINDOW:1]`". The retained b2r verdicts print
`Offending '(|lookup_hist[1])'`, the b2r list's gen_protocol_props.sv (64015c0d6e612605) is neither f1bc4d9's (2a6eef75bbbd523a) nor f28d09b's, and
no MUT-WIN mutant.diff is retained, so the compiled form is a third variant (bit 1 of the new register: the same "never latency 1" meaning, not the
literal). The true old form's red exists: the b0h run carries `Offending '(|lookup_hist[ICACHE_ECC_WINDOW:1])'` with 4 window failures beside the
first hook's 2 missing pulses. Cite b0h as the red of the committed landing-9 form, describe b2r as what it is, and retain its diff.

### L-3 (low) [S4 record] Hand-copied build shas in mutant rows, third landing running

gen_mut_step2b.md's MUT-SUP3 row says 5e241935603d2310 and MUT-ICE-ANN says 95aec3cd2c0f9bc6; every retained header, compile log and list of
those mutants says b5c7b2b602d2087a and 68c8d74dfaacb9a8, and the row's shas appear in no retained file. MUT-NT3's "(order 24x)" is the log's
"(order 242)". After tb_l7 L-6 (MUT-NT2) and tb_l10 L-3 (the same row again), the rows should be generated from the batch logs' own lines, not
typed.

### L-4 (low) [S4 record] Section 13 appears twice

gen_tdd_step2b.md carries `## 13. Landing 9: ...` at :473 and again at :506 with the same text: the diff inserted the second copy. Remove one.

### L-5 (low) [S4 precision] The window's upper edge is declared, not measured

Every retained injection run puts every pulse at latency 1 (histograms 0 / 436 / 0, 0 / 16 / 0, 0 / 4 / 0); latency 2 never occurred, so the yaml
desc's "within 1..2 cycles ... measured on the landing-11 injection runs" measured the lower edge only. Say "1 observed, 2 the declared bound", or
find the case that gives 2 (the RTL path suggests none: the tag error is combinational in IC1 the cycle after the read).

### L-6 (low) [S6 retention] Unstamped and unidentified pieces

The 11 proof check logs (gen_fu_l13_slice*_check.log) carry no stamp line while the FM check logs do, and all 11 urg commands name the same
vdb directory with freshness asserted in a comment; the reds of the landing-10 code on b0, nt3_b0 and sup3c_b0 have no compile log and no
per-file list (b0h has a list, not a compile log); the first hook's gen_icache_ram.sv (b0h list 3c122f98f67f592e) is in no commit and the FSDB
behind L11-F3 is not retained (both narrated). Stamp the proof checks as the FM checks are; keep a list and compile log for every red build.

### Informational

- I-1: build b2 predates gen_ut_boot_fe1.py, so its list does not pin the module the boot_zc_fe1 run loaded; the landed tree's own list
  (7a083655868cb9c9, the shared-tree canary compile) does, and Section 14 says so.
- I-2: the "shared-tree canary" runs on the committed tree (seven greens incl. 83 suppressed loads, 54 internal NMIs, 436 pulses) are the
  right closing form for a landing whose build was cut before its last edit.
- I-3: the injection hook is test equipment in the TB's RAM model, never an RTL change; the rate lives in the regime table; data RAMs are
  excluded with the reason. Conforming to the DV-never-modifies-RTL rule.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: every fix has a red on the old code and a green on an
identified build, with a mutant and ablation for the new rules (conforming); MUT-WIN's compiled form unidentified (L-2). S4 honesty: the
landing-10 claims withdrawn in the rows themselves (conforming); doubled counts and hand-copied shas (L-1, L-3); the duplicated section (L-4).
S2 derive from intent: the window, the mask rule, the mtval rule and the qualification all cite the RTL lines that define them (conforming).
One-line verdict: PASS with the lows.

## 5. Verdict

CRITIC VERDICT: APPROVE. tb_l10 and tb_l11 are lifted. Lows L-1..L-9 go to tb-infra's next touch (L-7's qualification fix with the next source
landing); L-1 and L-3 name a rule the team should adopt rather than a line to fix.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-f1bc4d9b-f28d09b9.md, read after Sections 1-5 were written)

APPROVE-WITH-CHANGES: one medium, five lows.

- Its medium is my L-1 (431 / 19 against 215 / 9, the doubled count). Level disagreement, stated: it rates the slip Medium because "for 436 pulses"
  reads as nearly every pulse failing where 215 of 436 did; I hold Low because the red is real, retained and correctly identified, and the count
  is a record slip of a known class; the rule I ask for in L-1 is the same fix.
- Its Section 13 low is my L-4.
- Adopted and verified, as L-7 (low) [S2 qualification]: the grace rule treats "an all-ways tag write" as an invalidation-sweep write
  (gen_tb_pkg.sv note_tag_write), but the RTL also writes all ways after every tag ECC error (rtl/ibex_icache.sv:591 `ecc_correction_ways_d =
  {IC_NUM_WAYS{|tag_err_ic1}} | ...`, the correction write of :593-600), and the red run's sva_icram_inval_write cover counts 692 = 256 (the reset
  sweep) + 436 (one per pulse). Every caught injection therefore un-qualifies the following GEN_ICACHE_ECC_GRACE_CYCLES of injections although the
  RTL checks those lookups (only the write cycle itself is masked: :250, :264); the frequent run judged 870 injections and qualified 682, and the
  188 unqualified are mostly this. The owed-pulse half is silent for 16 cycles after each pulse. Held at Low: the first half runs throughout, the
  qualified set is judged (0 missing), and MUT-ICE-MISS shows the rule can fire; required with the next source landing: tell a correction write
  (all ways at the lookup's index within two cycles of a pulse, or ecc_write_req's signature) from a sweep, and state the qualification's terms in
  the misc monitor doc and the yaml desc.
- Adopted and verified, as L-8 (low) [S5 comments]: the declaration of g_minstret_view in gen_isa_shim.cc carries two comments, the second ("this
  step's and the previous step's minstret / minstreth write") having ridden over from the g_minstret_written line (the class CM123-L-4 just fixed
  in the header); and the new unit-test rows (gen_ut_isa_shim.cc:603, :617, :641) and four directed programs' headers key their comments by review
  ids ("CM123-L-3:", "tb_l11 L-5:", "(CM132-L-4)") while the same landing removed review ids from gen_fcov_pkg.sv under CR-8 L-8. Keep the intent
  text, drop the ids, or record that unit rows and programs may name their row.
- Adopted, as L-9 (low) [S4 statement]: gen_component_api_scoreboard.md states "a store's corruption keeps the announced word" as the model's
  rule; rtl/ibex_load_store_unit.sv:258 gives the raw access address for a misaligned store's first-half corruption too (store responses are
  integrity-checked), so the model's mtval will differ from the DUT's crash_dump on that case, which no retained program reaches. Say it is an
  unmodelled case with a crash_dump red expected, not a rule.
- Not in the artifact: L-2 (MUT-WIN's compiled form), L-3 (the hand-copied shas), L-5 (the window's upper edge), L-6 (the unstamped proof
  checks and the unidentified red builds), I-1..I-3.
- Verdict levels agree in substance: no medium open; both verdicts approve the landing with the records to fix.
