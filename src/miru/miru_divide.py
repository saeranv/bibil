"""----------------
Miru Divide
----------------""" 

import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:
    if len(divide_num) < 2:
        divide_num = divide_num[0]
    
    rule = DataTree[object]()
    rule_ = [\
    ['divide', True],\
    ['div_num',divide_num],\
    ['div_deg', 0.],\
    ['div_cut', divide_cut],\
    ['div_ratio', divide_ratio],\
    ['div_type', divide_type],\
    ['axis', axis],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
    