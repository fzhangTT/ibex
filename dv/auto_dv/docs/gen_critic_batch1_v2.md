# Critic verdict: Phase 1 batch 1, second review (commit 2d72b4a, Test Writer remediation T-114)

Artifacts at commit 2d72b4a: the eight tests dv/auto_dv/tests/gen_test_{rst_boot,csr_reset,csr_access,csr_trap_setup,
cmp_zcb,cmp_zcmp_basic,bit_draft,pmp_csr_warl}.py with gen_programs/gen_<group>_prog.py, gen_programs/gen_prog_const.py
(93 lines), the eight manifests dv/auto_dv/fcov_expectations/gen_test_<group>.fcov.yaml (9 / 81 / 80 / 172 / 110 / 473 /
15 / 266 bins, 0 witness bins), gen_test_template.py and gen_test_lib.py (declare_bins default = plan bins of the items
the class's fire_tp_* methods name), gen_fcov_manifest.py (--test-module, rule (f)), dv/auto_dv/evidence/gen_tdd_batch1.md
Sections 6-8, dv/auto_dv/evidence/gen_critic_response_batch1.md (rows CR-H-1, CR-M-1..4, CR-L-1..4, CM-Major, CM-Minor,
per-test table), retained logs dv/auto_dv/evidence/gen_tdd_logs/test_writer/ (261 manifest rows).
Date: 2026-09-03T12:23Z   Role: Critic   Previous: gen_critic_batch1_v1.md (cb3d7eb, REQUEST-CHANGES). The parallel cross-model
artifact was not read. Every number below is from my own runs or scripts on the committed text.

CRITIC VERDICT: REQUEST-CHANGES on one medium (the declaration derivation has no guard against silent shrinkage; a
few lines in the template, the structure check and the generator). Everything else asked in v1 is closed and verified;
nothing in the eight tests' content blocks batch 2 from being written against the same template once that guard is in.

## 1. Cross-cutting

### Closed (verified)

- H-1: declare_bins() is the template default (plan bins of the items named by the class's fire_tp_<area>_<nnn>
  methods, lib.fire_items -> gm.plan_bins) and the generator's --test-module renders the same set by AST; the eight
  manifests equal the declarations (the lib self-test proves it for every committed test, PASS from a clean archive of
  the commit). rem_* greens on seeds 1 and 2 for all eight, manifests present, GEN_TEST_PASS in every log.
- M-1: manifests cover the built items only (bit_draft 15 bins for its one built item, rst_boot 9 for three).
- M-2: rule (f) implemented in gen_fcov_manifest.py (CYCLE_CLAUSE_TOKEN / WITNESS_CG, self-tested on TP-CSR-029);
  csr_trap_setup regenerated without witness bins; 0 gen_wit_ lines in all eight manifests.
- M-3: --red --red-item <TP> per generator; 59 retained red logs; every one of the 52 fire_tp_<area>_<nnn> items of
  the eight tests appears failing in at least one retained red (script over the logs: 52 of 52, none missing).
- M-4: the rd = x0 reads are gone (0 "zero_rd" in gen_csr_access_prog.py) and the clause is written as "BLOCKED on
  T-102 (the clause is not exercised at all; no read with a discarded result stands in for it)" (:40); the LRWX refusal is
  gone (0 hits) and LRWX = 1111 under MML is programmed with the spec expectation. Blocked clauses are labelled in the
  docstrings of csr_access, csr_reset, rst_boot, cmp_zcb (channel named), bit_draft (owner TB Infra, T-102 item 4).
- L-1 layers_required entries; L-2 gen_prog_const.py as the single home (CSR numbers, MSTATUS_RESET, MISA_VALUE,
  MCONFIGPTR_VALUE, TOHOST codes and CONFIG_NAME re-exported from their homes); L-3 history removed; L-4 noted.
- Retention: 261 manifest rows, every committed copy matches md5 and byte count AND every work-tree source matches
  the same md5 (261 of 261); no unmanifested file; all gen_-prefixed. The disclosed overwrite of the first csr_access
  remediation runs (gen_tdd_batch1.md:397) is recorded and the re-run set (rem_csr_access_v2_*) is retained.

### M-1 (medium) [S6 self-proving; S4 don't hide down-scoping]: the derivation is consistent but unguarded

- The declaration and the manifest now derive from the same fact, the set of fire_tp_* methods on the class (template
  :288-293; generator fire_items_of_module). They agree by construction, so the manifest check can no longer notice
  when that set shrinks: a fire method renamed outside the fire_tp_<area>_<nnn> form, deleted, or moved behind a guard
  silently removes its item from the declaration AND from the rendered manifest, and no run fails. The only guard in the
  generator is "the named items exist in the plan" (gm.plan_bins), which catches a typo, not a loss.
- The built set is a subset of the plan group for five tests (rst_boot 8 of 11 items not built, csr_access TP-CSR-005,
  csr_trap_setup TP-CSR-026/031, cmp_zcmp_basic TP-CMP-068, bit_draft 13 of 14), and the only record of what is not
  built is prose in the docstrings.
- Required: each test declares the group items it does not build as data, e.g. a class attribute
  `not_built = {"TP-RST-001": "<reason or blocker id>", ...}`; check_test_source (host) and gm.plan_bins (both the
  declaration and --test-module) assert fire_items | not_built == the plan group's item set and fire_items & not_built ==
  {}; the trace report lists not_built per test. Then the only way to shrink a declaration is an explicit, reviewable
  line with a reason, and a fire method that disappears fails the structure check.

### Lows

- L-1 The per-item reds of cmp_zcmp_basic each also trip fire_tp_cmp_039 (the base push check) and red_039 trips 042
  and 043; bit_draft red2 trips two checks. Fine for TDD (each check is seen failing), but the response's "each tripping
  its own item" should read "its own item, and for zcmp the base check as well".
- L-2 The committed flow testlist's red entries are still the per-test form (generator_args [--red], red_expect
  "[0-9]+ fire-check failure"); the per-item form with the fire id is in the Test Writer's staged entries, so the
  cross-model Major waits for Runtime's copy. Not the Test Writer's file. The one comparator-style red_expect belongs to
  gen_ut_lockstep_forced_red, where the comparator line is the designed failure.
