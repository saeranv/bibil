"""
Created on Jun 9, 2016
@author: Saeran Vasanthakumar
"""
import scriptcontext as sc
import System as sys

"""--------------------------------------------"""

from copy import deepcopy
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
    except Exception as e:
        print "Error @ Pattern.apply_pattern"
        print str(e)
    return tempnode    
    
def main(node_in_lst):
    try:
        NL = []
        for node_in_ in node_in_lst:
            node_out_ = apply_param_dictionary(node_in_)
            NL.append(node_out_)
        return NL
    except Exception as e:
        print e
    
if run and node_in_lst!=[None] and node_in_lst!=[]:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    EnableRedraw(False)
    geo_out_lst = main(node_in_lst)
    EnableRedraw(True)
