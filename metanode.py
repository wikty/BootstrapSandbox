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
    
    def __str__(self):
        return self.name
    
    def __gt__(self, other):
        return self.start > other.start

    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end)
    
    def __contains__(self, item):
        if isinstance(item, (BlockMetaNode, ContentMetaNode)):
            return (item.start > self.content_start) and (item.end < self.content_end)
        else:
            raise Exception('Only BlockMetaNode and ContentMetaNode Can Operator In With BlockMetaNode')
    
    def issibling(self, other):
        if self.end < other.start:
            # previous siblings
            return 1
        elif self.start > other.end:
            # next siblings
            return 2
    
    def isdescendant(self, other):
        return other in self
    
    def parse_relationships(self, block_list):
        siblings = []
        children = []
        for block in block_list:
            if block == self:
                continue
            if self.issibling(block):
                siblings.append(block)
            elif self.isdescendant(block):
                children.append(block)
        children = [child for child in children if not [True for c in children if child in c]]
        others = [block for block in block_list if block not in children and block not in siblings]
        return (siblings, children, others)

    def add_item(self, block_or_content):
        if isinstance(block_or_content, (BlockMetaNode, ContentMetaNode)):
            self.item_list.append(block_or_content)
        else:
            raise Exception('Must Add BlockMetaNode or ContentMetaNode object')
    
    def add_item_list(self, item_list):
        for item in item_list:
            self.add_item(item)

class FileMetaNode(object):
    def __init__(self, name, root=False):
        self.name = name
        self.item_list = []
        self.child = None
        self.root = root
        self.namespace = []

    def add_block(self, block):
        if isinstance(block, BlockMetaNode):
            self.item_list.append(block)
        else:
            raise Exception('Must Add BlockMetaNode object')
   
    def add_block_list(self, block_list):
        for block in block_list:
            self.add_block(block)
    
    def add_content(self, content):
        if not self.root:
            raise Exception('Only Root File can Add ContentMetaNode')
        else:
            if not isinstance(content, ContentMetaNode):
                raise Exception('Must Add ContentMetaNode object')
            else:
                self.item_list.append(content)
    
    def _generate_block_tree(self, block_list, content):
        trace_parent_node = []
        first_blocknode = min(block_list)
        block_list.remove(first_blocknode)
        parent_node = first_blocknode
        trace_parent_node.append(parent_node)
        #print(block_list)
        for block in sorted(block_list):
            #print(block)
            if block in parent_node:
                if parent_node.content_start != block.start:
                    parent_node.add_item(ContentMetaNode(**{
                        'content': content[parent_node.content_start:block.start],
                        'start': parent_node.content_start,
                        'end': block.start
                    }))
                
                parent_node.add_item(block)
                parent_node = block
                trace_parent_node.append(parent_node)
            else:
#                print([b.name for b in trace_parent_node])
                print(block)
                while True:
                    last_parent = trace_parent_node.pop()
                    last_parent_parent = trace_parent_node[-1]
#                    print(last_parent_parent)
                    
                    if last_parent.content_start != last_parent.content_end:
                        last_parent.add_item(ContentMetaNode(**{
                            'content': content[last_parent.content_start:last_parent.content_end],
                            'start': last_parent.content_start,
                            'end': last_parent.content_end
                        }))
                    
                    last_parent_parent.add_item(last_parent)
                    
                    if last_parent.end != last_parent_parent.content_end:
                        last_parent_parent.add_item(ContentMetaNode(**{
                            'content': content[last_parent.end:last_parent_parent.content_end],
                            'start': last_parent.end,
                            'end': last_parent_parent.content_end
                        }))

                    if block.issibling(last_parent_parent):
                        if last_parent.end != block.start:
                            # toplevel content(not included any block) will be ignored
                            if not block.issibling(first_blocknode):
                                trace_parent_node.pop()
                                trace_parent_node[-1].add_item(ContentMetaNode(**{
                                    'content': content[last_parent.end:block.start],
                                    'start': last_parent.end,
                                    'end': block.start
                                }))
                        parend_node = block
                        trace_parent_node.append(parend_node)
                        break
        
        return [block for block in block_list if first_blocknode.issibling(block)]
    
    def add_block_tree(self, blocknodes, content):
        self.namespace = [block.name for block in blocknodes]
        children = self._generate_block_tree(blocknodes, content)
        self.add_block_list(children)
    
    def get_all_blocks(self):
        return [block for block in self.item_list if isinstance(block, BlockMetaNode)]
    
    def set_child(self, filenode):
        if isinstance(filenode, FileMetaNode):
            self.child = filenode
        else:
            raise Exception('Must Set a FileMetaNode as child')
