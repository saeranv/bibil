"""----------------
Miru Court
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['court'] = True
R['court_width'] = podium_depth
R['court_node'] = -1#node_depth
R['court_slice']= True
R['court_ref'] = rs.coercegeometry(parent_ref)

if run:
    rule = [R]
else:
    rule = [copy.deepcopy(Miru)]
    
    
