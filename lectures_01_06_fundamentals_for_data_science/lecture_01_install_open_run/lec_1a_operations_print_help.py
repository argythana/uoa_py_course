"""
BIS UOA course
author: Argyriou Thanasis
Lecture 1, part A, Examples: operations, print, help.
"""

print("Use help() function to learn how another function works.")
help(print)  # print help about print

x = 4
y = 6
addition = x + y
substraction = x - y
multiplication = x * y

print("Examples of the print() function and its parameters.\n")  #\n denotes a new line.
print(addition)
print()
print(substraction)
print()
print(addition, substraction, multiplication)
print()
print(addition, substraction, multiplication, sep=", ")
print()
print(addition, substraction, multiplication, sep=", ", end=" this is a custom print end.\n")
print()
