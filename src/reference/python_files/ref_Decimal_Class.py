'''
Created on Oct 11, 2016

@author: vasanthakumars
'''


import math
from decimal import Decimal, getcontext

#Obj: loop through 9 dpeth/distToGlass combinations
#Rounding decimals ref
"""
Proper way to round financial values:
>>> Decimal("33.505").quantize(Decimal("0.01"))  # Half-even rounding by default
Decimal('33.50')
It is also common to have other types of rounding in different transactions:

>>> import decimal
>>> Decimal("33.505").quantize(Decimal("0.01"), decimal.ROUND_HALF_DOWN)
Decimal('33.50')
>>> Decimal("33.505").quantize(Decimal("0.01"), decimal.ROUND_HALF_UP)
Decimal('33.51')
"""