---
name: waveform-querying
description: Query and analyze simulation waveform data (FSDB/VCD/FST) for signal values, transitions, edges, timing relationships, and protocol compliance. Use when debugging a waveform — signal behavior at a specific time, handshake/latency measurement, or state-machine tracking; not for root-causing a signal against the RTL (use wave-rtl-correlate). Backed by the fsdb-mcp-server / siliconpilot `queryWaveform` MCP tools.
---

Adapted from ChipSmart (riscv/ChipSmart) waveform-querying.

# Waveform Querying Skill

## Overview

This skill enables extraction and analysis of data from waveform files (VCD, FST, FSDB formats). It provides the ability to query signal values, detect events, analyze timing relationships, and extract transaction-level information from simulation waveforms.

## When to Use

- User asks to analyze or debug a simulation waveform (VCD, FST, FSDB)
- Task requires extracting signal values, transitions, or timing from waveform data
- Need to verify protocol compliance or measure performance from simulation results
- User asks about signal behavior at specific simulation times

## Workflow

A typical waveform-debugging session has three phases:

1. **Discover & orient** — bound the time range, find the relevant signal hierarchy, sample a few values to confirm you have the right window.
2. **Deep analysis** — extract value changes / edges across the signals of interest, correlate timing, compute aggregates (counts, pulse widths, handshake latency).
3. **Follow-up on anomalies** — narrow in on specific events flagged in phase 2.

## Core Capabilities

### 1. Signal Discovery

#### Finding Signals

**By exact name:**
```
Query: Find all changes to signal 'top.cpu.pc'
Result: List of timestamps and values
```

**By pattern:**
```
Query: Find all signals matching 'top.*.valid'
Result: List of matching signal names
```

**By hierarchy:**
```
Query: Find all signals under 'top.memory'
Result: Complete signal list in that hierarchy
```

### 2. Value Change Analysis

#### Basic Queries

**Get all changes:**
```
Query: All value changes for signal X
Returns: Timestamp, value pairs
```

**Time-bounded changes:**
```
Query: Changes to signal X between time T1 and T2
Returns: Filtered timestamp, value pairs
```

**Value-specific changes:**
```
Query: When does signal X equal value V?
Returns: List of timestamps
```

#### Change Detection

**Transition detection:**
```
Query: When does signal X change from A to B?
Returns: Timestamps of specific transitions
```

**Delta analysis:**
```
Query: What changed between time T1 and T2?
Returns: All signals that changed in window
```

### 3. Edge Detection

#### Rising/Falling Edges

**Rising edges:**
```
Query: Find all rising edges of clock signal
Returns: Timestamps of 0->1 transitions
```

**Falling edges:**
```
Query: Find all falling edges of reset signal
Returns: Timestamps of 1->0 transitions
```

**Edge counting:**
```
Query: How many rising edges of clk between T1 and T2?
Returns: Count of edges
```

#### Clock Analysis

**Clock period:**
```
Query: What is the clock period?
Process: Find consecutive rising edges, compute delta
Returns: Period in time units
```

**Clock frequency:**
```
Query: What is the clock frequency?
Process: Compute from period
Returns: Frequency
```

### 4. Protocol Analysis

#### Handshake Detection

**Valid/Ready handshakes:**
```
Query: When do valid and ready both assert?
Returns: Timestamps of successful handshakes
```

**Transaction extraction:**
```
Query: Extract all AXI transactions
Process: Find handshakes, extract associated data
Returns: List of transactions with data
```

#### Bus Monitoring

**Bus activity:**
```
Query: When is the bus active?
Process: Check enable/valid signals
Returns: Active time windows
```

**Data capture:**
```
Query: What data was transferred?
Process: Sample data signal at handshake times
Returns: List of data values
```

### 5. Timing Analysis

#### Setup/Hold Checking

**Data stability:**
```
Query: Is data stable before clock edge?
Process: Check data changes relative to clock
Returns: Violations if any
```

