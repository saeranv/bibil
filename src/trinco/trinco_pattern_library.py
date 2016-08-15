"""
Created on Jun 22, 2016
@author: Saeran Vasanthakumar
"""

import copy
import scriptcontext as sc

PD_ = \
{'child':None, 'type_id': 'type_blank',\
'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,'solargap':True,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,\
'court':0, 'court_width':0., 'court_node':-1,'court_slice':None,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'terrace':0,'terrace_node':-1,\
'stepback_base':None,'stepback_tower':None, 'stepback_node':-1,\
'separate':False,\
'height':False,\
'dist_lst':None,'delete_dist':None,\
'stepback_ref':None,\
'concentric_divide': False} 

"""----------------TOWER AND PODIUM ----------------""" 
TT = copy.deepcopy(PD_) 
TT['type_id'] = 'trinco_tower_in_podium'
TT['court'], TT['court_width'],TT['court_node'] = 1, 24.5,0.#39.4, 0
TT['court_slice'] = True
TT['height'] = sc.sticky['ht_podium']
"""--------------------------------"""

"""----------------TOWER IN PARK ----------------""" 
TP = copy.deepcopy(PD_) 
TP['type_id'] = 'trinco_tower_in_park'
#TP['stepback_node'] = -1
#TP['stepback_base'] = [(0,9.)]
#TP['stepback_tower'] = []
TP['stepback_ref'] = [(0,stepback + stepback_acc)]
#TP['concentric_divide'] = True
TP['dist_lst'] = [new_separation,27.4]###
TP['delete_dist'] = [new_separation]
"""--------------------------------"""

if True:
    sc.sticky['trinco_tower_in_podium'] = TT
    sc.sticky['trinco_tower_in_park'] = TP
    o = True

