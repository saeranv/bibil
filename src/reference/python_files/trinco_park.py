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

def extrude_srf_xy(n_,split_line,split_depth):        
    ## Modified from op_split method in bibil.ahape
    split_path = rs.AddCurve([[0,0,0],[0,0,20.]],1)    
    split_surf = rs.coercebrep(rs.ExtrudeCurve(split_line,split_path))        
    
    ## Get vector pointing inwards
    ## Unitize and multiply by dimension x
    inner_norm = n_.data.shape.get_normal_point_inwards(split_line)
    inner_norm.Unitize()
    inner_norm = map(lambda v: v*split_depth,inner_norm)
    
    c = rs.AddCurve([rs.AddPoint(0,0,0),rs.AddPoint(inner_norm[0],inner_norm[1],inner_norm[2])],0)
    rc_cut = rs.ExtrudeSurface(split_surf,c)
    return rc_cut
    
def make_park_node(lst_dim_x_,park_line_,lst_node_):
    ## This function inputs the park_line, list of x dimensions
    ## and the nodes to calculate the park size
    ## and then generates the park geometry polygon
    TOL = sc.doc.ModelAbsoluteTolerance
    park_node_lst = []
    park_brep_lst,lot_brep_lst = [],[]
    
    park_line_ = rs.coercecurve(park_line_)    
    for n_,dx_ in zip(lst_node_,lst_dim_x_):
        P = Pattern()
        park_brep = extrude_srf_xy(n_,park_line_,dx_)
        park_node = P.helper_geom2node(park_brep,None)
        park_node_lst.append(park_node)   
        ## diff from lot
        park_node.data.shape.op_extrude(20.)
        park = park_node.data.shape.bottom_crv
        lot = n_.data.shape.bottom_crv
        if n_.data.shape.is_guid(park):
            park = rs.coercecurve(park)
        if n_.data.shape.is_guid(lot):
            lot = rs.coercecurve(park)
        park_brep_lst.append(park)
        lot_brep_lst.append(lot)
        
    return park_node_lst, park_brep_lst, lot_brep_lst



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
    lot_in_ = copy_node_lst(lot_in_)
    lst_node = make_node_lst(lot_in_)
    
    lst_dim_x = get_park_dim(lst_node,park_max,park_percent,park_line)
    lst_node,park,lot = make_park_node(lst_dim_x,park_line,lst_node)
    return lst_node, park, lot

if run and lot_in!=[None] and lot_in != None and lot_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    park_node,park,lot = main(lot_in)
else:
    print 'Add inputs!'
