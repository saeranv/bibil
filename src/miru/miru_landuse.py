"""----------------
Miru Land use
----------------""" 
import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


if run:
    rule = DataTree[object]()
    rule_ = [\
    ['landuse', True],\
    ['nodes2bucket', nodes2bucket],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
    