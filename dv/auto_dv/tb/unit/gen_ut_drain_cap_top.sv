// gen_ut_drain_cap_top: unit test of gen_tb_pkg::gen_irq_drain_cap_cycles, pure SV, no RTL and no UVM test.
// The cap ends an interrupt-entry drain whose core has stopped retiring, so it must never end a drain that is
// still doing its job. The drain runs while the retired count is AT OR BELOW GEN_IRQ_ENTRY_BOUND_RECORDS, so its
// length is the bound PLUS ONE records, and the cap has to cover that length out of its own per-record budget:
// GEN_IRQ_DRAIN_MARGIN_CYCLES is spent on the finish handshake and the last record's write-back, so borrowing it
// for an extra record would leave those unfunded. A cap short of the drain's length cannot fail a run, it can only
// end the drain early, which is the silent missed detection the bound-plus-one drain length exists to remove.
module gen_ut_drain_cap_top;
  import gen_tb_pkg::*;

  int unsigned fails = 0;

  function automatic void check(string what, longint got, longint exp);
    bit ok = (got === exp);
    $display("%s %s got %0d exp %0d", ok ? "OK  " : "FAIL", what, got, exp);
    if (!ok) fails++;
  endfunction

  function automatic void check_ge(string what, longint got, longint bound);
    bit ok = (got >= bound);
    $display("%s %s got %0d need at least %0d", ok ? "OK  " : "FAIL", what, got, bound);
    if (!ok) fails++;
  endfunction

  // The worst legitimate cost of one drain record, the same quantity the cap derives from: the slower bus's grant
  // plus response wait, plus the pipeline's own stages.
  function automatic int unsigned per_record(int unsigned ig, int unsigned ir, int unsigned dg, int unsigned dr);
    int unsigned ibus = ig + ir;
    int unsigned dbus = dg + dr;
    return (ibus > dbus ? ibus : dbus) + GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES;
  endfunction

  int unsigned drain_records;
  int unsigned pr_def, pr_wide, pr_mid;
  int unsigned cap_def, cap_wide, cap_mid, cap_narrow;

  initial begin
    drain_records = GEN_IRQ_ENTRY_BOUND_RECORDS + 1;
    $display("gen_ut_drain_cap: bound %0d records, drain length %0d records, overhead %0d, margin %0d",
             GEN_IRQ_ENTRY_BOUND_RECORDS, drain_records, GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES,
             GEN_IRQ_DRAIN_MARGIN_CYCLES);

    // 1. THE PROPERTY, at the default effective maxima the regimes produce.
    pr_def  = per_record(3, 4, 3, 4);
    cap_def = gen_irq_drain_cap_cycles(3, 4, 3, 4);
    $display("     default maxima i 3/4 d 3/4: per_record %0d, cap %0d", pr_def, cap_def);
    check_ge("cap covers the drain's length at the default maxima", cap_def, pr_def * drain_records);
    check("cap at the default maxima is the drain's length plus the margin", cap_def,
          pr_def * drain_records + GEN_IRQ_DRAIN_MARGIN_CYCLES);

    // 2. THE DISCRIMINATING CASE. A cap sized over the bound alone covers the extra record only out of the margin,
    // so it holds while a record costs less than the margin and breaks once a record costs more. These maxima put
    // one record above the margin, which is where borrowing it stops working.
    pr_wide  = per_record(20, 25, 3, 4);
    cap_wide = gen_irq_drain_cap_cycles(20, 25, 3, 4);
    $display("     wide instruction bus i 20/25 d 3/4: per_record %0d (margin %0d), cap %0d",
             pr_wide, GEN_IRQ_DRAIN_MARGIN_CYCLES, cap_wide);
    check_ge("a record costlier than the margin is still covered", cap_wide, pr_wide * drain_records);
    check("cap on the wide bus is the drain's length plus the margin", cap_wide,
          pr_wide * drain_records + GEN_IRQ_DRAIN_MARGIN_CYCLES);

    // 3. The data bus decides when it is the slower one, so the property must not be an instruction-bus accident.
    pr_mid  = per_record(3, 4, 20, 25);
    cap_mid = gen_irq_drain_cap_cycles(3, 4, 20, 25);
    check("the slower bus sets the per-record cost", pr_mid, pr_wide);
    check_ge("cap covers the drain's length when the data bus is the slower one", cap_mid,
             pr_mid * drain_records);

    // 4. POSITIVE CONTROLS, true of any correct sizing, so a run of this test that fails everything is visible as
    // such rather than read as the property above being wrong.
    cap_narrow = gen_irq_drain_cap_cycles(1, 1, 1, 1);
    check_ge("the cap grows with the bus maxima", cap_wide, cap_narrow);
    check_ge("the cap exceeds the margin alone", cap_narrow, GEN_IRQ_DRAIN_MARGIN_CYCLES);
    check("both buses at one give the overhead plus two per record", per_record(1, 1, 1, 1),
          2 + GEN_IRQ_DRAIN_RECORD_OVERHEAD_CYCLES);

    $display("GEN_UT_DRAIN_CAP %s (%0d failures)", fails ? "FAIL" : "PASS", fails);
    $finish;
  end
endmodule
