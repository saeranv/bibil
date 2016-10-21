"""
Created on Jun 6, 2016
@author: Saeran Vasanthakumar
"""

import scriptcontext as sc

class Tree:
    """
    http://stackoverflow.com/questions/14084367/tree-in-python-recursive-children-creating
    http://www.laurentluce.com/posts/binary-search-tree-library-in-python/
    double-linked binary tree
    """
    def __init__(self,shape=None,grammar=None,loc=None,parent=None,sib=None,depth=0):
        self.shape = shape
        self.grammar = grammar
        if loc is None: loc = []
        self.loc = loc
        self.parent = parent
        self.depth = depth
        
    def __repr__(self):
        """ http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html """
        ret = "nd:%s" % (self.depth)#"   "*self.depth+"depth:%s\n" % (self.depth)
        #for child in self.loc:
        #    ret += child.__repr__()
        return ret
    
    
    """
    def increase_depth(self,amount):
        self.depth += amount
        
    def insert_node(self,node,depth):
        #NEEDS TO BE TESTED
        #Purpose: Insert node at the depth specified
        #Base case 1: equal to depth
        if self.depth == depth:
            #add as sibling
            node.parent = self.parent
            node.depth = self.depth
        elif self.depth < depth:
            #Base case 2: empty child
            if self.loc == []:
                node.parent = self
                node.depth = self.depth + 1
                self.loc.append(node)
            else: 
                self.loc[0].insert_node(node,depth)
        elif self.depth > depth:
            #Base case 3: root
            if self.parent == None:
                node.loc.append(self)
                self.parent = node
                self.traverse_tree(lambda n:n.increase_depth(node.depth),internal=True)
            else:
                self.parent.insert_node(node,depth)
       """     
            
    def delete_node(self):
        if self is not None:
            self.loc = []
            if self.parent:
                for i,pc in enumerate(self.parent.loc):
                    if self.parent.loc[i] is self: 
                        self.parent.loc.pop(i)
                        break
        self = None
        del self
        
    def get_root(self):
        if self.parent ==  None:
            return self
        else:
            return self.parent.get_root()
    
    def search_up_tree(self,foo):
        """ 
        Backtracks tree, applies function argument to every
        node until parent.
        """
        if foo(self)==True:
            return self
        elif self.parent == None:
            return False
        else:
            return self.parent.search_up_tree(foo)
    
    def backtrack_tree(self,foo):
        def helper_backtrack_tree(node,foo,accumulator):
            accumulator.append(foo(node))
            if node.parent == None:
                return accumulator
            else:
                return helper_backtrack_tree(node.parent,foo,accumulator)
        """ 
        Backtracks tree, applies function argument to every
        node until parent. Use tail-end recurusion
        """
        return helper_backtrack_tree(self,foo,[])
            
    def traverse_tree(self,foo,internal=True):
        """ 
        traverse tree, applies function argument to every
        node, leaf
        """
        if self.loc == []:
            # base case
            return [foo(self)]
        else:
            L = []
            if internal:
                L = [foo(self)] 
            for i,child in enumerate(self.loc):
                if child:
                    L += self.loc[i].traverse_tree(foo,internal)
            return L
            
if True:
    sc.sticky["Tree"] = Tree
