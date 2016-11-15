"""----------------
Miru Court
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
 
if run:   
    """
    if court_ref:
        if type(court_ref) != type(int(1)):
            court_ref = rs.coercecurve(court_ref)
    else:
        parent_ref = 1
    """
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
    
    
