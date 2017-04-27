"""----------------
Miru Abstract BEM
----------------""" 

import copy
import scriptcontext as sc
import clr
import rhinoscriptsyntax as rs 

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:
    rule = DataTree[object]()
    bem_center = rs.coercecurve(bem_center)
    rule_ = [\
    ['abstract_bem', True],\
    ['grammar_key','abstract_bem'],\
    ['bem_tol',bem_tol],\
    ['bem_center',bem_center],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

