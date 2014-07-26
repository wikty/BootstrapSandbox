import os
import collections

from placeholder import regexp
from config import *
from metanode import FileMetaNode, BlockMetaNode, ContentMetaNode

# may be should imporve to support multiple extends
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
            #'content': content
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
                #'content': term_content
            }
            return extend_dict

def _convert_dict_to_tree(extend_dict):
    while extend_dict:
        file_data = extend_dict.popitem()
        content = file_data[1]['content']
        extend = file_data[1]['extend']
        blocks = file_data[1]['blocks']
        
        root_file_flag = True if extend is None else False
        filenode = FileMetaNode(file_data[0], root_file_flag)
        
        blocknodes = []
        for block in blocks:
            blocknode = BlockMetaNode(**block)
            blocknodes.append(blocknode)
        
        first_blocknode = min(blocknodes)
        filenode.add_block(first_blocknode)
        
        for blocknode in sorted(blocknodes):
            if first_blocknode.issiblings(blocknode):
                filenode.add_block(blocknode)
        
        
        
        if root_file_flag:
            prepend_contentnode = ContentMetaNode(content=content[0:first_blocknode.start], start=0, end=first_blocknode.start)
            append_contentnode = ContentMetaNode(content=content[first_blocknode.end:], start=first_blocknode.end, end=len(content))
            filenode.add_content(prepend_content)
            filenode.add_content(append_content)    
    
