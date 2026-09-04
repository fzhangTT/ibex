# Critic verdict: tb-infra landing 9 (commit 329902f, diff base 2aff837), reviewed as tb_l10

Scope (the Orchestrator's): the CM117 rows (the landing-2c cross-model review) and CM119 rows (the landing-7 review), and the B8 probe
assertion behind chk_sva_b8 (LOG-067). Base verdicts touched: gen_critic_tb_l7.md (2f78b6f17d8feb57) L-1, L-6, L-11 and the five
adopted lows of its Section 7; gen_critic_tb_l8.md (4c71724506d59387) M-1, M-2, M-3, L-1.

Artifacts reviewed (committed blobs at 329902f; sha256 first 16 hex):

- dv/auto_dv/tb/gen_b8_probe.sv  42f73be2199b6aac
- dv/auto_dv/tb/gen_binds.sv  82a4daca7ec78e93
- dv/auto_dv/tb/gen_protocol_props.sv  2a6eef75bbbd523a
- dv/auto_dv/env/gen_rvfi_pkg.sv  1d9e2f8d9e5927dd
- dv/auto_dv/tb/gen_tb_pkg.sv  3c44ee959c7439da
- dv/auto_dv/env/gen_agents_pkg.sv  00ca60b6935c0ea9
- dv/auto_dv/env/gen_checkers_pkg.sv  e70986e307e45f3f
- dv/auto_dv/env/gen_fcov_pkg.sv  885cf17679e50d67
- dv/auto_dv/tb/gen_tb_knobs.yaml  d4071e676e39aada
- dv/auto_dv/gen_tb/gen_knobs.py  caa8c389be64fd11
- dv/auto_dv/tb/gen_env_cfg_knobs.svh  e7c57e8b75ee189c
- dv/auto_dv/evidence/gen_tdd_step2b.md  96ad9c45d6f04074
- dv/auto_dv/evidence/gen_tdd_fcov.md  df3ca21574e93086
- dv/auto_dv/mutations/gen_mut_step2b.md  88a5f09e65482109
- dv/auto_dv/mutations/gen_mut_fcov.md  1da6dd0aeca06f11
- dv/auto_dv/evidence/gen_critic_response_fu2a.md  d76f5354ea736655
- dv/auto_dv/evidence/gen_critic_response_fcov.md  698f7dafd0adb25c
- dv/auto_dv/docs/gen_component_api_binds.md  2c2fbe8951633717
- dv/auto_dv/docs/gen_component_api_fcov.md  44bd555bc9e13c60
- dv/auto_dv/docs/gen_component_api_irq_checker.md  95c78a1284e975dc
- dv/auto_dv/docs/gen_component_api_scoreboard.md  62198f7aa291ef1f
- dv/auto_dv/evidence/gen_tdd_logs/gen_manifest.md  99394071be28902a
- dv/auto_dv/evidence/gen_tdd_logs/lockstep/gen_fu_l10_sources_sha256_aa.txt  4bc32b82a3b03340
- dv/auto_dv/evidence/gen_b8_rtl_facts.md  34c2d940162d39a8
- the 53 gen_fu_l10_* files under dv/auto_dv/evidence/gen_tdd_logs/{lockstep,mutations}/ (manifest rows recomputed 53/53) and the six edited retained copies

Date: 2026-09-04 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411, LOG-067,
rtl/ibex_if_stage.sv:173, :485-528, :587; rtl/ibex_compressed_decoder.sv:194-222; rtl/ibex_load_store_unit.sv:722; dv/auto_dv/evidence/gen_b8_rtl_facts.md
section 6; IEEE 1800 sampled-value semantics for concurrent assertions (a register q <= d sampled at the same edge equals $past(d, 1)).
Method: detached git worktree of 329902f. Build aa identity first-hand: the recipe of gen_tb_local.sh on the tree gives 4bc32b82a3b03340 under the
UTF-8 sort, equal to the 14 build-aa run headers, the compile log and the sha256 of the retained 70-line per-file list, byte-identical to my
recompute; every listed sha equals the committed blob (audit). Library and flow self-tests PASS, gen_knobs_codegen --check up to date;
gen_fcov_codegen --check reports gen_fcov_groups.svh STALE and the codegen unit test fails its two --check cases at this commit, the tree condition
the Orchestrator named (plan v3g / v3h moved the plan after tb-infra's v3f re-render; the re-render rides Slice A): not a landing-9 defect, but
Section 13's sentence "codegen --check up to date" is false of this commit (L-3). One unnamed subagent (an evidence audit of the 53 files and the six
edited copies, told the fence, kept out of dv/auto_dv/reviews/), its disagreements re-checked by me in the blobs. EXPOSURE: none beyond the
Orchestrator's sha-and-scope message and the git log subjects naming review levels; the CM117 / CM119 rows quote the two artifacts' findings, which I
had read for tb_l7 / tb_l8's reconciliations. The landing-9 cross-model artifact was not read before Sections 1-5; Section 6 reconciles.

CRITIC VERDICT: REQUEST-CHANGES. The rows are built as described with one exception: the alert_minor window, rewritten as a range, now covers
cycles 2..3 after the lookup where the comment, the yaml and the intent say 1..2, and nothing can show it because no run raises alert_minor_o.
Two mediums (the second adopted from the cross-model artifact after verification, Section 6) and six lows; the tb_l8 mediums M-1, M-2, M-3 are closed.

## 1. What was verified

| row | as built | anchor / evidence |
|---|---|---|
| CM117-M-1 spanning-load gate | gen_rvfi_pkg.sv:483-484: `spans` from gen_insn_mem_access and the address low bits plus size beyond the word; `announced = take(mem_addr) || (spans && take(mem_addr + 4))` | rtl/ibex_load_store_unit.sv:722 (the second beat at the next word); unexercised (L-4) |
| CM117-L-1 loads only | gen_tb_pkg.sv:545-548 `note_intg(addr, we)` pushes when !we; gen_agents_pkg.sv:321 passes p.we; the NMI queue untouched | intg_s7_allchk on aa: 83 suppressed loads accepted, 0 errors, every checker on |
| CM117-L-7 / L-8 never-taken rules | `never taken=%0d` in the GEN_IRQ_CHK summary; `&& !nmi_mode` on the per-entry bound (:133) and the end-of-run rule (:261) | greens: irq_storm (573 entries, never taken=0), irq_storm_nmi (175 entries, nmi=1, never taken=0), intg_s7_allchk |
| CM117-L-6 dcsr message | dcsr_q[GEN_DCSR_PRV_BIT_HIGH:GEN_DCSR_PRV_BIT_LOW] in the dbg_dret message | code |
| CM117-L-9 window | ICACHE_ECC_WINDOW default 2; lookup_hist shift register; `alert_minor_o |-> |lookup_hist[ICACHE_ECC_WINDOW:1]` | off by one (M-1) |
| CM117-L-2..L-5 records | MUT-NT2's build 4e4a02897de732d3 = the retained seed-3 header; per-mutant provenance; the rows file header says EXCERPT 199 of 574; CM43-L-3 names gen_checkers_pkg.sv | the corrections carry new errors (L-3) |
| CM119-M-1 exclusion | gen_fcov_pkg.sv: `ut_mv_miss_expected += n_mv_miss - miss0` | green ut_isa_cov_zc on aa: 27 cases 0 failures, `move pairs: 5 sampled, 1 with mismatching micro-ops (1 of them the self-test's)`; FM11 (landing 7) proves the referee line |
| CM119-M-2 / tb_l8 M-2 unit-test red | FM4UT: the FM4 text (the one-bit slt cast) under gen_ut_isa_cov: `slti rs1 == imm is eq: slt_case(..., 32'd5, 5) 6 expected 0`, 27 cases 1 failure, build b3d31097833751a4 = its compile log, original sha 885cf17679e50d67 = the committed gen_fcov_pkg.sv | the unit test has a red; its fcov-off run also fails (L-2 on the wording) |
| CM119-M-2 / tb_l8 M-3 referee set | 14 `sampled without coverage` lines (2aff837: 6): mul, div, alu_reg, zba_zbb, alu_imm, shift, bit_count, zca (+zca32), zcmp, zcmp_mv, csr, branch, sbit, zcb | FM10 proves the form; no new red needed |
| CM119-L-1..L-4 records | 1059 notes; the five l8 excerpt headers say 27; the zc run's 5 sampled and the other four's 3 named; FM10's failed compile narrated; the popret red on x stated | the FM10 quote unretained and the mv_res run still missing (L-3) |
| B8 probe (LOG-067) | gen_b8_probe.sv: `(pipe_we_i && dummy_i) |-> fsm_stable_i`, bound into ibex_if_stage on if_id_pipe_reg_we, gen_dummy_instr.insert_dummy_instr and the decoder's cm_state / cm_rlist / cm_sp_offset d == q; inputs only, no drive; knob default 0, silenced by chk_all=0 | rtl-arch's section-6 signature verbatim; the names exist (rtl/ibex_if_stage.sv:173, :489, :504-506; rtl/ibex_compressed_decoder.sv:194-196); reds: 35 firings on gen_zcmp_dummy_directed.S, 59 on the popret program, 0 with the knob off; the silence on non-Zcmp dummy runs stated as vacuous |

Build aa is the committed tree (70 of 70 list lines equal the 329902f blobs; 12 differ from 2aff837, exactly the files this landing edits). The six
edited retained copies changed in their `#` header line only, run output untouched, manifest rows refreshed and recomputed equal.

## 2. Closure of the base verdicts

- gen_critic_tb_l8.md: M-1 CLOSED (the exclusion advances by the vector case's own miss); M-2 CLOSED (FM4UT is the unit test's red, on an
  identified build, original sha equal to the committed blob); M-3 CLOSED (every counted group refereed). L-1 closed except the second build-x FAIL
  (L-3 below); L-2, L-3, L-4, L-5 not in this landing's scope, open.
- gen_critic_tb_l7.md: L-1's first two clauses built (loads only; both words), its third (state the Zcmp `!is_seq` bypass in the scoreboard doc)
  not done; L-6's MUT-NT2 sha and 574-rows items corrected (with new errors, L-3); L-11 reworded, still imprecise (L-3); the five adopted lows
  of its Section 7 built (the file name, the dcsr message, never taken, !nmi_mode, the window: M-1). L-2, L-3, L-5, L-7, L-8, L-9, L-10 not in
  scope, open.

## 3. Findings

### M-1 (medium) [S6 a check that claims a window it does not implement; vacuous] sva_alert_minor_window now covers cycles 2..3, not 1..2

gen_protocol_props.sv:158 registers `lookup_hist <= (lookup_hist << 1) | icram_lookup_read`; :275 asserts `alert_minor_o |-> |lookup_hist[ICACHE_ECC_WINDOW:1]`.
A concurrent assertion samples lookup_hist before the edge, where its bit 0 is the register loaded at the previous edge, i.e. $past(icram_lookup_read, 1);
bit 1 is $past(.., 2), bit 2 is $past(.., 3). The old form `$past(x, 1) || $past(x, 2)` covered the cycle after the lookup and the one after that; the
new `|lookup_hist[2:1]` covers two and three cycles after it. The comment on :275 ("1..ICACHE_ECC_WINDOW = 2 cycles from the lookup"), the yaml desc
(1..2) and the CM117-L-9 row describe the old window. No retained run raises alert_minor_o (no icache ECC injection exists, CM43-M-1), so the
assertion is vacuous in every green and the shift is invisible; once an injection lands, a one-cycle alert would fail it. Required:
`|lookup_hist[ICACHE_ECC_WINDOW-1:0]` (with the register sized ICACHE_ECC_WINDOW-1:0), the comment kept, and a self-checking form: a directed
one-cycle and two-cycle pulse pair in a small unit bench, or the assertion re-expressed with $past over a generate so the window is spelled
by the same number the comment uses.

### L-1 (low) [S4 record] The B8 reds are described with doubled counts and an unequal control

gen_tdd_step2b.md Section 13 says 70 and 118 firings; the excerpt headers count `sva_b8_dummy_in_expansion: 35` and `59` (each firing prints one
VCS line and one UVM_ERROR line, and the doc itself says the run goes "red twice"). "Beside their comparator rows (27 and 9408)" holds for the
dummy run (62 - 35 = 27) and not for the popret run (13251 - 59 = 13192): the knob-on runs use +gen_ut_boot_retire=1000 and no export file where
the knob-off controls use 10 and an export, so the pairs are not one run with one knob toggled, and "no other run changes" is not shown. Re-run
the controls with the knob-on plusargs (or the reverse), and state the counts as the headers print them.

### L-2 (low) [S4 record] "FAILS identically" is false for the FM4UT fcov-off run

The catch fails 1 of 27 cases; the +gen_fcov_en=0 run fails 11 (the clz rows, cm.push minstret_once, the cm.mva01s and cm.mvsa01 shadow rows, the
wrong-second-micro-op pair): ten vector rows read shadows that the sampling path fills, so the unit test needs the covergroups on. The record
should say that (it is a useful fact about the test) rather than "identically"; the run is rightly retained.

### L-3 (low) [S4 record] Corrections that carry new errors, and claims without a retained line

The MUT-NT2 row's "88c4cfa250b44e1e was the tb7 form" names MUT-NT's build (batch tb); the tb7 MUT-NT2 build is b74b099eeff78e04, and "the mask
from order 2488" is not in any retained line (the tb7 log says order 2956). The provenance sentence "21:29-21:53Z ... all before w" excludes
MUT-SUP (21:57Z), MUT-SUPB (21:58Z), MUT-NIB (22:06Z) and MUT-NT2 (22:10Z), the last two after build w's driver start (21:58:46Z); a copy time is
retained nowhere, so "beside build u" is an inference, not a record. The FM10 narrative quotes "Too few arguments", a string in no retained log (the
first compile's log was not kept). Section 13's "codegen --check up to date" is false at this commit (STALE after plan v3g / v3h) and has no log:
name the plan sha it held at, or retain the check output. gen_tdd_fcov.md Section 6 names the popret FAIL on build x and still not the second
FAIL of gen_fu_l8_x_driver.log (lockstep_zcmp_mv_res, 32 errors).

### L-4 (low) [S6 unexercised] The widened gate has no run and no mutant

No retained program corrupts the second half of a spanning load, so the `+ 4` lookup has never taken a path in a run; no mutant targets it or the
loads-only filter; the record says "stated rather than staged", which is honest. Two details for the fix's own touch: `||` short-circuits, so when
both halves of a spanning load were corrupted the second announcement stays in the list (a stale entry of tb_l7 L-1's kind); and the Zcmp
`!is_seq` bypass is still unstated in the scoreboard doc. Required with the next integrity program: a spanning-load corruption case (the driver
announces per word), its red on the old lookup, and both words consumed.

### L-5 (low) [record hygiene] Retained copies edited in place

Five gen_fu_l8_ut_isa_cov_* excerpts and the gen_fu_l7 rows file had their `#` header line rewritten and their manifest rows refreshed. The
edits are confined to the descriptive line and the run output is untouched (verified), which is the only acceptable form; a rewritten header
should carry the correction's date and reason so a later reader can tell it from the original copy. The mutation canary still hashes
gen_rvfi_pkg.sv for a gen_fcov_pkg.sv mutant (tb_l8 L-5, open).

### Informational

- I-1: the per-entry bound's age is not paused in NMI mode: an expectation older than the bound is judged on the first record after mret with
  !nmi_mode true; the entry clearing runs before the bound loop, so a line taken on that record clears first. Restarting the bound at NMI exit
  would remove the one-record slack.
- I-2: the B8 probe is the honest form of LOG-067: it fails on the DUT's own defect, is off by default with the reason, drives nothing, and its
  silence on non-Zcmp dummy runs is stated as vacuous. The DUT finding stays B8's.
- I-3: items of tb_l7 and tb_l8 outside this landing's scope stay open: tb_l7 L-2 (the tautological width assert), L-3 (the yaml's "landing 2b
  measured 1 or 2"), L-5, L-7, L-8, L-9, L-10; tb_l8 L-2, L-3, L-4, L-5.

## 4. Principles check

dv-principles-check (docs/dv/dv_principles.md d9c27db18f511411): S6 trust triad: the unit test now has a red (conforming); the widened gate has
none (L-4); one assertion re-expressed to a window it does not describe and unexercised (M-1). S4 honesty: the B8 silence stated as vacuous
(conforming); doubled counts, an unequal control and a false "identically" (L-1, L-2); corrections carrying new errors (L-3). One-line verdict:
FAIL on M-1 until fixed.

## 5. Required for re-review

1. M-1: the window indexed 0..ICACHE_ECC_WINDOW-1 (or the $past range form) with a unit-bench pulse pair or an equivalent self-check.
2. L-1..L-5 with the same touch.

CRITIC VERDICT: REQUEST-CHANGES (M-1; M-2 of Section 6). tb_l8 M-1 / M-2 / M-3 are closed; the B8 probe stands on its substance, with L-6's paperwork owed.

## 6. Reconciliation with the cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-2aff8377-329902fc.md, read after Sections 1-5 were written)

REQUEST-CHANGES: one high, two mediums, four lows.

- Its high is my M-1 (the same sampled-value argument, the same slice [N:1] = latencies 2..N+1). Level disagreement, stated: it rates the shift
  High; I hold Medium because no run can reach the assertion today (alert_minor_o never rises without an icache ECC injection), so nothing is
  hidden yet; the fix is required either way.
- Adopted and verified, as M-2 (medium) [S2 a rule made silent by forgetting]: gen_checkers_pkg.sv:126-141: the per-entry bound loop judges an
  expired expectation only under `!nmi_mode` (:133) and then deletes it unconditionally (:140 `expects.delete(i)`), so an expectation whose bound
  expires while the DUT is in NMI mode is dropped without judgement; a line raised before or during the NMI handler, still held after mret and
  never taken is then invisible to the bound rule and to the end-of-run rule alike. The CM117-L-8 row asked for silence in NMI mode, not for the
  expectation to be forgotten. Required: in NMI mode neither age nor delete the expectation (or restart its bound at NMI exit, I-1), a red with a
  line held through an NMI handler and withheld afterwards, and the storms re-run. This supersedes my I-1.
- Adopted and verified, as L-6 (low) [S4 the ruling's letter]: LOG-067 names the knob chk_sva_probe and asks that the exception be "recorded in the
  SVA layer header as the C10 exception with this log id"; the built knob is chk_sva_b8 with no recorded reason for the rename, the
  gen_protocol_props.sv header (:1-8) still describes the internal properties as unbound with no mention of the exception, and
  gen_component_api_binds.md:99's own gate ("Add probe binds only with a probe-register row marked approved") has no B8 / T-225 row in
  gen_probe_register.md (its table ends at P-MD). The substance of the ruling is met (a separate bind, off by default, drives nothing, the
  exception recorded in gen_binds.sv and the binds API doc, the reds retained); the paperwork is owed: the register row, the header line, the
  knob name reconciled with the log or the log amended. The flow's refusal of a measured entry that sets the knob is Runtime's, per the ruling.
- Its lows are my L-1 (the doubled counts and the unequal control), L-2 ("FAILS identically"), L-4's short-circuit clause; and one more adopted:
  gen_b8_rtl_facts.md:167 still says the section-6 assertion "is not built" (verified) after this landing built it (rtl-arch's file, one line).
- Not in the artifact: L-3 (the corrections carrying new errors, the unretained "Too few arguments", the false "codegen --check up to date", the
  mv_res run), L-5 (the edited retained copies), I-3.
- Verdict levels agree (REQUEST-CHANGES both); the work asked for is the same two fixes plus the records.
