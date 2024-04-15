import os
import re

input_lines = []
top_module = None

def get_sensitive_variables():
    sensitive_variables = []
    print("Enter the names of the sensitive variables (separated by commas):")
    variables_input = input().strip()
    if variables_input:
        sensitive_variables = [var.strip() for var in variables_input.split(',')]
    
    print("Enter the names of the output variables (separated by commas):")
    output_variables_input = input().strip()
    output_variables = []
    if output_variables_input:
        output_variables = [var.strip() for var in output_variables_input.split(',')]
    
    return sensitive_variables, output_variables

def get_input_lines(input_file):
    with open(input_file, 'r') as f:
        input_lines = f.readlines()
    return input_lines

def find_ports(input_lines):
    sensitive_vars = []
    output_vars = []
    for line in input_lines:
        if "input" in line:
            sensitive_vars += re.findall(r'input\s+(?:reg|wire)?\s*\[.*?\]\s*(\w+)', line)
        elif "output" in line:
            output_vars += re.findall(r'output\s+(?:reg|wire)?\s*\[.*?\]\s*(\w+)', line)
        
    return sensitive_vars, output_vars


def duplicate_variables(sensitive_vars, output_vars, input_lines):
    internal_variables = []
    duplicated_lines = []
    for line in input_lines:
        if "input" in line:
            for var in sensitive_vars:
                if var in line:
                    if not line[-2] == ",":
                        duplicated_lines.append(line.replace(var, f"{var}1,"))
                        duplicated_lines.append(line.replace(var, f"{var}2"))
                    else:
                        duplicated_lines.append(line.replace(var, f"{var}1"))
                        duplicated_lines.append(line.replace(var, f"{var}2"))
                else:
                    duplicated_lines.append(line)

        elif "output" in line:
            for var in output_vars:
                if var in line:
                    if not line[-2] == ",":
                        duplicated_lines.append(line.replace(var, f"{var}1,"))
                        duplicated_lines.append(line.replace(var, f"{var}2"))
                    else:
                        duplicated_lines.append(line.replace(var, f"{var}1"))
                        duplicated_lines.append(line.replace(var, f"{var}2"))
                else:
                    duplicated_lines.append(line)

        elif "reg" in line or "wire" in line:
            variables = re.findall(r'\[.*?\] (\w+)', line)
            internal_variables += variables
            for var in variables:
                pattern = rf'\b{var}\b'
                if re.search(pattern, line):
                    duplicated_lines.append(re.sub(pattern, f"{var}1", line))
                    duplicated_lines.append(re.sub(pattern, f"{var}2", line))
                else:
                    duplicated_lines.append(line)

        elif "initial" in line:
            variables = re.findall(r'initial (\w+)', line)
            for var in variables:
                pattern = rf'\b{var}\b'
                if re.search(pattern, line):
                    duplicated_lines.append(re.sub(pattern, f"{var}1", line))
                    duplicated_lines.append(re.sub(pattern, f"{var}2", line))
                else:
                    duplicated_lines.append(line)

        else:
            duplicated_lines.append(line)

    return duplicated_lines, internal_variables

def modify_verilog_code(sensitive_vars, output_vars, internal_vars, modules, current_module, modified_lines):
    
    final_verilog_code = []
    duplicate_variables = sensitive_vars + output_vars + internal_vars
    if_beginning = False
    ifelse_block = []
    module_instantiation = False
    instances = []
    module_name = None
    duplicated_module_lines = []

    for line in modified_lines:
        if "if" in line:
            line1 = line
            for var in duplicate_variables:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)
            final_verilog_code.append(line1)

            line2 = line
            for var in duplicate_variables:
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)
            ifelse_block.append(line2)
            if_beginning = True
            continue

        if "end" in line and if_beginning:
            if "else" in line:
                final_verilog_code.append(line)
                ifelse_block.append(line)
                continue
            else:
                ifelse_block.append(line)
                final_verilog_code.append(line)
                if_beginning = False
                final_verilog_code += ifelse_block
                ifelse_block = []
                continue
        
        if if_beginning:
            line1 = line
            for var in duplicate_variables:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)
            final_verilog_code.append(line1)
            line2 = line
            for var in duplicate_variables:
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)
            ifelse_block.append(line2)
            continue

            
        if not if_beginning and ifelse_block:
            final_verilog_code += ifelse_block
            ifelse_block = []
        
        
        for module in modules:
            if module in line and module != current_module:
                instance = re.findall(rf'{module}\s+(\w+)', line)
                if instance:
                    instances.append(instance[0])
                
                print(f"Module found: {module}")
                module_name = module
                module_instantiation = True
                break
        
        if module_instantiation:
            print("Module instantiation found")
            new_lines = duplicate_module(input_lines, module_name, [], [], modules)
            duplicated_module_lines = new_lines

            line1 = line
            line2 = line
            for var in duplicate_variables + instances:
                line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)
                line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)
            final_verilog_code.append(line1)
            if line1 != line2:
                final_verilog_code.append(line2)

            ports = re.findall(r'\((.*?)\)', line)[0].split(', ')
            new_ports = ', '.join([f"{port}1, {port}2" for port in ports])
            new_line = re.sub(f"{module_name}", f"{module_name}2", line)
            new_line = re.sub(r'\((.*?)\)', f"({new_ports})", new_line)

            final_verilog_code.append(new_line)
            module_instantiation = False
            continue
        


        line1 = line
        line2 = line
        for var in duplicate_variables:
            line1 = re.sub(rf'\b{var}\b', f"{var}1", line1)
            line2 = re.sub(rf'\b{var}\b', f"{var}2", line2)
        final_verilog_code.append(line1)
        if line1 != line2:
            final_verilog_code.append(line2)
    

    return final_verilog_code, duplicated_module_lines

