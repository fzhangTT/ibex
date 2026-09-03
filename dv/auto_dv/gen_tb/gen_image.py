"""gen_image: Python view of a program image produced by dv/auto_dv/stim/gen_program.py (the .vmem
plus its .sym.json sidecar): the plusargs that load it, the word dictionary for the MEM_PEEK
read-back, and the tohost address. No simulator access here; pure file parsing (ASCII paths)."""
import json
import random
from pathlib import Path

from dv.auto_dv.gen_tb.gen_knobs import MEMORY_MAP, plusarg


def parse_vmem(path):
    """word index -> word, exactly the gen_elf2mem.py format (`@<hex index>` runs, one hex word per line)."""
    words = {}
    idx = 0
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line[0] == "@":
            idx = int(line[1:], 16)
        else:
            words[idx] = int(line, 16)
            idx += 1
    return words


class GenImage:
    def __init__(self, vmem_path):
        self.vmem = Path(vmem_path)
        self.sidecar = json.loads(self.vmem.with_suffix(".sym.json").read_text())
        self.words = parse_vmem(self.vmem)
        self.crc32 = int(self.sidecar["checksum"]["crc32"], 16)
        self.count = int(self.sidecar["checksum"]["count"])
        self.entry = int(self.sidecar["entry"], 16)
        syms = self.sidecar.get("symbols", {})
        self.tohost = int(syms["tohost"], 16) if "tohost" in syms else None
        assert self.count == len(self.words), f"GEN_IMAGE: sidecar count {self.count} != vmem words {len(self.words)}"

    def plusargs(self):
        args = [plusarg("mem_image", str(self.vmem)), plusarg("mem_image_crc32", f"{self.crc32:08x}"),
                plusarg("mem_image_words", self.count),
                plusarg("boot_addr", f"{self.entry & MEMORY_MAP['boot_page_mask']:08x}")]
        if self.tohost is not None:
            args.append(plusarg("tohost_addr", f"{self.tohost:08x}"))
        return args

    def sample(self, n, seed):
        """n (index, word) pairs drawn from the image with the run seed (the read-back set); non-zero
        words first so an empty or zero-filled model cannot pass the read-back by matching zeros."""
        rng = random.Random(seed)
        nonzero = sorted(k for k, w in self.words.items() if w != 0)
        zero = sorted(k for k, w in self.words.items() if w == 0)
        if n >= len(self.words):
            picks = nonzero + zero
        elif n <= len(nonzero):
            picks = rng.sample(nonzero, n)
        else:
            picks = nonzero + rng.sample(zero, n - len(nonzero))
        return [(k, self.words[k]) for k in sorted(picks)]
