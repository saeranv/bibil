'''
Created on Dec 25, 2016
#author: Saeran Vasanthakumar
'''
from decimal import Decimal, getcontext
from koku_vector import Vector

getcontext().prec = 30


class Hyperplane(object):
    """
    Standard form for hyperplane is = Ax + By + Cz + .... Nn = k
    This is the same as the Plane/Line module, except 'line'/'plane' is 
    replaced by 'hyperplane'. 
    """
    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'
    EITHER_DIM_OR_NORMAL_VEC_MUST_BE_PROVIDED_MSG = "Either the dimension or normal must be provided"
    def __init__(self, normal_vector=None, constant_term=None, dimension=None):
        if not dimension and not normal_vector:
            raise Exception(self.EITHER_DIM_OR_NORMAL_VEC_MUST_BE_PROVIDED_MSG)
        elif not normal_vector:
            self.dimension = dimension
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        else:
            self.dimension = normal_vector.dim
        self.normal_vector = normal_vector

        if not constant_term:
            constant_term = Decimal('0')
            self.constant_term = constant_term
        else:
            self.constant_term = Decimal(constant_term)

        self.set_basepoint()

    def set_basepoint(self):
        try:
            n = self.normal_vector.coord
            c = self.constant_term
            basepoint_coords = ['0']*self.dimension
            
            ## Find the first scalar coefficient that is not zero
            ## to use as divisor to find the value of x,y,z of
            ## of basepoint
            ## Ax + By + Cz = D
            ## if A != 0; x = D/A, y = 0, z = 0
            ## if B != 0; x = 0, y = D/B, z = 0
            initial_index = Hyperplane.first_nonzero_index(n)
            initial_coefficient = n[initial_index]
            basepoint_coords[initial_index] = c/initial_coefficient
            # Now make the basepoint a vector
            self.basepoint = Vector(basepoint_coords)
        except Exception as e:
            if str(e) == Hyperplane.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e
    
    def __repr__(self):
        ### This function goves is the coefficients (A,B,C)
        ### which is calculated from the basepoints.. somehow
        num_decimal_places = 3

        def write_coefficient(coefficient, is_initial_term=False):
            coefficient = round(coefficient, num_decimal_places)
            if coefficient % 1 == 0:
                coefficient = int(coefficient)

            output = ''
            if coefficient < 0:
                output += '-'
            else:
                output += "+"
            #if coefficient > 0 and not is_initial_term:
            #    output += '+'
            #if not is_initial_term:
            #    output += ' '
            
            coefficient = str(abs(coefficient))
            if len(coefficient) < 2:
                coefficient = '0'+coefficient
            output += coefficient
            return output
        
        n = self.normal_vector.coord
        try:
            initial_index = Hyperplane.first_nonzero_index(n)
            terms = []
            for i in range(self.dimension):
                if True:#round(n[i], num_decimal_places) != 0:
                    init=(i==initial_index)
                    var = 'n_'+str(i+1)
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
        output += ' = '+str(constant)

        return output
        
    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not MyDecimal(item).is_near_zero():
                return k
        raise Exception(Hyperplane.NO_NONZERO_ELTS_FOUND_MSG)
    
    def is_parallel(self,p):
        """
        Hyperplanes are parallel when the normals are parallel.
        Check for parallelity by comparing the normals.
        """
        if True:#try:
            bool_ = self.normal_vector.is_parallel(p.normal_vector)
            return bool_
        #except Exception as e:
        #    print "Error checking Hyperplane parallel: ", str(e)
            
    def __eq__(self,p):
        """
        Hyperplanes are equal when they are parallel and
        their basis points are located in the same
        Hyperplane of origin. Check this by checking to see
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
            # If self vector NOT zero vector, heck if other normal is zero
            elif p.normal_vector.is_zero():
                return False
            # Check if parallel
            if self.is_parallel(p):
                # Make a line from two base points
                testvec = self.basepoint.minus(p.basepoint)
                # Check the dot product to see if zero = ortho
                # to the normal vectors
                # Because Hyperplane equality occurs when basis points are
                # in the same Hyperplane of origin
                return testvec.is_orthogonal(self.normal_vector)
            else:
                return False
        except Exception as e:
            print "Error checking line equality: ", str(e)
            
            
class MyDecimal(Decimal):
    def is_near_zero(self, eps=1E-10):
        return abs(float(self)) < eps



### Hyperplane tests

##init test
#plane_0 = Plane(Vector([3,4,1]),40)
#print plane_0
### Plane parallel
"""
plane_0 = Plane(Vector(["-0.412","3.806","0.728"]),"-3.46")
plane_1 = Plane(Vector(["1.03","-9.515","-1.82"]),"8.65")
print 'test 1'
print 'is eq', plane_1 == plane_0
print 'is parallel', plane_1.is_parallel(plane_0)

plane_0 = Plane(Vector(['2.611','5.528','0.283']),'4.6')
plane_1 = Plane(Vector(['7.715','8.306','5.342']),'3.76')
print '\ntest 2'
print 'is eq', plane_1 == plane_0
print 'is parallel', plane_1.is_parallel(plane_0)

plane_0 = Plane(Vector(['-7.926','8.625','-7.212']),'-7.952')
plane_1 = Plane(Vector(['-2.642','2.875','-2.404']),'-2.443')
print '\ntest 3'
print 'is eq', plane_1 == plane_0
print 'is parallel', plane_1.is_parallel(plane_0)

plane_0 = Plane(Vector(['1','2','3']),'5')
plane_1 = Plane(Vector(['2','4','6']),'10')
print '\ntest 4'
print 'is eq', plane_1 == plane_0
print 'is parallel', plane_1.is_parallel(plane_0)
"""
