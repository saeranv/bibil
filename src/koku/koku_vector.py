'''
#Created on Jun 6, 2016
#author: Saeran Vasanthakumar
'''
from math import acos,pi
from decimal import Decimal, getcontext

## Set the decimal precision to 30 places.
getcontext().prec = 30

class Vector(object):
    
    CANNOT_NORMALIZE_ZERO_VECTOR_MSG = 'Cannot normalize zero vector'
    NO_UNIQUE_PARALLEL_COMPONENT_MSG = 'No unique parallel component'
    NO_UNIQUE_ORTHOGONAL_COMPONENT_MSG = 'No unique orthogonal component'
    ONLY_DEFINED_IN_TWO_THREE_DIM_MSG = 'Cross product is limited to 2 or 3 dimensions'
    
    def __init__(self, coord):
        try:
            if not coord:
                raise ValueError
            self.coord = tuple(map(lambda c: Decimal(c),coord))
            self.dim = len(coord)
            
        except ValueError:
            ## instantiate a custom instance of ValueError class with cust arg
            raise ValueError('The coordinates must be nonempty')
        except Exception as e: #TypeError:
            print str(e)
            #raise TypeError('The coordinates must be an iterable')
    def __repr__(self):
        return str([round(float(c),4) for c in self.coord])
    def __eq__(self, v):
        return self.coord == v.coord
    def plus(self,v):
        newv = map(lambda x: x[0]+x[1],zip(self.coord,v.coord))
        return Vector(newv)
    def minus(self,v):
        newv = map(lambda x: x[0]-x[1],zip(self.coord,v.coord))
        return Vector(newv)
    def times_scalar(self,scalar):
        scalar = Decimal(scalar)
        newv = map(lambda i: i*scalar,self.coord)
        return Vector(newv)
    def magnitude(self):
        ### Purpose: find the magnitude of a vector.
        ### find square root of sum of square of 
        ### change in all coordinates
        mag_lst = map(lambda c: c*c,self.coord) 
        sum_ = reduce(lambda i,j: i+j, mag_lst)
        return sum_**Decimal('.5')
    def normalized(self):
        ### Purpose: find the direction of vector aka 
        ### return the unit vector
        ### divide the vector coordinates by the magnitde
        ### of the vector
        try:
            magnitude = self.magnitude()
            return self.times_scalar(Decimal('1.')/magnitude)
        except ZeroDivisionError:
            ## raise genertic Exception class with custom arg
            raise Exception(self.CANNOT_NORMALIZE_ZERO_VECTOR_MSG)
    def dot_product(self,v):
        ### Purpose: Return dot product of two vectors
        ### v*w = v1*w1 + v2*w2 + .... + vn*wn
        prod_lst = map(lambda i: i[0]*i[1], zip(self.coord,v.coord))
        return reduce(lambda i,j: i+j, prod_lst)
    def angle(self,v,units='deg'):
        ### Purpse: Return angle between two vectors in degrees
        ### theta = arcos(v*w / ||v|*||w||)
        ### OR
        ### theta = arcos(normalized(v)*normalized(w))
        try:
            unitdotprod = self.normalized().dot_product(v.normalized())
            rad = acos(unitdotprod)
            deg = str(rad*(180./pi)) #because 180 deg == pi
            angle = Decimal(rad) if units == 'rad' else Decimal(deg)
            return angle
        except Exception as e:
            ## Pass generic Exception type as e variable 
            ## Check type e to see if cannot normalize zero vector error
            if self.CANNOT_NORMALIZE_ZERO_VECTOR_MSG in e.args:
                ## Other ways of taking out e.args
                print type(e), e.args, e
                ## raise custom exception
                raise Exception('Cannot compute an angle with the zero vector')
            else:
                print 'def angle error', str(e)
        
    def is_zero(self,tolerance=Decimal(str(1e-10))):
        return self.magnitude() < tolerance
    def is_parallel(self,v):
        ### Purpose: Checks if vector is parallel
        ### examines if either vector is zero vector (returns True),
        ### checks if abs angle is 0 or 180
        ### returns True; else if all False returns False.
        ### self -> boolean
        return self.is_zero() or v.is_zero()\
        or self.angle(v) == Decimal('0.') \
        or self.angle(v) == Decimal('180.')
    def is_orthogonal(self,v,tolerance=Decimal(str(1e-10))):
        ### Purpose: Checks if vector is perpendicular
        ### examines if dot product == 0. (cos(theta) == 0
        ### returns True or False
        ### self -> boolean
        return abs(self.dot_product(v)) < tolerance
    def component_projected_to(self,basis):
        ### Purpose: projects self.vector onto basis
        ### vector b; returns projected vector
        ### self, vector -> vector
        ### unitvector(b) x unitvector(b)*vector = proj(vector)
        try:
            unitb = basis.normalized()
            vbdot = unitb.dot_product(self)
            projection_vector = unitb.times_scalar(vbdot)  
            return projection_vector
        except Exception as e:
            if self.CANNOT_NORMALIZE_ZERO_VECTOR_MSG in e.args: 
                raise Exception(self.NO_UNIQUE_PARALLEL_COMPONENT_MSG)
            else:
                raise e
    def component_orthogonal_to(self,basis):
        ### Purpose: Get the perpendicular vector to a
        ### projection on the basis vector
        ### vector - vector_parrallel = vector_perpendicular
        try:
            vector_parrallel = self.component_parallel_to(basis)
            vector_perpendicular = self.minus(vector_parrallel)
            return vector_perpendicular
        except Exception as e:
            if self.NO_UNIQUE_PARALLEL_COMPONENT_MSG in e.args:
                raise Exception(self.NO_UNIQUE_ORTHOGONAL_COMPONENT_MSG)
            else:
                ## Print out e instance which contains more data about error
                raise e
    def cross_product(self,w):
        ### Purpose: Input vector self (v) and vector w,
        ### returns cross product v x w, the vector orthogonal
        ### to both (normal) as determined by right hand rule
        ### this only works for three dimensions
        ### v x w = 
        ### [[y1z2 - y2z1]
        ###  [-(x1z2 - x2z1)]
        ###  [y2x1 - y1x2]]
        try:
            if self.dim == 2:
                self, w = Vector(self.coord.append(0)), Vector(w.coord.append(0))
            x1,y1,z1 = self.coord
            x2,y2,z2 = w.coord
            if self.dim == 3:
                new_coord = [ y1*z2 - y2*z1,
                            -(x1*z2 - x2*z1),
                              x1*y2 - x2*y1]
                return Vector(new_coord)
        except ValueError as e:
            print self.ONLY_DEFINED_IN_TWO_THREE_DIM_MSG
            raise e
            
    def area_of_parallelogram(self,w):
        ### Purpose: Input two vectors in three or two dim
        ### and output the area of paralellogram defined by
        ### both
        ### Formula: ||v x w|| = |v||w||sin(theta) = area of parallelogram
        cross = self.cross_product(w)
        return cross.magnitude()
    def area_of_triangle(self,w):
        ### Purpose: Input two vectors in three or two dim
        ### and output the area of triangle defined by both
        ### Formula: ||v x w|| = |v||w||sin(theta) = area of parallelogram
        return self.area_of_parallelogram(w)/Decimal('2.0')
    def __getitem__(self, i):
        return self.coord[i]
    def __setitem__(self, i, x):
        #x is vector coordinate we are swapping
        self.coord[i] = x
    
