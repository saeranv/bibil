'''
Created on Jun 7, 2016
#@author: user
'''
'''
Created on Jun 6, 2016
#author: Saeran Vasanthakumar
'''
from decimal import Decimal, getcontext
from koku_vector import Vector
import sys

## Set the decimal precision to 30 places.
getcontext().prec = 30

class Line(object):

    NO_NONZERO_ELTS_FOUND_MSG = 'No nonzero elements found'
    def __init__(self, normal_vector=None, constant_term=None):
        """
        ### Purpose: generates line object
        ### Inputs normal vector and constant term
        ### Outputs None
        ### The standard form of the line is:
        ### Ax + By = k
        """
        self.dimension = 2
        
        ## The normal vector [A,B] gives the coefficients for
        ## the standard form of the line
        ## The direction vector is [-B,A] 
        if not normal_vector:
            all_zeros = ['0']*self.dimension
            normal_vector = Vector(all_zeros)
        self.normal_vector = normal_vector

        if not constant_term:
            constant_term = Decimal('0')
        self.constant_term = Decimal(constant_term)
        
        ## Sets the basepoint by setting one of the
        ## coordinates to zero
        ## Formula: y = c/B or x = c/A
        self.set_basepoint()
    def set_basepoint(self):
        """
        The basepoint is the y or x or z intercept:
        [0,k/B] iff B!=0
        [k/A,0] iff A!=0
        """
        try:
            n = self.normal_vector.coord
            c = self.constant_term
            basepoint_coords = ['0']*self.dimension
            
            ## Find the first scalar coefficient that is not zero
            ## to use as divisor to find the value of x,y,z of
            ## of basepoint
            ## Ax + By = C
            ## if A != 0; x = C/A, y = 0
            ## if B != 0; x = 0, y = C/B
            initial_index = Line.first_nonzero_index(n)
            initial_coefficient = n[initial_index]
            basepoint_coords[initial_index] = c/initial_coefficient
            self.basepoint = Vector(basepoint_coords)

        except Exception as e:
            if str(e) == Line.NO_NONZERO_ELTS_FOUND_MSG:
                self.basepoint = None
            else:
                raise e
    def __repr__(self):
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
            output += str(abs(coefficient))

            return output

        n = self.normal_vector.coord
        try:
            
            initial_index = Line.first_nonzero_index(n)
            terms = []
            for i in range(self.dimension):
                ## If normal A,B,C... is not equal to zero
                if round(n[i], num_decimal_places) != 0:
                    ## True if it is initial index 
                    init=(i==initial_index)
                    var = 'n_' + str(i+1) #n1,n2,n3
                    coef = write_coefficient(n[i],is_initial_term=init)
                    coef_w_var = coef + var
                    terms.append(coef_w_var)
            output = ' '.join(terms)
        
        
        except Exception as e:
            if str(e) == self.NO_NONZERO_ELTS_FOUND_MSG:
                output = '0'
            else:
                print e.message, \
                    'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)
                raise e
        
        constant = round(self.constant_term, num_decimal_places)
        if constant % 1 == 0:
            constant = int(constant)
        output += ' = ' + str(constant)

        return output
    @staticmethod
    def first_nonzero_index(iterable):
        for k, item in enumerate(iterable):
            if not MyDecimal(item).is_near_zero():
                return k
        #print Line.NO_NONZERO_ELTS_FOUND_MSG
        raise Exception(Line.NO_NONZERO_ELTS_FOUND_MSG)
    
    def is_parallel(self,line):
        """
        Input line and self. Checks if the normal vectors 
        of two lines are parallel. Outputs Boolean.
        """
        try:
            bool_ = self.normal_vector.is_parallel(line.normal_vector)
            return bool_
        except Exception as e:
            print "Error checking line parallel: ", str(e)
    def __eq__(self,line):
        """
        Input line and self. Line is equal if parallel 
        and intersects along infinite points (lines are
        on top of each other). 
        To check this: find basis point on each line, get vector
        between both points and see if that vector is orthogonal
        to the normal vector.
        """
        try:
            # Check to see if normal is zero vector
            if self.normal_vector.is_zero():
                # If other line is not zero, not equal
                if not line.normal_vector.is_zero():
                    return False
                # Check equality of constant terms??
                else:
                    diff = self.constant_term - line.constant_term
                    return MyDecimal(diff).is_near_zero()
            elif line.normal_vector.is_zero():
                return False

            if self.is_parallel(line):
                testvec = self.basepoint.minus(line.basepoint)
                # Check the dot product to see if zero = ortho
                return testvec.is_orthogonal(self.normal_vector)
            else:
                return False
        except Exception as e:
            print "Error checking line equality: ", str(e)
    def get_intersection(self,line):
        """
        Purpose: Check for intersection between two lines.
        """
        try:
            # If equal therefore infinite intersections.
            if self.is_equal(line): 
                return self
            # If lines not equal but parallel, not intersect. 
            elif self.is_parallel(line):
                return None
            # If lines not equal and not parallel then intersect exists
            else:
                sn = self.normal_vector.coord
                ln = line.normal_vector.coord
                A,B,k = sn[0],sn[1],self.constant_term
                C,D,m = ln[0], ln[1],line.constant_term
                y = (A*m - k*C)/(A*D - B*C)
                x = (m - D*y)/C
                return Vector([x,y])
        except ZeroDivisionError:
            # the case when lines are equal
            if self == line:
                return self
            else:
                return None
      
class MyDecimal(Decimal):
    def is_near_zero(self, eps=1E-10):
        return abs(float(self)) < eps

"""
## testing __init__ for line
line_0 = Line(Vector([3,4]),100)
print "Init:",line_0
## testing parallel for line
line_0 = Line(Vector([4.046,2.836]),1.21)
line_1 = Line(Vector([10.115,7.09]),3.025)
print "Parallel:", line_0.is_parallel(line_1)
## testing equality for line
line_0 = Line(Vector([3,4]),3.)
line_1 = Line(Vector([3,4]),3.)
print "Equality:", line_0 == line_1
"""
"""
## testing intersection for lines 1
line_0 = Line(Vector([4.046,2.836]),1.21)
line_1 = Line(Vector([10.115,7.09]),3.025)
print "intersection:", line_0.get_intersection(line_1)
## testing intersection for lines 2
line_0 = Line(Vector([7.204,3.182]),8.68)
line_1 = Line(Vector([8.172,4.114]),9.883)
print "intersection:", line_0.get_intersection(line_1)
## testing intersection for lines 3
line_0 = Line(Vector([1.182,5.562]),6.744)
line_1 = Line(Vector([1.773,8.343]),9.525)
print "intersection:", line_0.get_intersection(line_1)
"""