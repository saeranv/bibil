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
    if parent_ref:
        if type(parent_ref) != type(int(1)):
            parent_ref = rs.coercecurve(parent_ref)
    else:
        parent_ref = 1
        
    rule = [\
    ['court', True],\
    ['court_width', podium_depth],
    ['court_node', -1],
    ['court_slice', True],
    ['court_ref', parent_ref]]
else:
    rule = []
    
    
