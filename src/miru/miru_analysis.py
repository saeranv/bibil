"""----------------
Miru Analysis Points
----------------""" 
import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['bula'] = True
R['bula_point_lst'] = analysis_ref
R['bula_value_lst'] = value_ref
R['bula_scale'] = scale

if run:
    rule = [R]
else:
    rule = [copy.deepcopy(Miru)]
