"""----------------
Miru Meta Tree
----------------""" 
import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['meta_tree'] = True
R['meta_insert'] = insert
R['meta_node'] = node
R['meta_relation'] = relation

if run:
    rule = [R]
else:
    rule = [copy.deepcopy(Miru)]