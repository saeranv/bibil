"""
Created on Jun 25, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

## Import classes
#Pattern = sc.sticky["Pattern"]
#Shape_3D = sc.sticky["Shape_3D"]
#Tree = sc.sticky["Tree"] 
#Grammar = sc.sticky["Grammar"]

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
class Bula_Data:
    def __init__(self,bpt_lst=None,value=0.):
        if bpt_lst == None:
            bpt_lst = []
        self.bpt_lst = bpt_lst
        self.bpt_num = 1 if len(bpt_lst) < 1. else len(bpt_lst)
        #Normalized value of bpt_lst data
        self.value = value
        self.lot_gfa = 0
    
    def normalize_list(self,lov,hibound,lobound,max_=None,min_=None):
        """normalized_val = ( (val-min)*(hibound-lobound) )/(max-min) + lobound"""
        if max_ == None:
            max_ = max(lov)
        if min_ == None:
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
    def getpoints4lot(self,lots_,cpt_):
        ## Loop through tree lots and add the point_nodes
        ## to each lot; returns lst of (listof points inside each lot)
        ## bpt_lst,lots: listof(listof(point data) 
        debug = sc.sticky['debug']
        lst_bpt_lst_ = []
        for j,lot in enumerate(lots_):
            boundary = lot.data.shape.bottom_crv
            neighbor = []
            # look through all cpts from dpts and add to neighborlst
            for i,cp in enumerate(cpt_):
                """
                movedist = abs(lot.data.shape.cpt[2]-cp[2])
                if abs(movedist-0.0)>0.1:
                    if lot.data.shape.cpt[2] < cp[2]:
                        movedist *= -1
                    vec = rc.Geometry.Vector3d(0,0,movedist)
                else:
                    vec = rc.Geometry.Vector3d(0,0,0)
                if not lot.data.shape.is_guid(cp):
                    cp = sc.doc.Objects.AddPoint(cp)
                copy_cp = rs.CopyObject(cp,vec)
                #copy_cp = rs.coerce3dpoint() 
                """
                copy_cp = cp
                in_lot = 0
                try:
                    in_lot = int(rs.PointInPlanarClosedCurve(copy_cp,boundary,lot.data.shape.cplane))
                except:
                    pass
                #0 = point is outside of the curve
                #1 = point is inside of the curve
                #2 = point in on the curve
                if abs(float(in_lot) - 1.) <= 0.1:
                    neighbor.append(cp)#,datalst[i]])
            lst_bpt_lst_.append(neighbor)
        ## Now get the outpts
        out_lst = []
        for cp in cpt_:
            copy_cp = cp
            PtInside = False
            for lot in lots_:
                IsGround = True
                if lot.data.shape.cpt:
                    IsGround = abs(lot.data.shape.cpt[2] - 0.0) < 0.5
                if IsGround:
                    boundary = lot.data.shape.bottom_crv
                    try:
                        in_lot = int(rs.PointInPlanarClosedCurve(copy_cp,boundary,lot.data.shape.cplane))
                    except:
                        pass
                    #0 = point is outside of the curve
                    #1 = point is inside of the curve
                    #2 = point in on the curve
                    if abs(float(in_lot) - 1.) <= 0.1:
                        PtInside = True
                        break
                if PtInside:
                    break
            if not PtInside: 
                out_lst.append(cp)
        return lst_bpt_lst_, out_lst 
    def generate_bula_point(self,lots_,lst_bpt_lst_,value_lst=None):
        ## Loop through lots w/ bula_pts
        ## Add them together and generate the bpt
        lov = []
        for i,lot in enumerate(lots_):
            bpt_lst_ = lst_bpt_lst_[i]
            val = value_lst[i]
            ## Make a bpt for each lot
            bpt = Bula_Data(bpt_lst_,val)
            lot.data.type['bula_data'] = bpt
            lov.append(lot.data.type['bula_data'].value)
        
        ## Normalize the bpt.value
        norm_bpt_lst = self.normalize_list(lov,1.,0.,min_=0.)
        for lot,norm in zip(lots_,norm_bpt_lst):
            lot.data.type['bula_data'].value = norm
        return lots_
    def remove_duplicate(self,out_pts_,lst_plain_pt_lst_,tol=5.):
        remove_duplicate = []
        pt_lst = reduce(lambda x,y: x+y,lst_plain_pt_lst_)
        for opt in out_pts:
            print opt
            x,y,z = opt[0], opt[1], opt[2]
            Duplicate = False
            for ppt in pt_lst:
                x_ = abs(x - ppt[0]) < tol
                y_ = abs(y - ppt[1]) < tol
                z_ = abs(z - ppt[2]) < tol
                if (x_ and y_ and z_):
                    Duplicate = True
            if not Duplicate:
                remove_duplicate.append(opt)
        return remove_duplicate
    def calculate_node_gfa(self,lots_):
        ## It would be a lot easier to do all these additions
        ## and operations on lists with numpy!!
        ## Old obselete, will need to rwrite to reflect
        ## lot.data.type['bula_pt'] = lot.data.type['bula_data']
        ## is a single class not list of bpt classes
        
        ### This section recalculates density amounts to bring the 
        ### actual density in line with the reference density provided by
        ### the designer while maintaining the exponential or nonexponetial
        ### relationship between different lot FARS.
        lot_num = float(len(lots_))
        lot_area = sum(map(lambda l:l.data.shape.get_area(),lots_))
        sum_gfa = 0.
        for l in lots_:
            for bpt in l.data['bula_pt']:
                sum_gfa += bpt.value
            bula_num = len(l.data['bula_pt'])
            sum_gfa += 0 if bula_num < 1 else sum_gfa/float(bula_num)
        ref_gfa = ref_density * lot_area
        ## Calculate difference between reference FAR, and actual FAR
        abs_diff = abs(float(ref_gfa) - sum_gfa)
        abs_diff = abs_diff*-1 if ref_gfa < sum_gfa else abs_diff
        ## Sort lot nodes from lowest to highest FAR
        lots.sort(key=lambda n: n.data.type['bula_pt'].value)
           
        ## Loop through the listof(lots)
        for i,lot in enumerate(lots_):
            ## Neighbor nodes are the fine grain Batty cells, within a lot
            ## used to derive density sim. Not surrounding neighbors. 
            ## Sort the neighbor nodes for each lot from 
            ## lowest to highest by their FAR 
            lot_num = float(len(lot.data.type['bula_pt']))
            lot_val = sum(map(lambda bpt: bpt.value,lot.data.type['bula_pt']))
            try: 
                lot_gfa = (lot_val/lot_num) * lot.data.shape.get_area()
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
            lot.data.type['lot_gfa'] = new_lot_gfa
        return lots_
    def sort_by_bula(self,lots_):
        ## Sort by Bula_data.value, from highest to lowest
        def helper_chk_bula(lot_):
            if lot_.data.type.has_key('bula_data'):
                bula_val = lot_.data.type['bula_data'].value 
            else: 
                bula_val = 0.
            return bula_val 
        #print map(lambda n: n.data.type['bula_data'].value,lots_)
        bula_sort = sorted(lots,key=lambda n: helper_chk_bula(n),reverse=True)
        #print map(lambda n: n.data.type['bula_data'].value,bula_sort)
        return bula_sort
    def create_bula_viz(self,lots_,scale_):
        viz_dict = {}
        viz = []
        for lot_ in lots_:
            ht = lot_.data.type['bula_data'].value
            #if lot_.data.shape.cpt:
            #    base = lot_.data.shape.cpt[2]
            #else:
            #    base = 0.0
            #Sort through each bulapt
            for i,bula_pt in enumerate(lot_.data.type['bula_data'].bpt_lst):
                cp = bula_pt    
                chk_str = str(int(cp[0])) + str(int(cp[1]))
                IsExist = viz_dict.has_key(chk_str)
                if not IsExist:
                    viz_dict[chk_str] = [ht,cp]
                else:
                    viz_dict[chk_str][0] += ht
                    viz_dict[chk_str][1] = rc.Geometry.Point3d(cp[0],cp[1],viz_dict[chk_str][0])
                #lot_.data.type['bula_data'].bpt_lst[i] = newpt
        
        lovp = viz_dict.values()
        for vp in lovp:    
            cp = vp[1]
            ht = vp[0]
            try:
                #viz_input = rs.AddLine([cp[0],cp[1],cp[2]*scale_],[cp[0],cp[1],0.])
                viz_input = rs.AddPoint(cp[0],cp[1],cp[2]*scale_)
                viz.append(viz_input)
            except:
                pass
        return viz

debug = sc.sticky['debug']
debug = []
sc.sticky['BulaData'] = Bula_Data


if run and cpt!=[] and cpt!=[None] and child_node_in!=[] and child_node_in!=[None]:
    Bula = Bula_Data()
    #zones = Bula.ghtree2nestlist(zones)[0]
    if child_node_in[0].data.shape.is_guid(cpt[0]):
        norm_cpt_lst = map(lambda p: rs.coerce3dpoint(p),cpt)
    else:
        norm_cpt_lst = cpt
    
    
    lst_plain_pt_lst,out_pts = Bula.getpoints4lot(child_node_in,norm_cpt_lst)
    #debug.extend(reduce(lambda x,y: x+y, lst_plain_pt_lst))
    lots = Bula.generate_bula_point(child_node_in,lst_plain_pt_lst,values)
    line = Bula.create_bula_viz(lots,scale_)
    debug.extend(out_pts)
    