# The three ibus property firings that follow the ruled exclusivity property: an RTL/TB reading

Owner: rtl-arch, 2026-09-05, at the Orchestrator's request after runtime-2's 403-run wave regression
on commit 4017573. Question asked: can the ibus firings be a consequence of the exclusivity
property's condition, or are they a separate protocol observation, and what would settle it.
No RTL change and no exclusion follows from this reading. Citations are to commit 4017573, the tree
those runs were built from, and were checked against that commit rather than against HEAD.

## 1. Answer in one paragraph

The three ibus firings are ONE observation, not three, and they are NOT a consequence of the
exclusivity property's condition. Two of the three are mechanically downstream of the first inside the
testbench's own counter, which is proved from the logs without a wave. The exclusivity property is not
sufficient for them: it fires in 8 of the 403 runs and the ibus signature appears in 2. What the two
share is a plausible provoking condition, the interrupt and NMI traffic that drains the fetch
pipeline, not a causal chain from one property to the other. A property is an observer; it cannot
cause a bus event. What the logs cannot settle is whether the single root event is a testbench
grant-decision artefact or a core protocol violation, and that needs one wave.

## 2. What the three properties actually assert (4017573)

    dv/auto_dv/tb/gen_protocol_props.sv:183  `P_ASSERT(ibus, sva_ibus_gnt_only_with_req,  instr_gnt_i |-> instr_req_o)          // TB
    dv/auto_dv/tb/gen_protocol_props.sv:184  `P_ASSERT(ibus, sva_ibus_rvalid_outstanding, instr_rvalid_i |-> ibus_outstanding > 0) // TB
    dv/auto_dv/tb/gen_protocol_props.sv:185  `P_ASSERT(ibus, sva_ibus_outstanding_max,    ibus_outstanding <= IBUS_MAX_OUTSTANDING) // DUT (bound 8)

All three are evaluated under the macro's guard `disable iff (!rst_ni || !en_ibus)` (:111). Two are
TB obligations by their own annotation; the third is annotated DUT.

The third does not read a DUT signal. It reads the TESTBENCH's counter, updated at
dv/auto_dv/tb/gen_protocol_props.sv:128 as

    ibus_outstanding <= ibus_outstanding + (instr_req_o & instr_gnt_i) - instr_rvalid_i;

`ibus_outstanding` is declared `int unsigned` (:122). So a response with the counter at zero does not
saturate, it WRAPS to 4294967295, and the bound-8 property then fires every cycle until the counter is
brought back under eight. The file already anticipates the neighbouring case in words at :119-120:
"a response in its own grant cycle sees outstanding == 0 and fails the TB obligation".

## 3. The evidence in the two runs, measured

Runs, under /proj_soc/user_dev/fzhang/ibex_dv_out/regress_wave_4017573/runs/:
gen_test_irq_basic_165313640 and gen_test_irq_basic_1207954461. Times are the UVM log's 10 ps ticks;
one cycle is 1000 ticks.

| run | property | firings | first at |
|---|---|---|---|
| 165313640 | sva_rvfi_irq_valid_exclusive | 2 | 13565500 |
| 165313640 | sva_ibus_gnt_only_with_req | 1 | 18338500 (cycle 18334) |
| 165313640 | sva_ibus_rvalid_outstanding | 8 | 18349500 (cycle 18345) |
| 165313640 | sva_ibus_outstanding_max | 280 | 18350500 (cycle 18346) |
| 1207954461 | sva_rvfi_irq_valid_exclusive | 3 | 6591500 |
| 1207954461 | sva_ibus_gnt_only_with_req | 1 | 9250500 |
| 1207954461 | sva_ibus_rvalid_outstanding | 70199 | 15158500 |
| 1207954461 | sva_ibus_outstanding_max | 449948 | 26503500 |

Three readings follow from those numbers alone.

The bound-8 firing is the counter wrapping, not a bus event. In 165313640 its first firing is at cycle
18346 and the first response-without-outstanding is at cycle 18345: EXACTLY one cycle, which is the
counter's own update delay. Its 280 firings against the other's 8 is the every-cycle flood that a
wrapped unsigned counter produces.

The response-without-outstanding firing does NOT always wrap the counter. In 1207954461 it fires 70199
times from cycle 15158 while the bound-8 property stays silent until 26503, eleven million ticks later.
That is the same-cycle case the file names at :119-120: with a grant and its response in one cycle the
expression is 0 + 1 - 1 = 0, so the obligation fails while the counter never wraps. The bound-8 flood
starts only when a response finally arrives without a same-cycle grant.

The grant-without-request firing is first in BOTH runs and fires exactly ONCE in each. In 165313640 it
precedes the other two by 11 and 12 cycles.

So the signature reduces to one root event per run, a grant asserted in a cycle whose request is low,
followed by a queued response the counter never accounted for, followed by the counter wrapping.

## 4. Why it is not a consequence of the exclusivity condition

The exclusivity property fires in 8 of the 403 runs; the ibus signature appears in 2. Six runs
therefore satisfy the exclusivity condition and produce no ibus firing at all, so that condition is not
sufficient. The gaps are also large: 4773 cycles in 165313640 and 2659 cycles in 1207954461 between
the first exclusivity firing and the first ibus firing. (Those are tens of MICROseconds at this
timescale, not milliseconds.)

More fundamentally, a property is an observer. `rvfi_ext_irq_valid |-> !rvfi_valid` reads two RVFI
ports; it drives nothing and cannot make a grant appear. The only honest form of the question is
whether the STATE the exclusivity property happens to observe also provokes the bus event, and the
answer available from the logs is that it is neither necessary nor sufficient, only correlated in two
runs out of eight.

What is plausible, and is a shared cause rather than a chain: the interrupt and NMI traffic drains the
fetch pipeline, and the core's request is combinational, `assign instr_req = ((~icache_enable_i |
branch_i) & lookup_grant_ic0) | (|fill_ext_req);` at rtl/ibex_icache.sv:1030-1031, with the fill
buffers marked stale on a branch at :741. An interrupt entry is a branch, so a drain can drop the
request within a cycle.

## 5. The one thing the logs cannot settle, and the wave that would

At the pin, "a grant with the request low" has two very different causes and the logs cannot separate
them.

Either the core deasserted its request before the grant, which the clone's own interface reference
forbids in prose: `instr_req_o` "must stay high until `instr_gnt_i` is high for one cycle"
(doc/03_reference/instruction_fetch.rst:53-54). That would be a core protocol finding.

Or the request was high at the accepting edge and the property saw an instant where it had already
moved. That is a testbench decision-instant question, and the driver's shape at 4017573 makes it live:
the loop waits on `@(negedge vif.clk)` (dv/auto_dv/env/gen_agents_pkg.sv:265) and asserts
`vif.gnt = 1'b1` at :313, still on that falling edge, while the accepting-edge fix moved only the
address capture, `@(posedge vif.clk)` at :320 followed by `p.addr = vif.addr` at :321. So the grant
DECISION is still taken half a cycle before the edge at which this property is evaluated.

