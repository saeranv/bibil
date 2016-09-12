"""
Miru Grammar
This module defines the shape grammar rules for specific
building typologies.  


"""

import copy
import scriptcontext as sc

PD_ = \
{'child':None, 'type_id': 'type_blank',\
'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,'div_type':'simple_divide',\
'court':0, 'court_width':0., 'court_node':-1,'court_slice':None,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'terrace':0,'terrace_node':-1,\
'stepback':False,'stepback_geom':[],'stepback_data':None,'stepback_node':-1,\
'separate':False,\
'height':False,\
'concentric_divide': False,\
'dist_lst':None,'delete_dist':None}
"""--------------------------------"""

"""----------------
DIVIDE GRAMMAR
----------------""" 
R = copy.deepcopy(PD_)
R['div_num'] = divide_num
R['div_deg'] = 0.
R['div_cut'] = divide_cut
R['div_ratio'] = divide_ratio
R['div_type'] = divide_type
R['axis'] = axis


if True:
    rule = [R]
    
