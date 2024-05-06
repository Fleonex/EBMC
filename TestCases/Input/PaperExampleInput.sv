module main(
    input [31:0] x,
    input [31:0] y,
    input [31:0] z,
    input [31:0] h,
    input clk,
    output reg [31:0] out
);

    reg [31:0] a, b, c;

    initial a = 0;
    initial b = 0; // remove initial
    initial c = 0;

    always @(posedge clk or posedge reset) begin
        if (h > 0) begin
            b <= x - y;
            c <= x + y;
            a <= b - c;
        end else begin
            b <= x - y;
            a <= b + z;
        end

        out <= a + b + c;
    end

endmodule
