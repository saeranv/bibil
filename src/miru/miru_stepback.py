"""----------------
Miru Stepback
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)
    
R['stepback'] = True
R['stepback_node'] = node_ref
R['stepback_data'] = map(lambda x,y: (x,y),height,distance)
R['stepback_geom'] = map(lambda l: rs.coercecurve(l),geom_ref)

if run:
    rule = [R]
else:
    rule = []
