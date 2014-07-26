import os
import sys
import string

from config import *
from utils import get_extend_dict, find_all_blocks, _convert_dict_to_tree


def help():
    t = string.Template('''
    Usage:
        python ${main} ${options} ${args}
    ''')
    
    helptext = t.substitute({'main': 'testbox.py',
                             'options': '',
                             'args': '[file...]'
    })
    
    arg = sys.argv[1]
    if not os.path.isfile(os.path.join(WORKING_DIR, arg)):
        return helptext

def main():
    helptext = help()
    if helptext:
        print(helptext)
        return
    
    with open(BASE_FILE, 'r') as f:
        base_content = ''.join(f.readlines())
        base_blocks = find_all_blocks(base_content)
    
    for input_file in sys.argv[1:]:
        if not input_file.startswith(WORKING_DIR):
            input_file = os.path.join(WORKING_DIR, input_file)
        if not os.path.isfile(input_file):
            print('')
            print('------> File *%s* does not exist!!!' % input_file)
        else:
            generated_file = os.path.join(os.path.dirname(input_file), os.path.basename(input_file)+'.gen.html')
            print('')
            print('------> File *%s* will be generated from *%s*...' % (generated_file, input_file))
        
        extend_tree = get_extend_dict(input_file, BASE_FILE)
        print(_convert_dict_to_tree(extend_tree))
        
        

if __name__ == '__main__':
    main()
