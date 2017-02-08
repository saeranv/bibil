"""
Created on Jun 6, 2016
@author: Saeran Vasanthakumar
"""

import rhinoscriptsyntax as rs
import Rhino as rc
import math
import ghpythonlib.components as ghcomp
import copy
import scriptcontext as sc
import itertools


TOL = sc.doc.ModelAbsoluteTolerance



class Shape:
    """
    Parent shape operations and information
    """
    TOL = sc.doc.ModelAbsoluteTolerance

    def __init__(self,geom=None,cplane=None):
        self.geom = geom
        self.cplane = cplane
        self.north = rc.Geometry.Vector3d(0,1,0)#rs.VectorCreate([0,1,0],[0,0,0])
        self.area = None
        self.dimension = '3d'
        self.bottom_crv = None
        self.primary_axis_vector = None
        self.base_matrix = None
        self.normal = rc.Geometry.Vector3d(0,0,1)
        if geom == None:
            self.geom = rs.coercebrep(rs.AddBox([[0,0,0],[0,10,0],[-10,10,0],[-10,0,0],\
                                        [0,0,10],[0,10,10],[-10,10,10],[-10,0,10]]))
        else:
            try:
                self.reset(xy_change=True)
            except Exception as e:
                print str(e), "Error at Shape.reset()"
    def reset(self,xy_change=True):
        def get_dim_bbox(b):
            ## counterclockwise, start @ bottom SW
            #      n_wt
            #      -----
            #      |   |
            # w_ht |   | e_ht = y_dist
            #      |   |
            #      -----
            #     s_wt = x_dist
            """    self.s_wt,self.e_ht,self.n_wt,self.w_ht """
            return b[:2],b[1:3],b[2:4],[b[3],b[0]]

        # primary edges
        if xy_change == True:
            try:
                self.bottom_crv = self.get_bottom(self.geom,self.get_boundingbox(self.geom,None)[0])
            except Exception as e:
                #print str(e)##sys.exc_traceback.tb_lineno
                self.bottom_crv = None
            try:
                if self.cplane == None:
                    self.cplane = self.get_cplane_advanced(self.geom)
                self.primary_axis_vector = self.cplane.YAxis

            except Exception as e:
                print str(e)##sys.exc_traceback.tb_lineno
                self.cplane, self.primary_axis_vector = None, None
            try:
                self.bbpts = self.get_boundingbox(self.geom,self.cplane)
                self.s_wt,self.e_ht,self.n_wt,self.w_ht = get_dim_bbox(self.bbpts)
                self.ew_vector = self.n_wt[1]-self.n_wt[0]
                self.ns_vector = self.e_ht[1]-self.e_ht[0]
                """
                print 'check ew'
                print self.primary_axis_vector.IsParallelTo(self.ew_vector)
                print self.primary_axis_vector.IsPerpendicularTo(self.ew_vector)
                print ''
                """
                # x,y,z distances
                self.x_dist = float(rs.Distance(self.s_wt[0],self.s_wt[1]))
                self.y_dist = float(rs.Distance(self.e_ht[0],self.e_ht[1]))
                self.area = None
            except Exception as e:
                #print str(e)
                self.bbpts,self.s_wt,self.e_ht,self.n_wt,self.w_ht = None, None, None, None, None
            try:
                bp = self.bbpts
                self.cpt = rc.Geometry.AreaMassProperties.Compute(self.bottom_crv).Centroid
            except Exception as e:
                #print str(e)#sys.exc_traceback.tb_lineno
                self.cpt = None
        try:# curve profile info
            if xy_change == False:
                self.bbpts = self.get_boundingbox(self.geom,self.cplane)
            self.ht = float(self.bbpts[4][2])
            self.z_dist = float(float(self.bbpts[4][2]) - self.cpt[2])
        except Exception as e:
            #print str(e)#sys.exc_traceback.tb_lineno
            self.ht, self.z_dist = None, None
    def calculate_ratio_from_dist(self,axis,dist,dir_=0.):
        # Direction of cut
        # Long axis: YAxis
        # 1.0 ^
        #     |
        # 0.5 ^ w_ht = y_dist
        #     |
        # 0.0 ->->->->->->->
        #     0.0  0.5   1.0
        #  s_wt = x_dist

        ## dir: 0 = cut dist from bottom
        ## dir: 1 = cut dist from top
        ## test1: 25m/100m
        ## if dir == 0: ratio = 0.25
        ## if dir == 1: ratio = 0.75
        ## test2: 75m/100m
        ## if dir == 0: ratio = 0.75
        ## if dir == 1: ratio = 0.25
        if "NS" in axis:
            total_dist = self.x_dist
        else:# if "EW" in axis
            total_dist = self.y_dist
        # Cut from bottom
        ratio = dist/float(total_dist)
        # Cut from top
        if dir_ > 0.5:
            ratio = 1. - ratio
        return ratio
    def vector2axis(self,ref_vector):
        ## Compare ref_vector with shape axis, and return
        ## closest shape axis
        ew_axis = self.n_wt[1]-self.n_wt[0]
        ns_axis = self.e_ht[1]-self.e_ht[0]
        ## unitize
        ref_vector.Unitize()
        ew_axis.Unitize()
        ns_axis.Unitize()
        ew_dotprod = rc.Geometry.Vector3d.Multiply(ew_axis,ref_vector)
        ns_dotprod = rc.Geometry.Vector3d.Multiply(ns_axis,ref_vector)
        ## Greater the dot product, closer it is to 90
        cutaxis = "NS" if abs(ew_dotprod) < abs(ns_dotprod) else "EW"
        return cutaxis
    def op_split(self,axis,ratio,deg=0.,split_depth=0,split_line_ref=None):
        """
        op_split: self, ratio -> (list of geom)
        Splits original geom into two
        """
        debug = sc.sticky['debug']
        def helper_make_split_surf_z(ratio_):
            try:
                zht = ratio_ * self.z_dist
                splitptlst = self.bbpts[:4]+[self.bbpts[0]]
                #splitcurve_ = rc.Geometry.Curve.CreateControlPointCurve(splitptlst[:4],1)
                #splitcurve_ = sc.doc.Objects.AddCurve(splitcurve_)
                #debug.append(splitcurve_)
                splitptlst = map(lambda b:rc.Geometry.Point3d(b[0],b[1],b[2]+zht),splitptlst)
                splitcurve = rc.Geometry.Curve.CreateControlPointCurve(splitptlst,1)
                #debug.append(splitcurve)
                split_surf_ = rc.Geometry.Brep.CreatePlanarBreps(splitcurve)[0]
                return split_surf_
            except Exception as e:
                print "Error @ shape.helper_make_split_srf_z"
                print str(e)#sys.exc_traceback.tb_lineno
        def helper_make_split_line_xy(ratio_,degree,ref_shape=None):
            debug = sc.sticky['debug']
            try:
                if ref_shape:
                    s_wt,n_wt = ref_shape.s_wt,ref_shape.n_wt
                    e_ht,w_ht = ref_shape.e_ht,ref_shape.w_ht
                    x_dist,y_dist = ref_shape.x_dist,ref_shape.y_dist
                else:
                    s_wt,n_wt = self.s_wt,self.n_wt
                    e_ht,w_ht = self.e_ht,self.w_ht
                    x_dist,y_dist = self.x_dist,self.y_dist

                if axis == "NS":
                    edge_0, edge_1 = s_wt, n_wt
                    dist = ratio_* x_dist
                else:#if axis == "EW"
                    edge_0, edge_1 = e_ht, w_ht
                    dist = ratio_* y_dist

                ### helper geom that splits box
                line_0 = rs.AddLine(edge_0[0],edge_0[1])
                line_1 = rs.AddLine(edge_1[1],edge_1[0])
                # ^flip because counterclockwise
                mid_0 = rs.DivideCurveLength(line_0,dist,True,True)[1]
                mid_1 = rs.DivideCurveLength(line_1,dist,True,True)[1]
                split_line = rs.AddCurve([mid_0,mid_1],1)
                if float(degree) > 0.5:
                    cpt = rs.DivideCurve(split_line,2,True,True)[1]
                    split_line = rs.RotateObject(split_line,cpt,degree)
                sc_ = 1.5,1.5,1.5
                line_cpt = rs.DivideCurve(split_line,2)[1]
                split_line_sc = rs.ScaleObject(split_line,line_cpt,sc_)
                #split_line_sc = rs.coercecurve(split_line_sc)
                return split_line_sc
            except Exception as e:
                pass#print "Error @ shape.helper_make_split_srf_xy"
                #print str(e)#sys.exc_traceback.tb_lineno
        def helper_make_split_surf(split_line__):
            if self.ht < 1:
                ht = 1.
            else:
                ht = self.ht
            split_path = rs.AddCurve([[0,0,0],[0,0,ht*2]],1)
            if not self.is_guid(split_line__):
                split_line__ = sc.doc.Objects.AddCurve(split_line__)
            split_surf = rs.coercebrep(rs.ExtrudeCurve(split_line__,split_path))
            return split_surf
        def helper_get_split_line_surf(ratio_,axis_,deg_,split_line_ref_):
            split_line_, split_surf_ = None,None
            if split_line_ref_ != None:
                ## Check if Closed curve
                if type(self) == type(split_line_ref_):
                    split_line_ = helper_make_split_line_xy(ratio_,deg_,ref_shape=split_line_ref_)
                else:
                    split_line_ = split_line_ref_
                    if not self.is_guid(split_line_):
                        split_line_ = sc.doc.Objects.AddCurve(split_line_)
                    sc_ = 3,3,3
                    line_cpt = rs.DivideCurve(split_line_,2)[1]
                    split_line_ = rs.ScaleObject(split_line_,line_cpt,sc_)
                #debug.append(split_line_)
                split_surf_ = helper_make_split_surf(split_line_)
            elif axis_ == "Z":
                split_surf_ = helper_make_split_surf_z(ratio_)
            else:
                split_line_ = helper_make_split_line_xy(ratio_,deg_)
                split_line_ = rs.coercecurve(split_line_)
                split_surf_ = helper_make_split_surf(split_line_)

            return split_line_, split_surf_

        rs.EnableRedraw(False)
        split_line,split_surf = helper_get_split_line_surf(ratio,axis,deg,split_line_ref)
        #debug.append(split_surf)
        try:#if True:
            ## For split_depth == 0.
            if split_depth <= 0.1:
                geom = rs.coercebrep(self.geom) if self.is_guid(self.geom) else self.geom
                lst_child = geom.Split(split_surf,TOL)
                #debug.append(lst_child[0])
            ## For split_depth > 0.
            else:
                if self.z_dist < 0.09:
                    print 'not a 3d geom, therefore will not split'
                # vec transformation
                if self.is_guid(split_line):
                    split_line = rs.coercecurve(split_line)
                nc = split_line.ToNurbsCurve()
                end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
                dir_vector = end_pts[1] - end_pts[0]
                z_vector = rs.VectorCreate([0,0,0],[0,0,1])
                # create forward and backwards vector using crossproduct
                normal_f = rs.VectorCrossProduct(dir_vector,z_vector)
                normal_b = rs.VectorCrossProduct(z_vector,dir_vector)

                sc_ = split_depth,split_depth,split_depth

                normal_f.Unitize()
                normal_b.Unitize()
                normal_b = map(lambda v: v*split_depth/2.,normal_b)

                c = rs.AddCurve([rs.AddPoint(0,0,0),rs.AddPoint(normal_f[0],normal_f[1],normal_f[2])],0)
                c = rs.ScaleObject(c,rs.AddPoint(0,0,0),sc_)
                rc_cut = rs.ExtrudeSurface(split_surf,c)
                rc_cut = rs.MoveObject(rc_cut,normal_b)
                #debug.append(rc_cut)
                #debug.append(split_surf)
                lst_child = []
                rc_geom,rc_cut = rs.coercebrep(self.geom),rs.coercebrep(rc_cut)
                #ghcomp.Flip(rc_cut,sc.sticky['surface_ref'])[0]
                geom_childs = rc.Geometry.Brep.CreateBooleanDifference(rc_geom,rc_cut,TOL)
                lst_child.extend(geom_childs)
                del rc_cut
                del nc
                #debug.extend(geom_childs)
        except Exception as e:
            print "Error @ shape.op_split while splitting"
            print str(e)#, sys.traceback.tb_lineno

        ## Clean up or rearrange or cap the split child geometries
        try:
            if float(len(lst_child)) < 1. or lst_child == [None] or lst_child == []:
                lst_child = []
            else:
                if not self.is_guid(lst_child[0]):
                    lst_child_ = map(lambda child: sc.doc.Objects.AddBrep(child), lst_child)
                map(lambda child: rs.CapPlanarHoles(child),lst_child_)
                lst_child = map(lambda child: rs.coercebrep(child),lst_child_)
                if axis == "Z":
                    z_0 = rc.Geometry.AreaMassProperties.Compute(lst_child[0]).Centroid[2]
                    z_1 = rc.Geometry.AreaMassProperties.Compute(lst_child[1]).Centroid[2]
                    if z_0 > z_1:
                        tempchild = lst_child.pop(0)
                        lst_child.append(tempchild)
        except Exception as e:
            print "Error @ shape.op_split while formatting children"
            print str(e)#, sys.traceback.tb_lineno

        rs.EnableRedraw(False)
        return lst_child
    def get_boundingbox(self,geom_,cplane_):
        def check_bbpts(b):
            ## check if 3d shape and if first 4 pts at bottom
            if b[0][2] > b[4][2]:
                b_ = b[4:] + b[:4]
                b = b_
            return b
        try:
            bbpts_ = rs.BoundingBox(geom_,cplane_)
            return check_bbpts(bbpts_)
        except Exception as e:
            print "Error @ get_boundingbox"
            #print str(e)#sys.exc_traceback.tb_lineno
    def check_shape_dim(self,axis_,dim_,shape=None,min_or_max=False,tol=0.1):
        ### Checks that the shape dimension is equal to
        if shape==None:
            shape = self
        if "EW" in axis_:
            shapedim = shape.x_dist
        else:
            shapedim = shape.y_dist
        if min_or_max != False:
            ## Check if more than min
            if 'min' in min_or_max:
                IsWidth = (shapedim+tol) >= dim_
            ## Check if less than max
            else:
                IsWidth = shapedim <= (dim_+tol)
        else:
            IsWidth = abs(shapedim-dim_) <= tol
            #print shapedim, dim_
        return IsWidth
    def is_guid(self,geom):
        return type(rs.AddPoint(0,0,0)) == type(geom)
    def convert_rc(self,dim=None):
        # phase this function out
        try:
            if dim==None: dim = self.dimension
            if dim == "2d":
                if self.is_guid(self.crv):
                    self.crv = rs.coercecurve(self.crv)
                if self.is_guid(self.ext):
                    self.ext = rs.coercebrep(self.ext)
            else:
                if self.is_guid(self.bottom_crv):
                    self.bottom_crv = rs.coercecurve(self.bottom_crv)
            if self.is_guid(self.geom):
                self.geom = rs.coercegeometry(self.geom)
        except Exception as e:
            print "Error @ shape.convert_rc"
            print str(e)#sys.exc_traceback.tb_lineno
    def convert_guid(self,dim='2d'):
        # phase this out
        try:
            if dim == "2d":
                if not self.is_guid(self.crv):
                    self.crv = sc.doc.Objects.AddCurve(self.crv)
                if not self.is_guid(self.ext):
                    self.ext = sc.doc.Objects.AddBrep(self.ext)
            else:
                if self.bottom_crv and not self.is_guid(self.bottom_crv):
                    self.bottom_crv = sc.doc.Objects.AddCurve(self.bottom_crv)
            if not self.is_guid(self.geom):
                self.geom = sc.doc.Objects.AddBrep(self.geom)
        except Exception as e:
            print "Error @ shape.convert_guid"
            print str(e)#sys.exc_traceback.tb_lineno
    def get_bottom(self,g,refpt,tol=0.1):
        ## Extract curves from brep according to input cpt lvl
        try:
            if g == None: g = self.geom
            #print g
            if self.is_guid(refpt): refpt = rs.coerce3dpoint(refpt)
            if self.is_guid(g): g = rs.coercebrep(g)
            plane = rc.Geometry.Plane(refpt,rc.Geometry.Vector3d(0,0,1))
            crvs = g.CreateContourCurves(g,plane)
            return crvs[0]
        except Exception as e:
            print "Error @ shape.get_bottom"
            print str(e)#sys.exc_traceback.tb_lineno
    def move_geom(self,obj,dir_vector,copy=False):
        #Moves a geometry
        #Note, you will likely have to convert to guid and convert back to rc geom
        xf = rc.Geometry.Transform.Translation(dir_vector)
        xform = rs.coercexform(xf, True)
        id = rs.coerceguid(obj, False)
        id = sc.doc.Objects.Transform(id, xform, not copy)
        return id
    def is_near_zero(self,num,eps=1E-10):
        return abs(float(num)) < eps
    def check_region(self,crvA,crvB=None,tol=0.1):
            """
            If disjoint, output 0 else returns 1.
            Disjoint    0    There is no common area between the two regions.
            Intersect   1    The two curves intersect. There is therefore no full containment relationship either way.
            AInsideB    2    Region bounded by curveA (first curve) is inside of curveB (second curve).
            BInsideA    3    Region bounded by curveB (second curve) is inside of curveA (first curve).
            """
            disjoint = rc.Geometry.RegionContainment.Disjoint
            intersect = rc.Geometry.RegionContainment.MutualIntersection
            #add the rest
            if crvB == None:
                crvB = self.bottom_crv
            if self.is_guid(crvB):
                crvB = rs.coercecurve(crvB)
            if self.is_guid(crvA):
                crvA = rs.coercecurve(crvA)
            refplane = self.cplane
            setrel = rc.Geometry.Curve.PlanarClosedCurveRelationship (crvA,crvB,refplane,tol)
            if disjoint == setrel:
                return 0
            elif intersect == setrel:
                return 2
            else:
                return 1
    def get_normal_point_inwards(self,refline_,to_outside=False):
        ## Input a reference line or points and self.shape.polygon
        ## Returns the normal vector pointing
        ## into the polygon
        z_vector = self.normal#rs.VectorCreate([0,0,0],[0,0,1])
        ## Make sure the line is CCW, else reverse order
        IsCCW = self.check_vertex_order(refline=refline_)
        #Check to see if reffline is not a list of two points already
        if type(refline_) != type([]):
            end_pts = self.get_endpt4line(refline_)
        else:
            end_pts = refline_
        if not IsCCW:
            end_pts = [end_pts[1],end_pts[0]]
        #To check the CCW dir
        #debug.append(n_.data.shape.get_endpt4line(park_line_)[0])

        # Get direction vector and take cross-product
        dir_vector = end_pts[1] - end_pts[0]
        # Create to_inner vector using crossproduct
        # CCW dir_vector X z_vector = to_inner vector
        to_inner = rs.VectorCrossProduct(z_vector,dir_vector)
        if to_outside == True:
            to_inner.Reverse()
        to_inner.Unitize()
        return to_inner
    def extrude_pt_perpendicular_to_pt(self,basept_,reflineptlst):
        #Input: basept, list of line pts
        #Output: pt that is 90 degrees from that pt
        normvector = self.get_normal_point_inwards(reflineptlst)
        perppt = basept_ + normvector
        return perppt
    def check_vertex_order(self,refline=None):
        ### Check if the shape is counter-clockwise
        ### This is achieved by walking the polygon,
        ### and then summing the crossproduct
        ### of each adjacent vectors. If the resulting crossproduct sum
        ### is positive, then according to the RHR it is CCW else it
        ### is negative. If refline provided, we make a triangle
        ### with refline and cpt
        ### Ref: http://stackoverflow.com/posts/1167206/revisions
        if refline!=None:
            endpts_lst = []
            if type(refline) != type([]):
                linepts = self.get_endpt4line(refline)
            else:
                linepts = refline
            # Make triangle
            endpts_lst.append([self.cpt,linepts[0]])
            endpts_lst.append(linepts)
            endpts_lst.append([linepts[1],self.cpt])
        else:
            #need to test this!
            print 'First time testing the vertex order for polygon'
            print 'double check this at def check_vertex_order'
            endpts_lst = self.set_base_matrix()

        ## Loop through and take the crossproduct of edge
        i = 0
        sum_of_cross_product = 0.
        while i < (len(endpts_lst)-1):
            curr_edgepts = endpts_lst[i]
            next_edgepts = endpts_lst[i+1]
            #Cast to vector3d om case it is point3d
            curr_edgepts = map(lambda p: rc.Geometry.Vector3d(p),curr_edgepts)
            next_edgepts = map(lambda p: rc.Geometry.Vector3d(p),next_edgepts)

            curr_edgevector = curr_edgepts[1]-curr_edgepts[0]
            next_edgevector = next_edgepts[1]-curr_edgepts[0]
            cp = rs.VectorCrossProduct(curr_edgevector,next_edgevector)
            sum_of_cross_product += cp[2]
            i+=1

        #if positive, then according to RHR, vertices are CCW
        if sum_of_cross_product > 0.:
            return True
        else:
            return False
    def rotate_vector_from_axis(self,angle_,lineveclst,movehead=True,to_inside=False):
        def helper_rotate_vector(vector,deg,axis=[0,0,1]):
            axis = rs.coerce3dvector(axis)
            angle_radians = rc.RhinoMath.ToRadians(deg)
            rotvec = rc.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
            rotvec.Rotate(angle_radians, axis)
            return rotvec
        #Rotates the lst of vectors (of line) around axis pt
        #if we are moving the tail, you ahve to flip the vector so rotate vector works
        if movehead==True:
            dir_vec = lineveclst[1]-lineveclst[0]
            refvec4axis = lineveclst[0]
        else:
            dir_vec = lineveclst[0]-lineveclst[1]
            refvec4axis = lineveclst[1]
        #Vectors in rhino want to move inwards (counterwclockwise)
        #However if you are moving the tail then dsire to flip out so reverse vector
        if movehead==False:
            angle_ = angle_ * -1.0
        if to_inside == False:
            angle_ = angle_ * -1.0
        #print rotatehead
        rot_vector = helper_rotate_vector(dir_vec,angle_,axis=[0,0,1])
        rot_vector.Unitize()
        magnitude = dir_vec.Length
        rot_vector = rot_vector * magnitude
        rotated_linept = rot_vector + refvec4axis

        if movehead==True:
            linept_ = [refvec4axis,rotated_linept]
        else:
            linept_ = [rotated_linept,refvec4axis]
        return linept_
    def get_pt_of_intersection(self,lines2intersect):
        #Input: list of list of pts for TWO lines
        #Output: pt of intersection and bool of if intersection exist
        linelst4int = map(lambda lpt: rc.Geometry.Curve.CreateControlPointCurve(lpt,0),line2intersect)
        linelst4int = map(lambda crv: rs.coerceline(crv),linelst4int)
        lineA,lineB = linelst4int[0], linelst4int[1]
        IsIntersect,a,b = rc.Geometry.Intersect.Intersection.LineLine(lineA,lineB)
        if IsIntersect:
            a = lineA.PointAt(a)
        return IsIntersect,a
    def get_endpt4line(self,line_):
        if self.is_guid(line_):
            line_ = rs.coercecurve(line_)
        nc = line_.ToNurbsCurve()
        end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
        return end_pts
    def set_base_matrix(self,crv=None):
        ## Breaks up geometry into:
        ##[ [[vector1a,vector1b],  // line 1
        ##   [vector2a,vector2b],  // line 2
        ##          ....
        ##   [vectorna, vectornb]] // line n
        ## topological ordering preserved
        ## direction counterclockwise
        ## but can start from anywhere!
        #debug = sc.sticky['debug']

        if self.base_matrix == None:
            if crv == None:
                crv = self.bottom_crv
            if not self.is_guid(crv):
                crv = rs.coercecurve(crv)
            segments = crv.DuplicateSegments()
            matrix = []
            for i in xrange(len(segments)):
                segment = segments[i]
                nc = segment.ToNurbsCurve()
                end_pts = [nc.Points[i_].Location for i_ in xrange(nc.Points.Count)]
                matrix.append(end_pts)
            self.base_matrix = matrix
        return self.base_matrix
    def get_midpoint(self,line):
        #Midpoint formula: x1+x2/2, y1+y2/2
        pt1,pt2 = line[0], line[1]
        midpt = (line[0]+line[1])/2. #vector addition and division
        return midpt
    def get_shape_axis(self,crv=None):
        def helper_group_parallel(AL):
            ## Identifies parallel lines and groups them
            lop = []
            CULLDICT = {}
            for i,v in enumerate(AL):
                refdist = rs.Distance(v[0],v[1])
                refdir = v[1] - v[0]
                power_lst = []
                if i < len(AL)-1 and not CULLDICT.has_key(refdist):
                    power_lst.append(refdist)
                    AL_ = AL[i+1:]
                    for v_ in AL_:
                        currdist = rs.Distance(v_[0],v_[1])
                        currdir = v_[1] - v_[0]
                        if currdir.IsParallelTo(refdir) != 0 and not CULLDICT.has_key(currdist):
                            power_lst.append(currdist)
                            CULLDICT[currdist] = True
                if power_lst != []:
                    power_lst.sort(reverse=True)
                    power_num = reduce(lambda x,y: x+y,power_lst)
                else:
                    power_num = 0.
                lop.append(power_num)
            return lop

        ### Purpose: Input 2d planar curve
        ### and return list of vector axis based
        ### on prominence
        debug = sc.sticky['debug']
        try:
            if crv==None:
                crv = self.bottom_crv
            axis_matrix = self.set_base_matrix(crv)
            if axis_matrix != []:
                axis_power_lst = helper_group_parallel(axis_matrix)
                pa_index = axis_power_lst.index(max(axis_power_lst))
                pa_vector = axis_matrix[pa_index][1]-axis_matrix[pa_index][0]
            else:
                #degenerate crv
                pa_vector = None
            self.primary_axis_vector = pa_vector
            return self.primary_axis_vector
        except Exception as e:
            print "Error @ shape.get_shape_axis"
            print str(e)#sys.exc_traceback.tb_lineno
    def get_cplane_advanced(self,g):
        def helper_define_axis_pts(primary_vec):
            ##(origin,x,y)
            o_pt_ = rc.Geometry.Point3d(0,0,0)
            y_pt_ = primary_vec
            z_pt_ = rc.Geometry.Vector3d(0,0,1)
            ## construct x_pt_ using the communitive property of crossproduct
            x_pt_ = rc.Geometry.Vector3d.CrossProduct(y_pt_,z_pt_)
            return o_pt_,x_pt_,y_pt_
        try:
            if self.is_guid(g):
                brep = rs.coercebrep(g)
            else: brep = g
            debug = sc.sticky['debug']
            ## Get primary axis
            nc = self.bottom_crv.ToNurbsCurve()
            planar_pts = [nc.Points[i].Location for i in xrange(nc.Points.Count)]
            primary_axis_vector = self.get_shape_axis(self.bottom_crv)
            if primary_axis_vector:
                o_pt,x_pt,y_pt = helper_define_axis_pts(primary_axis_vector)
            else:
                #degenerate shape
                o_pt = rc.Geometry.Point3d(0,0,0)
                x_pt = rc.Geometry.Point3d(1,0,0)
                y_pt = rc.Geometry.Point3d(0,1,0)
            cplane = rc.Geometry.Plane(o_pt,x_pt,y_pt)
            return cplane
        except Exception as e:
            print "Error @ shape.get_cplane_advanced"
            print str(e)#sys.exc_traceback.tb_lineno
    def check_colinear_pt(self,crv,testpt,tol=0.01):
        ## May need to swap with own method
        dist = ghcomp.CurveClosestPoint(testpt,crv)[2]
        IsColinear = True if abs(dist-0.)<tol else False
        return IsColinear
    def planar_intersect_ray_with_line(self,base_vector,direction_vector,linept1,linept2,refz=0.0):
        #Input: ray (basevector and dirvector), line (two pts)
        #Output: intersection point or else False
        #Will only take place in 2d at defined z ht
        #This function took me half a day to understand!

        r0 = base_vector
        r1 = direction_vector
        a = linept1
        b = linept2

        #For ray: r0,r1; and line: a,b
        #parametric form of ray: r0 + t_1*r1 = pt
        #parametric form of line: a + t_2*b = pt

        #ray: r0 + t * d
        #r0: base point
        #d: direction vector
        #t = scalar parameter t, where 0 <= t < infinity
        #if line segment, then 0 <= t <= 1 is the parametric form of a line.

        #Solve for r0 + t_1*r1 = a + t_2*b; two unknowns t_1, t_2
        #This can result in a lot of algebra, but essentially can
        #simplify to the vector operations below
        #Ref: http://stackoverflow.com/questions/14307158/how-do-you-check-for-intersection-between-a-line-segment-and-a-line-ray-emanatin

        ## This needs to have push/pop/transformation matrix
        ## so that it can work outside of z-axis
        def helper_flatten_z(lst,z):
            return rc.Geometry.Vector3d(lst[0],lst[1],z)

        #debug = sc.sticky['debug']
        z = 0.0 #flatten then unflatten
        a = helper_flatten_z(a,z)
        b = helper_flatten_z(b,z)

        #Correct the ordering of the line segment
        IsCCW = self.check_vertex_order(refline=[a,b])
        if not IsCCW:
            a,b = b,a

        r0 = helper_flatten_z(r0,z)
        r1 = helper_flatten_z(r1,z)
        ray_dir = r0+(r1*5) - r0#(r0+r1) - r0
        #debug.append(rs.AddCurve([r0,ray_dir+r0]))
        #debug.append(b)

        ortho = rc.Geometry.Vector3d(ray_dir.Y*-1.,ray_dir.X,z)
        aToO = r0 - a
        aToB = b - a
        point_intersect = False
        denominator = aToB * ortho
        #Check if zero: Then cos(90) = 0, or ray normal and segment
        #perpendicular therefore no intersection

        if not self.is_near_zero(denominator):
            cross_prod = rc.Geometry.Vector3d.CrossProduct(aToB,aToO)
            dot_prod = ortho * aToO
            t_1 = cross_prod.Length / denominator
            t_2 = dot_prod / denominator

            #t_1 = abs(t_1)
            #t_2 = abs(t_2)
            if (t_2 >= 0. and t_2 <= 1.) and t_1 >= 0.: #t_1 can go to infinity
                #print 't1', t_1
                #print 't2', t_2
                #print '--'
                #debug.append(rs.AddCurve([r0,ray_dir+r0]))
                #Collision detected
                ix,iy = r0.X + (t_1 * ray_dir.X), r0.Y + (t_1 * ray_dir.Y)
                #print t_1
                point_intersect = rc.Geometry.Vector3d(ix,iy,refz)
        #if point_intersect:
            #debug.append(point_intersect)
            #debug.append(rs.AddCurve([r0,point_intersect]))
        return point_intersect
    def intersect_ray_with_line(self,base_vector,direction_vector,linept1,linept2,refz=None):
        #Input: ray (basevector and dirvector), line (two pts)
        #Output: intersection point or else False
        #Same as above but with rhinocommon library

        vertical_tolerance = -5.0
        r0 = base_vector
        r1 = direction_vector
        a = linept1
        b = linept2
        a.Z = a.Z + vertical_tolerance
        b.Z = b.Z + vertical_tolerance
        if refz==None: refz = self.ht
        refz -= vertical_tolerance
        debug = sc.sticky['debug']

        #extrude as surface to check int
        upnormal = self.normal * refz
        upnormalcrv = rc.Geometry.Curve.CreateControlPointCurve([self.cpt,self.cpt + upnormal])
        reflinepath = rc.Geometry.Curve.CreateControlPointCurve([a,b])
        srf2int = rc.Geometry.SumSurface.Create(reflinepath,upnormalcrv)
        ray = rc.Geometry.Ray3d(r0,r1)
        point_intersect_lst = rc.Geometry.Intersect.Intersection.RayShoot(ray,[srf2int],1)
        if point_intersect_lst:
            point_intersect_lst = list(point_intersect_lst)
            #debug.extend(point_intersect_lst)
            #debug.append(self.cpt)

        return point_intersect_lst
    def get_parallel_segments(self,lst_edge_,dir_ref_,angle_tol_):
        #Inputs lst of edges, a dir_ref
        #Outputs lst of edges that are parallel w/i tol
        parallel_edges_ = []
        #debug = sc.sticky['debug']
        for i in xrange(len(lst_edge_)):
            edge_pts = lst_edge_[i]
            dir_vec = edge_pts[1]-edge_pts[0]
            #Check for pi/0 (180,0 degrees)
            IsParallel = dir_ref_.IsParallelTo(dir_vec,angle_tol_)
            if not self.is_near_zero(IsParallel):#set this as tolerance in setback
                #yield edge_pts
                parallel_edges_.append(edge_pts)
        return parallel_edges_
    def identify_front_or_back_to_ref_edge(self,ref_edge,edges_to_check,dis_tol,front=True,ht_ref=0.0):
        #Casts a ray from front/back edges2check and sees if intersect with ref_edge
        #If identifies one front edge, then will break loop send back edge
        #Used as a way to see if the edge is back or front from a reference edge
        #ht_ref is problematic. Must get rid of with implementation of push/pop matrix for ray interesction
        debug = sc.sticky['debug']
        front_edges = []
        int_pt = None
        for i in xrange(len(edges_to_check)):
            edge = edges_to_check[i]
            edge = map(lambda pt: rc.Geometry.Point3d(pt[0],pt[1],ht_ref),edge)

            m = self.get_midpoint(edge)
            #Change this for rear stepback
            normal2steprefline = self.get_normal_point_inwards(edge,to_outside=front)
            ray_m,ray_norm = m, normal2steprefline
            line = self.get_endpt4line(ref_edge)
            int_pt = self.intersect_ray_with_line(ray_m,ray_norm,line[0],line[1],ht_ref)
            #debug.append(m)

            if int_pt:
                int_pt = int_pt[0]
                ray2geom = rc.Geometry.Ray3d(int_pt,normal2steprefline*-1)
                #debug.append(int_pt)
                #debug.append(int_pt + normal2steprefline*-10)
                pt4front = rc.Geometry.Intersect.Intersection.RayShoot(ray2geom,[self.geom],1)
                if pt4front:
                    m_ht = rs.AddPoint(m[0],m[1],ht_ref)
                    dist2front = rs.Distance(pt4front[0],m_ht)
                    if front==True and self.is_near_zero(dist2front):
                        front_edges.append(edge)
                    elif front==False and not self.is_near_zero(dist2front):
                        front_edges.append(edge)
        return front_edges
    def match_edges_with_refs(self,lst_edge,lst_refedge,norm_ht=0.0,dist_tol=1.0,angle_tol=15.0,to_front=True):
        #Purpose: Identifying edges from list of edges and ref edge by angle
        #Input: list of edges (list of pts) and list of ref_edge, tolerance
        #Output: list of edges that match angle to ref_edge, given by distance
        #debug = sc.sticky['debug']
        parallel_and_front_edges = []
        angle_tol = math.radians(angle_tol)
        #Get paralllel edges
        #Get front or back edges
        for i in xrange(len(lst_refedge)):
            sbrefedge = lst_refedge[i]
            sbrefpt = self.get_endpt4line(sbrefedge)
            dir_ref = sbrefpt[1] - sbrefpt[0]
            parallel_edges = self.get_parallel_segments(lst_edge,dir_ref,angle_tol)
            #print 'pe', len(parallel_edges)
            parallel_and_front_edges += self.identify_front_or_back_to_ref_edge(sbrefedge,parallel_edges,dist_tol,front=to_front,ht_ref=norm_ht)
            #print 'ph', len(parallel_and_front_edges)
            #print norm_ht
            #print '---'
        return parallel_and_front_edges
    def offset_perpendicular_from_line(self,ref_line,dist2offset):
        #debug = sc.sticky['debug']
        L = []
        reflineendpts = self.get_endpt4line(ref_line)
        for i in xrange(len(reflineendpts)):
            basept_ = reflineendpts[i]
            normvector = self.get_normal_point_inwards(reflineendpts)
            perppt1 = basept_ + normvector * dist2offset
            perppt2 = basept_ + normvector * -1.0 * dist2offset
            if i%2==0:
                L.append(perppt1)
                L.append(perppt2)
            else:
                L.append(perppt2)
                L.append(perppt1)
        L += [L[0]]
        return L
    def compute_straight_skeleton(self):
        ##Initialization
        #1a. Organize given vertices into LAV in SLAV
        #LAV is a doubly linked list (DLL). Here I'll treat 
        #normal python list as DLL, rather then write a new obj
        class DoubleLinkedList(object):
            #Creates empty doubly linked list
            def __init__(self):
                self.size = 0
                self.head = None
                self.tail = None
            def IsEmpty(self):
                return self.size == 0
            def __len__(self):
                return self.size
            def append(self,data):
                new_node = DLLNode(data,None,None)
                if self.head == None:
                    self.head = self.tail = new_node
                else:
                    #Add new node to front of list
                    new_node.prev = self.tail
                    new_node.next = None
                    self.tail.next = new_node
                    self.tail = new_node
                #Now complete circle
                self.head.prev = self.tail
                self.tail.next = self.head 
                self.size += 1
        class DLLNode(object):
            def __init__(self,data,prev,next):
                self.data = data
                self.next = None
                self.prev = None
            def __str__(self):
                return str(self.data)
        class Vertex(object):
            def __init__(self,vertex,edge_prev=None,edge_next=None):
                self.vertex = vertex
                self.edge_prev = edge_prev
                self.edge_next = edge_next
            def __str__(self):
                return str(self.vertex)
        ##Test
        #dll = DoubleLinkedList()
        #dll.append(1)
        #dll.append(2)
        #dll.append(3)
        
        #Test initialization
        #print 'head', dll.head
        #print 'tail', dll.tail
        #print '== 2', dll.head.next
        #print '== 2', dll.tail.prev
        #print '== 3', dll.head.prev
        #print '== 1', dll.tail.next 
        #print '== 3', dll.head.next.next
        
        #Initialize List of Active Vertices as Double Linked List
        LAV = DoubleLinkedList()
        #Add all vertices and incident edges from polygon
        for i in xrange(len(self.base_matrix[:-1])):
            v = self.base_matrix[i][0]
            edge_next = self.base_matrix[i]
            if i==0: i = -1
            edge_prev = self.base_matrix[i]
            vrt = Vertex(v,edge_prev,edge_next)
            LAV.append(vrt)
            
        #Compute the vertex angle bisector (ray) bi
        #iterate through vertex
        #get two edges
        #calculate bisector
        #if bisector on wrong side of normal, flip
        
        #print LAV.head.data.edge_next
        print LAV.tail.next
        print '--'
        print 'shape'
        
    def vector_to_transformation_matrix(self,dir_vector):
        #obj: Create transformation matrix
        # For n-dim vector create n x n matrix
        # where pivot variables are vector coordinates
        dim = len(dir_vector)
        matrix = []
        for i in xrange(dim):
            row = [0] * dim
            row[i] = dir_vector[i]
            matrix.append(row)
        return matrix
    def multiply_matrix2matrix(self,basematrix,transform_matrix):
        #Takes every single vector
        #Multiplies by transformation matrix
        #creates polyline out of resulting moved vectors
        #resets base plane
        #resets rule based on base plane
        M = []
        dim = len(basematrix[0][0])
        for i in xrange(len(basematrix)):
            vector = basematrix[i][0]
            movevector = self.vector_matrix_multiply(vector,transform_matrix,dim)
            M.append(movevector)
        return M
    def vector_matrix_multiply(self,vector,transform_matrix,dim):
        #Multiply matrix by vector
        move_vec = []
        for row_i in xrange(dim):
            move_vec_coord = 0.
            for col_i in xrange(dim):
                vector_coord = vector[col_i]
                plane_coefficient = transform_matrix[col_i][row_i]
                #print row_i, col_i
                #print plane_coefficient, ',', vector_coord
                #print ''
                move_vec_coord += vector_coord * plane_coefficient
            move_vec.append(move_vec_coord)
        return move_vec
    def get_area(self):
        try:
            area_crv = self.bottom_crv if self.dimension == '3d' else self.crv
            if self.is_guid(area_crv):area_crv = rs.coercecurve(area_crv)
            try:
                area = rc.Geometry.AreaMassProperties.Compute(area_crv).Area
            except Exception as e:
                print e
                area = self.x_dist * self.y_dist
            self.area = area
            return area
        except Exception as e:
            print "Error @ shape.get_area"
            print str(e)#sys.exc_traceback.tb_lineno
    def get_long_short_axis(self):
        if (self.x_dist > self.y_dist):
            long_dist,short_dist = self.x_dist,self.y_dist
            long_axis,short_axis = 'EW','NS'
        else:
            long_dist,short_dist = self.y_dist,self.x_dist
            long_axis,short_axis = 'NS','EW'
        return long_axis,long_dist,short_axis,short_dist
    def op_extrude(self,z_dist,curve=None):
        debug = sc.sticky['debug']
        try:
            returnflag = True
            if curve == None:
                curve = rs.coercecurve(self.bottom_crv) if self.is_guid(self.bottom_crv) else self.bottom_crv
                returnflag = True
            ext = rc.Geometry.Extrusion.Create(curve,z_dist,True)
            ## check if extruded correct dir
            refcpt = rc.Geometry.AreaMassProperties.Compute(ext).Centroid
            v = rc.Geometry.Vector3d(0,0,1)
            if z_dist > 0.:
                if refcpt[2] < self.cpt[2]:
                    #print 'move up'
                    ext.Translate(0.,0.,z_dist)
            else:
                if refcpt[2] > self.cpt[2]:
                    #print 'move down'
                    ext.Translate(0.,0.,z_dist*-1)
            brep = ext.ToBrep()
            #if returnflag == False:
            #    return brep
            if True:#else:
                self.geom = brep
                self.reset(xy_change=False)
        except Exception as e:
            print "Error @ Shape.op_extrude"
            print str(e)#sys.exc_traceback.tb_lineno
    def op_offset_crv(self,dim,curve=None,count=0,refcpt=None,corner=1):
        #print 'count: ', count, 'dim: ', dim
        if count > 5. or abs(dim-0.)<=0.1:
            return None
        else:
            try:
                if curve == None:
                    curve = copy.copy(self.bottom_crv)
                if not self.is_guid(curve):
                    curve = sc.doc.Objects.AddCurve(curve)
                if not refcpt:
                    refcpt = rs.CurveAreaCentroid(curve)[0]
                offcurve = rs.OffsetCurve(rs.CopyObject(curve),refcpt,dim,None,corner)
                #print 'offcurve', offcurve
                if not offcurve or len(offcurve) > 1:
                    dim -= 1.
                    count += 1
                    return self.op_offset_crv(dim,curve,count,refcpt,corner)
                else:
                    return offcurve[0]
            except Exception as e:
                print "Error @ Shape.op_offset_crv"
                print str(e)#sys.exc_traceback.tb_lineno
    def op_offset(self,dim,curve,dir="courtyard",useoffcrv=False):
        try:
            rs.EnableRedraw(False)
            shapecurve = self.bottom_crv
            abort = False
            if not self.is_guid(curve):
                curve = sc.doc.Objects.AddCurve(curve)
            if self.is_guid(shapecurve):
                shapecurve = rs.coercegeometry(rs.CopyObject(shapecurve))
            #curve = "let's break this fucker."
            cpt = rs.CurveAreaCentroid(curve)[0]
            #style[opt] = the corner style
            #0 = None, 1 = Sharp, 2 = Round, 3 = Smooth, 4 = Chamfer
            copy_curve = rs.CopyObject(curve)
            if not useoffcrv:
                check_curve = self.op_offset_crv(dim,copy_curve,0,refcpt=cpt)
            else: check_curve = copy_curve

            if check_curve:
                if self.is_guid(check_curve):
                    offcurve = rs.coercecurve(check_curve)
                else:
                    offcurve = check_curve
            else:
                print 'courtyard/terrace offset failed'
                diff_geom = None
                abort = True
            if dir=="courtyard" and not abort:
                ht = self.z_dist * 2.5
                geom = copy.copy(self.geom)
                geom = rs.coercegeometry(geom)
                diff_geom = rc.Geometry.Extrusion.Create(offcurve,ht,True)
                #diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
                diff_geom = rs.coercebrep(diff_geom)
            elif dir=="terrace" and not abort:
                ht = self.z_dist+1.
                offgeom = rc.Geometry.Extrusion.Create(offcurve,self.z_dist,True)
                offgeom = sc.doc.Objects.AddBrep(rs.coercebrep(offgeom))
                diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
            elif dir=="terrace_3d" and not abort:
                ht = self.z_dist+1.
                offgeom = rc.Geometry.Extrusion.Create(offcurve,self.z_dist,True)
                offgeom = rs.coercebrep(offgeom)
                geom = copy.copy(self.geom)
                geom = rs.coercebrep(geom)
                ext = rc.Geometry.Extrusion.Create(shapecurve,ht,True)
                diff_geom = sc.doc.Objects.AddBrep(rs.coercebrep(ext))
            #if dir == "courtyard":
                #print diff_geom
            if not abort:
                try:
                    #if True:
                    if dir=="courtyard":
                        booldiff = rc.Geometry.Brep.CreateBooleanDifference(geom,diff_geom,TOL)
                        if len(booldiff) > 1:
                            self.geom = booldiff
                        elif len(booldiff) > 0:
                            self.geom = booldiff[0]
                    elif dir=="terrace":
                        booldiff = rs.BooleanIntersection(diff_geom,offgeom,True)
                        #booldiff = map(lambda c: rs.coercegeometry(c),booldiff)
                        if len(booldiff)>0.1:
                            self.geom = booldiff[0]
                    elif dir=="terrace_3d":
                        booldiff = rc.Geometry.Brep.CreateBooleanIntersection(geom,offgeom,TOL)
                        booldiff = map(lambda c: sc.doc.Objects.AddBrep(c),booldiff)
                        diff_geom = offgeom
                        if len(booldiff) > 1:
                            self.geom = booldiff
                        elif len(booldiff)> 0.1:
                            self.geom = booldiff[0]
                    self.reset()
                except Exception,e:
                    print str(e)#sys.exc_traceback.tb_lineno
                    print 'fail op_offset'
            rs.EnableRedraw(True)
            return diff_geom
        except Exception as e:
            print 'Error @ Shape.op_offset'
            print str(e)#sys.exc_traceback.tb_l


if True:
    sc.sticky["Shape"] = Shape
