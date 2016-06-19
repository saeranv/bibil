'''
Created on Jun 18, 2016

@author: Saeran Vasanthakumar
'''
"""
Playing around with standard form of a line Ax + By = C
"""

import rhinoscriptsyntax as rs

A = 10
B = 12
C = 500

L = []

for i in range(100):
    x = i
    y = (C - A*x)/B
    L.append(rs.AddPoint(x,y,0))
    print x,y

A_ = 12
B_ = -10
C_ = 500

for i in range(100):
    x = i
    y = (C_ - A_*x)/B_
    L.append(rs.AddPoint(x,y,0))
    print x,y

o = L