**Response latency:**
```
Query: Time from request to response
Process: Find request event, find response event, compute delta
Returns: Latency values
```

#### Performance Metrics

**Throughput:**
```
Query: How many transactions per cycle?
Process: Count transactions, divide by time
Returns: Throughput metric
```

**Utilization:**
```
Query: What percentage of time is interface busy?
Process: Sum active cycles, divide by total
Returns: Utilization percentage
```

### 6. State Machine Analysis

#### State Tracking

**State transitions:**
```
Query: What states does FSM visit?
Returns: Sequence of states with timestamps
```

**State duration:**
```
Query: How long in each state?
Process: Compute time between state changes
Returns: Duration per state
```

**Illegal states:**
```
Query: Does FSM enter illegal states?
Process: Check state values against legal set
Returns: Illegal state occurrences
```

### 7. Common Query Patterns

#### Pattern 1: Find First Occurrence

```
Task: When does error flag first assert?
Process:
1. Query all changes to error signal
2. Filter for value = 1
3. Return first timestamp
```

#### Pattern 2: Count Events

```
Task: How many packets were sent?
Process:
1. Find all rising edges of packet_valid
2. Count edges
3. Return count
```

#### Pattern 3: Extract Transaction Data

```
Task: Get all write transactions
Process:
1. Find handshakes (write_valid & write_ready)
2. For each handshake, sample write_data
3. Return list of data values
```

#### Pattern 4: Verify Protocol

```
Task: Check that ready never drops during valid
Process:
1. Find all times when valid=1
2. For each, check if ready ever goes to 0
3. Report violations
```

#### Pattern 5: Measure Latency

```
Task: Request to grant latency
Process:
1. Find all request rising edges
2. For each, find next grant rising edge
3. Compute time delta
4. Return latency statistics (min/max/avg)
```

### 8. Multi-Signal Analysis

#### Correlation

**Simultaneous events:**
```
Query: When do signals A and B both change?
Process: Find change times for each, find intersection
Returns: Common timestamps
```

**Causal relationships:**
```
Query: Does A always change before B?
Process: Compare change timestamps
Returns: Verification result
```

#### Bus Analysis

**Multi-bit values:**
```
Query: What is the value of 32-bit bus?
Process: Combine individual bit signals
Returns: Composite values
```

**One-hot checking:**
```
Query: Is grant bus one-hot?
Process: Check that exactly one bit is set
Returns: Violations if any
```

### 9. Debugging Workflows

#### Workflow 1: Find Failure Point

```
1. Identify failure symptom (e.g., wrong output)
2. Query output signal to find failure time
3. Work backwards:
   - Query inputs at that time
   - Query intermediate signals
   - Trace data flow
4. Identify first incorrect value
5. Determine root cause
```

#### Workflow 2: Protocol Violation

```
1. Query protocol signals (valid, ready, etc.)
2. Check for illegal patterns:
   - Valid without ready for too long
   - Ready drops during valid
   - Data changes during valid
3. Find first violation
4. Examine surrounding signals
5. Determine cause
```

#### Workflow 3: Performance Analysis

```
1. Query transaction signals
2. Count transactions in time window
3. Compute throughput
4. Identify bottlenecks:
   - When is interface idle?
   - What causes stalls?
5. Suggest optimizations
```

### 10. Best Practices

#### Query Efficiency

**Do:**
- Specify time windows when possible
- Use exact signal names when known
- Query multiple signals in one operation
- Filter early to reduce data volume

**Don't:**
- Query entire waveform without time bounds
- Use overly broad patterns
- Query signals individually in loops
- Extract unnecessary data

#### Data Interpretation

**Remember:**
- Time units are waveform-specific (usually ps)
- X/Z values indicate uninitialized or contention
- Multi-bit signals may need bit extraction
- Clock edges define sampling points

#### Verification

**Always:**
- Verify signal names exist before querying
- Check for X/Z values in results
- Validate time ranges are reasonable
- Cross-check results with expectations

### 10b. Visualizing Timing

