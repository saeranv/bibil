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
        ret = "nd__" + str(self.grammar.type['label']) \
        + "__%s__%s" % (self.grammar.type['grammar'],self.depth)
        #for child in self.loc:
        #    ret += child.__repr__()
        return ret
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
    
    def backtrack_tree(self,foo,accumulate=False):
        def helper_backtrack_tree(node,foo,accumulator,acc_):
            #tail-end recursion backtracking
            if node == None:
                if acc_ == False:
                    return None
                else:
                    return accumulator    
            elif foo(node):
                if acc_ == False:
                    return node
                else:
                    accumulator.append(node) 
            return helper_backtrack_tree(node.parent,foo,accumulator,acc_)
        """ 
        Backtracks tree, applies function argument to every
        node until parent. Use tail-end recurusion
        """
        return helper_backtrack_tree(self,foo,[],accumulate)
            
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
