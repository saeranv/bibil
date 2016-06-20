"""
Created on Jun 19, 2016
author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import copy

"""import classes"""
Shape_3D = sc.sticky["Shape_3D"]
Fabric_Grammar = sc.sticky["Fabric_Grammar"]
Fabric_Tree = sc.sticky["Fabric_Tree"]

def make_node_lst(copy_lot_in_): 
    for lot_node in copy_lot_in_:
        if rs.IsCurve(lot_node):
            lot_curve = rs.CopyObject(lot_node)
            lot_curve = rs.coercecurve(lot_curve)
            lot_node = rs.AddPlanarSrf(lot_node)[0]
        lot_shape = Shape_3D(lot_node)
        if int(lot_shape.z_dist) == 0:
            lot_shape.op_extrude(6.)
        lot_grammar = Fabric_Grammar([],lot_shape,0)
        lot_grammar.label = label
        lot_grammar.type["label"] = label
        lot_node = Fabric_Tree(lot_grammar,parent=None,depth=0)
        setback_line_ = map(lambda l: rs.coercecurve(l),setback_line)
        lot_grammar.type["setback_reference_line"] = setback_line_
        yield lot_node
        
        
def split_node_lst(node_lst_):
    for lot_node in node_lst_:
        axis_,dist_,saxis_,sdist_ = lot_node.data.shape.get_long_short_axis()
        if flip_axis: axis_ = saxis_
        lot_node.data.shape.convert_rc()
        lot_node.make_tree_3D("subdivide_depth",depth,axis=axis_,cut_width=street_dim)
        #lot_node.make_tree_3D("subdivide_depth_same",depth,axis=axis_,cut_width=street_dim)
        #lot_node.make_tree_3D("subdivide_dim",(18,18),axis=axis_,random_tol=0,cut_width=street_dim)
        yield lot_node.traverse_tree(lambda n:n,internal=False)
        
def main(lot_in_):
    ### Grid_Subdivide: (listof node) int int -> (listof node))
    ### Purpose: This component consumes a list of node lots and two int and 
    ###generates a list of mutated nodes, with the lots subdivided according
    ###to the int int dimensions.     
    
    lst_node = make_node_lst(lot_in_)
    split_nodes = split_node_lst(lst_node)
    generator = reduce(lambda s, a: s + a, split_nodes)
    return generator

if run and lot_in!=[None]:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    geo_out = main(lot_in)
else:
    print 'Add inputs!'