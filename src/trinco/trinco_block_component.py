"""
Created on Jun 19, 2016
author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

"""import classes"""
Pattern = sc.sticky["Pattern"]

def make_node_lst(copy_lot_in_,ref_block_in_): 
    L = []
    for lot_geom in copy_lot_in_:
        P = Pattern()
        p_n_ = P.helper_geom2node(ref_block_in_,None,label="block")
        n_ = P.helper_geom2node(lot_geom,p_n_,label=label_)
        setback_line_ = map(lambda l: rs.coercecurve(l),setback_line)
        p_n_.data.type["setback_reference_line"] = setback_line_
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
        
def main(lot_in_):
    ### Grid_Subdivide: (listof node) int int -> (listof node))
    ### Purpose: This component consumes a list of node lots and two int and 
    ###generates a list of mutated nodes, with the lots subdivided according
    ###to the int int dimensions.     
    lst_node = make_node_lst(lot_in_,ref_block_in)
    split_nodes = split_node_lst(lst_node)
    generator = reduce(lambda s, a: s + a, split_nodes)
    return generator

if run and lot_in!=[None]:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    geo_out = main(lot_in)
else:
    print 'Add inputs!'