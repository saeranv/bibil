"""----------------
Miru Height
----------------""" 
import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['height'] = height

if run:
    rule = [R]
else:
    rule = [copy.deepcopy(Miru)]