def add_assertions(sensitive_vars, output_vars, internal_vars, modified_lines):
    final_verilog_code = []
    duplicate_variables = sensitive_vars + output_vars + internal_vars
    endmodule_line_index = None
    
    for index, line in enumerate(modified_lines):
        if "endmodule" in line:
            endmodule_line_index = index
            break
    
    for index, line in enumerate(modified_lines):
        if index == endmodule_line_index:
            for var in duplicate_variables:
                final_verilog_code.append(f"\tassert property ({var}1 == {var}2); \n")
        final_verilog_code.append(line)
    
    return final_verilog_code



def duplicate_module(input_lines, module, sensitive_vars, output_vars, modules, duplicated_modules=set()):

    if module in duplicated_modules:
        return input_lines

    duplicated_modules.add(module) 
    print("Working on the module... ", module)
    top_module_lines= []
    module_found = False
    for line in input_lines:
        if module in line and not module_found:
            module_found = True
            top_module_lines.append(line)
        elif module_found and "endmodule" not in line:
            top_module_lines.append(line)
        elif module_found and "endmodule" in line:
            top_module_lines.append(line)
            break
    
    if not sensitive_vars and not output_vars:
        sensitive_vars, output_vars = find_ports(top_module_lines)

    print(f"Sensitive variables: {sensitive_vars}")
    print(f"Output variables: {output_vars}")

    modified_lines, internal_vars = duplicate_variables(sensitive_vars, output_vars, top_module_lines)

    final_verilog_code, duplicate_module_lines = modify_verilog_code(sensitive_vars, output_vars, internal_vars, modules, module, modified_lines)

    final_verilog_code = add_assertions(sensitive_vars, output_vars, internal_vars, final_verilog_code)

    
    if module != top_module:
        final_verilog_code = [re.sub(rf'\b{module}\b', f"{module}2", line) for line in final_verilog_code]
        final_verilog_code.append("\n")
        final_verilog_code += top_module_lines
    
    if duplicate_module_lines and module == top_module:
        final_verilog_code = duplicate_module_lines + ["\n"] + final_verilog_code

    return final_verilog_code


def duplicate(input_lines, sensitive_vars, output_vars):
    modules = []
    for line in input_lines:
        if "module" in line:
            module_name = re.findall(r'module (\w+)', line)
            if module_name:
                modules.append(module_name[0])

    print(f"Modules in the input file: {modules}")
    
    final_verilog_code = duplicate_module(input_lines, top_module, sensitive_vars, output_vars, modules)
    
    return final_verilog_code


def main():
    global input_lines
    global top_module

    input_file = input("Enter the input Verilog file path: ")
    output_file = input("Enter the output Verilog file path: ")
    top_module = input("Enter the name of the top module: ")
    sensitive_vars, output_vars = get_sensitive_variables()


    
    input_lines = get_input_lines(input_file)

    final_verilog_code = duplicate(input_lines, sensitive_vars, output_vars)

    with open(output_file, 'w') as f:
        f.writelines(final_verilog_code)

    print(f"Modified Verilog code written to {output_file}")

if __name__ == "__main__":
    main()
