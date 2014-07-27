import os
import sys
import string

from config import *
from utils import linearize
from server import page_server


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
    
    for input_file in sys.argv[1:]:
        if not input_file.startswith(WORKING_DIR):
            input_file = os.path.join(WORKING_DIR, input_file)
        if not os.path.isfile(input_file):
            print('')
            print('------> File *%s* does not exist!!!' % input_file)
        else:
            generated_file = os.path.join(os.path.dirname(input_file), os.path.basename(input_file)+SUFFIX_NAME)
            print('')
            print('------> File *%s* will be generated from *%s*...' % (generated_file, input_file))
            print('')
        
        content = linearize(input_file, BASE_FILE)
        with open(generated_file, 'wb+') as f:
            f.write(content)
        
        page_server.run()
        

if __name__ == '__main__':
    main()
