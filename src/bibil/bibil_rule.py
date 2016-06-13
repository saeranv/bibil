"""
Created on Jun 6, 2016
author: Saeran Vasanthakumar
"""

import scriptcontext as sc
import copy

class Grammar:
    """ Parent Shape Grammar """
    def __init__(self,rule,shape,deg,axis="EW",ratio=None):
        self.rule = filter(lambda item: item!=[],rule)
        self.shape = shape
        self.label = "nothing"
        self.axis = axis
        self.ratio = ratio
        self.degree = deg
        self.daylight = None
        self.type = None
        if self.rule: 
            #handles child rules before making the labels
            #child rules only apply to mutations, if geometric children
            # are returned, they are not added back to the tree object!
            self.make_shape([self.rule.pop()])
    def make_shape_helper(self,rule_lst,child_lst,child_rule_lst):
        rule = rule_lst[0]
        rule_operation = rule[0]
        if not child_lst: child_lst = []
        if not child_rule_lst: child_rule_lst = []
        if rule_operation == "offset":
            dim,off_curve,dir = rule[1],rule[2],rule[3] 
            self.shape.op_offset(dim,off_curve,dir)
        if rule_operation == "extrude":
            ht = rule[1]
            self.shape.op_extrude(ht)
        if rule_operation == "extrude_2d":
            ht = rule[1]
            self.shape.op_extrude_2d(ht)
        if rule_operation == "move":
            self.shape.op_move(rule[1],rule[2],rule[3])
        elif rule_operation == "terrace":
            ht,base_ht = rule[1], rule[2]
            try:
                self.shape.op_terrace(ht,base_ht)
            except: print "373 terrace fail at %s %d" %(self.label,self.shape.cpt[2])
        elif rule_operation == "split":
            axis,ratio,deg,cut_width,child_rule = rule[1], rule[2], rule[3], rule[4], rule[5]
            if ratio == 0.0:
                g = rs.CopyObject(self.shape.geom)
                child_lst = [g]
            else:
                child_lst = self.shape.op_split(axis,ratio,deg,split_depth=cut_width)
            for i in child_lst:
                cr = copy.copy(child_rule)
                child_rule_lst.append([cr])
        """recurse"""
        if rule_lst[1:] == []:#base case
            return child_lst,child_rule_lst
        else:
            return self.make_shape_helper(rule_lst[1:],child_lst,child_rule_lst)
    def make_shape(self,rule):
        """ 
        make_shape: self (listof (listof rules)) -> None
        Purpose: This function consumes self, and a list of rule_lsts.
        It pops each rule, applies it, and then recursively calls the
        function again for the other rules. 
        """
        loc = self.make_shape_helper(rule[:],None,None)
        return loc
    def normalize_list(self,lov,hibound,lobound):
        """normalized_val = ( (val-min)*(hibound-lobound) )/(max-min) + lobound"""
        max_ = max(lov)
        min_ = min(lov)
        for i,v in enumerate(lov):
            lov[i] = ((hibound-lobound)*(v-min_))/(max_-min_) + lobound
        return lov

TOL = sc.doc.ModelAbsoluteTolerance
if True:
    sc.sticky["Grammar"] = Grammar