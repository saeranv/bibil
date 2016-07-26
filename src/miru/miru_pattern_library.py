import copy
import scriptcontext as sc

PD_ = \
{'child':None, 'type_id': 'type_blank',\
'axis':None,\
'solartype':0, 'solartime':11.0, 'solarht':0.,\
'flip':False,\
'div_num':0, 'div_deg':0, 'div_cut':0,\
'div_ratio':0.,\
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

grammar_lst = []
"""----------------
Test Override 
----------------""" 
TO = copy.deepcopy(PD_) 
TO['type_id'] = 'override_park_street'
#TO['stepback_node'] = -1
#TO['stepback_base'] = [(13.5,14.5),(0.,7.5)]
TO['stepback_tower'] = []
TO['separate'] = True 
TO['separation_dist'] = 25.
TO['dim'] = 27.4 
TO['height'] = 10.

"""----------------
Tower and Podium 
----------------""" 
TT = copy.deepcopy(PD_) 
TT['type_id'] = 'miru_tower_in_podium'
#TT['div_num'],TT['div_deg'],TT['div_cut'] = 1, 0, 7.
#TT['solartype'] = 3
#TT['solartime'], TT['solarht'] = 11.5, 15.
##TT['height'] = 12.
#TT['court'], TT['court_width'],TT['court_node'] = 1, 24.5,0.#39.4, 0
#TT['court_slice'] = True
TT['stepback_node'] = -1
TT['stepback_base'] = [(13.5,3.)]
#TT['height'] = 16.5


"""----------------
Tower and Park
----------------""" 
TP = copy.deepcopy(PD_) 
TP['type_id'] = 'miru_tower_in_park'
TP['separate'] = True 
TP['dist_lst'] = [25.,27.4]
TP['delete_dist'] = [25.]
TP['height'] = 'bula'

grammar_lst.extend([TO,TT,TP])

if reset==False:
    import rhinoscriptsyntax as rs
    sc.sticky['miru_tower_in_podium'] = TT
    sc.sticky['miru_tower_in_park'] = TP
    
    sc.sticky['override'] = []
    sc.sticky['envelope'] = []
    sc.sticky['existing_tower'] = []
    
    dpt_yonge = rs.coerce3dpoint(dpt_yonge)
    dpt_mount = rs.coerce3dpoint(dpt_mount)
    sc.sticky['bula_transit'] = [dpt_yonge,dpt_mount]
    
    for envelope_node in envelope_srfs:
        envelope_node = rs.coercebrep(envelope_node)
        sc.sticky['envelope'].append(envelope_node)
    for sepcrv in override_sep:
        sepcrv = rs.coercecurve(sepcrv)
        sc.sticky['existing_tower'].append(sepcrv)
        
    for overnode in override_crvs:
        # Find better way to do this.
        for grammar in grammar_lst:
            label=grammar['type_id']
            if label in overnode.data.type['label']:
                overnode.data.type['grammar'] = grammar
                sc.sticky['override'].append(overnode)
            
    #print sc.sticky['existing_tower']
    o = True
    
