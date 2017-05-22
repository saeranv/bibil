"""----------------
Miru Extract Canyon
----------------""" 

import copy
import scriptcontext as sc
import clr
import rhinoscriptsyntax as rs 

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


ghenv.Component.Message = 'Bibil'

Bula = sc.sticky['Bula']

if run:
    rule = DataTree[object]()
    canyon_center = rs.coercecurve(canyon_center)
    
    B = Bula()
    srf_data = B.ghtree2nestlist(srf_data)
    
    rule_ = [\
    ['extract_canyon', True],\
    ['grammar_key','extract_canyon'],\
    ['canyon_tol',canyon_tol],\
    ['canyon_center',canyon_center],\
    ['srf_data',srf_data],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

