# Test Writer plan (T-058)

Owner: test-writer. Version 2, 2026-09-03 09:00 UTC: promoted from
`dv/auto_dv/work/test-writer/gen_test_writer_plan.md` after the DV Lead's acceptance with three
changes (Section 2 manifest rule, Section 1 expected-fail and informational rows, acceptance item 6).
Build configuration `opentitan`. Governing texts: `DV_prompt.txt` Sections 5, 6, 8, 10;
`docs/dv/dv_principles.md` Section 6 (trust triad); `dv/auto_dv/docs/gen_tb_architecture.md`
(Sections 3, 4.2, C9, 8.3a); `dv/auto_dv/docs/gen_test_plan.md` Sections 0, 0a, 3;
`dv/auto_dv/docs/gen_fcov_plan.md` Sections 0, 1.1 and 3.8 (REG); `dv/auto_dv/docs/gen_bug_log.md`
(B1..B18); `dv/auto_dv/docs/gen_runtime_api.md` Sections 4, 7c, 7e.

Gate in force: no Phase 1 feature-targeted test is written against a test-plan item until the
plan set passes its cross-model re-review (round 2 REQUEST-CHANGES; plan v2b changes item text,
not groups; the Orchestrator signals round 3 APPROVE). Everything below that does not depend on
item text (template, library, boots-and-retires test, batch mechanics, mutation procedure) is done
or in progress now.

## 1. Test-plan groups to test files and names

Rule (one test per group, `gen_test_plan.md` Section 0 "Test groups"):

