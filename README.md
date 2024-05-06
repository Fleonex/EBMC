# Verilog Code Duplicator

This Python script duplicates variables in Verilog code to aid in testing and verification processes. It duplicates input, output, and internal variables, as well as module instantiations and assertions.

## Table of Contents

- [Usage](#usage)
- [Other Information](#Other-Information)
- [Installation](#installation)
- [How it Works](#how-it-works)


## Usage

1. Clone the repository or download the `verilog_code_duplicator.py` script.
2. Ensure you have Python installed on your system.
3. Run the script with the following command:

python verilog_code_duplicator.py


4. Follow the prompts to provide the necessary input file path, output file path, and the name of the top module.
5. Enter the names of the sensitive variables and output variables when prompted.
6. Once the script finishes execution, check the specified output file for the modified Verilog code.

## Other Information

- To run EBMC on the duplicated code -- http://www.cprover.org/ebmc/manual/
- To access QIF command list -- ./qif -h
- For more verilog code -- https://github.com/ckarfa/FastSim/tree/master/benchmark_examples/CHStone

There is no installation required for this script. Simply download the `verilog_code_duplicator.py` file and run it with Python.

## How it Works

The script reads a Verilog file, identifies sensitive and output variables, duplicates them, and modifies the Verilog code accordingly.
