from decimal import Decimal, getcontext
from copy import deepcopy

from koku_vector import Vector
from koku_plane import Plane

getcontext().prec = 30

class MyDecimal(Decimal):
    def is_near_zero(self, eps=1E-10):
        return abs(float(self)) < eps
class Parametrization(object):
    BASEPT_AND_DIR_VECTORS_MUST_BE_IN_SAME_DIM_MSG = "The basepoint and direction vectors should all be in the same dimension."
    
    def __init__(self,base_pt,lst_dir_vec):
        self.base_pt = base_pt
        self.lst_dir_vec = lst_dir_vec
        self.dimension = self.base_pt.dim
        try:
            for v in lst_dir_vec:
                assert v.dim == self.dimension
        except AssertionError:
            raise Exception(self.BASEPT_AND_DIR_VECTORS_MUST_BE_IN_SAME_DIM_MSG)

    def __repr__(self):
        def make_tuple_str(vec):
            bpt_str = ""
            for i in xrange(vec.dim):
                p = round(vec[i],4)
                bpt_str += str(p)
                if i < vec.dim-1: bpt_str += ', '
            return "(" + bpt_str + ")"
        
        ret = 'Parameterization\n'
        #Base pt
        bpt = make_tuple_str(self.base_pt)
        ret += "basept: " + bpt
        #Direction Vectors
        for i in xrange(len(self.lst_dir_vec)):
            dir = self.lst_dir_vec[i]
            ret += "\ndirvec: " + make_tuple_str(dir)
        return ret

#basept = Vector(['0','0','0'])
#dir_vec1 = Vector(['0','0','1'])
#dir_vec2 = Vector(['0','1','0'])
#param = Parametrization(basept,[dir_vec1,dir_vec2])
#print param


