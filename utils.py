import os
import collections

from placeholder import regexp
from config import *
from metanode import FileMetaNode, BlockMetaNode, ContentMetaNode

# may be should imporve to support multiple extends
def _find_extend(content):
    extends = []
    for extend in regexp['extend'].finditer(content):
        extends.append({
            'filename': extend.groupdict()['filename'],
            'start': extend.start(),
            'end': extend.end()
        })
    return extends[0]

def _recursive_match(delimiter_regexp, content, start_delimiter, end_delimiter=''):
    results = []
    block_list = None
    for block in delimiter_regexp.finditer(content):
        if block.groupdict()[start_delimiter]:
            if block_list is None:
                block_list = []
            block_list.append(block)
        else:
            if not block_list:
                raise Exception('Before start delimiter should not display end limiter')
            else:
                blockstart = block_list.pop()
                results.append({
                    'block': blockstart.groupdict()['blockname'],
                    'start': blockstart.start(),
                    'end': block.end(),
                    'content_start': blockstart.end(),
                    'content_end': block.start()
                })
    return results

def find_all_blocks(content, base=0):
    def sorted_key(item):
        return item['start']
    
    blocks = _recursive_match(regexp['blockdelimiter'], content, 'blockstart')
    return sorted(blocks, key=sorted_key)

def get_extend_dict(current_file, terminal_file):
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
        term_content = ''.join(f.readlines())
    term_blocks = find_all_blocks(term_content)
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
        extend_file = os.path.abspath(os.path.join(WORKING_DIR, extend['filename']))
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
            'blocks': blocks,
            'content': content
        }
        current = extend_file
        if current in extend_dict.keys():
            print('------> Error, Circle Extend')
            print('------> Trace: ' + '->'.join(extend_dict.keys()))
            return
        if current == terminal_file:
            extend_dict[terminal_file] = {
                'extend': None,
                'blocks': term_blocks,
                'content': term_content
            }
            return extend_dict

def _convert_dict_to_tree(extend_dict):
    # Construct Root File Node
    file_data = extend_dict.popitem()
    if file_data[1]['extend'] is not None:
        raise Exception('Root File should not include extend')
    rootnode = FileMetaNode(file_data[0], True)
    blocknodes = [BlockMetaNode(**block) for block in file_data[1]['blocks']]
    first_blocknode = min(blocknodes)
    rootnode.add_block_tree(blocknodes, file_data[1]['content'])
    rootnode.add_content(
        ContentMetaNode(
            content=file_data[1]['content'][0:first_blocknode.start],
            start=0,
            end=first_blocknode.start
        )
    )
    rootnode.add_content(
        ContentMetaNode(
            content=file_data[1]['content'][first_blocknode.end:],
            start=first_blocknode.end,
            end=len(file_data[1]['content'])
        )
    )
    previous_filenode = rootnode
    # Construct subsequent Nodes
    while extend_dict:
        file_data = extend_dict.popitem()
        filenode = FileMetaNode(file_data[0])
        blocknodes = [BlockMetaNode(**block) for block in file_data[1]['blocks']]
        filenode.add_block_tree(blocknodes, file_data[1]['content'])  
        if previous_filenode:
            previous_filenode.set_child(filenode)
        previous_filenode = filenode
   
    return rootnode
