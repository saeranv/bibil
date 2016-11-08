"""----------------
Miru Analysis Points
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:    
    rule = DataTree[object]()
    rule_ = [\
    ['bula', True],\
    ['bula_point_lst', map(lambda pt: rs.coerce3dpoint(pt), analysis_ref)],\
    ['bula_value_lst', value_ref],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)

else:
    rule = []






