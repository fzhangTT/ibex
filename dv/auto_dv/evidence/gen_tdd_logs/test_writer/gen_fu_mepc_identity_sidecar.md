# Companion to gen_fu_mepc_identity.log: a path-free identity for the sidecar it names

WHY THIS FILE EXISTS. The retained log names its third input as "sidecar of a program built at the
same seed 60326dfb0989". That digest is over prog.sym.json, which embeds absolute paths (the ELF it
was produced from, among others), so nobody rebuilding the same program in a different directory can
reproduce it. The retained log's bytes are not reopened; this companion adds the identity that IS
reproducible, and names what the line was carrying.

WHAT THE LINE IS FOR. One value: the address of the spin instruction, gen_irq_wait = 0x80000154,
which the fixed check compares every recorded mepc against. Nothing else in the sidecar is used.

THE MEASUREMENT, two builds of mine at the same seed in different directories.

  build A, the one the retained log names
    prog.sym.json  sha256[:12]  60326dfb0989      <- path-bearing, not reproducible elsewhere
    symbols block  sha256[:12]  70f98779d358
    gen_irq_wait                0x80000154        (9 symbols in the block)
  build B, a second build in a fresh directory
    prog.sym.json  sha256[:12]  fe31ec219e0d      <- a different file digest, same program
    symbols block  sha256[:12]  70f98779d358
    gen_irq_wait                0x80000154        (9 symbols in the block)

The two file digests differ and the two symbols-block digests agree, which is the point: the block
is the part of the sidecar that a rebuild reproduces. Both builds report the same image checksum
(crc32 0x03c84170, entry 0x80000080, 217 words), and prog.nm carries the same line in both,
"80000154 T gen_irq_wait".

COMMANDS, from the clone root after ci/env.sh with PYTHONPATH unset:
  python3 dv/auto_dv/tests/gen_programs/gen_irq_basic_prog.py --seed 694904681 --out <D>/gen_source.S
  python3 dv/auto_dv/stim/gen_program.py --directed <D>/gen_source.S --seed 694904681 \
      --out <D>/prog --gcc-opts=-Idv/auto_dv/tests/gen_programs
  python3 -c "import hashlib,json;d=json.load(open('<D>/prog/prog.sym.json'));\
print(hashlib.sha256(json.dumps(d['symbols'],sort_keys=True).encode()).hexdigest()[:12])"

INDEPENDENT AGREEMENT, stated as such. The Critic's re-review reports the same symbols-block digest
from its own build. That figure was not copied into this file: both numbers above are from my two
builds, and the agreement is a cross-check rather than a source.

WHAT A LATER READER SHOULD USE. Cite the symbols-block digest 70f98779d358, or prog.nm, for any
claim about this program's symbols. The path-bearing file digest identifies one directory's copy and
nothing more.