When a timing relationship is the answer — a handshake, a clock/edge alignment,
a multi-signal sequence, a protocol violation — present it as a **WaveDrom**
diagram in addition to prose. Emit a fenced ` ```wavedrom ` block containing a
WaveDrom signal object built from the values/edges you extracted. A
text-capable renderer draws it inline (no image needed), so this is a low-cost,
high-clarity way to make a timing answer legible.

Keep it small and faithful to the queried data (don't invent edges):

```wavedrom
{ "signal": [
  { "name": "clk",     "wave": "p......" },
  { "name": "req",     "wave": "0.1..0." },
  { "name": "ack",     "wave": "0..1.0." },
  { "name": "data[7:0]","wave": "x.=..x.", "data": ["0xA5"] }
]}
```

Wave chars: `p`/`n` clock, `0`/`1` levels, `.` hold previous, `x` unknown,
`z` hi-z, `=`/`2`-`9` bus segments (label via the `data` array). Use this only
when a picture clarifies; for a single value or count, plain text is better.

### 11. Format Support

#### VCD (Value Change Dump)
- Standard format
- Text-based
- Widely supported
- Can be large

#### FST (Fast Signal Trace)
- Compressed format
- Faster than VCD
- Smaller file size
- GTKWave native format

#### FSDB (Fast Signal Database)
- Synopsys proprietary
- Requires Verdi libraries
- High performance
- Industry standard for large designs

**Note:** FSDB requires `VERDI_HOME` or `LD_LIBRARY_PATH` to be set to Verdi installation.

### 12. Limitations

**Cannot:**
- Modify waveform data
- Generate new signals (only query existing)
- Perform complex mathematical operations
- Handle corrupted waveform files
- Access signals not dumped in simulation

**Performance considerations:**
- Large waveforms may be slow to query
- Broad time ranges increase query time
- Pattern matching slower than exact names
- Multiple queries faster than repeated single queries

### 13. Common Use Cases

#### Use Case 1: Debug Assertion Failure

```
Task: Assertion failed at time T, why?
Process:
1. Query all signals in assertion at time T
2. Check which condition failed
3. Trace back signal history
4. Find root cause
```

#### Use Case 2: Verify Coverage

```
Task: Did we hit all FSM states?
Process:
1. Query FSM state signal
2. Extract all unique values
3. Compare against expected states
4. Report missing states
```

#### Use Case 3: Performance Measurement

```
Task: What is average transaction latency?
Process:
1. Find all transaction starts (request edges)
2. Find corresponding ends (response edges)
3. Compute deltas
4. Calculate statistics
```

#### Use Case 4: Protocol Compliance

```
Task: Verify AXI protocol compliance
Process:
1. Query all AXI signals
2. Check handshake rules
3. Verify data stability
4. Check burst behavior
5. Report violations
```

## Usage Examples

### Example 1: Find Signal Value

**Task**: "What is the value of pc at time 1000?"

**Process**:
1. Query changes to 'top.cpu.pc'
2. Find last change before time 1000
3. Return that value

### Example 2: Count Transactions

**Task**: "How many writes occurred?"

**Process**:
1. Query handshakes (write_valid & write_ready)
2. Count handshake occurrences
3. Return count

### Example 3: Measure Latency

**Task**: "What is request-to-grant latency?"

**Process**:
1. Find all request rising edges
2. For each, find next grant rising edge
3. Compute time differences
4. Return min/max/average

### Example 4: Debug Failure

**Task**: "Why did output go to X at time 5000?"

**Process**:
1. Query output at time 5000 (confirm X)
2. Query inputs at time 5000
3. Trace back through logic
4. Find first X value in chain
5. Identify source

## Integration with Other Skills

**With RTL Analysis:**
- Query waveform to understand behavior
- Verify RTL implementation matches waveform
- Debug RTL issues using waveform data

**With Verification:**
- Extract coverage data from waveforms
- Verify test stimulus in waveform
- Debug test failures

**With Documentation:**
- Generate timing diagrams from waveform data
- Document actual behavior
- Create examples from real simulations

### 14. Large Waveform Strategies

#### Time-Window Narrowing

When working with large waveforms (billions of cycles), narrow the search space systematically:

```
1. Start broad: get simulation time range (start_time, end_time)
2. If looking for an event: binary search by time
   - Check midpoint for condition
   - Narrow to relevant half
   - Repeat until window is <1000 cycles
