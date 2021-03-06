"""
Created on Jun 25, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc
import math
import copy
import itertools

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
        self.value_actual = []

    def normalize_list(self,lov,hibound,lobound):
        """normalized_val = [(val-min)/(max-min)] * (hibound-lobound) + lobound
        Alternatively, can be thought of vector normalization (vec/vec_mag) of 1D vector.
        """
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
    def calculate_combination(self,iterable,r):
        # combinations(iterable, r)
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        return itertools.combinations(iterable,r)
    def ghtree2nestlist(self,tree,nest=True):
        nested_lst = []
        for i in range(tree.BranchCount):
            branchList = tree.Branch(i)
            #change from listobject
            lst = []
            for b in branchList:
                if nest:
                    lst.append(b)
                else:
                    nested_lst.append(b)
            if nest:
                nested_lst.append(lst)
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
    def set_node_bula_pt_ref(self,curr_node,bula_node_ref):
        #Purpose: Reference bula pts to curr_node's shape_geom boundaries
        #Input: curr_node,bula_node_ref
        #Output: mutated curr_node w/ bula_data if exists
        buladata = bula_node_ref.grammar.type['bula_data']
        curr_node_lst = [curr_node]
        #Input Point list, Value list
        shape_point_lst = buladata.bpt_lst
        shape_value_lst = buladata.value_lst
        shape_value_lst_actual = buladata.value_actual

        #Call getpoints4lst
        lst_bpt_lst_,lst_val_lst_,lst_val_lst_actual_  = buladata.getpoints4lot(curr_node_lst,shape_point_lst,shape_value_lst,shape_value_lst_actual)
        #print 'bula', lst_bpt_lst_, lst_val_lst_
        return lst_bpt_lst_,lst_val_lst_,lst_val_lst_actual_
    def getpoints4lot(self,lots_,cpt_,value_ref_,actual_value_ref_):
        ## Loop through tree lots and add the point_nodes
        ## to each lot; returns lst of (listof points inside each lot)
        ## bpt_lst,lots: listof(listof(point data)
        debug = sc.sticky['debug']
        lst_bpt_lst_ = []
        lst_val_lst_ = []
        lst_val_lst_actual_ = []

        for j,lot in enumerate(lots_):
            boundary = lot.shape.bottom_crv
            neighbor = []
            neighbor_val= []
            neighbor_val_actual = []
            # look through all cpts from dpts and add to neighborlst
            for i,cp in enumerate(cpt_):

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

                #copy_cp = cp
                in_lot = 0
                try:
                    in_lot = int(rs.PointInPlanarClosedCurve(copy_cp,boundary,lot.shape.cplane))
                except:
                    pass
                #0 = point is outside of the curve
                #1 = point is inside of the curve
                #2 = point in on the curve
                if abs(float(in_lot) - 1.) <= 0.1:
                    cp = rs.coerce3dpoint(cp)
                    neighbor.append(cp)#,datalst[i]])
                    neighbor_val.append(value_ref_[i])
                    neighbor_val_actual.append(actual_value_ref_[i])
                    #d = rs.AddPoint(copy_cp[0], copy_cp[1],0)
                    #debug.append(d)
            lst_bpt_lst_.append(neighbor)
            lst_val_lst_.append(neighbor_val)
            lst_val_lst_actual_.append(neighbor_val_actual)
        return lst_bpt_lst_,lst_val_lst_,lst_val_lst_actual_
    def generate_bula_point(self,shapes_,lst_bpt_lst_,lst_value_lst,lst_value_lst_actual_):
        ## Loop through shape nodes w/ bula_pts
        for i,shape_node in enumerate(shapes_):
            bpt_lst_ = lst_bpt_lst_[i]
            val_lst = lst_value_lst[i]
            actual_val_lst = lst_value_lst_actual_[i]
            avg_val = reduce(lambda x,y: x+y,val_lst)
            ## Make a bpt for each lot
            bpt = Bula(bpt_lst_,val_lst,avg_val)
            bpt.value_actual = actual_val_lst
            #if shape_node.grammar.type.has_key('bula_data'):
            #    shape_node.grammar.type['bula_data'].append(bpt)
            #else:
            shape_node.grammar.type['bula_data'] = bpt
            shapes_[i] = shape_node
        return shapes_
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
        def helper_dist2focal_lst(focal_ref_,analysis_pt_lst):
            #Create nested list:
            #lst of Focal pts (len=2):
            #>> nested lst of distance to focal pt for every analysis pt (len=100)
            apt_lst_in_fpt_lst_ = []
            for i,fpt in enumerate(focal_ref_):
                dist_lst = []
                for j,apt_ in enumerate(analysis_pt_lst):
                    dist2fpt = rs.Distance(fpt,apt_)
                    dist_lst.append(dist2fpt)
                apt_lst_in_fpt_lst_.append(dist_lst)
            return apt_lst_in_fpt_lst_
        def helper_min_dist4apt(apt_lst_in_fpt_lst_,analysis_pt_lst,smooth_factor_):
            #Purpose: Find the minimum distance for each apt
            #Loop through each apt
            #Then loop through each dist2fpt for each apt
            min_dist_lst_ = []
            min_fptindex_lst_ = []
            smooth_fac_lst_ = []
            for i,apt_ in enumerate(analysis_pt_lst):
                dist4fpts = []
                #lstdist2fot = dist of each analysis_pt to fpt
                for lstofdist2fpt in apt_lst_in_fpt_lst_:
                    dist4fpts.append(lstofdist2fpt[i])
                #Identify the fpt that is closer to the apt
                min_fpt_index = dist4fpts.index(min(dist4fpts))
                min_dist = min(dist4fpts)
                min_fptindex_lst_.append(min_fpt_index)
                min_dist_lst_.append(min_dist)

                #Calculate Smoothing factor
                #Find all combinations of two for each fref pt
                comb_dist = self.calculate_combination(dist4fpts,2)
                #Take sqrt of abs difference btwn each dist2fpt and sum
                smooth_ = 0.
                for fptdist in comb_dist:
                    smooth_ += math.pow(math.fabs(fptdist[0]-fptdist[1]),smooth_factor_)
                    #print smooth_factor
                smooth_fac_lst_.append(smooth_)
            return min_dist_lst_,min_fptindex_lst_,smooth_fac_lst_

        #Purpose: Go through each point and add value based on formula
        formula = formula_ref_[0]
        focal_ref = formula_ref_[1]
        focal_height = formula_ref_[2]
        focal_ht_min = focal_height.pop(-1)
        smooth_factor = formula_ref_[3]

        #Set defaults
        if len(focal_height) != len(focal_ref):
            if len(focal_height) == 1 and len(focal_ref) > 1:
                focal_height = focal_height * len(focal_ref)
            else:
                print 'Correct the number of focal_weight inputs'

        #Calculate distance from apt to each focal ref
        apts_in_fpts = helper_dist2focal_lst(focal_ref,analysis_pts_)
        #Make list of the minimum distance to fpt for each apt
        min_dist_lst,min_fptindex_lst,smooth_fac_lst = helper_min_dist4apt(apts_in_fpts,analysis_pts_,smooth_factor)

        #Main function apply formula to min dist of each apt
        #This is ordered by fpt so we can weight it later
        #Careful when adding lists! They are complex objects
        #can unintentionally create odd mutations
        value_lst_by_fpt = []
        for fi in enumerate(focal_ref):
            value_lst_by_fpt.append([])
        for apt_i,dist_data in enumerate(zip(min_dist_lst,min_fptindex_lst)):
            min_dist,fpt_i = dist_data[0],dist_data[1]
            #formula: 1/math.exp(0.1813*dist)
            #print 'f', formula
            #print 'd', min_dist
            #Keep track of which fpt is referenced
            try:
                dist = (min_dist/1000.)*10 #<<< convert to km * 10 for 10 min walk
                val = eval(formula)
            except ZeroDivisionError:
                val = 0.
            #store value, apt index tuple
            value_lst_by_fpt[fpt_i].append((val,apt_i))

        #Add weights to each
        maxht = max(focal_height)
        wtlst = map(lambda ht: ht/maxht,focal_height)
        val_actual_flt = [0]*len(value_lst_by_fpt)
        #print 'wtlst', wtlst
        for fi,val_ind_lst in enumerate(value_lst_by_fpt):
            weight = wtlst[fi]*maxht

            #Separate value and index
            val_lst = map(lambda v: v[0],val_ind_lst)
            ind_lst = map(lambda v: v[1],val_ind_lst)
            #print 'val', val_lst
            #Calculate weighted value
            #
            val_actual = []
            for v in val_lst:
                val_actual.append(float(v) * 100.0)
            #
            max_bound = weight * max(val_lst)
            min_bound = weight * min(val_lst)
            val_lst = self.normalize_list(val_lst,max_bound,min_bound)
            #Now merge value and index back
            val_ind_lst = map(lambda x:(x[0],x[1]),zip(val_lst,ind_lst))

            val_actual = map(lambda x: (x[0],x[1]),zip(val_actual,ind_lst))
            val_actual_flt[fi] = val_actual

            value_lst_by_fpt[fi] = val_ind_lst

        #Resort by apt order
        #this is a clever way of handling this problem
        flat_val_ind_lst = reduce(lambda x,y:x+y,value_lst_by_fpt)
        flat_val_ind_lst.sort(key=lambda n:n[1])
        value_lst = map(lambda x: x[0],flat_val_ind_lst)

        #Resort by apt order ACTUAL
        flat_val_ind_lst_actual = reduce(lambda x,y:x+y,val_actual_flt)
        flat_val_ind_lst_actual.sort(key=lambda n:n[1])
        value_lst_actual = map(lambda x: x[0],flat_val_ind_lst_actual)

        #Add smoothing factor
        if len(focal_ref) > 1:
            smooth_fac_lst = self.normalize_list(smooth_fac_lst, 1, 0.001)
        else:
            smooth_fac_lst = self.normalize_list(value_lst,1, 0.001)

        value_lst = map(lambda vs: vs[0]*vs[1], zip(value_lst,smooth_fac_lst))
        #max_wtd_value = max(value_lst)
        for i,wtd_val in enumerate(value_lst):
            sf = smooth_fac_lst[i]
            #wtd_sf_val = wtd_val *sf
            inc = (1.-sf)*focal_ht_min
            #print '---'
            #print 'sf: ', sf
            #print 'inc:', inc
            #print 'ht: ', wtd_val
            #if sf <= 0.999:
            #    if (wtd_val + inc) <= max_wtd_value:
            wtd_val_inc = wtd_val + inc
            value_lst[i] = wtd_val_inc

        #Done!
        return value_lst, value_lst_actual
    def set_bula_height4viz(self,shape_node_lst):
        for shape_node in shape_node_lst:
            buladata = shape_node.grammar.type['bula_data']
            bpt_lst = buladata.bpt_lst
            val_lst =  buladata.value_lst
            for i,bp_tuple in enumerate(zip(bpt_lst,val_lst)):
                bpt,val = bp_tuple[0],bp_tuple[1]
                vizpt = rc.Geometry.Point3d(bpt[0],bpt[1],val)
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
