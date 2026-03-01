"""
BIS UOA course
author: Argyriou Thanasis
Lecture 1, part A, Examples: operations, print, help.

Story example: a small campus café order.
Learn:
1) print() output and parameters.
2) Assignments: name = value.
3) Basic operations.
"""

# print("Use help() to learn how another function works.")
# help(print)  # print help about print
print()

print("--- Campus café order ---")

# Assignments: name = value
coffee_price = 2.50
sandwich_price = 4.20
cookie_price = 1.10

coffee_qty = 2
sandwich_qty = 1
cookie_qty = 3

# Basic operations
coffee_total = coffee_price * coffee_qty
sandwich_total = sandwich_price * sandwich_qty
cookie_total = cookie_price * cookie_qty

subtotal = coffee_total + sandwich_total + cookie_total
discount = 0.10  # 10% discount
total = subtotal - (subtotal * discount)

print("Items:")
print("coffee", coffee_qty, "x", coffee_price, "=")
print(coffee_total)
print("sandwich", sandwich_qty, "x", sandwich_price, "=")
print(sandwich_total)
print("cookie", cookie_qty, "x", cookie_price, "=")
print(cookie_total)
print()
