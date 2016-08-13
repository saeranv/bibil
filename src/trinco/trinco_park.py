"""
Trinco park
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
        lot_area =  n_.data.shape.get_area()
        if lot_area >= park_max:
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

def get_park_dim(node_lst_,p_max,p_percent,ln):
    dim_x_lst = []
    setback_line_ = rs.coercecurve(ln)
    nc = setback_line_.ToNurbsCurve()
    end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
    dim_y = rs.Distance(end_pts[0],end_pts[1])
    for node_ in node_lst_:
        lot_area = node_.data.shape.get_area()
        park_area = lot_area * (p_percent/100.)
        dim_x = park_area / dim_y
        dim_x_lst.append(dim_x)
    return dim_x_lst

def make_park_brep(lst_dim_x_,park_line_,lst_node_):
    brep_lst_= []
    for n_,dx_ in zip(lst_node_,lst_dim_x_):
        P = Pattern()
        stepback_node = -1
        stepback_ref = None
        stepback_data = [(0.,dx_)]
        try:
            park_node = P.pattern_stepback(n_,step_data,stepback_node,setback_ref)
            park_nodes = park_node.traverse_tree(lambda n: n,internal=False)
            
        except Exception as e:
            print str(e)#,sys.exc_traceback.tb_lineno    
        
    return brep_lst_
def copy_node_lst(nlst):
    L = []
    for n in nlst:
        L.append(copy.deepcopy(n))
    return L
        
def main(lot_in_):
    ### Grid_Subdivide: (listof node) int int -> (listof node))
    ### Purpose: This component consumes a list of node lots and two int and 
    ###generates a list of mutated nodes, with the lots subdivided according
    ###to the int int dimensions.
    sc.sticky['seperation_offset_lst'] = []
    lot_in_ = copy_node_lst(lot_in_)     
    lst_node = make_node_lst(lot_in_)
    lst_dim_x = get_park_dim(lst_node,park_max,park_percent,park_line)
    brep_lst = make_park_brep(lst_dim_x,park_line,lst_node)
    print brep_lst
    split_nodes = split_node_lst(lst_node)
    try:
        split_nodes = reduce(lambda s, a: s + a, split_nodes)
    except: 
        pass
    return split_nodes

if run and lot_in!=[None] and lot_in != None and lot_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    park_out = main(lot_in)
else:
    print 'Add inputs!'