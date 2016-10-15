import rhinoscriptsyntax as rs
import Rhino as rc
import random
import scriptcontext as sc
import copy
import math
import ghpythonlib.components as ghcomp

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
        self.type = {'label':"",'axis':"NS",'ratio':0.,'print':False}

    def helper_geom2node(self,geom,parent_node=None,label=""):
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
                cplane_ref = parent_node.shape.cplane
                tree_depth = parent_node.depth+1
            try:
                child_shape = Shape(geom,cplane=cplane_ref)
            except Exception as e: 
                print 'Bibil has detected a degenerate shape', str(e)
                child_shape = Shape(geom,parent_node.shape.cplane)
            IsDegenerate = abs(child_shape.x_dist-0.) < 0.0001 or abs(child_shape.y_dist-0.) < 0.0001
            if not IsDegenerate:
                if child_shape.z_dist!=None and int(child_shape.z_dist) <= 0.0001:
                    child_shape.op_extrude(6.)
                child_grammar = Grammar()
                child_grammar.type["label"] = label
                child_node = Tree(child_shape,child_grammar,parent=parent_node,depth=tree_depth)
        except Exception as e:
            print "Error at Pattern.helper_geom2node", str(e)
        return child_node                   
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
        sb_geom = PD_['stepback_geom']
        sb_node = PD_['stepback_node']
        sb_data = PD_['stepback_data']
        ##sb_data: [(height,distance),(height,distance)...]     
        try:
            ## Loop through the height,setback tuples
            for sbd in sb_data:
                ht, dist = sbd[0], sbd[1]
                ## Not efficient, but for now: loop through all sb_geoms
                for sbg in sb_geom:
                    # move sbref
                    move_vector= rc.Geometry.Vector3d(0,0,float(ht))
                    sbref_crv = sc.doc.Objects.AddCurve(sbg)
                    sbref_crv = rs.coercecurve(rs.CopyObject(sbref_crv,move_vector))
                    cut_geom = None
                    try: 
                        cut_geom = tnode.shape.op_split("EW",0.5,deg=0.,\
                                            split_depth=float(dist*2.),split_line_ref=sbref_crv)
                    except:
                        pass
                    if cut_geom:
                        tnode.shape.geom = cut_geom[0]
                        tnode.shape.reset(xy_change=True)
        except Exception as e:
            print str(e)#,sys.exc_traceback.tb_lineno 
            print "Error at Pattern.stepback"
        return tnode    
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
                ###debug.extend(loc)
                #print len(loc)
                for i,child_geom in enumerate(loc):
                    #print 'child nodes'
                    ###debug.append(child_geom)
                    child_node = self.helper_geom2node(child_geom,node_)
                    #print child_node.shape.x_dist
                    #print child_node.shape.y_dist
                    if child_node: node_.loc.append(child_node)
                #print ''
                #if 'simple_divide' not in grid_type: 
                for nc in node_.loc:
                    helper_divide_recurse(nc,grid_type,div_,div_depth_+1,cwidth_,ratio_,axis_,count+1)
        debug = sc.sticky['debug']
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
    def separate_by_dist(self,temp_node_,distlst,dellst):
        def extract_topo(n_,ht_):
            pt = n_.shape.cpt
            refpt = rs.AddPoint(pt[0],pt[1],ht_)
            topcrv = n_.shape.get_bottom(n_.shape.geom,refpt)
            childn = self.helper_geom2node(topcrv,n_,"")
            n_.loc.append(childn)
            childn.shape.op_extrude(6.)
            return childn 
        def subdivide_by_dim(temp_node_topo_,cut_axis,distlst_,dellst_):
            ## Subdivide by large dist
            cutwidth_first = distlst_[0] + distlst_[1]
            firstdiv = (cutwidth_first,cutwidth_first)
            self.divide(temp_node_topo_,"subdivide_dim",firstdiv,cut_axis)#,2.)
            ## Subdivide by small dist
            #cutwidth_second = distlst_[0] if distlst_[1] in dellst_ else distlst_[0]#distlst_[0] if distlst_[0] > distlst_[1] else distlst_[1]
            # can't cut smaller height?
            if distlst_[0] < distlst_[1]:
                cutwidth_second = distlst_[1]
            else:
                cutwidth_second = distlst_[0]
            topo_child_lst = temp_node_topo_.traverse_tree(lambda n:n, internal=False)
            for tnc in topo_child_lst:
                seconddiv = (cutwidth_second,cutwidth_second)
                try:
                    self.divide(tnc,'subdivide_dim',seconddiv,cut_axis)#,2.)
                except Exception as e: 
                    print 'error at subbydim', str(e)
            return temp_node_topo_
        def check_base_with_offset(base_,offsetlst):
            # check if interect with tower-seperation list
            intersect_offset = False
            for offset in offsetlst:
                crvA = offset
                crvB = base_.shape.bottom_crv
                ##debug.append(offset)
                setrel = base_.shape.check_region(crvA,crvB,tol=0.1)
                #If not disjoint
                if not abs(setrel-0.)<0.1:
                    intersect_offset = True
                    break
            return not intersect_offset
        def set_separation_record(check_base_separation_,sep_dist,separation_tol_):
            ## Add some tolerance to separation distance
            separation_tol_ = 0.5
            sep_dist_tol = (sep_dist - separation_tol_) * -1
            sep_crv = check_base_separation_.shape.op_offset_crv(sep_dist_tol,corner=2)
            #debug.append(check_base_separation_.shape.bottom_crv)
            ## For viz
            sep_crv_viz = check_base_separation_.shape.op_offset_crv(sep_dist*-1,corner=2)
            debug.append(sep_crv_viz)
            ## Append crv
            sc.sticky['seperation_offset_lst'].append(sep_crv)
            check_base_separation_.grammar.type["print"] = True
        def check_shape_validity(t_,cut_axis_,dstlst,dellst,sep_lst_,separation_tol_):
            ## Check dimension then check if collision w/ offset dist
            dim_ = dstlst[0] if dstlst[1] in dellst else dstlst[1]
            # flip cut axis to check the resulting dim
            IsEWDim,IsNSDim = False, False
            try:
                IsEWDim = t_.shape.check_shape_dim("EW",dim_,tol=2.)
                IsNSDim = t_.shape.check_shape_dim("NS",dim_,tol=2.)
                IsMinArea = t_.shape.get_area() >= 740.
            except:
                pass
            #print IsNSDim, IsEWDim
            
            #debug.append(t_.shape.geom)
            if IsEWDim and IsNSDim and IsMinArea:
                exist_lst = sc.sticky['existing_tower']
                check_separation_new = check_base_with_offset(t_,sep_lst_)
                check_separation_exist = check_base_with_offset(t_,exist_lst)
                #print 'new', check_separation_new
                #print 'exis', check_separation_exist
                IsIntersect = check_separation_new and check_separation_exist
                #print IsIntersect
                #print ''
                #print len(exist_lst)
                if IsIntersect == True:# != None:
                    sep_dist_ = dstlst[0]
                    set_separation_record(t_,sep_dist_,separation_tol_)
        debug = sc.sticky['debug']
        #temp_node_topo = extract_topo(temp_node_,0.)
        temp_node_topo = temp_node_
        #delete base node
        temp_node_topo.grammar.type['print']=False
        
        ## Get normal to exterior srf
        normal2srf = self.helper_normal2extsrf(temp_node_topo)
        cut_axis = temp_node_topo.shape.vector2axis(normal2srf)
        
        ## Recursively subdivide the lot crvs
        temp_node_topo = subdivide_by_dim(temp_node_topo,cut_axis,distlst,dellst)
        topo_grand_child_lst_ = temp_node_topo.traverse_tree(lambda n:n, internal=False)
        
        #try:
        EL = []
        for topo in topo_grand_child_lst_:
            g = self.divide(topo,'subdivide_dim',(27.4,27.4),cut_axis)#,tol=3.)
            g = g.traverse_tree(lambda n:n,internal=False)
            gsh = map(lambda n:n.shape.geom,g)
            #debug.extend(gsh)
            #print 'test'
            #print 'g'
            EL.extend(g)
        topo_grand_child_lst_ = EL
        #except:
        #    pass
        
        # Check base dim, check base separation
        # Llabel bases that are valid separations
        if not sc.sticky.has_key('seperation_offset_lst'):
            sc.sticky['seperation_offset_lst'] = []
        
        sep_lst = sc.sticky['seperation_offset_lst']
        separation_tol = 0.5
        for t in topo_grand_child_lst_:
            #debug.append(t.shape.geom)
            check_shape_validity(t,cut_axis,distlst,dellst,sep_lst,separation_tol)    
        
        return temp_node_topo
    def set_height(self,temp_node_,ht_):
        def height_from_bula(n_):
            bula_node,bptlst = False,False
            setht = 21. #default ht = midrise
            bula_node = n_.search_up_tree(lambda n: n.grammar.type.has_key('bula_data'))
            if bula_node:
                buladata = bula_node.grammar.type['bula_data']
                nodecrvlst = [n_]
                #make this function in bula
                inptlst = buladata.getpoints4lot(nodecrvlst,buladata.bpt_lst)
                if inptlst != [[]]:
                    buladata.generate_bula_point(nodecrvlst,inptlst)
                    ## you are now a bulalot!
                    ht_factor = n_.grammar.type['bula_data'].value
                    setht = ht_factor#1000.*ht_factor
                    ##debug.extend(n_.grammar.type['bula_data'].bpt_lst)
                return setht
        def height_from_envelope(n_,envref=None):
            #TO['solartype'],TO['solartime']
            #env = sc.sticky['envelope']
            maxht_env = 150.
            """
            if PD_['solartype']>0:
                starthr = PD_['solartime']
                endhr = starthr+5.
                crv = sc.sticky['envelope'][0].shape.bottom_crv
                env = self.get_solar_zone(starthr,endhr,curve=crv,zonetype='fan')
                env = [env]
            """
            if envref == None:
                env = sc.sticky['envelope']
            else:
                env = envref
            
            base_matrix = n_.shape.set_base_matrix()
            ptlst = map(lambda l:l[0], base_matrix)
            dir = rc.Geometry.Vector3d(0,0,1) 
            tol = sc.doc.ModelAbsoluteTolerance
            projlst = rc.Geometry.Intersect.Intersection.ProjectPointsToBreps(env,ptlst,dir,tol)
            projlst = filter(lambda pt:abs(pt[2]-200.)>0.5,projlst)
            projlst = filter(lambda p: abs(p[2]-0)>1.,projlst)
            if projlst:
                #debug.extend(projlst)
                min_index = projlst.index(min(projlst,key=lambda p:p[2]))
                min_pt = projlst[min_index]
                envht = min_pt[2]
            else:
                envht = 150.
            print 'envht', envht
            return envht
            
        debug = sc.sticky['debug']
        #print 'We are setting height!'
        ht_node_ = 'print'
        lst_nodes = temp_node_.traverse_tree(lambda n: self.print_node(n,label=ht_node_))
        lst_nodes = filter(lambda n:n!=None,lst_nodes)
        #ypt = sc.sticky['bula_transit'][0]
        #mpt = sc.sticky['bula_transit'][1]
        for n_ in lst_nodes:
            #if type(ht_)==type('') and 'bula' in ht_:
            #    setht_ = height_from_bula(n_)
            if type(ht_)==type('') and 'envelope' in ht_:
                setht_ = height_from_envelope(n_)
            elif type(ht_)==type('') and 'angle_srf' in ht_:
                angle_srf = sc.sticky['angle_srf']
                setht_ = height_from_envelope(n_,envref=angle_srf)
            else:
                setht_ = ht_
            
            """
            #angle_srf = sc.sticky['angle_srf']
            #setht_angle = height_from_envelope(n_,envref=angle_srf)
            ## These are the Anchor points from Yonge/Eglinton and Mount Pleasant/Eglinton
            #ydist = rs.Distance(n_.shape.cpt,ypt)
            #mdist = rs.Distance(n_.shape.cpt,mpt)
            ydist = 121
            mdist = 121
            if ydist < mdist:
                maxht = sc.sticky['max_ht_yonge']# 70 storeys
            else:
                maxht = sc.sticky['max_ht_mount']# 40 storeys
            
            #IsSolarEnv = type(ht_)==type('') and 'envelope' in ht_
            IsPodium = 'podium' in n_.get_root().grammar.type['label']
            IsMaxht = maxht != None and setht_ > maxht
            if IsMaxht:
                setht_ = maxht
            if setht_ > setht_angle:
                setht_ = setht_angle 
            if IsPodium:
                setht_ = sc.sticky['ht_podium']
            """
            n_.shape.op_extrude(setht_)
            n_.grammar.type['print'] = True
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
    def print_node(self,node_,label='print'):
        #debug = sc.sticky['debug']
        if node_.grammar.type.has_key(label) and node_.grammar.type[label]:
            return node_
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
    def court(self,temp_node_,PD_):        
        #Abstract this as helper to parse ref geoms
        def helper_court_refcrv(court_ref_,subdiv_):
            N = Tree()
            ##Checks the input type and outputs the a Shape obj based on reference
            #Check if number reference to index of depth in binary data tree
            if type(court_ref_) == type(1) or type(court_ref_) == type(1.):
                if int(court_ref_) == 0:
                    root = subdiv_.get_root()
                    refshape_ = root.shape
                else:
                    refshape_ = subdiv_.shape
            ##Check if node ref
            elif type(court_ref) == type(N):
                refshape_ = court_ref_.shape
            ##Assume geometry ref, let helper deal with different geoms
            else:
                court_node = self.helper_geom2node(court_ref)
                refshape_ = court_node.shape 
            return refshape_  
        def court_slice(curr_node,rootshape,width_):
            def recurse_slice(curr_node_,matrice,valid_node_lst,diff,count,count_subdiv):
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
                            try:
                                split_node_lst = []
                                split_geoms = curr_node_.shape.op_split("NS",0.5,split_depth=0,split_line_ref=split_crv)
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
                            except:
                                pass## Split fail, so test the next line split
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
                                    L_,diff_ = recurse_slice(sn,shape_matrix,[],None,0,count_subdiv+1)
                                    valid_node_lst.extend(L_)
                                    #debug.extend(map(lambda n:n.shape.geom,L_))
                                except:
                                    pass
                                #debug.append(sn.shape.geom)
                # If the node has been split (invalid_node!= None)
                # OR the node has no valid split lines (invalid_node == None)
                # then we send it back into the recurser.
                return recurse_slice(invalid_node,matrice,valid_node_lst,diff,count+1,count_subdiv)
            
            ### REWRITE AS EXTRUSION OF BASE_MATRIX
            ### O(2n) complexity time
            offset = rootshape.op_offset_crv(width_)
            ###debug.append(rootshape.bottom_crv)
            chk_offset = rootshape.op_offset_crv(width_+0.21)
            if chk_offset:
                off_node = self.helper_geom2node(offset,curr_node)
                shape_matrix = off_node.shape.set_base_matrix()
                #debug.append(curr_node.shape.geom)
                L,diff = recurse_slice(curr_node,shape_matrix,[],None,0,0)
                #debug.extend(map(lambda n:n.shape.geom,L))
                #debug.append(diff.shape.geom)
                #print diff
                for i,n in enumerate(L):
                    n.depth = curr_node.depth+1
                    n.parent = curr_node
                    L[i] = n
                curr_node.loc = L##<<
            else:
                diff = None
            return diff
        
        #Unpack the parameters         
        court_ref = PD_['court_ref']
        court_width = PD_['court_width']
        court_slice_bool = PD_['court_slice']
        
        debug = sc.sticky['debug']
        diff = None
        lon = temp_node_.traverse_tree(lambda n: n,internal=False)
        
        for subdiv in lon:
            subdiv.shape.convert_rc('3d')
            refshape = helper_court_refcrv(court_ref,subdiv)
            if court_slice_bool:
                try:
                    diff = court_slice(subdiv,refshape,court_width)
                except Exception as e:
                    print 'Error @ court_slice', str(e)
            elif court_width > 0.:
                try:
                    subdiv.shape.op_offset(court_width,refshape.bottom_crv,dir="courtyard")
                except Exception as e:
                    print 'Error @ court', str(e)        
        return diff
    def bula(self,temp_node_,PD_):
        Bula_ = Bula()
        analysis_ref = PD_['bula_point_lst']
        value_ref = PD_['bula_value_lst']
        scale_ = PD_['bula_scale']
        
        ##Check to see what are input combo
        chk_apt = filter(lambda x: x!=None,analysis_ref) != []
        chk_val = filter(lambda x: x!=None,value_ref) != []
        chk_sc = scale_ != None
        if not chk_sc:
            scale_ = 1.
        #If both are missing, inputs are wrong
        if not chk_apt and not chk_val:
            print 'Inputs are missing!'
        #One of both values are true
        else:
            #If analysis pts are treu
            assert if chk_apt:
            #Get the analysis points
            if zones[0].shape.is_guid(cpt[0]):
                norm_cpt_lst = map(lambda p: rs.coerce3dpoint(p),cpt)
            else:
                norm_cpt_lst = cpt
            #Put analysis pts in lots
            lst_plain_pt_lst = Bula.getpoints4lot(zones,norm_cpt_lst)
            #debug.extend(reduce(lambda x,y: x+y, lst_plain_pt_lst))
            
            #Make value list
            #----
            #Add bula points for each lot
            lots = Bula.generate_bula_point(zones,lst_plain_pt_lst,values)
            
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
    sc.sticky["Grammar"] = Grammar