| Plan object | Test Writer artifact |
|---|---|
| group `gen_<area>_<topic>` (Section 3 table, 216 groups) | test name `gen_test_<area>_<topic>`; file `dv/auto_dv/tests/gen_test_<area>_<topic>.py`; cocotb module `dv.auto_dv.tests.gen_test_<area>_<topic>`; one `@cocotb.test()` of the same name |
| `_xfail` group | its own test, testlist `expected_fail: true`, never shares a file with a pass item (Section 0). The test sets `xfail_bug = "<Bn>"` and asserts the SPEC outcome through the compare `gen_test_plan.md` Section 0a names for that bug: B1, B2, B3, B15 through the C5.3b checker rows (their `uvm_error` is the collected failure); B4, B5, B7, B10, B11, B13, B16, B17 through the named test-level compare in `fire_check()`. It logs the RTL outcome as `GEN_TEST_RTL_OUTCOME <Bn> ...` (`GenTest.info`), and its failing line reads `GEN_TEST_XFAIL <Bn> ...` so the flow's XFAIL is attributable. Bug ids run B1..B18 (`gen_bug_log.md` v1d); B6 and B12 carry no expected-fail item |
| `_info` group (B9 and B14 items, and the other `Expected: informational` items) | its own test, `measured: false`, tier `check`, `expected_fail: false`; asserts only that the scenario fired and logs the observation as `GEN_TEST_INFO <TP id> ...`; contributes no manifest bin |
| directed program of a test | `dv/auto_dv/tests/gen_programs/gen_<area>_<topic>[_<n>].S` (Test Writer tree; `gen_program.py --directed` accepts any clone-relative path); Zc encodings through `dv/auto_dv/stim/gen_zc_insn.h`; end of test = tohost store 1 pass / 3 fail (riscv-dv convention); every directed program defines the word `gen_min_retired` |
| riscv-dv program of a test | a `gen_<name>` entry in `dv/auto_dv/stim/gen_riscv_dv_target/gen_testlist.yaml` (TB Infra's file: entries requested through the Orchestrator) or the existing `gen_rand_smoke`; `program.seed: run` |
| items of a group | one fire-check per item inside the group's test, named `fire_<tp_id_lower>` (for example `fire_tp_isa_001`), called from `fire_check()`; each asserts a per-seed observable through `GenTest.check`, and every item's result is collected before the finish handshake |
| bins of a test | `dv/auto_dv/fcov_expectations/gen_test_<area>_<topic>.fcov.yaml`, rendered by the generator (Section 2) from the items the test's fire_tp_* methods name (built items only; blocked items contribute no bin) after the manifest rule |
| docstring of a test | names the group, the TP items, the canonical feature IDs those items cover (ALIAS and FOLDED IDs resolved through `gen_feature_list.md` Section 3), the program, the knobs it pins (normally none) and the checkers it relies on, so the Critic's traceability sampling can start from the test file |
| testlist entry | written by me to `dv/auto_dv/work/test-writer/gen_testlist_entries.yaml`, copied into `dv/auto_dv/flow/gen_testlist.yaml` by Runtime (one owner per file); a test's red run is its own entry (a request cannot swap a program) with `red_fixture: true`, `measured: false`, tier `check`: the flow reports its designed FAIL as RED-OK and an unexpected PASS as FAIL (gen_runtime_api.md Sections 2 and 7) |

Tier, phase and `feature_groups`: the item's Tier becomes the test's `tier` (lowest tier over its
items); `feature_groups` carries the area (`isa`, `mul`, ...), the group name and `mutation` for
mutation-evidence tests. Phase 2 groups (`gen_<area>_random`, `gen_<area>_regime`, `gen_xif_*`,
`gen_reg_*`) are written after the Phase 1 gate (DV_prompt Section 5 step 6), except
`gen_reg_schedule` and `gen_reg_knob_sweep`, which prove the three randomization layers the
template depends on and are written first once the plan passes.

The per-area weight tables W1..W10 (`gen_test_plan.md` Section 4.1 and the other area headers) are
the layer-1 distributions: a test draws per-transaction operands with `gen_test_lib.Weighted` from
the table named by its items; the tables are transcribed once into `gen_test_lib.py` as data
(`W_TABLES`) with the plan section cited, so a table change is one edit.

## 2. Per-test manifest convention

- File `dv/auto_dv/fcov_expectations/<test>.fcov.yaml`, schema of `gen_runtime_api.md` Section 7c
  (`test`, `owner: test-writer`, `bins:` bare `gen_<feature>_cg.<cp>.<bin>` tokens, one
  `anti_vacuity` note per bin). The plan's `CG-<AREA>-<nnn>.cp_x.bin` names map to the
  implementation names through the plan header `### CG-<AREA>-<nnn>: gen_cg_<area>_<name>` and the
  architecture rule (plan `gen_cg_<x>` = implementation `gen_<x>_cg`, Section 5), confirmed against
  URG's grpinfo.txt at the first covergroup.
- Generator: `dv/auto_dv/tests/gen_fcov_manifest.py --group <group> --test <test> [--write]`
  renders the manifest from `gen_trace_tp_bin.csv`, never by hand, and applies the manifest rule of
  `gen_fcov_plan.md` Section 0 (DV Lead change 1): it excludes the bins of informational items
  (`- Expected: informational`), every bin of an item whose `- Manifest:` field says `not in
  manifest` (probe-gated items), bins of coverpoints whose plan line carries `not in manifest`
  (probe-gated coverpoints P1, P4, P7, P8, P9), bins the plan names as bug witnesses, and the
  regression-level coverpoints of `gen_fcov_plan.md` Section 1.1. A `_`-joined cross bin is accepted
  only if it segments into declared bin words of its covergroup by the `segmentable` rule of
  `dv/auto_dv/tools/gen_trace_check.py`, which the generator loads from that file's source (never a
  second implementation), so the manifest and the plan cannot drift; a bin that fails the rule stops
  the generator. The CSV already lists every auto-cross bin expanded; the generator validates, it
  expands nothing. Each bin's anti-vacuity note is the covergroup's own Sample sentence. Dropped bins
  are listed on stderr for the record. `--self-test` PASS on the DV Lead's working tree:
  gen_reg_schedule 67 bins, informational and probe-gated items yield no manifest, the trace
  checker's rule accepted and rejected on known names; the committed tree yields 86 excluded
  coverpoints (bc9dba9 and later; the self-test prints the SHA). An earlier working-tree figure of
  122 predates two changes: the auto-cross segmentation rule moved into
  `dv/auto_dv/tools/gen_trace_check.py` (one implementation, imported by the generator), and the
  exclusion set became the plan's Section 0 rule (probe-gated P1/P4/P7/P8/P9 coverpoints,
  informational items, witness bins, and the Section 1.1 regression-level coverpoints, now 74).
  Before that landing the generator exited with `GEN_FCOV_MANIFEST_INPUT_VERSION`; nothing was
  produced from it.
