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

def apply_param_dictionary(copy_node_in_):
    copy_node_in_ = list(copy_node_in_)
    LN = []
    if True:#try:
        
        for i,node in enumerate(copy_node_in_):
            #copy_PD = deepcopy(blank_param_dict)
            #pd = get_param_dictionary(node,copy_PD)
            pd = node.data.type
            noderoot = node.get_root()
            noderoot.traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
            #noderoot.data.type.get('setback_reference_line')
            #debug.append(noderoot.data.shape.geom)
            
            s = node.data.shape
            if pd['axis']:
                s.cplane = s.get_cplane_vector(s.geom,pd['axis']) 

            try:
                P = Pattern()
                tempnode = P.apply_pattern(node,pd)
                RhinoApp.Wait()
                tempnode.traverse_tree(lambda n: n.data.shape.convert_rc('3d'),internal=False)
                lon = tempnode.traverse_tree(lambda n: n,internal=False)
            except Exception as e:
                print "Error @ Pattern.apply_pattern"
                print str(e)
                lon = node.traverse_tree(lambda n:n,internal=False)
            for i,n in enumerate(lon):
                n.data.type_id = node.data.type['type_id']

            
            lon = filter(lambda n: n!=None, lon)
            #yield leaves
            LN.extend(lon)
            #"""
        return LN    
    
def main(node_in_lst_):
    def helper_main_copy(nlst):
        for n in nlst:
            yield deepcopy(n)
    copy_node_in = helper_main_copy(node_in_lst_)
    
    try:
        gen_nodes = apply_param_dictionary(copy_node_in)
        #generator = reduce(lambda s, a: s + a, gen_nodes)
        return gen_nodes
    except Exception as e:
        print e
    
if run and node_in_lst!=[None] and node_in_lst!=[]:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    EnableRedraw(False)
    geo_out_lst = main(node_in_lst)
    EnableRedraw(True)