- L-3 The commit adds whole-group manifests for seven batch-2 groups that have no test yet (bit_ratified, cmp_zca,
  isa_alu, isa_cti, isa_shift, mul_div, mul_mul). Each will fail its test's manifest check the moment a test declaring a
  subset lands; they must be re-rendered with --test-module then. State it in the plan or do not pre-render.
- L-4 Rule (f) in the generator keys on the plan's marker token while gen_fcov_plan.md and WP-5 name the CSV's marked
  column; the tool asserts the two agree today, but the generator should read the CSV (one fact, one source).

## 2. Per test (v1 Section 3 items; (V) = re-read by me at 2d72b4a)

- 3.1 gen_test_rst_boot: PMPNumRegions from ibex_configs.yaml and the pmpcfg()/pmpaddr() helpers (V); KEY_REGIMES from
  lib.knob_values (V); dropped TP-RST-006 clauses listed as blocked (V, docstring); 3 items built, reds 003/006/007 retained.
- 3.2 gen_test_csr_reset: key regime from the layer-2 draw through _knob_regimes (V); "never + 2" gone (V); W_EARLY lead
  items with the retirement position asserted (V); 6 items, reds 037/105-109 retained.
- 3.3 gen_test_csr_access: red keeps the drawn op and flips one writable bit (red_flip, V); W-without-R patterns drawn
  (V); every op class asserted (V); M-4 as above; TP-CSR-005 stays not built (comparator C-1 row, now fixed by T-102:
  can be built next); reds 001/002/003/004/012 retained (v2 set after the overwrite).
- 3.4 gen_test_csr_trap_setup: low base class via a handler copy in .debug_rom and the boot class via the boot-page
  write, asserted per seed (V: debug_rom, base classes); W-PAT-derived weights for the 027 pattern (V, :100-111);
  9 items, reds 023-036 retained; TP-CSR-026/031 not built (irq agent).
- 3.5 gen_test_cmp_zcb: fire_program_verdict added (V); RVFI clauses named as blocked on the record export (V);
  reds 034/036/038.
- 3.6 gen_test_cmp_zcmp_basic: 48 combos x 3 asserted (V); b2b pop with a longer partner rlist (B2B_PUSH_COMBOS,
  longer_same_adj, V); CSR literal replaced (V); 17 items, 17 reds; TP-CMP-068 not built (no writable low words).
- 3.7 gen_test_bit_draft: directed floor of 128 (base, control) pairs with fire_tp_bit_016_controls / _single_bit /
  _rs2_upper asserted (V); vacuous operands counted apart (D, response); 13 blocked items with owner TB Infra (V), now
  unblocked by T-102's references: the Test Writer can build TP-BIT-022..033 in the next landing.
- 3.8 gen_test_pmp_csr_warl: LRWX programmed (V); rules cited to machine.adoc / smepmp.adoc / cs_registers.rst with the
  RTL as cross-check (12 spec citations, 1 RTL mention, V); bases from the symbol sidecar (V); 8 items, reds red1..red8.

## 3. Evidence audit

Retained under gen_tdd_logs/test_writer/ with a manifest: greens s1/s2 for all eight (rem_*), 59 red logs (rem_*_red*),
the declbins greens and the manifest-missing / manifest-stale reds, the v2 csr_access set after the overwrite, the
seed-25 pmp run. Every red log fails through GEN_TEST_FAIL with a named fire id; every item of every test is covered.
The four comparator-blocked tests carry comparator errors in these logs (pre-T-102 build) and their entries are refiled
after T-102, as the response says.

## 4. What closes this verdict

The M-1 guard (not_built declarations, the two-sided assertion in the structure check and the generator, the report
line) in the next Test Writer landing, with the lib self-test extended by one refused source (a fire method removed
without a not_built entry). I re-check that mechanism only; the eight tests need no other change.
