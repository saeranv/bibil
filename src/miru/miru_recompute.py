"""----------------
Miru Recompute Solution
----------------""" 

import Grasshopper
import Grasshopper.Kernel as gh



## This is a refence right now, must copy and paste 
## into ghcomponent to work
objnum = 0
if reset:
    ghenv.Component.Message = 'Recompute_Soln'
    document = ghenv.Component.OnPingDocument()
    
    objects = list(document.Objects)
    for obj in objects:
        #get the ghpython components
        if type(obj)!= type(ghenv.Component):
            pass
        else:
            chk_bug = obj.Name!=None and "Ladybug" in obj.Name
            chk_self = obj.Message!=None and "Recompute_Soln" in obj.Message
            if chk_bug or chk_self:
                pass
            else:
                obj.ExpireSolution(True)
                objnum += 1

o = "Recomputed %s compoents!" % str(objnum)
print o
