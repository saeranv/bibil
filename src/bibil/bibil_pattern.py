"""
Created on Jun 8, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import random
import scriptcontext as sc
import copy
import System as sys

"""import classes"""
Shape_3D = sc.sticky["Shape_3D"]
Tree = sc.sticky["Tree"] 
Grammar = sc.sticky["Grammar"] 



class Pattern:
    """Pattern"""
    def __init__(self):
        self.lot_lst = []
    def apply_pattern(self,node_,pd_):
        #print 'num', count
        try:
            tempnode = self.main_pattern(node_,pd_)
            return tempnode
        except Exception as e:
            print str(e)
    def helper_geom2node(self,geom,parent_node,label=""):
        def helper_curve2srf(geom_):
            #check if not guid and is a curve
            curve_guid = None
            if type(geom_) != type(rs.AddPoint(0,0,0)):
                points = [rc.Geometry.Point3d(0,0,0),rc.Geometry.Point3d(0,1,0),rc.Geometry.Point3d(1,0,0)]
                curve = rc.Geometry.Curve.CreateControlPointCurve(points,1)
                if geom_.ObjectType == curve.ObjectType: 
                    curve_guid = sc.doc.Objects.AddCurve(geom_)
            else:
                if rs.IsCurve(geom_): 
                    curve_guid = geom_
            if curve_guid:
                srf_guid = rs.AddPlanarSrf(curve_guid)[0]
                rc_brep = rs.coercebrep(srf_guid)
                return rc_brep
            else:
                return geom_     
        debug = sc.sticky['debug']
        child_node = None
        try:
            geom = helper_curve2srf(geom)
            cplane_ref = None
            tree_depth = 0
            
            if parent_node: 
                cplane_ref = parent_node.data.shape.cplane
                tree_depth = parent_node.depth+1
            try:
                child_shape = Shape_3D(geom,cplane=cplane_ref)
            except Exception as e: 
                print 'Bibil has detected a degenerate shape', str(e)
                child_shape = Shape_3D(geom,parent_node.data.shape.cplane)
            
            IsDegenerate = abs(child_shape.x_dist-0.) < 0.0001 or abs(child_shape.y_dist-0.) < 0.0001
            
            if not IsDegenerate:
                if child_shape.z_dist!=None and int(child_shape.z_dist) <= 0.0001:
                    child_shape.op_extrude(12.)
                child_grammar = Grammar(child_shape)
                child_grammar.type["label"] = label
                child_node = Tree(child_grammar,parent=parent_node,depth=tree_depth)
        except Exception as e:
            print "Error at Pattern.helper_geom2node", str(e)
        return child_node               
    def split_brep_zaxis(self,s,ht,splitsrf=None,geom=None,cplane=None):
        try:
            #debug = sc.sticky['debug']
            lst_child = []
            base, top = None, None
            s.convert_guid('3d')
            if not splitsrf:
                splitsrf = rs.AddPlanarSrf([s.bottom_crv])[0]
            if geom == None:
                geom = copy.copy(s.geom)
            if not cplane:
                cplane = s.cplane
            split_surf = rs.CopyObject(splitsrf,[0,0,ht])
            #debug.append(split_surf)
            
            #if ht == 12.: 
                #debug.append(split_surf)
                #debug.append(geom)
            try:lst_child = rs.SplitBrep(geom,split_surf)
            except: print 'splitfail at ht: ', ht
            try: map(lambda child: rs.CapPlanarHoles(child),lst_child)
            except: pass
            if lst_child:
                for i,child in enumerate(lst_child):
                    if rs.IsSurface(child): lst_child[i] = None
                lst_child = filter(lambda c: c != None, lst_child)
                if lst_child and len(lst_child) > 1:
                    first_child_z = rs.BoundingBox(lst_child[0],cplane)[0][2]
                    second_child_z = rs.BoundingBox(lst_child[1],cplane)[0][2]
                    if first_child_z > second_child_z:
                        base = lst_child[1]
                        top = lst_child[0]
                    else:
                        base = lst_child[0]
                        top = lst_child[1]
            return rs.coercegeometry(base), rs.coercegeometry(top)
            #debug.append(rs.coercegeometry(top))
        except Exception as e:
            print e
    def pattern_solar_envelope_uni(self,node_0,time,seht,stype):
        def helper_get_curve_in_tree(node_,stype_,seht_):
            if stype_ == 3:
                noderoot = node_.get_root()
                basecrv = copy.copy(noderoot.data.shape.bottom_crv)
                #debug.append(basecrv)
            else:
                basecrv = copy.copy(node_.data.shape.bottom_crv)
            # Move up to lot_node height
            rc.Geometry.PolyCurve.Translate(basecrv,0.,0.,seht_)
            return basecrv
        
        def helper_intersect_solar(se_,node_,seht_):
            nodegeomlst = node_.data.shape.op_split("Z",seht_/node_.data.shape.z_dist)
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
            node_0.get_root().traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
            ## Get correct curve from data tree
            se_crv = helper_get_curve_in_tree(node_0,stype,seht)
            ## Get base and top
            #split_ratio = seht/node_0.data.shape.z_dist
            #lstchild = node_0.data.shape.op_split("Z",split_ratio)
            #lot_base,lot_top = lstchild[0],lstchild[1]
            ## Generate solar envelope
            #print 'se_crv', se_crv
            se = node_0.data.shape.op_solar_envelope(start,end,se_crv)
            sebrep = helper_intersect_solar(se,node_0,seht)
            #print 'solarbrep', sebrep
            #debug.append(sebrep)
            return sebrep
        except Exception as e:
            print "Error @ pattern_solar_env_uni", str(e)
    def pattern_solar_envelope_multi(self,temp_node_,solartime_,data,solarht_):
        def helper_pattern_solar_envelope_multi(data,time,ht):
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
                #debug.append(srf)
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
                    se = helper_pattern_solar_envelope_multi(subnode.data,solartime_,solarht_)
                    geo_brep = rs.coercebrep(rs.CopyObject(subnode.data.shape.geom))
                    unioned =  rc.Geometry.Brep.CreateBooleanUnion([se,geo_brep],TOL)
                except Exception as e:
                    print "Error at solar_envelope multi"
                    print e
                try: 
                    unioned = unioned[0]
                    subnode.data.shape.geom = unioned
                except: 
                    print 'error multi unioning solartypes'
            return temp_node_
        except Exception as e:
            print "Error at pattern solar envelope multi"
            print e
    def pattern_stepback(self,tnode,stepback_,stepback_node_,sb_ref_):
        ##stepback_: height,recess distance 
        lon_ = tnode.traverse_tree(lambda n: n,internal=False)
        try:
            for i,curr_n in enumerate(lon_):
                node_root = curr_n.get_root()
                ht, dist = stepback_[0], stepback_[1]
                for sbref in sb_ref_:
                    # move sbref
                    move_vector= rc.Geometry.Vector3d(0,0,float(ht))
                    sbref_crv = sc.doc.Objects.AddCurve(sbref)
                    sbref_crv = rs.coercecurve(rs.CopyObject(sbref_crv,move_vector))
                    cut_geom = curr_n.data.shape.op_split("EW",0.5,deg=0.,\
                    split_depth=float(dist),split_line_ref=sbref_crv)  
                    try:
                        curr_n.data.shape.geom = cut_geom[0]
                        curr_n.data.shape.reset(xy_change=True)
                    except Exception as e:
                        print "Error at shape.reset at pattern_stepback",str(e)
        except Exception as e:
            print str(e)#,sys.exc_traceback.tb_lineno 
            print "Error at Pattern.stepback"
        return tnode    
    def pattern_divide(self,node,grid_type,div,axis="NS",random_tol=0,cut_width=0,div_depth=0,ratio=None,flip=False):        
        def helper_calculate_split(hnode,grid_type,div,div_depth,ratio_,axis_ref="NS"):            
            if grid_type == "subdivide_depth":
                #print 'divdepth, div', div_depth,',', div
                # stop subdivide
                if int(div_depth) >= int(div) or abs(div-0.) <= 0.01:
                    haxis,hratio = axis_ref,0.
                # start subdivide
                elif int(div_depth) == 0 and int(div) > 0:
                    haxis,hratio = axis_ref,0.5
                # alternate subdivide by axis
                elif "NS" in hnode.parent.data.type['axis']:
                    haxis,hratio = "EW",0.5
                elif "EW" in hnode.parent.data.type['axis']:
                    haxis,hratio = "NS",0.5
            if grid_type == "subdivide_depth_same":
                # stop subdivide
                if int(div_depth) >= int(div) or abs(div-0.) <= 0.01:
                    haxis,hratio = axis_ref,0.
                # alternate subdivide by axis
                else:
                    haxis,hratio = axis_ref,0.5
            hnode.data.type['axis'] = haxis
            hnode.data.type['ratio'] = hratio
            return hnode
        #print "We are changing recursively!"
        if node.depth >=100: # base case 1
            print 'node.depth > 60'
        else:
            axis_ = axis
            if flip:
                axis_ = "NS" if "EW" in axis else "EW"
            node = helper_calculate_split(node,grid_type,div,div_depth,ratio,axis_ref=axis_)
            if node.data.type['ratio'] > 0.0001:
                loc = node.data.shape.op_split(node.data.type['axis'],node.data.type['ratio'],0.,split_depth=cut_width)
                for i,child_geom in enumerate(loc):
                    child_node = self.helper_geom2node(child_geom,node)
                    if child_node: node.loc.append(child_node)
                for c in node.loc:
                    self.pattern_divide(c,grid_type,div,axis_,random_tol,cut_width,div_depth+1,ratio)
        return node
    def pattern_court(self,temp_node_,court_node,court_width,subdiv_num,subdiv_cut,subdiv_flip,slice=None):        
        def helper_court_refcrv(court_node_,subdiv_):
            if int(court_node_) == 0:
                root = temp_node_.get_root()
                refshape_ = root.data.shape
            else:
                refshape_ = subdiv_.data.shape
            return refshape_  
        def helper_court_slice(curr_node,ref_shape_,axis_,ratio_):
            rootshape = ref_shape_
            L = []
            curr_node_ref = curr_node 
            for i in range(2):
                if i%2==0:
                    axis_ = "NS"
                else:
                    axis_ = "EW"
                for j in range(2):
                    ###'simpledivdie' in patterndivide
                    if j%2==0: 
                        ratio_ = 0.2
                    else:
                        ratio_ = 0.8
                    geom_lst = curr_node.data.shape.op_split(axis_,ratio_,deg=0.,split_depth=0.,split_line_ref=rootshape)    
                    for j,geom in enumerate(geom_lst):
                        child_node = self.helper_geom2node(geom,parent_node=curr_node,label="")
                        cns = child_node.data.shape
                        IsRatioX = abs(cns.x_dist/float(rootshape.x_dist)-0.2)<=0.01
                        IsRatioY = abs(cns.y_dist/float(rootshape.y_dist)-0.2)<=0.01
                        if IsRatioX or IsRatioY:
                            L.append(copy.deepcopy(child_node))
                        else:
                            curr_node = child_node 
            for i,n in enumerate(L):
                n.depth = curr_node_ref.depth+1
                n.parent = curr_node_ref
                L[i] = n
            curr_node_ref.loc = L 
                   
        debug = sc.sticky['debug']
        lon = temp_node_.traverse_tree(lambda n: n,internal=False)  
        for subdiv in lon:    
            subdiv.data.shape.convert_rc('3d')
            refshape = helper_court_refcrv(court_node,subdiv)
            debug.append(refshape.bottom_crv)
            if slice:
                try:
                    helper_court_slice(subdiv,refshape,"NS",0.2)
                except Exception as e:
                    print 'Error @ court_slice', str(e)
            elif court_width > 0.:
                try:
                    subdiv.data.shape.op_offset(court_width,refshape.bottom_crv,dir="courtyard")
                except Exception as e:
                    print 'Error @ court', str(e)
        return temp_node_
              
    def main_pattern(self,node,PD):
        """
        param_dictionary
        solar: solartype, solartime
        divis: div_num, div_deg, div_cut
        court: court, court_width, court_node
        sdiv: subdiv_num, subdiv_cuttime
        """
        debug = sc.sticky["debug"]
        TOL = sc.doc.ModelAbsoluteTolerance
        
        ## 0. make a copy of the geometry
        
        gb = node.data.shape.geom
        if node.data.shape.is_guid(gb): gb = rs.coercebrep(gb)#gb = sc.doc.Objects.AddBrep(gb)
        geo_brep = copy.copy(gb)
        
        ## 1. param 1 or param 3
        solartype = PD['solartype']
        solartime = PD['solartime']
        solarht = PD['solarht']
        
        if solartype == 1 or solartype == 3: # uni-cell
            try:
                geo_brep = self.pattern_solar_envelope_uni(node,solartime,solarht,solartype)
            except Exception as e:
                    print "Error @ solartype 1 or 3", str(e)

        ## 2. make a new, fresh node
        build_shape = Shape_3D(geo_brep,cplane=node.data.shape.cplane)
        build_grammar = Grammar(build_shape)
        temp_node = Tree(build_grammar,parent=node,depth=0)
        #node.data.shape = build_shape
        #temp_node = node
            
        ## 3. param 2
        div_num = PD['div_num']
        div_deg = PD['div_deg']
        div_cut = PD['div_cut']
        div_ratio = PD['div_ratio']
        flip = PD['flip']
        
        if div_num > 0:
            try:
                temp_node = self.pattern_divide(node,temp_node,div_num,div_deg,div_cut,div_ratio,flip)
            except Exception as e:
                print "Error @ main_pattern @ pattern_divide"
                print e
             
        ## 4. param 3
        if solartype == 2: # multi_cell
            try:
                temp_node = self.pattern_solar_envelope_multi(temp_node,solartime,node.data,solarht)
            except Exception as e:
                print e
        
           
        ## 5. stepback
        stepback = PD['stepback']
        stepback_node = PD['stepback_node']
        if stepback != None and stepback != []:
            setback_ref = temp_node.get_root().data.type.get('setback_reference_line')
            for step_data in stepback:
                #sr: [ht,dim]
                try:
                    temp_node = self.pattern_stepback(temp_node,step_data,stepback_node,setback_ref)
                except Exception as e:
                    print "Error @ stepback"
                    print str(e)#,sys.exc_traceback.tb_lineno 
            
            
        ## 5. param 1
        court = PD['court']
        court_node = PD['court_node']
        court_width = PD['court_width']
        court_slice = PD['court_slice']
        subdiv_num = PD['subdiv_num']
        subdiv_cut = PD['subdiv_cut'] 
        subdiv_flip = PD['subdiv_flip']
        terrace = float(PD['terrace'])
        terrace_node = PD['terrace_node']
        
        if terrace > 0.:
            lon = temp_node.traverse_tree(lambda n: n,internal=False)
            for i,subdiv in enumerate(lon):
                #debug.append(subdiv.data.shape.geom)
                #tcrv = subdiv.data.shape.bottom_crv
                # 2. offset
                #if debug_print:
                #    print 'terracenode', terrace_node
                if int(terrace_node) == 0:
                    root = node.get_root()
                    tcrv = root.data.shape.bottom_crv
                elif int(terrace_node) == 1:
                    tcrv = subdiv.parent.data.shape.bottom_crv
                elif int(terrace_node) == 2 and subdiv.parent.parent:
                    tcrv = subdiv.parent.parent.data.shape.bottom_crv
                elif int(terrace_node) == 3 and subdiv.parent.parent.parent:
                    tcrv = subdiv.parent.parent.parent.data.shape.bottom_crv
                else:#terrace_node = -1
                    tcrv = subdiv.data.shape.bottom_crv
                subdiv.data.shape.op_offset(terrace,tcrv,dir="terrace_3d")
        
        if court==1:
            try:
                temp_node = self.pattern_court(temp_node,court_node,court_width,subdiv_num,subdiv_cut,subdiv_flip,slice=court_slice)            
                #print 'tn', temp_node.traverse_tree(lambda n:n,internal=False)
            except Exception as e:
                print "Error at pattern_court"
                print str(e)
        ## 7. finish
        return temp_node
        

            
TOL = sc.doc.ModelAbsoluteTolerance
if True:
    sc.sticky["Pattern"] = Pattern 
