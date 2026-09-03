// gen_cfg_pkg: the environment configuration (knob fields rendered from gen_tb_knobs.yaml) and the
// bridge command item, in their own package so the agents (gen_agents_pkg) and the environment
// (gen_env_pkg) both see them without a cycle.
package gen_cfg_pkg;
  import uvm_pkg::*;
  import gen_tb_pkg::*;
  `include "uvm_macros.svh"

  class gen_env_cfg extends uvm_object;
    `uvm_object_utils(gen_env_cfg)
    int unsigned seed = 0;   // +ntb_random_seed, echoed in the banner next to Python's RANDOM_SEED
    `include "gen_env_cfg_knobs.svh"
    function new(string name = "gen_env_cfg");
      super.new(name);
    endfunction
  endclass

  // One bridge command as captured from gen_bridge_if; published to the agents.
  class gen_cmd_item extends uvm_sequence_item;
    logic [7:0]  kind;
    logic [31:0] arg [4];
    logic [15:0] seq;
    `uvm_object_utils_begin(gen_cmd_item)
      `uvm_field_int(kind, UVM_ALL_ON)
      `uvm_field_sarray_int(arg, UVM_ALL_ON)
      `uvm_field_int(seq, UVM_ALL_ON)
    `uvm_object_utils_end
    function new(string name = "gen_cmd_item");
      super.new(name);
    endfunction
    function string kind_name();
      case (kind)
        GEN_CMD_IRQ_SET:        return "IRQ_SET";
        GEN_CMD_IRQ_CLR:        return "IRQ_CLR";
        GEN_CMD_NMI_PULSE:      return "NMI_PULSE";
        GEN_CMD_DBG_REQ:        return "DBG_REQ";
        GEN_CMD_REGIME_SET:     return "REGIME_SET";
        GEN_CMD_KEY_MODE:       return "KEY_MODE";
        GEN_CMD_MEM_ERR_ARM:    return "MEM_ERR_ARM";
        GEN_CMD_ICACHE_ECC_ARM: return "ICACHE_ECC_ARM";
        GEN_CMD_FETCH_EN:       return "FETCH_EN";
        GEN_CMD_MEM_PEEK:       return "MEM_PEEK";
        GEN_CMD_MISC:           return "MISC";
        default:                return $sformatf("UNKNOWN(%0d)", kind);
      endcase
    endfunction
  endclass
endpackage
