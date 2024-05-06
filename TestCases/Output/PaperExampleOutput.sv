module main(
    input [31:0] x,
    input [31:0] y,
    input [31:0] z,
    input [31:0] h1,
    input [31:0] h2,
    input reset,
    input clk,
    output reg [31:0] out1,
    output reg [31:0] out2
);

    reg [31:0] a1, b1, c1;
    reg [31:0] a2, b2, c2;

    initial    a1 = 0;
    initial    b1 = 0;
    initial    c1 = 0;
    initial    a2 = 0;
    initial    b2 = 0;
    initial    c2 = 0;
    initial    out1 = 0;
    initial    out2 = 0;

    always @(posedge clk or posedge reset) begin

        if (h1 > 0) begin
            b1 <= x - y;
            c1 <= x + y;
            a1 <= b1 - c1;
        end else begin
            b1 <= x - y;
            a1 <= b1 + z;
        end

        if (h2 > 0) begin
            b2 <= x - y;
            c2 <= x + y;
            a2 <= b2 - c2;
        end else begin
            b2 <= x - y;
            a2 <= b2 + z;
        end

        out1 <= a1 + b1 + c1;
        out2 <= a2 + b2 + c2;

    end

    assert property (a1 == a2);
    assert property (b1 == b2);
    assert property (c1 == c2);
    assert property (out1 == out2);

endmodule
