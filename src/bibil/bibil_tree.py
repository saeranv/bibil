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
    def __init__(self,data,loc=None,parent=None,sib=None,depth=0):
        self.data = data
        self.data.node = self
        self.data.shape.node = self
        if loc is None: loc = []
        self.loc = loc
        self.parent = parent
        self.sib = sib
        self.depth = depth
        self.root_index = None
        
    def __repr__(self):
        """ http://cbio.ufs.ac.za/live_docs/nbn_tut/trees.html """
        ret = "nd:%s" % (self.depth)#"   "*self.depth+"depth:%s\n" % (self.depth)
        #for child in self.loc:
        #    ret += child.__repr__()
        return ret
    ## def lookup
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
    
    def get_node_by_depth(self,d):
        root = self.get_root()
        lob = root.traverse_tree(lambda n:n.depth==d)
        lon = root.traverse_tree(lambda n:n)
        L = []
        for n,b in zip(lon,lob):
            if b==True: L.append(n) 
        return L
    
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
