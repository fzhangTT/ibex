#!/usr/bin/env python3
"""Convert a RISC-V ELF32 program into the memory image the generated TB and the ISA shim load.

Output format (defined here; the TB architecture document section C3.3 refers to this file):
  <base>.vmem     Verilog hex for $readmemh into a WORD-addressed sparse memory: a line
                  "@<hex word index>" (byte address / 4) starts each contiguous 4-byte-aligned
                  run, followed by one 8-hex-digit little-endian word per line. Bytes outside
                  PT_LOAD segments inside a run are zero (segments are padded to word bounds).
  <base>.sym.json Entry point, PT_LOAD segments (vaddr, size), every global symbol (name ->
                  address), and the image checksum, for the TB (tohost, signature, debug_rom,
                  _start), the shim, and the read-back check.
  checksum        {"crc32": CRC-32 (zlib, IEEE) over the emitted (word index, word) pairs in
                  ascending index order, each pair as 8 little-endian bytes; "count": number of
                  words}. REQUIREMENT on the consumer: after loading, the SV memory model (and the
                  ISA shim) must recompute both from what they hold and fatal on mismatch, so the
                  backdoor load is verified by read-back (DV_prompt.txt Section 6); the digest is
                  address-dependent, so a word landing at the wrong index is detected.
No third-party modules: the ELF32 program headers and .symtab are parsed here.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

PT_LOAD = 1
SHT_SYMTAB = 2
STB_GLOBAL = 1
STB_WEAK = 2
STT_SECTION = 3
STT_FILE = 4


def parse_elf32(data: bytes):
    if data[:4] != b"\x7fELF":
        sys.exit("not an ELF file")
    if data[4] != 1:
        sys.exit("not ELF32")
    if data[5] != 1:
        sys.exit("not little-endian")
    (e_type, e_machine, _ver, e_entry, e_phoff, e_shoff, _flags, _ehsize, e_phentsize, e_phnum,
     e_shentsize, e_shnum, e_shstrndx) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    if e_machine != 243:
        sys.exit(f"not a RISC-V ELF (e_machine={e_machine})")
    segs = []
    for i in range(e_phnum):
        (p_type, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, _p_flags,
         _p_align) = struct.unpack_from("<IIIIIIII", data, e_phoff + i * e_phentsize)
        if p_type == PT_LOAD and p_memsz:
            body = data[p_offset:p_offset + p_filesz] + b"\x00" * (p_memsz - p_filesz)
            segs.append((p_vaddr, body))
    shdrs = []
    for i in range(e_shnum):
        shdrs.append(struct.unpack_from("<IIIIIIIIII", data, e_shoff + i * e_shentsize))
    symbols = {}
    for sh in shdrs:
        sh_type, sh_offset, sh_size, sh_link, sh_entsize = sh[1], sh[4], sh[5], sh[6], sh[9]
        if sh_type != SHT_SYMTAB:
            continue
        strtab = shdrs[sh_link]
        str_off, str_size = strtab[4], strtab[5]
        strings = data[str_off:str_off + str_size]
        for j in range(sh_size // sh_entsize):
            st_name, st_value, _st_size, st_info, _other, st_shndx = struct.unpack_from(
                "<IIIBBH", data, sh_offset + j * sh_entsize)
            st_bind, st_type = st_info >> 4, st_info & 0xF
            if st_type in (STT_SECTION, STT_FILE) or st_bind not in (STB_GLOBAL, STB_WEAK):
                continue
            end = strings.index(b"\x00", st_name)
            name = strings[st_name:end].decode()
            if name:
                symbols[name] = st_value
    return e_entry, segs, symbols


def to_words(segs):
    """Merge PT_LOAD segments at byte granularity (abutting or word-sharing segments are legal),
    then pack little-endian words; a byte written twice with different values is an error."""
    bytes_map = {}
    for vaddr, body in segs:
        for i, b in enumerate(body):
            a = vaddr + i
            if a in bytes_map and bytes_map[a] != b:
                sys.exit(f"overlapping segments disagree at 0x{a:08x}")
            bytes_map[a] = b
    words = {}
    for a in bytes_map:
        idx = a >> 2
        if idx not in words:
            words[idx] = 0
    for idx in words:
        base = idx << 2
        words[idx] = sum(bytes_map.get(base + k, 0) << (8 * k) for k in range(4))
    return words


def render_vmem(words):
    lines = []
    prev = None
    for idx in sorted(words):
        if prev is None or idx != prev + 1:
            lines.append(f"@{idx:08x}")
        lines.append(f"{words[idx]:08x}")
        prev = idx
    return "\n".join(lines) + "\n"


def checksum(words):
    """CRC-32 over (index, word) pairs in ascending index order, 8 LE bytes per pair (see docstring)."""
    crc = 0
    for idx in sorted(words):
        crc = zlib.crc32(struct.pack("<II", idx, words[idx]), crc)
    return {"crc32": crc & 0xFFFFFFFF, "count": len(words)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("elf", type=Path)
    ap.add_argument("--out-base", type=Path, default=None, help="output path without extension (default: beside the ELF)")
    args = ap.parse_args()
    data = args.elf.read_bytes()
    entry, segs, symbols = parse_elf32(data)
    words = to_words(segs)
    base = args.out_base or args.elf.with_suffix("")
    base.with_suffix(".vmem").write_text(render_vmem(words))
    meta = {
        "source_elf": str(args.elf),
        "entry": f"0x{entry:08x}",
        "segments": [{"vaddr": f"0x{v:08x}", "size": len(b)} for v, b in segs],
        "checksum": {k: (f"0x{v:08x}" if k == "crc32" else v) for k, v in checksum(words).items()},
        "symbols": {k: f"0x{v:08x}" for k, v in sorted(symbols.items())},
    }
    base.with_suffix(".sym.json").write_text(json.dumps(meta, indent=2) + "\n")
    cs = checksum(words)
    print(f"wrote {base}.vmem ({cs['count']} words, crc32 0x{cs['crc32']:08x}) and {base}.sym.json "
          f"({len(symbols)} symbols, entry 0x{entry:08x})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
