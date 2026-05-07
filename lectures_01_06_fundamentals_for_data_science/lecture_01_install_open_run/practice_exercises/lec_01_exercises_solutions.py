"""
Lecture 1 Exercises - Solutions
BIS UOA course
author: Argyriou Thanasis

Run this file to see outputs for the scripted parts.
Interpreter-only tasks are shown as comments.
"""

# ---------------------------
# A. Warm-up (Interpreter)
# ---------------------------
# 1) In interpreter:
# >>> print("Hello from Thanos!")

# 2) In interpreter:
# >>> help(print)
# Answer: "sep" defines the string inserted between items when printing.

# 3) In interpreter:
# >>> x = 7
# >>> print(x)

# 4) In interpreter:
# >>> a = 3
# >>> b = 5
# >>> print(a + b, a - b, a * b)


# ---------------------------
# B. Print practice (Script)
# ---------------------------
print("B1:", 1, 2, 3, sep=", ")
print("B2:", 1, 2, 3, sep=" | ")
print("B3:", "Hello", end=" ")
print("class!")
print()


# ---------------------------
# C. Names and errors
# ---------------------------
# 1) Validity of names:
# - 1item -> invalid (starts with a number)
# - item_1 -> valid
# - Item -> valid (case-sensitive)
# - total-cost -> invalid ("-" is not allowed in names)
# - total_cost -> valid

# 2) Case-sensitive names:
value = 10
Value = 20
print("C2:", value, Value)

# 3) NameError demo (commented to avoid stopping script)
# print(unknown_total)  # NameError
unknown_total = 42
print("C3:", unknown_total)
print()


# ---------------------------
# D. PEMDAS and readability
# ---------------------------
print("D1:", 20 / 5 / 4)
print("D1:", 20 / (5 / 4))

A = 4
a = 5
expr_readable = 2 * a + 4 * 3 + (A / 4) * 5
print("D2:", expr_readable)

expr_changed = 2 * (a + 4) * 3 + (A / 4) * 5
print("D3:", expr_changed)
print()


# ---------------------------
# E. Comments and docstrings
# ---------------------------
# This comment describes a calculation:
# We compute the area of a rectangle.
length = 6
width = 2
area = length * width
print("E:", area)
print()


# ---------------------------
# F. Mini-project (Café order)
# ---------------------------
coffee_price = 2.50
sandwich_price = 4.20
cookie_price = 1.10

coffee_qty = 2
sandwich_qty = 1
cookie_qty = 3

coffee_total = coffee_price * coffee_qty
sandwich_total = sandwich_price * sandwich_qty
cookie_total = cookie_price * cookie_qty

subtotal = coffee_total + sandwich_total + cookie_total
discount = 0.10
subtotal_after_discount = subtotal - (subtotal * discount)

print("F: Receipt")
print("coffee", coffee_qty, "x", coffee_price, "=", coffee_total)
print("sandwich", sandwich_qty, "x", sandwich_price, "=", sandwich_total)
print("cookie", cookie_qty, "x", cookie_price, "=", cookie_total)
print("subtotal:", subtotal)
print("discount:", discount)
print("total:", subtotal_after_discount)
print()


# ---------------------------
# G. Challenge
# ---------------------------
tax_rate = 0.24
final_total = subtotal_after_discount + (subtotal_after_discount * tax_rate)
print("G1:", final_total)

print("G2:", "coffee", coffee_qty, "x", coffee_price, "=", coffee_total)
print("G2:", "sandwich", sandwich_qty, "x", sandwich_price, "=", sandwich_total)
print("G2:", "cookie", cookie_qty, "x", cookie_price, "=", cookie_total)
print()


# ---------------------------
# H. Reflection (short answers)
# ---------------------------
print("H1: Interactive output shows expression results immediately; scripts need print().")
print("H2: Readability helps you and others understand and debug code faster.")
