import copy
import scriptcontext as sc

PD_ = \
{'child':None, 'type_id': 'type_blank',\
'height':6, 'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,'solargap':True,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,\
'court':0, 'court_width':0., 'court_node':-1,'court_slice':None,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'terrace':0,'terrace_node':-1,\
'stepback':None, 'stepback_node':-1,\
'separate':False,'separation_dist':0.,\
'dim_x':30., 'dim_y':30, 'dim_z':0.} 
"""--------------------------------"""

"""----------------
TOWER ----------------""" 
TT = copy.deepcopy(PD_) 
TT['type_id'] = 'type_tower'
#TT['div_num'],TT['div_deg'],TT['div_cut'] = 1, 0, 7.
#TT['solartype'] = 3
#TT['solartime'], TT['solarht'] = 11.5, 15.
##TT['height'] = 12.
TT['stepback_node'] = -1
TT['stepback'] = [(0.,32),(12.,32+7.)]#,(24.,32+12.)]
## Change this to separate PD so it can be reused for base
TT['separate'] = True 
TT['separation_dist'] = 25.
TT['dim_x'],TT['dim_y'],TT['dim_z']=25.,25.,27. 

#TT['court'], TT['court_width'],TT['court_node'] = 1, 30., 0
#TT['terrace']=1.5
#TT['terrace_node']=-1

"""--------------------------------"""
if True:
    sc.sticky['type_tower'] = TT
    
    o = True 
    #Rhino.RhinoApp.Wait()

