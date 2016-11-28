"""
Trinco UI
"""

import scriptcontext as sc
import clr

Grammar = sc.sticky["Grammar"]
clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

if run and node_in != []:
    node_in = filter(lambda n: n!=None,node_in)
    if rule_in.BranchCount < 0.5:
        rule_in = DataTree[object]()
        rule_ = []
        for i, r in enumerate(rule_):
            rule_in.Add(r)
        
    G = Grammar()
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = G.main_UI(node_in,rule_in,label_)
else:
    print 'Add inputs!'
    
