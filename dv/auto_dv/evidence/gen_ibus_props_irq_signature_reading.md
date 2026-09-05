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
