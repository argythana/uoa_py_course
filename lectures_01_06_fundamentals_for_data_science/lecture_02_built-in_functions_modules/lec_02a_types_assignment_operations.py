
"""
BIS UOA class
author: Argyriou Thanasis
Lecture 1, Part C: Intro to basic data types, assignments, operations.
"""

# assignment = assign **value** and also **attributes** to a "name".
# an assignment binds a "name" to a "value";

# Naming conventions for this course:  
# * snake_case_for_variables_names
# * english_names
# * no_blank_spaces_in_names
# * DO NOT use of python RESERVED names for keywords, functions, modules.
# [keywords](https://docs.python.org/3.9/reference/lexical_analysis.html#keywords)
# [functions](https://docs.python.org/3.9/library/functions.html)

"""
Goal: After lecture 1, when you read a python file. you should understand what part of the code is a:
- comment
- docstring
- variable name
- value of a variable
- which words have been created by the programmer that wrote the script.
- which words are names of python functions.
"""

# After the 1st lecture you should be able to:
# => Understand, the message that this very romantic poem conveys:

"""
In python everything we create is an "object",  
We are not gods but, 
we can create as many objects without shame.
We give each object a "name",  
we "call" it by that "name",  
We "assign" a "value" to it,
and it gets "attributes" and "methods" too.   
So, when we "call" an "object" by its "name", e.g "foo",   
python "returns" its "value" to you.   
After this lecture, this poem should make sense to you! Yoohooo!  
"""

# If you don't get the poem after the lecture, then either:
# a) your tutor should write the poem on the board ten times using a chalk.
# b) you should read the lecture notes again.
# The choice is yours.


# CONTENTS:
# Lecture 1, Part C. Basic built-in types, assignments and operations.
# [Official basic built-in types tutorial](https://docs.python.org/3/library/stdtypes.html)  
# > Numeric types: Integer and float.  
# > Basic Numeric types operations.  
# > Strings and basic string operations.  


###-----------------------------------------------------------------
# ### Numeric types: Integer and float.
### [Built-in Numeric types docs](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)

# integer numbers
x = 3
print(x)  # We print it on the screen. Not to a printer.

type(x)  # this prints output only interactively

print(type(x))  # This is the standard way to print non-interactively.

x = 3
y = 4.1
z = x + y

z  # We "call" it. This has no effect when working non-interactively.

type(z)  # Without print, it will show nothing when the script is executed.

# Uncomment the lines below to see the result.
# print(z)
# print(type(z))

# floats are like decimal numbers but BE CAREFUL: precision differs!
a = 0.1 + 0.2
a  # We call it by its name.

print()  # this prints and empty line.
print('0.1 + 0.2 =', a, 'and is type float: ', type(a))


# ### Basic Numeric types "operations" and "operators".
# plus: +  
# minus: -  
# multiplication: *  
# division: /  (division returns float number, NOT integer)  
# Equal: ==   
# NOT equal: !=    
# Raise to power (Exponentiation):  **   
# Floor (integer) division: //    
# remainder of division: % modulo sign   

# Remember PEMDAS: [Operations precedence](https://docs.python.org/3/reference/expressions.html#operator-summary) 

10/2  # Division ALWAYS returns float type.

x != 10  # Will explain "Boolean" in following lecture. Not today.

x == 10  # Will explain "Boolean" in following lecture.  Not today.

integer_division = 10//3
integer_division

print(10 % 3, '\nThe modulo sign % returns the remainder.')  #\n denotes new line.

# A new function. More about it in the second part of the lecture.
# help(divmod)
divmod(10, 3)

# Two assignments because this function returns two values when we call it.
division_result, remainder = divmod(10,3)

division_result, remainder  # We "call" the "names" and get the "values".


###-----------------------------------------------------------------
# ### Strings ("Ordered Text Sequence") and basic string operations.
# [strings docs](https://docs.python.org/3.9/library/stdtypes.html#text-sequence-type-str)

#string is like representation of a text
text_type = "String types are ordered sequences of characters. Appear as text. Can contain numbers."

# the \ sign denotes line break in the code python. The code continues in the next line.
# the \n denotes a new line in a string.
# try it in the interpreter
# If you read and run the lecture files material you will find extra material.
print("\nThe difference between \ and \\n : The one slash character \
is used to break a long line of code, \
so that the code is more readable by the programmer.\n But: \
\n \\n means a new line in a text, \
so that:\n the printed output is more readable by the user.\n\n")  # This is one line of code.
# Notice when \ or \n are printed? They disappear if we use then and if we don't "escape" them.
# A extra \ is a special character that "escape" (cancels) the next special character.
# Black magic, don't worry about it for the moment.


print(text_type)
print(type(text_type))



example_name = "John"  # "John" is a value of a variable here.

type(example_name)

John = "student"  # John is a variable name, with assigned value = "student".

John = 4  # John is an object "name", with integer "value" = 4.

type(John)  # Variable with name John stores the latest value assigned to it.

example_name * 5  # Strings can be multiplied.

added_string = example_name + " " + "Pappas"  # Strings can be added.
print("Below is an added string:")
print(added_string)

print("\nBelow is the added string multiplied by 5:")
print((added_string + " ") * 5)
print()
# Uncomment the 2 lines below to try the errors.
# "john" ** "jack"
# "john" / "jack"

# Python FAQ: How can I find the methods or attributes of an object?
#https://docs.python.org/3/faq/programming.html#how-can-i-find-the-methods-or-attributes-of-an-object
dir(example_name)  # This will return the methods and attributes of the object.



# ### An extensive example, in class exercise.
## Learning goal: assignment, naming, values, order of assignment.
## Find the monthly wage of someone who:
## works 8 hours a day, for 20 days a month and gets 20€ per hour.

# To assign is to "name" and "assign" some "value".
# Python will also "auto-assign" attributes.
hour_wage = 20  # Assign value to a name
daily_hours_work = 8
days_work = 20

# Then an expression that uses other names (variables).
daily_income = hour_wage * daily_hours_work

monthly_income = daily_income * days_work  # Work 25 days

print('The monthly income is: ')
print(monthly_income)
# Not the best way to print. Can you tell why?
# Check the "bonus" file of the next lecture to learn about print formatting syntax.


## The script below does not work.
##  Can you tell why? Can you fix it?
## Copy the lines below IN A NEW PY FILE and fix it.

# hour_w = 10  # is this hours of work or hourly wage?
## Not descriptive names => bad practice! (But not the coding "error").

# work_days = 25

# daily_income = hour_w * daily_h

# daily_h = 8 # is this daily hours work or 

# monthly_income = daily_income * work_days  # Work 25 days

# print(f'Your monthly income is: {monthly_income}')  # f-string format. Check bonus file.
