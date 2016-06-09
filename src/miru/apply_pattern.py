'''
Created on Jun 9, 2016

@author: user
'''
import rhinoscriptsyntax as rs
import Rhino as rc
#import math
import random
import ghpythonlib.components as ghcomp
import ghpythonlib
import Grasshopper.Kernel as gh
import scriptcontext as sc

"""import classes"""
Shape_2D = sc.sticky["Shape_2D"]
Shape_3D = sc.sticky["Shape_3D"]
Tree = sc.sticky["Tree"]
Grammar = sc.sticky["Grammar"]
Fabric_Tree = sc.sticky["Fabric_Tree"] 
Fabric_Grammar = sc.sticky["Fabric_Grammar"] 
"""--------------------------------------------"""

from copy import deepcopy
from rhinoscriptsyntax import EnableRedraw
from Rhino import RhinoApp
Pattern = sc.sticky["Pattern"]


def get_param_dictionary(node_,PD):
    # courtyard is for the first division, NOT the subdivs!
    # set defaults
    #PD_['solartime'] = 10.5#10 + random.randint(1,3)/float(1.5)#build.lot_node.data.density.factor/20. + 9.5
    #print 'solartime', PD_['solartime']
    #print build.lot_node.data.type['type_id']
    #print build.lot_node.data.density.FAR
    TR = node_.data.type
    PD['child'] = TR['child']
    PD['type_id'] = TR['type_id']
    
    PD['height'],PD['axis'],PD['flip'] = \
    TR['height'],TR['axis'],TR['flip']
        
    PD['solartype'], PD['solarht'],PD['solartime'] = \
    TR['solartype'], TR['solarht'],TR['solartime']
            
    PD['court'], PD['court_node'],PD['court_width'] = \
    TR['court'], TR['court_node'],TR['court_width']
        
    PD['terrace'] = TR['terrace']
    PD['terrace_node'] = TR['terrace_node']
        
    PD['div_num'],PD['div_deg'],PD['div_cut'],PD['div_ratio'] = \
    TR['div_num'],TR['div_deg'],TR['div_cut'],TR['div_ratio']
        
    PD['subdiv_num'],PD['subdiv_cut'],PD['subdiv_flip'] = \
    TR['subdiv_num'],TR['subdiv_cut'],TR['subdiv_flip']
        
    PD['stepback'] = TR['stepback']
    return PD
    
def apply_param_dictionary(copy_node_in_):
    def helper_blank_param_dict():
        PD_ = \
        {'child':None,\
        'type_id':'type_blank',\
        'height':None, 'axis':None,'flip':False,\
        'solartype':0, 'solartime':0.0, 'solarht':1,'solargap':True,\
        'div_num':0, 'div_deg':0, 'div_cut':0,'div_ratio':0.,\
        'court':0, 'court_width':0., 'court_node':-1,'terrace':0,'terrace_node':-1,\
        'subdiv_num':0, 'subdiv_cut':0, 'subdiv_flip':False,'stepback':None}
        return PD_
        
    blank_param_dict = helper_blank_param_dict()
    copy_node_in_ = list(copy_node_in_)
    LN = []
    for i,node in enumerate(copy_node_in_):
        copy_PD = deepcopy(blank_param_dict)
        pd = get_param_dictionary(node,copy_PD)
        
        node.get_root().traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
        s = node.data.shape
        if pd['axis']:
            s.cplane = s.get_cplane_vector(s.geom,pd['axis']) 
        #if node.data.shape.ht > 27.:
        #    pd['solartype'] = 0 
        
        P = Pattern() 
        lon = P.apply_pattern(node,pd,0)
        RhinoApp.Wait()
        
        for i,n in enumerate(lon):
            n.data.density = node.data.density
            n.data.label = "subbuild"
            n.data.type_id = node.data.type['type_id']
            
            #try:
            #    #quick and dirty fix!
            #    if type(n.data.shape.geom) == type([]):
            #        geom1 = n.data.shape.geom[0]
            #        geom2 = n.data.shape.geom[1]
            #        n.data.shape.geom = geom1
            #        n2 = deepcopy(n)
            #        n2.data.shape.geom = geom2
            #        lon.append(n2)
            #except: pass
        
        lon = filter(lambda n: n!=None, lon)
        
        node.loc = lon
        leaves = node.traverse_tree(lambda n:n,internal=False)
        #yield leaves
        LN.append(leaves)
    return LN
def main(node_in_lst_):
    def helper_main_copy(nlst):
        for n in nlst:
            yield deepcopy(n)
    copy_node_in = helper_main_copy(node_in_lst)
    gen_nodes = apply_param_dictionary(copy_node_in)
    generator = reduce(lambda s, a: s + a, gen_nodes)
    return generator

if run and node_in_lst!=[None] and node_in_lst!=[]:
    #sc.sticky["debug"] = []
    #debug = sc.sticky["debug"]
    EnableRedraw(False)
    geo_out_lst = main(node_in_lst)
    EnableRedraw(True)
