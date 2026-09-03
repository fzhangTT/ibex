# Critic verdict: tb-infra landing 2b, delta re-review v2 (d752fb3 with the docs-only delta e534438, diff base 2a414f6)

Artifacts reviewed (committed blobs; sha256 first 16 hex):

- dv/auto_dv/docs/gen_component_api_scoreboard.md at e534438  bd2ca4a7e6447c64
- dv/auto_dv/evidence/gen_critic_response_fu2a.md at e534438  bc53cc1ae8a1e72f
- dv/auto_dv/env/gen_rvfi_pkg.sv at e534438  7927a36ea2e6e470 (unchanged since d752fb3)
- the landing under re-review: d752fb3, judged in dv/auto_dv/docs/gen_critic_tb_l2b.md (6dc57b57174842d5, REQUEST-CHANGES on M-3)

Date: 2026-09-03 (UTC). Role: Critic (reviewer other than the author). Basis: docs/dv/dv_principles.md d9c27db18f511411
and gen_critic_tb_l2b.md Sections 2 and 5. Reconciled cross-model artifact: dv/auto_dv/reviews/2026-09-03-claude-diff-2a414f64-e5344388.md.
This file is the re-review of landing 2b after its first docs delta; the first verdict file is not edited (committed review
artifacts are immutable). The section below is the text written when the Orchestrator held the M-3 closure for tb-infra's
second docs delta; the closure will be its own file when that delta is named. L-16 and L-17 below are relayed as
CR-2Bv2-L-16 / CR-2Bv2-L-17 (tb-infra's CM60 rows).

## 7. Delta re-review: tb-infra's docs-only correction e534438 (diff base 2a414f6), 2026-09-03 UTC

Artifacts: dv/auto_dv/docs/gen_component_api_scoreboard.md at e534438 bd2ca4a7e6447c64; dv/auto_dv/evidence/gen_critic_response_fu2a.md at
e534438 bc53cc1ae8a1e72f. Method: committed blobs; the delta touches those two files only (git show --stat); gen_rvfi_pkg.sv is unchanged
between d752fb3 and e534438 (blob 7927a36ea2e6e470 both). EXPOSURE: a `git log` subject line for the review-record commit
cb173d9 told me the cross-model artifact for this delta is APPROVE-WITH-CHANGES before I wrote this section; the artifact
itself was not read before it; the reconciliation follows the section.

CRITIC VERDICT (landing 2b with the delta e534438): HELD -- the REQUEST-CHANGES of Section 2 stands until tb-infra's second
docs delta is named and judged together with this one (Orchestrator instruction after the delta's cross-model review). The
M-3 sentences themselves are corrected (below); the lift will be recorded in Section 8 when the second delta closes L-16,
L-17 and lift condition 3. The analysis and the decision reasoning below are kept as written before the hold instruction.

- M-3 closed: the conventions row (doc:132) now states the acceptance "on the DUT's flag alone" and that "the gate on an
  announced corruption for that load and on the DUT's rd fields reporting no write is OWED to landing 2c (T-183, LOG-051
  carve-out): until it lands, integrity-corruption runs are consistency-only"; the run-class sentence (doc:86) now says
  "NMI-enabled runs are full lock-step compares (LOG-051); integrity-error runs stay consistency-only until the
  suppressed-write gate lands (T-183, landing 2c)". Both agree with the code and with the response file.
- The response file carries the CR-2B rows: M-1 "protocol stable" on the TB side with T-226 naming the three roles (agrees
  with my conditions); M-2 OWED to 2c with one named mutant per group and the icram route stated; M-3 FIXED; L-1..L-15 OWED
  to 2c "row by row with landing 2c". Acceptable; the row-by-row answers are due with 2c.
- L-16 (low, new) [S4 wording] doc:86-87 kept the old sentence's tail: it now reads "... integrity-error runs stay
  consistency-only until the suppressed-write gate lands (T-183, landing 2c), no longer consistency-only. An interrupt entry
  ...". The dangling "no longer consistency-only" contradicts the clause before it; delete it (the correct statement is
  the first clause).
- L-17 (low, new; adopted from the delta's cross-model artifact and verified, correcting my first reading of this delta)
  [S2] doc:146 now derives GEN_BUS_ERR_DRAIN_CYCLES = 64 as "2 x 32: the two in-order transactions of a split access each
  waiting the longest rvalid window". The announcement is stamped in the driver's GRANT branch
  (`gen_bus_err_log::note(p.addr, bvif.cycle_count)` before `p.rvalid_delay` is drawn, gen_agents_pkg.sv:304-306, :327-329
  at e534438), each response is due rvalid_delay (max 32, yaml:170) after its own grant, and the second half of a split
  access first waits its own grant window (max 32, yaml:169); the worst case from the first stamp to the trap record is
  about 1 + 32 + 32 plus the record lag, above 64. Consequence: a false `bus_err_leftover` red when a split fault is in
  flight in the last ~65 cycles of a run, never a silent green. Derive the window from the grant stamp (gnt max + rvalid
  max + record lag, with the margin) or from the regime windows in gen_knobs, and bring the `ann_t` comment "with the cycle
  of the response" (gen_tb_pkg.sv:525) in line with the grant stamp. My first draft of this section called the derivation
  correct; that sentence is withdrawn here.
- Hold statements unchanged: T-183 owed; LOG-037c integrity runs consistency-only; the LOG-051 lifts unaffected.

### Reconciliation of the delta with its cross-model artifact (dv/auto_dv/reviews/2026-09-03-claude-diff-2a414f64-e5344388.md, read after the section above was written)

APPROVE-WITH-CHANGES, three lows. Its first low is my L-16 (the dangling clause at doc:86-87), same fix. Its second low is
L-17 above, adopted after verification in the driver and the yaml; it corrected my own reading. Its third low observes that my
lift conditions 3 and 4 (Section 5: the mutation record stating the five proven and four owed SVA groups with the owed mutants
named; L-1 and L-2 closing with M-3) are deferred to 2c by the CR-2B rows, and leaves the lift decision to me. Decision: the
REQUEST-CHANGES stood on M-3, the undisclosed medium; with M-3 corrected and M-2 now disclosed in the response file with a
route per group, the disclosure requirement is met and the verdict lifts; condition 3 stays required with 2c as the owed
mutants themselves (gen_mut_step2b.md must carry the proven / owed statement and the four named mutants, not only the
response file), and the L-1 / L-2 record edits are owed with 2c. Its verifications (the code at gen_rvfi_pkg.sv:464-470,
LOG-051's carve-out text, the CR-2B and CM43 rows matching the two verdicts) agree with mine.
