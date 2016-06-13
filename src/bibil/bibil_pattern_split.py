"""
Created on Jun 12, 2016
author: Saeran
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
TOL = sc.doc.ModelAbsoluteTolerance

"""import classes"""
Shape_3D = sc.sticky["Shape_3D"]
Tree = sc.sticky["Tree"]
Grammar = sc.sticky["Grammar"]

class Fabric_Grammar(Grammar):
    """Fabric Shape Grammar"""
    def __init__(self,rule,shape,deg,axis="EW",ratio=None):
        Grammar.__init__(self,rule,shape,deg,axis,ratio)
        self.maxht = None
        self.type = None
        self.label = ""
        self.density = None
    def make_label(self,node,grid_type,div,div_depth,axis="NS"):
        """make_label: self -> None"""
        ## check density weight possibly distance here
        ## pg = parent Grammar
        ## dw = density weight
        def equals(a,b,tol=int(3)):
            return abs(a-b) <= tol
        def greater(a,b,tol=int(3)):
            checktol = abs(a-b) <= tol
            return a >= b and not checktol

        # add self.dw
        ss = self.shape
        if self.label != None:
            label_identity = "-" + self.label 
        else:
            label_identity = ""
        if grid_type == "subdivide_depth":
            #print 'divdepth, div', div_depth,',', div
            # stop subdivide
            if int(div_depth) >= int(div) or int(div) == 0:
                label = None
            # start subdivide
            elif int(div_depth) == 0 and int(div) > 0:
                label = axis + "-0.50" + label_identity
            
            # alternate subdivide by axis
            elif node.parent.data.axis == "NS":
                label = "EW-0.50" + label_identity
            elif node.parent.data.axis == "EW":
                label = "NS-0.50" + label_identity
        
        elif grid_type == "subdivide_depth_same":
            if int(div_depth) >= int(div) or int(div) == 0:
                label = None
            # start subdivide
            elif int(div_depth) == 0 and int(div) > 0:
                label = axis + "-0.50" + label_identity
            
            # alternate subdivide by axis
            elif node.parent.data.axis == "NS":
                label = "NS-0.50" + label_identity
            elif node.parent.data.axis == "EW":
                label = "EW-0.50" + label_identity

        elif grid_type == "subdivide_dim":
            grid_x, grid_y = float(div[0]), float(div[1])
            if greater(ss.y_dist,grid_y,.1):
                label = "EW-" + str(grid_y/float(ss.y_dist)) + label_identity
            elif greater(ss.x_dist,grid_x,.1): 
                label = "NS-" + str(grid_x/float(ss.x_dist)) + label_identity
            else: label = None
        self.label = label
        
    def make_grammar(self,label,random_tol,cut_width,ratio):
        """ make_grammar: self -> None """
        # child rules only apply to mutations, 
        # if geometric children are returned, 
        # they are not added back to the tree object!
        label_div = 0
        deg = 0.#random_tol if (random_tol==0) else random.randint(random_tol*-1, random_tol)
        label_lst = label.split('-')
        axis = label_lst[0]
        if len(label_lst) > 1:
            label_div = label_lst[1] 
        if axis == "NS": # rename to block? fabric? nested cities
            div = ratio if ratio else float(label_div)
            axis,ratio,degree = "NS",div,deg
        elif axis == "EW":
            div = ratio if ratio else float(label_div)
            axis,ratio,degree = "EW",div,deg
        else: print 'error @ 51'
        self.axis = axis    
        self.ratio = ratio
        self.degree = degree
        child_rule = []
        self.rule += [["split",self.axis,self.ratio,self.degree,cut_width,child_rule]]

class Fabric_Tree(Tree):
    """Fabric Tree"""
    def __init__(self,data,loc=None,parent=None,sib=None,depth=0):
        Tree.__init__(self,data,loc,parent,sib,depth)
    
    def get_label(self,label):
        if self.data.label != None and label in self.data.label: 
            return self

    def make_tree_3D(self,grid_type,div,axis="NS",random_tol=0,cut_width=0,div_depth=0,ratio=None):        
        print "We are splitting recursively!"
        axis_ = axis
        if self.depth >=100: # base case 1
            print 'node.depth > 60'
        else:
            if self.parent: pg,sib = self.parent.data,self.sib  
            else: pg,sib = None,None
            self.data.make_label(self,grid_type,div,div_depth,axis_)
            #print 'label: ', self.data.label
            if self.data.label == None: # base case 2
                pass
            else:
                self.data.make_grammar(self.data.label,random_tol,cut_width,ratio)
                loc,locr = self.data.make_shape(self.data.rule)
                for i,child in enumerate(loc):
                    kill = False
                    try:
                        child_shape = Shape_3D(child,self.data.shape.cplane)
                    except Exception,e: 
                        print str(e)
                        child_shape = Shape_3D(child,self.data.shape.cplane,reset=False)
                        child_shape.bottom_crv = None
                        child_shape.top_crv = None
                        child_shape.cpt = None
                        child_shape.ht = None
                        child_shape.top_cpt = None
                        child_shape.z_dist = None
                        # primary edges
                        bp = rs.BoundingBox(child,self.data.shape.cplane)
                        ## check if 3d shape and if first 4 pts at bottom
                        if bp[0][2] > bp[4][2]:
                            bp_ = bp[4:] + bp[:4]
                            bp = bp_
                        child_shape.s_wt,child_shape.e_ht,child_shape.n_wt,child_shape.w_ht = bp[:2],bp[1:3],bp[2:4],[bp[3],bp[0]]
                        child_shape.x_dist = float(rs.Distance(child_shape.s_wt[0],child_shape.s_wt[1]))
                        child_shape.y_dist = float(rs.Distance(child_shape.e_ht[0],child_shape.e_ht[1]))
                        if abs(child_shape.x_dist-0.) < 0.0001 or abs(child_shape.y_dist-0.) < 0.0001:
                            #print 'degenerate child_shape (line or point)'
                            kill = True
                        
                    if not kill:
                        child_grammar = Fabric_Grammar(locr[i],child_shape,0,axis=axis_)
                        child_node = Fabric_Tree(child_grammar,parent=self,depth=self.depth+1)
                        self.loc.append(child_node)
                for i,c in enumerate(self.loc):
                    if len(self.loc)==2:
                        self.loc[i].sib = 1 if i == 0 else 0
                    self.loc[i].make_tree_3D(grid_type,div,axis_,random_tol,cut_width,div_depth+1,ratio)


if True:
    sc.sticky["Fabric_Grammar"] = Fabric_Grammar 
    sc.sticky["Fabric_Tree"] = Fabric_Tree