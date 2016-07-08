"""
Created on Jun 6, 2016
author: Saeran Vasanthakumar
"""

import scriptcontext as sc

##Phase this out and replace with type dictionary data

class Grammar:
    """ Parent Shape Grammar """
    ## WIll phase this out and swap with Pattern eventually   
    def __init__(self,shape):
        self.shape = shape
        self.type = {'label':None,'axis':"NS",'ratio':0.,'print':False}

TOL = sc.doc.ModelAbsoluteTolerance
if True:
    sc.sticky["Grammar"] = Grammar