"""
Bibil plain
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import copy

"""import classes"""
Pattern = sc.sticky["Pattern"]

def copy_node_lst(nlst):
    L = []
    for n in nlst:
        L.append(copy.deepcopy(n))
    return L

def make_node_lst(copy_node_in_): 
    L = []
    for node_geom in copy_node_in_:
        P = Pattern()
        n_ = P.helper_geom2node(node_geom,None,label=label_)
        L.append(n_)
    return L

def node2pattern(lst_node_):
    return lst_node_

def main(node_in_):
    ### Grid_Subdivide: (listof node) int int -> (listof node))
    node_in_ = copy_node_lst(node_in_)     
    lst_node = make_node_lst(node_in_)
    lst_node = node2pattern(lst_node)
    #lst_node = reduce(lambda s, a: s + a, split_nodes)
    return lst_node

if run and node_in!=[None] and node_in != None and node_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = main(node_in)
else:
    print 'Add inputs!'