class MyDecimal(Decimal):
    def is_near_zero(self, eps=1E-10):
        return abs(float(self)) < eps

if True:
    
    ### Vector Tests
    #"""
    ## cross product test
    vector_v = Vector(['4','6','5.5'])#[8.462,7.893,-8.187])
    vector_w = Vector(['6.984','-5.975','4.778'])
    #print vector_v.cross_product(vector_w),'\n'
    """
    ## area parallelogram test
    vector_v = Vector([-8.987,-9.838,5.031])
    vector_w = Vector([-4.268,-1.861,-8.866])
    print vector_v.area_of_parallelogram(vector_w),'\n'
    """
    """
    ## vector projection test
    vector_0 = Vector([3.039,1.879])
    vector_1 = Vector([0.825,2.036])
    print vector_0.component_parallel_to(vector_1),'\n'
    ## vector projection perpendicular test
    vector_0 = Vector([-9.88,-3.264,-8.159])
    vector_1 = Vector([-2.155,-9.353,-9.473])
    print vector_0.component_orthogonal_to(vector_1),'\n'
    ## vector addition test
    vector_0 = Vector([3.009,-6.172,3.692,-2.51])
    vector_1 = Vector([6.404,-9.144,2.759,8.718])
    print vector_0.component_parallel_to(vector_1)
    print vector_0.component_orthogonal_to(vector_1)
    """
    """
    ## vector parralel or orthogonal test
    vector_0 = Vector([-7.579,-7.88])
    vector_1 = Vector([22.737,23.64])
    print vector_0.is_parallel(vector_1), vector_0.is_orthogonal(vector_1),'\n'
    vector_0 = Vector([-2.029,9.97,4.172])
    vector_1 = Vector([-9.231,-6.639,-7.245])
    print vector_0.is_parallel(vector_1), vector_0.is_orthogonal(vector_1),'\n'
    vector_0 = Vector([-2.328,-7.284,-1.214])
    vector_1 = Vector([-1.821,1.072,-2.94])
    print vector_0.is_parallel(vector_1), vector_0.is_orthogonal(vector_1),'\n'
    vector_0 = Vector([-2.328,-7.284,-1.214])
    vector_1 = Vector([0,0,0])
    print vector_0.is_parallel(vector_1), vector_0.is_orthogonal(vector_1),'\n'
    """
    """
    ## vector dot product test
    #vector_0 = Vector([7.887,4.138])
    #vector_1 = Vector([-8.802,6.776])
    #vector_ans = vector_0.dot_product(vector_1)
    #print vector_ans,'\n'
    #vector_0 = Vector([-5.955,-4.904,-1.874])
    #vector_1 = Vector([-4.496,-8.755,7.103])
    #vector_ans = vector_0.dot_product(vector_1)
    #print vector_ans,'\n'
    ## vector angle test
    #vector_0 = Vector([3.183,-7.627])
    #vector_1 = Vector([0,0])#([-2.668,5.319])
    #vector_ans = vector_0.angle(vector_1,'rad')
    #print vector_ans,'\n'
    #vector_0 = Vector([7.35,0.221,5.188])
    #vector_1 = Vector([2.751,8.259,3.985])
    #vector_ans = vector_0.angle(vector_1,'deg')
    #print vector_ans,'\n'
    """
    
    """
    ## vector magnitude test
    vector_0 = Vector([-0.221,7.437])
    vector_ans = vector_0.magnitude()
    print vector_ans
    vector_1 = Vector([8.813,-1.331,-6.247])
    vector_ans = vector_1.magnitude()
    print vector_ans
    ## vector direction test
    vector_0 = Vector([5.581,-2.136])
    vector_ans = vector_0.normalized()
    print vector_ans
    vector_0 = Vector([1.996,3.108,-4.554])
    vector_ans = vector_0.normalized()
    print vector_ans
    """
    
    """
    ## vector sum tests
    vector_0 = Vector([8.218,-9.341])
    vector_1 = Vector([-1.129,2.111])
    vector_sum = vector_0.plus(vector_1)
    print vector_sum
    
    ## vector minus tests
    vector_0 = Vector([7.119,8.215])
    vector_1 = Vector([-8.223,0.878])
    vector_subtract = vector_0.minus(vector_1)
    print vector_subtract
    
    ## vector scalar mutiplicationt tests
    vector_0 = Vector([1.671,-1.012,-0.318])
    vm = vector_0.times_scalar(7.41)
    print vm
    """

        