# Critic verdict v1: TB architecture component sections C1-C11 (T-011 part 1)

- Artifact under review: dv/auto_dv/work/tb-infra/gen_tb_arch_component_sections.md (sha256 first
  16: 17154e9838f49eea; 634 lines; sections C1-C11 plus open items), to be folded verbatim into
  dv/auto_dv/docs/gen_tb_architecture.md by the DV Lead.
- Companion inputs: dv/auto_dv/evidence/gen_t019_spike_build.md, dv/auto_dv/work/tb-infra/
  gen_spike_linktest.cc, dv/auto_dv/docs/gen_component_api_dut_top.md, the pinned upstream Spike
  source in tools/riscv-isa-sim (4ffd6ba860f4190ceac2716fa3c2cf139e85538f; upstream riscv-isa-sim,
  allowed by DV_prompt Section 3), rtl/ for the timing facts cited below, the Critic's earlier
  verdicts (gen_critic_feature_list_v1.md C-06/C-16, gen_critic_t010_dv_principles_v1.md P-04).
- Standard: DV_prompt.txt Sections 6 (stimulus), 7 (modelling and checking), 8 (mutation classes
  and disable knobs), 9 (language split and hygiene); docs/dv/dv_principles.md Sections 1-3, 5;
  docs/dv/TB_CONTRACT.md.
- Date (UTC): 2026-09-03 05:58
- Reviewer role: critic (Claude Fable 5.1). Spike API claims were checked in the pinned source;
  RTL timing claims at the cited lines. No fence event; no LSF command.

CRITIC VERDICT: REQUEST-CHANGES

Severity counts: high 0, medium 4, low 13, info 8; plus the probe rulings in Section C8 (two
accepted, one accepted for coverage only, one accepted as debug-only, three rejected). The
architecture is sound: boundary-only drive with one agent per interface, the three
randomization layers with command-line pinning, one seed, passive always-on checking, checker
tables with mutation classes and per-id disable knobs, a single constants source generated into
SV, Python and C, one binds home and one Python handles module. The four medium items are design
corrections to make before code: the bridge's per-retirement Python wake-ups (A-01), the
checker direction for the spec-violation bug candidates (A-08), the cycle-exact compares against
an RVFI-timed CSR model (A-09), and the Spike interrupt injection design given the pinned
model's mie write mask and priority chain (A-14).

---------------------------------------------------------------------------------------------------
## C2. TB top, language split and the cocotb/UVM bridge (DV_prompt S9; TB_CONTRACT)

