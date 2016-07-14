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
'separate':False,'separation_dist':0.,'dim':30.,\
'height':False,'height_node':''} 
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
TO['height'],TO['height_node'] = 10., 'valid_seperation' 

"""----------------
Default Tower and Podium 
----------------""" 

TT = copy.deepcopy(PD_) 
TT['type_id'] = 'type_tower'
#TT['div_num'],TT['div_deg'],TT['div_cut'] = 1, 0, 7.
#TT['solartype'] = 3
#TT['solartime'], TT['solarht'] = 11.5, 15.
##TT['height'] = 12.
TT['stepback_node'] = -1
TT['stepback_base'] = [(13.5,3.)]#[(13.5,18.)]
TT['stepback_tower'] = []
## Change this to separate PD so it can be reused for base
TT['separate'] = True 
TT['separation_dist'] = 25.
TT['dim'] = 27.4 
TT['height'],TT['height_node'] = 'bula', 'valid_seperation' 

#TT['court'], TT['court_width'],TT['court_node'] = 1, 30., 0
#TT['terrace']=1.5
#TT['terrace_node']=-1

grammar_lst.extend([TO,TT])

if reset==False:
    import rhinoscriptsyntax as rs
    sc.sticky['type_tower'] = TT
    sc.sticky['override'] = []
    sc.sticky['envelope'] = []
    sc.sticky['existing_tower'] = []
    for envelope_node in envelope_srfs:
        envelope_node = rs.coercebrep(envelope_node)
        sc.sticky['envelope'].append(envelope_node)
    for sepcrv in override_sep:
        sepcrv = rs.coercecurve(sepcrv)
        sc.sticky['existing_tower'].append(sepcrv)
        
    """
    for overnode in override_crvs:
        # Find better way to do this.
        for grammar in grammar_lst:
            label=grammar['type_id']
            if label in overnode.data.type['label']:
                overnode.data.type['grammar'] = grammar
                sc.sticky['override'].append(overnode)
    """        
    o = True
    
