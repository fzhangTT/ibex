---
name: rtl-workspace-exploration
description: Efficient search/glob strategies for navigating an unfamiliar RTL/DV workspace without search spirals — inventory first, cap reads, batch searches, never re-search what's already in context. Use when at risk of a search spiral ("where is X", repeated greps returning little) and a discovery pass is needed before reading files.
---

Adapted from ChipSmart (riscv/ChipSmart) rtl-workspace-exploration.

# RTL Workspace Exploration

Efficient strategies for navigating SystemVerilog/Verilog RTL and UVM DV workspace structures
without triggering search spirals or reading files unnecessarily.

## Workspace Layout Convention (this repo)

- `rtl/` — synthesizable ibex RTL (`.sv`)
- `dv/uvm/core_ibex/` — verification environment (`.sv`, `Makefile`, no bzsim/Bazel)
- `dv/uvm/core_ibex/env/` — UVM environment: `*_env.sv`, `*_agent.sv`, `*_driver.sv`, `*_monitor.sv`
- `dv/uvm/core_ibex/tests/` — test files: `*_test.sv`, `*_seq.sv`
- `dv/uvm/core_ibex/tb/` — testbench top: `*_tb_top.sv`, `*_if.sv`

## Step 1: Inventory First, Read Second

**ALWAYS start by finding files before reading anything:**
- Find all `rtl/**/*.sv` files → see all RTL modules at once
- Find all `dv/**/*.sv` files → see all DV components at once

Identify the top-level module from names: `*_top.sv`, `*_wrap.sv`, `*_subsystem.sv`.

## Step 2: One-Pass Reading Budget

For RTL analysis questions — read at most 3 files:
1. Find all `rtl/**/*.sv` files — inventory
2. Read the top module file — instantiation hierarchy
3. Search for `module ` in the `rtl/` directory — confirm all module names (optional)

For DV hierarchy questions — read at most 3 files:
1. Find all `dv/**/*env*.sv` files — find env class
2. Read the env file — agent instantiations
3. Find all `dv/**/*agent*.sv` files — agent files

## Search Convergence Rules

- **2-search rule**: If 2 searches for the same target return nothing → report it missing and move on.
  Do NOT try 8 different pattern variants.
- **Never repeat patterns**: Each search must use a DIFFERENT pattern from all previous searches this session.
- **Width before depth**: Search the whole `rtl/` directory before narrowing to a specific file.
- **Trust file listing results**: If a file doesn't appear when listing all `rtl/**/*.sv` files, it doesn't exist here.

## Search OR-Pattern Batching

When scanning for multiple related RTL constructs, merge into ONE search with a regex OR pattern:

- RTL quality scan — all constructs in one search: search for `assert property|assume property|cover property|\$assert|\$cover` in `rtl/`
- Clock/reset survey — one search: search for `always_ff|always_comb|always @\s*\(` in `rtl/` (list matching files only)
- Latch/combinational hazard scan — one search: search for `latch|transparent|level.sensitive` in `rtl/`

**Anti-pattern**: Searching for `assert property`, then `assume property`, then `cover property` separately — 3 searches returning the same file sets, could be 1.

## File Search Brace Batching

When looking for multiple file names or extensions in the same directory tree, use ONE search with braces:

- All sim config files in one search: find all `dv/**/{Makefile,*.f,*.yaml}` files
- All RTL file types in one search: find all `rtl/**/*.{sv,v,vh,svh}` files
- All UVM component types in one search: find all `dv/**/*_{env,agent,driver,monitor,scoreboard}.sv` files

**Anti-pattern**: Searching for `**/Makefile`, then `**/*.f`, then `**/*.yaml` separately — 3 searches, same result as 1.

## Exploration Tracking

For tasks reading 4+ files, keep a live search log:

1. Note before reading: `"reading rtl/mc/mc_top.sv"`
2. Mark complete with a result summary: `"mc_top.sv ✓ — instantiates csr_ctrl, data_path"`
3. Log searches: `"searched 'assert property|assume property' in rtl/ → 12 hits in 4 files"`
4. Before any new search or file read: check prior results — if already done, use cached result.

This prevents re-reading files already in context and prevents duplicate search patterns across a multi-step exploration.

## Clock Domain Identification (One-Pass)

- Search for `clk|clock` in `rtl/` (list matching files only)
- Search for `always_ff.*@.*posedge` in `rtl/`

That's it — 2 searches maximum. Do NOT read every file to find clocks.

## Signal Tracing (3-Step Maximum)

1. Search for `signal_name` in `rtl/` — find all files referencing it
2. Read the source file — where it's driven
3. Read the destination file — where it's consumed

## Efficiency Rules (NEVER violate)

- NEVER run raw shell commands for content search — always use your platform's content search capability
- NEVER run raw shell commands to read files — always use your platform's file reading capability
- NEVER run raw shell commands to find files — always use your platform's file finding capability
- NEVER re-read a file you already have in context — use the cached content
- NEVER list directories one-by-one for file discovery — use a recursive file search (e.g., find all `rtl/**/*.sv`) to get every file path in the entire tree in one step

## Largest File Query

To find the largest/most complex RTL module (highest line count):

1. Find all `rtl/**/*.sv` files
2. Run: `wc -l rtl/foo.sv rtl/bar.sv rtl/baz.sv | sort -n | tail -10`

Do NOT search within files individually or list directories one-by-one to survey file sizes — 2 steps vs 10+.

## Multi-Hop Signal Trace

To trace a signal path end-to-end through the hierarchy:

Each hop:
1. Search for `signal_name` across all files in `rtl/` — finds all files in 1 search
2. Read `rtl/path/to/driver.sv` — read the driving module
3. Identify next signal in chain → repeat

Cap at 4 hops. Do NOT search within each file individually — one search across `rtl/` covers the whole tree.

## Session Context Reuse

When a prompt says "from the module you found earlier" or "from the DV env you mapped earlier":
- The file is **already in your context** from a prior result
- Look in prior results for the file path or content — do NOT re-search or re-list files
- Wrong: P6 "find scoreboard from DV env" → searching for files 6 times to rediscover what P2 already read
- Right: DV env was read in P2 → scan that result for scoreboard name → read the file directly
