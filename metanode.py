import functools

class ContentMetaNode(object):
    def __init__(self, content, start, end):
        self.content = content
        self.start = start
        self.end = end
        self.parent = None
    
    def __str__(self):
        return str(self.content)
    
    def __repr__(self):
        return repr(self.content)

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
        self.parent = None
    
    def __str__(self):
        return str(self.name)
    
    def __repr__(self):
        return repr(self.name)
    
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
        # return None, does not mean self and other are not siblings
        # return 1 or 2 means self and other must be siblings
        if self.end < other.start:
            # previous sibling
            return 1
        elif other.end < self.start:
            # next sibling
            return 2
    
    def must_be_sibling(self, other):
        if self.parent is None or other.parent is None:
            raise Exception('BlockMetaNode object cannot use issibling() before it has a parent block')
        if self.parent is not None and self.parent is self.other:
            if self.end < other.start:
                # previous siblings
                return 1
            elif other.end < self.start:
                # next siblings
                return 2
    
    def isdescendant(self, other):
        return other in self
    
    def parse_relationships(self, block_list):
        siblings = []
        children = []
        for block in block_list:
            if block is self:
                continue
            if self.issibling(block):
                siblings.append(block)
            elif self.isdescendant(block):
                children.append(block)
        children = [child for child in children if not [True for c in children if child in c]]
        others = [block for block in block_list if block not in children and block not in siblings]
        return (siblings, children, others)
    
    def get_next_sibling(self, block_list, parent_block):
        if (not block_list) or \
                (not parent_block) or \
                (parent_block not in block_list) or \
                (self not in block_list):
            return None
        else:
            child_blocks = [(block, i) for block, i in zip(block_list, len(block_list)) if block in parent_block]
            child_blocks = [(block, i) for block, i in child_blocks if not [True for c, j in child_blocks if block in c]]
            for block, i in child_blocks:
                if self.end < block.start:
                    return (block, i)
    
    def collect_content(self):
        content = []
        for item in sorted(self.item_list):
            if isinstance(item, ContentMetaNode):
                content.append(item.content)
            elif isinstance(item, BlockMetaNode):
                content.append(item.collect_content())
        return ''.join(content)
    
    def add_item(self, block_or_content):
        if isinstance(block_or_content, (BlockMetaNode, ContentMetaNode)):
            block_or_content.parent = self
            self.item_list.append(block_or_content)
        else:
            raise Exception('Must Add BlockMetaNode or ContentMetaNode object')
    
    def add_item_list(self, item_list):
        for item in item_list:
            self.add_item(item)
    
    def get_child_blocks(self):
        return [item for item in self.item_list if isinstance(item, BlockMetaNode)]
    
    def get_descendant_block(self, blockname):
        # get descendant or children block by name
        child_blocks = self.get_child_blocks()
        if not child_blocks:
            return
        for block in child_blocks:
            if block.name == blockname:
                return block
            else:
                return block.get_descendant_block(blockname)

