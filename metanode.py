import functools

class ContentMetaNode(object):
    def __init__(self, content, start, end):
        self.content = content
        self.start = start
        self.end = end


#b1 = metanode.BlockMetaNode('b1', 40, 500, 50, 400)
#b2 = metanode.BlockMetaNode('b2', 51, 399, 100, 300)
#b3 = metanode.BlockMetaNode('b3', 0, 39, 10, 20)
#b4 = metanode.BlockMetaNode('b4', 600, 1000, 620, 900)
#c = metanode.ContentMetaNode('c1', 150, 200)

@functools.total_ordering
class BlockMetaNode(object):
    def __init__(self, block, start, end, content_start, content_end):
        if (start>end) or (content_start>content_end):
            raise Exception('Block start should litter than end')
        self.name = block
        self.start = start
        self.end = end
        self.content_start = content_start
        self.content_end = content_end
        self.item_list = []
    
    def __gt__(self, other):
        return self.start > other.start

    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end)
    
    def __contains__(self, item):
        if isinstance(item, (BlockMetaNode, ContentMetaNode)):
            return (item.start >= self.content_start) and (item.end <= self.content_end)
        else:
            raise Exception('Only BlockMetaNode and ContentMetaNode Can Operator In With BlockMetaNode')
    
    def issiblings(self, other):
        if self.end < other.start:
            # previous siblings
            return 1
        elif self.start > other.end:
            # next siblings
            return 2
    
    def add_item(self, block_or_content):
        if isinstance(block_or_content, (BlockMetaNode, ContentMetaNode)):
            self.item_list.append(block_or_content)
        else:
            raise Exception('Must Add BlockMetaNode or ContentMetaNode object')

class FileMetaNode(object):
    def __init__(self, name, root=False):
        self.name = name
        self.item_list = []
        self.child = None
        self.root = root

    def add_block(self, block):
        if isinstance(block, BlockMetaNode):
            self.item_list.append(block)
        else:
            raise Exception('Must Add BlockMetaNode object')
    
    def add_content(self, content):
        if not self.root:
            raise Exception('Only Root File can Add ContentMetaNode')
        else:
            if not isinstance(content, ContentMetaNode):
                raise Exception('Must Add ContentMetaNode object')
            else:
                self.item_list.append(content)
    
    def get_all_blocks(self):
        return [block for block in self.item_list if isinstance(block, BlockMetaNode)]
    
    def set_child(self, filenode):
        if isinstance(filenode, FileMetaNode):
            self.child = filenode
        else:
            raise Exception('Must Set a FileMetaNode as child')
