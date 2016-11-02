"""
Trinco UI
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
Bula = sc.sticky["Bula"]
Miru = sc.sticky["Miru"]


def node2grammar(lst_node_,rule_in_,label_):
    def helper_type2node(copy_node_,type_):
        #type: list of (dictionary of typology parameters)
        copytype = copy.deepcopy(type_)
        copy_node_.grammar.type.update(copytype)
        return copy_node_
    def helper_generate_node(node_geom,label_in_): 
        #if node
        if type(T) == type(node_geom):
            childn = G.helper_clone_node(node_geom,parent_node=node_geom,label=label_in_)
            node_geom.loc.append(child_n)  
        else:
            n_ = G.helper_geom2node(node_geom,label=label_in_)
        return n_
    ## Purpose: Input list of nodes, applies type
    ## Applies pattern based on types
    ## outputs node
    G = Grammar()
    T = Tree()
    L = []
    for i,node_ in enumerate(lst_node_):
        ## Everytime we add a rule, we clone a node. 
        ## Every rule mutates the node, or creates child nodes.
        child_node_ = helper_generate_node(node_,label_)
        ## Apply type to node
        child_node_ = helper_type2node(child_node_,rule_in_)
        ## Apply pattern
        if True:#try:
            node_out_ = main_grammar(child_node_)
            RhinoApp.Wait() 
        #yield node_out_
        L.extend(node_out_)
        #except Exception as e:
        #    print "Error @ Pattern.main_pattern"
    return L

def main_grammar(node):
    #move this back to grammar?
    G = Grammar()
    ## Check geometry
    gb = node.shape.geom
    if node.shape.is_guid(gb): node.shape.geom = rs.coercebrep(gb)
    PD = node.grammar.type
               
    temp_node = node
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
        G.set_bula_point(temp_node,PD)
    elif PD['meta_tree'] == True:
        G.meta_tree(temp_node,PD)
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
    lst_childs = temp_node.traverse_tree(lambda n:n,internal=False)
    return lst_childs
    
def insert_rule_dict(rule_tree_):
    #Purpose: Extract rules from tree insert nest list of rule dictionaries
    B = Bula()
    
    #Convert tree to flat list
    flat_lst = B.ghtree2nestlist(rule_tree_,nest=False)
    
    #Convert flat list to nested list of typology rules
    nest_rdict = []
    rdict = copy.deepcopy(Miru)
    for parselst in flat_lst:
        if parselst[0] != 'end_rule':
            miru_key,miru_val = parselst[0],parselst[1]
            rdict[miru_key] = miru_val  
        else:
            nest_rdict.append(rdict)
            rdict = copy.deepcopy(Miru)
    #Test
    #for i in nest_rdict:
    #    print 'bula', i['bula']
    #    print 'bula', i['bula_value_lst'][0]
    #    print '---'
    
    return nest_rdict
    
def main(node_in_,rule_in_,label__):
    def helper_main_recurse(lst_node_,rule_lst):
        #print rule_lst
        if rule_lst == []:
            return lst_node_
        else:
            rule_ = rule_lst.pop(0)
            #apply rule to current list of nodes, get child lists flat
            lst_node_leaves = node2grammar(lst_node_,rule_)
            return helper_main_recurse(lst_node_leaves,rule_lst,label__)
    
    #prep rules
    nested_rule_dict = insert_rule_dict(rule_in_)
    #recursively create a child node derived from parent and apply a grammar rule           
    lst_node_out = helper_main_recurse(node_in_,nested_rule_dict)

    return lst_node_out


node_in = filter(lambda n: n!=None,node_in)
if run and node_in != []:
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = main(node_in,rule_in,label_)
else:
    print 'Add inputs!'
