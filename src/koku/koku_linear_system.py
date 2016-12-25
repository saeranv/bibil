from decimal import Decimal, getcontext
from copy import deepcopy

from koku_vector import Vector
from koku_plane import Plane
from koku_parametrization import Parametrization
getcontext().prec = 30


class LinearSystem(object):

    ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG = 'All planes in the system should live in the same dimension'
    NO_SOLUTIONS_MSG = 'No solutions'
    INF_SOLUTIONS_MSG = 'Infinitely many solutions'

    def __init__(self, planes):
        ### Takes list of planes
        ### Checks if all planes are in the same dimension
        ### adds planes and dimension to class
        try:
            d = planes[0].dimension
            for p in planes:
                assert p.dimension == d

            self.planes = planes
            self.dimension = d
        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)
    def __len__(self):
        return len(self.planes)
    def __getitem__(self, i):
        return self.planes[i]
    def __setitem__(self, i, x):
        ### x = plane that we are setting or swapping
        ### with plane[i]
        try:
            assert x.dimension == self.dimension
            self.planes[i] = x
        except AssertionError:
            raise Exception(self.ALL_PLANES_MUST_BE_IN_SAME_DIM_MSG)
    def __repr__(self):
        ### Prints linear system
        ### Iterates each plane as an equation, and print equation of the plane.
        ret = 'Linear System:\n'
        temp = []
        for i,p in enumerate(self.planes):
            temp += ['Equation ' + str(i) + ':' + str(p)]
        ret += '\n'.join(temp)
        return ret
    def swap_rows(self, row0, row1):
        #You can achieve this swap using a temporary container
        #or you can use this, which accounts for the temp storage
        #Mutate
        self.planes[row0],self.planes[row1] = self.planes[row1],self.planes[row0]
    def multiply_coefficient_and_row(self, coefficient, row):
        #Multiples normal vector and constant by scalar coefficient
        #Makes a NEW normal vector and NEW scalar coefficient and then
        #creates a new plane instance for the row
        #This is done for two reasons:
        #1. Redefining the vector/coefficient will mutate the original 
        # plane that was referenced in initiating the object, which gets confusing
        # Will mutate.
        
        new_normal_vector = self.planes[row].normal_vector.times_scalar(coefficient)
        new_constant_term = self.planes[row].constant_term * coefficient
        self.planes[row] = Plane(normal_vector=new_normal_vector, constant_term=new_constant_term)
    def add_multiple_times_row_to_row(self, coefficient, row_index_to_add, row_index):
        # Multiples the row_index_to_add with coefficient and then
        # adds it to the row_index
        # This function will mutate the row
        
        #print 'old rows'
        #print self[row_index], 'row index'
        #print self[row_index_to_add], 'row index to add'
        #Create new row normal and constant
        new_normal = self.planes[row_index_to_add].normal_vector.times_scalar(coefficient)
        new_constant = self.planes[row_index_to_add].constant_term * coefficient
        
        #Add the rows normal and constants
        sum_normal_vector = self.planes[row_index].normal_vector.plus(new_normal)
        sum_constant_term = self.planes[row_index].constant_term + new_constant
        
        #Create new plane
        self.planes[row_index] = Plane(normal_vector=sum_normal_vector,constant_term=sum_constant_term)
        #print 'new rows'
        #print self[row_index], 'row index'
        #print self[row_index_to_add], 'row index to add'
    def indices_of_first_nonzero_terms_in_each_row(self):
        ### Finds the first nonzero terms in each row
        ### Therefore identifies the variable used to divide rows by
        ### Iterates through list of planes
        ### Finds the first nonzezo index in normal of plane (coefficient)
        ### If no nonzero, index is -1, and continues iteration at next plane
        ### Returns list of indices
        num_equations = len(self)
        num_variables = self.dimension
        indices = [-1] * num_equations

        for i,p in enumerate(self.planes):
            try:
                indices[i] = p.first_nonzero_index(p.normal_vector.coord)
            except Exception as e:
                if str(e) == Plane.NO_NONZERO_ELTS_FOUND_MSG:
                    continue
                else:
                    raise e
        return indices
      
    def compute_solution(self):
        try:
            return self.compute_ge()
        except Exception as e:
            if str(e)==self.NO_SOLUTIONS_MSG:
                return str(e)
            else:
                print str(e)
                raise e
    def compute_ge(self):
        #Takes matrix and outputs gaussian_elimination
        #(a) Unique solution to matrix as vector
        #(b) Indication there is no solution
        #(c) Indiciation there are infinite solutions
        
        system = self.compute_rref()
        # Compute pivot indices, loop through each row,
        # Check: if unique then add to vector
        # Check: if parameter present then not unique
        # Check: if 0 = k then no solution 
        solution = []
        pivot_indices = system.indices_of_first_nonzero_terms_in_each_row()
        
        for i in range(len(system))[::-1]:
            j = pivot_indices[i]
            constant_term = system[i].constant_term
            if j < 0 and not MyDecimal(constant_term).is_near_zero():
                # 0 = k, no solution
                solution = []
                raise Exception(self.NO_SOLUTIONS_MSG)
            else:
                # Check if there are other zeros
                if j+1 <= system.dimension-1: 
                    sum_coord = reduce(lambda c,d:c+d,system[i].normal_vector[j+1:])
                    sum_coord = Decimal(str(sum_coord))
                    if not MyDecimal(sum_coord).is_near_zero():
                        # Parameterization
                        basept, direction_vectors = system.get_basept_dir_vec_from_solution()
                        solution = Parametrization(basept,direction_vectors)
                        #print self.INF_SOLUTIONS_MSG
                        break
                solution.append(system[i].constant_term)
        if solution and type(solution) == type([]):
            solution.reverse()
            solution = Vector(solution)
        return solution
    def get_basept_dir_vec_from_solution(self):
        #Purpose: Inputs RREF system with infinite solutions and outputs basept and direction vectors
        
        #Example 1
        #[1,1,1]=5
        #[0,0,0]=0
        #[0,0,0]=0
        #x = 5 - 1y - 1z
        #y = 0 + 1y + 0
        #z = 0 + 0 + 1z
        #dir: t[-1,1,0],s[-1,0,1]
        #Example 2
        #[1,0,0]=5
        #[0,1,1]=6
        #[0,0,0]=0
        #x = 5 + 0 + 0
        #y = 0 + 6 - z
        #z = 0 + 0 + z
        #dir: t[0,-1,1]
        #1. Identify the parameter indices
        #Subtract the dimension of system
        #the pivot points. 
        #Example 1: (0,1,2) - (0) = [1,2] << param indices
        #Example 2: (0,1,2) - (0,1) = [2] << param indicies
        
        #2. Extract coordinates for parameter vector
        #The logic for this hinges on: 
        #    (1) how the parameter col i is equal to normal row pivot j
        #    (2) how the parameter_col[param_index] is always equal to 1, because that is parameter
        #So:
        #param_vector[pivot_index] == - self.plane[i].normal[param_index]
        #param_vector[param_index] == 1 << b/c this by definition has no pivot (will be zero row), must add manually 
        #Example 1: self[pivoti].normal[1] -> t[-1,1,0], s[-1,0,1] row[1,2] is parameter
        #Example 2: self[pivoti].normal[2] -> t[0,-1,1] row[2] is parameter
        
        num_variables = self.dimension
        num_planes = len(self.planes)
        pivot_indices = self.indices_of_first_nonzero_terms_in_each_row()
        param_indices = set(range(num_variables)) - set(pivot_indices)
        basept = [0] * num_variables
        dir_vectors = []
        
        #param_indices = []
        #for var in range(num_variables):
        #    ##
        
        #Get basept: Not clever, but clear and correct
        for i in xrange(len(self.planes)):
            pivot_index = pivot_indices[i]
            if pivot_index < 0:
                break
            basept[pivot_index] = self.planes[i].constant_term
        basept = Vector(basept)
        
        #Get direction vectors
        for param_index in param_indices:
            vector = [0] * num_variables
            for i in xrange(num_planes):
                #The param row j, in col i == param coeff
                #Except when col i == param row j
                plane = self.planes[i]
                pivot_index = pivot_indices[i]
                #If no pivot, then 
                if pivot_index < 0.:
                    #then this and all planes after
                    #are zeros therefore they correspond 
                    #to parameters = 1
                    break
                vector[i] = -1 * plane.normal_vector[param_index]
            vector[param_index] = 1   
            dir_vectors.append(Vector(vector))
        
        #print 'b', basept
        #for v in dir_vectors:
        #    print 'v', v
                
        return basept, dir_vectors
    def compute_rref(self):
        #RREF:
        #1. Triangular form
        #2. Each pivot variable has coefficient of 1
        #3. Each pivot variable is in its own column
        #4. Any non-single pivots are a parameter
        system = self.compute_triangular_form()
        numofplanes = len(self)
        nonzero_indices = system.indices_of_first_nonzero_terms_in_each_row()
        for i in xrange(numofplanes):
            coeff_index = nonzero_indices[i]
            #Now we go across each row and try to set non-pivot coeff to 0 
            j = coeff_index + 1 #because anything before pivot is zero after triangular form acheived
            i_inc = 1 #row below you are multipying by
            while j < self.dimension:
                curr_coeff = MyDecimal(system[i].normal_vector[j]) 
                #print 'cell i,j: ',i,j
                #print system[i].normal_vector
                
                if not curr_coeff.is_near_zero(): #If already zero, go to next j col
                    #start a new loop
                    while i+i_inc < numofplanes: #check if row below exists and is nonzero
                        #Transform coeff from row below to current i,j cell:
                        #rowbelow = (rowbelow * curr_coeff/below_coeff) 
                        #Then add the negative of this to current row
                        below_coeff = MyDecimal(system[i+i_inc].normal_vector[j])
                        if not below_coeff.is_near_zero():
                            factor2zero = -1/below_coeff * curr_coeff
                            system.add_multiple_times_row_to_row(factor2zero,i+i_inc,i)
                            #increment i so you avoid messing up row cell you just zeroed
                            i_inc += 1
                            break                            
                        else:#move down to next row
                            i_inc += 1
                    else:
                        #this is a paramater
                        # if all rows below are zero, then it is a parameter: continue
                        pass
                j += 1
        
        
        #Make leading/pivot coefficient to be one
        for i in xrange(numofplanes):
            coeff_index = nonzero_indices[i]
            if coeff_index >= -0.5: #will be -1 if no nonzero indices
                coeff2one = system[i].normal_vector[coeff_index] #using my getters!
                onefactor = Decimal(str(1./float(coeff2one)))
                system.multiply_coefficient_and_row(onefactor,i)
            
        #print '---'
        #print system
        
        return system
    def compute_triangular_form(self):
        # Compute triangular form, i.e
        # 2 1 1 = 4
        # 0 3 1 = 5
        # 0 0 2 = 5
        
        # Assumptions: 
        # 1. Swap with current row with topmost row below current row
        # 2. Don't multiply rows by numbers
        # 3. Only add a multiple of a row to rows underneat row underneath.
    
        system = deepcopy(self)
        #print 'orig', system
        lstofplanes = system.planes
        # define system variables
        numofeqn = len(lstofplanes)
        numofcoord = system.dimension
        col_i = 0 #the column/coordinate
        # Iterate down through each row
        for row_i in xrange(numofeqn):
            # Iterate through each column of each row
            roweqn = lstofplanes[row_i]
            while col_i < numofcoord:
                coef = MyDecimal(roweqn.normal_vector.coord[col_i])
                #Check if coeff == 0
                if coef.is_near_zero():
                    #swap rows with one below
                    IsSwap = system.swap_first_nonzero_row(row_i,col_i)
                    if not IsSwap:
                        #then all zero, so move to next column
                        col_i += 1
                        continue # this continues to next iterative loop
                system.clear_all_terms_below(row_i,col_i)
                col_i += 1
                break #break b/c done all terms below, move to next
            col_i = 0
            #print '---'
        #print 'rref', system
        return system

    def clear_all_terms_below(self,rowi,coli):
        #check not last row
        if rowi+1 < len(self.planes):
            beta = self[rowi].normal_vector.coord[coli]
            for i,roweqn in enumerate(self.planes[rowi+1:]):
                index = rowi + 1 + i
                gamma = roweqn.normal_vector.coord[coli]
                alpha = -gamma/beta
                self.add_multiple_times_row_to_row(alpha,rowi,index)
    def swap_first_nonzero_row(self,rowi,coli):
        #check if last row
        if rowi+1 < len(self.planes):
            for i,eqn in enumerate(self.planes[rowi+1:]):
                index = rowi + 1 + i
                coef2chk = eqn.normal_vector.coord[coli]
                if not MyDecimal(coef2chk).is_near_zero():
                    self.swap_rows(rowi,index)
                    return True
        return False

