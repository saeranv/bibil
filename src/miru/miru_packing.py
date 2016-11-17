"""----------------
Miru Packing
----------------""" 
import copy
import scriptcontext as sc
import clr
import random 

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:
    rule = DataTree[object]()
    rule_ = [\
    ['separate', True],\
    ['dim2keep',dim2keep],\
    ['dim2delete', dim2delete],\
    ['sep_ref', seperation_ref],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

