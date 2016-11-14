"""
Trinco UI
"""

#import rhinoscriptsyntax as rs
#import Rhino as rc
import scriptcontext as sc
#import copy
#import clr

#clr.AddReference("Grasshopper")
#from Grasshopper.Kernel.Data import GH_Path
#from Grasshopper import DataTree
    

## Import classes
#Shape = sc.sticky["Shape"]
#Tree = sc.sticky["Tree"] 
Grammar = sc.sticky["Grammar"]
#Bula = sc.sticky["Bula"]
#Miru = sc.sticky["Miru"]
    
node_in = filter(lambda n: n!=None,node_in)
if run and node_in != []:
    G = Grammar()
    sc.sticky["debug"] = []
    debug = sc.sticky["debug"]
    node_out = G.main_UI(node_in,rule_in,label_)
else:
    print 'Add inputs!'
    
