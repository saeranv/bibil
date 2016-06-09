'''
Created on Jun 8, 2016
@author: Saeran Vasanthakumar
'''

import rhinoscriptsyntax as rs
import Rhino as rc
import random
import scriptcontext as sc
import copy

"""import classes"""
Shape_2D = sc.sticky["Shape_2D"]
Shape_3D = sc.sticky["Shape_3D"]
Tree = sc.sticky["Tree"]
Grammar = sc.sticky["Grammar"]
Fabric_Tree = sc.sticky["Fabric_Tree"] 
Fabric_Grammar = sc.sticky["Fabric_Grammar"] 

class Pattern:
    """Pattern"""
    def __init__(self):
        self.lot_lst = []
    def apply_pattern_helper(self,nod,pd):
        #debug = sc.sticky['debug']
        lstnodes = []
        try:
            tempnod = self.apply_param(nod,pd)
            tempnod.traverse_tree(lambda n: n.data.shape.convert_rc('3d'),internal=False)
            lstnodes = tempnod.traverse_tree(lambda n: n, internal=False)
        except Exception as e:
            #print e.message, 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
            print 'error in pattern', str(e)
            lstnodes = nod.traverse_tree(lambda n: n, internal=False)
        return lstnodes
    def apply_pattern(self,node_, pd_,count):
        #print 'num', count
        lstnodes_ = self.apply_pattern_helper(node_,pd_)
        if pd_['child']:
            ln = []
            for i,n_ in enumerate(lstnodes_):
                #print 'child index', i
                ln_temp = self.apply_pattern(n_,pd_['child'][0],count+1)
                ln.extend(ln_temp)
            return ln
        else:
            return lstnodes_
    def se_wrapper_uni(self,node_0,time,seht,stype):
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

        #debug = sc.sticky["debug"]
        TOL = sc.doc.ModelAbsoluteTolerance
        start,end = time, abs(time - 12.) + 12.
        
        node_0.get_root().traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
        ## Get correct curve from data tree
        se_crv = helper_get_curve_in_tree(node_0,stype,seht)
        ## Get base and top
        split_ratio = seht/node_0.data.shape.z_dist
        lstchild = node_0.data.shape.op_split("Z",split_ratio)
        lot_base,lot_top = lstchild[0],lstchild[1]
        ## Generate solar envelope
        se = node_0.data.shape.op_solar_envelope(start,end,se_crv)
        sebrep = helper_intersect_solar(se,node_0,seht)
        return sebrep
    def se_wrapper_multi(self,data,time,solarht):
        #debug = sc.sticky["debug"]
        cpt = data.shape.cpt
        #time = [9,10,11,12,13]
        time += random.randint(-3,3)
        start = time
        end = start + 1.
        data.shape.make_top_crv()
        data.shape.convert_guid(dim='3d')
        #curve = top_crv#rs.CopyObject(data.shape.bottom_crv,[0,0,data.shape.ht])
        g = copy.copy(rs.coercegeometry(data.shape.geom))
        cpt = rs.coerce3dpoint(data.shape.top_cpt)#[cpt[0], cpt[1], data.shape.ht] 
        curve = data.shape.top_crv
        
        se = data.shape.op_solar_envelope(start,end,curve)
        
        htpt = rs.AddPoint(cpt[0],cpt[1],solarht)#data.shape.ht)
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
            print 'error at solar uni'
        return se
    def apply_stepback(self,lst_stepback_tuple):
        return None
    def apply_param(self,node,PD):
        """
        param_dictionary
        solar: solartype, solartime
        divis: div_num, div_deg, div_cut
        court: court, court_width, court_node
        sdiv: subdiv_num, subdiv_cuttime
        """
        debug = sc.sticky["debug"]
        TOL = sc.doc.ModelAbsoluteTolerance
        debug_print = False
        
        
        ## 0. make a copy of the geometry
        gb = node.data.shape.geom
        if node.data.shape.is_guid(gb): gb = rs.coercebrep(gb)#gb = sc.doc.Objects.AddBrep(gb)
        geo_brep = copy.copy(gb)
        
        ## 1. param 1 or param 3
        solartype = PD['solartype']
        solartime = PD['solartime']
        solarht = PD['solarht']
        
        if solartype == 1 or solartype == 3: # uni-cell
            geo_brep = self.se_wrapper_uni(node,solartime,solarht,solartype)

        ## 2. make a new, fresh node
        build_shape = Shape_3D(geo_brep,node.data.shape.cplane)
        #build_shape.cplane = build_shape.get_cplane_advanced(geo_brep)
        #build_shape.reset()
        build_grammar = Fabric_Grammar([],build_shape,0)
        temp_node = Fabric_Tree(build_grammar,parent=node,depth=0)
        
        ## 3. param 2
        div_num = PD['div_num']
        div_deg = PD['div_deg']
        div_cut = PD['div_cut']
        div_ratio = PD['div_ratio']
        flip = PD['flip']
        if div_num >= 0:
            #print div_num
            # 1. fabric subdivide
            #print 'divparam', div_param
            temp_node.data.shape.convert_guid(dim='3d')
            axis_ = "EW"
            if flip: axis_ = "NS"
            if node.parent:
                if node.parent.data.axis == "EW": 
                    if not flip: axis_ = "NS"
                    else: axis_ = "EW"
                else: 
                    if not flip: axis_ = "EW"
                    else: axis_ = "NS"
            try:
                temp_node.make_tree_3D("subdivide_depth",div_num,axis=axis_,cut_width=div_cut)
                temp_node.traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
            except Exception as e:
                print 'error at split div', str(e)
        ## 4. param 3
        if solartype == 2: # multi_cell
            sublst = temp_node.traverse_tree(lambda n:n,internal=False)
            for subnode in sublst:
                add_hour = float(random.randint(-2,2))
                if add_hour == 0.: add_hour = 1
                solartime += 1/add_hour
                se = self.se_wrapper_multi(subnode.data,solartime,solarht)
                geo_brep = rs.coercebrep(rs.CopyObject(subnode.data.shape.geom))
                unioned =  rc.Geometry.Brep.CreateBooleanUnion([se,geo_brep],TOL)
                try: 
                    unioned = unioned[0]
                    subnode.data.shape.geom = unioned
                except: print 'error unioning solartypes'
        
        ## 5. param 1
        court = PD['court']
        terrace = float(PD['terrace'])
        terrace_node = PD['terrace_node']
        court_node = PD['court_node']
        court_width = PD['court_width']
        subdiv_num = PD['subdiv_num']
        subdiv_cut = PD['subdiv_cut'] 
        subdiv_flip = PD['subdiv_flip']
        #print court_width_, subdiv_num, subdiv_cut
        if terrace > 0.:
            lon = temp_node.traverse_tree(lambda n: n,internal=False)
            for i,subdiv in enumerate(lon):
                #debug.append(subdiv.data.shape.geom)
                #tcrv = subdiv.data.shape.bottom_crv
                # 2. offset
                if debug_print:
                    print 'terracenode', terrace_node
                if int(terrace_node) == 0:
                    root = node.get_root()
                    tcrv = root.data.shape.bottom_crv
                elif int(terrace_node) == 1:
                    tcrv = subdiv.parent.data.shape.bottom_crv
                elif int(terrace_node) == 2 and subdiv.parent.parent:
                    tcrv = subdiv.parent.parent.data.shape.bottom_crv
                elif int(terrace_node) == 3 and subdiv.parent.parent.parent:
                    tcrv = subdiv.parent.parent.parent.data.shape.bottom_crv
                else:
                    tcrv = subdiv.data.shape.bottom_crv
                subdiv.data.shape.op_offset(terrace,tcrv,dir="terrace_3d")

        if court==1:
            lon = temp_node.traverse_tree(lambda n: n,internal=False)
            court_width_ = 8.
            for i,subdiv in enumerate(lon):
                subdiv.data.shape.convert_rc('3d')
                # 2. offset
                if debug_print:
                    print 'courtnode', court_node
                if int(court_node) == 0:
                    root = node.get_root()
                    bcrv = root.data.shape.bottom_crv
                    refshape = root.data.shape
                elif int(court_node) == 1:
                    bcrv = subdiv.parent.data.shape.bottom_crv
                    refshape = subdiv.parent.data.shape
                elif int(court_node) == 2 and subdiv.parent.parent:
                    bcrv = subdiv.parent.parent.data.shape.bottom_crv
                    refshape = subdiv.parent.parent.data.shape
                elif int(court_node) == 3 and subdiv.parent.parent.parent:
                    bcrv = subdiv.parent.parent.parent.data.shape.bottom_crv
                    refshape = subdiv.parent.parent.parent.data.shape
                    #print 'bcrv', bcrv
                    #debug.append(bcrv)
                else:
                    bcrv = subdiv.data.shape.bottom_crv
                    refshape = subdiv.data.shape
                
                #print refshape.bottom_crv
                area = refshape.get_area()
                long_axis,long_dist,short_axis,short_dist = refshape.get_long_short_axis()
                
                if short_dist >= 13:
                    thickfactor = float(random.randint(-2,2))
                    thickfactor = thickfactor if thickfactor != float(0) else 1. 
                    court_width_ = short_dist/3. + 1//thickfactor
                
                testcrv = refshape.op_check_offset(court_width_,bcrv)
                #debug.append(rs.coercegeometry(testcrv))
                if testcrv: 
                    if not refshape.is_guid(testcrv):
                        testcrv = sc.doc.Objects.AddCurve(testcrv)
                    offsrf = rs.AddPlanarSrf([testcrv])[0]
                    srfcplane = refshape.get_cplane_advanced(offsrf)
                    offshape_temp = Shape_3D(offsrf,srfcplane)
                    off_area = offshape_temp.get_area()
                    ofla,ofld,off_shortaxis,off_shortdist = offshape_temp.get_long_short_axis() 
                else:
                    off_area,off_shortdist,off_shortaxis = area,short_dist,short_axis 
                    
                buildht = node.data.shape.ht
                #print 'buildht', buildht
                if buildht > 21: minarea, mindist,minwidth = 170, 12, 9.5
                elif buildht > 15: minarea, mindist,minwidth = 100, 9, 8.3
                else: minarea,mindist,minwidth = 75, 7, 8.

                if court_width > 0:
                    court_width_ = court_width
                    subdiv.data.shape.op_offset(court_width_,bcrv,dir="courtyard")
                elif off_area < minarea or off_shortdist < mindist or not testcrv:
                    if court_width_ > minwidth:
                        court_width_ = minwidth #short_dist/4.
                        if buildht<15.: court_width_ = 10. 
                        subdiv.data.shape.op_offset(court_width_,bcrv,dir="courtyard")
                else:
                    if buildht<15.: court_width_ = 10. 
                    subdiv.data.shape.op_offset(court_width_,testcrv,dir="courtyard",useoffcrv=True)
                #debug_print = True
                if debug_print:
                    print 'cw: ', court_width_, 'area', off_area, 'shortdist', off_shortdist
                    print '  '
                # 3, building subdiv
                lolon = subdiv.traverse_tree(lambda n:n,internal=False)
                lolon_ = map(lambda n: n.data.shape.geom,lolon)
                #print lolon_
                for subsubdiv in lolon:
                    if subdiv_flip: saxis = "NS"
                    else: saxis = "EW"
                    #subsubdiv.make_tree_3D("subdivide_depth_same",subdiv_num,axis=saxis,random_tol=0,cut_width=subdiv_cut)
                    #except Exception, e: print str(e)
        
        ## 7. finish
        temp_node.get_root().traverse_tree(lambda n: n.data.shape.convert_rc('3d'))
        return temp_node
    

    def split_brep_zaxis(self,s,ht,splitsrf=None,geom=None,cplane=None):
        debug = sc.sticky['debug']
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

TOL = sc.doc.ModelAbsoluteTolerance
if run:
    sc.sticky["Pattern"] = Pattern 
