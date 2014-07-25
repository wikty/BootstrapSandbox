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
    def __init__(self, name, start, end, content_start, content_end):
        if (start>end) or (content_start>content_end):
            raise Exception('Block start should litter than end')
        self.name = name
        self.start = start
        self.end = end
        self.content_start = content_start
        self.content_end = content_end
        self.block_list = []
        self.content_list = []
    
    def __gt__(self, other):
        return (self.start > other.end) and (self.end > other.end)
    
    def __lt__(self, other):
        return (self.end < other.start) and (self.start < other.start)
    
    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end)
    
    def __contains__(self, item):
        if isinstance(item, (BlockMetaNode, ContentMetaNode)):
            return (item.start >= self.content_start) and (item.end <= self.content_end)
        else:
            raise Exception('Only BlockMetaNode and ContentMetaNode Can Operator In With BlockMetaNode')
    
    def add_block(self, block):
        if isinstance(block, BlockMetaNode):
            self.block_list.append(block)
        else:
            raise Exception('Must Add BlockMetaNode object')
    
    def add_content(self, content):
        if isinstance(content, ContentMetaNode):
            self.content_list.append(content)
        else:
            raise Exception('Must Add ContentMetaNode object')

class FileMetaNode(object):
    def __init__(self, name):
        self.name = name
        self.block_list = []

    def add_block(self, block):
        if isinstance(block, BlockMetaNode):
            self.block_list.append(block)
        else:
            raise Exception('Must Add BlockMetaNode object')
