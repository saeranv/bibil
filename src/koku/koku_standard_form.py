"""
Playing around with standard form of a line Ax + By = C

For parametric definition of plane see here:
http://math.stackexchange.com/questions/152467/parametric-form-of-a-plane
"""

import rhinoscriptsyntax as rs

A = 4
B = 4
#C = 100

sc = 5.#scalara multiplier
b = rs.AddLine([A*sc,B*sc,0],[0,0,0])

L = []
# Standard form of this line is
# Ax + By = C
# 10x + 12y = 500
# Any x,y that is solution to this is on the line

for i in range(100):
    x = i
    y = (C - A*x)/B
    L.append(rs.AddPoint(x,y,0))
    if abs(x-0)<0.001 or abs(y-0)<0.001:
        print 'x', x, 'y', y

yint = C/float(A)
print 'yint', yint

#Therefore C = yint * A or xint * B

## Question: convert standard form
## to parametric form by finding the 
## base points (A,B is not 0], and dir vector by moving
## line to oriign.

"""
If we move Ax + By = C to the origin point, then 
any point x,y is a direction vector for the line. 

Therefore, the normal to the line is [B,-A].
That is how you find the direction vector and normal from
standard form.

"""


"""
A_ = 12
B_ = -10
C_ = 500


for i in range(100):
    x = i
    y = (C_ - A_*x)/B_
    L.append(rs.AddPoint(x,y,0))
    print x,y
"""
a = L