### A-01 (medium) [S9 "Do not use high-cost VPI features ... per-cycle signal polling from Python is a last resort"]
C2 bridge table, `evt_retired[31:0]` "read (edge/value)", and C9 layer 3 "awaiting evt_retired
thresholds, not polling". A cocotb await on a 32-bit counter that changes on every retirement is
one VPI callback per retired instruction, which on a NOP-dense program is one per cycle: polling
by another name. Required change: Python writes a target (`evt_retired_target[31:0]`, and a
cycle target for cycle triggers) and awaits a single-bit `evt_thresh_hit` edge raised by SV; the
same pattern for every threshold the schedule needs. With this change no per-cycle polling exists
and no waiver is requested or granted; the document should say so explicitly (S9 requires the
reviewer's agreement for any polling).

### A-02 (low) [TB_CONTRACT Section 4 ASCII-only logging]
The C2 conventions omit the rule that every Python-side string that may be logged or raised is
pure ASCII (a non-ASCII character in a failure message crashes the cocotb log path and can turn
a failure into a silent pass). Add it to the bridge/test conventions and to gen_tests' template.

### A-03 (info) [S9 language split] Conformant
Programs and run-time stimulus decisions in Python/C; agents, monitors, scoreboard, shim and
covergroups in SV/UVM/C++; one UVM test class, tests differ by Python. The per-transaction SV
randomization under knob control needs no recompile for a new test: agreed, compliant, not a
deviation. The seed banner echoes `+ntb_random_seed` and `RANDOM_SEED` at time 0.

---------------------------------------------------------------------------------------------------
## C3. Interface agents and test-equipment models (DV_prompt S6; dv_principles S1)

### A-04 (low) [S6 "Counts and ranges derive from the design's parameters ... never from re-typed literals"; dv_principles S1 future-proof counts]
C3.1 "hard cap 8", C3.2 "hard cap 2", C3.6 "18 bits: 15 fast + ext + sw + timer". NUM_FB and
FB_THRESHOLD are localparams inside ibex_icache (rtl/ibex_icache.sv:72-73), not exported by
ibex_pkg; IC_LINE_BEATS is. Required: one constant each in gen_tb_pkg (`GEN_IBUS_MAX_OUTSTANDING =
GEN_ICACHE_NUM_FB * IC_LINE_BEATS` with the localparam value cited as the one unavoidable re-type,
`GEN_DBUS_MAX_OUTSTANDING` cited to the LSU split rule, fast-interrupt width from
`$bits(irqs_t.irq_fast)`), imported by the agents and the checkers; never a literal in a knob table.

### A-05 (low) [dv_principles S1 "Sensitizing operands ... No all-zeros ... that mask a fault"]
C3.4 `+gen_icram_init=zero|random` has no stated default. Default `random` (the reset sweep makes
tag contents irrelevant; random data on never-hit lines is harmless); `zero` only for a directed
bring-up.

### A-06 (info) [S6 boundary drive, independent agents, three layers, one seed] Conformant
Six agents/responders on the six DUT interfaces plus RVFI and misc monitors; layer 1 `dist`
weights in items, layer 2 named regimes per agent, layer 3 a seed-derived schedule echoed as
`+gen_regime_sched` and pinnable with `+gen_regime_pin`, both in the banner and covered by
`gen_regime_cg`. Error injection is boundary-only (bus responses, RAM read data, key valid).

### A-07 (low) [dv_principles S1 "if a backdoor is unavoidable, verify it took (write -> clock -> read back -> error on mismatch)"]
C3.3 image load is the single backdoor and is verified by checksum plus "a sampled VPI read-back
of N words from cocotb". State N (or the rule that derives it), that the read-back compares
against the `.sym.json` sidecar, and the failing mechanism on mismatch (Python assert or
`uvm_fatal MEM_LOAD`), so the verification is a check and not a log line.

---------------------------------------------------------------------------------------------------
## C4. Monitors and checkers (DV_prompt S7, S8; dv_principles S2, S4)

### A-08 (medium) [dv_principles S4 "if the RTL is less complete than the documented intent ... write the test to the intended behavior, mark it as a known expected-fail"; DV_prompt S10]
C5.3 legalization table and the C4 checker rules follow the RTL on every row; the specification
violations the team has logged as bug candidates are not separated: B1 dret into U leaves
mstatus.MPRV (Sdext.adoc:202), B2/BUG-01 MPRV honoured in debug mode with mprven = 0, BUG-03
dcsr.ebreaks writable without S-mode (the Critic's gen_critic_feature_list_v1.md C-21), B3
tdata3/mcontext/scontext read 0 instead of trapping (Sdtrig.adoc:370), B5 dcsr.nmip hardwired 0.
As written, `dbg_dret` (C4.5) and `pmp_data` (C4.3) and the shim would adopt the RTL behaviour
and the bugs would never fire. Required: split C5.3 into (a) RTL-defined rows where the model
follows the RTL (checker-direction policy Q-DL-5, each row citing its source) and (b) spec-
violation rows where the model and checkers follow the specification, the affected tests carry
`expected_fail: true` in the testlist, and the row names the bug id; apply the same split to the
C4.3/C4.5 rules. Note that the pinned Spike already implements the spec for BUG-03 (riscv/csrs.cc:
1625: ebreaks is forced 0 unless S is enabled; :1600 xdebugver 4), so the comparator will flag
Ibex's writable bit without any legalization: do not legalize it away.

### A-09 (medium) [dv_principles S2 "Place the check where the failure lands"; S4 evidence over inference]
C4.4 `irq_pending`: "`irq_pending_o == |(pins & mie_q)` every cycle, `mie_q` from the CSR model
(updates the cycle after the write retires)". The RTL updates mie_q at the CSR-write commit edge
(rtl/ibex_cs_registers.sv:790, :1103-1106) while the RVFI record of the csrw appears after WB
(two-stage RVFI pipeline, rtl/ibex_core.sv:1655); a cycle-exact compare against a model that
updates on the RVFI record false-fails around every mie/mstatus write. The same holds for
`ctr_mcycle` "exact": `rvfi_ext_mcycle` is sampled when the instruction left ID (rtl/ibex_core.sv:
2102), not at retirement, so the model needs the pipeline offset. Required: define, per cycle-
exact checker, the compare window or the offset (a constant in gen_tb_pkg, measured at bring-up
and pinned by a directed test), or derive the commit cycle from boundary events; state the
exactness class (exact / windowed / bound) in every C4 row, as C4.6 already does for the HPM
counters.

### A-10 (low) [dv_principles S4 evidence over inference]
C4.2 `core_busy`: "Off only after a retired WFI with no pending wake and no outstanding bus
beats". ctrl_busy_o is 0 in WAIT_SLEEP unconditionally (rtl/ibex_controller.sv:598-604), so
core_busy_o dips for exactly one cycle after every retired WFI even when a wake condition (step,
debug mode, pending interrupt) is already true; only the SLEEP cycles depend on the wake terms
(:606-621). Fix the rule (one-cycle Off always; Off beyond that only with no pending wake) and
align the feature list (gen_critic_feature_list_v1.md C-06 on F-DBG-044/059).

### A-11 (low) [DV_prompt S8 "For every checker ... show at least one named mutation"]
The ISA comparator (C5.2, `uvm_error ISA_<field>`, knob `+gen_chk_isa`) is the central checker but
has no row naming the mutation classes it catches. Add rows ISA_pc, ISA_rd, ISA_mem, ISA_trap,
ISA_csr, ISA_priv with example loci (ALU operator select rtl/ibex_alu.sv, decoder rd/we,
LSU address/data rotation, controller exception cause, cs_registers legalization) and per-field
knobs, so the Test Writer can produce the isolated evidence per field.

### A-12 (info) [S8, S2, S5] Conformant
Every C3/C4 checker names its mutation classes with an RTL locus and a `+gen_chk_<id>` knob; the
master `+gen_chk_all=0 +gen_chk_<id>=1` gives the isolated evidence run; failures are `uvm_error`
with id, cycle and expected-versus-actual (S5 concise diagnostics); protocol-fatal states use
`uvm_fatal`. Checks sit at the DUT boundary or on RVFI; no checker reads a DUT internal.

### A-13 (low) [S8 accounting]
`ibus_order` is a TB self-check (mutation class n/a). Say in the fold-in that TB self-checks are
listed for completeness and are not counted as DUT checkers in the trust-triad evidence table,
so the evidence count is not inflated.

---------------------------------------------------------------------------------------------------
## C5. ISA-model integration (DV_prompt S7; feasibility against the pinned Spike)

### A-14 (medium) [S7 "compare architectural results ... against the DUT's retirement trace"; feasibility]
C5.1 `gen_isa_arm_async` "inject mip bits via backdoor_write_with_mask" and C5.3 "mie fast bits
16..30: model mask may drop them (UNVERIFIED)". Verified in the pinned source: `mie_csr_t::
write_mask()` (riscv/csrs.cc:993-1001) is MSIP | MTIP | MEIP plus S/H/LCOF/COP bits only when
those extensions exist; bits 16..30 are never writable through a CSR write, so the model never
enables Ibex's fast interrupts by itself, and `take_interrupt` (riscv/processor.cc:316 onward)
selects by Spike's own chain (M-external > M-software > M-timer), not Ibex's (fast, lowest id
first > external > software > timer). Required design: (1) the shim shadows mie and sets the fast
bits with `mip_or_mie_csr_t::write_with_mask` (csrs.cc:946-949, a public method that bypasses
`write_mask`), so no Spike patch is needed (closes Q-DL-10 for this item); (2) the shim injects
exactly the ONE interrupt the DUT took (from the record's `pre_mip` and the Ibex priority rule
implemented in the shim, or from the handler's `csrr mcause` read-back), never the raw pending
set, and compares the entry: Spike's vectored mtvec gives `base + 4*cause` (processor.cc:513-514),
identical to Ibex for causes 3, 7, 11 and 16..30; NMI (31) and the internal NMI stay emulated as
C5.3 says. Record the mask fact in C5.3 and drop the UNVERIFIED mark.

### A-15 (low) [S4 evidence over inference; C5.4 (b) UNVERIFIED byte order]
With `addr_to_mem` returning NULL for every address (C5.1), each model access reaches the shim's
`mmio_load` / `mmio_store` / `mmio_fetch` as ONE call carrying the full access length:
`store_slow_path` (riscv/mmu.cc:355-400) performs an intra-page misaligned store whole and splits
only at a page boundary; `mmio_fetch` (riscv/simif.h:21, used by mmu.cc:99) likewise. The byte
order of a partially faulting misaligned store is therefore decided by the shim's `mmio_store`,
not by Spike. Rewrite C5.4: the shim implements Ibex's per-word rule itself (perform the
permitted word, fault the denied one, report `mtval` per BS MEM-10/13); this removes the
UNVERIFIED mark and the mirroring step of case (a) becomes unnecessary when `mmio_store`
performs the permitted half directly.

### A-16 (info) [feasibility verified against tools/riscv-isa-sim at 4ffd6ba8]
Verified: `simif_t::mmio_fetch` exists and defaults to `mmio_load` (riscv/simif.h:21; the fetch
path uses it, mmu.cc:99); `halt_request` with `HR_REGULAR` (riscv/processor.h:352-354);
`state.in_wfi` with public `clear_waiting_for_interrupt()` (processor.h:97, :364-365; wfi.h: legal
in U-mode without S unless TW, matching Ibex); `state.csrmap` is public (processor.h:90), so
cpuctrlsts/secureseed can be custom `csr_t` objects at 0x7C0/0x7C1 (name this mechanism in
C5.3 instead of "extension_t or intercept"); debug entry sets pc to DEBUG_ROM_ENTRY 0x800 and
exceptions in debug mode to DEBUG_ROM_TVEC 0x808 (processor.cc:391, :423-425), so the override to
DmHaltAddr/DmExceptionAddr is needed exactly as C5.3 states; `zicclsm` enables misaligned handling
(riscv/mmu.h:374-376); `dcsr` xdebugver 4 and ebreaks forced 0 without S (csrs.cc:1600, :1625).
The T-019 link test (14/14) proves construction without `sim_t`, stepping, commit log, get/put_csr,
mip backdoor, n_pmp = 16 and a fetch fault through simif. Not yet demonstrated and required as a
second link test before shim coding: halt_request entry and dret, in_wfi wake, a custom CSR in
csrmap, one cm.push step with `log_mem_write`, and a misaligned `mmio_store` fault.

### A-17 (low) [C5.3 `time(h)` row]
"model returns illegal-instruction for those addresses": Spike implements `time` as a real CSR
(readable in M-mode); it does not trap by default. State the mechanism (replace the csrmap entry
for 0xC01/0xC81 with a trapping csr object) or the compare exception; UNVERIFIED as written.

### A-18 (low) [S3 fence note; S6 trust triad]
C5.5 reference functions "written from the public Bitmanip draft text (upstream riscv/
riscv-bitmanip)": allowed subject to Q-003 (pending); if denied, the Q-DL-2 fallback
("RTL-defined reference" from rtl/ibex_alu.sv comments) applies and must be recorded as such.
The reference functions are new checkers: TDD and mutation evidence apply to them too.

---------------------------------------------------------------------------------------------------
## C6. CSR observability plan (DV_prompt S7; dv_principles S2)

### A-19 (info) Plan accepted
Model of record derived from intent (reset values, every retired CSR write from `rvfi_insn` and
operands, trap entry/exit from `rvfi_trap`/`rvfi_intr`/handler pc), the handler read block
(csrr of mcause/mepc/mtval/mstatus before any write; dcsr/dpc in the debug ROM), the periodic
and end-of-test CSR sweeps, the fire-check read after each write in feature tests, and the
behavioural observation through the PMP and interrupt checkers together make every CSR
observable without a probe. Conditions: (a) the sweep frequency knob and "write followed by
read within N records" bins appear in the coverage plan so the observability gap is measured;
(b) the read blocks are csrr only (stated); (c) mip is taken from `rvfi_ext_pre/post_mip`.

### A-20 (low) [dv_principles S2 "A model mirrored from the RTL only proves the RTL matches itself"]
C6 item 4 "the shim compares the model's post-write CSR against its own legalization": a model
compared with its own legalization is a self-consistency check of the shim and observes nothing
about the DUT until a read-back. Reword: the DUT-facing check is the read-back (item 3 and the
per-feature fire-check); item 4 validates the shim only.

---------------------------------------------------------------------------------------------------
## C7. Covergroup implementation strategy (dv_principles S4, S6)

### A-21 (low) [S5 single source of truth]
"Code coverage: `-cm_hier` with the two `+tree` entries (C1)" conflicts with the Runtime flow's
`+tree <tb_top>.u_dut` (dv/auto_dv/flow/gen_cm_hier.cfg; the Critic's gen_critic_t010_dv_principles
_v1.md P-04). One recorded DV Lead decision; C7 cites it and does not restate a scope.

### A-22 (info) Conformant
Sampling on monitor events only, named `gen_smp_<name>` conditions for the anti-vacuity review,
covergroups in their own `gen_fcov_pkg` namespace never added into another group, bins from
ibex_pkg parameters, `gen_regime_cg` for layer 3, per-test fcov expectation manifests checked
pre-merge (trust triad rule 3).

---------------------------------------------------------------------------------------------------
## C8. Probe register rulings (DV_prompt S7: "Probing internal design state is allowed only where the starting state is genuinely unknowable from intent"; the Critic's approval duty)

| Id | Ruling | Conditions / rationale |
|---|---|---|
| RVFI | ACCEPTED as a boundary interface, not a probe | The rvfi_* ports are ibex_core module ports that exist under `+define+RVFI`; record them in the probe register as "define-gated DUT interface" so the register lists everything the TB reads inside gen_dut_top. |
| P1 `dummy_instr_id/wb`, `rf_raddr_a/b`, `rf_waddr_wb`, `rf_we_wb` (wrapper seam) | ACCEPTED for coverage and for the BUG-02/B7 quantification only | (i) Observation-only bind in gen_binds.sv on the wrapper-internal seam nets, which are ibex_core PORTS (no reference below ibex_core); (ii) the only pass/fail use is the dummy-count reproducer for the minstret bug candidate, reported as such; the trusted `ctr_minstret` rule with dummies on stays `>=`; (iii) rationale recorded: insertion cycles come from the RTL LFSR (rtl/ibex_dummy_instr.sv:60-75) and security.rst:44-47 says only "random intervals", so intent cannot supply them; the S7 exception is met; (iv) the bind's failure on a renamed net identifies itself (dv_principles S2). |
| P2 icache hit/miss internals | REJECTED for now | Hit/miss is derivable at the boundary: a lookup is a tag read of both ways on `ic_tag_req_o`, a miss is followed by an `instr_req_o` fill of that line, a hit is not; the RAM model and the ibus agent see both. Re-apply only with URG evidence that the derived bins stay unreachable after a closure round. |
| P3 fill-buffer occupancy | REJECTED | Occupancy equals granted-unanswered fetches, which the ibus agent counts exactly (the same quantity `ibus_outstanding` checks); "buffer full" is `outstanding == GEN_IBUS_MAX_OUTSTANDING`. |
| P4 `ctrl_fsm_cs` and the RTL `fcov_*` nets | CONDITIONALLY ACCEPTED for coverage sampling only | The cycle in which the controller enters a state is pipeline timing no specification defines, and FSM code coverage cannot express a cross with stimulus timing (interrupt, debug request or fetch error arriving in a named state), so the S7 exception applies for coverage. Conditions: never a checker input; each cross names the feature it serves; the bind resolves through gen_binds.sv; the `fcov_*` nets exist only when DV_FCOV_DISABLE is undefined (state the build dependence); re-review when the cross list exists. |
| P5 icache `valid_o`/`ready_i`/`rdata_o` seam | REJECTED for checking; NOT approved for coverage now | The stability rule is the RTL's own assertion (assertion coverage counts it); F-FE-012 bins use the boundary derivation first; re-apply with URG evidence. |
| P6 `cs_registers_i` CSR flops, `csr_wdata_int` | ACCEPTED as a debug-only aid | Default off; knob name declared once; never enabled in a measured regression (the flow must fail a measured run that has it on); its message names itself as a model-versus-RTL debug compare, not a DUT failure; not counted as a checker in the trust-triad evidence. |

Per-cycle Python polling: none is requested; after A-01 none exists; no waiver is granted. Every
accepted item gets a probe-register row before use, as C8 already says.

---------------------------------------------------------------------------------------------------
## C9-C11. Environment, binds home, constants home (DV_prompt S9; dv_principles S5)

### A-23 (low) [dv_principles S5 "a mistyped gate silently no-ops"; S2 fail through a collected mechanism]
C9: an unknown plusarg on the command line is reported by `uvm_warning GEN_UNKNOWN_PLUSARG`. A
warning is collected by nothing (the flow's verdict counts UVM_ERROR/UVM_FATAL). Make an unknown
`+gen_*` plusarg a `uvm_error` (or `uvm_fatal` at time 0), so a mistyped regime pin or checker
knob fails the run instead of silently running the default.

### A-24 (info) Conformant, with one note for Runtime
gen_binds.sv is the only binds home; no bind forces or drives a DUT net; SVA protocol assertions
are knob-guarded through `gen_sva_ctl` so the isolated evidence run can silence them; mutation
runs compile a mutated RTL copy in a scratch out-dir (DV never modifies rtl/). Runtime's
gen_build.py needs an RTL-root override (or a filelist override) to compile from that copy;
relay. gen_tb_knobs.yaml -> codegen -> SV package, Python module and C header with `--check` is
the single source S5 asks for; gen_handles.py is the one hierarchical-path home on the Python side.

### A-25 (info) Site dependency to state in the fold-in
Every test is cocotb-master, and cocotb runs on LSF are blocked until the clone is on shared
storage (intervention log Q-012; gen_t010_compile_path.md Section 1). The architecture document
must state the dependency and the interim mode (`--local` runs on the submit host) so the Phase 1
schedule does not assume LSF fan-out for cocotb tests.

---------------------------------------------------------------------------------------------------
## Summary for TB Infra (changes before the fold-in)
Replace the counter-await pattern of the bridge with SV-side thresholds and a single-bit event
(A-01). Split the legalization table and the debug/PMP checker rules into RTL-defined rows and
spec-violation rows with expected-fail tests (A-08). Give every cycle-exact checker a defined
window or offset and an exactness class (A-09). Redesign interrupt injection around the verified
Spike facts: shadow mie through `write_with_mask`, inject the single cause the DUT took (A-14).
Apply the low items: parameter-derived caps (A-04), random RAM init default (A-05), read-back
verification details (A-07), the WAIT_SLEEP dip (A-10), ISA comparator mutation rows (A-11),
self-check accounting (A-13), the mmio_store byte-order rewrite (A-15), the `time` CSR mechanism
(A-17), the Q-003 dependence (A-18), the item-4 wording (A-20), the coverage-scope cross-reference
(A-21), unknown-plusarg severity (A-23), and the ASCII rule (A-02). Record the C8 rulings in the
probe register as given. REQUEST-CHANGES stands until the four medium items are addressed; part 2
of T-011 reviews the DV Lead's top half and the fold-in fidelity of these sections.
