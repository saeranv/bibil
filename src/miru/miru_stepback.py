"""----------------
Miru Stepback
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
import clr
Grammar = sc.sticky["Grammar"]

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run:
    
    #coerce geom if set as reference
    if stepback_ref:
        G = Grammar()
        type_info = G.helper_get_type(stepback_ref[0])
        if type_info == "geometry":
            stepback_ref =  map(lambda l: rs.coercecurve(l),stepback_ref)
    else:
        stepback_ref = [-1]
    rule = DataTree[object]()
    rule_ = [\
    ['stepback', True],\
    ['grammar_key','stepback'],\
    ['stepback_data', height_stepback],\
    ['stepback_ref', stepback_ref],\
    ['stepback_randomize', randomize],\
    ['stepback_tol', stepback_tol],\
    ['stepback_dir', from_rear],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
