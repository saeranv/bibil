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


"""import classes"""
Shape = sc.sticky["Shape"]
Tree = sc.sticky["Tree"]
Bula = sc.sticky["Bula"]
Miru = sc.sticky["Miru"]

sc.sticky['debug'] = []
debug = sc.sticky["debug"]

TOL = sc.doc.ModelAbsoluteTolerance
    
class Grammar:
    """Grammar """
    def __init__(self):
        self.type = {'label':"x",'grammar':"null",'axis':"NS",'ratio':0.,'top':False}
        #need to move axis, NS, ratio to divide
        empty_rule_dict = copy.deepcopy(Miru)
        self.type.update(empty_rule_dict)
        
    def helper_geom2node(self,geom,parent_node=None,label="x",grammar="null"):
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
                return rs.coercebrep(geom_)     
        
        debug = sc.sticky['debug']
        child_node,child_shape = None, None
        IsDegenerate = False
        tree_depth = 0
        try:
            if geom:
                geom = helper_curve2srf(geom)
                cplane_ref = None
                if parent_node: 
                    cplane_ref = parent_node.shape.cplane
                try:
                    child_shape = Shape(geom,cplane=cplane_ref)
                except Exception as e: 
                    print 'Bibil has detected a degenerate shape', str(e)
                    child_shape = Shape(geom,parent_node.shape.cplane)
                IsDegenerate = abs(child_shape.x_dist-0.) < 0.01 or abs(child_shape.y_dist-0.) < 0.01
            elif parent_node:
                #cloned nodes get link to parent_node.shape
                child_shape = parent_node.shape
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
        except Exception as e:
            print "Error at Pattern.helper_geom2node", str(e)
        return child_node
    def helper_clone_node(self,node_,parent_node=None,label="x"):
        #Purpose: Input node, and output new node with same Shape, new Grammar
        return self.helper_geom2node(None,parent_node,label)
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
    def stepback(self,tnode,PD_):
        debug = sc.sticky['debug']
        sb_ref = PD_['stepback_ref']
        sb_data = PD_['stepback_data'] #height:stepback
        sb_random = PD_['stepback_randomize']
        ##sb_data: [(height,distance),(height,distance)...]     
        if True:#try:
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
            
            #Get data if not geometry
            sbg_type = self.helper_get_type(sb_ref[0])
            if sbg_type != "geometry":
                sb_node_ref = self.helper_get_ref_node(sb_ref[0],tnode)
                axis_matrix = sb_node_ref.shape.set_base_matrix()
                line_lst = []
                for vectors in axis_matrix:
                    line =  rc.Geometry.Curve.CreateControlPointCurve(vectors,0)
                    line_lst.append(line)
                sb_ref = line_lst
            ## Loop through the height,setback tuples
            for sbd in sb_data:
                ht, dist = sbd[0], sbd[1]
                if sb_random:
                    if not self.is_near_zero(randht_lo) and not self.is_near_zero(randht_hi):
                        ht += random.randrange(randht_lo,randht_hi)
                    if not self.is_near_zero(randsb_lo) and not self.is_near_zero(randsb_hi):
                        dist += random.randrange(randsb_lo,randsb_hi)
                
                #Dissect floor
                sh_top_node = tnode#None
                #if ht < tnode.shape.ht:
                #    sh_bot_node,sh_top_node = self.helper_divide_through_normal(tnode,ht)
                
                ##Loop through all sb_geoms
                if sh_top_node:
                    for sbg in sb_ref:
                        # move sbref
                        move_vector= sh_top_node.shape.normal*float(ht)
                        sbref_crv = sc.doc.Objects.AddCurve(sbg)
                        sbref_crv = rs.coercecurve(rs.CopyObject(sbref_crv,move_vector))
                        cut_geom = None
                        #cut at ht
                        #then take top node and split that
                        try: 
                            cut_geom = sh_top_node.shape.op_split("EW",0.5,deg=0.,\
                                                split_depth=float(dist*2.),split_line_ref=sbref_crv)
                        except:
                            pass
                        if cut_geom:
                            sh_top_node.shape.geom = cut_geom[0]
                            sh_top_node.shape.reset(xy_change=True)
        #except Exception as e:
        #    print str(e)#,sys.exc_traceback.tb_lineno 
        #    print "Error at Pattern.stepback"
        return tnode    
    def helper_divide_through_normal(self,temp_node_,dist_):
        #Need to rewrite this so all variables in divide is null
        #and option to orient results vertically exists
        #Divides based on 'height'
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
            temp_node_.grammar.type['top'] = False
            top_shape.grammar.type['top'] = True
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
                #print loc
                #print '----'
                if 'simple_divide' not in grid_type: 
                    for nc in node_.loc:
                        helper_divide_recurse(nc,grid_type,div_,div_depth_+1,cwidth_,ratio_,axis_,count+1)
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
        def check_shape_validity(t_,dim2chk_tuple,minarea,tol_=2.):
            ## Move this to shape class
            ## Flip cut axis to check the resulting dim
            ## EW akways checks x axis, NS always checks y axis
            IsEWDim,IsNSDim,IsMinArea = False, False, False
            x_dim = dim2chk_tuple[0]
            y_dim = dim2chk_tuple[1]
            try:
                IsEWDim = t_.shape.check_shape_dim("EW",x_dim,tol=tol_)
                IsNSDim = t_.shape.check_shape_dim("NS",y_dim,tol=tol_)
                IsMinArea = abs(t_.shape.get_area() - minarea) <= tol_
            except:
                pass
            #print IsNSDim, IsEWDim, IsMinArea
            return IsEWDim and IsNSDim and IsMinArea
        def separate_dim(temp_node_topo_,x_keep_omit_,y_keep_omit_,cut_axis,cut_axis_alt):
            def helper_simple_divide(lstvalidshape_,dimkeep,dimaxis):
                #Now cut the valid shapes
                VL = []
                for validshape in lstvalidshape_:
                    simple_ratio = validshape.shape.calculate_ratio_from_dist(dimaxis,dimkeep,dir_=0.)
                    validshape_param_lst = [1.,dummy_deg,0.,simple_ratio,"simple_divide",dimaxis]
                    try:
                        self.divide(validshape,validshape_param_lst)
                    except:
                        pass
                    VL.extend(validshape.traverse_tree(lambda n:n, internal=False))
                return VL
            #Axis issue:
            #cut_axis: axis that cuts perpendicular to primary axis of shape
            #EW will cut y_dist
            #NS will cut x_dist
            #In bibil - y_axis (cutting EW) is always set as the primary axis. 
            
            #Prep inputs
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
            #EW checks x_dist, NS checks y_dist << THIS SHOULD BE CHANGED TO HAVE SAME NAME        
            if "EW" in cut_axis:##then the we are cutting y axis, give y dims
                dimprimekeep = y_keep_
                dimsecondkeep = x_keep_
            else:
                dimprimekeep = x_keep_
                dimsecondkeep = y_keep_
            lstfirkeepnodes = helper_simple_divide(topo_child_lst,dimprimekeep,cut_axis)
            lstseckeepnodes = helper_simple_divide(lstfirkeepnodes,dimsecondkeep,cut_axis_alt)
            
            for final_node in lstseckeepnodes:
                min_area = x_keep_ * y_keep_
                div2keep = (x_keep_,y_keep_)
                IsValidDimKeepOmit = check_shape_validity(final_node,div2keep,min_area,tol_=2.)
                if IsValidDimKeepOmit:
                    shape2keep_lst.append(final_node)
                else:
                    shape2omit_lst.append(final_node)
            #debug.extend(map(lambda n: n.shape.geom,shape2keep_lst))
            return shape2omit_lst,shape2keep_lst
        def check_base_with_offset(shape2off,GLOBLST):
            # check if interect with tower-seperation list
            intersect_offset = False
            for offset in GLOBLST:
                crvA = offset
                crvB = shape2off.shape.bottom_crv
                ##debug.append(offset)
                print crvA
                setrel = shape2off.shape.check_region(crvA,crvB,tol=0.1)
                #If not disjoint
                if not abs(setrel-0.)<0.1:
                    intersect_offset = True
                    break
            return not intersect_offset
        def set_separation_record(shape2record,sep_dist,separation_tol_):
            ## Add some tolerance to separation distance
            sep_dist_tol = (sep_dist - separation_tol_) * -1
            sep_crv = shape2record.shape.op_offset_crv(sep_dist_tol,corner=3)
            #debug.append(check_base_separation_.shape.bottom_crv)
            #debug.append(sep_crv)
            ## Append crv
            sc.sticky['GLOBAL_COLLISION_LIST'].append(rs.coercecurve(sep_crv))
            
        debug = sc.sticky['debug']
        
        #Extract data
        x_keep_omit = PD_['x_keep_omit']
        y_keep_omit = PD_['y_keep_omit']
        
        #Parse the data
        x_keep_omit = map(lambda s: float(s), x_keep_omit.split(','))
        y_keep_omit = map(lambda s: float(s), y_keep_omit.split(','))
        
        temp_node_topo = temp_node_#copy.deepcopy(sep_ref_node)
        
        ## Get normal to exterior srf
        normal2srf = self.helper_normal2extsrf(temp_node_topo)
        cut_axis = temp_node_topo.shape.vector2axis(normal2srf)
        noncut_axis = "EW" if "NS" in cut_axis else "NS" 
        
        ## Get cut dimensions     
        shapes2omit,shapes2keep = separate_dim(temp_node_topo,x_keep_omit,y_keep_omit,cut_axis,noncut_axis)
        
        temp_node_topo.loc = []
        
        if shapes2keep:
            #Flatten tree
            temp_node_topo = self.flatten_node_tree_single_child(shapes2keep,temp_node_topo,grammar="shape2keep",empty_parent=True)
            temp_node_topo = self.flatten_node_tree_single_child(shapes2omit,temp_node_topo,grammar="shape2omit",empty_parent=False)
            
            # Make/call global collision list
            #if not sc.sticky.has_key('GLOBAL_COLLISION_LIST'):
            sc.sticky['GLOBAL_COLLISION_LIST'] = []
            
            offset_dist = x_keep_omit[1]
            seperate_tol = 0.5
            # Check shape separation
            for i,t in enumerate(temp_node_topo.loc):
                if 'shape2keep' in t.grammar.type['grammar']:
                    GLOBAL_LST = sc.sticky['GLOBAL_COLLISION_LIST']
                    GLOBAL_LST = filter(lambda offcrv: offcrv!=None,GLOBAL_LST)
                    isSeperate = check_base_with_offset(t,GLOBAL_LST)
                    if isSeperate == True:
                        #offset_tuple
                        set_separation_record(t,offset_dist,seperate_tol)
        else: 
            temp_node_topo.loc = [] 
        ##TEMP4MEETING
        for i,t in enumerate(temp_node_topo.loc):
            if 'omit' in t.grammar.type['grammar']:
                temp_node_topo.loc[i] = None
                debug.append(t)
        temp_node_topo.loc = filter(lambda n:n!=None,temp_node_topo.loc)
        return temp_node_topo
    def extract_slice(self,temp_node_,PD_):
        def extract_topo(n_,ht_):
            pt = n_.shape.cpt
            refpt = rs.AddPoint(pt[0],pt[1],ht_)
            topcrv = n_.shape.get_bottom(n_.shape.geom,refpt)
            childn = self.helper_geom2node(topcrv,n_,"extract_slice")
            n_.loc.append(childn)
            return childn

        ## Warning: this function will raise height of geom 1m.
        slice_ht = PD_['extract_slice_height']
        IsTop = True
        #Check inputs
        if type(slice_ht) != type([]): slice_ht = [slice_ht]
        if slice_ht == [] or slice_ht == [None]: 
            slice_ht = ['max']
            ##unsure about this but works for now...
            IsTop = temp_node_.backtrack_tree(lambda n:n.grammar.type['top'])
                   
        if slice_ht and IsTop:
            if self.helper_get_type(slice_ht[0]) == "string":
                if slice_ht[0] == 'max':
                    slice_ht = [temp_node_.shape.ht]
                else:
                    slice_ht = map(lambda s: float(s),slice_ht)
            
            #Extract topo
            for slht in slice_ht:
                extract_topo(temp_node_,slht)
        
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
        
        debug = sc.sticky['debug']
        #print 'We are setting height!'
        ht_ = PD_['height']
        randomize_ht = PD_['height_randomize']
        if randomize_ht:
            random_bounds = map(lambda r: int(float(r)),randomize_ht.split('>'))
            randht_lo,randht_hi = random_bounds[0],random_bounds[1]
            ht_ += random.randrange(randht_lo,randht_hi)
        n_ = temp_node_
        #print 'labelchk', temp_node_.parent.parent.grammar.type['label']
        if type(ht_)==type('') and 'bula' in ht_:
            setht_ = height_from_bula(n_)
        else:
            setht_ = ht_
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
                shape_ref_ = int(shape_ref_)
                type_info = "number"
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
            #Check if node
            elif type_info == "node":
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
                cmax = 20.
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
                    for i,line in enumerate(matrice):
                        #print i
                        dirvec = line[1]-line[0]
                        # get magnitude of line
                        dist = math.sqrt(sum(map(lambda p: p*p,dirvec)))
                        if dist > tol: 
                            split_crv = rs.AddCurve(line,1)
                            midpt = curr_node_.shape.get_midpoint(line)
                            sc_ = 5,5,0
                            split_crv = rs.ScaleObject(split_crv,midpt,sc_)
                            if True:#try:
                                split_node_lst = []
                                split_geoms = curr_node_.shape.op_split("NS",0.5,split_depth=cut_width__,split_line_ref=split_crv)
                                for geom in split_geoms:
                                    #if type(geom)!= type(rootshape.shape.geom):
                                    #    ##debug.append(geom)
                                    split_node = self.helper_geom2node(geom,None)
                                    split_node_lst.append(split_node)
                                    split_crv = split_node.shape.bottom_crv
                                    set_rel = curr_node_.shape.check_region(chk_offset,split_crv,tol=0.1)
                                    if abs(set_rel-0.)<0.1:
                                        valid_node = split_node
                                    else:
                                        invalid_node = split_node
                            #except:
                                #pass## Split fail, so test the next line split
                        matrice_max = len(matrice)==i+1
                        if invalid_node != None and valid_node != None:
                            valid_node_lst.append(valid_node)
                            matrice.pop(i)
                            break
                    if matrice_max == True and abs(set_rel-2.)<0.1:
                        #debug.append(curr_node_.shape.geom)
                        chk_offset_out = rootshape.op_offset_crv(width_-1.)
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
                L,diff = recurse_slice(curr_node,shape_matrix,[],None,0,0,cut_width_)
                #debug.extend(map(lambda n:n.shape.geom,L))
                #debug.append(diff.shape.geom)
                #print diff
                curr_node = self.flatten_node_tree_single_child(L,curr_node,grammar="courtslice")
                
            else:
                diff = None
            return diff
        
        #Unpack the parameters         
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
    def meta_tree(self,temp_node_,PD_):
        def inc_depth(n):
            if n.parent:
                n.depth = n.parent.depth + 1
            else:
                n.depth = 0
        meta_node = PD_['meta_node']
        #THIS SHOULD BE DONE IN TREE CLASS
        #print 'label metanode:', meta_node.parent
        #print 'label currnode: ', temp_node_
        meta_root = meta_node.get_root()
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
    def landuse(self,temp_node_,PD_):
        nodes2bucket = PD_['nodes2bucket']
        node_lst = []
        """
        #Make nodes/labels of inputs
        for node,label in zip(landuse_node,landuse_label):
            emptyrules = DataTree[object]()
            print node
            print label
            landuse_node = self.main_UI([node],emptyrules,label)
            node_lst.append(landuse_node)
        temp_node_.loc.extend(node_lst)
        """
        return temp_node_
    def building_analysis(self,node_in,height,GFA,groundFloor_ht,restFloor_ht):
        def get_label(n):
            label_ = []
            root = n[0].get_root()
            L = root.traverse_tree(lambda n:n,internal=True) 
            for nl in L:
                #print nl
                label_.append(nl)
            return label_
        def make_analysis(nodelen,pd):
            ## Input: dictionary of parameter key, list of data value 
            ## Output: Filtered list of str: with keys and value
            L = [""] * nodelen
            if pd.has_key('height'):
                for i,ht in enumerate(pd['height']):
                    valstr = 'height: %s' % (ht)
                    L[i] += valstr
            if pd.has_key('GFA'):
                for i,gfa in enumerate(pd['GFA']):
                    valstr = '\nGFA: %s' % (gfa)
                    L[i] += valstr
            return L
        def get_ht(node_):
            L = []
            for n_ in node_:
                storey = str(round(n_.shape.ht,1))
                L.append(storey)
            return L
        def get_GFA(node_,ght,rht):
            def helper_by_floor_div(n__,groundht):
                ratio = groundht/n__.shape.ht
                PD = {}
                PD['div_num'] = 1
                PD['div_deg'] = 0.
                PD['div_cut'] = 0.
                PD['div_ratio'] = ratio
                PD['div_type'] = 'simple_divide'
                PD['axis'] = "Z"
                divnode = n__.grammar.divide(n_,PD)
                
                if abs(divnode.loc[0].shape.ht - groundht) < 0.01:
                    groundfloor = divnode.loc[0]
                    restfloor = divnode.loc[1]
                else:
                    groundfloor = divnode.loc[1]
                    restfloor = divnode.loc[0]
                return groundfloor,restfloor
            def helper_by_floor_calc(n__,htdiv):
                n__.shape.geom = ghcomp.CapHolesEx(n__.shape.geom)[0]
                shapevol = rc.Geometry.VolumeMassProperties.Compute(n__.shape.geom).Volume
                shapegfa = shapevol/htdiv
                return shapegfa
            debug = sc.sticky['debug']
            ReadMe_ = ""
            L = []
            for n_ in node_:
                if abs(ght-rht)<0.1:
                    gfacalc = helper_by_floor_calc(n_,rht)
                else:
                    try:
                        grndshape,rstshape = helper_by_floor_div(n_,ght)
                        grndgfa = grndshape.shape.get_area()
                        rstgfa = helper_by_floor_calc(rstshape,rht)
                        gfacalc = grndgfa + rstgfa
                    except:
                        ReadMe_ = "Calculating by specific floor heights has failed, probably because the geometry was too complicated. GFA is now based on restfloorht."
                        gfacalc = helper_by_floor_calc(rstshape,3.)
                #debug.extend(map(lambda n:n.shape.geom,divnode.loc))
                L.append(str(round(abs(gfacalc),1)))
            return L,ReadMe_
        
        node = filter(lambda n: n!=None,node_in)
        if node and node != []:
            node = map(lambda n: copy.deepcopy(n),node)
            debug = sc.sticky['debug']
            ReadMe = ""
            
            #These always appear by default
            label_out = get_label(node)
            geom_out = map(lambda n:n.shape.geom,node)
            pt_out = map(lambda n:n.shape.cpt,node)
            #Analysis paramaters
            param_dict = {}
            if height==True:
                ht_out = get_ht(node)
                param_dict['height'] = ht_out
            if GFA == True:
                if not groundFloor_ht:
                    groundFloor_ht = 3.0
                if not restFloor_ht:
                    restFloor_ht = 3.0
                gfa_out,readmegfa = get_GFA(node,groundFloor_ht,restFloor_ht)
                param_dict['GFA'] = gfa_out
                ReadMe += readmegfa
            analysis_out = make_analysis(len(node),param_dict)
            if not ReadMe:
                ReadMe = "Successfully calculated"
    def shape2height(self,temp_node_,PD_):
        angle = 0.5
        ht_inc = 3.0
        side_inc = 0.1
        ht = temp_node_.shape.ht
        floor_div = int(math.floor(ht/ht_inc))
        input_node = temp_node_
        #print 'floordiv', floor_div
        for i,fdiv in enumerate(range(floor_div)):
            print 'fdiv', fdiv
            if fdiv > 10.0:
                inc_angle = angle * -1.0
            else:
                inc_angle = angle
            print 'angle', inc_angle
            input_node_with_child = self.squeeze_angle(input_node,inc_angle,ht_inc,side_inc)
            input_node = input_node_with_child.loc[0]
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
            temp_node_child = self.helper_geom2node(shapecrv,temp_node_,grammar="squeeze_angle")
            temp_node_.loc.append(temp_node_child)
        return temp_node_
    def node2grammar(self,lst_node_,rule_in_):
        def helper_type2node(copy_node_,type_):
            #type: list of (dictionary of typology parameters)
            copytype = copy.deepcopy(type_)
            copy_node_.grammar.type.update(copytype)
            return copy_node_
        def helper_clone_node(node_geom): 
            #Purpose: Create a node from geometry/parent node
            #if geometry, turned into node w/ blank label
            #if node, clone a child node w/ blank label
            if type(T) == type(node_geom):
                #print 'make cloned node'
                childn = self.helper_clone_node(node_geom,parent_node=node_geom)
                node_geom.loc.append(childn)
                n_ = childn
            else:
                #print 'make a geom'
                n_ = self.helper_geom2node(node_geom)
            return n_       
        ## Purpose: Input list of nodes, applies type
        ## Applies pattern based on types
        ## outputs node
        T = Tree()
        L = []
        for i,node_ in enumerate(lst_node_):
            ## Everytime we add a rule, we clone a node. 
            ## Every rule mutates the node, or creates child nodes.
            child_node_ = helper_clone_node(node_)
            ## Apply type to node
            child_node_ = helper_type2node(child_node_,rule_in_)
            ## Apply pattern
            if True:#try:
                node_out_ = self.main_grammar(child_node_)
                RhinoApp.Wait() 
            #print 'label', node_out_
            #print '---'
            #yield node_out_
            L.extend(node_out_)
            #except Exception as e:
            #    print "Error @ Pattern.main_pattern"
            #print node_out_[0]
        #print '--'

        return L
    def main_grammar(self,node):
        ## Check geometry
        if node.shape:
            gb = node.shape.geom
            if node.shape.is_guid(gb): node.shape.geom = rs.coercebrep(gb)
        
        PD = node.grammar.type
        temp_node = node
        
        if PD['label_UI'] == True:
            #simple therefore keep in UI for now...
            temp_node.grammar.type['label'] = PD['label']
            temp_node.grammar.type['grammar'] = 'label'
        elif PD['divide'] == True:
            temp_node = self.divide(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'divide'
        elif PD['height'] != False:
            temp_node = self.set_height(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'height'
        elif PD['stepback']:
            ## Ref: TT['stepback'] = [(ht3,sb3),(ht2,sb2),(ht1,sb1)]
            temp_node = self.stepback(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'stepback'
        elif PD['court'] == True:
            self.court(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'court'
        elif PD['bula'] == True:
            self.set_bula_point(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'bula'
        elif PD['meta_tree'] == True:
            self.meta_tree(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'meta_tree'
        elif PD['landuse'] == True:
            temp_node = self.landuse(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'landuse'
        elif PD['separate'] == True:
            temp_node = self.separate_by_dist(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'separate'
        elif PD['shape2height'] == True:
            temp_node = self.shape2height(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'shape2height'
        elif PD['extract_slice'] == True:
            temp_node = self.extract_slice(temp_node,PD)
            temp_node.grammar.type['grammar'] = 'extract_slice'
        """
        These have to be rewritten
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
        #print temp_node.grammar.type['grammar']
        ## 7. Finish
        lst_childs = temp_node.traverse_tree(lambda n:n,internal=False)
        return lst_childs
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
            if rule_lst == []:
                for i,ng in enumerate(lst_node_):
                    if type(T) != type(ng):
                        ng = self.helper_geom2node(ng)
                        lst_node_[i] = ng
                return lst_node_
            else:
                rule_ = rule_lst.pop(0)
                #apply rule to current list of nodes, get child lists flat
                lst_node_leaves = self.node2grammar(lst_node_,rule_)
                return helper_main_recurse(lst_node_leaves,rule_lst)
        
        T = Tree()
        lst_node_out = []
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
        IsLeaf = True
        for n in node_in_:
            if type(n) == type(T) and len(n.loc) > 0.5:
                IsLeaf = False
                lst_node_out = node_in_
                break
                
        if chk_input_len and IsLeaf:
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
                lst_node_out_ = helper_main_recurse(node_in_,nested_rule_dict)
                lst_node_out.extend(lst_node_out_)
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
                    lst_node_out_ = helper_main_recurse([node_],nested_rule_dict)
                    lst_node_out.extend(lst_node_out_)
        else:
            print 'Either check the length of your inputs or you have already ran this component'
        return lst_node_out 
                    
if True:
    sc.sticky["Grammar"] = Grammar