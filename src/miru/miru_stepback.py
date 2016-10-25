"""----------------
Miru Stepback
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


if run:
    rule = DataTree[object]()
    rule_ = [\
    ['stepback', True],\
    ['stepback_node', node_ref],\
    ['stepback_data', map(lambda x,y: (x,y),height,distance)],\
    ['stepback_geom', map(lambda l: rs.coercecurve(l),geom_ref)],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
