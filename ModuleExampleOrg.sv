module ope(
    input [31:0] x,
    output reg [31:0] y
);
    initial y = 0;

    wire [31:0] result;
    assign result = x + 5;

    always@(posedge clk) begin
        y <= result;
    end
    
endmodule

module main(
    input [31:0] h,
    output reg [31:0] v
);

    wire [31:0] res;

    initial v = 0;

    ope u (h, res);

    always@(posedge clk) begin
        v <= res;
    end

    //assertions
    assert property (v == 0);
    
endmodule
        

