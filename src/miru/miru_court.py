"""----------------
Miru Court
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
import clr
Grammar = sc.sticky["Grammar"]

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
 
if run:   
    if court_ref:
        G = Grammar()
        type_info = G.helper_get_type(court_ref)
        if type_info == "geometry":
            court_ref = rs.coercegeometry(court_ref)
            
    rule = DataTree[object]()
    rule_ = [\
    ['court', True],\
    ['court_width', width],\
    ['court_node', -1],\
    ['court_slice', True],\
    ['court_ref', court_ref],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
    
    
