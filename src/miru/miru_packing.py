"""----------------
Miru Packing
----------------""" 

import copy
import scriptcontext as sc
#Miru = sc.sticky["Miru"]
#R = copy.deepcopy(Miru)

if run:
    rule = [['separate', True], 
    ['dist_lst',[20.,27.]],\
    ['delete_dist', [25.]],\
    ['height', 90.]]
else:
    rule = []