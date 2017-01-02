"""----------------
Miru Packing
----------------""" 

"""
BIBIL
-
BIBIL PACKING  
    Args:
        x_keep_omit:  X axis is the short dimension on shape. Define keep and omit dimensions separated by comma i.e. 1,2
        y_keep_omit: Y axis is the long dimension on shape. Define keep and omit dimensions separated by comma i.e. 1,2
        seperation_ref: Reference to shape node in grammar tree. Default is leaves of grammar tree.
        run: Set to True to run.
    Returns:
        rule: Resulting grammar rules, to insult into node component.
"""

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
    ['grammar_key','separate'],\
    ['x_keep_omit',x_keep_omit],\
    ['y_keep_omit',y_keep_omit],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