The wave that settles it, and nothing less will: a dump covering the cycles around the single
grant-without-request event, in 165313640 that is cycle 18334 with a margin of about fifty cycles each
side, carrying gen_tb_top.u_ibus_if.{req,gnt,rvalid,addr,outstanding}, the DUT ports
gen_tb_top.u_dut.{instr_req_o,instr_gnt_i,instr_rvalid_i,instr_addr_o}, and on the core side
if_stage_i.gen_icache.icache_i.{instr_req,fill_ext_req,fill_busy_q,fill_stale_q,branch_i}. The single
question to read off it is whether instr_req_o was high at the rising edge where the grant was
sampled. If it was, the finding is the decision instant and belongs with the driver; if it was not,
the finding is the core dropping a request before its grant and belongs to the RTL.

## 6. Whether the parked replacement property changes the picture

It does not. The replacement proposed in Section 6 of dv/auto_dv/evidence/gen_rvfi_irq_valid_exclusive_ruling.md
changes what the RVFI property asserts. It touches no bus signal, no driver and no counter, so every
firing in Section 3 would occur unchanged with the replacement in place. The only difference is that
the exclusivity firing would stop being reported, which would remove the correlation from the logs
without removing anything from the design or the testbench. That is worth stating plainly, because a
correlation that disappears when one observer is retired was never evidence of a chain.