- The Python test declares its bins through `GenTest.declare_bins()` and logs them (`GEN_TEST_BINS n=<count>`).
  Default: the plan's bins of exactly the items the class's `fire_tp_<area>_<nnn>` methods name, produced by the
  same generator code that renders the manifest (`gen_fcov_manifest.py --test-module`), so finish()'s cross-check
  (`gen_test_lib.check_manifest_matches`) proves the committed manifest current against the plan and covering only
  built items; a stale or missing manifest fails the run. A test that must narrow or extend the set overrides
  `declare_bins()` with the reason in its docstring, and the cross-check then compares that override.
- Until the first covergroup exists (`gen_fcov_pkg` is TB Infra build step 3), testlist entries
  carry `fcov_expectation_file: null` and the manifests are rendered but not wired; the flow's
  `fcov_manifest_required_tiers` policy switches them on. A test accepted before covergroups exist is
  re-accepted (declared bins hit on 3 seeds) when its groups land.

## 3. Batch size and Runtime turnaround

Runtime's measured numbers (`dv/auto_dv/work/runtime/gen_turnaround_purpose1.md`, 08:31 UTC): one
purpose-1 request (1 test x 3 seeds, coverage off) takes about 45-70 s wall (compile 20-30 s per
request, riscv-dv program step 2.9 s, LSF pend under 2 s, sim 5-9 s), 60-100 s with coverage;
runs inside a request go 8-wide; pickup is immediate on a message naming the request path.
Orchestrator ruling (08:38 UTC): purpose 1 stays one test per request, and Runtime serves
independent purpose-1 requests concurrently (bounded by its run pool), so a subagent batch of N tests
is N request files filed together (`test-writer-<seq>.yaml` each) and returns in about one request's
time. Batch size adopted: 8 tests x 3 seeds per batch (Runtime's run-pool width), one request file
per test, one message naming all the paths; a test's red run is its own testlist entry and request.
Until TB Infra's T-068 lands, Runtime serves gen_tb requests locally on the submit host (same
verdict path), so the first batches do not depend on LSF. Request notes are YAML block scalars
(`notes: >-`), never plain scalars with a colon (test-writer-001/-002 were refused on that).

## 4. Acceptance check per test (the Test Writer applies it before the DV Lead sees the test)

1. Compiles: `python3 -m py_compile` clean; `gen_test_lib.check_ascii(<file>)` clean (TB_CONTRACT
   Section 4); no hierarchical path outside `gen_handles.py`; plusarg names only through
   `gen_knobs.plusarg()`; no re-typed count (ranges from `gen_knobs.CONSTANTS`, `MEMORY_MAP`,
   `PLUSARGS[..]['values']`, `ibex_pkg` values through the rendered constants).
2. Fire-check passes on at least 3 seeds through Runtime (purpose 1, `seeds: 3`, `coverage: no`
   until covergroups exist, then `coverage: yes`), manifest cited by path.
3. Declared bins hit on every seed (`fcov_check: PASS` in each result.yaml) once the manifest is wired.
4. Randomization visible: the run log's `GEN_TEST_KNOBS` line differs between seeds for the knobs
   the test does not pin, and the `GEN_TEST_SCHED` line shows the seed-derived schedule.
5. Expected-fail items fail for the right reason: the result is XFAIL and the first failing line
   is the test's own fire-check assert naming the bug id (`GEN_TEST_XFAIL <Bn>`), not a timeout, a
   TB fatal or an unrelated checker; the `GEN_TEST_RTL_OUTCOME <Bn>` line with the RTL outcome is
   present. Informational tests log `GEN_TEST_INFO <TP id>` and PASS on the fired scenario alone.
