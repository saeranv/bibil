'''
Created on Jun 6, 2016

@author: Saeran Vasanthakumar
'''
from decimal import Decimal, getcontext
from vector import Vector

getcontext().prec = 30


class Plane(object):
    """
    Standard form for plane is = Ax + By + Cz = k
    This is the same as the Line module, except 'line' is 
    replaced by 'plane'. 
    """
    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'

    def __init__(self, normal_vector=None, constant_term=None):
        self.dimension = 3

        if not normal_vector:
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        self.normal_vector = normal_vector

        if not constant_term:
            constant_term = Decimal('0')
        self.constant_term = Decimal(constant_term)

        self.set_basepoint()

    def set_basepoint(self):
        try:
            n = self.normal_vector.coord
            c = self.constant_term
            basepoint_coords = ['0']*self.dimension

            initial_index = Plane.first_nonzero_index(n)
            initial_coefficient = n[initial_index]

            basepoint_coords[initial_index] = c/initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e

    def __str__(self):

        num_decimal_places = 3

        def write_coefficient(coefficient, is_initial_term=False):
            coefficient = round(coefficient, num_decimal_places)
            if coefficient % 1 == 0:
                coefficient = int(coefficient)

            output = ''

            if coefficient < 0:
                output += '-'
            if coefficient > 0 and not is_initial_term:
                output += '+'
            if not is_initial_term:
                output += ' '
            output += '{}'.format(abs(coefficient))

            return output

        n = self.normal_vector.coord

        try:
            initial_index = Plane.first_nonzero_index(n)
            terms = []
            for i in range(self.dimension):
                if round(n[i], num_decimal_places) != 0:
                    init=(i==initial_index)
                    var = 'x_{}'.format(i+1)
                    coef = write_coefficient(n[i],is_initial_term=init)
                    coef_w_var = coef + var
                    terms.append(coef_w_var)
            output = ' '.join(terms)

        except Exception as e:
            if str(e) == self.NO_NONZERO_ELTS_FOUND_MSG:
                output = '0'
            else:
                print e.message
                raise e
        constant = round(self.constant_term, num_decimal_places)
        if constant % 1 == 0:
            constant = int(constant)
        output += ' = {}'.format(constant)

        return output

    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not MyDecimal(item).is_near_zero():
                return k
        raise Exception(Plane.NO_NONZERO_ELTS_FOUND_MSG)
    
    def is_parallel(self,p):
        """
        Planes are parallel when the normals are parallel.
        Check for parallelity by comparing the normals.
        """
        try:
            bool_ = self.normal_vector.is_parallel(p.normal_vector)
            return bool_
        except Exception as e:
            print "Error checking plane parallel: ", str(e)

    def __eq__(self,p):
        """
        Planes are equal when they are parallel and are
        their basis points are located in the same
        plane of origin. Check this by checking to see
        if line made by two basis points is perpendicular
        to the normal vector. 
        """
        try:
            # Check to see if normal is zero vector
            if self.normal_vector.is_zero():
                # If other line is not zero, not equal
                if not p.normal_vector.is_zero():
                    return False
                # if both normals are zero
                # check too see if constant terms are equal
                else:
                    diff = self.constant_term - p.constant_term
                    return MyDecimal(diff).is_near_zero()
            # Else check if other normal is zero
            elif p.normal_vector.is_zero():
                return False
            # Check if parallel
            if self.is_parallel(p):
                # Make a line from two base points
                testvec = self.basepoint.minus(p.basepoint)
                # Check the dot product to see if zero = ortho
                # to the normal vectors
                return testvec.is_orthogonal(self.normal_vector)
            else:
                return False
        except Exception as e:
            print "Error checking line equality: ", str(e)

class MyDecimal(Decimal):
    def is_near_zero(self, eps=1e-10):
        return abs(self) < eps



### Plane tests
"""
##init test
plane_0 = Plane(Vector([0,0,1]),3)
#print plane_0
### Plane parallel
plane_0 = Plane(Vector([-0.412,3.806,0.728]),-3.46)
plane_1 = Plane(Vector([1.03,-9.515,-1.82]),8.65)
print 'test 1'
print plane_1 == plane_0
plane_0 = Plane(Vector([2.611,5.528,0.283]),4.6)
plane_1 = Plane(Vector([7.715,8.306,5.342]),3.76)
print '\ntest 2'
print plane_1 == plane_0
print plane_1.is_parallel(plane_0)
plane_0 = Plane(Vector([-7.926,8.625,-7.212]),-7.952)
plane_1 = Plane(Vector([-2.642,2.875,-2.404]),-2.443)
print '\ntest 3'
print plane_1 == plane_0
print plane_1.is_parallel(plane_0)
"""
plane_0 = Plane(Vector([1,2,3]),5)
plane_1 = Plane(Vector([2,4,6]),10)
print '\ntest 3'
print plane_1 == plane_0
print plane_1.is_parallel(plane_0)

