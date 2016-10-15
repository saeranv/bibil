"""
Bibil UI
"""

import rhinoscriptsyntax as rs
import Rhino as rc
from Rhino import RhinoApp
import scriptcontext as sc
import copy

## Import classes
Shape = sc.sticky["Shape"]
Tree = sc.sticky["Tree"] 
Grammar = sc.sticky["Grammar"]

def copy_node_lst(nlst):
    L = []
    for n in nlst:
        #L.append(copy.deepcopy(n))
        yield copy.deepcopy(n)

def make_node_lst(copy_node_in_,parent_node_=None): 
    #L = []
    G = Grammar()
    T = Tree()
    
    for node_geom in copy_node_in_:
        if type(T) == type(node_geom):
            n_ = node_geom
        else:
            n_ = G.helper_geom2node(node_geom,parent_node_,label=label_)
        yield n_
        #L.append(n_)
        #return L

def sort_node2grammar(lst_node_,rule_in_):
    def type2node(copy_node_,type_):
        #type: list of (dictionary of typology parameters)
        copytype = copy.deepcopy(type_)
        copy_node_.grammar.type.update(copytype)
        return copy_node_
    ## Purpose: Input list of nodes, applies type
    ## Applies pattern based on types
    ## outputs node    
    #NL = []
    for node_ in lst_node_:
        ## Apply type to node
        node_ = type2node(node_,rule_in_)
        ## Apply pattern
        if True:#try:
            node_out_ = node2grammar(node_)
            nlst = node_out_.traverse_tree(lambda n:n,internal=False)
            #NL.extend(nlst)
            RhinoApp.Wait() 
        yield nlst
        #except Exception as e:
        #    print "Error @ Pattern.main_pattern"
        #return NL

def node2grammar(node):
    G = Grammar()
    ## Make a copy of the geometry
    gb = node.shape.geom
    if node.shape.is_guid(gb): gb = rs.coercebrep(gb)#gb = sc.doc.Objects.AddBrep(gb)
    geo_brep = copy.copy(gb)
    PD = node.grammar.type
    ## Make a new, fresh node
    temp_node = G.helper_geom2node(geo_brep,node)
    temp_node.grammar.type['print'] = True
                 
    if PD['divide'] == True:
        temp_node = G.divide(temp_node,PD)
    elif PD['height'] != False:
        temp_node = G.set_height(temp_node,PD['height'])
    elif PD['stepback']:
        ## Ref: TT['stepback'] = [(ht3,sb3),(ht2,sb2),(ht1,sb1)]
        temp_node = G.stepback(temp_node,PD)
    elif PD['court'] == True:
        G.court(temp_node,PD)
    elif PD['bula'] == True:
        G.bula(temp_node,PD)
    """
    These have to be rewritten
    #elif PD['separate'] == True:
    #    dist_lst = PD['dist_lst']
    #    del_lst = PD['delete_dist']
    #    temp_node = G.separate_by_dist(temp_node,dist_lst,del_lst)
    if solartype == 2: # multi_cell
        try:
            temp_node = self.solar_envelope_multi(temp_node,solartime,node.grammar,solarht)
        except Exception as e:
            print e
    if PD['concentric_divide']:
        dist_lst = PD['dist_lst']
        del_dist_lst = PD['delete_dist']
        temp_node = self.concentric_divide(temp_node,dist_lst,del_dist_lst,ROOTREF) 
    ## 1. param 1 or param 3
    solartype = PD['solartype']
    solartime = PD['solartime']
    solarht = PD['solarht']
    if solartype == 1 or solartype == 3: # uni-cell
        try:
            geo_brep = self.solar_envelope_uni(node,solartime,solarht,solartype)
        except Exception as e:
                print "Error @ solartype 1 or 3", str(e)
    """
    ## 7. Finish
    return temp_node

def main(node_in_,rule_in_):
    def helper_main_recurse(lst_node_,rule_lst):
        #print rule_lst
        if rule_lst == []:
            return lst_node_
        else:
            rule_ = rule_lst.pop(0)
            lst_node_ = sort_node2grammar(lst_node_,rule_)
            lst_node_ = reduce(lambda x,y:x+y,lst_node_)
            return helper_main_recurse(lst_node_,rule_lst)
                
    #prep nodes
    node_in_ = copy_node_lst(node_in_)
    lst_node = make_node_lst(node_in_)
    
    #apply patterns           
    lst_node = helper_main_recurse(lst_node,rule_in_)
    return lst_node

node_in = filter(lambda n: n!=None,node_in)
rule_in = filter(lambda n: n!=None,rule_in)
if run and node_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = main(node_in,rule_in)
else:
    print 'Add inputs!'
