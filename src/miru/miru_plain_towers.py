"""
Miru Grammar Tower
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
'stepback_base':None, 'stepback_tower':None,'stepback_node':-1,\
'separate':False,\
'height':False,\
'concentric_divide': False,\
'stepback_ref':None,\
'dist_lst':None,'delete_dist':None}
"""--------------------------------"""

"""----------------
Tower and Park
----------------""" 
TP = copy.deepcopy(PD_)
TP['separate'] = True 
TP['dist_lst'] = [20.,25.]
TP['delete_dist'] = [20.]
TP['height'] = 90.


if True:
    rule = [TP]
    
