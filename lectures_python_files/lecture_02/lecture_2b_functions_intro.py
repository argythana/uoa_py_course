
"""
BIS UOA class
author: Argyriou Thanasis
Lecture 2, Part B: Intro to "functions".
"""

# Assignment = assign **value** and also **attributes** to a "name".  

# Naming conventions for this course:  
# * snake_case_for_variables_names
# * english_names
# * no_blank_spaces_in_names
# * DO NOT use of python RESERVED names for keywords, functions, modules.
# [keywords](https://docs.python.org/3.9/reference/lexical_analysis.html#keywords)
# [functions](https://docs.python.org/3.9/library/functions.html)


# CONTENTS:

# ## 2b. Functions.
# > Different Functions => different data types (as input and as output).
# > Built-in functions.    
# > Parentheses, function call.  
# > Function arguments and parameters.  
# > Function(Function()).    
# > Various built-in functions.  

# Functions = objects that allow for:
# Decomposition, abstraction, modular code development.
# Built-in VS User-defined functions.  
# Built-in functions: https://docs.python.org/3/library/functions.html   
# Similar to mathematics ==>  processes, the output of which depends on parameters' value.
# Arguments (= formal name  for parameters values, parameters' values).
# Optional VS mandatory arguments.
# Default argument values.  
# A function can be called inside another function f(g(x)).


# ### Functions for data types.

# type() # check type  
# str() # convert to string.  
# int() # convert to integer.  
# float() # convert to float.

size = "5.9"  # string because denoted with quotes.
print(type(size))

size = float(size)  # convert to float.
print(size)

print(type(size))

size = int(size)  # convert to integer and keep only the integer part.
size

# Uncomment the line below see the error.
# int("adsd")

int(10.0)  # this works

# Uncomment the line below see the type of error.
# int("10.0")   # This does not work.

# Uncomment the line below see the type of the error.
#  example_name = int(example_name)  # Functions need the proper value type.
# The int() function cannot covert "John" to integer type.

# help(str)
# str?  # this works only in "ipython" notebooks. Not today, soon.

str(4)  # Convert an integer to string.
# No assignment here. Nothing is stored in memory. Just a "call".

type(str(4))

type(4)

type("4")  # string because denoted with quotes.

text_of_four = str(4)  # Assign a new name to a value.

print(type(4))

print(type("4"))

print(type(text_of_four))

ten = 10  # Name value pair.
ten

str(ten)  # No assignment here. Nothing is stored in memory.

type(ten)  # No assignment here. Nothing is stored in memory.

ten = str(ten)  # Assign a new value to the variable name ten.

type(ten)

ten

print(f"ten = {ten}")  # f-string notation sneakily slipped in. Read bonus file.

print("ten =", 10)


# ### Examples with print()

greetings = "Welcome to lecture 2..."
compliments = "You are my favorite class"

greetings, compliments

compliments

x = 20
y = 23

print(greetings, compliments, x, y, sep= "|", end="\n"*10)
#help(print)

print("Default print output without second argument.")

print('Default print output', "with second argument.")

print('Comma separated output', "with second argument.", sep=", ", end=",")

print('Five Extra lines print output.', end="\n" * 5)


# ### Examples with input()
# input() always returns a string

student_name = input("What is your name: ")  # Ask for user input and wait for it.

print("Hello", student_name, "! Nice to meet you.")  # Another way of print syntax.

favorite_num = input("What is your favourite number: ")  # Ask for user input and wait for it.

print(f'Cool, my favourite number is {favorite_num} too!')  # Better print syntax.

print(type(favorite_num))

number = input("give a number: ")

print(type(number))

# If you did not give a number above the code will break.
convert_input_to_integer = int(number)

convert_input_to_integer

number

number = float(input("give a number sfgsfdg: "))  # The message does not matter for the code.

print(number)


# ### Various built-in functions.
# [built-in functions docs](https://docs.python.org/3.9/library/functions.html)

x = -3

abs(x)


# help(range)
x_as_range = range(1, 10 , 2)  # x_as_range now is a "range of numbers" object.
x_as_range  # this is what we get when we call it.

#help(range)

type(x_as_range)

# Ooops! How did this boring loop slip in? This is for a future lecture.
for number in x_as_range:
    print(number)


string_with_9_characters = "You rock."
len(string_with_9_characters)  # Count characters not just letters.

len("asdf")  # Quotes are part of the definition of a string. Not counted.
# When the script is executed, why is there no output for the commands above?


# len() of numeric data types does not work in python.
# Uncomment the line below to try it.
# len(1345)

help(len)

x = 2
y = 5

print(pow(x, y))


x = 2
y = 5
z = x ** y

print(z)


# Uncomment the line below to try the error and then fix the code.
# divmod(10)

# Uncomment the line below to try the error and then fix the code.
# pow(x)  # pow() needs at least 2 arguments. But may get 3 too.

#help(pow)

# Uncomment the line below to try the error.
# pow("john", "jack")  # pow() arguments cannot be strings (text).

# Please try some functions for string data types:
# https://docs.python.org/3/library/stdtypes.html#string-methods
