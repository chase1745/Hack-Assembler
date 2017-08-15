"""
*****************************************
Please run using the command:
	python3 Assembler.py <asm_file.asm>
*****************************************
"""


import sys
import re
import string

comp_binary_vals = {
      '0': '0101010',
      '1': '0111111',
     '-1': '0111010',
      'D': '0001100',
      'A': '0110000',
      'M': '1110000',
     '!D': '0001101',
     '!A': '0110001',
     '!M': '1110001',
     '-D': '0001111',
     '-A': '0110011',
     '-M': '1110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'M-1': '1110010',
    'D+A': '0000010',
    'D+M': '1000010',
    'D-A': '0010011',
    'D-M': '1010011',
    'A-D': '0000111',
    'M-D': '1000111',
    'D&A': '0000000',
    'D&M': '1000000',
    'D|A': '0010101',
    'D|M': '1010101'
}
dest_binary_vals = {
       '': '000',
      'M': '001',
      'D': '010',
     'MD': '011',
     'DM': '011',
      'A': '100',
     'AM': '101',
     'MA': '101',
     'AD': '110',
     'DA': '110',
    'AMD': '111'
}
jump_binary_vals = {
       '': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}
symbols = { # Symbol table
        'R0': '0',
        'R1': '1',
        'R2': '2',
        'R3': '3',
        'R4': '4',
        'R5': '5',
        'R6': '6',
        'R7': '7',
        'R8': '8',
        'R9': '9',
       'R10': '10',
       'R11': '11',
       'R12': '12',
       'R13': '13',
       'R14': '14',
       'R15': '15',
    'SCREEN': '16384',
       'KBD': '24576',
        'SP': '0',
       'LCL': '1',
       'ARG': '2',
      'THIS': '3',
      'THAT': '4'
}

# regex strings
comment_line = re.compile( r'\s*//.*')
empty_line = re.compile( r'\s*')
a_inst = re.compile( r'@.*')
a_num = re.compile( r'@\d+')
a_symb = re.compile( r'@.*')
a_label = re.compile( r'\s*\(\w+\)\s*')
c_inst = re.compile( r'([DAM]+\s*\=.*)|(\s*\-?\!?[AMD10]\s*[+-|&]?\s*[AMD10]?\;J\w\w)')
c_eq = re.compile( r'[DAM]+\s*\=\s*\-?\!?[AMD10]\s*[+-|&]?\s*[10AMD]?\s*')
c_dest = re.compile( r'[DAM]+\s*(?=\=)')
c_comp = re.compile( r'(?<=\=)\s*\-?\!?[AMD10]\s*[+-|&]?\s*[AMD10]?')
c_jmp = re.compile( r'D?A?M?0?1?\;J\w\w')
c_jmp_comp = re.compile( r'\s*\-?\!?[AMD10]\s*[+-|&]?\s*[AMD10]?(?=\;J)')
c_jmp_jmp = re.compile( r'(?<=\;)J\w\w')


""" Helper functions """
def get_binary(string):
    # converts an inputted string representing a decimal number to 16-bit binary 
    s_to_int = int(string)
    return format(s_to_int, '016b')

def convert_c_comp(dest, comp):
    binary = '111' + comp_binary_vals[comp] + dest_binary_vals[dest] + '000'
    return binary

def convert_c_jump(comp, jump):
    binary = '111' + comp_binary_vals[comp] + '000' + jump_binary_vals[jump]
    return binary

def strip(line):
    # removes whitespace and comments; returns line without a closing \n
    if len(line) < 1:
        return ''
    else:
        c = line[0]
        if c == "\n" or c == "/":
              return ""
        elif c == " ":
              return strip(line[1:])
        else:
              return c + strip(line[1:])



"""
##################################################
				Program begins.
##################################################
"""
if len(sys.argv) > 2:
    print("Only one file is allowed to be inputted at a time.\nProgram exiting.")
    exit()

# Create '.hack' file
in_to_out_file = re.compile( r'.*(?=\.asm)')
in_file = str(in_to_out_file.match(sys.argv[1]).group())
out = open(in_file+'.hack', 'w')

symbol_counter = 16
label_rom_address = 0

# parse lines
with open(sys.argv[1]) as f:
    for line in f:
        if comment_line.match(line):
            pass
        if empty_line.match(line):
            pass

        if a_label.search(line):
        	# A instruction - label
            label = strip(a_label.search(line).group())
            label = label.replace('(', '')
            label = label.replace(')', '')
            symbols[label] = str(label_rom_address)
        if a_inst.search(line) or c_inst.search(line):
        	# A instruction - not label
            label_rom_address += 1
with open(sys.argv[1]) as f:
    for line in f:
        if comment_line.match(line):
            pass # skip line
        if empty_line.match(line):
            pass # skip line
        if a_inst.search(line):
        	# A instruction
            if a_num.search(line):
                # a instruction with number
                a_num_binary = get_binary(strip(str(a_num.search(line).group()))[1:])
                out.write(a_num_binary + '\n')
            else:
            	# A instruction with variable or label
                label = strip(a_inst.search(line).group())
                try:
                    a_label_binary = format(int(symbols[label[1:]]), '016b')
                except KeyError:
                	# not in symbol table yet
                    symbols[label[1:]] = str(symbol_counter)
                    symbol_counter += 1
                    a_label_binary = format(int(symbols[label[1:]]), '016b')
                out.write(a_label_binary + '\n')

        if c_inst.search(line):
        	# C instruction
            if c_eq.search(line):
            	# dest = comp
                dest, comp = '', ''
                if c_dest.search(line):
                    dest = strip(str(c_dest.search(line).group()))
                    dest = ''.join(dest.split())
                if c_comp.search(line):
                    comp = strip(str(c_comp.search(line).group()))
                    comp = ''.join(comp.split())
                if dest and comp:
                    c_comp_binary = convert_c_comp(dest, comp)
                    out.write(c_comp_binary + '\n')
            if c_jmp.search(line):
            	# comp;jmp
                if c_jmp_comp.search(line):
                    comp = strip(str(c_jmp_comp.search(line).group()))
                    comp = ''.join(comp.split())
                if c_jmp_jmp.search(line):
                    jump = strip(str(c_jmp_jmp.search(line).group()))
                    jump = ''.join(jump.split())
                if comp and jump:
                    c_jump_binary = convert_c_jump(comp, jump)
                    out.write(c_jump_binary + '\n')
out.close