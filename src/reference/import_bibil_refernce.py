'''
Created on Jun 8, 2016
'''


import sys
#import os

src = "C:\\saeran\\master\\git\\bibil\\src"
if not src in sys.path:
    sys.path.insert(0,src)
#for i in sys.path:
#    print i
import koku

vector = koku.koku_vector
line = koku.koku_line
plane = koku.koku_plane

#koku.koku_vector.minus()

#kdir = src+"\koku"
#print os.listdir(kdir)

