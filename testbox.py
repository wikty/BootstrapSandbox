import os
import re
import sys

BASE_FILE_NAME = os.path.join(os.dirname(__file__), 'base.html')
EXTEND_REGEXP = re.compile(r'{%\s*extend\s+(?P<quote>["\']?)(?P<filename>[-a-zA-Z0-9_.]+)(?(quote)(?P=quote)|\s*)\s*%}')
BLOCK_REGEXP = re.complie(r'{%\s*block\s+(?P<blockname>[-a-zA-Z0-9_.]+)\s*}(?P<subcontent>.*){%\s*endblock\s*}', re.DOTALL)

def find_all_blocks(content):
    blocks = []
    for block in BLOCK_REGEXP.finditer(content):
        blocks.append(block.groupdict()['blockname'])
        blocks.extend(find_all_blocks(block.groupdict()['subcontent']))
    return blocks

def find_all_extends(content):
    extends = []
    for extend in EXTEND_REGEXP.finditer(content):
        extends.append(extend.groupdict()['filename'])
    return extends

def main():
    with open(BASE_FILE_NAME, 'r') as f:
        content = ''.join(f.readlines())
        place_holder_blocks = find_all_blocks(content)

if __name__ == '__main__':
    main()
