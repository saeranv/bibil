"""----------------
Miru Court
----------------""" 
import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['court'] = 1
R['court_width'] = podium_depth
R['court_node'] = -1#node_depth
R['court_slice']= True

if run:
    rule = [R]
else:
    rule = [copy.deepcopy(Miru)]
    
    
