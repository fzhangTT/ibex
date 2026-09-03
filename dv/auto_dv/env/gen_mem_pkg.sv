// gen_mem_pkg: the shared sparse memory behind both bus agents (architecture C3.3). Test equipment
// only: word-addressed image load (the gen_elf2mem.py .vmem format), the CRC-32 digest the image
// sidecar defines, byte-masked writes, MMIO windows with handlers, region mapping from the rendered
// GEN_MM_* constants, and the MEM_PEEK read path. Failure paths are UVM reports (collected): MEM_LOAD
// fatal on a digest mismatch, MEM_UNMAPPED error unless unmapped_ok.
package gen_mem_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;

  // Handler for one MMIO window (signature sink, interrupt acknowledge, end-of-test, phase marker).
  class gen_mmio_handler;
    virtual function void on_write(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
    endfunction
    virtual function logic [31:0] on_read(logic [31:0] addr);
      return 32'h0;
    endfunction
  endclass

  typedef struct {
    logic [31:0]     base;
    logic [31:0]     size;
    gen_mmio_handler h;
  } gen_mmio_window_t;

  class gen_mem_model;
    string name;
    logic [31:0] mem [int unsigned];      // word index -> word (sparse)
    gen_mmio_window_t windows [$];
    bit          unmapped_ok = 1'b0;      // +gen_mem_unmapped_ok: count and answer 0 instead of erroring
    int unsigned unmapped_count = 0;
    int unsigned mmio_writes = 0;

    function new(string name = "gen_mem_model");
      this.name = name;
    endfunction

    // ---- regions (rendered constants; the MMIO page is handled by windows first) ----------------
    function bit in_range(logic [31:0] addr, logic [31:0] base, logic [31:0] size);
      return (addr >= base) && (addr - base < size);
    endfunction
    function bit is_mapped(logic [31:0] addr);
      return in_range(addr, GEN_MM_BOOT_PAGE, GEN_MM_PROG_SIZE) ||
             in_range(addr, GEN_MM_DM_BASE, GEN_MM_DM_SIZE) ||
             in_range(addr, GEN_MM_MMIO_BASE, GEN_MM_MMIO_SIZE);
    endfunction
    function int find_window(logic [31:0] addr);
      foreach (windows[i]) if (in_range(addr, windows[i].base, windows[i].size)) return i;
      return -1;
    endfunction
    function void add_mmio(logic [31:0] base, logic [31:0] size, gen_mmio_handler h);
      gen_mmio_window_t w;
      w.base = base; w.size = size; w.h = h;
      windows.push_back(w);
    endfunction

    // ---- image load: "@<hex word index>" runs of one hex word per line (gen_elf2mem.py) ---------
    // Returns the number of words loaded; a malformed file is a MEM_LOAD fatal.
    function int unsigned load_vmem(string path);
      int fd, n = 0;
      string line;
      int unsigned idx = 0;
      logic [31:0] w;
      fd = $fopen(path, "r");
      if (fd == 0) uvm_report_fatal("MEM_LOAD", $sformatf("cannot open image %s", path));
      while ($fgets(line, fd)) begin
        // strip trailing newline / spaces
        while (line.len() > 0 && (line[line.len()-1] == "\n" || line[line.len()-1] == "\r" || line[line.len()-1] == " "))
          line = line.substr(0, line.len() - 2);
        if (line.len() == 0) continue;
        if (line[0] == "@") begin
          if ($sscanf(line.substr(1, line.len() - 1), "%h", idx) != 1)
            uvm_report_fatal("MEM_LOAD", $sformatf("bad address line '%s' in %s", line, path));
        end else begin
          if ($sscanf(line, "%h", w) != 1)
            uvm_report_fatal("MEM_LOAD", $sformatf("bad data line '%s' in %s", line, path));
          mem[idx] = w;
          idx++;
          n++;
        end
      end
      $fclose(fd);
      return n;
    endfunction

    function int unsigned word_count();
      return mem.num();
    endfunction

    // ---- digest: CRC-32 (zlib polynomial, init 0xFFFFFFFF, final XOR) over 8 LE bytes (index, word)
    // per loaded word in ascending index order; identical to gen_elf2mem.checksum().
    function logic [31:0] crc32_bytes(logic [31:0] crc, logic [7:0] b);
      crc = crc ^ {24'h0, b};
      for (int k = 0; k < 8; k++)
        crc = (crc[0]) ? ((crc >> 1) ^ 32'hEDB8_8320) : (crc >> 1);
      return crc;
    endfunction
    function logic [31:0] crc32_index_word();
      logic [31:0] crc = 32'hFFFF_FFFF;
      int unsigned i;
      if (mem.first(i)) begin
        do begin
          logic [31:0] w = mem[i];
          crc = crc32_bytes(crc, i[7:0]);   crc = crc32_bytes(crc, i[15:8]);
          crc = crc32_bytes(crc, i[23:16]); crc = crc32_bytes(crc, i[31:24]);
          crc = crc32_bytes(crc, w[7:0]);   crc = crc32_bytes(crc, w[15:8]);
          crc = crc32_bytes(crc, w[23:16]); crc = crc32_bytes(crc, w[31:24]);
        end while (mem.next(i));
      end
      return crc ^ 32'hFFFF_FFFF;
    endfunction
    function bit verify_digest(logic [31:0] crc32, int unsigned count);
      return (crc32_index_word() == crc32) && (mem.num() == count);
    endfunction

    // ---- accesses (word aligned; the agents pass the granted address) ------------------------
    function logic [31:0] read32(logic [31:0] addr);
      int wi = find_window(addr);
      if (wi >= 0) return windows[wi].h.on_read(addr);
      if (!is_mapped(addr)) begin
        unmapped_count++;
        if (!unmapped_ok) uvm_report_error("MEM_UNMAPPED", $sformatf("read of unmapped address 0x%08h", addr));
        return 32'h0;
      end
      return mem.exists(addr >> 2) ? mem[addr >> 2] : 32'h0;
    endfunction
    function void write_masked(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
      int wi = find_window(addr);
      logic [31:0] cur;
      if (wi >= 0) begin
        mmio_writes++;
        windows[wi].h.on_write(addr, data, be);
        return;
      end
      if (!is_mapped(addr)) begin
        unmapped_count++;
        if (!unmapped_ok) uvm_report_error("MEM_UNMAPPED", $sformatf("write to unmapped address 0x%08h", addr));
        return;
      end
      cur = mem.exists(addr >> 2) ? mem[addr >> 2] : 32'h0;
      for (int k = 0; k < 4; k++) if (be[k]) cur[8*k +: 8] = data[8*k +: 8];
      mem[addr >> 2] = cur;
    endfunction
    // MEM_PEEK: the stored word without side effects (no MMIO call, no unmapped accounting).
    function logic [31:0] peek_word(logic [31:0] addr);
      if (!is_mapped(addr)) return 32'h0;
      return mem.exists(addr >> 2) ? mem[addr >> 2] : 32'h0;
    endfunction
  endclass
endpackage