class MyDecimal(Decimal):
    def is_near_zero(self, eps=1E-10):
        return abs(float(self)) < eps

## Test 6: Parametrization

#"""
p0 = Plane(Vector(['0.786','0.786','0.588']),'-0.714')
p1 = Plane(Vector(['-0.138','-0.138','0.244']),'0.319')
s = LinearSystem([p0,p1])
sol = s.compute_solution()
print sol
#"""
"""
p0 = Plane(Vector(['8.631','5.112','-1.816']),'-5.113')
p1 = Plane(Vector(['4.315','11.132','-5.27']),'-6.775')
p2 = Plane(Vector(['-2.158','3.01','-1.727']),'-0.831')
s = LinearSystem([p0,p1,p2])
sol = s.compute_solution()
print sol
"""
"""
p0 = Plane(Vector(['0.935','1.76','-9.365']),'-9.955')
p1 = Plane(Vector(['0.187','0.352','-1.873']),'-1.991')
p2 = Plane(Vector(['-0.374','0.704','-3.746']),'-3.982')
p3 = Plane(Vector(['-0.561','-1.056','5.619']),'5.973')
s = LinearSystem([p0,p1,p2,p3])
sol = s.compute_solution()
print sol
"""

## Test 0
"""
p0 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p1 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
p2 = Plane(normal_vector=Vector(['1','1','-1']), constant_term='3')
p3 = Plane(normal_vector=Vector(['1','0','-2']), constant_term='2')
s = LinearSystem([p0,p1,p2,p3])
print s.indices_of_first_nonzero_terms_in_each_row()
"""
## Test 1
"""
print s.indices_of_first_nonzero_terms_in_each_row()
print "%s,%s,%s,%s" % (s[0],s[1],s[2],s[3])
print len(s)
print s
s[0] = p1
print s
print MyDecimal('1e-9').is_near_zero()
print MyDecimal('1e-11').is_near_zero()
"""
## Test 2
"""
p0 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p1 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
p2 = Plane(normal_vector=Vector(['1','1','-1']), constant_term='3')
p3 = Plane(normal_vector=Vector(['1','0','-2']), constant_term='2')

s = LinearSystem([p0,p1,p2,p3])
#print s
#print '---'
s.swap_rows(0,1)
chkrow_swap = p0 == s[1] and p1 == s[0]
chkrow_not_swap = p2 == s[2] and p3 == s[3]
if not (chkrow_swap and chkrow_not_swap):
    print 'test case 1 failed'
s.swap_rows(1,3)
if not (s[0] == p1 and s[1] == p3 and s[2] == p2 and s[3] == p0):
    print 'test case 2 failed'

s.swap_rows(3,1)
if not (s[0] == p1 and s[1] == p0 and s[2] == p2 and s[3] == p3):
    print 'test case 3 failed'

s.multiply_coefficient_and_row(1,0)
#print s[0].basepoint
#print p1.basepoint #basepoints are the same
if not (s[0] == p1 and s[1] == p0 and s[2] == p2 and s[3] == p3):
    print 'test case 4 failed'

s.multiply_coefficient_and_row(-1,2)
if not (s[0] == p1 and
        s[1] == p0 and
        s[2] == Plane(normal_vector=Vector(['-1','-1','1']), constant_term='-3') and
        s[3] == p3):
    print 'test case 5 failed'

s.multiply_coefficient_and_row(10,1)
if not (s[0] == p1 and
        s[1] == Plane(normal_vector=Vector(['10','10','10']), constant_term='10') and
        s[2] == Plane(normal_vector=Vector(['-1','-1','1']), constant_term='-3') and
        s[3] == p3):
    print 'test case 6 failed'

s.add_multiple_times_row_to_row(0,0,1)
if not (s[0] == p1 and
        s[1] == Plane(normal_vector=Vector(['10','10','10']), constant_term='10') and
        s[2] == Plane(normal_vector=Vector(['-1','-1','1']), constant_term='-3') and
        s[3] == p3):
    print 'test case 7 failed'

s.add_multiple_times_row_to_row(1,0,1)
if not (s[0] == p1 and #p1 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
        s[1] == Plane(normal_vector=Vector(['10','11','10']), constant_term='12') and
        s[2] == Plane(normal_vector=Vector(['-1','-1','1']), constant_term='-3') and
        s[3] == p3):
    print 'test case 8 failed'

#Plane(normal_vector=['-10','-10','-10', constant_term='-10')
s.add_multiple_times_row_to_row(-1,1,0)
if not (s[0] == Plane(normal_vector=Vector(['-10','-10','-10']), constant_term='-10') and
        s[1] == Plane(normal_vector=Vector(['10','11','10']), constant_term='12') and
        s[2] == Plane(normal_vector=Vector(['-1','-1','1']), constant_term='-3') and
        s[3] == p3):
    print 'test case 9 failed'
"""
"""
## Test 3: Triangular Form

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['0','1','1']), constant_term='2')
s = LinearSystem([p1,p2])
t = s.compute_triangular_form()
if not (t[0] == p1 and
        t[1] == p2):
    print 'test case 1 failed'
    

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['1','1','1']), constant_term='2')
s = LinearSystem([p1,p2])
t = s.compute_triangular_form()
if not (t[0] == p1 and
        t[1] == Plane(constant_term='1')):
    print 'test case 2 failed'

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
p3 = Plane(normal_vector=Vector(['1','1','-1']), constant_term='3')
p4 = Plane(normal_vector=Vector(['1','0','-2']), constant_term='2')
s = LinearSystem([p1,p2,p3,p4])
t = s.compute_triangular_form()
if not (t[0] == p1 and
        t[1] == p2 and
        t[2] == Plane(normal_vector=Vector(['0','0','-2']), constant_term='2') and
        t[3] == Plane()):
    print 'test case 3 failed'


p1 = Plane(normal_vector=Vector(['0','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['1','-1','1']), constant_term='2')
p3 = Plane(normal_vector=Vector(['1','2','-5']), constant_term='3')
s = LinearSystem([p1,p2,p3])
t = s.compute_triangular_form()
if not (t[0] == Plane(normal_vector=Vector(['1','-1','1']), constant_term='2') and
        t[1] == Plane(normal_vector=Vector(['0','1','1']), constant_term='1') and
        t[2] == Plane(normal_vector=Vector(['0','0','-9']), constant_term='-2')):
    print 'test case 4 failed'
"""
"""
#Test 4: RREF
p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
p3 = Plane(normal_vector=Vector(['0','0','0']), constant_term='0')
s = LinearSystem([p1,p2,p3])
a = s.compute_rref()

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['0','1','1']), constant_term='2')
s = LinearSystem([p1,p2])
r = s.compute_rref()
if not (r[0] == Plane(normal_vector=Vector(['1','0','0']), constant_term='-1') and
        r[1] == p2):
    print 'test case 1 failed'

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['1','1','1']), constant_term='2')
s = LinearSystem([p1,p2])
r = s.compute_rref()
if not (r[0] == p1 and
        r[1] == Plane(constant_term='1')):
    print 'test case 2 failed'

p1 = Plane(normal_vector=Vector(['1','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['0','1','0']), constant_term='2')
p3 = Plane(normal_vector=Vector(['1','1','-1']), constant_term='3')
p4 = Plane(normal_vector=Vector(['1','0','-2']), constant_term='2')
s = LinearSystem([p1,p2,p3,p4])
r = s.compute_rref()
if not (r[0] == Plane(normal_vector=Vector(['1','0','0']), constant_term='0') and
        r[1] == p2 and
        r[2] == Plane(normal_vector=Vector(['0','0','-2']), constant_term='2') and
        r[3] == Plane()):
    print 'test case 3 failed'

p1 = Plane(normal_vector=Vector(['0','1','1']), constant_term='1')
p2 = Plane(normal_vector=Vector(['1','-1','1']), constant_term='2')
p3 = Plane(normal_vector=Vector(['1','2','-5']), constant_term='3')
s = LinearSystem([p1,p2,p3])
r = s.compute_rref()
if not (r[0] == Plane(normal_vector=Vector(['1','0','0']), constant_term=Decimal('23')/Decimal('9')) and
        r[1] == Plane(normal_vector=Vector(['0','1','0']), constant_term=Decimal('7')/Decimal('9')) and
        r[2] == Plane(normal_vector=Vector(['0','0','1']), constant_term=Decimal('2')/Decimal('9'))):
    print 'test case 4 failed'

"""
"""
#Test 5: Gaussian Elimination
p1 = Plane(normal_vector=Vector(['5.862','1.178','-10.366']), constant_term='-8.15')
p2 = Plane(normal_vector=Vector(['-2.931','-0.589','5.183']), constant_term='-4.075')
s = LinearSystem([p1,p2])
#print s.compute_rref()
#sol = s.compute_solution()
#print sol

p1 = Plane(normal_vector=Vector(['8.631','5.112','-1.816']), constant_term='-5.113')
p2 = Plane(normal_vector=Vector(['4.315','11.132','-5.27']), constant_term='-6.775')
p3 = Plane(normal_vector=Vector(['-2.158','3.01','-1.727']), constant_term='-0.831')
s = LinearSystem([p1,p2,p3])
#print s.compute_rref()
#sol = s.compute_solution()
#print sol
#print '---'

p1 = Plane(normal_vector=Vector(['5.262','2.739','-9.878']), constant_term='-3.441')
p2 = Plane(normal_vector=Vector(['5.111','6.358','7.638']), constant_term='-2.152')
p3 = Plane(normal_vector=Vector(['2.016','-9.924','-1.367']), constant_term='-9.278')
p4 = Plane(normal_vector=Vector(['2.167','-13.543','-18.883']), constant_term='-10.567')
s = LinearSystem([p1,p2,p3,p4])
#print s.compute_rref()
#sol = s.compute_solution()
#print sol
#print '---'
"""
