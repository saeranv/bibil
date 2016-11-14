"""----------------
Miru Land use
----------------""" 
import copy
import scriptcontext as sc
import clr

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree
                
"""            
childn = self.helper_clone_node(node_geom,parent_node=node_geom)
node_geom.loc.append(childn)
n_ = childn
else:
n_ = self.helper_geom2node(node_geom)
"""
            
if run:
    rule = DataTree[object]()
    rule_ = [\
    ['landuse', True],\
    ['landuse_zone', map(lambda n:)],\
    ['landuse_label', zone_label],\
    ['end_rule']]
    
    for i, r in enumerate(rule_):
        rule.Add(r)
else:
    rule = []
    