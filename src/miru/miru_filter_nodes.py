"""----------------
Miru Filter Nodes
----------------""" 
import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


if run:
    if flip==None:
        flip = False
    if tol==None:
        tol = 1.
    rule = DataTree[object]()
    rule_ = [['filter_nodes', True],\
             ['grammar_key','filter_nodes'],\
             ['dim_long',dim4long],\
             ['dim_short',dim4short],\
             ['flip',flip],\
             ['tol',tol],\
             ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
        
else:
    rule = []



