# TDD transcript: the ibus grant repair, the ruled gated shape

Component: `dv/auto_dv/tb/gen_bus_if.sv` (the grant becomes the driver's readiness ANDed with a live
request) and `dv/auto_dv/env/gen_agents_pkg.sv` (the driver drives the readiness, and enqueues only for a
grant the accepting edge actually made). Owner: tb-infra. Written 2026-09-08T04:23:14Z.

Authority for the shape and for the no-loop precondition: rtl-arch's
`dv/auto_dv/evidence/gen_ibus_props_irq_signature_reading.md` Sections 12.1 to 12.5, cited by number and
not restated. Section 12.5 is the one that fixes the acceptance: for the GATED shape the firing count goes
to ZERO by construction, where the decision-only shape would keep one per run.

Retained logs, all under `dv/auto_dv/evidence/gen_tdd_logs/fcov/`, with rows in the area manifest:
`gen_fu_l67_gnt_census.log` (the four flow runs and the three local controls),
`gen_fu_l67_gnt_waveform.log` (the same window on both drivers, with the FSDB paths),
`gen_fu_l67_verify.log` (the handed tree assembled from the handed list alone, built and run on an archive
of the base), and the run logs and sim logs named in their manifest rows.

TWO BUILDS CARRY THE AFTER COLUMN and both are named wherever a figure is given. The measurement build is
`3dd4530832d978cd`; then three comment blocks were trimmed, which moves a build digest without touching
behaviour, so the handed sources build as `e2492acab5c48ecc` and both seeds were re-run there. Every figure
in this record holds on both, to the digit, including the waveform's times and values.

## 1. The defect, located in the driver rather than only in the property

The committed driver reads `vif.req` at the FALLING edge, decides there, writes `vif.gnt = 1'b1` at that
same falling edge, then waits the rising edge and captures the address. Between those two edges the core
can withdraw its request, because `instr_req_o` is combinational out of the icache, and nothing re-checks
it. So the grant stands at the accepting edge with the request low, which is
`sva_ibus_gnt_only_with_req: instr_gnt_i |-> instr_req_o`, and the driver enqueues a transaction the core
never booked.

THE INTERFACE ALREADY DISAGREED WITH THE DRIVER, which is the shortest statement of the bug.
`gen_bus_if.sv` counts a grant as outstanding only when both are high at the edge,
`outstanding <= outstanding + ((req && gnt) ? 1 : 0) - ...`, so the phantom grant increments nothing, the
driver answers it anyway, and the interface's own `sva_rvalid_legal` catches the response with
`outstanding == 0`. The repair makes the driver agree with the accounting its own interface has always
used.

## 2. The shape, and the three things verified rather than trusted

The interface gains a driver-owned `gnt_ready` and one continuous assignment, `gnt = gnt_ready & req`, so
the grant cannot stand at an edge whose request is not live. The driver drives `gnt_ready` from its own
state at the falling edge, waits the rising edge, and enqueues only if `vif.gnt` was high there; a refused
decision counts in a new `withdrawn` counter, keeps its arming, and queues nothing.

What "keeps its arming" means in the driver's own terms: `gnt_armed` stays set and `gnt_wait` stays at
zero, so if the request is still up at the next falling edge the driver re-decides there immediately with
no new delay drawn, and if the request has really gone the existing `else` arm clears the arming. The
retried grant therefore reports a `gnt_delay` one cycle longer than the delay that was drawn for it, which
is the truth about when the grant happened and not a figure to correct. Nothing is exported on the refused
path either, because the grant export event sits after the check.

rtl-arch's Section 12 says in as many words that a reader re-greps rather than trusting its line numbers,
so:

- The four combinational uses of `instr_gnt_i` in `rtl/ibex_icache.sv` are still exactly `:704`, `:705`,
  `:762` and `:765`, and the file has not been touched since the cleanroom export commit, so the citation
  cannot have drifted. What each one terminates in is Section 12.3's finding and stays theirs; Section 12.4
  carries the conclusion outside the icache and to the no-icache build. I re-checked the citation, not the
  conclusion.
- The only writers of the interface's `gnt` were the driver; `gen_tb_top.sv` only reads it, so one
  continuous driver is legal.
- `gen_smoke_tb_top.sv:306` has driven `assign instr_gnt = instr_req` since the first landing, which is
  the gated shape already compiling and running in this design, independent of the argument above.

## 3. ONE CLAUSE OF THE RULED SHAPE IS NOT BUILT, and here is the measurement that refused it

The handover's ruled shape has three clauses, and this landing builds two: the decision is taken at the
falling edge on driver state, and the grant is asserted as readiness AND a live request at the accepting
edge. The third, "the capture must read the SAME registered sample the decision used", IS NOT BUILT. I built
it first, exactly as written, and it fails. What follows is that measurement; the decision about the clause
itself belongs to whoever ruled it, not to me.

