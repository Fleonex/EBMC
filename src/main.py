import os
import re

# Initialize global variables
input_lines = []    # List to store input lines from Verilog file
top_module = None   # Variable to store the name of the top module

# Function to prompt user for sensitive and output variables
def get_sensitive_variables():
    sensitive_variables = []
    print("Enter the names of the sensitive variables (separated by commas):")
    variables_input = input().strip()    # Get user input
    if variables_input:   # If input is not empty
        sensitive_variables = [var.strip() for var in variables_input.split(',')]   # Split input by commas and strip spaces
    
    print("Enter the names of the output variables (separated by commas):")
    output_variables_input = input().strip()    # Get user input for output variables
    output_variables = []
    if output_variables_input:     # If input is not empty
        output_variables = [var.strip() for var in output_variables_input.split(',')]   # Split input by commas and strip spaces
    
    return sensitive_variables, output_variables    # Return sensitive and output variables

# Function to read input lines from a file
def get_input_lines(input_file):
    with open(input_file, 'r') as f:
        input_lines = f.readlines()    # Read lines from file
    return input_lines

# Function to find input and output ports in Verilog code
def find_ports(input_lines):
    sensitive_vars = []     # List to store sensitive variables
    output_vars = []        # List to store output variables
    for line in input_lines:    # Iterate through each line in input lines
        if "input" in line:     # Check if line contains "input"
            sensitive_vars += re.findall(r'input\s+(?:reg|wire)?\s*\[.*?\]\s*(\w+)', line)   # Find variables in input line
        elif "output" in line:  # Check if line contains "output"
            output_vars += re.findall(r'output\s+(?:reg|wire)?\s*\[.*?\]\s*(\w+)', line)  # Find variables in output line
        
    return sensitive_vars, output_vars   # Return sensitive and output variables

# Function to duplicate variables in Verilog code
def duplicate_variables(sensitive_vars, output_vars, input_lines):
    internal_variables = []     # List to store internal variables
    duplicated_lines = []       # List to store duplicated lines
    for line in input_lines:    # Iterate through each line in input lines
        if "input" in line:     # Check if line contains "input"
            for var in sensitive_vars:     # Iterate through each sensitive variable
                if var in line:     # Check if variable is in line
                    if not line[-2] == ",":    # Check if line doesn't end with a comma
                        duplicated_lines.append(line.replace(var, f"{var}1,"))    # Append line with duplicated variable and comma
                        duplicated_lines.append(line.replace(var, f"{var}2"))     # Append line with duplicated variable
                    else:
                        duplicated_lines.append(line.replace(var, f"{var}1"))     # Append line with duplicated variable
                        duplicated_lines.append(line.replace(var, f"{var}2"))     # Append line with duplicated variable
                else:
                    duplicated_lines.append(line)   # Append original line

        elif "output" in line:  # Check if line contains "output"
            for var in output_vars:    # Iterate through each output variable
                if var in line:     # Check if variable is in line
                    if not line[-2] == ",":    # Check if line doesn't end with a comma
                        duplicated_lines.append(line.replace(var, f"{var}1,"))    # Append line with duplicated variable and comma
                        duplicated_lines.append(line.replace(var, f"{var}2"))     # Append line with duplicated variable
                    else:
                        duplicated_lines.append(line.replace(var, f"{var}1"))     # Append line with duplicated variable
                        duplicated_lines.append(line.replace(var, f"{var}2"))     # Append line with duplicated variable
                else:
                    duplicated_lines.append(line)   # Append original line

        elif "reg" in line or "wire" in line:   # Check if line contains "reg" or "wire"
            variables = re.findall(r'\[.*?\] (\w+)', line)   # Find variables in line
            internal_variables += variables    # Add variables to internal variables list
            for var in variables:   # Iterate through each variable
                pattern = rf'\b{var}\b'    # Define regex pattern for variable
                if re.search(pattern, line):    # If pattern is found in line
                    duplicated_lines.append(re.sub(pattern, f"{var}1", line))   # Replace variable with duplicated variable
                    duplicated_lines.append(re.sub(pattern, f"{var}2", line))   # Replace variable with duplicated variable
                else:
                    duplicated_lines.append(line)   # Append original line

        elif "initial" in line:     # Check if line contains "initial"
            variables = re.findall(r'initial (\w+)', line)    # Find variables in line
            for var in variables:   # Iterate through each variable
                pattern = rf'\b{var}\b'    # Define regex pattern for variable
                if re.search(pattern, line):    # If pattern is found in line
                    duplicated_lines.append(re.sub(pattern, f"{var}1", line))   # Replace variable with duplicated variable
                    duplicated_lines.append(re.sub(pattern, f"{var}2", line))   # Replace variable with duplicated variable
                else:
                    duplicated_lines.append(line)   # Append original line

        else:
            duplicated_lines.append(line)   # Append original line if none of the conditions are met

    return duplicated_lines, internal_variables    # Return duplicated lines and internal variables

