"""
Created on Jun 25, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math
import copy

"""
Bula takes in data points (i.e. from GIS, from manhattan distance 
analysis) and uses data to drive form generative methods i.e. height, 
setback distance, tower separation at a high degree of precision. 
Since the data points are normalized, you must set the domain extents
of the data you are working with in order to get sensible data. 
By incrementing the bula.value, you can experiment with densities, 
but the density will always be DIRECTIONALLY DRIVEN by underling point
data.
"""
class Bula:
    def __init__(self,bpt_lst=None,value_lst=None,avg_val=0.):
        #Set defaults for list types
        if bpt_lst == None:
            bpt_lst = []
        if value_lst == None:
            value_lst = []
        #Init
        self.bpt_lst = bpt_lst
        self.value_lst = value_lst
        self.avg_value = avg_val
        self.bpt_viz_lst = copy.copy(bpt_lst)
         
    def normalize_list(self,lov,hibound,lobound):
        """normalized_val = ( (val-min)*(hibound-lobound) )/(max-min) + lobound"""
        max_ = max(lov)
        min_ = min(lov)
        L = []
        
        for i,v in enumerate(lov):
            if max_-min_ > 0.:
                norm_val = ((hibound-lobound)*(v-min_))/(max_-min_) + lobound
            else: 
                norm_val = 1/float(len(lov))
            L.append(norm_val)
        return L
    def ghtree2nestlist(self,tree):
        nested_lst = []
        for i in range(tree.BranchCount):
            branchList = tree.Branch(i)
            nested_lst.append(branchList)
        return nested_lst
    def normalize_cpt_data(self,cpt_lst_):
        ## Normalize points
        cpt_lst_val = map(lambda cpt: cpt[2], cpt_lst_)
        ## temp add lowerbound for height
        norm_lst = self.normalize_list(cpt_lst_val,1.,0.)
        for i,val in enumerate(zip(norm_lst,cpt_lst_)):
            norm,cpt = val[0],val[1]
            cpt[2] = norm
            cpt_lst_[i] = cpt
        return cpt_lst_ 
    def getpoints4lot(self,lots_,cpt_,value_ref_):
        ## Loop through tree lots and add the point_nodes
        ## to each lot; returns lst of (listof points inside each lot)
        ## bpt_lst,lots: listof(listof(point data) 
        debug = sc.sticky['debug']
        lst_bpt_lst_ = []
        lst_val_lst_ = []
        for j,lot in enumerate(lots_):
            boundary = lot.shape.bottom_crv
            neighbor = []
            neighbor_val= []
            # look through all cpts from dpts and add to neighborlst
            for i,cp in enumerate(cpt_):
                """
                movedist = abs(lot.shape.cpt[2]-cp[2])
                if abs(movedist-0.0)>0.1:
                    if lot.shape.cpt[2] < cp[2]:
                        movedist *= -1
                    vec = rc.Geometry.Vector3d(0,0,movedist)
                else:
                    vec = rc.Geometry.Vector3d(0,0,0)
                if not lot.shape.is_guid(cp):
                    cp = sc.doc.Objects.AddPoint(cp)
                copy_cp = rs.CopyObject(cp,vec)
                #copy_cp = rs.coerce3dpoint() 
                """
                copy_cp = cp
                in_lot = 0
                try:
                    in_lot = int(rs.PointInPlanarClosedCurve(copy_cp,boundary,lot.shape.cplane))
                except:
                    pass
                #0 = point is outside of the curve
                #1 = point is inside of the curve
                #2 = point in on the curve
                if abs(float(in_lot) - 1.) <= 0.1:
                    neighbor.append(cp)#,datalst[i]])
                    neighbor_val.append(value_ref_[i])
                    #d = rs.AddPoint(copy_cp[0], copy_cp[1],0)
                    #debug.append(d)
            lst_bpt_lst_.append(neighbor)
            lst_val_lst_.append(neighbor_val)
        return lst_bpt_lst_,lst_val_lst_ 
    def generate_bula_point(self,shapes_,lst_bpt_lst_,lst_value_lst):
        ## Loop through shape nodes w/ bula_pts
        for i,shape_node in enumerate(shapes_):
            bpt_lst_ = lst_bpt_lst_[i]
            val_lst = lst_value_lst[i]
            avg_val = reduce(lambda x,y: x+y,val_lst)
            ## Make a bpt for each lot
            bpt = Bula(bpt_lst_,val_lst,avg_val)
            shape_node.grammar.type['bula'] = bpt
    def calculate_node_gfa(self,lots_,ref_density):
        ##It would be a lot easier to do all these additions
        ## and operations on lists with numpy!!
        ## Old obselete, will need to rwrite to reflect
        ## lot.grammar.type['bula_pt'] = lot.grammar.type['bula_data']
        ## is a single class not list of bpt classes

        ### This section recalculates density amounts to bring the 
        ### actual density in line with the reference density provided by
        ### the designer while maintaining the exponential or nonexponetial
        ### relationship between different lot FARS.
        lot_num = float(len(lots_))
        lot_area = sum(map(lambda l:l.shape.get_area(),lots_))
        sum_gfa = 0.
        for l in lots_:
            for bpt in l.grammar['bula_pt']:
                sum_gfa += bpt.value
            bula_num = len(l.grammar['bula_pt'])
            sum_gfa += 0 if bula_num < 1 else sum_gfa/float(bula_num)
        ref_gfa = ref_density * lot_area
        ## Calculate difference between reference FAR, and actual FAR
        abs_diff = abs(float(ref_gfa) - sum_gfa)
        abs_diff = abs_diff*-1 if ref_gfa < sum_gfa else abs_diff
        ## Sort lot nodes from lowest to highest FAR
        lots_.sort(key=lambda n: n.grammar.type['bula_pt'].value)
           
        ## Loop through the listof(lots)
        for i,lot in enumerate(lots_):
            ## Neighbor nodes are the fine grain Batty cells, within a lot
            ## used to derive density sim. Not surrounding neighbors. 
            ## Sort the neighbor nodes for each lot from 
            ## lowest to highest by their FAR 
            lot_num = float(len(lot.grammar.type['bula_pt']))
            lot_val = sum(map(lambda bpt: bpt.value,lot.grammar.type['bula_pt']))
            try: 
                lot_gfa = (lot_val/lot_num) * lot.shape.get_area()
                ## Calculate the actual lot FAR / actual total FAR
                ## This fixes the exponential relationship.
                proportion = lot_gfa/sum_gfa
                ## If there is more than one neighbor nodes (or batty cells)
                ## then change FAR to be: the (avg neighbor FAR)
                ## plus the proportional difference between reference and actual 
                ## FAR (abs_diff*proportion)
                if lot_num >= 1.:
                    new_lot_gfa = lot_gfa/lot_num + (abs_diff*proportion)
            except ZeroDivisionError:
                lot_gfa = 1.
                new_lot_gfa
            lot.grammar.type['lot_gfa'] = new_lot_gfa
        return lots_
    def sort_by_bula(self,lots_):
        ## Sort by Bula_data.value, from highest to lowest
        def helper_chk_bula(lot_):
            if lot_.grammar.type.has_key('bula_data'):
                bula_val = lot_.grammar.type['bula_data'].value 
            else: 
                bula_val = 0.
            return bula_val 
        #print map(lambda n: n.grammar.type['bula_data'].value,lots_)
        bula_sort = sorted(lots_,key=lambda n: helper_chk_bula(n),reverse=True)
        #print map(lambda n: n.grammar.type['bula_data'].value,bula_sort)
        return bula_sort
    def apply_formula2points(self,formula_ref_,analysis_pts_):
        #Purpose: Go through each point and add value based on formula
        formula = formula_ref_[0]
        focal_ref = formula_ref_[1]
        focal_weight = formula_ref_[2]
        value_lst = []
        
        #Set defaults
        if len(focal_weight) != len(focal_ref):
            if len(focal_weight) == 1:
                focal_weight = focal_weight * len(focal_ref)
            elif len(focal_weight) == 0:
                focal_weight = [1.] * len(focal_ref)
            else:
                print 'Correct the number of focal_weight inputs'
                
        #Create list of focal pt: list of distance
        lst_fpt_lst = []
        for i,fpt in enumerate(focal_ref):
            fpt_lst = []
            for j,apt_ in enumerate(analysis_pts_):
                dist2fpt = rs.Distance(fpt,apt_)
                fpt_lst.append(dist2fpt)
            lst_fpt_lst.append(fpt_lst)
            
        #Normalize distances according to focal weight
        norm_lst_fpt_lst = []
        for fpt_dist_lst,fwt in zip(lst_fpt_lst,focal_weight):
            norm_dist2fpt = fpt_dist_lst#self.normalize_list(fpt_dist_lst,0.,fwt)
            norm_lst_fpt_lst.append(norm_dist2fpt)
        
        #Loop through dist2fptlst for each analysis_pts and find min dist2fpt
        min_norm_dist_lst = []
        for i,apt_ in enumerate(analysis_pts_):
            dist4fpts = []
            #lstdust2fot = dist of each analysis_pt to fpt
            for lstdist2fpt in lst_fpt_lst:
                dist4fpts.append(lstdist2fpt[i])
            #Identify the fpt that is closer to the apt
            min_fpt_index = dist4fpts.index(min(dist4fpts))
            min_norm_dist = norm_lst_fpt_lst[min_fpt_index][i]
            min_norm_dist_lst.append(min_norm_dist)
        #Use min fpt w/ formula export value list
        print 'values'
        for apt_,min_norm_dist in zip(analysis_pts_,min_norm_dist_lst):
            #formula: 1/math.exp(0.1813*dist)
            #print 'f', formula
            #print 'd', min_norm_dist
            try:
                dist = (min_norm_dist/1000.)*10 #<<< convert to km * 10 for 10 min walk
                val = eval(formula)
            except ZeroDivisionError:
                val = 0.
            value_lst.append(val)
        print min(value_lst)
        print max(value_lst)
        max_bound = 150 * max(value_lst)
        min_bound = 150 * min(value_lst)
        print max_bound, min_bound
        value_lst = map(lambda n: n*100,value_lst)
        #value_lst = self.normalize_list(value_lst,max_bound,min_bound)
        return value_lst
    def set_bula_height4viz(self,shape_node_lst,scale_factor):
        for shape_node in shape_node_lst:
            buladata = shape_node.grammar.type['bula']
            bpt_lst = buladata.bpt_lst
            val_lst =  buladata.value_lst
            for i,bp_tuple in enumerate(zip(bpt_lst,val_lst)):
                bpt,val = bp_tuple[0],bp_tuple[1]
                vizpt = rc.Geometry.Point3d(bpt[0],bpt[1],val*scale_factor)
                buladata.bpt_viz_lst[i] = vizpt
    def set_bula_line4viz(self):
        pass
        """
        #Extract bulapt for each lot and visualize as line graph
        line = []
        newlots = []
        for lot in lots:
            for bula_data in lot.data.type['bula_data']:
                ht = lot.data.type['bula_data'].value
                for bpt in bula_data.bpt_lst: 
                    cp = bpt
                    try:
                        line_ = rs.AddLine([cp[0],cp[1],ht],[cp[0],cp[1],0.])
                        line.append(line_)
                    except:
                        pass
        
        pt = line
        """
if True:
    sc.sticky['Bula'] = Bula
