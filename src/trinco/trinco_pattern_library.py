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
'separate':False,'separation_dist':0.,'dim':0.,\
'height':False,'height_node':''} 

"""----------------
TOWER ----------------""" 
TT = copy.deepcopy(PD_) 
TT['type_id'] = 'type_block'
#TT['div_num'],TT['div_deg'],TT['div_cut'] = 1, 0, 7.
TT['court'], TT['court_width'],TT['court_node'] = 1, 30.4,0.#39.4, 0
TT['court_slice'] = True

"""--------------------------------"""
if True:
    sc.sticky['type_block'] = TT
    o = True 
    #Rhino.RhinoApp.Wait()

