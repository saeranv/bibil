"""----------------
Miru Packing
----------------""" 

import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)

R['separate'] = True 
R['dist_lst'] = [20.,27.]
R['delete_dist'] = [25.]
#TP['concentric_divide'] = True
R['height'] = 90.

if run:
    rule = [R]
else:
    rule = []
