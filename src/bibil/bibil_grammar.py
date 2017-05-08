import rhinoscriptsyntax as rs
import Rhino as rc
import random
import scriptcontext as sc
import copy
import math
import ghpythonlib.components as ghcomp
import clr
from Rhino import RhinoApp

clr.AddReference("Grasshopper")
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree

#"C:\Users\vasanthakumars\AppData\Local\Temp"

"""import classes"""
Shape = sc.sticky["Shape"]
Tree = sc.sticky["Tree"]
Bula = sc.sticky["Bula"]

sc.sticky['debug'] = []
debug = sc.sticky["debug"]

TOL = sc.doc.ModelAbsoluteTolerance

class Grammar:
    """Grammar """
    def __init__(self):
        self.type = {'label':"x","rule_stack":[],'grammar':"null",\
                     'axis':"NS",'ratio':0.,'freeze':False,'dispose':False}
        #need to move axis, NS, ratio to divide
    def label(self,temp_node_,PD_):
        temp_node_.grammar.type['label'] = PD_['label']
        temp_node_.grammar.type['grammar'] = 'label'
        return temp_node_
    def make_rule_stack(self,node):
        #returns the grammar rules that were applied to this node
        rule_stack = node.backtrack_tree(lambda n:n,accumulate=True)
        rule_stack = map(lambda n: n.grammar.type['grammar_key'],rule_stack)
        return rule_stack
    def helper_geom2node(self,geom,parent_node=None,label="x",grammar="null",cplane_ref=None,UINode=False):
        debug = sc.sticky['debug']
        child_node,child_shape = None, None
        IsDegenerate = False
        tree_depth = 0
        if True:#try:
            if geom:
                if parent_node:
                    cplane_ref = parent_node.shape.cplane
                #try:
                #geom = copy.copy(geom)
                child_shape = Shape(geom,cplane=cplane_ref)
                #except Exception as e:
                #    print 'Bibil has detected a degenerate shape', str(e)
                #    child_shape = Shape(geom,parent_node.shape.cplane)
                IsDegenerate = child_shape.cpt==None or abs(child_shape.x_dist-0.) <= 0.1 or abs(child_shape.y_dist-0.) <= 0.1
            elif parent_node:
                #cloned nodes get link to parent_node.shape
                child_shape = parent_node.shape
            
            if UINode:
                    child_shape.UIgeom = copy.copy(rs.coercebrep(geom))
            
            if parent_node:
                tree_depth = parent_node.depth+1
            if IsDegenerate == False:
                if geom:
                    if child_shape.z_dist!=None and int(child_shape.z_dist) <= 0.0001:
                        child_shape.op_extrude(1.)
                child_grammar = Grammar()
                child_grammar.type["label"] = label
                child_grammar.type["grammar"] = grammar
                child_node = Tree(child_shape,child_grammar,parent=parent_node,depth=tree_depth)
        #except Exception as e:
        #    print "Error at Pattern.helper_geom2node", str(e)
        return child_node
    def helper_clone_node(self,node_,parent_node=None,label="x"):
        #Purpose: Input node, and output new node with same Shape, new Grammar
        return self.helper_geom2node(None,parent_node,label)
    def helper_UI_geom(self,tnode):
        if tnode.shape.UIgeom != None:
            tnode.shape = Shape(tnode.shape.UIgeom,tnode.shape.cplane)
        return tnode
    def is_near_zero(self,num,eps=1E-10):
        return abs(float(num)) < eps
    def solar_envelope_uni(self,node_0,time,seht,stype):
        def helper_get_curve_in_tree(node_,stype_,seht_):
            if stype_ == 3:
                noderoot = node_.get_root()
                basecrv = copy.copy(noderoot.shape.bottom_crv)
                ###debug.append(basecrv)
            else:
                basecrv = copy.copy(node_.shape.bottom_crv)
            # Move up to lot_node height
            rc.Geometry.PolyCurve.Translate(basecrv,0.,0.,seht_)
            return basecrv

        def helper_intersect_solar(se_,node_,seht_):
            nodegeomlst = node_.shape.op_split("Z",seht_/node_.shape.z_dist)
            nodebase,nodetop = nodegeomlst[0],nodegeomlst[1]
            se_intersect =  rc.Geometry.Brep.CreateBooleanIntersection(nodetop,se_,TOL)[0]
            rc.RhinoApp.Wait()
            se_union =  rc.Geometry.Brep.CreateBooleanUnion([se_intersect,nodebase],TOL)[0]
            return se_union

        #debug = sc.sticky["debu
        TOL = sc.doc.ModelAbsoluteTolerance
        start,end = time, abs(time - 12.) + 12.
        debug = sc.sticky['debug']
        try:
            node_0.get_root().traverse_tree(lambda n: n.shape.convert_rc('3d'))
            ## Get correct curve from data tree
            se_crv = helper_get_curve_in_tree(node_0,stype,seht)
            ## Get base and top
            #split_ratio = seht/node_0.shape.z_dist
            #lstchild = node_0.shape.op_split("Z",split_ratio)
            #lot_base,lot_top = lstchild[0],lstchild[1]
            ## Generate solar envelope
            #print 'se_crv', se_crv
            se = node_0.shape.op_solar_envelope(start,end,se_crv)
            sebrep = helper_intersect_solar(se,node_0,seht)
            #print 'solarbrep', sebrep
            ###debug.append(sebrep)
            return sebrep
        except Exception as e:
            print "Error @ solar_env_uni", str(e)
    def solar_envelope_multi(self,temp_node_,solartime_,data,solarht_):
        def helper_solar_envelope_multi(data,time,ht):
            try:
                #debug = sc.sticky["debug"]
                cpt = data.shape.cpt
                #time = [9,10,11,12,13]
                time += random.randint(-3,3)
                start = time
                end = start + 1.
                data.shape.make_top_crv()
                data.shape.convert_guid(dim='3d')
                #curve = top_crv#rs.CopyObject(data.shape.bottom_crv,[0,0,data.shape.ht])
                #g = copy.copy(rs.coercegeometry(data.shape.geom))
                cpt = rs.coerce3dpoint(data.shape.top_cpt)#[cpt[0], cpt[1], data.shape.ht]
                curve = data.shape.top_crv

                se = data.shape.op_solar_envelope(start,end,curve)

                htpt = rs.AddPoint(cpt[0],cpt[1],ht)#data.shape.ht)
                if curve:
                    bottom_crv = curve
                else:
                    if not data.shape.is_guid(data.shape.bottom_crv):
                        tcrv = sc.doc.Objects.AddCurve(data.shape.bottom_crv)
                    else:
                        tcrv = data.shape.bottom_crv
                    tvec = rs.VectorCreate(data.shape.top_cpt, data.shape.cpt)
                    bottom_crv = rs.CopyObject(tcrv,tvec)
                dcpt = data.shape.cpt
                if not data.shape.is_guid(dcpt):
                    dcpt = rs.AddPoint(dcpt[0],dcpt[1], dcpt[2])
                path_ = rs.AddCurve([dcpt,htpt])
                srf = rs.ExtrudeCurve(bottom_crv,path_)
                rs.CapPlanarHoles(srf)
                srf = rs.coercegeometry(srf)
                TOL = sc.doc.ModelAbsoluteTolerance
                ###debug.append(srf)
                try:
                    se =  rc.Geometry.Brep.CreateBooleanIntersection(se,srf,TOL)[0]
                except:
                    print 'error at solar multi helper'
                return se
            except Exception as e:
                print e
        try:
            sublst = temp_node_.traverse_tree(lambda n:n,internal=False)
            for subnode in sublst:
                add_hour = float(random.randint(-2,2))
                if add_hour == 0.: add_hour = 1
                solartime_ += 1/add_hour
                try:
                    se = helper_solar_envelope_multi(subnode.grammar,solartime_,solarht_)
                    geo_brep = rs.coercebrep(rs.CopyObject(subnode.shape.geom))
                    unioned =  rc.Geometry.Brep.CreateBooleanUnion([se,geo_brep],TOL)
                except Exception as e:
                    print "Error at solar_envelope multi"
                    print e
                try:
                    unioned = unioned[0]
                    subnode.shape.geom = unioned
                except:
                    print 'error multi unioning solartypes'
            return temp_node_
        except Exception as e:
            print "Error at pattern solar envelope multi"
            print e
    def abstract_BEM(self,tnode,PD_):
        debug = sc.sticky['debug']
        tnode.grammar.type['grammar'] = 'abstract_bem'
        dist_tol = PD_['bem_tol']
        center = PD_['bem_center']
        #Need to eliminate geoms not in dist_tol
        if not tnode.grammar.type.has_key('tolerance_curve'):
                tnode.grammar.type['tolerance_curve'] = []
        try:
            perppts = tnode.shape.offset_perpendicular_from_line(center,dist_tol)
        except:
            debug.append(tnode.shape.geom)
            return tnode
        canoffcrv = rc.Geometry.Curve.CreateControlPointCurve(perppts,1)
        tnode.grammar.type['tolerance_curve'].append(canoffcrv)
        IsIntersect = tnode.shape.check_region(canoffcrv,realvalue=True)
        #if disjoint==setrel: return 0
        #elif intersect==setrel:return 1
        #elif AInsideB==setrel:return 2
        #else: return 3
        if self.is_near_zero(IsIntersect):
            tnode.grammar.type['context_geometry'] = tnode.shape.geom
            tnode.grammar.type['freeze'] = True
            return tnode
        #debug.append(tnode.shape.geom)
        
        maxht = tnode.shape.ht
        minht = tnode.shape.cpt[2]
        if self.is_near_zero(minht):
            minht = 0.0
        dimz = maxht - minht
        
        bothtpt = copy.copy(tnode.shape.cpt)
        htlst = [bothtpt]
                 
        if dimz > 4.5:
            midhtpt = copy.copy(tnode.shape.cpt)
            tophtpt = copy.copy(tnode.shape.cpt)
            midhtpt.Z = (dimz/2.)-(dimz/2.)%3 + minht
            tophtpt.Z = maxht - 3.
            
            #ugly but short term works
            htlst = [bothtpt,midhtpt,tophtpt]
        
            if (tophtpt.Z - midhtpt.Z)/2. > 9.:
                topmidpt = copy.copy(tnode.shape.cpt)
                topmidpt.Z = ((tophtpt.Z - midhtpt.Z)/2.) - ((tophtpt.Z - midhtpt.Z)/2.)%3 + midhtpt.Z
                htlst = [bothtpt,midhtpt,topmidpt,tophtpt]
            if (midhtpt.Z - bothtpt.Z)/2. > 9.:
                botmidpt = copy.copy(tnode.shape.cpt)
                botmidpt.Z = ((midhtpt.Z - bothtpt.Z)/2.) - ((midhtpt.Z - bothtpt.Z)/2.)%3 + bothtpt.Z
                htlst = [bothtpt,botmidpt,midhtpt,topmidpt,tophtpt]
            
            
        tnode.loc = []
        for i in xrange(len(htlst)): 
            refpt = htlst[i]
            crv = tnode.shape.get_bottom(tnode.shape.geom,refpt,tol=1.0,bottomref=minht)
            zone = self.helper_geom2node(crv,parent_node=tnode,grammar='thermalzone',cplane_ref=tnode.shape.cplane)
            if zone==None:
                refpt.Z += 0.5
                crv = tnode.shape.get_bottom(tnode.shape.geom,refpt,tol=1.0,bottomref=minht)
                zone = self.helper_geom2node(crv,parent_node=tnode,grammar='thermalzone',cplane_ref=tnode.shape.cplane)
            if zone==None:
                return tnode
            flr_ht = 0.0 if self.is_near_zero(zone.shape.cpt.Z,eps=0.1) else zone.shape.cpt.Z
            zone.grammar.type['flr_ht'] = flr_ht
            
            if i==0 or i==len(htlst)-1:
                zone.grammar.type['is_interzone'] = False
            else:
                zone.grammar.type['is_interzone'] = True
            zone.shape.op_extrude(3.0)
            tnode.loc.append(zone)
            
        return tnode
    def extract_canyon(self,tnode,PD_):
        debug = sc.sticky['debug']
        tnode.grammar.type['grammar'] = 'extract_canyon'
        dist_tol = PD_['canyon_tol']
        center = PD_['canyon_center']
        srf_data = PD_['srf_data']
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        if dist_tol == None: dist_tol = 10.0
        angle_tol = 15.0
        
        #Add data to Bibil node
        tnode.grammar.type['processed_srf_data'] = []
        tnode.grammar.type['processed_srf'] = []
        tnode.grammar.type['processed_srf_pt'] = []
        tnode.grammar.type['processed_srf_geom'] = []
        tnode.grammar.type['processed_srf_normal'] = []
        
        #Get HBZone from hive (?)
        hnode = tnode.backtrack_tree(lambda n:n.grammar.type.has_key('HBZone'))
        HZone = hnode.grammar.type['HBZone']
        zone = hb_hive.visualizeFromHoneybeeHive([HZone])[0]
        zone_num = int(zone.name.split('_')[-1])
        
        if 'ground' in hnode.grammar.type['label']:
            def process_ground_data(tnode_,ground_zone,ground_zone_num):
                tnode_.grammar.type['ground_srf_data'] = []
                tnode_.grammar.type['ground_srf'] = []
                tnode_.grammar.type['ground_srf_pt'] = []
                tnode_.grammar.type['ground_srf_geom'] = []
                
                #Find the srf data for ground zone
                valid_srf_index_dict = {}
                for i in xrange(len(srf_data)):
                    info4srf = srf_data[i][2]
                    
                    if not 'Roof' in info4srf:
                        continue
                    srfdatalst = info4srf.split('_')
                    zone_num_chk = int(srfdatalst[1])    
                    if zone_num_chk != ground_zone_num:
                        continue
                    srf_num_chk = srfdatalst[3].split(':')[0]
                    
                    valid_srf_index_dict[srf_num_chk] = i
                    
                valid_srf_obj = []
                #Sort srf in zone.surface
                for i in xrange(len(ground_zone.surfaces)):
                    srf = ground_zone.surfaces[i]
                    srfnumchk = srf.name.split('_')[-1]
                    if not valid_srf_index_dict.has_key(srfnumchk):
                        continue
                    
                    srfindex = valid_srf_index_dict[srfnumchk]    
                    
                    srf_temp_lst = srf_data[srfindex][7:]
                    srf_temp_avg = reduce(lambda x,y:x+y,srf_temp_lst)/float(len(srf_temp_lst))
                    tnode_.grammar.type['ground_srf_data'].append(srf_temp_avg)
                    tnode_.grammar.type['ground_srf'].append(srf)
                    tnode_.grammar.type['ground_srf_pt'].append(srf.cenPt)
                    tnode_.grammar.type['ground_srf_geom'].append(srf.geometry)
                    #zerovec = rc.Geometry.Vector3d(0,0,0)
                    #tnode.grammar.type['ground_srf_normal'].append(zerovec)
                    #print '--'
            process_ground_data(tnode,zone,zone_num)
            return tnode
        #Check zone_num and srf_data_index
        #print zone.name
        #print srf_data[srf_data_index][2]
        
        #Need to eliminate geoms not in dist_tol
        if not tnode.grammar.type.has_key('tolerance_curve'):
                tnode.grammar.type['tolerance_curve'] = []
        try:
            perppts = tnode.shape.offset_perpendicular_from_line(center,dist_tol)
        except:
            tnode.grammar.type['freeze'] = True
            return tnode
        canoffcrv = rc.Geometry.Curve.CreateControlPointCurve(perppts,1)
        tnode.grammar.type['tolerance_curve'].append(canoffcrv)
        IsIntersect = tnode.shape.check_region(canoffcrv,realvalue=True)
        #if disjoint==setrel: return 0
        #elif intersect==setrel:return 1
        #elif AInsideB==setrel:return 2
        #else: return 3
        if self.is_near_zero(IsIntersect):
            tnode.grammar.type['context_geometry'] = tnode.shape.geom
            tnode.grammar.type['freeze'] = True
            return tnode

        #Get tnode matrix
        
        matrix = tnode.shape.base_matrix
        if not matrix:
            matrix = tnode.shape.set_base_matrix()
        #debug.append(tnode.shape.geom)
        #Get reference matrix
        ht = tnode.shape.cpt[2]
        ref_edge = tnode.shape.match_edges_with_refs(matrix,[center],ht,dist_tol=dist_tol,angle_tol=angle_tol)            
        
        #Match srf normals 
        srf_normal = tnode.shape.get_normal_point_inwards(ref_edge[0],to_outside=True)
        
        #srf_normal.Unitize()
        srf_opaque = None
        srf_glass_lst = []
        srf_num = None
        #Sort srf in zone.surface
        for i in xrange(len(zone.surfaces)):
            srf = zone.surfaces[i]
            srf_opaque = srf
            #print srf.normalVector
            #print srf_normal
            IsEqual = srf.normalVector.IsParallelTo(srf_normal,0.1)
            if IsEqual==1:
                if srf_num == None:
                    srf_num = int(srf.name.split('_')[3])
                srf_glass_lst.append(srf_opaque)
                #if srf.hasChild:
                #    for j in xrange(len(srf.childSrfs)):
                #        childSrf = srf.childSrfs[j]
                #        srf_glass_lst.append(childSrf)
                #        #print srf_glass
                break
        #srfopaquenum = srf_opaque.name.split('_')[-1]
        #print srf_opaque.name
        #print srf_glass.name
        glz_num_lst = []
        #for i in xrange(len(srf_glass_lst)):
        #    #print srf_glass_lst[i].name
        #    glz_num_lst.append(srf_glass_lst[i].name.split('_')[-1])
        
        #%%for opaque wall
        glz_num_lst.append(srf_opaque.name.split('_')[-1])
        
        #Identify srf_index from input srf data
        srfdataindex = []
        #for i in xrange(0,len(srf_data),10):
        for i in xrange(len(srf_data)):
            info4srf = srf_data[i][2]
            if not 'Wall' in info4srf:
                continue
            
            srfdatalst = info4srf.split('_')
            zone_num_chk = int(srfdatalst[1])    
            if zone_num_chk != zone_num:
                continue

            srf_num_chk = int(srfdatalst[3].split(':')[0])
            if srf_num_chk != srf_num:
                continue
            
            #glz_num_chk = srfdatalst[-1].split(':')[0] 
            #if glz_num_chk in glz_num_lst:
            srfdataindex.append(i)
        
        #print len(srfdataindex)
        #print len(srf_glass_lst)
        #print '-'
        for i in xrange(len(srfdataindex)):
            srf_glass = srf_glass_lst[i]
            srfindex = srfdataindex[i]
            #zonesrfname = srf_data[srfindex][2]
            #print zonesrfname
            srf_temp_lst = srf_data[srfindex][7:]
            srf_temp_avg = reduce(lambda x,y:x+y,srf_temp_lst)/float(len(srf_temp_lst))
            tnode.grammar.type['processed_srf_data'].append(srf_temp_avg)
            tnode.grammar.type['processed_srf'].append(srf_glass)
            tnode.grammar.type['processed_srf_pt'].append(srf_glass.cenPt)
            tnode.grammar.type['processed_srf_geom'].append(srf_glass.geometry)
            tnode.grammar.type['processed_srf_normal'].append(srf_normal)
        
            #print srf_temp_avg
            #print '----'
        
        #Use window geom
        if srf_opaque.hasChild:
            tnode.shape.geom = srf_opaque.punchedGeometry
        else:
            tnode.shape.geom = srf_opaque.geometry

        #Loop through ref edges
        #edge = ref_edge[0]
        #if type([])==type(edge):
        #    bld_crv = rc.Geometry.Curve.CreateControlPointCurve(edge,0)
        #else:
        #    bld_crv = rs.MoveObject(sc.doc.Objects.AddCurve(edge),[0,0,ht])
        #    bld_crv = rs.coercecurve(bld_crv)
        #exht = tnode.shape.ht - ht
        #srf = tnode.shape.extrude_curve_along_normal(exht,tnode.shape.cpt,bld_crv)
        #debug.append(srf)
        
        return tnode
    def interpolate_vertical(self,tnode_,PD_):
        debug = sc.sticky['debug']
        tnode_.grammar.type['grammar'] = 'interpolate_vertical'
        
        #Assume thermzones in bem >= 3.
        hnode = tnode_.backtrack_tree(lambda n:n.grammar.type.has_key('HBZone'))
        if 'ground' in hnode.grammar.type['label']:
            return tnode_
        
        foobem = lambda n: n.grammar.type['grammar']=='abstract_bem'
        bemnode = tnode_.backtrack_tree(foobem,accumulate=False)
        thermnode = tnode_.parent.parent
        
        #Sort the therm nodes by height
        therm_node_lst = bemnode.loc
        therm_node_lst = sorted(therm_node_lst,key=lambda n:n.grammar.type['flr_ht'])
        
        #Point of separating this from prior function is that
        # every extract_canyon node is processed yet. So null will exist.
        #for t in therm_node_lst:
        #    print t.loc[0]
        #print '--'
        
        #Locate index of current node
        therm_index = therm_node_lst.index(thermnode)
        
        #Isolate floors from current node to next floor
        #This is your interpolation range
        if therm_index+1 >= len(therm_node_lst):
            return tnode_
        
        node_min = therm_node_lst[therm_index]
        node_max = therm_node_lst[therm_index + 1]
        
        if node_min.loc[0].grammar.type.has_key('IsProcessed'):
            if node_min.loc[0].grammar.type['IsProcessed']==True:
                return tnode_
        
        #Starting at next floor, calculate interpolation values
        xlvl = node_min.grammar.type['flr_ht']
        ylvl = node_max.grammar.type['flr_ht']
        xtemplst = node_min.loc[0].grammar.type['processed_srf_data']
        ytemplst = node_max.loc[0].grammar.type['processed_srf_data']
              
        tnode_.grammar.type['interpolate_temperature']=[]
        tnode_.grammar.type['interpolate_srf_geom']=[]
        tnode_.grammar.type['interpolate_cpt']=[]
        tnode_.grammar.type['interpolate_srf_normal']=[]
        #loop through floors, avoiding top, bottom floors
        floor_quantity = (ylvl - xlvl)-(ylvl - xlvl)%3 / 3.0
        for i in xrange(floor_quantity):
            newflrfromht = 3.*i
            newflrht = 3.*i + xlvl
            IsMax = self.is_near_zero(newflrht - node_max.grammar.type['flr_ht'],1.5)
            IsMin = self.is_near_zero(newflrht - node_min.grammar.type['flr_ht'],1.5)
            if IsMin:
                continue
            if IsMax:
                break
            cptlst = node_min.loc[0].grammar.type['processed_srf_pt']
            srfgeomlst = node_min.loc[0].grammar.type['processed_srf_geom']
            srflst = node_min.loc[0].grammar.type['processed_srf']
            
            for j in xrange(len(cptlst)):
                cpt = cptlst[j]
                srfgeom = srfgeomlst[j]
                int_cpt = copy.copy(cpt)
                int_cpt.Z = int_cpt.Z + newflrfromht #to get center of srf
                
                move_vector_up = int_cpt - cpt
                srfguid = sc.doc.Objects.AddBrep(srfgeom)
                movesrfguid = tnode_.shape.move_geom(srfguid,move_vector_up,True)
                srfgeom = rs.coercegeometry(movesrfguid)
                
                #Make new temp 
                if j < len(ytemplst):
                    ytemp = ytemplst[j]
                else:
                    ytemp = ytemplst[-1]
                xtemp = xtemplst[j]
                
                xtemp = xtemplst[j]
                itemp = ((newflrht - xlvl) / (ylvl-xlvl)) * (ytemp-xtemp) + xtemp
                
                tnode_.grammar.type['interpolate_temperature'].append(itemp)
                tnode_.grammar.type['interpolate_srf_geom'].append(srfgeom)
                tnode_.grammar.type['interpolate_cpt'].append(int_cpt)
                srf_normal = node_min.loc[0].grammar.type['processed_srf_normal'][0]
                tnode_.grammar.type['interpolate_srf_normal'].append(srf_normal)
                #srf = srflst[j]
                
        """    
        #for i in xrange(len(therm_node_lst)):
        #    zone = therm_node_lst[i]
        #    print zone.grammar.type['flr_ht']#['is_interzone']
        print '--'
        """
        """
            if bemnode.grammar.type['is_interzone']:
                #Find ref nodes    
                srflst = srfnode.grammar.type['processed_srf']
                templst = srfnode.grammar.type['processed_srf_data']
                srfcptlst = map(lambda srf: srf.cenPt,srflst)
                debug.extend(srfcptlst)
                
                print bemnode.grammar.type['flr_ht']
        """
        return tnode_
    def filter_nodes(self,tnode,PD_):
        debug = sc.sticky['debug']
        tnode.grammar.type['grammar'] = 'filter_nodes'
        ref_long = PD_['dim_long']
        ref_short = PD_['dim_short']
        flip = PD_['flip']
        tol = PD_['tol']
        
        if ref_long==None: ref_long=False
        if ref_short==None: ref_short=False
        
        longshort = tnode.shape.get_long_short_axis()
        shp_short = longshort[3]
        shp_long = longshort[1]
        
         
        if ref_long: ref_long += tol
        if ref_short: ref_short += tol
        
        ref_short += tol
        if shp_short < ref_short and shp_long < ref_long:
            tnode.grammar.type['freeze'] = True
        elif ref_long and shp_long < ref_long:
            tnode.grammar.type['freeze'] = True
        elif ref_short and shp_short < ref_short:
            tnode.grammar.type['freeze'] = True
        
        if flip==True:
            tnode.grammar.type['freeze'] = not tnode.grammar.type['freeze']
        return tnode
    def stepback(self,tnode,PD_):
        debug = sc.sticky['debug']
        ## Ref: TT['stepback'] = [(ht3,sb3),(ht2,sb2),(ht1,sb1)]
        tnode.grammar.type['grammar'] = 'stepback'
        sb_ref = PD_['stepback_ref']
        sb_data = PD_['stepback_data'] #height:stepback
        sb_random = PD_['stepback_randomize']
        sb_dir = PD_['stepback_dir']
        sb_dist_tol = PD_['stepback_tol']
        if sb_dist_tol == None: sb_dist_tol = 10.0
        sb_ref_tol = 15.0
        IsInsideTol = True
        S = Shape()
        
        #Clean/Define the Inputs

        ##sb_data: [(height,distance),(height,distance)...]     :
        #Parse setback data
        for i,sbd in enumerate(sb_data):
            sb_data[i] = map(lambda s: float(s), sbd.split(':'))
        #Parse setback_randomize
        if sb_random:
            random_bounds = sb_random.split(':')
            for i,rb in enumerate(random_bounds):
                random_bounds[i] = map(lambda r: int(float(r)),rb.split('>'))
            randht_lo,randht_hi = random_bounds[0][0],random_bounds[0][1]
            randsb_lo,randsb_hi = random_bounds[1][0],random_bounds[1][1]

        if sb_dir == "side":
            IsSide = True
            sb_dir = None
        else:
            IsSide = False
        if not sb_dir:sb_dir = False

        #Get data if not geometry
        
        IsSelf = True if sb_ref[0] == -1 else False
        sbg_type = self.helper_get_type(sb_ref[0])
        if sbg_type != "geometry":
            sb_node_ref = self.helper_get_ref_node(sb_ref[0],tnode)
            #print sb_node_ref, sb_ref[0]
            #debug.append(sb_node_ref.shape.geom)
            axis_matrix = sb_node_ref.shape.set_base_matrix()
            line_lst = []
            for vectors in axis_matrix:
                line =  rc.Geometry.Curve.CreateControlPointCurve(vectors,0)
                line_lst.append(line)
            sb_ref = line_lst
        
        ##Check region not work!
        """ 
        #Add a check for street tolerance if geometry
        if sbg_type == "geometry":
            if not tnode.grammar.type.has_key('street_tolerance_curve'):
                tnode.grammar.type['street_tolerance_curve'] = []
            for i in xrange(len(sb_ref)):
                sbrefline = sb_ref[i]
                perppts = tnode.shape.offset_perpendicular_from_line(sbrefline,sb_dist_tol)
                streetoffcrv = rc.Geometry.Curve.CreateControlPointCurve(perppts,1)
                tnode.grammar.type['street_tolerance_curve'].append(streetoffcrv)
                IsIntersect = tnode.shape.check_region(streetoffcrv,realvalue=True)
                #if disjoint==setrel: return 0
                #elif intersect==setrel:return 1
                #elif AInsideB==setrel:return 2
                #else: return 3
                if self.is_near_zero(IsIntersect):
                    IsInsideTol = False
                    break
        """
        
        ## Loop through the height,setback tuples
        #rename tnode
        node2cut = self.helper_UI_geom(tnode)
        
        #Loop through the stepback dimensions
        for sb_index in xrange(len(sb_data)):
            #not IsSelf and not IsInsideTol:
            #    break
            sbd = sb_data[sb_index]
            ht, dist = sbd[0], sbd[1]
            
            IsHighEnough = ht < node2cut.shape.ht
            
            if IsHighEnough and sb_random:
                if not self.is_near_zero(randht_lo) and not self.is_near_zero(randht_hi):
                    ht += random.randrange(randht_lo,randht_hi)
                if not self.is_near_zero(randsb_lo) and not self.is_near_zero(randsb_hi):
                    dist += random.randrange(randsb_lo,randsb_hi)

            ##Now actually implement setback
            sh_top_node = node2cut
            
            if not IsHighEnough:
                break
            
            #Get self matrix to match
            matrix = sh_top_node.shape.base_matrix
            if not matrix:
                matrix = sh_top_node.shape.set_base_matrix()

            if IsSelf:
                if IsSide:
                    mi1 = int(random.randrange(0,len(matrix)))
                    if random.randrange(0,2)==1:
                        if mi1 < len(matrix)-1:
                            mi2 = mi1 + 1
                        else:
                            mi2 = mi1 - 1
                        matrix = [matrix[mi1],matrix[mi2]]
                    else:
                        matrix = [matrix[mi1]]

                matrix = map(lambda ptlst:map(lambda pt:rc.Geometry.Point3d(pt[0],pt[1],ht),ptlst),matrix)
                ref_edge = matrix
                #debug.extend(reduce(lambda x,y:x+y,matrix))
            elif sbg_type == "geometry":##need to rethink this
                ref_edge = sh_top_node.shape.match_edges_with_refs(matrix,sb_ref,ht,dist_tol=sb_dist_tol,angle_tol=sb_ref_tol,to_front=not sb_dir)
            else:
                ref_edge = sb_ref
            
            #loop through steback-data-applied ref edges and cut the input geometry
            for sbg in ref_edge:
                cut_geom = None
                #if self.is_near_zero(ht):
                    
                if type([])==type(sbg):
                    sbref_crv = rc.Geometry.Curve.CreateControlPointCurve(sbg,0)
                else:
                    sbg = rs.MoveObject(sc.doc.Objects.AddCurve(sbg),[0,0,ht])
                    sbg = rs.coercecurve(sbg)
                    sbref_crv = sbg
                
                #Doesn't work for some reason!!
                #ptend,ptstart = copy.copy(sbref_crv.PointAtEnd),copy.copy(sbref_crv.PointAtStart)
                #ptend.Z,ptstart.Z = 0.,0.
                #chkcrv = rc.Geometry.Curve.CreateControlPointCurve([ptend,ptstart],0)
                #Check if refedge interesects the input geometry
                #intcrv = rc.Geometry.Intersect.Intersection.CurveCurve(sh_top_node.shape.bottom_crv,chkcrv,0.01,0.01)
                #if self.is_near_zero(intcrv.Count):
                
                try:
                    cut_geom = sh_top_node.shape.op_split("EW",0.5,deg=0.,\
                                        split_depth=float(dist*2.),split_line_ref=sbref_crv)
                except:
                    pass
                #print len(cut_geom)
                #print '--'
                if cut_geom:
                    IsCut = True
                    sh_top_node.shape.geom = cut_geom[0]
                    sh_top_node.shape.reset(xy_change=True)
            node2cut = sh_top_node
            
        
        return tnode
    def transform(self,temp_node_,PD_):
        debug = sc.sticky['debug']
        temp_node_.grammar.type['grammar'] = 'transform_move'
        move_vector = PD_['transform_move']
        basematrix = temp_node_.shape.base_matrix
        if not basematrix:
            basematrix = self.set_base_matrix()

        transform_matrix = temp_node_.shape.vector_to_transformation_matrix(move_vector)
        moved_pts = temp_node_.shape.multiply_matrix2matrix(basematrix,transform_matrix)
        """
        for t in transform_matrix:
            print t
        print '--'
        for b in basematrix:
            print map(lambda c: round(c,2),b[0])
        print '--'
        for p in moved_pts:
            print map(lambda c: round(c,2),p)
        """
        rule_stack = temp_node_.grammar.make_rule_stack(temp_node_)

        moved_pts = map(lambda v: rc.Geometry.Point3d(v[0],v[1],v[2]),moved_pts)
        moved_pts += [moved_pts[0]]
        new_crv = rc.Geometry.Curve.CreateControlPointCurve(moved_pts,1)
        debug.extend(moved_pts)
        debug.append(new_crv)
        childnode = self.helper_geom2node(new_crv,parent_node=temp_node_,grammar="null")
        temp_node_.loc.append(childnode)
        return temp_node_
    def helper_divide_through_normal(self,temp_node_,dist_):
        #Need to rewrite this so all variables in divide is null
        #and option to orient results vertically exists
        #Divides based on 'height'
        #print 'helperdividethroughnormal chk'
        debug = sc.sticky['debug']
        bottom_shape,top_shape = None, None
        ratio_ = (dist_ - temp_node_.shape.cpt[2])/temp_node_.shape.z_dist
        
        PD = {}
        PD['div_num'] = 1
        PD['div_deg'] = 0.
        PD['div_cut'] = 0.
        PD['div_ratio'] = ratio_
        PD['div_type'] = 'simple_divide'
        PD['axis'] = "Z"
        temp_node_ = self.divide(temp_node_,PD)
        
        if temp_node_.loc:
            ext_pt = temp_node_.shape.cpt + (temp_node_.shape.normal * dist_)
            dist_0 = temp_node_.loc[0].shape.cpt - ext_pt
            dist_1 = temp_node_.loc[1].shape.cpt - ext_pt

            if dist_0.Length > dist_1.Length:
                bottom_shape = temp_node_.loc[0]
                top_shape = temp_node_.loc[1]
            else:
                bottom_shape = temp_node_.loc[1]
                top_shape = temp_node_.loc[0]
            #mark top ##this should be an automatic check in helpergeom2node or clonenodes
            #lst_top_nodes = temp_node_.backtrack_tree(lambda n:n.grammar.type['top'],accumulate=True)
            #for tn in lst_top_nodes: tn.grammar.type['top'] = False
            #top_shape.grammar.type['top'] = True
        return bottom_shape,top_shape
    def divide(self,node,PD_):
        def helper_subdivide_depth(hnode,div,div_depth,ratio_,axis_ref="NS"):
            #print 'divdepth, div', div_depth,',', div
            # stop subdivide
            if int(div_depth) >= int(div) or abs(div-0.) <= 0.01:
                haxis,hratio = axis_ref,0.
            # start subdivide
            elif int(div_depth) == 0 and int(div) > 0:
                haxis,hratio = axis_ref,ratio_
            # alternate subdivide by axis
            elif "NS" in hnode.parent.grammar.type['axis']:
                haxis,hratio = "EW",ratio_
            elif "EW" in hnode.parent.grammar.type['axis']:
                haxis,hratio = "NS",ratio_
            hnode.grammar.type['axis'] = haxis
            hnode.grammar.type['ratio'] = hratio
            return hnode
        def helper_subdivide_depth_same(hnode,div,div_depth,ratio_,axis_ref="NS"):
            # base case: stop subdivide
            if int(div_depth) >= int(div) or abs(div-0.) <= 0.01:
                haxis,hratio = axis_ref,0.
            # alternate subdivide by axis
            elif float(div_depth) < 0.5 and int(div) > 0.01:
                haxis,hratio = axis_ref,ratio_
            # alternate subdivide by axis
            else:
                haxis,hratio = node.parent.grammar.type['axis'],0.5
            hnode.grammar.type['axis'] = haxis
            hnode.grammar.type['ratio'] = hratio
            return hnode
        def helper_subdivide_dim(hnode,div,div_depth,ratio_,axis_ref="NS",tol_=3.):
            def equals(a,b,tol=int(3)):
                return abs(a-b) <= tol
            def greater(a,b,tol=int(3)):
                checktol = abs(a-b) <= tol
                return a >= b and not checktol
            ss = hnode.shape
            tol_ = 2.5
            grid_x, grid_y = float(div[0]), float(div[1])
            #print 'g', grid_x, grid_y
            #print 'gref', ss.y_dist, ss.x_dist

            if greater(ss.y_dist,grid_y,tol_):
                haxis = "EW"
                hratio = grid_y/float(ss.y_dist)
            elif greater(ss.x_dist,grid_x,tol_):
                haxis = "NS"
                hratio = grid_x/float(ss.x_dist)
            else:
                haxis,hratio = axis_ref,0.
            #print haxis, hratio
            #print '--'
            hnode.grammar.type['axis'] = haxis
            hnode.grammar.type['ratio'] = hratio
            return hnode
        def helper_simple_divide(hnode,div_,div_depth_,ratio_,axis_ref="NS"):
            hnode.grammar.type['axis'] = axis_ref
            hnode.grammar.type['ratio'] =ratio_
            return hnode
        def helper_divide_recurse(node_,grid_type_,div_,div_depth_,cwidth_,ratio_,axis_,count):
            ## Split, make a node, and recurse.
            if grid_type == "subdivide_depth":
                node_ = helper_subdivide_depth(node_,div_,div_depth_,ratio_,axis_ref=axis_)
            elif grid_type == "subdivide_depth_same":
                node_ = helper_subdivide_depth_same(node_,div_,div_depth_,ratio_,axis_ref=axis_)
            elif grid_type == "subdivide_dim":
                node_ = helper_subdivide_dim(node_,div_,div_depth_,ratio_,axis_ref=axis_)
            else:#simple_divide
                node_ = helper_simple_divide(node_,div_,div_depth_,ratio_,axis_ref=axis_)

            if count >=200.:
                pass
            elif node_.grammar.type['ratio'] > 0.0001:
                #node_.grammar.type['ratio'] = 1. - node_.grammar.type['ratio']
                #debug.extend(node_.shape.bbpts)
                loc = node_.shape.op_split(node_.grammar.type['axis'],node_.grammar.type['ratio'],0.,split_depth=cwidth_)
                #debug.extend(loc)
                #print len(loc)
                for i,child_geom in enumerate(loc):
                    #print 'child nodes'
                    ###debug.append(child_geom)
                    child_node = self.helper_geom2node(child_geom,node_)
                    #print child_node.shape.x_dist
                    #print child_node.shape.y_dist
                    if child_node: node_.loc.append(child_node)
                
                #node_.grammar.dispose_geom(node_)
                
                #print loc
                #print '----'
                if 'simple_divide' not in grid_type:
                    for nc in node_.loc:
                        helper_divide_recurse(nc,grid_type,div_,div_depth_+1,cwidth_,ratio_,axis_,count+1)

        node.grammar.type['grammar'] = 'divide'
        debug = sc.sticky['debug']
        if type(PD_)==type([]):
            div = PD_[0]
            div_deg = PD_[1]
            cut_width = PD_[2]
            ratio = PD_[3]
            grid_type = PD_[4]
            axis = PD_[5]
        else:
            div = PD_['div_num']
            div_deg = PD_['div_deg']
            cut_width = PD_['div_cut']
            ratio = PD_['div_ratio']
            grid_type = PD_['div_type']
            axis = PD_['axis']
        tree_depth = 0.
        helper_divide_recurse(node,grid_type,div,tree_depth,cut_width,ratio,axis,0)
        return node
    def helper_normal2extsrf(self,temp_node_):
        def get_colinear_line(refnode_,tn_):
            def get_max_magnitude(lst):
                max_index = 0
                max_dist = rs.Distance(lst[0][0],lst[0][1])
                for i,ln in enumerate(lst[1:]):
                    dist = rs.Distance(ln[0],ln[1])
                    if dist > max_dist:
                        max_dist = dist
                        max_index = i+1
                lst = [lst[max_index]]
                return lst
            ## Input refnode, and tn
            ## Outputs the lines of tn that are colinear to refnode
            ## Loop through all lines in refshape
            ## Loop through all lines in tempnode
            ## if colinear line, add to colinear_lst
            ref_base = refnode_.shape.set_base_matrix()
            foo_colinear = refnode_.shape.check_colinear_pt
            colinear_lst = []
            newht = tn_.shape.cpt[2]
            n_matrix = tn_.shape.set_base_matrix()
            check_x = False
            check_y = False
            for line in ref_base:
                newline = map(lambda p: [p[0],p[1],newht],line)
                refcrv = rs.coercecurve(rs.AddLine(newline[0],newline[1]))
                ##debug.append(refcrv)
                for nline in n_matrix:
                    pt_0 = foo_colinear(refcrv,nline[0],tol=0.5)
                    pt_1 = foo_colinear(refcrv,nline[1],tol=0.5)
                    if pt_0 and pt_1:
                        colinear_lst.append(nline)
            if len(colinear_lst) < 1:
                colinear_lst = get_max_magnitude(tn_.shape.base_matrix)
            if len(colinear_lst) > 1:
                colinear_lst = get_max_magnitude(colinear_lst)
            return colinear_lst.pop(0)
        def get_normal_to_exterior_vector(parallel2ext):
            ## Take cross product ccw * [0,0,1] vector
            ## solution vector is inward pointing vector
            ccw_vec = parallel2ext[1] - parallel2ext[0]
            up_vec = rc.Geometry.Vector3d(0,0,1)
            cross = rc.Geometry.Vector3d.CrossProduct(ccw_vec,up_vec)
            return cross

        ## Takes a node and finds the vector perpendicular to the surface
        ## pointing inward, relative to the rootnode surface
        ## This should be abstracted and moved to shape class
        debug = sc.sticky['debug']
        temp_node_.traverse_tree(lambda n: n,internal=False)
        ref_node = temp_node_.get_root()
        parallel2refext = get_colinear_line(ref_node,temp_node_)
        #line = rs.AddLine(parallel2refext[0],parallel2refext[1])
        ##debug.append(line)
        normal2srf = get_normal_to_exterior_vector(parallel2refext)
        return normal2srf
    def separate_by_dist(self,temp_node_,PD_):
        def helper_simple_divide(lstvalidshape_,dimkeep,dimaxis,xkeep,ykeep):
            #Now cut the valid shapes
            #lstvalidshape_ : list of valid shapes
            #dimkeep: dimension we are initially cutting
            #dimaxis: axis we are cutting along (EW or NW)
            #print '---'
            VL = []
            for validshape_index in xrange(len(lstvalidshape_)):
                validshape = lstvalidshape_[validshape_index]
                
                #Check shape dim validity and break if not valid
                min_area = xkeep * ykeep
                dim2chk_xy = (xkeep,ykeep)
                #print round(validshape.shape.x_dist,2), round(validshape.shape.y_dist,2)
                #pv = validshape.shape.primary_axis_vector
                #print validshape.shape.vector2axis(pv)
                #print '--'
                #Remember, xkeep=shortdim, ykeep=longdim
                if validshape.shape.x_dist > validshape.shape.y_dist:
                    dim2chk_xy = (ykeep,xkeep)
                
                IsDimValid = validshape.shape.check_shape_validity(dim2chk_xy,min_area,min_or_max_="min",tol_=1.)
                #print '---'
                #print dimkeep
                #print xkeep,ykeep
                #print round(validshape.shape.x_dist,1),round(validshape.shape.y_dist,1)
                #print IsDimValid
                
                if IsDimValid == False:
                    continue
                
                #Check if we are cutting in dirn of primary axis
                #B/c will use shape-fitting optimization here
                dir_cut = 1           
                vs = validshape.shape
                vsht = vs.cpt[2]
                valid_vec = vs.primary_axis_vector
                valid_axis = vs.vector2axis(valid_vec)
                OUT_LST = []
                
                #Get validshape matrix
                valid_matrix = vs.base_matrix
                if not valid_matrix: valid_matrix = vs.set_base_matrix()
                #Get outerref matrix
                outer_ref = self.helper_get_ref_node(0,validshape)
                outer_matrix = outer_ref.shape.base_matrix
                if not outer_matrix: outer_matrix = outer_ref.shape.set_base_matrix()
                #valid_matrix = n sides
                #outer_matrix = m sides
                outer_crv_lst = []
                for i in xrange(len(outer_matrix)):
                    outer_edge = outer_matrix[i]
                    for j in xrange(len(outer_edge)): outer_edge[j].Z = vsht
                    outer_crv = rc.Geometry.Curve.CreateControlPointCurve(outer_edge)
                    #debug.append(outer_crv)
                    outer_crv_lst.append(outer_crv)
                    
                edge_pts = vs.match_edges_with_refs(valid_matrix,outer_crv_lst,norm_ht=vsht,dist_tol=10.0,angle_tol=5.0,to_front=True)
                if edge_pts:
                    out_vec = edge_pts[0][1] - edge_pts[0][0]
                    edge_crv = rc.Geometry.Line(edge_pts[0][0],edge_pts[0][1])
                    #debug.append(edge_crv)
                    OUT_LST.append((out_vec,edge_crv))
                
                for out in OUT_LST:
                    out_axis = vs.vector2axis(out[0])
                    if out_axis == dimaxis:
                        if dimaxis=="NS":
                            p1,p2 = vs.e_ht[0],vs.e_ht[1]
                        else:
                            p1,p2 = vs.s_wt[0],vs.s_wt[1]
                        closept = rc.Geometry.Line.ClosestPoint(out[1],p1,0.0)
                        if not self.is_near_zero(rs.Distance(closept,p1),1):
                            dir_cut = 0
                
                simple_ratio = validshape.shape.calculate_ratio_from_dist(dimaxis,dimkeep,dir_=dir_cut)
                #print simple_ratio
                #print '---'
                
                
                validshape_param_lst = [1.,0.0,0.,simple_ratio,"simple_divide",dimaxis]
                try:
                    self.divide(validshape,validshape_param_lst)
                except:
                    pass
                validchilds = validshape.traverse_tree(lambda n:n, internal=False)
                VL.extend(validchilds)
            return VL
        def separate_dim(temp_node_topo_,x_keep_omit_,y_keep_omit_,cut_axis,cut_axis_alt):
            #Axis issue:
            #cut_axis: axis that cuts perpendicular to primary axis of shape
            #EW will cut y_dist
            #NS will cut x_dist
            #In bibil - y_axis (cutting EW) is always set as the primary axis.

            #Prep inputs
            #xkeep is always < ykeep
            x_keep_,x_omit_ = x_keep_omit_[0],x_keep_omit_[1]
            y_keep_,y_omit_ = y_keep_omit_[0],y_keep_omit_[1]
            
            #Make first division
            divbydim = (x_keep_+x_omit_,y_keep_+y_omit_)
            dummy_ratio, dummy_axis, dummy_deg = 0.5, "NS", 0.
            param_lst = [divbydim,dummy_deg,0.,dummy_ratio,"subdivide_dim",dummy_axis]
            try:
                self.divide(temp_node_topo_,param_lst)
            except:
                pass
            ##Now recursively divide once for dim keep and check dim...
            shape2keep_lst = []
            shape2omit_lst = []

            #Set inputs for simple divide
            topo_child_lst = temp_node_topo_.traverse_tree(lambda n:n, internal=False)
            #debug.extend(map(lambda n:n.shape.geom,topo_child_lst))
            #EW checks x_dist, NS checks y_dist << THIS SHOULD BE CHANGED TO HAVE SAME NAME
            if "EW" in cut_axis:##then the we are cutting y axis, give y dims
                dimprimekeep = y_keep_
                dimsecondkeep = x_keep_
                
            else:
                dimprimekeep = x_keep_
                dimsecondkeep = y_keep_
            
            lstfirkeepnodes = helper_simple_divide(topo_child_lst,dimprimekeep,cut_axis,x_keep_,y_keep_)
            lstseckeepnodes = helper_simple_divide(lstfirkeepnodes,dimsecondkeep,cut_axis_alt,x_keep_,y_keep_)
            #debug.extend(map(lambda n:n.shape.geom,lstseckeepnodes))
            for i in xrange(len(lstseckeepnodes)):
                final_node = lstseckeepnodes[i]
                min_area = x_keep_ * y_keep_
                div2keep = (x_keep_,y_keep_)
                IsValidDimKeepOmit = final_node.shape.check_shape_validity(div2keep,min_area,tol_=2.)
                chkMin = False
                if final_node.shape.x_dist >= (x_keep_-2.) and final_node.shape.y_dist >= (y_keep_-2.):
                    chkMin = True
                if IsValidDimKeepOmit and chkMin==True:
                    shape2keep_lst.append(final_node)
                else:
                    shape2omit_lst.append(final_node)
            #debug.extend(map(lambda n: n.shape.geom,shape2keep_lst))
            return shape2omit_lst,shape2keep_lst
        def check_base_with_offset(shape2off,GLOBLST):
            # check if interect with tower-seperation list
            IsSeparate_ = True
            for offset in GLOBLST:
                chkoff = rs.coercecurve(offset)
                if chkoff!=None:
                    crvA = chkoff
                    crvB = shape2off.shape.bottom_crv
                    #debug.append(chkoffset)
                    setrel = shape2off.shape.check_region(crvA,crvB,tol=0.1)
                    #If not disjoint
                    #if not abs(setrel-0.)<=0.1:
                    #    debug.append(crvB)
                    #    debug.append(crvA)
                    if not abs(setrel-0.)<=0.001:
                        IsSeparate_ = False
                        break
            return IsSeparate_
        def set_separation_record(shape2record,sep_dist,separation_tol_):
            ## Add some tolerance to separation distance
            sep_dist_tol = (sep_dist - separation_tol_) * -1
            try:
                sep_crv = shape2record.shape.op_offset_crv(sep_dist_tol,corner=3)
            except Exception as e:
                print str(e)
                print 'Error at set_separation_record'
            #debug.append(check_base_separation_.shape.bottom_crv)
            debug.append(sep_crv)
            ## Append crv
            sc.sticky['GLOBAL_COLLISION_LIST'].append(sep_crv)

        debug = sc.sticky['debug']
        temp_node_.grammar.type['grammar'] = 'separate'
        #Extract data
        x_keep_omit = PD_['x_keep_omit']
        y_keep_omit = PD_['y_keep_omit']
        #Check collision detection
        add_collision = PD_['add_collision']
        
        #Parse the data
        x_keep_omit = map(lambda s: float(s), x_keep_omit.split(','))
        y_keep_omit = map(lambda s: float(s), y_keep_omit.split(','))
        
        temp_node_topo = temp_node_#copy.deepcopy(sep_ref_node)

        ## Get normal to exterior srf
        try:
            normal2srf = self.helper_normal2extsrf(temp_node_topo)
            cut_axis = temp_node_topo.shape.vector2axis(normal2srf)
        except:
            cut_axis = "NS"
        noncut_axis = "EW" if "NS" in cut_axis else "NS"

        ## Get cut dimensions
        shapes2omit,shapes2keep = separate_dim(temp_node_topo,x_keep_omit,y_keep_omit,cut_axis,noncut_axis)

        #print temp_node_topo,x_keep_omit,y_keep_omit
        #debug.append(temp_node_topo.shape.geom)

        for i in xrange(len(shapes2omit)):
            omit = shapes2omit[i]
            omit.delete_node()
            del omit

        temp_node_topo.loc = []
        
        if shapes2keep:
            #Flatten tree
            temp_node_topo = self.flatten_node_tree_single_child(shapes2keep,temp_node_topo,grammar="shape2keep",empty_parent=True)
            #temp_node_topo = self.flatten_node_tree_single_child(shapes2omit,temp_node_topo,grammar="shape2omit",empty_parent=False)

            # Make/call global collision list
            if not sc.sticky.has_key('GLOBAL_COLLISION_LIST'):
                sc.sticky['GLOBAL_COLLISION_LIST'] = []
            if add_collision != []:
                sc.sticky['GLOBAL_COLLISION_LIST'].extend(add_collision)
            
            #This needs a rewrite.
            sc.sticky['GLOBAL_COLLISION_LIST'] = []
            #print 'GLOBAL_COLLISION', sc.sticky['GLOBAL_COLLISION_LIST']
            
            offset_dist = x_keep_omit[1]
            seperate_tol = 0.5
            # Check shape separation
            for i,t in enumerate(temp_node_topo.loc):
                if 'keep' in t.grammar.type['grammar']:
                    GLOBAL_LST = sc.sticky['GLOBAL_COLLISION_LIST']
                    GLOBAL_LST = filter(lambda offcrv: offcrv!=None,GLOBAL_LST)
                    isSeperate = check_base_with_offset(t,GLOBAL_LST)
                    if isSeperate == True:
                        #offset_tuple
                        set_separation_record(t,offset_dist,seperate_tol)
                    else:
                        temp_node_topo.loc[i] = None
                        t.delete_node()
                        del t
                        #t.grammar.type['grammar'] = 'omit'
                else:
                    temp_node_topo.loc[i] = None
                    t.delete_node()
                    del t
                    #t.grammar.type['grammar'] = 'omit'
        else:
            temp_node_topo.loc = []

        temp_node_topo.loc = filter(lambda n:n!=None,temp_node_topo.loc)

        ##TEMP4MEETING
        #for i,t in enumerate(temp_node_topo.loc):
        #    if not 'keep' in t.grammar.type['grammar']:
        #        temp_node_topo.loc[i] = None
        #        debug.append(t)
        #temp_node_topo.loc = filter(lambda n:n!=None,temp_node_topo.loc)
        if temp_node_topo.loc == []:
            temp_node_topo.grammar.type['freeze'] = True
        #print 'freeze?', temp_node_topo.grammar.type['freeze']
        return temp_node_topo
    def extract_slice(self,temp_node_,PD_):
        def extract_topo(n_,ht_):
            childn = None
            if ht_ < 0.2:
                n_ = self.helper_UI_geom(n_)
                childn = self.helper_geom2node(n_.shape.bottom_crv,n_,'extracted_slice')
                n_.loc.append(childn)
            try:
                refpt = copy.copy(n_.shape.cpt)
                refpt.Z = ht_ - 1.0
                #refpt = rs.AddPoint(pt[0],pt[1],ht_)
                topcrv = n_.shape.get_bottom(n_.shape.geom,refpt)
                topcrv=sc.doc.Objects.AddCurve(topcrv)
                movetopcrv = n_.shape.move_geom(topcrv,rc.Geometry.Vector3d(0,0,1.))
                movetopcrv = rs.coercecurve(movetopcrv)
                #debug.append(movetopcrv)
                childn = self.helper_geom2node(movetopcrv,n_,'extracted_slice')
                n_.loc.append(childn)
            except:
                pass
            return childn
        temp_node_.grammar.type['grammar'] = 'extract_slice'
        debug = sc.sticky['debug']
        ## Warning: this function will raise height of geom 1m.
        slice_ht = PD_['extract_slice_height']
        #IsTop = False
        #Check inputs
        if type(slice_ht) != type([]): slice_ht = [slice_ht]
        if slice_ht == [] or slice_ht == [None]:
            slice_ht = ['max']
            ##unsure about this but works for now...
            #IsTop = temp_node_.backtrack_tree(lambda n:n.grammar.type['top'])
        if slice_ht:
            if self.helper_get_type(slice_ht[0]) == "string":
                if slice_ht[0] == 'max':
                    slice_ht = [temp_node_.shape.ht]
                else:
                    slice_ht = map(lambda s: float(s),slice_ht)
                
            #Extract topo
            for slht in slice_ht:
                chld = extract_topo(temp_node_,slht)
        return temp_node_
    def set_height(self,temp_node_,PD_):
        def height_from_bula(n_):
            setht = 6. #default ht = midrise
            bula_node_lst = temp_node_.backtrack_tree(lambda n: n.grammar.type['bula'],accumulate=True)
            #temp
            min_bula_node_sum = None
            min_bula_node_index = None

            for bula_ref_index,bula_node in enumerate(bula_node_lst):
                bula_node_sum = 0
                buladata = bula_node.grammar.type['bula_data']
                lpl_,lvl_, lvl_actual = buladata.set_node_bula_pt_ref(temp_node_,bula_node)

                #for vl_ in lvl_:
                bula_node_min = min(reduce(lambda x,y: x+y,lvl_))

                if min_bula_node_sum == None or min_bula_node_sum > bula_node_min:
                    min_bula_node_sum = bula_node_min
                    min_bula_node_index = bula_ref_index
            buladata = bula_node_lst[min_bula_node_index].grammar.type['bula_data']
            lpl_,lvl_,actual_lvl_ = buladata.set_node_bula_pt_ref(temp_node_,bula_node_lst[min_bula_node_index])
            if lpl_ != [[]]:
                n_ = buladata.generate_bula_point([n_],lpl_,lvl_,actual_lvl_)[0]
                val_lst = n_.grammar.type['bula_data'].value_lst
                setht = min(val_lst)#sum(val_lst)/float(len(val_lst))
            return setht
        #print 'We are setting height!'
        temp_node_.grammar.type['grammar'] = 'height'
        debug = sc.sticky['debug']
        ht_ = PD_['height']
        randomize_ht = PD_['height_randomize']
        ht_ref = PD_['height_ref']

        ### If ht_ and ht_ref have values: then ht_ is taken as a maximum!!
        
        if ht_ref:
            ht_type = self.helper_get_type(ht_ref)
            if ht_type != "geometry":
                ht_ref = self.helper_get_ref_node(ht_ref,temp_node_)
            
            ht_ref = self.helper_UI_geom(ht_ref)
            ht_ref_shape = ht_ref.shape
            
            #Check to make sure ref is not the same
            if abs(ht_ref_shape.ht-temp_node_.shape.ht)>1.0:
                ht_w_ref = ht_ref_shape.ht - temp_node_.shape.ht
            else:
                ht_w_ref = temp_node_.shape.ht
            
            #Check if maxht is defined
            ht_copy = copy.copy(ht_)
            if ht_==True:
                ht_ = ht_w_ref
            else:
                ht_ = ht_w_ref if ht_w_ref <= ht_ else ht_copy
            #print ht_, ht_copy, ht_w_ref

        if randomize_ht:
            random_bounds = map(lambda r: int(float(r)),randomize_ht.split('>'))
            randht_lo,randht_hi = random_bounds[0],random_bounds[1]
            ht_ += random.randrange(randht_lo,randht_hi)
        
        
        n_ = self.helper_UI_geom(temp_node_)
        #n_ = temp_node_
        #print 'labelchk', temp_node_.parent.parent.grammar.type['label']
        if type(ht_)==type('') and 'bula' in ht_:
            setht_ = height_from_bula(n_)
        else:
            setht_ = ht_#- n_.shape.cpt[2] 
        n_.shape.op_extrude(setht_)
        #print '---'
        return temp_node_
    def get_solar_zone(self,start_time,end_time,curve=None,zonetype='envelope'):
        try:
            if type(curve) == type(rs.AddPoint(0,0,0)):
                curve = rs.coercecurve(curve)
            if 'envelope' in zonetype:
                se = ghcomp.DIVA.SolarEnvelope(curve,43.65,start_time,end_time)
            else:
                minhr = end_time-start_time
                se = ghcomp.DIVA.SolarFan(curve,43.65,minhr,263,200.)
            return se
        except Exception as e:
            print "P.op_solar_envelope error"
            print e
    def concentric_divide(self,temp_node_,distlst,dellst,ROOTREF):
        def helper_recurse(curr_node_,rootref_,distlst_,dist_acc,dellst_,lst_ring,diffn,count):
            ##base case: fail chk_offset
            if ROOTREF:
                rootshape = ROOTREF
            else:
                rootshape = 0
            if curr_node_ == None or count > 10:
                if diffn!=None:
                    lst_ring.append(diffn.shape.geom)
                return lst_ring
            else:
                try:
                    dist_ = distlst_.pop(1)
                    shgeom = curr_node_.shape.geom
                    curr_node_ = self.helper_geom2node(shgeom,rootref_)
                    #debug.append(curr_node_.shape.geom)
                    try:
                        diff_node = self.court(curr_node_,rootshape,dist_+dist_acc,slice=True)
                        #dl = diff_node.traverse_tree(lambda n:n,internal=False)
                        #debug.extend(map(lambda n:n.shape.geom,dl))
                    except:
                        pass
                    #fig this out: diff_node.parent = curr_node_.get_root()
                    if dist_ not in dellst_:
                        for cn in curr_node_.loc:
                            lst_ring.append(cn.shape.geom)
                    ## Check diff node dimension and store it
                    if diff_node:
                        chk_EW_dim = diff_node.shape.check_shape_dim("EW",dist_,min_or_max='min')
                        chk_NS_dim = diff_node.shape.check_shape_dim("NS",dist_,min_or_max='min')
                        if chk_EW_dim and chk_NS_dim:
                            diffn = diff_node
                    distlst_.insert(0,dist_)
                    ## Change the relationships
                    return helper_recurse(diff_node,rootref_,distlst_,dist_acc+dist_,dellst_,lst_ring,diffn,count+1)
                except Exception as e:
                    pass#print 'error at concentric', str(e)
        debug = sc.sticky['debug']
        lon = temp_node_.traverse_tree(lambda n: n,internal=False)
        rootref = temp_node_.get_root()

        for subdiv in lon:
            ringlst = helper_recurse(subdiv,rootref,distlst,0.,dellst,[],None,0)
            ringlst = filter(lambda n: n!=None,ringlst)
            ##debug.extend(ringlst)
            for ring in ringlst:
                childnode = self.helper_geom2node(ring,subdiv)
                subdiv.loc.append(childnode)
        return temp_node_
    #Abstract this as helper to parse ref geoms
    def helper_get_type(self,type_ref_):
        type_info = None
        N = Tree()
        S = Shape()
        #Check if number reference to index of depth in binary data tree
        if type_ref_ == None:
            type_info = None
        elif type(type_ref_)==type(""):
            type_info = "string"
        elif type(type_ref_) == type(1) or type(type_ref_) == type(1.):
            type_info = "number"
        elif type(type_ref_) == type(N):
            type_info = "tree"
        elif type(type_ref_) == type(S):
            type_info = "shape"
        else:
            type_info = "geometry"
        return type_info
    def helper_get_ref_node(self,shape_ref_,node_):
        ##Checks the input type and outputs the a Node based on reference
        refshape_ = None
        #Base case
        type_info = self.helper_get_type(shape_ref_)
        if type_info == None:
            refshape_ = node_
        else:
            #Check if number reference to index of depth in binary data tree
            if type_info == "string":
                try:
                    shape_ref_ = int(shape_ref_)
                    type_info = "number"
                except ValueError:
                    node_ = node_.backtrack_tree(lambda n:n.grammar.type['label']==shape_ref_,accumulate=False)
                    type_info = "node"

            if type_info == "number":
                shape_ref_ = int(shape_ref_)
                #positive or zero or negative
                if shape_ref_ > -0.5:
                    refdepth = shape_ref_
                else:
                    refdepth = node_.depth + (shape_ref_ + 1)
                refshape_backtrack = node_.backtrack_tree(lambda n:n.depth==refdepth,accumulate=False)
                if refshape_backtrack:
                    refshape_ = refshape_backtrack
            elif type_info == "node":
                #Check if node
                refshape_ = node_
            #Assume geom
            else:
                try:
                    shape_node = self.helper_geom2node(shape_ref_)
                    refshape_ = shape_node
                except:
                    pass
        #check if nothing matches
        if refshape_ == None:
            refshape_ = node_
        refshape_ = self.helper_UI_geom(refshape_)
        return refshape_
    def flatten_node_tree_single_child(self,lstofchild,parent_ref_node,grammar="null",empty_parent=True):
        #Input list of nodes at different depths, a parent, grammar
        #Create flat list of nodes w/ same parent
        def clean_child_nodes(loc):
            #Clean child nodes of links to parent or childs
            for i,c in enumerate(loc):
                for lc in c.loc:
                    try:
                        del lc.shape.geom
                    except:
                        pass
                    del lc
                c.loc = []
                c.parent = None
                loc[i] = c
            return loc
        if empty_parent == True:
            parent_ref_node.loc = []
        lstofchild = clean_child_nodes(lstofchild)
        for i,n in enumerate(lstofchild):
            n.depth = parent_ref_node.depth+1
            n.parent = parent_ref_node
            lstofchild[i] = n
            if grammar != "null":
                n.grammar.type['grammar'] = grammar
        parent_ref_node.loc.extend(lstofchild)
        return parent_ref_node
    def court(self,temp_node_,PD_):
        def court_slice(curr_node,rootshape,width_,cut_width_):
            def recurse_slice(curr_node_,matrice,valid_node_lst,diff,count,count_subdiv,cut_width__):
                #print count, curr_node_
                cmax = 40.
                tol = 2.
                invalid_node = None
                valid_node = None
                #Base case
                if count >= cmax or curr_node_==None:
                    return valid_node_lst,diff
                else:
                    diff = curr_node_
                    #chk_offset_ = rootshape.op_offset_crv(width_+0.1)
                    matrice_max = False
                    #print 'start---'
                    set_rel = -100
                    #debug.append(curr_node_.shape.geom)
                    for i,line in enumerate(matrice):
                        #print i
                        dirvec = line[1]-line[0]
                        # get magnitude of line
                        dist = math.sqrt(sum(map(lambda p: p*p,dirvec)))
                        if dist <= tol:
                            print 'too small to court slice'
                        if dist > tol:
                            split_crv = rs.AddCurve(line,1)
                            midpt = curr_node_.shape.get_midpoint(line)
                            sc_ = 5,5,0
                            split_crv = rs.ScaleObject(split_crv,midpt,sc_)
                            #Check if refedge interesects the input geometry
                            #This is a huge time saver
                            
                            if self.is_near_zero(cut_width__):
                                intcrv = rc.Geometry.Intersect.Intersection.CurveCurve(curr_node_.shape.bottom_crv,rs.coercecurve(split_crv),0.001,0.001)
                                if self.is_near_zero(intcrv.Count):
                                    #debug.append(rs.coercecurve(split_crv))
                                    #debug.append(curr_node_.shape.bottom_crv)
                                    continue
                            
                            if True:#try:
                                split_node_lst = []
                                split_geoms = curr_node_.shape.op_split("NS",0.5,split_depth=cut_width__,split_line_ref=split_crv)
                                for geom in split_geoms:
                                    #if type(geom)!= type(rootshape.shape.geom):
                                    split_node = self.helper_geom2node(geom,None)
                                    if split_node==None:
                                        pass
                                    else:
                                        split_node_lst.append(split_node)
                                        split_crv = split_node.shape.bottom_crv
                                        #Check if this geom intersects with larger offset.
                                        #if so keep cutting
                                        set_rel = curr_node_.shape.check_region(chk_offset,split_crv,realvalue=True,tol=0.1)
                                        #if disjoint==setrel: return 0
                                        #elif intersect==setrel:return 1
                                        #elif AInsideB==setrel:return 2
                                        #else: return 3
                                        #debug.append(chk_offset)
                                        if self.is_near_zero(set_rel):#if disjoint stop splitting
                                            valid_node = split_node
                                            valid_node_lst.append(valid_node)
                                        else:#keep splitting
                                            #print set_rel
                                            invalid_node = split_node
                                            #debug.append(chk_offset)
                                            #debug.append(split_crv)
                                            #debug.append(split_node.shape.geom)
                            #except:        
                            #    pass## Split fail, so test the next line split
                        #Check if reach max of matrice len
                        matrice_max = len(matrice)==i+1
                        #if invalid_node != None and valid_node != None:
                        if valid_node!=None:
                            #valid_node_lst.append(valid_node)
                            matrice.pop(i)
                            break
                    if matrice_max == True and abs(set_rel-1.)<0.1:
                        #debug.append(curr_node_.shape.geom)
                        chk_offset_out = rootshape.op_offset_crv(width_-1.5)
                        for sn in split_node_lst:
                            split_crv = sn.shape.bottom_crv
                            set_rel = curr_node_.shape.check_region(chk_offset_out,split_crv,tol=0.1)
                            if abs(set_rel-2.)<0.1 and count_subdiv < 1.:
                                try:
                                    L_,diff_ = recurse_slice(sn,shape_matrix,[],None,0,count_subdiv+1,cut_width__)
                                    valid_node_lst.extend(L_)
                                    #debug.extend(map(lambda n:n.shape.geom,L_))
                                except:
                                    pass
                                #debug.append(sn.shape.geom)
                # If the node has been split (invalid_node!= None)
                # OR the node has no valid split lines (invalid_node == None)
                # then we send it back into the recurser.
                return recurse_slice(invalid_node,matrice,valid_node_lst,diff,count+1,count_subdiv,cut_width__)

            ### REWRITE AS EXTRUSION OF BASE_MATRIX
            ### O(2n) complexity time
            offset = rootshape.op_offset_crv(width_)
            ###debug.append(rootshape.bottom_crv)
            chk_offset = rootshape.op_offset_crv(width_+0.21)
            diff = None
            if chk_offset:
                off_node = self.helper_geom2node(offset,curr_node)
                shape_matrix = off_node.shape.set_base_matrix()
                #debug.append(curr_node.shape.geom)
                #debug.append(off_node.shape.geom)
                L,diff = recurse_slice(curr_node,shape_matrix,[],None,0,0,cut_width_)
                #debug.extend(map(lambda n:n.shape.geom,L))
                offset = rs.coercecurve(offset)
                IsInside = offset.Contains(diff.shape.cpt,diff.shape.cplane) == rc.Geometry.PointContainment.Inside
                #if IsInside:
                    #debug.append(diff.shape.geom)
                #print diff
                curr_node = self.flatten_node_tree_single_child(L,curr_node,grammar="courtslice")

            else:
                diff = None
            return diff

        #Unpack the parameters

        temp_node_.grammar.type['grammar'] = 'court'
        court_ref = PD_['court_ref']
        court_width = PD_['court_width']
        court_slice_bool = PD_['court_slice']
        court_randomize = PD_['court_randomize']
        cut_width = PD_['court_cut_width']
        if not cut_width:
            cut_width = 0.
        if court_randomize:
            random_bounds = map(lambda r: int(float(r)),court_randomize.split('>'))
            randct_lo,randct_hi = random_bounds[0],random_bounds[1]
            court_width += random.randrange(randct_lo,randct_hi)

        debug = sc.sticky['debug']
        diff = None
        lon = temp_node_.traverse_tree(lambda n: n,internal=False)

        for subdiv in lon:
            subdiv = self.helper_UI_geom(subdiv)
            subdiv.shape.convert_rc('3d')
            refshape_node = self.helper_get_ref_node(court_ref,subdiv)
            refshape = refshape_node.shape
            if court_slice_bool:
                try:
                    diff = court_slice(subdiv,refshape,court_width,cut_width)
                except Exception as e:
                    print 'Error @ court_slice', str(e)
            elif court_width > 0.:
                try:
                    subdiv.shape.op_offset(court_width,refshape.bottom_crv,dir="courtyard")
                except Exception as e:
                    print 'Error @ court', str(e)
        return diff
    def set_bula_point(self,temp_node_,PD_):

        temp_node_.grammar.type['grammar'] = 'bula'
        #Move this back to Bula as main_bula
        B = Bula()
        S = Shape()
        #Get the inputs
        analysis_ref = PD_['bula_point_lst']
        value_ref = PD_['bula_value_lst']

        ##Check to see what are input combo
        chk_apt = filter(lambda x: x!=None,analysis_ref) != []
        chk_val = filter(lambda x: x!=None,value_ref) != []
        value_ref_actual = None
        #Set defaults or add warnings
        if not chk_apt:
            print 'Analysis inputs are missing!'
            chk_apt = False
        if not chk_val:
            val_num = len(analysis_ref)
            value_ref = [0]*val_num
            chk_val = True
        elif chk_val and type(value_ref[0]) == type(''): #should be more explicit
            #If value is a formula
            if chk_apt:
                value_ref,value_ref_actual = B.apply_formula2points(value_ref,analysis_ref)
        if value_ref_actual == None:
                value_ref_actual = copy.copy(value_ref)
        if chk_apt and chk_val:
            #Convert from guid
            if S.is_guid(analysis_ref[0]):
                analysis_pts = map(lambda p: rs.coerce3dpoint(p),analysis_ref)
            #Sort analysis pts into leaf nodes
            shape_leaves = temp_node_.traverse_tree(lambda n: n,internal=False)
            #shape_leaves = [temp_node_]
            lst_plain_pt_lst, lst_value_lst,lst_value_lst_actual = B.getpoints4lot(shape_leaves,analysis_ref,value_ref,value_ref_actual)
            #Make bula point for each lot
            B.generate_bula_point(shape_leaves,lst_plain_pt_lst,lst_value_lst,lst_value_lst_actual)
            B.set_bula_height4viz(shape_leaves)
        print temp_node_.traverse_tree(lambda n:n,internal=False)
    def meta_tree(self,temp_node_,PD_):
        def inc_depth(n):
            if n.parent:
                n.depth = n.parent.depth + 1
            else:
                n.depth = 0

        temp_node_.grammar.type['grammar'] = 'meta_tree'
        meta_node_lst = PD_['meta_node']
        debug = sc.sticky['debug']
        #THIS SHOULD BE DONE IN TREE CLASS
        #print 'label metanode:', meta_node.parent
        #print 'label currnode: ', temp_node_
        for meta_node in meta_node_lst:
            meta_root = meta_node.get_root()
            IsIn = rs.PointInPlanarClosedCurve(temp_node_.shape.cpt,meta_root.shape.bottom_crv)
            if not IsIn:
                continue
            else:
                temp_root = temp_node_.get_root()
                #Check to make sure we haven't already inserted as root
                chklabel = temp_root.grammar.type['label'] != meta_root.grammar.type['label']
                if chklabel:
                    new_child_node = temp_node_.get_root()
                    #Insert and link both ways
                    meta_node.loc.append(new_child_node)
                    #Give a unique id to meta_node to make sure we don't double ref
                    meta_node.grammar.type['label'] += str(random.randrange(1,1000))
                    #Now reference it
                    new_child_node.parent = meta_node
                    #Reset depths
                    root = meta_node.get_root()
                    root.traverse_tree(lambda n:inc_depth(n),internal=True)
    def bucket_shape(self,temp_node_lst_,PD_):
        def helper_sort_val_by_tol(node_lst,grammar2find,func):
            # Input: node, str, tol, function
            # Extract �grammar� and value foo
            # add foo(value/numofleaves / TOL)
            # add to dictionary if key/not key
            # Output: key:tuple of dictionary
            grammar_dict = {}
            #foo = eval(func)
            for node in node_lst:
                key = node.grammar.type[grammar2find]
                if grammar_dict.has_key(key):
                    grammar_dict[key].append(node)
                else:
                    grammar_dict[key] = [node]
            lstofkeyvaltuple = grammar_dict.items()
            return lstofkeyvaltuple

        def pass_grammar_rules(node_lst,grammar2findlst,funclst):
            # pass grammars to helper
            B = []
            for grammar2find,func in zip(grammar2findlst,funclst):
                lstkeyval = helper_sort_val_by_tol(node_lst,grammar2find,func)
                B.append(lstkeyval)
            return B

        ## Purpose: buckets input shapes
        debug = sc.sticky['debug']
        apply2 = PD_['apply2list']
        keys2bucket = PD_['keys2bucket']#'height','primary_axis_vector']
        fx2bucket = PD_['fx2bucket']

        #Apply grammar key
        for i in xrange(len(temp_node_lst_)):
            temp_node_lst_[i].grammar.type['grammar'] = 'bucket_shape'
        nodes2bucket = temp_node_lst_

        ## Bucket: [(grammar_key,{keyval:lstofnode}),(grammar_key,{keyval:lstofnode})]
        ## keys2find = [key1,key2,key3]

        Bucket = pass_grammar_rules(nodes2bucket,keys2bucket,fx2bucket)
        """
        ###This is for energy archetype identification
        #htfoo = lambda n: str(round(n.shape.ht/9.0,2))
        for n in nodes2bucket:
            lstn = n.backtrack_tree(lambda n_:n_.grammar.type.has_key('ratio'),accumulate=True)
            bucket.append(n.shape.bottom_crv)
            for nl in lstn:
                if 'stepback' in nl.grammar.type['grammar']:
                    #print nl
                    stpd = nl.grammar.type['stepback_data']
                    ht = float(stpd[0][0])+3
                    #print stpd
                    pt = n.shape.cpt
                    refpt = rs.AddPoint(pt[0],pt[1],ht)
                    topcrv = n.shape.get_bottom(n.shape.geom,refpt)
                    #print topcrv
                    #tn = self.helper_geom2node(topcrv)
                    bucket.append(topcrv)
        debug.extend(bucket)
        """
        return Bucket
    def shape2height(self,temp_node_,PD_):
        #TBD
        temp_node_.grammar.type['grammar'] = 'shape2height'
        angle = 0.5
        ht_inc = 3.0
        side_inc = 0.1
        ht = temp_node_.shape.ht
        floor_div = int(math.floor(ht/ht_inc))
        input_node = temp_node_
        for i,fdiv in enumerate(range(floor_div)):
            #print 'fdiv', fdiv
            if fdiv > 10.0:
                inc_angle = angle * -1.0
            else:
                inc_angle = angle
            #print 'angle', inc_angle
            try:
                input_node_with_child = self.squeeze_angle(input_node,inc_angle,ht_inc,side_inc)
                input_node = input_node_with_child.loc[0]
            except:
                print 'error at shape2height'
        loc = temp_node_.traverse_tree(lambda n:n,internal=True)
        loc.pop(0)
        temp_node_ = self.flatten_node_tree_single_child(loc,temp_node_)
        return temp_node_
    def squeeze_angle(self,temp_node_,angle,ht_inc,side_inc):
        #Purpose: Input node, angle degree
        #Output a shape2d with angle chagned according to degree

        ## Prep inputs
        debug = sc.sticky['debug']
        #Get base matrix
        base_matrix = temp_node_.shape.set_base_matrix()
        lines2rotate = [base_matrix[0],base_matrix[1]]
        line2intersect = []

        ## Roteate intersection lines outside
        for i,linept_ in enumerate(lines2rotate):
            if i%2==0:
                heta = False
                basept_index = 0
            else:
                heta = True
                basept_index = 1
            toin = False
            linept_ = temp_node_.shape.rotate_vector_from_axis(angle,linept_,movehead=heta,to_inside=toin)

            ## Increment side length
            if not self.is_near_zero(side_inc,eps=1E-10):
                newdirvec = linept_[1] - linept_[0]
                newdirvec.Unitize()
                sideincvec = newdirvec * side_inc
                orig_vec = linept_[1] - linept_[0]
                extended_vec = orig_vec + sideincvec
                linept_[1] = linept_[0] + extended_vec

            lines2rotate[i] = linept_
            newbasept = lines2rotate[i][basept_index]
            #Getting the perp pt for each rotated line
            perppt = temp_node_.shape.extrude_pt_perpendicular_to_pt(newbasept,linept_)
            if i%2==0:
                perp_linept_ = [perppt,newbasept]
            else:
                perp_linept_ = [newbasept,perppt]
            line2intersect.append(perp_linept_)

        ## Intersect the two lines
        #lines2rotate: first two lines that we rotated
        #line2intersect: lines we are going to intersect
        #Intersecting the lines
        IsIntersect,intpt = temp_node_.shape.get_pt_of_intersection(line2intersect)
        if IsIntersect:
            for i,linept in enumerate(line2intersect):
                if i%2==0:
                    line2intersect[i] = [intpt,linept[1]]
                else:
                    line2intersect[i] = [linept[0],intpt]
            # To perserve the ccw order
            line2intersect = [line2intersect[1],line2intersect[0]]
            # Now add everything together and draw the lines
            base_matrix = lines2rotate + line2intersect
            pts4crv = []
            for i,b in enumerate(base_matrix):
                pts4crv.append(b[0])
            pts4crv += [pts4crv[0]]
            shapecrv = rc.Geometry.Curve.CreateControlPointCurve(pts4crv,1)

            ## Increment height
            if not self.is_near_zero(ht_inc,eps=1E-10):
                htvec = rc.Geometry.Vector3d(0,0,ht_inc)
                shapecrv_guid = sc.doc.Objects.AddCurve(shapecrv)
                movevec = temp_node_.shape.move_geom(shapecrv_guid,htvec)
                shapecrv = rs.coercecurve(movevec)
            ## Mutate the node
            temp_node_child = self.helper_geom2node(shapecrv,parent_node=temp_node_,grammar="squeeze_angle")
            temp_node_.loc.append(temp_node_child)
        return temp_node_
    def straight_skeleton(self,temp_node_,PD_):
        temp_node_.shape.compute_straight_skeleton()
        return temp_node_
    def node2grammar(self,lst_node_,rule_in_,firstUINode=False):
        def helper_type2node(copy_node_,type_):
            #type: list of (dictionary of typology parameters)
            copytype = copy.deepcopy(type_)
            copy_node_.grammar.type.update(copytype)
            return copy_node_
        def helper_clone_node(node_geom,IsUINode=False):
            #Purpose: Create a node from geometry/parent node
            #if geometry, turned into node w/ blank label
            #if node, clone a child node w/ blank label
            if type(T) == type(node_geom):
                # If node create 'clone', new tree, new Grammar, link to same Shape
                childn = self.helper_clone_node(node_geom,parent_node=node_geom)
                node_geom.loc.append(childn)
                n_ = childn
            else:
                n_ = self.helper_geom2node(node_geom,UINode=IsUINode)
            return n_
        ## Purpose: Input list of nodes, applies type
        ## Applies pattern based on types
        ## outputs node
        T = Tree()
        L = []
        DL = []
        #Apply rule to each node
        child_node_lst_ = []
        for i,node_ in enumerate(lst_node_):
            ## Everytime we add a rule, we clone a node.
            ## Every rule mutates the node, or creates child nodes.
            ## If node create 'clone', new tree, new Grammar, link to same Shape
            child_node_ = helper_clone_node(node_,IsUINode=firstUINode)
            if child_node_:
                ## Apply type to node that we will apply rule to
                child_node_ = helper_type2node(child_node_,rule_in_)
                child_node_lst_.append(child_node_)

        ##Check how we apply the rules
        IsApply2Full = rule_in_.has_key('apply2list') and  rule_in_['apply2list'] == True

        #Feed in entire list of nodes
        if IsApply2Full:
            #When we apply full list, we assume we are applying same rule to all nodes
            ParamDict = child_node_lst_[0].grammar.type
            node_out_,dead_node_out_ = self.main_grammar(child_node_lst_,ParamDict)
            RhinoApp.Wait()
            L.extend(node_out_)
            DL.extend(dead_node_out_)
        else:
            for i,child_node_ in enumerate(child_node_lst_):
                ## Apply pattern
                if True:#try:
                    ParamDict = child_node_.grammar.type
                    node_out_,dead_node_out_ = self.main_grammar(child_node_,ParamDict)
                    RhinoApp.Wait()
                    L.extend(node_out_)
                    DL.extend(dead_node_out_)
                #except Exception as e:
                #    print "Error @ node2grammar"


        return L,DL
    def main_grammar(self,temp_node,PD):
        isList = type(temp_node) == type([])

        ## ---- START TEST --- ##
        ## Date 2016 11 30 << if this doesn't pop up delete this check.
        if not isList and temp_node.shape:
            gb = temp_node.shape.geom
            if temp_node.shape.is_guid(gb):
                print 'guid identified in grammar.main_grammar dont delete me!'
                #node.shape.geom = rs.coercebrep(gb)
        ## ---- END TEST --- ##

        if PD.has_key('label_UI') and PD['label_UI'] == True:
            temp_node = self.label(temp_node,PD)
        elif PD.has_key('divide') and PD['divide'] == True:
            temp_node = self.divide(temp_node,PD)
        elif PD.has_key('height') and PD['height']:
            temp_node = self.set_height(temp_node,PD)
        elif PD.has_key('stepback') and PD['stepback'] == True:
            temp_node = self.stepback(temp_node,PD)
        elif PD.has_key('court') and PD['court'] == True:
            self.court(temp_node,PD)
        elif PD.has_key('bula') and PD['bula'] == True:
            self.set_bula_point(temp_node,PD)
        elif PD.has_key('meta_tree') and PD['meta_tree'] == True:
            self.meta_tree(temp_node,PD)
        elif PD.has_key('separate') and PD['separate'] == True:
            temp_node = self.separate_by_dist(temp_node,PD)
        elif PD.has_key('shape2height') and PD['shape2height'] == True:
            temp_node = self.shape2height(temp_node,PD)
        elif PD.has_key('extract_slice') and PD['extract_slice'] == True:
            temp_node = self.extract_slice(temp_node,PD)
        elif PD.has_key('abstract_bem') and PD['abstract_bem'] == True:
            temp_node = self.abstract_BEM(temp_node,PD)
        elif PD.has_key('extract_canyon') and PD['extract_canyon'] == True:
            temp_node = self.extract_canyon(temp_node,PD)
        elif PD.has_key('transform') and PD['transform'] == True:
            temp_node = self.transform(temp_node,PD)
        elif PD.has_key('straight_skeleton') and PD['straight_skeleton'] == True:
            temp_node = self.straight_skeleton(temp_node,PD)
        elif PD.has_key('interpolate_vertical') and PD['interpolate_vertical'] == True:
            temp_node = self.interpolate_vertical(temp_node,PD)
        elif PD.has_key('filter_nodes') and PD['filter_nodes'] == True:
            temp_node = self.filter_nodes(temp_node,PD)
        #Sort out the outputs
        if isList:
            lst_childs = temp_node
        else:
            lst_childs = temp_node.traverse_tree(lambda n:n,internal=False) #change this to based on inoput type
        
        
        ## Check freezing
        dead_lst_childs = filter(lambda n: n.grammar.type['freeze']==True,lst_childs)
        lst_childs = filter(lambda n:n.grammar.type['freeze']==False,lst_childs)
        
        ## Finish
        return lst_childs, dead_lst_childs
    def main_UI(self,node_in_,rule_in_,label__):
        def helper_nest_rules(label_lst_,rule_tree_):
            #Purpose: Extract rules from tree insert nest list of rule dictionaries
            B = Bula()

            #Convert tree to flat list
            #Also we will add label rules to top

            flat_lst = label_lst_
            flat_lst_ = B.ghtree2nestlist(rule_tree_,nest=False)
            flat_lst += flat_lst_

            #Convert flat list to nested list of typology rules
            nest_rdict = []
            rdict = {}#copy.deepcopy(Miru)
            for parselst in flat_lst:
                if parselst[0] != 'end_rule':
                    miru_key,miru_val = parselst[0],parselst[1]
                    rdict[miru_key] = miru_val
                else:
                    nest_rdict.append(rdict)
                    rdict = {}
            #Test
            #for i in nest_rdict:
            #    print 'bula', i['bula']
            #    print 'bula', i['bula_value_lst'][0]
            #    print '---'

            return nest_rdict
        def helper_label2rule(labelin):
            rule_ = []
            if labelin:
                rule_ = [\
                ['label_UI', True],\
                ['label', labelin],\
                ['end_rule']]
            return rule_
        def helper_main_recurse(lst_node_,rule_lst):
            #if no rules/label_rules node is just passed through
            IsFirst = True
            dead_lst_node_ = []
            
            while len(rule_lst) > 0:
                rule_ = rule_lst.pop(0)
                #apply rule to current list of nodes, get child lists flat
                lst_node_leaves, dead_leaves = self.node2grammar(lst_node_,rule_,firstUINode=IsFirst)
                if IsFirst==True:
                    IsFirst = False
                #if len(dead_leaves) > 0.001:
                dead_lst_node_.extend(dead_leaves)
                #if len(lst_node_leaves) > 0.001:
                lst_node_ = lst_node_leaves
                if len(lst_node_leaves) < 0.001:
                    break
            
            for i,ng in enumerate(lst_node_):
                if type(T) != type(ng):
                    ng = self.helper_geom2node(ng)
                    lst_node_[i] = ng
            
            return lst_node_, dead_lst_node_
        T = Tree()
        lst_node_out = []
        dead_node_out = []
        #Check inputs
        chk_input_len = False
        #if node and label are ==
        if abs(len(label__)-len(node_in_)) < 0.5:
            chk_input_len = True
        #if llabel = 1
        elif abs(len(label__)-1.) < 0.5:
            chk_input_len = True
        elif len(label__) <= 0.5:
            chk_input_len = True
        
        #Check if rule has already propogated
        for n in node_in_:
            #If loc exist, then this rule is being reset
            if type(n) == type(T) and len(n.loc) > 0.5:
                for nc in n.loc:
                    nc.delete_node()
                #n.traverse_tree(lambda n:n.delete_node(),internal=True)
                #if n.grammar.type['top'] == None:
                #    n.grammar.type['top'] = True

        if chk_input_len:
            if abs(len(label__)-1.) < 0.5 or abs(len(label__)-0.) < 0.5:
                #label is treated as a rule
                if len(label__) > 0.5:
                    label_rule_ = helper_label2rule(label__[0])
                else:
                    label_rule_ = []
                #nest rules
                nested_rule_dict = helper_nest_rules(label_rule_,rule_in_)
                #make label a rule
                #recursively create a child node derived from parent and apply a grammar rule
                lst_node_out_,dead_node_ = helper_main_recurse(node_in_,nested_rule_dict)   
            
            else:
                #print 'multiple labels'
                #Map label num to label num if multiple labels
                for lab,node_ in zip(label__,node_in_):
                    #label is treated as a rule
                    label_rule_ = helper_label2rule(lab)
                    #nest rules
                    nested_rule_dict = helper_nest_rules(label_rule_,rule_in_)
                    #make label a rule
                    #recursively create a child node derived from parent and apply a grammar rule
                    lst_node_out_,dead_node_ = helper_main_recurse([node_],nested_rule_dict)
            lst_node_out.extend(lst_node_out_)
            dead_node_out.extend(dead_node_)
            
        else:
            print 'Check the length of your inputs'
         
        
        return lst_node_out, dead_node_

if True:
    sc.sticky["Grammar"] = Grammar
