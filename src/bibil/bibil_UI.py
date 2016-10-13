"""
Bibil plain
"""

import rhinoscriptsyntax as rs
import Rhino as rc
from Rhino import RhinoApp
import scriptcontext as sc
import copy

## Import classes
Shape = sc.sticky["Shape"]
Tree = sc.sticky["Tree"] 
Grammar = sc.sticky["Grammar"]

def copy_node_lst(nlst):
    L = []
    for n in nlst:
        #L.append(copy.deepcopy(n))
        yield copy.deepcopy(n)

def make_node_lst(copy_node_in_,parent_node_=None): 
    #L = []
    G = Grammar()
    T = Tree()
    
    for node_geom in copy_node_in_:
        if type(T) == type(node_geom):
            n_ = node_geom
        else:
            n_ = G.helper_geom2node(node_geom,parent_node_,label=label_)
        yield n_
        #L.append(n_)
        #return L

def node2grammar(lst_node_,rule_in_):
    def type2node(copy_node_,type_):
        #type: list of (dictionary of typology parameters)
        copytype = copy.deepcopy(type_)
        copy_node_.grammar.type.update(copytype)
        return copy_node_
    ## Purpose: Input list of nodes, applies type
    ## Applies pattern based on types
    ## outputs node    
    G = Grammar()
    #NL = []
    for node_ in lst_node_:
        ## Apply type to node
        node_ = type2node(node_,rule_in_)
        ## Apply pattern
        if True:#try:
            node_out_ = G.main_pattern(node_)
            nlst = node_out_.traverse_tree(lambda n:n,internal=False)
            #NL.extend(nlst)
            RhinoApp.Wait() 
        yield nlst
        #except Exception as e:
        #    print "Error @ Pattern.main_pattern"
        #return NL

def main(node_in_,rule_in_):
    def helper_main_recurse(lst_node_,rule_lst):
        #print rule_lst
        if rule_lst == []:
            return lst_node_
        else:
            rule_ = rule_lst.pop(0)
            lst_node_ = node2grammar(lst_node_,rule_)
            lst_node_ = reduce(lambda x,y:x+y,lst_node_)
            return helper_main_recurse(lst_node_,rule_lst)
                
    #prep nodes
    node_in_ = copy_node_lst(node_in_)
    lst_node = make_node_lst(node_in_)
    
    #apply patterns           
    lst_node = helper_main_recurse(lst_node,rule_in_)
    return lst_node

node_in = filter(lambda n: n!=None,node_in)
rule_in = filter(lambda n: n!=None,rule_in)
if run and node_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = main(node_in,rule_in)
else:
    print 'Add inputs!'
