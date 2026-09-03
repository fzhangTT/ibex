# Critic verdict: TB architecture document v1a, fidelity re-check and closure of v1 lows (T-011 part 2, v2)

Artifact: dv/auto_dv/docs/gen_tb_architecture.md v1a, sha256 31f11d3fc8617523, 1278 lines, committed (HEAD da2a482),
header status "adopted by DV Lead 2026-09-03 08:04 UTC (v1a)".
Response file (committed): dv/auto_dv/evidence/gen_critic_response_tb_architecture_v1.md, sha256 1d4b497e99f022a1;
nothing disputed; answers my L-1..L-8 and the cross-model delta review's findings in one table.
Comparison base: dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md version 3, sha256 b9a3cc16eccec313, 856
lines, mtime 07:19:52Z, unchanged since my T-011 part 2 v1 verdict cited it.
Date: 2026-09-03 (UTC). Role: Critic. Supersedes dv/auto_dv/docs/gen_critic_tb_architecture_v1.md (APPROVE with L-1..L-8).

CRITIC VERDICT: APPROVE

## 1. Fold-in fidelity (Section 6 against TB Infra's version 3)

Method as in v1: the v3 file was hashed (b9a3cc16eccec313, equal to the hash the document's header and Section 6
preamble claim) and the embedded text (document lines 268-1136) was diffed against it with heading depth flattened and
blank lines removed.

| Difference | Lines | Judgement |
|---|---|---|
| Section 6.0 preamble (source, hash, heading shift, retirement of 6.13, known C9 leftovers, response citations) | 10 added | expected |
| Any change inside the embedded body | 0 | faithful |

The former 6.13 (fact-check table) is gone because v3 folds the eight T-051 corrections into the body with "(v3,
T-051-n)" marks; my component v2 conditions F-01..F-05 are therefore in the text a component author reads.

## 2. Closure of the v1 lows

| v1 | Status | Evidence in v1a |
|---|---|---|
| L-1 phantom ports in Section 1.1 | CLOSED | no scramble_key_i / scramble_nonce_i / ram_cfg_i in Sections 1-2; the only remaining mention is v3 C1's list of ibex_top-only ports |
| L-2 "WAIT_SLEEP one-cycle dip" in 2.1 | CLOSED | phrase absent; port-level rule |
| L-3 version lag, 6.13 binding clause | CLOSED | v3 embedded verbatim (Section 1); 6.13 retired |
| L-4 knob names in 4.2 | CLOSED | Section 4.2 uses `+gen_knob_<name>` and `+gen_regime_sched` only |
| L-5 header status, gitignored citations, log cites | CLOSED | header names the component v2 APPROVE and the embedded hash; citations are dv/auto_dv/evidence/gen_critic_response_tb_arch.md, gen_critic_response_feature_list_v1.md, gen_critic_tb_arch_components_v2.md; Section 5 cites Q-014 and R-002 (lines 214, 237); Section 7 rows for both |
| L-6 informational wrapper tree | CLOSED | Section 5 states the committed mechanism: `cov_trees` two disjoint roots, `info_trees: [u_dut]`, gate row as the per-metric sum over the gated URG rows, the n/a rule, and the re-baselined round-0 numbers under both rulings (dv/auto_dv/evidence/gen_round_0_rebaseline/) |
| L-7 Section 7 omissions | CLOSED | Section 7 lists Q-001, Q-002 (revised), Q-003..Q-014, R-002, F-001 |
| L-8 GEN_ICACHE_ECC_WINDOW wording | CLOSED | 8.2: "1 counted from the lookup request", alert alone 0 from the corrupted-rdata cycle; agrees with v3 C4.8 |

The cross-model delta review's items are answered in the same table of the response file; my Section 8 comparison in
v1 stands, and the one severity difference (scope mechanism) is moot now that Section 5 describes the implemented
mechanism and cites the commits.

## 3. Notes (no action for the DV Lead)

I-1 The DV Lead discloses (Section 6 preamble, 8.3 item 4) that v3 C9 still names the retired forms `+gen_<agent>_regime`,
`+gen_regime_pin` and `+gen_regime_seed` once each; Section 4.2 is authoritative. TB Infra removes them in the next v3
revision; re-adoption then repeats the hash-and-diff.

I-2 Section 7 and 8.1 say the glitch filter is applied through `extra_vcs_args` on "both" testlist build entries, never a
flow constant. At review time gen_testlist.yaml has three build entries (gen_smoke, gen_smoke_cocotb and the new gen_tb)
and every one carries `extra_vcs_args: ["-cm_glitch", "0"]`; "both" predates the gen_tb build and can become "every" at
the next edit. My T-040 condition F-4 (the flag present in every measured compile command and stated in every report
header) is checked at the first measured regression, not here.

I-3 8.1 item 6 records the `SIMULATION` ruling (stays undefined; Runtime confirmed the effective define set) and the TB
banner prints the define either way (gen_env_pkg.sv banner), which is the right pairing of ruling and evidence.

## 4. Method and fence record

Hash-and-diff of the embedded text against the v3 file; greps of the v1a text for each closed item; the response file
read in full. No RTL re-read was needed. No LSF command; no fence event.
