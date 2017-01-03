"""----------------
Miru Height
----------------""" 
import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


if run:
    if height_ref: height=True
    rule = DataTree[object]()
    rule_ = [['height',height],\
             ['grammar_key','height'],\
             ['height_randomize',randomize],\
             ['height_ref',height_ref],\
             ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
        
else:
    rule = []