# Function to modify Verilog code by duplicating variables
def modify_verilog_code(sensitive_vars, output_vars, internal_vars, modules, current_module, modified_lines):
    final_verilog_code = []     # List to store final Verilog code
    duplicate_variables = sensitive_vars + output_vars + internal_vars    # Combine sensitive, output, and internal variables
    if_beginning = False    # Flag to track if inside an 'if' block
    ifelse_block = []       # List to store lines inside an 'if-else' block
    module_instantiation = False    # Flag to track module instantiation
    instances = []         # List to store module instances
    module_name = None     # Variable to store module name
    duplicated_module_lines = []    # List to store lines of duplicated module

    for line in modified_lines:    # Iterate through each line in modified lines
        if "if" in line:     # Check if line contains "if"
            line1 = line
            for var in duplicate_variables:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)    # Replace variables with duplicated variables
            final_verilog_code.append(line1)   # Append modified line to final Verilog code

            line2 = line
            for var in duplicate_variables:
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)    # Replace variables with duplicated variables
            ifelse_block.append(line2)   # Append modified line to if-else block
            if_beginning = True     # Set flag to True
            continue

        if "end" in line and if_beginning:   # Check if line contains "end" and inside an 'if' block
            if "else" in line:    # Check if line contains "else"
                final_verilog_code.append(line)    # Append line to final Verilog code
                ifelse_block.append(line)    # Append line to if-else block
                continue
            else:
                ifelse_block.append(line)    # Append line to if-else block
                final_verilog_code.append(line)    # Append line to final Verilog code
                if_beginning = False    # Reset flag
                final_verilog_code += ifelse_block   # Append if-else block to final Verilog code
                ifelse_block = []    # Reset if-else block
                continue
        
        if if_beginning:    # Check if inside an 'if' block
            line1 = line
            for var in duplicate_variables:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)    # Replace variables with duplicated variables
            final_verilog_code.append(line1)   # Append modified line to final Verilog code
            line2 = line
            for var in duplicate_variables:
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)    # Replace variables with duplicated variables
            ifelse_block.append(line2)   # Append modified line to if-else block
            continue

            
        if not if_beginning and ifelse_block:    # Check if not inside an 'if' block and if-else block is not empty
            final_verilog_code += ifelse_block    # Append if-else block to final Verilog code
            ifelse_block = []    # Reset if-else block
        
        for module in modules:    # Iterate through each module
            if module in line and module != current_module:   # Check if module is in line and not the current module
                instance = re.findall(rf'{module}\s+(\w+)', line)   # Find instance of module
                if instance:    # If instance is found
                    instances.append(instance[0])   # Append instance to list
                print(f"Module found: {module}")
                module_name = module    # Store module name
                module_instantiation = True   # Set flag
                break
        
        if module_instantiation:    # Check if module instantiation
            print("Module instantiation found")
            new_lines = duplicate_module(input_lines, module_name, [], [], modules)   # Duplicate module
            duplicated_module_lines = new_lines   # Store duplicated lines of module

            line1 = line
            line2 = line
            for var in duplicate_variables + instances:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)    # Replace variables with duplicated variables
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)    # Replace variables with duplicated variables
            final_verilog_code.append(line1)   # Append modified line to final Verilog code
            if line1 != line2:    # Check if lines are different
                final_verilog_code.append(line2)   # Append modified line to final Verilog code

            ports = re.findall(r'\((.*?)\)', line)[0].split(', ')   # Find ports in module instantiation line
            new_ports = ', '.join([f"{port}1, {port}2" for port in ports])    # Create new ports with duplicated names
            new_line = re.sub(f"{module_name}", f"{module_name}2", line)    # Replace module name with duplicated name
            new_line = re.sub(r'\((.*?)\)', f"({new_ports})", new_line)    # Replace ports with duplicated names

            final_verilog_code.append(new_line)    # Append modified line to final Verilog code
            module_instantiation = False    # Reset flag
            continue
        

        line1 = line
        line2 = line
        for var in duplicate_variables:
            line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)    # Replace variables with duplicated variables
            line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)    # Replace variables with duplicated variables
        final_verilog_code.append(line1)   # Append modified line to final Verilog code
        if line1 != line2:    # Check if lines are different
            final_verilog_code.append(line2)   # Append modified line to final Verilog code

    return final_verilog_code, duplicated_module_lines    # Return final Verilog code and duplicated module lines

