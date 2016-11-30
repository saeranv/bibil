"""----------------
Miru Bucket
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
    ['bucket4shape', True],\
    ['analyze_list',True],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

