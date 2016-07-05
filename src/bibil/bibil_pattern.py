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
import math

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
                for j,sbref in enumerate(sb_ref_):
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
                        pass
                        #print "Error at shape.reset at pattern_stepback",str(e)
        except Exception as e:
            print str(e)#,sys.exc_traceback.tb_lineno 
            print "Error at Pattern.stepback"
        return tnode    
    def pattern_divide(self,node,grid_type,div,axis="NS",random_tol=0,cut_width=0,div_depth=0,ratio=None,flip=False):        
        def helper_subdivide_depth(hnode,div,div_depth,ratio_,axis_ref="NS"):            
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
            hnode.data.type['axis'] = haxis
            hnode.data.type['ratio'] = hratio
            return hnode
        def helper_subdivide_depth_same(hnode,div,div_depth,ratio_,axis_ref="NS"):            
            # base case: stop subdivide
            if int(div_depth) >= int(div) or abs(div-0.) <= 0.01:
                haxis,hratio = axis_ref,0.
            # alternate subdivide by axis
            elif float(div_depth) < 0.5 and int(div) > 0.01:
                haxis,hratio = axis_ref,0.5
            # alternate subdivide by axis
            else:
                haxis,hratio = node.parent.data.type['axis'],0.5
            hnode.data.type['axis'] = haxis
            hnode.data.type['ratio'] = hratio
            return hnode
        def helper_subdivide_dim(hnode,div,div_depth,ratio_,axis_ref="NS",tol=0.1):            
            def greater(a,b,tol):
                checktol = abs(a-b) <= tol
                return a >= b and not checktol
            ss = hnode.data.shape
            grid_x, grid_y = float(div[0]), float(div[1])
            if greater(ss.y_dist,grid_y,tol):
                haxis = "EW" 
                hratio = grid_y/float(ss.y_dist)
            elif greater(ss.x_dist,grid_x,tol): 
                haxis = "NS"
                hratio = grid_x/float(ss.x_dist)
            else: 
                haxis,hratio = axis_ref,0.
            hnode.data.type['axis'] = haxis
            hnode.data.type['ratio'] = hratio
            return hnode
        def helper_simple_divide(hnode,ratio_,axis_ref="NS"):
            hnode.data.type['axis'] = axis_ref
            hnode.data.type['ratio'] =ratio_
            return hnode
        debug = sc.sticky['debug']
        if node.depth >=10: # base case 1
            print 'node.depth > 10'
        else:
            ## Calculate and encode the ratio and axis data
            axis_ = axis
            if flip:
                axis_ = "NS" if "EW" in axis else "EW"
            if grid_type == "subdivide_depth":
                node = helper_subdivide_depth(node,div,div_depth,ratio,axis_ref=axis_)
            elif grid_type == "subdivide_depth_same":
                node = helper_subdivide_depth_same(node,div,div_depth,ratio,axis_ref=axis_)
            elif grid_type == "subdivide_dim":
                node = helper_subdivide_dim(node,div,div_depth,ratio,axis_ref=axis_)
            else:#simple_divide
                node = helper_simple_divide(node,ratio,axis_ref=axis_)
            
            ## Split, make a node, and recurse.
            if node.data.type['ratio'] > 0.0001:
                loc = node.data.shape.op_split(node.data.type['axis'],node.data.type['ratio'],0.,split_depth=cut_width)
                #debug.extend(loc)
                for i,child_geom in enumerate(loc):
                    child_node = self.helper_geom2node(child_geom,node)
                    if child_node: node.loc.append(child_node)
                if 'simple_divide' not in grid_type:
                    for c in node.loc:
                        self.pattern_divide(c,grid_type,div,axis_,random_tol,cut_width,div_depth+1,ratio)
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
            ref_base = refnode_.data.shape.set_base_matrix()
            foo_colinear = refnode_.data.shape.check_colinear_pt
            colinear_lst = []
            newht = tn_.data.shape.cpt[2]
            n_matrix = tn_.data.shape.set_base_matrix()
            check_x = False
            check_y = False
            for line in ref_base:
                newline = map(lambda p: [p[0],p[1],newht],line)
                refcrv = rs.coercecurve(rs.AddLine(newline[0],newline[1]))
                #debug.append(refcrv)
                for nline in n_matrix:
                    pt_0 = foo_colinear(refcrv,nline[0],tol=0.5)
                    pt_1 = foo_colinear(refcrv,nline[1],tol=0.5)
                    if pt_0 and pt_1:
                        colinear_lst.append(nline)
            if len(colinear_lst) < 1:
                colinear_lst = get_max_magnitude(tn_.data.shape.base_matrix)
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
        #debug.append(line)
        normal2srf = get_normal_to_exterior_vector(parallel2refext)
        return normal2srf
    def pattern_separate_by_dist(self,temp_node_,sep_dist,dim=1.):
        def extract_topo(n_):    
            L = []
            pt = n_.data.shape.cpt
            refpt = rs.AddPoint(pt[0],pt[1],n_.data.shape.z_dist)
            topcrv = n_.data.shape.get_bottom(n_.data.shape.geom,refpt)
            childn = self.helper_geom2node(topcrv,n_,"tower_base")
            L.append(childn) 
            return         
        ## Takes a node subdivides it along one axis according to separation distance
        ## and dimension
        def new_subdivide_by_dim(count,tn_,cut_axis_,cut_width_,recurse=True):
            if count <= 30:
                if "NS" in cut_axis_:
                    IsWidth = abs(tn_.data.shape.x_dist-cut_width_) <= 3.
                else:
                    IsWidth = abs(tn_.data.shape.y_dist-cut_width_) <= 3.
                if not IsWidth:
                    try:
                        cut_ratio_ = tn_.data.shape.calculate_ratio_from_dist(cut_axis_,cut_width_,0)
                        self.pattern_divide(tn_,'simple_divide',0,axis=cut_axis_,ratio=cut_ratio_)
                        if recurse:
                            for tnc_ in tn_.loc:
                                new_subdivide_by_dim(count+1,tnc_,cut_axis_,cut_width_)
                    except:
                        pass
            else:
                print 'newsubdivide by depth > 30 recursion!'
        def extrude_tower(tn_,cut_axis,cut_width_,z):
            if "NS" in cut_axis:
                IsWidth = abs(tn_.data.shape.x_dist-cut_width_) <= 3.
            else:
                IsWidth = abs(tn_.data.shape.y_dist-cut_width_) <= 3.
            if IsWidth:
                tn_.data.shape.op_extrude(z)
    
        print 'We are separating!'
        #topo_lst = extract_topo(temp_node_)
        refshape = temp_node_.data.shape
        normal2srf = self.helper_normal2extsrf(temp_node_)
        cut_axis = temp_node_.data.shape.vector2axis(normal2srf)
        cut_width = sep_dist + dim
        new_subdivide_by_dim(0,temp_node_,cut_axis,cut_width)
        t_lst = temp_node_.traverse_tree(lambda n:n,internal=False)
        for tnc in t_lst:
            new_subdivide_by_dim(0,tnc,cut_axis,dim,recurse=False)
            t_lst_ = tnc.traverse_tree(lambda n:n,internal=False)
            for t in t_lst_:
                extrude_tower(t,cut_axis,dim,150.)
    def pattern_court(self,temp_node_,court_node,court_width,subdiv_num,subdiv_cut,subdiv_flip,slice=None):        
        def helper_court_refcrv(court_node_,subdiv_):
            if int(court_node_) == 0:
                root = temp_node_.get_root()
                refshape_ = root.data.shape
            else:
                refshape_ = subdiv_.data.shape
            return refshape_  
        def helper_court_slice(curr_node,rootshape,width_):
            L = []
            curr_node_ref = curr_node 
            for i in range(2):
                if i%2==0:
                    axis_ = "EW"
                else:
                    axis_ = "NS"
                for j in range(2):
                    if j%2==0:dir = 1. 
                    else: dir = 0.
                    ratio_ = rootshape.calculate_ratio_from_dist(axis_,width_,dir)
                    
                    ## Construct width_reference to find small slice
                    width_ref = ratio_
                    if "EW" in axis_:
                        total_dist = rootshape.y_dist
                    else:
                        total_dist = rootshape.x_dist
                    if width_/total_dist < width_ref: width_ref = 1.-ratio_
                    #y_dist = rootshape.y_dist
                    #print 'ratio',width_,axis_, round(ratio_,2)
                    #print 'y_dist', y_dist, y_dist * ratio_
                    ## Split the geom (use simple divide for this, is redundant)
                    geom_lst = curr_node.data.shape.op_split(axis_,ratio_,deg=0.,split_depth=0.,split_line_ref=rootshape)    
                    debug.extend(geom_lst)
                    for j,geom in enumerate(geom_lst):
                        child_node = self.helper_geom2node(geom,parent_node=curr_node,label="")
                        cns = child_node.data.shape
                        IsRatioX = abs(cns.x_dist/float(rootshape.x_dist)-width_ref)<=0.1
                        IsRatioY = abs(cns.y_dist/float(rootshape.y_dist)-width_ref)<=0.1
                        if IsRatioX or IsRatioY:
                            L.append(copy.deepcopy(child_node))
                        else:
                            curr_node = child_node 
            ## Make this into separate function: clean up depth (also in spearate)
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
            
            if slice:
                try:
                    helper_court_slice(subdiv,refshape,court_width)
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
        temp_node = self.helper_geom2node(geo_brep,node)
        
        
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
            
        

        ## 6. separation_distance 2
        if PD['separate']:
            separation_dist = PD['separation_dist']
            unitdim = PD['dim']
            norm2srfvector = self.helper_normal2extsrf(temp_node)
            self.pattern_separate_by_dist(temp_node,separation_dist,unitdim) 
        
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
                #newyaxis = self.helper_normal2extsrf(temp_node)
                #oldyaxis = temp_node.data.shape.cplane.YAxis
                #radian_angle = rc.Geometry.Vector3d.VectorAngle(oldyaxis,newyaxis)
                #zaxis = rc.Geometry.Vector3d(0,0,1)
                #temp_node.data.shape.cplane.Rotate(radian_angle,zaxis)
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
