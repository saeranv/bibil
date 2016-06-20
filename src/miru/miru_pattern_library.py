'''
Created on Jun 8, 2016
@author: Saeran Vasanthakumar
'''

import copy
import scriptcontext as sc
import Rhino


#type_blank_dict
PD_ = \
{'child':None, 'type_id': 'type_blank',\
'height':6, 'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,'solargap':True,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,\
'court':0, 'court_width':0., 'court_node':-1,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'stepback':None, 'stepback_node':-1}
"""--------------------------------"""

"""----------------
TOWER ----------------""" 
TT = copy.deepcopy(PD_) 
TT['type_id'] = 'type_tower'
#TT['div_num'],TT['div_deg'],TT['div_cut'] = 1, 0, 7.
#TT['solartype'] = 3
#TT['solartime'], TT['solarht'] = 11.5, 15.
##TT['height'] = 12.
TT['stepback'] = [(6.,20.),(12.,20.)]
TT['stepback_node']=-1
#TT['court'], TT['court_width'] = 1, 2.5


"""--------------------------------"""
if True:
    sc.sticky['type_tower'] = TT
    
    o = True 
    Rhino.RhinoApp.Wait()