6. The test's docstring names its group, its TP items and the canonical feature IDs they cover
   (ALIAS/FOLDED resolved through `gen_feature_list.md` Section 3), its program, the knobs pinned
   (if any) and the checkers it relies on; the testlist entry is in `gen_testlist_entries.yaml` with
   the same names.
7. Red evidence: every new fire-check was seen failing once (a red run cited in the test's TDD
   transcript under `dv/auto_dv/evidence/gen_tdd_test_<name>.md`, or the batch transcript).

## 5. Mutation-evidence procedure per checker id

Checker ids and knobs are the rendered `gen_knobs.CHECKERS` list (44 ids today: `ibus_proto`,
`ibus_outstanding`, `sva_rvalid_legal`, `dbus_proto`, `dbus_outstanding`, `dbus_split`,
`dbus_store_intg`, `icram_write_ecc`, `icram_inval_sweep`, `icram_ecc_response`, `scrkey_proto`,
`alert_minor`, `alert_bus`, `alert_internal`, `crash_dump`, `double_fault`, `core_busy`,
`data_tag_quiet`, `fetch_en`, `irq_pending`, `irq_entry`, `irq_masked`, `nmi_entry`, `nmi_internal`,
`dbg_entry`, `dbg_exc`, `dbg_masked`, `dbg_dret`, `dbg_trigger`, `ctr_mcycle`, `ctr_minstret`,
`ctr_hpm_exact`, `ctr_hpm_bound`, `pmp_data`, `pmp_fetch`, `isa`, `isa_pc`, `isa_insn`, `isa_trap`,
`isa_rd`, `isa_mem`, `isa_prv`, `isa_pc_next`, `isa_csr`, `rvfi_proto`, `t022_never`,
`bridge_accounting`); TB self-checks (`sva_rvalid_legal`, `bridge_accounting`, `t022_never`) get no
DUT mutation record (architecture A-13). For each DUT checker id, once TB Infra reports it landed:

1. Pick one mutation from the checker's "mutation classes" column (component API document), at
   the cited RTL locus; write `dv/auto_dv/mutations/gen_mut_<id>.md` in the README format
   (id `MUT-<NNN>`, file:line, original, mutated, expected_detector = the checker id).
2. Prepare the mutated copy out of tree: `dv/auto_dv/work/test-writer/mut/<MUT-NNN>/rtl/<file>.sv`
   (clone-relative layout; the flow substitutes it and refuses leftovers). `rtl/` is never edited.
3. Choose the covering test: the smallest test whose scenario exercises the locus (a Phase 1 test
   of the checker's area; before those exist, `gen_test_boot_retire` or a directed program under
   `gen_programs/`).
4. Request purpose 2 (`component: <checker's component>`, `notes` naming the mutation id and the
   RTL root, `--rtl-root`, `--mutation-id` as operator extra args) with three runs of the covering
   test at one seed: (a) isolation `+gen_chk_all=0 +gen_chk_<id>=1` on the mutated build: must FAIL
   with `UVM_ERROR ... [<id>]` as the first failing line; (b) ablation `+gen_chk_all=0` (every
   checker off, the named one included) on the mutated build: must PASS (the mutation survives);
   (c) the unmutated build with defaults: PASS. Every run `measured: false`.
5. Record in the mutation file: the three manifest paths, the first failing line of (a) verbatim,
   the verdicts of (b) and (c), the date; the Critic audits (trust triad rule 2).
6. The ISA comparator rows share the master `+gen_chk_isa`: isolation of a field is
   `+gen_chk_all=0 +gen_chk_isa=1 +gen_chk_isa_<field>=1`; TB Infra's `_set` flags make the
   isolation form work (scoreboard API document).

Note for the Critic: "hidden referees inert" in Zone A is satisfied by (a) alone because every
other Zone A check is disabled by `+gen_chk_all=0`; the log scanner still fails a run on UVM_FATAL
(MEM_LOAD, ISA_INIT, alive watchdog), which are TB integrity events and not checkers.

