"""----------------
Miru Interpolate Vertical
----------------""" 
import scriptcontext as sc
import clr
Grammar = sc.sticky["Grammar"]

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:

    rule = DataTree[object]()
    rule_ = [\
    ['interpolate_vertical', True],\
    ['grammar_key','interpolate_vertical'],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
