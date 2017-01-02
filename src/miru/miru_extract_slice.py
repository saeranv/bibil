"""----------------
Miru Extract Slice
----------------""" 
import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


if run:

    rule = DataTree[object]()
    rule_ = [['extract_slice', True],\
             ['grammar_key','extract_slice'],\
             ['extract_slice_height', slice_height],\
             ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
        
else:
    rule = []



