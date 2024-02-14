
import re
from context_free_grammar import Prog

with open('test.txt', 'r') as file:
    input_lines = []
    for line in file:
        line = line.strip()
        if line != "" and (len(line) > 0 and line[0] != "#"):
            input_lines.append(line)

    print(input_lines)
    
    prog = Prog()
    prog.parse_grammar(input_lines, 0)
    
import sys