## 6. TB components needed before each area's tests, mapped to TB Infra's build steps

| Build step (TB Infra) | Components | Areas / groups unblocked |
|---|---|---|
| 1 (landed 07:50Z) | bridge, memory model + MEM_PEEK, bus agents with the imem/dmem regime knobs, icache RAM models, scramble-key responder, FETCH_EN | template setup and finish; `gen_test_boot_retire`; program-only groups whose fire-check is RVFI-visible through the bridge counts |
| 2a (landed) | RVFI monitor, scoreboard with the ISA comparator (`isa_*`), `rvfi_proto` | every ISA/MUL/CMP/BIT/BTALU group (pass criteria `gen_isa_compare`) as soon as the plan passes |
| 2b (built 08:21Z, parked during T-068 under `work/tb-infra/step2b_wip/`) | irq/dbg agents and drivers (IRQ_SET/IRQ_CLR/NMI_PULSE/DBG_REQ), `irq_pending`, `irq_masked`, `dbg_entry`, `dbg_masked`, misc monitor (`alert_bus`, `alert_internal`, `double_fault`, `data_tag_quiet`), REGIME_SET for the imem/dmem/irq/debug_req/scr_key knobs, KEY_MODE, MEM_ERR_ARM | IRQ, DBG, EXC (trap entry), SEC alert-injection groups, IMEM/DMEM error groups, `gen_reg_schedule` for the TB-side knobs; the template's layers 2 and 3 (gated off until it re-lands) |
| 2c (owed) | REGIME_SET consumers for `fetch_enable_regime`, `icache_ecc_err_rate`, `mcounteren_writable` and the program-side knobs (`instr_mix`, `priv_regime`, `pmp_regime` phase markers through the riscv-dv user extension), ICACHE_ECC_ARM, `icram_*` checkers, `scrkey_proto`, `core_busy`, `fetch_en`, `crash_dump`, `irq_entry`, `nmi_entry`, `nmi_internal`, `dbg_exc`, `dbg_dret`, `dbg_trigger` | IC, RST, FE, SEC scr-key/crash-dump/sleep groups; full layer-3 coverage (`gen_reg_knob_sweep` over all 20 knobs) |
| 2d (owed) | counter model (`ctr_*`), PMP model (`pmp_data`, `pmp_fetch`, `pmp_csr_warl`), CSR observability read-back (`csr_readback`, `isa_csr`), `gen_csr_sweep_stream` user extension | PMC, PMP, CSR, PRV, TRG, DIT groups |
| 3 (owed) | `gen_fcov_pkg` covergroups, binds home with rtl-arch SVAs, `gen_regime_cg` phase log sampling | every manifest becomes live; REG/XIF bins; assertion coverage |

Items the Test Writer needs from TB Infra (queued by the Orchestrator after T-068):
1. The bridge argument encodings that Python must use (IRQ line-mask bit positions, hold-policy
   codes, DBG_REQ policy codes, MEM_ERR_ARM kind codes) rendered into `gen_knobs.py` from
   `gen_tb_knobs.yaml`; today `gen_ut_irq.py` and `gen_ut_dbg.py` re-type them, and
   `gen_test_lib.py` carries a mirror marked as such until the codegen renders them.
2. A phase-log record that Python can read at finish (count of applied phases) or a bridge field
   `evt_phase_count`, so the template's schedule fire-check (`applied == scheduled`) does not
   depend on parsing the SV log.
