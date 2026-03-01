"""
BIS UOA class
author: Argyriou Thanasis
Lecture 2, Part B: Strings and basic string operations.
Goal: Understand how strings work in Python — creation, concatenation,
multiplication, escape characters, reassignment, and dir().
"""

# Lecture 2, Part B: Strings and basic string operations.
# CONTENTS:
# > String type: ordered text sequence.
# > Escape characters: \ and \n.
# > String concatenation (+) and multiplication (*).
# > Reassignment: which value does a name keep?
# > dir() — finding methods and attributes of an object.


# Strings ("Ordered Text Sequence") and basic string operations.
# [strings docs](https://docs.python.org/3.9/library/stdtypes.html#text-sequence-type-str)

# A string is like representation of a text.
text_type = "String types are ordered sequences of characters. Appear as text. Can contain numbers."

# the \ sign denotes a "line break" in the code python. The code continues in the next line.
# the \n denotes a "new line" in a string.
# try it in the interpreter.

# If you read and run the lecture files you will find extra material.
print("\nThe difference between \ and \\n : The one slash character \
is used to break a long line of code, \
so that the code is more readable by the programmer.\n But: \
\n \\n means a new line in a text, \
so that:\n the printed output is more readable by the user.\n\n")  # This is one line of code.

# Can you notice when \ or \n are printed? They disappear if we use then and if we don't "escape" them.
# An extra \ is a special character that "escapes" (cancels) the next special character.
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

# Which value does a name keep?
# The latest assigned value. The previous value is lost.
# This is a common source of errors. 
# Be careful when you assign values to names.    


# Uncomment the 2 lines below to try the errors.
# "john" ** "jack"
# "john" / "jack"

# Python FAQ: How can I find the methods or attributes of an object?
# https://docs.python.org/3/faq/programming.html#how-can-i-find-the-methods-or-attributes-of-an-object
dir(example_name)  # This will return the methods and attributes of the object.

# Please try some functions for string data types:
# https://docs.python.org/3/library/stdtypes.html#string-methods

# When I say "Please", I mean that you definitely have to do it at home.
