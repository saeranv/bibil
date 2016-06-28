"""
Created on Jun 27, 2016
@author: Saeran Vasanthakumar
"""
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