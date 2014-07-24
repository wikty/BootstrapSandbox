import os
import collections

from placeholder import regexp

def _find_extend(content):
    extend = regexp['extend'].search(content)
    if not extend:
        return
    extend = {
        'filename': extend.groupdict()['filename'],
        'start': extend.start(),
        'end': extend.end()
    }
    return extend

def find_all_blocks(content):
    blocks = []
    for block in regexp['block'].finditer(content):
        blocks.append({
            'block': block.groupdict()['blockname'],
            'start': block.start(),
            'end': block.end()
        })
        blocks.extend(find_all_blocks(block.groupdict()['subcontent']))
    return blocks

def get_extend_tree(current_file, terminal_file):
    current_file = os.path.abspath(current_file)
    terminal_file = os.path.abspath(terminal_file)
    extend_dict = collections.OrderedDict()
    if not os.path.isfile(current_file):
        print('------> File *%s* does not exist!!!' % current_file)
        print('------> You must specify a start point')
        return
    if not os.path.isfile(terminal_file):
        print('------> File *%s* does not exist!!!' % terminal_file)
        print('------> You must specify a end point')
    current = current_file
    
    with open(terminal_file, 'r') as f:
        content = ''.join(f.readlines())
    term_blocks = find_all_blocks(content)
    
    while True:
        with open(current, 'r') as f:
            content = ''.join(f.readlines())
        extend = _find_extend(content)
        blocks = find_all_blocks(content)
        if not extend:
            print('------> Error, The End Point Is Not *%s*' % terminal_file)
            if extend_dict:
                print('------> Trace: ' + '->'.join(extend_dict.keys()))
            return
        extend_file = os.path.abspath(extend['filename'])
        if not os.path.isfile(extend_file):
            print('------> Error, Find A Invalid Extend Filename *%s* In File: *%s*' % (extend['filename'], current))
            if extend_dict:
                print('------> Trace: ' + '->'.join(extend_dict.keys()))
            return
        extend_dict[current] = {
            'extend': {
                'start': extend['start'],
                'end': extend['end'],
                'filename': extend_file
            },
            'blocks': blocks
        }
        current = extend_file
        if current in extend_dict.keys():
            print('------> Error, Circle Extend')
            print('------> Trace: ' + '->'.join(extend_dict.keys()))
            return
        if current == terminal_file:
            extend_dict[terminal_file] = {
                'pos': None,
                'blocks': term_blocks
            }
            return extend_dict
