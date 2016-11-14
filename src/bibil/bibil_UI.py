"""
Trinco UI
"""

import scriptcontext as sc

Grammar = sc.sticky["Grammar"]

    
node_in = filter(lambda n: n!=None,node_in)
if run and node_in != []:
    G = Grammar()
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = G.main_UI(node_in,rule_in,label_)
else:
    print 'Add inputs!'
    
