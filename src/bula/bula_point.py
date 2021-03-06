"""
Created on Jun 25, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import scriptcontext as sc

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
    def extract_line_data(self,lstx_):
        ## lstx is the line extruded z height
        ## cpt: the topcpt of lstx
        # loop through all lines, get origin and zht (relative density)
        # zht (density) is divided by 10
        cpt_ = []
        for i in lstx_:
            try:
                if type(rs.AddPoint(0,0,0)) != type(i):
                    i = sc.doc.Objects.AddLine(i)
                cptlst_ = rs.PolylineVertices(i)
                if cptlst_[0][2] < cptlst_[1][2]:
                    topcpt = cptlst_[1]
                else:
                    topcpt = cptlst_[0]
        
                #print si
                cpt_.append(topcpt)
            except Exception as e:
                print 'problem at line extraaxtion', str(e)
        return cpt_
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
                    #d = rs.AddPoint(copy_cp[0], copy_cp[1],0)
                    #debug.append(d)
            lst_bpt_lst_.append(neighbor)
        return lst_bpt_lst_ 
    def generate_bula_point(self,lots_,lst_bpt_lst_):
        ## Loop through tree lots w/ bula_pts
        ## Add them together and generate the bpt
        lov = []
        for lot,bpt_lst_ in zip(lots_,lst_bpt_lst_):
            ## Make a bpt for each lot
            bpt = Bula_Data(bpt_lst_)
            norm_lst = map(lambda b: b[2],bpt_lst_)
            bpt.value = sum(norm_lst)/float(bpt.bpt_num)
            lot.data.type['bula_data'] = bpt
            #lov.append(lot.data.type['bula_data'].value)
        ## Normalize the bpt.value
        #norm_bpt_lst = self.normalize_list(lov,1.,0.08)
        #for lot,norm in zip(lots_,norm_bpt_lst):
        #    lot.data.type['bula_data'].value = norm
        return lots_
    def calculate_node_gfa(self,lots_):
        ##It would be a lot easier to do all these additions
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

def brute_force_reorder(oldlots_,newlots,maxrecursenum,count):
    ## brute force bade code
    ## "Premature optimization is the root of all evil" - Donald Knut    
    if count >= maxrecursenum:
        return newlots
    else:
        for lot in oldlots:
            if lot.loc:
                newlots.append(lot.loc.pop(0))
        return brute_force_reorder(oldlots_,newlots,maxrecursenum,count+1)

debug = sc.sticky['debug']
debug = []
sc.sticky['BulaData'] = Bula_Data

if lstx!=[] and lstx!=[None] and oldlots!=[] and oldlots!=[None]:
    Bula = Bula_Data()
    cpt_lst = Bula.extract_line_data(lstx)
    #norm_cpt_lst = Bula.normalize_cpt_data(cpt_lst)
    norm_cpt_lst = cpt_lst    
    if 'park' in oldlots[0].get_root().data.type['label']:
        lot_lst = []
        maxcourtslices = 0.
        for lot in oldlots:
            if maxcourtslices < float(len(lot.loc)):
                maxcourtslices = float(len(lot.loc))
        #lot_lst = brute_force_reorder(oldlots,lot_lst,maxcourtslices+1,0)
        #oldlots = lot_lst
    for i,lot in enumerate(oldlots):
        if i < 1:
            debug.append(lot.data.shape.geom)
    #"""
        
    lst_bpt_lst = Bula.getpoints4lot(oldlots,norm_cpt_lst)
    lots = Bula.generate_bula_point(oldlots,lst_bpt_lst)
    
    line = []
    newlots = []
    for lot in oldlots:
        cp = lot.data.shape.cpt
        ht = lot.data.type['bula_data'].value
        try:
            line_ = rs.AddLine([cp[0],cp[1],ht],[cp[0],cp[1],0.])
            line.append(line_)
        except:
            pass
        #if 'podium' in lot.get_root().data.type['label']:
        #newlots.extend(lot)
        newlots.extend(lot.traverse_tree(lambda n: n,internal=False))
        #debug.append(lot.data.shape.geom)
    #oldlots = Bula.sort_by_bula(oldlots)
    lst_lots = newlots#oldlots
    #print 'debug', debug
    