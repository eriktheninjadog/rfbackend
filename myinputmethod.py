#myinputmethod.py

import json

jyutping_file_path = "/var/www/html/mp3/gulag.txt"


def process_jyutping_file(input_file_path):
    with open(input_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    jyutping_dict = {}
    for line in lines:
        k = line.split('\t')
        if len(k) < 2:
            continue
        jyutping = k[1].strip()
        chinese = k[0]
        if jyutping not in jyutping_dict:
            jyutping_dict[jyutping] = []
        jyutping_dict[jyutping].append(chinese)    
    return jyutping_dict

def move_lines_to_top(character, filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    matching_lines = [line for line in lines if line.startswith(character)]
    non_matching_lines = [line for line in lines if not line.startswith(character)]
    
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(matching_lines + non_matching_lines)
        
def get_jyutping_dict():
    return process_jyutping_file(jyutping_file_path)

def update_input_method_prio(character):
    move_lines_to_top(character, jyutping_file_path)


        
