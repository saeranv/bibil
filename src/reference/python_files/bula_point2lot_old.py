"""
Created on Jun 25, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import copy
import math


class Density_Point:
    def __init__(self,index,shape,factor=0):
        self.index = index
        self.shape = shape
        self.lot_area = None
        self.GFA = 0
        self.factor = factor #basically cell z val
        self.prep = 1
        self.low_N = None
        # list of closest neighbors, sorted from closest to furthest
        self.lst_N = []
        self.slope = 0
        self.max_ht = None

lst_lots = []
#debug = sc.sticky['debug']

if lstx!=[] and lstx!=[None] and oldlots!=[] and oldlots!=[None]:
    # lstx is the line extruded z height
    for index,x in enumerate(lstx):
        cpt, datalst = [], []
        # loop through all lines, get origin and zht (relative density)
        # zht (density) is divided by 10
        for i in x:
            try:
                i = sc.doc.Objects.AddLine(i)
                cptlst = rs.PolylineVertices(i)
                if cptlst[0][2] < cptlst[1][2]:
                    cpt_ = cptlst[0]
                    si = cptlst[1][2]
                    topcpt = cptlst[1]
                else:
                    cpt_ = cptlst[1]
                    si = cptlst[0][2]
                    topcpt = cptlst[0]
        
                #print si
                cpt.append(topcpt)
                #datalst.append(si/10.)
            except:
                pass
    
    line_ = [] 
    # the lot tree nodes 
    lots = copy.deepcopy(oldlots)
    
    #loop through tree lots
    for lot in lots:
        boundary = lot.data.shape.bottom_crv
        #print cpt
        neighbor = []
        # look through all cpts from dpts and add to neighborlst
        for i,cp in enumerate(cpt):
            in_lot = int(rs.PointInPlanarClosedCurve(cp,boundary,lot.data.shape.cplane))
            #0 = point is outside of the curve
            #1 = point is inside of the curve
            #2 = point in on the curve
            lotGFA = 0
            if abs(float(in_lot) - 1.) <= 0.1:
                neighbor.append(cp)#,datalst[i]])
                #line_.append(rs.AddLine(cp,[cp[0],cp[1],0.]))
        lot.data.neighbor = neighbor
    
    print ''
    sum_GFA = 0.
    neighbor_num = 0.
    #loop through tree lots w/ dpts
    for i,lot in enumerate(lots):
        if True:
            GFAsum = 0
            for n in lot.data.neighbor:
                # add all the relative density numbers together
                GFAsum += n[2]/10.
                neighbor_num += 1.
                #print n[1]
            # make a dpt for each lot
            dpt = Density_Point(i,lot.data.shape,factor=0)
            #lot_area,dist,axis = lot.data.shape.get_property()
            dpt.lot_area = lot.data.shape.get_area()
            
            ## The lot FAR is the average relative frequency
            if len(lot.data.neighbor) >= 1.:
                dpt.GFA = GFAsum/float(len(lot.data.neighbor))
            else:
                dpt.GFA = 0.
            #if dpt.FAR > float(max_far):
            #    dpt.FAR = float(max_far)
            #print farsum, len(lot.data.neighbor)
            lot.data.density = copy.deepcopy(dpt)
            sum_GFA += dpt.GFA
    
    ### This section recacalculates density amounts to bring the 
    ### actual density in line with the reference density provided by
    ### the designer while maintaining the exponential or nonexponetial
    ### relationship between different lot FARS.
    
    lot_num = float(len(lots))
    
    #lot_area = lots[0].get_root().data.shape.geom
    lot_area = float(rs.Area(ref_root))
    ref_GFA = ref_density * lot_area
    ## Calculate difference between reference FAR, and actual FAR
    abs_diff = abs(float(ref_GFA) - sum_GFA)
    abs_diff = abs_diff*-1 if ref_GFA < sum_GFA else abs_diff
    ## Sort lot nodes from lowest to highest FAR
    lots.sort(key=lambda n: n.data.density.GFA)
    
    ## Define new variables
    print 'original sum_GFA', sum_GFA
    print 'w/ abs_avg', sum_GFA + abs_diff
    print abs_diff, 'num', neighbor_num, '\n'
    
    count = 0
    data = []
    
    #if abs(sum_GFA-0.) <= 0.0001:
    #    debug.append(
    ## Loop through the listof(lots)
    for i,lot in enumerate(lots):
        ## Neighbor nodes are the fine grain Batty cells, within a lot
        ## used to derive density sim. Not surrounding neighbors. 
        ## Sort the neighbor nodes for each lot from 
        ## lowest to highest by their FAR 
        n_len = float(len(lot.data.neighbor))
        lot.data.neighbor.sort(key=lambda n: n[1])
        lotGFA = lot.data.density.GFA
        localGFAsum = 0.
        
        #if i == 0:
        #    debug.append(lot.data.shape.cpt)
        #    data.append(lot.data.density.FAR)
        #print '\n',i, lotfar*n_len, '=='
        
        ## Loop through the sorted listof (neighbor nodes)
        ## add the FAR to farsum
        for n in lot.data.neighbor:
            count += 1
            #ht = ((n[2]/10.)/n_len) + abs_diff
            localGFAsum += (n[2]/10.)
        #print 'farsum:', i, ',', round(farsum,2)
        ## Calculate the actual lot FAR / actual total FAR
        ## This fixes the exponential relationship.
        proportion = lot.data.density.GFA/sum_GFA
        ## If there is more than one neighbor nodes (or batty cells)
        ## then change FAR to be: the (avg neighbor FAR)
        ## plus the proportional difference between reference and actual 
        ## FAR (abs_diff*proportion)
        if n_len >= 1.:
            ht = localGFAsum/n_len + (abs_diff*proportion)
        else: # farsum = 0
            ht = 0.

        cp = lot.data.shape.cpt
        line_.append(rs.AddLine([cp[0],cp[1],ht*.025],[cp[0],cp[1],0.]))
        lot.data.density.GFA = ht
        
    #print i, sumfar
    print 'ref_GFA', ref_GFA
    print 'actual_density', localGFAsum/lot_area
    
    FAR_info = 'ori sum_GFA: ' + str(sum_GFA) + \
    '\nnew sum_GFA: ' + str(localGFAsum) + '\nref_GFA: ' + str(ref_GFA) +\
    '\nnew density: ' + str(localGFAsum/lot_area)
    
    
    for lot in lots: lot.get_root().traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
    lst_lots = lots

"""
for i,lots in enumerate(lst_lots):
    print '\nbatch', i
    for lot in lots:
        print lot.data.density.FAR
"""    