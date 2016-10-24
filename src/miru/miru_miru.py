'''
Created on Sep 13, 2016
@author: vasanthakumars
'''

import scriptcontext as sc
import copy

Miru = \
{'child':None, 'type_id': 'type_blank',\
'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,\
'flip':False,\
'divide':False,'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,'div_type':'simple_divide',\
'court':False, 'court_width':0., 'court_ref':None,'court_slice':None,\
'stepback':False,'stepback_geom':[],'stepback_data':None,'stepback_node':-1,\
'separate':False,\
'height':False,\
'concentric_divide': False,\
'dist_lst':None,'delete_dist':None,\
'bula':False,'bula_point_lst':None,'bula_value_lst':None,'bula_scale':1.,\
'meta_tree':False,'meta_insert':None, 'meta_relation':None,'meta_node':None}
"""--------------------------------"""

if True:
    sc.sticky["Miru"] = Miru