class FileMetaNode(object):
    def __init__(self, name, root=False):
        self.name = name
        self.item_list = []
        self.child = None
        self.root = root
        self.namespace = []
        self.accessed_blocks = []

    def __repr__(self):
        return repr({'name': self.name,
                'namespace': self.namespace,
                'child': self.child
        })
    
    def __str__(self):
        return str({'name': self.name,
                'namespace': self.namespace,
                'child': self.child
        })
    
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
        # Block tree like this:
        #       block1             block2         # block1 and block2 are siblings
        #    /     |    \            |   \ 
        #   /      |     \           |    \
        # block3 content block4    block5 content
        #  |              |          |
        # content        content   content
        # 
        # After sort block_list(by block.start), there are some regulars:
        # 1. parent node is before children nodes
        # 2. sibling node is after previous-siblings' all children nodes
        # 3. leaf node must be content node
        # 4. content node all possible positions:
        #    {% block %}
        #       after-block-start-delimiter-content
        #       {% block %}content, recursive match{% endblock %}
        #       between in sub-blocks, ...
        #       {% block %}content, recursive match{% endblock %}
        #       before-block-end-delimiter-content
        #    {% endblock %}
        # 
        # Actually, this is a tree inorder-traversal's inverse process       

        first_blocknode = min(block_list)
        last_blocknode = max(block_list)
        
        block_list.remove(first_blocknode)  #
        
        # use a list to record history parent nodes
        trace_parent_node = []
        parent_node = first_blocknode
        trace_parent_node.append(parent_node)
        
        if not block_list:
            if first_blocknode.content_start != first_blocknode.content_end:
                first_blocknode.add_item(ContentMetaNode(**{
                    'content': content[first_blocknode.content_start:first_blocknode.content_end],
                    'start': first_blocknode.content_start,
                    'end': first_blocknode.content_end
                }))
            return [first_blocknode]
        
        for block in sorted(block_list):
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
                if block is last_blocknode:
                    if block.content_start != block.content_end:
                        block.add_item(ContentMetaNode(**{
                            'content': content[block.content_start:block.content_end],
                            'start': block.content_start,
                            'end': block.content_end
                        }))
                    last_block = trace_parent_node.pop()
                    last_parent = trace_parent_node.pop()
                    while last_parent:
                        if last_block.end != last_parent.content_end:
                            last_parent.add_item(ContentMetaNode(**{
                                'content': content[last_block.end:last_parent.content_end],
                                'start': last_block.end,
                                'end': last_parent.content_end
                            }))
                        try:
                            last_parent = trace_parent_node.pop()
                        except Exception as e:
                            last_parent = None    
            else:
                while True:
                    last_parent = trace_parent_node.pop()
                    last_parent_parent = trace_parent_node[-1]
                    if not block.issibling(first_blocknode) and block not in last_parent_parent:
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
                    elif block.issibling(first_blocknode):
                        # toplevel content(not included any block) will be ignored
                        parent_node = block
                        trace_parent_node.append(parent_node)
                        break
                    elif block in last_parent_parent:
                        if last_parent.end != block.start:
                            last_parent_parent.add_item(ContentMetaNode(**{
                                'content': content[last_parent.end:block.start],
                                'start': last_parent.end,
                                'end': block.start
                            }))
                        parent_node = block
                        trace_parent_node.append(parent_node)
                        break
        
        children = [first_blocknode]
        children.extend([block for block in block_list if first_blocknode.issibling(block)])
        return children
    
    def _generate_block_tree2(self, block_list, content):
        
        def treeize(root_blocknode, block_list, content):
            if not block_list:
                if root_blocknode.content_start != root_blocknode.content_end:
                    root_blocknode.add_item(ContentMetaNode(**{
                        'content': content[root_blocknode.content_start:root_blocknode.content_end],
                        'start': root_blocknode.content_start,
                        'end': root_blocknode.content_end
                    }))
                return
            
            for i, block in zip(range(0, len(block_list)), sorted(block_list)):
                if block not in root_blocknode:
                   return
                elif block is root_blocknode:
                    continue
                else:
                    # add *after-block-start-delimiter-content*
                    if root_blocknode.content_start != block.start:
                        root_blocknode.add_item(ContentMetaNode(**{
                            'content': content[root_blocknode.content_start:block.start],
                            'start': root_blocknode.content_start,
                            'end': block.start
                        }))
                    # add block
                    root_blocknode.add_item(block)
                    # recursive match
                    treeize(block, block_list[i:], content)
                    # between in sub-blocks
                    previous_sibling = block
                    next_sibling, j = block.get_next_sibling(block_list[i:], root_blocknode)
                    while next_sibling:
                        if previous_sibling.end != next_sibling.start:
                            root_blocknode.add_item(ContentMetaNode(**{
                                'content': content[previous_sibling.end:next_sibling.start],
                                'start': previous_sibling.end,
                                'end': next_sibling.start
                            }))
                        # add block
                        root_blocknode.add_item(next_sibling)
                        treeize(next_sibling, block_list[i+j:], content)
                        previous_sibling = next_sibling
                        next_sibling, j = previous_sibling.get_next_sibling(block_list[i:], root_blocknode)
                    else:
                        if previous_sibling.end != root_blocknode.content_end:
                            root_blocknode.add_item(ContentMetaNode(**{
                                'content': content[previous_sibling.end:root_blocknode.content_end],
                                'start': previous_sibling.end,
                                'end': root_blocknode.content_end
                            }))
        
        first_blocknode = min(block_list)
        toplevel_blocks = [(0, first_blocknode), ]
        toplevel_blocks.extend([(i, block) for i, block in zip(range(0, len(block_list)), sorted(block_list)) if first_blocknode.issibling(block)])
        for i, toplevel_block in toplevel_blocks:
            treeize(toplevel_block, block_list[i:], content)
        return [block for i, block in toplevel_blocks]
    
    def add_block_tree(self, blocknodes, content):
        # must before _generate_block_tree, because it remove blocknodes first element
        self.namespace = [block.name for block in blocknodes if isinstance(block, BlockMetaNode)]
        children = self._generate_block_tree(blocknodes, content)
        self.add_block_list(children)
    
    def get_all_blocks(self):
        return [item for item in self.item_list if isinstance(item, BlockMetaNode)]
    
    def get_all_contents(self):
        return [item for item in self.item_list if isinstance(item, ContentMetaNode)]
    
    def set_child(self, filenode):
        if isinstance(filenode, FileMetaNode):
            self.child = filenode
        else:
            raise Exception('Must Set a FileMetaNode as child')
    
    def has_block(self, blockname):
        if isinstance(blockname, BlockMetaNode):
            blockname = blockname.name
        return blockname in self.namespace
    
    def get_block(self, blockname):
        if self.has_block(blockname):
            for block in self.get_all_blocks():
                if block.name == blockname:
                    return block
                result = block.get_descendant_block(blockname)
                if result:
                    return result
    
    def search_block_in_descendant(self, blockname):
        # search child list to find a block named blockname
        if isinstance(blockname, BlockMetaNode):
            blockname = blockname.name
        child = self.child
        while child:
            if child.has_block(blockname):
                return child
            child = child.child
    
#    def remove_block(self, blockname):
#        if isinstance(blockname, BlockMetaNode):
#            blockname = blockname.name
#        if blockname in self.namespace:
#            self.namespace.remove(blockname)
#            for block in self.get_all_blocks():
#                if block.name == blockname:
#                    self.item_list.remove(block)
    
    def collect_block_content(self, blockname):
        if isinstance(blockname, BlockMetaNode):
            blockname = blockname.name
        self.accessed_blocks.append(blockname)
        childnode = self.search_block_in_descendant(blockname)
        if childnode:
            return childnode.collect_block_content(blockname)
        elif self.has_block(blockname):
            child_blocks = sorted(self.get_block(blockname).get_child_blocks())
            if child_blocks:
                return ''.join([self.collect_block_content(block.name) for block in child_blocks])
            else:
                return self.get_block(blockname).collect_content()
        else:
            return ''
