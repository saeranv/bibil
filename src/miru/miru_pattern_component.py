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

def apply_type(copy_node_):
    #type: list of (dictionary of typology parameters)
    L = []
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
        copytype = copy.deepcopy(type)
        node.data.type.update(copytype)
        L.append(node)
    return L
def copy_node_lst(nlst):
    L = []
    for n in nlst:
        L.append(copy.deepcopy(n))
    return L

def main(node_in_lst):
    gen_node_lst = apply_type(node_in_lst)
    node_in_lst = copy_node_lst(gen_node_lst)
    try:
        NL = []
        P = Pattern()
        #debug.append(node_in_lst[1].data.shape.geom)
        for node_in_ in node_in_lst:
            try:
                node_out_ = P.main_pattern(node_in_)
                NL.append(node_out_)
                RhinoApp.Wait() 
            except Exception as e:
                print "Error @ Pattern.main_pattern"
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
