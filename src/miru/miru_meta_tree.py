"""----------------
Miru Meta Tree
----------------""" 
import copy
import scriptcontext as sc
import clr
import random 

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:
    
    for n in node:
        if n.grammar.type['label'] == "":
            n.grammar.type['label'] = "UnlabeledRoot"
    
    rule = DataTree[object]()
    rule_ = [\
    ['meta_tree', True],\
    ['grammar_key','meta_tree'],\
    ['meta_node', node],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
    