## 7. The root event, settled by waveform (added 2026-09-05)

Section 5 left the single grant-without-request event open between two causes and named the dump that
would decide it. That dump was run and read, and this section records the answer. It also records the
transitions themselves, because the waveforms were non-durable scratch and have been released: this
text is now the surviving evidence of what they showed.

The runs. A fresh -debug_access+all build from the same root, pinned to the same commit 4017573 as the
wave regression and differing from it only by that flag, at both seeds, 165313640 and 1207954461. The
firing totals matched the original runs in both seeds (291 and 520233), so the dump did not perturb
the behaviour. The waveforms were
`regress_ibus_wave/runs/gen_test_irq_basic_165313640/waves.fsdb` (665363 bytes, md5 049a2646bf09) and
`.../gen_test_irq_basic_1207954461/waves.fsdb` (23564419 bytes, md5 e9579d32030d); both were verified
against those figures before reading and are RELEASED SCRATCH, not retained evidence.

What the waveform shows, seed 165313640, in the FSDB's 10 ps units with the clock rising on the half
tick and falling on the tick. The grant is held high with ZERO transitions across 18330000 to
18342000, twelve cycles spanning the event. The request is high throughout that span except for a
single dip, low from the falling edge 18338000 and high again exactly at the rising edge 18338500,
which is where the property fires. At that falling edge `branch_i` goes 1 to 0 and `lookup_grant_ic0`
goes 1 to 0 while `fill_ext_req` is already 0 from 18337500, which is the whole request expression at
rtl/ibex_icache.sv:1030-1031 going false.

Seed 1207954461 is independent and identical in shape: the request low from the falling edge 9250000
to the rising edge 9250500, the same two signals collapsing at that falling edge, and there the
grant's own timing is visible, asserted at the falling edge 9249000 and deasserted at 9251000.

THE ANSWER. The request was low at the rising edge where the grant was sampled, and the core is
nonetheless clean. In both seeds the grant was already high at the rising edge BEFORE the dip, so the
request had been accepted and the obligation that
doc/03_reference/instruction_fetch.rst:53-54 states, that the request stay high until the grant is
high for one cycle, was discharged. The core then stopped requesting, which that rule permits. The
property fired because the grant OUTLIVED the request it accepted by one cycle and the half-cycle dip
landed in that extra cycle. So the root event is the grant-hold policy meeting a combinational
request, not a core protocol violation. No RTL change and no bug row against the design follows,
which is the same conclusion Section 1 reached for the signature as a whole and now rests on
measurement rather than on the two open hypotheses.

One measurement bounds it. In seed 165313640 the request toggles 217 times across the run, roughly a
hundred low periods, while sva_ibus_gnt_only_with_req fires exactly once. The grant is deasserted in
time in essentially every other case, so this is a rare alignment and not a policy that is broadly
wrong.

A hypothesis raised and refuted during the read, recorded so it is not raised again: that the grant
might be held constantly high, which would make `instr_gnt_i |-> instr_req_o` degenerate into a claim
that the core must always be requesting. It is not. The grant transitions 1357 times across that run.

What remains is not an RTL question. The property treats a held grant as implying a live request,
while the driver's grant can outlive the request it accepted, so the property and the driver's policy
disagree about what a held grant means. Which of the two should change is tb-infra-2's call.
