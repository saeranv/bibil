"""
Created on Jun 22, 2016
@author: Saeran Vasanthakumar
"""

import copy
import scriptcontext as sc
import random 
import Rhino
import math

PD_ = \
{'child':None, 'type_id': 'type_blank',\
'height':6, 'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,'solargap':True,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,\
'court':0, 'court_width':0., 'court_node':-1,\
'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,
'terrace':0,'terrace_node':-1,\
'stepback':None, 'stepback_node':-1}
"""--------------------------------"""


"""----------------
0 BAR Y
----------------"""
TBY = copy.deepcopy(PD_)
TBY['type_id'] = 'type_bar_y'
TBY['court'], TBY['court_node'], TBY['court_width'] = 1, 0, 100.
TBY['subdiv_num'], TBY['subdiv_cut'], TBY['subdiv_flip'] = 1, 54., True
TBY['height'] = 10.


"""----------------
1 BAR X
----------------"""
TBX = copy.deepcopy(PD_)
TBX['type_id'] = 'type_bar_x'
TBX['court'], TBX['court_node'], TBX['court_width'] = 1, 0, 100.
TBX['subdiv_num'], TBX['subdiv_cut'], TBX['subdiv_flip'] = 1, 36., False
TBX['height'] = 10.



"""----------------
2 SLAB
----------------"""
TS = copy.deepcopy(PD_)
TS['type_id'] = 'type_slab'
TS['court'], TS['court_node'], TS['court_width'] = 1, 0, 18.
TS['height'] = 9.


"""----------------
3 SLAB DIV
----------------"""
TSD = copy.deepcopy(PD_)
TSD['type_id'] = 'type_slab_div'
#TSD['solartype'], TSD['solarht'] = 1, 30.
TSD['div_num'],TSD['div_deg'],TSD['div_cut'] = 1, 0, 18.
TSD['court'], TSD['court_node'],TSD['court_width'] = 1, 0, 18.
#TSD['height'] = 10.


"""----------------
4 REGULAR
----------------"""
TR = copy.deepcopy(PD_)
TR['type_id'] = 'type_regular' 
TR['height'] = 10.
TR['child'] = []
TRC = copy.deepcopy(PD_)
TRC['type_id'] = 'type_regular'
TRC['court'], TRC['court_node'], TRC['court_width'] = 1, 1, 18.
TRC['subdiv_num'], TRC['subdiv_cut'], TRC['subdiv_flip'] = 1, 0., False
TR['child'].append(TRC)

"""----------------
5 REGULAR DIV
----------------"""
TRD = copy.deepcopy(PD_)
TRD['type_id'] = 'type_regular_div'
#TRD['solartype'], TRD['solarht'] = 1, 30.
TRD['height'] = 10.
TRD['child'] = []
TRDC = copy.deepcopy(PD_)
TRDC['type_id'] = 'type_regular_div' 
TRDC['court'], TRDC['court_node'], TRDC['court_width'] = 1, -1, 18.
TRDC['subdiv_num'], TRDC['subdiv_cut'], TRDC['subdiv_flip'] = 1, 18., True
TRD['child'].append(TRDC)

"""----------------
6 REGULAR DIV DIV
----------------"""
TRDD = copy.deepcopy(PD_)
TRDD['type_id'] = 'type_regular_div_div'
TRDD['height'] = 10.
TRDD['child'] = []
TRDDC = copy.deepcopy(PD_)
TRDDC['type_id'] = 'type_regular_div_div' 
TRDDC['court'], TRDDC['court_node'], TRDDC['court_width'] = 1, -1, 18.
TRDDC['subdiv_num'], TRDDC['subdiv_cut'], TRDDC['subdiv_flip'] = 1, 18., True
TRDDC['child'] = []
TRDDCC = copy.deepcopy(PD_)
TRDDCC['type_id'] = 'type_regular_div_div' 
TRDDCC['div_num'],TRDDCC['div_deg'],TRDDCC['div_cut'] = 1, 0, 36.
TRDDC['child'].append(TRDDCC)
TRDD['child'].append(TRDDC)

"""----------------
7 COMPACT
----------------"""
TC = copy.deepcopy(PD_)
TC['type_id'] = 'type_compact'
TC['div_num'],TC['div_cut'] = 1, 0
TC['flip'] = True
TC['height'] = 10.
TC['child'] = []
TCC = copy.deepcopy(PD_)
TCC['type_id'] = 'type_compact'
TCC['court'], TCC['court_node'], TCC['court_width'] = 1, -1, 9.
TCC['subdiv_num'], TCC['subdiv_cut'], TCC['subdiv_flip'] = 1, 0., False
TC['child'].append(TCC)


"""----------------
8 COMPACT DIV
----------------"""
TCD = copy.deepcopy(PD_)
TCD['type_id'] = 'type_compact_div'
TCD['div_num'],TCD['div_cut'] = 1, 0
TCD['flip'] = True
TCD['height'] = 10.
TCD['child'] = []
TCDC = copy.deepcopy(PD_)
TCDC['type_id'] = 'type_compact'
TCDC['court'], TCDC['court_node'], TCDC['court_width'] = 1, -1, 9.
TCDC['subdiv_num'], TCDC['subdiv_cut'], TCDC['subdiv_flip'] = 1, 18., True
TCD['child'].append(TCDC)


"""--------------------------------"""
if True:
    
    sc.sticky['type_bar_y'] = TBY
    sc.sticky['type_bar_x'] = TBX
    sc.sticky['type_slab'] = TS
    sc.sticky['type_slab_div'] = TSD
    sc.sticky['type_regular'] = TR
    sc.sticky['type_regular_div'] = TRD
    sc.sticky['type_regular_div_div'] = TRDD
    sc.sticky['type_compact'] = TC
    sc.sticky['type_compact_div'] = TCD
    
    TD = True 
    Rhino.RhinoApp.Wait()

