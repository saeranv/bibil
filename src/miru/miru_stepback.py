"""----------------
Miru Stepback
----------------""" 
import copy
import scriptcontext as sc
import rhinoscriptsyntax as rs
#Miru = sc.sticky["Miru"]
#R = copy.deepcopy(Miru)

if run:
    rule = [\
    ['stepback', True],\
    ['stepback_node', node_ref],\
    ['stepback_data', map(lambda x,y: (x,y),height,distance)],\
    ['stepback_geom'], map(lambda l: rs.coercecurve(l),geom_ref)]]
else:
    rule = []
