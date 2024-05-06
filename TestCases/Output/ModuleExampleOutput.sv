module ope2(
    input [31:0] x1,
    input [31:0] x2,
    output reg [31:0] y1,
    output reg [31:0] y2
);
    initial y1 = 0;
    initial y2 = 0;

    wire [31:0] result1, result2;
    assign result1 = x1 + 5;
    assign result2 = x2 + 5;

    always@(posedge clk) begin
        y1 <= result1;
        y2 <= result2;
    end

    //assertions

    assert property (y1 == y2);
    assert property (x1 == x2);

endmodule

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
    input [31:0] h1,
    input [31:0] h2,
    output reg [31:0] v1,
    output reg [31:0] v2
);

    wire [31:0] res1, res2;

    initial v1 = 0;
    initial v2 = 0;

    ope u1 (h1, res1);
    ope u2 (h2, res2);

    ope2 uu1 (h1, h2, res1, res2);

    always@(posedge clk) begin
        v1 <= res;
        v2 <= res;
    end

    //assertions

    assert property (h1 == h2); 
	assert property (v1 == v2); 
	assert property (res1 == res2);
endmodule
        

