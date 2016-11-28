"""----------------
Miru Strip Faces
----------------""" 

"""
Use this component to convert faces in a brep to shape nodes.
-
Bibil     
    Args:
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
    ['strip_faces', True],\
    ['end_rule']]   
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []

