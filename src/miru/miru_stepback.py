"""
Miru Grammar Stepback 
"""

import copy
import rhinoscriptsyntax as rs


PD_ = \
{'child':None, 'type_id': 'type_blank',\
'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,'div_type':'simple_divide',\
'court':0, 'court_width':0., 'court_node':-1,'court_slice':None,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'stepback':False,'stepback_geom':[],'stepback_data':None,'stepback_node':-1,\
'separate':False,\
'height':False,\
'concentric_divide': False,\
'dist_lst':None,'delete_dist':None}
"""--------------------------------"""

"""----------------
COURT GRAMMAR
----------------""" 
R = copy.deepcopy(PD_)
R['stepback'] = True
R['stepback_node'] = -1
R['stepback_data'] = [(3.,9.),(1.,3.)]
R['stepback_geom'] = map(lambda l: rs.coercecurve(l),geom_ref)

if True:
    rule = [R]
    