The first form added a registered sample of the address in the interface and captured from it. That is a
full cycle STALE: the interface's non-blocking assignment updates in the NBA region of the accepting edge,
while the driver's read right after `@(posedge)` happens in the Active region, so it takes the PREVIOUS
edge's address. Every fetch then carried the wrong address and seed 165313640 collected 564297 errors,
129038 of them `isa_pc`.

That is exactly the defect the reverted two-process restructure had, which the handover records as "its
registered-sample decision was a full cycle stale". So the clause asks for the shape the handover's own
history rejected, in a sentence written before the gate existed to make it unnecessary. The correct reading
for the GATED shape is that the gate and the capture use ONE EDGE: the enqueue happens only where the gate
passed, and the address is read at that same edge from the net, which is what the committed driver's own
comment already defended. The registered sample is removed and the interface change is now the gate alone.

## 4. The two grant-event seeds, before and after

`gen_test_irq_basic` through `gen_run.py`, each seed into a fresh run directory so the program is generated
by the run, and the same program image on both drivers per seed. The before build is the driver HEAD
CARRIES: its runs record git=5a64b1e, an ancestor of HEAD 8869874, and both repair files hash the same at
both commits (`gen_bus_if.sv` efc37cb28fd2, `gen_agents_pkg.sv` c271ef7cce08, sha256 first-12).

| | before 165313640 | after 165313640 | before 1207954461 | after 1207954461 |
|---|---|---|---|---|
| sva_ibus_gnt_only_with_req | 1, at 18338500 | 0 | 1, at 9250500 | 0 |
| unbooked response (sva_rvalid_legal, sva_ibus_rvalid_outstanding) | 1 and 1 | 0 | 1 and 1 | 0 |
| comparator and checker errors (isa_*, crash_dump, irq_entry) | 327 | 0 | 102796 | 0 |
| sva_rvfi_irq_valid_exclusive | 2 | 2 | 3 | 5 |
| write to an unmapped address | 1 | 0 | 1 | 0 |
| all UVM_ERROR lines | 333 | 2 | 102803 | 5 |
| cocotb test | FAIL | PASS | FAIL | PASS |
| end of test | 20 of 20 by EOT | 20 of 20 by EOT | NEVER REACHED, runaway | 21 of 21 by EOT |
| cycles / retired | 19164 / 1775 | 19367 / 1804 | 1627542 / 23849 | 47131 / 1658 |
| flow verdict | FAIL | FAIL | FAIL | FAIL |

Both before firings land at the tick rtl-arch's pair record recorded for these seeds, Section 3's 18338500
and 9250500, so the defect reproduces on this base exactly and not merely in kind.

## 5. What the second seed's hundred thousand errors actually are

A runaway. The phantom grant derails the program: the committed run on 1207954461 never reaches its
end-of-test store, runs 35 times longer than the repaired run, retires 23849 instructions instead of 1658,
and is stopped by the cocotb module's own runaway detector with "end-of-test store 84 of 93 not seen within
16 x 100000 cycles". The 102803 errors are one consequence of that, not 102803 findings. The first seed's
collapse is contained by comparison, 29 retirements apart from the repaired run, its program still
finishing its schedule and its 333 errors the comparator reporting the corrupted fetches between cycles
18374 and 18951.

## 6. The verdict does not move, and that is the honest headline

All four runs end `verdict: FAIL`, and on all four the reason field names the same item,
`sva_rvfi_irq_valid_exclusive`. That is the LOG-085 frozen property replacement and it is not this
repair's business. THE REPAIR DOES NOT MAKE THIS TEST GREEN. What it does is remove the grant firing, the
unbooked response, the lockstep collapse and the runaway, and turn the cocotb-side test from FAIL to PASS
on both seeds. A reader who takes the verdict line alone will see no change at all.

The frozen item surviving is itself a clause of the acceptance, because a driver that simply granted less
would have moved the interrupt timing and taken it with it. Its COUNT is not comparable across the pair on
the second seed: 2 before and 2 after on 165313640, but 3 before and 5 after on 1207954461, because a
runaway executes a different instruction stream. What is comparable is the item's presence, and it is
present on both sides of both seeds.

## 7. The zero is not a vacuous zero: withdrawn is its positive control

| seed | ibus grants | ibus withdrawn | dbus grants | dbus withdrawn |
|---|---|---|---|---|
| 165313640 | 7378 | 1 | 121 | 0 |
| 1207954461 | 3779 | 3 | 216 | 0 |

On 165313640 the gate refused exactly ONE decision, and the committed driver produced exactly ONE firing on
that seed. The gate acted where the defect was and nowhere else, so the zero above is a measurement and not
an absence of stimulus.

WHAT THE WITHDRAWN COUNT IS NOT. It is not the number of firings the committed driver would have produced
on the same seed. Past the first phantom grant the two runs are different experiments, and the second seed
shows how different. Only the FIRST withdrawal is comparable, and on 165313640 it is one against one.