# Function to add assertions to Verilog code
def add_assertions(sensitive_vars, output_vars, internal_vars, modified_lines):
    final_verilog_code = []     # List to store final Verilog code
    duplicate_variables = sensitive_vars + output_vars + internal_vars    # Combine sensitive, output, and internal variables
    endmodule_line_index = None    # Variable to store index of 'endmodule' line
    
    for index, line in enumerate(modified_lines):    # Iterate through each line and its index in modified lines
        if "endmodule" in line:     # Check if line contains "endmodule"
            endmodule_line_index = index    # Store index of 'endmodule' line
            break
    
    for index, line in enumerate(modified_lines):    # Iterate through each line and its index in modified lines
        if index == endmodule_line_index:    # Check if index is equal to 'endmodule' line index
            for var in duplicate_variables:
                final_verilog_code.append(f"\tassert property ({var}1 == {var}2); \n")    # Append assertion for duplicated variables
        final_verilog_code.append(line)    # Append line to final Verilog code
    
    return final_verilog_code    # Return final Verilog code

# Function to duplicate a module in Verilog code
def duplicate_module(input_lines, module, sensitive_vars, output_vars, modules, duplicated_modules=set()):
    if module in duplicated_modules:    # Check if module is already duplicated
        return input_lines    # Return input lines

    duplicated_modules.add(module)    # Add module to set of duplicated modules
    print("Working on the module... ", module)
    top_module_lines= []    # List to store lines of top module
    module_found = False    # Flag to track if module is found
    for line in input_lines:    # Iterate through each line in input lines
        if module in line and not module_found:    # Check if module is in line and module is not found yet
            module_found = True    # Set flag to True
            top_module_lines.append(line)    # Append line to top module lines
        elif module_found and "endmodule" not in line:    # Check if module is found and line is not 'endmodule'
            top_module_lines.append(line)    # Append line to top module lines
        elif module_found and "endmodule" in line:    # Check if module is found and line is 'endmodule'
            top_module_lines.append(line)    # Append line to top module lines
            break
    
    if not sensitive_vars and not output_vars:    # Check if sensitive and output variables are not provided
        sensitive_vars, output_vars = find_ports(top_module_lines)    # Find sensitive and output variables in top module

    print(f"Sensitive variables: {sensitive_vars}")    # Print sensitive variables
    print(f"Output variables: {output_vars}")    # Print output variables

    modified_lines, internal_vars = duplicate_variables(sensitive_vars, output_vars, top_module_lines)    # Duplicate variables in top module

    final_verilog_code, duplicate_module_lines = modify_verilog_code(sensitive_vars, output_vars, internal_vars, modules, module, modified_lines)    # Modify Verilog code by duplicating variables

    final_verilog_code = add_assertions(sensitive_vars, output_vars, internal_vars, final_verilog_code)    # Add assertions to Verilog code

    if module != top_module:    # Check if module is not top module
        final_verilog_code = [re.sub(rf'\b{module}\b', f"{module}2", line) for line in final_verilog_code]    # Replace module name with duplicated name
        final_verilog_code.append("\n")    # Append newline character
        final_verilog_code += top_module_lines    # Append top module lines
    
    if duplicate_module_lines and module == top_module:    # Check if duplicated module lines exist and module is top module
        final_verilog_code = duplicate_module_lines + ["\n"] + final_verilog_code    # Append duplicated module lines and newline character

    return final_verilog_code    # Return final Verilog code

# Function to duplicate variables in Verilog code
def duplicate(input_lines, sensitive_vars, output_vars):
    modules = []    # List to store module names
    for line in input_lines:    # Iterate through each line in input lines
        if "module" in line:    # Check if line contains "module"
            module_name = re.findall(r'module (\w+)', line)    # Find module name in line
            if module_name:    # If module name is found
                modules.append(module_name[0])    # Append module name to list of modules

    print(f"Modules in the input file: {modules}")    # Print modules in input file
    
    final_verilog_code = duplicate_module(input_lines, top_module, sensitive_vars, output_vars, modules)    # Duplicate top module
    
    return final_verilog_code    # Return final Verilog code

# Main function
def main():
    global input_lines    # Declare global variable
    global top_module    # Declare global variable

    input_file = input("Enter the input Verilog file path: ")    # Prompt user for input file path
    output_file = input("Enter the output Verilog file path: ")    # Prompt user for output file path
    top_module = input("Enter the name of the top module: ")    # Prompt user for top module name
    sensitive_vars, output_vars = get_sensitive_variables()    # Get sensitive and output variables from user

    
    input_lines = get_input_lines(input_file)    # Read input lines from file

    final_verilog_code = duplicate(input_lines, sensitive_vars, output_vars)    # Duplicate variables in Verilog code

    with open(output_file, 'w') as f:    # Open output file in write mode
        f.writelines(final_verilog_code)    # Write final Verilog code to file

    print(f"Modified Verilog code written to {output_file}")    # Print message

if __name__ == "__main__":
    main()    # Call main function
