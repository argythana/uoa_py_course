
"""
BIS UOA class, February 2022
author: Argyriou Thanasis
BONUS file! Because the 2022 class is AMAZING!  :-)

Notes for print formatting syntax.
Since Python 3.6 we have: "formatted string literals" (f-strings)=>
Code reability and speed improvement.

Goal: Learn various print syntaxes and find the optimal one.

Try the "timeit" modified example form:
https://cito.github.io/blog/f-strings/
"""


import timeit #  help(timeit) Read it only if you have the courage.

ex_rate = 1.11
dollars = 10000 #  Play with larger numbers to check results.
euros = dollars/ex_rate

##  Uncomment line to change default digits rounding of floats.
# euros = round(euros, 5) #  Play with number of digits


##  String format syntaxes:

## https://docs.python.org/3/reference/lexical_analysis.html#f-strings
print('\n1) f-strings, default format is 16 digits in total:')
print(f'{dollars} Dollars = {euros} Euros \n')

print('2) f-strings and format euros to 6 digits in total:')
print(f'{dollars} Dollars = {euros:.6} Euros \n') #  Play with number of digits


## https://docs.python.org/3/library/stdtypes.html#old-string-formatting
print('3) String formating with % operator, default format is 6 decimals:')
print('%i Dollars = Euros %f \n' % (dollars, euros))

print('4) String formating with % operator. \n\
   Format dollars to float() and format digits to 3 decimals:')
print('%.3f Dollars = %.3f Euros \n' % (dollars, euros)) #  Play with number of digits

print('5) Print and concatenate strings, default is 16 digits in total:')
print(str(dollars) + " Dollars = " + str(euros) + " Euros" + "\n")


## https://docs.python.org/3/library/stdtypes.html#str.format
print('6) str.format method. Default is 16 digits in total:')
print("{} Dollars = {} Euros \n".format(dollars, euros))

print('7) Use commas between text, variables. Default is 16 digits in total:')
print(dollars, "Dollars =", euros, "Euros \n")
print(""*5)



## The script below measures the Seconds that it takes to:
## run 1000 times the test with each format syntax
 
print("\n ======= Execution time of various print syntaxes =======\n\
Seconds that it takes to run 1 thousand times the test with each format:\n")

format = """
def format(name, age):
    return f'He said his name is {name} and he is {age} years old.'
""", """
def format(name, age):
    return 'He said his name is %s and he is %s years old.' % (name, age)
""", """
def format(name, age):
    return 'He said his name is ' + name + ' and he is ' + str(
        age) + ' years old.'
""",  """
def format(name, age):
    return 'He said his name is {} and he is {} years old.'.format(name, age)
""", """
from string import Template

template = Template('He said his name is $name and he is $age years old.')

def format(name, age):
    return template.substitute(name=name, age=age)
"""


test = """
def test():
    for name in ('Fred', 'Barney', 'Gary', 'Rock', 'Perry', 'Jackie'):
        for age in range (20, 200):
            format(name, age)
"""


for fmt in format:
    print(f'Format is: {fmt}')
    print(timeit.timeit('test()', fmt + test, number=1000))
    print('------------------------------')
