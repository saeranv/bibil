"""----------------
Miru Divide
----------------""" 

import copy
import scriptcontext as sc
Miru = sc.sticky["Miru"]
R = copy.deepcopy(Miru)

R['divide'] = True
if len(divide_num) < 2:
    divide_num = divide_num[0]
R['div_num'] = divide_num
R['div_deg'] = 0.
R['div_cut'] = divide_cut
R['div_ratio'] = divide_ratio
R['div_type'] = divide_type
R['axis'] = axis

if run:
    rule = [R]
else:
    rule = []
    