3. If analyzing behavior: sample at regular intervals
   - Sample every N cycles (N = total_time / 100)
   - Identify interesting regions from samples
   - Zoom into those regions
4. If counting events: chunk the time range
   - Process in 10K-cycle chunks
   - Aggregate counts across chunks
   - Avoid loading entire waveform at once
```

#### Memory-Efficient Patterns
- **Cache `get_signals()` result** — call once, reuse for all queries
- **Always specify `start_time` and `end_time`** — unbounded queries on large waveforms are very slow
- **Query specific signals** — avoid iterating all signals unless necessary
- **Process in time slices** — for long simulations, analyze in chunks

## Integration

- **With rtl-systemverilog-analysis-generation**: Query waveform to verify RTL behavior matches intent
- **With code-review-debugging**: Use waveform data to debug simulation failures
- **With verification-planning-test-generation**: Extract coverage data and verify test stimulus
- **With diagram-builder**: Compare expected timing diagrams against actual waveforms

## Agent Rules

1. **Never expose implementation details** — Do not describe the wavescript binary or internal query engine to the user.
2. **Report in natural language** — Translate raw signal values into hardware-meaningful interpretations (e.g., "grant asserted for 3 cycles" not "value=1 at t=300,400,500").
3. **Always validate results** — Check for X/Z values, verify signal names exist before reporting, confirm time range is sensible.
4. **Be efficient** — Use time windows and exact signal names whenever possible; batch multiple queries into one call.

## RTL Pivot — When Waveform Finds a Stuck Signal

When the waveform reveals a signal stuck at 0 or constant throughout simulation:

**Step 1 — Check git diff FIRST.**
If the workspace has a `git diff` (modified RTL files), run `git diff` immediately.
The bug almost always lives in the modified code. Do NOT spend multiple calls searching
for the signal name in source — the waveform name (e.g. `Trramenable`) may come from
generated RTL that isn't in the workspace source tree.

**Step 2 — If searching for the signal name returns 0 results**, stop searching and pivot to RTL analysis:
- Analyze the cone of influence for `<signal>` in `rtl/<module>.sv` (input direction)
  → finds what drives the stuck signal within the module
- Trace `<signal>` upward from `<mod>` across module boundaries
  → traces the signal upward across module boundaries when cone of influence hits a port

**Step 3 — Map memory-interface addresses to the field/CSR they hit** using the RTL
address decode logic (e.g. `ibex_cs_registers.sv` for CSRs, or the LSU/instr-fetch
address path) by searching file contents or reading the file, not by guessing from
waveform address values alone.

**DO NOT** make 5+ search calls looking for a signal name that returned 0 results on the
first try. One failed search → immediate pivot to `git diff` + cone of influence analysis.

## Optional: illustrate with a diagram

A diagram is **optional** — reach for one only when it makes the answer clearer
than prose/tables would (a multi-signal handshake, a non-obvious state sequence).
Don't emit one by default. See the `diagram-builder` skill for format syntax.

- **Timing / handshake / bus window** → a ` ```wavedrom ` block of the relevant
  cycles. The interactive TUI draws this INLINE as a real waveform card, so it's
  the natural choice when a few signals' relative timing is the whole point.
  Build the `signal` array from the edge/value data you actually queried — never
  from assumed protocol behaviour.
- **State-machine analysis** (the state-tracking queries) → a ` ```mermaid `
  `stateDiagram-v2` of the observed states + transition triggers.

Ground every transition in a value you read; if a query returned no data, say so
rather than drawing a speculative wave.
<!-- length-justified: 8 distinct query patterns with worked examples — each is its own use-case -->
