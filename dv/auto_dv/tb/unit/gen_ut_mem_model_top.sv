// gen_ut_mem_model_top: unit test of gen_mem_pkg::gen_mem_model (architecture C3.3), pure SV + UVM
// report functions, no RTL. Loads a real image produced by gen_elf2mem.py, checks the CRC-32 against
// the sidecar value passed as plusargs, the word count, reads, byte-masked writes, region mapping, the
// MMIO handler path and the unmapped-access policy (TDD transcript: dv/auto_dv/evidence/gen_tdd_mem_model.md).
//   +gen_ut_image=<path.vmem> +gen_ut_crc32=<hex> +gen_ut_words=<n> +gen_ut_entry=<hex> +gen_ut_entry_word=<hex>
module gen_ut_mem_model_top;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  import gen_mem_pkg::*;
  `include "uvm_macros.svh"

  int unsigned fails = 0;
  function automatic void check(string what, logic [63:0] got, logic [63:0] exp);
    bit ok = (got === exp);
    $display("%s %s got 0x%0h exp 0x%0h", ok ? "OK  " : "FAIL", what, got, exp);
    if (!ok) fails++;
  endfunction

  // MMIO handler that records the last store it saw and answers reads with a constant.
  class ut_handler extends gen_mmio_handler;
    logic [31:0] last_addr = '0, last_data = '0;
    logic [3:0]  last_be = '0;
    int unsigned writes = 0;
    virtual function void on_write(logic [31:0] addr, logic [31:0] data, logic [3:0] be);
      last_addr = addr; last_data = data; last_be = be; writes++;
    endfunction
    virtual function logic [31:0] on_read(logic [31:0] addr);
      return 32'hC0DE_0000 | addr[15:0];
    endfunction
  endclass

  initial begin
    string image; logic [31:0] crc, entry, entry_word; int unsigned words;
    gen_mem_model m;
    ut_handler h;
    logic [31:0] v;
    if (!$value$plusargs("gen_ut_image=%s", image)) $fatal(1, "need +gen_ut_image");
    if (!$value$plusargs("gen_ut_crc32=%h", crc)) $fatal(1, "need +gen_ut_crc32");
    if (!$value$plusargs("gen_ut_words=%d", words)) $fatal(1, "need +gen_ut_words");
    if (!$value$plusargs("gen_ut_entry=%h", entry)) $fatal(1, "need +gen_ut_entry");
    if (!$value$plusargs("gen_ut_entry_word=%h", entry_word)) $fatal(1, "need +gen_ut_entry_word");

    m = new("ut_mem");
    // 1. image load and digest (the CRC definition of gen_elf2mem.py)
    check("load_vmem word count", m.load_vmem(image), words);
    check("crc32_index_word", m.crc32_index_word(), crc);
    check("verify_digest ok", m.verify_digest(crc, words), 1);
    check("verify_digest rejects a wrong crc", m.verify_digest(crc ^ 32'h1, words), 0);
    check("verify_digest rejects a wrong count", m.verify_digest(crc, words + 1), 0);
    // 2. reads and byte-masked writes
    check("read32 entry word", m.read32(entry), entry_word);
    check("entry is mapped", m.is_mapped(entry), 1);
    m.write_masked(entry + 32'd4, 32'h1122_3344, 4'b0011);
    v = m.read32(entry + 32'd4);
    check("write_masked low half", v[15:0], 16'h3344);
    m.write_masked(entry + 32'd8, 32'hAABB_CCDD, 4'b1111);
    check("write_masked full word", m.read32(entry + 32'd8), 32'hAABB_CCDD);
    check("misaligned read is word aligned", m.read32(entry + 32'd9), 32'hAABB_CCDD);
    check("read of never-written mapped word is 0", m.read32(GEN_MM_BOOT_PAGE + GEN_MM_PROG_SIZE - 32'd4), 32'h0);
    // 3. regions
    check("DM window mapped", m.is_mapped(GEN_MM_DM_HALT), 1);
    check("MMIO page mapped", m.is_mapped(GEN_MM_SIG_ADDR), 1);
    check("hole below program unmapped", m.is_mapped(GEN_MM_BOOT_PAGE - 32'd4), 0);
    check("address 0 unmapped", m.is_mapped(32'h0), 0);
    // 4. MMIO handler path
    h = new();
    m.add_mmio(GEN_MM_SIG_ADDR, 32'h10, h);
    m.write_masked(GEN_MM_SIG_ADDR + 32'd4, 32'hDEAD_0001, 4'b1111);
    check("mmio handler saw the store", h.writes, 1);
    check("mmio handler addr", h.last_addr, GEN_MM_SIG_ADDR + 32'd4);
    check("mmio handler data", h.last_data, 32'hDEAD_0001);
    check("mmio read comes from the handler", m.read32(GEN_MM_SIG_ADDR + 32'd4), 32'hC0DE_0000 | (GEN_MM_SIG_ADDR[15:0] + 16'd4));
    // the two write_masked targets above are words the image already holds, so the count is unchanged;
    // an MMIO store must never add a RAM word
    check("mmio store did not land in RAM words", m.word_count(), words);
    // 5. unmapped policy: with unmapped_ok the access is counted and answered with 0, no error
    m.unmapped_ok = 1'b1;
    check("unmapped read returns 0", m.read32(32'h10), 32'h0);
    check("unmapped access counted", m.unmapped_count, 1);
    // 6. peek path for MEM_PEEK: same word, no side effect on counters
    check("peek_word entry", m.peek_word(entry), entry_word);
    check("peek_word unmapped is 0 without counting", m.peek_word(32'h20), 32'h0);
    check("unmapped count unchanged by peek", m.unmapped_count, 1);
    // 7. word watch (tohost / end-of-test): the store lands in RAM AND the handler sees it
    begin
      ut_handler wh = new();
      m.add_watch(entry + 32'd12, wh);
      m.write_masked(entry + 32'd12, 32'h0000_0001, 4'b1111);
      check("watched store lands in RAM", m.read32(entry + 32'd12), 32'h1);
      check("watch handler saw the store", wh.writes, 1);
      check("watch handler data", wh.last_data, 32'h1);
      m.write_masked(entry + 32'd16, 32'h5, 4'b1111);
      check("unwatched store does not call the handler", wh.writes, 1);
    end
    $display("GEN_UT_MEM_MODEL %s (%0d failures)", fails ? "FAIL" : "PASS", fails);
    $finish;
  end
endmodule
