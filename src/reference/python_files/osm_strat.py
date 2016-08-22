# Import standard library modules
import json

# Import Rhino modules
import Rhino
from Rhino.Geometry import *
from scriptcontext import doc

# import .NET libraries
import System

import rhinoscriptsyntax as rs



#-------------------------------------------------------

f = open('Data/strat_2.geojson').read() # returns a string
data = json.loads(f)
num_bldg = len(data['features'])
print 'numbldg= ', num_bldg
#print data['features'][3]['geometry']['coordinates'][0]

#for i in range(num_bldg):
#    next_loc = data['features'][i]['geometry']['coordinates'][0]
#    for j in range(len(next_loc)):
#        next_loc[j] += [0]
#    block = Block(next_loc,6)
#    Block.make_new(block)'''

