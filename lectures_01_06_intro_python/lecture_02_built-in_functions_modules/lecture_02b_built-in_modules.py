"""
BIS UOA class
author: Argyriou Thanasis
Lecture 2, Part B: Built-in Modules and dot notation.
"""

# Lecture 2, Part B: Built-in Modules and dot notation.
# > Import a module, from module, use aliases.  
# > math, random, statistics.  
# > Function and method dot notation.
# > **Built-in** vs **installed** vs **user-defined** modules.   
# > Methods are functions too.  
# [Numeric and Mathematical Modules](https://docs.python.org/3/library/numeric.html)


###-----------------------------------------------------------------
# ### ["math" module methods](https://docs.python.org/3/library/math.html)

import math

#Uncomment the line below to read help on math module.
# help(math)

# uncomment and try autocomplete and suggested methods.
# math.

###-----------------------------------------------------------------
#method dot notation
math.cos(1)

help(math.exp)

math.exp(4)

# Τhe code breaks here. No reference to module.
# Ποιός είναι; Τίνος είσαι; Δεν τον ξέρω τον κύριο!
# Uncomment the line below to try the error.
# cos(1)  # Explicitly refence the module that contains the method.

math.e ** 4

number = 10

print(math.sqrt(number)) 

from math import cos, sqrt

cos(1) # this works now. Do you understand why?

sqrt(16)  # this works now. Do you understand why?

from math import sqrt as square_root  # alias = ψευδώνυμο

square_root(16)

# Not recommended practice. SUPER IMPORTANT.
from math import *  # import everything from math module.

cos(1)  # this works now. But is a very bad practice.


###-----------------------------------------------------------------
# ### ["statistics" module methods](https://docs.python.org/3/library/statistics.html)

## use aliases!
import statistics as stats


list_of_x = [1, 2, 3, 4, 4, 10, 4]

print(stats.mean(list_of_x))

stats.stdev(list_of_x)


###-----------------------------------------------------------------
# ### ["random" module methods](https://docs.python.org/3/library/random.html)

import random as rm

rm.randint(1, 100)

# The code two lines below does not work now. Why?
# Uncomment the line below and try to understand the problem.
# random.randint(1, 100)

rm.gauss(30, 10)

# Uncomment the lines below one by one. Try to see what works when.
#help(rm.gauss)
#help(random.gauss)