## 8. The waveform, the same window on both drivers

Read with the fsdb-mcp-server from `dv/auto_dv/out_l65w3/runs/irq_basic_165313640/waves.fsdb` (committed)
and `dv/auto_dv/out_gnt2/runs/g1/waves.fsdb` (repaired), both seed 165313640, both carrying program crc32
03c84170 of 217 words. Times are the FSDB's 10 ps unit; posedges in this window fall on ...500. The full
transition tables are in the retained waveform log.

Sampled at 183382ns, inside the withdrawn-request half cycle and before the accepting posedge:

| | clk | req | gnt_ready | gnt | outstanding |
|---|---|---|---|---|---|
| committed | 0 | 0 | (none) | 1 | 4 |
| repaired | 0 | 0 | 1 | 0 | 4 |

The driver's DECISION is the same in both, `gnt_ready` high through the low window. What differs is the
gate: `gnt` tracks `req` down at 18338000, so the pre-edge sample of the accepting posedge is req=0 with
gnt=0 and the property has nothing to report. The driver then reads `vif.gnt` at that posedge, sees 0,
counts the withdrawal, and re-arms at the next falling edge.

The region ordering is why the driver and the property cannot disagree. `req` rises again AT the accepting
posedge, and `gnt` does NOT rise with it: it rises a half cycle later. `instr_req_o` is combinational out
of registers that update in the NBA region of that edge, so the core's reaction lands strictly after the
driver's Active-region read, and the driver therefore reads the gate computed from the PRE-EDGE request,
which is the value the property's Preponed sample uses. The opposite case is covered by the same ordering:
a request live before the edge and falling because of it leaves the driver reading gnt=1 and enqueueing
while the property samples req=1 and holds. Both are right, and they agree.

## 9. The data side, because one driver class serves both buses

The change tightens the grant on the data side too, where no phantom grant was ever reported, so a
data-side regression must not hide behind an instruction-side pass. Three load- and store-heavy runs on the
repaired driver, local build c670b56ff4556f3e, all clean:

| run | collected errors | withdrawn (dbus, ibus) | cocotb |
|---|---|---|---|
| gen_ut_intg_span | none | 0, 0 | PASS |
| gen_ut_intg_store | none | 0, 0 | PASS |
| gen_ut_counters on the B17 program | none | 0, 0 | PASS |

Zero withdrawals there is the expected reading and it is what these runs show: nothing on the data side was
relying on a grant standing over a withdrawn request. The third run also re-passes the counter model's
fire-check with the ranges test-writer landed, so the counter rules still judge what they judged before the
driver changed.

## 10. What the property is for now

Section 12.1 answers this and it is worth repeating where a reader of the driver will see it: the gated
shape makes `sva_ibus_gnt_only_with_req` hold BY CONSTRUCTION for this agent, so its permanent silence is
the repair working rather than a property to delete. It remains the only detector for any future agent and
for any change that reintroduces an ungated grant, because the icache's response path carries no address
term and the bus carries no response tag, so nothing in the design can reject a response it did not ask
for.

## 11. What this landing does not settle

- The pair record also lists `sva_ibus_rvalid_outstanding` 8 and `sva_ibus_outstanding_max` 280 for seed
  165313640, where my before run reads 1 and none. Those two ids are the every-cycle floods a wrapping
  outstanding counter produced, and the pair's runs predate the saturating-counter landings. The numbers
  fit that explanation; I have not rebuilt their base to confirm it, so it stands as a reading. It does
  not touch the repair either way.
- `sva_rvfi_irq_valid_exclusive` is untouched here and stays frozen under LOG-085.
- The repair is measured on two seeds, the two the pair record named. No sweep.

## 12. One repair to the area manifest, carried by this hand

Adding the twelve rows meant reading the whole table, which is how a defect in one of my own committed
rows surfaced: the landing-64 row for `gen_fu_l64_b16_c1_seed1_stdout_excerpt.log` recorded its filter as
a grep alternation, and the alternation's PIPES sat unescaped inside a Markdown table cell. That row
renders as six columns rather than four, and a parser that splits on the delimiter sees five fields. It is
the same shape of defect as the testlist entry whose unquoted commas split a YAML flow sequence: a
delimiter inside a scalar. The retained log's bytes, path, size and md5 are untouched; only the source
cell's prose changes, and it now names the filter in words. The excerpt's own header does not carry the
filter, so that cell was the only record of it and rewording rather than deleting was the only option.

Every row of the area manifest now resolves: 3589 rows, none malformed, none missing, every byte count and
md5 recomputed against the file it names.

The test-writer area manifest carries a related but milder inconsistency, a trailing fifth cell on a
number of rows under a four-column header. That file has another owner and it is dirty in the working
tree, so it is reported here and not touched.
