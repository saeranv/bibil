"""
Bibil plain
"""

import rhinoscriptsyntax as rs
import Rhino as rc
from Rhino import RhinoApp
import scriptcontext as sc
import copy

## Import classes
Pattern = sc.sticky["Pattern"]
Shape_3D = sc.sticky["Shape_3D"]
Tree = sc.sticky["Tree"] 
Grammar = sc.sticky["Grammar"]

def copy_node_lst(nlst):
    L = []
    for n in nlst:
        #L.append(copy.deepcopy(n))
        yield copy.deepcopy(n)

def make_node_lst(copy_node_in_): 
    #L = []
    P = Pattern()
    ref_geom = rs.coercebrep(rs.AddBox([[0,0,0],[0,1,0],[-1,1,0],[-1,0,0],\
                                        [0,0,1],[0,1,1],[-1,1,1],[-1,0,1]]))
    ref_shape = Shape_3D(ref_geom,cplane=None)
    ref_grammar = Grammar(ref_shape)
    ref_node = Tree(ref_grammar,parent=None,depth=0)
    
    for node_geom in copy_node_in_:
        if type(ref_node) == type(node_geom):
            n_ = node_geom
        else:
            n_ = P.helper_geom2node(node_geom,None,label=label_)
        yield n_
        #L.append(n_)
        #return L

def node2pattern(lst_node_,rule_in_):
    def type2node(copy_node_,type_):
        #type: list of (dictionary of typology parameters)
        copytype = copy.deepcopy(type_)
        copy_node_.data.type.update(copytype)
        return copy_node_
    ## Purpose: Input list of nodes, applies type
    ## Applies pattern based on types
    ## outputs node    
    P = Pattern()
    #NL = []
    for node_ in lst_node_:
        ## Apply type to node
        node_ = type2node(node_,rule_in_)
        ## Apply pattern
        if True:#try:
            node_out_ = P.main_pattern(node_)
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
            lst_node_ = node2pattern(lst_node_,rule_)
            lst_node_ = reduce(lambda x,y:x+y,lst_node_)
            return helper_main_recurse(lst_node_,rule_lst)
                
    node_in_ = copy_node_lst(node_in_)     
    lst_node = make_node_lst(node_in_)
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
