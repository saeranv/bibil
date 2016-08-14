"""
Bibil plain
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import copy

"""import classes"""
Pattern = sc.sticky["Pattern"]

def make_node_lst(copy_lot_in_): 
    L = []
    for lot_geom in copy_lot_in_:
        P = Pattern()
        n_ = P.helper_geom2node(lot_geom,None,label=label_)
        L.append(n_)
    return L
    
def split_node_lst(node_lst_):
    for lot_node in node_lst_:
        P = Pattern()
        axis_ = "NS"
        #debug.extend(lot_node.data.shape.bbpts)
        lot_node.data.shape.convert_rc()
        P.pattern_divide(lot_node,"subdivide_depth",depth,axis=axis_,cut_width=street_dim,flip=flip_axis)
        #P.pattern_divide(lot_node,"subdivide_depth_same",depth,axis=axis_,cut_width=street_dim,flip=flip_axis)
        #lot_node.make_tree_3D(lot_node,"subdivide_dim",(18,18),axis=axis_,random_tol=0,cut_width=street_dim)
        yield lot_node.traverse_tree(lambda n:n,internal=False)
        
def copy_node_lst(nlst):
    L = []
    for n in nlst:
        L.append(copy.deepcopy(n))
    return L

def solver_test(nlst_):
    P = Pattern()
    dist_lst = [10,30]
    del_lst = [10]
    for n_ in nlst_:
        #P.pattern_divide(n_,"subdivide_depth",1,axis="NS",cut_width=6.)
        childlst = n_.traverse_tree(lambda n:n,internal=False)
        for n__ in childlst:
            P.pattern_court(n__,-1,10.,0,0,False,slice=True) 
            #P.pattern_separate_by_dist(n__,dist_lst,del_lst) 
            
    return nlst_               
               
        
def main(lot_in_):
    ### Grid_Subdivide: (listof node) int int -> (listof node))
    ### Purpose: This component consumes a list of node lots and two int and 
    ###generates a list of mutated nodes, with the lots subdivided according
    ###to the int int dimensions.
    lot_in_ = copy_node_lst(lot_in_)     
    lst_node = make_node_lst(lot_in_)
    split_nodes = split_node_lst(lst_node)
    generator = reduce(lambda s, a: s + a, split_nodes)
    generator = solver_test(generator)
    return generator

if run and lot_in!=[None] and lot_in != None and lot_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = main(lot_in)
else:
    print 'Add inputs!'
