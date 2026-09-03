module sem(input clk_i, input rst_ni, input d_i);
  reg q_a; reg q_n; reg [3:0] cnt;
  always @(posedge clk_i or negedge rst_ni) if (!rst_ni) q_a <= 1'b0; else q_a <= 1'b1;
  always @(posedge clk_i) if (d_i) q_n <= 1'b1;
  always @(posedge clk_i or negedge rst_ni) if (!rst_ni) cnt <= 4'd0; else cnt <= cnt + 4'd1;
  initial assume(!rst_ni);
  always @(posedge clk_i) if (rst_ni) assert(q_a == 1'b0 || cnt < 4'd3); // A: q_a=1 from step 2 on (sampled), cnt reveals step
  always @(posedge clk_i) if (rst_ni) assert(!q_n); // N: no-reset flop free at init
endmodule
