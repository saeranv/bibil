"""
Created on Jun 9, 2016
@author: Saeran Vasanthakumar
"""
import scriptcontext as sc
import System as sys

"""--------------------------------------------"""

import copy 
from rhinoscriptsyntax import EnableRedraw
from Rhino import RhinoApp
Pattern = sc.sticky["Pattern"]

def apply_param_dictionary(node):
    pd = node.data.type
    if pd['axis']:
        s = node.data.shape
        s.cplane = s.get_cplane_vector(s.geom,pd['axis']) 
    try:
        P = Pattern()
        tempnode = P.apply_pattern(node,pd)
        RhinoApp.Wait() 
    except Exception as e:
        print "Error @ Pattern.apply_pattern"
        print str(e)
    return tempnode    

def apply_type(copy_node_):
    #type: list of (dictionary of typology parameters)
    for node in copy_node_:
        type_label = node.get_root().data.type['label']
        if bibil == 'miru' and 'tower_in_podium' in type_label:
            type = sc.sticky['miru_tower_in_podium']
        elif bibil == 'miru' and 'tower_in_park' in type_label:
            type = sc.sticky['miru_tower_in_park']
        elif bibil=='trinco' and 'tower_in_podium' in type_label:
            type = sc.sticky['trinco_tower_in_podium']
        elif bibil=='trinco' and 'tower_in_park' in type_label:
            type = sc.sticky['trinco_tower_in_park']
        type = copy.deepcopy(type)
        node.data.type.update(type)
        node.data.label = ""
        node.data.type.update(type)
        yield node
    
def copy_node_lst(nlst,cnum):
    i = 0
    while i < cnum:
        yield copy.deepcopy(nlst[i])
        i += 1

def main(node_in_lst):
    gen_node_lst = apply_type(node_in_lst)
    node_in_lst = gen_node_lst
    try:
        NL = []
        for node_in_ in node_in_lst:
            node_out_ = apply_param_dictionary(node_in_)
            NL.append(node_out_)
        return NL
    except Exception as e:
        print e

node_in_lst = filter(lambda n: n!=None,node_in_lst)
if run and node_in_lst!=[] and node_in_lst!=None:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    EnableRedraw(False)
    geo_out_lst = main(node_in_lst)
    EnableRedraw(True)