3. REGIME_SET consumers for the remaining knobs (2c above) and the program-side region marker.
4. Per-phase MEASURED statistics readable from Python: the REG fire-checks (TP-REG-001..014) compare
   the agents' per-phase grant/rvalid latency histograms, error and injection rates and event rates
   against the applied knob value ("measured DUT-side traffic against the echo, not echo against
   schedule"). Today nothing of the agents' bookkeeping is readable through the bridge. Proposal
   (supported by the DV Lead): a bridge statistic command that answers one statistic in `peek_data`
   (agent, phase, statistic id), so Python reads a few words at finish and never polls; alternative:
   a per-phase record file written by the SV side that the test parses after `finish_ack`. Without
   one of these the REG group cannot be written to its fire-checks and would degrade to schedule
   accounting only, which the plan forbids.
5. An RVFI record export readable by Python in measured runs (asked 09:12 UTC, highest priority):
   the monitor writes one ASCII line per `gen_rvfi_txn` (and per irq marker) to the path of a normal
   knob `+gen_rvfi_export=<file>` set by the flow to `<run dir>/gen_rvfi_records.txt`; a bridge
   command (MISC sub-op or a new kind RVFI_FLUSH) makes SV `$fflush` and ack, so a test reads the
   complete file inside `fire_check()` after the end-of-test edge and before the finish handshake.
   Reason: almost every Phase 1 fire-check reads per-record RVFI facts (opcode, operand classes,
   `rvfi_trap`, `rvfi_ext_*`), `+gen_rvfi_trace` is debug-only uvm_info, and per-cycle polling is
   forbidden (A-01). Until it lands, only tohost/count-based checks and the program report channel
   (template attribute `expected_reports`: K result words a directed program stores to the EOT MMIO
   register before tohost, collected edge by edge) are available, and batch 1 is limited to the
   directed self-checking groups listed in `dv/auto_dv/work/test-writer/batch1/README.md`.
   Status: TB Infra's T-080 design addendum (`dv/auto_dv/work/tb-infra/gen_rvfi_export_addendum.md`,
   09:29 UTC) meets the requirements; Test Writer comments (09:31 UTC): the per-record
   `ext_mhpmcounters` are needed in v1 behind `+gen_rvfi_export_counters=1` (PMC/DIT/BTALU
   fire-checks read them), the flush marker must carry the bridge retirement count sampled at the
   same instant, and the `I` lines carry `ext_debug_req`/`ext_debug_mode`. Addendum version 2 (09:33 UTC)
   adopted all three (header `counters=<0|1>` with the field list matching; markers `records=<n> retired=<r>`;
   I lines with the debug flags; header names seed and image); it now waits for the DV Lead's acceptance,
   the replan review and the T-068 landing. Version 3 (09:52 UTC, `dv/auto_dv/docs/gen_rvfi_export_addendum.md`,
   embedded in the architecture as Section 9): the knob is opt-in per testlist entry
   (`+gen_rvfi_export=gen_rvfi_records.txt` on tests that consume records), `gen_rvfi_export.read()`
   is the enforcing parser (prefix before the last complete flush marker, `records == retired`,
   order strictly +1, field count per line), all 34 `gen_rvfi_txn` fields per R line with the 20 hpm
   words under `+gen_rvfi_export_counters=1`, rendered `RVFI_EXPORT_FIELDS` /
   `RVFI_EXPORT_COUNTER_FIELDS`. When it lands, `GenTest` adds the knob for tests that declare they
   need records, issues the flush after the end-of-test edge and exposes `self.records` through
   `read()` (never its own line parser).

## 7. First real test and the template proof (this task)

`gen_test_boot_retire` (file `dv/auto_dv/tests/gen_test_boot_retire.py`): program `gen_rand_smoke`
at the run seed; layer 2 drawn by Python for the schedulable knobs and applied through REGIME_SET
before the core is released; layer 3 = the seed-derived schedule applied at cycle thresholds; fire-
check per seed: (1) the program's tohost store carries code 1, (2) the retirement count after that
store is at least the program's retirement floor (`+instr_cnt` of the riscv-dv entry, read from the
target testlist, never re-typed; a directed program's `gen_min_retired` word), (3) every scheduled
regime phase whose trigger was reached was applied (template). Red first: the same module on a
directed program that stores tohost 3 after a handful of instructions and declares an unreachable
floor (`gen_programs/gen_boot_retire_red.S`), so both halves of the fire-check fail through the
Python assert; green: the riscv-dv program on 3 seeds. Transcript with identifying lines and the
Runtime manifests: `dv/auto_dv/evidence/gen_tdd_test_template.md`.
