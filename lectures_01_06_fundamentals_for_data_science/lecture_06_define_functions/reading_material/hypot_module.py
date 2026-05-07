"""
hypot_module.py — A simple user-defined module for calculating the hypotenuse.

This module is used in lectures 06c and 06d to demonstrate:
- how to create a user-defined module,
- how to import it in a notebook or another script,
- how `if __name__ == "__main__"` works.
"""

from math import sqrt


def calculate_hypot(side_a, side_b):
    """
    Calculate the hypotenuse of a right triangle.
    Params:
        side_a: length of side a (number).
        side_b: length of side b (number).
    Returns:
        hyp: length of the hypotenuse (float).
    """
    hyp = sqrt(side_a * side_a + side_b * side_b)
    return hyp


def hypot_calculator_modular():
    """
    Ask user for triangle sides and print the hypotenuse.
    Input should be numbers.
    """
    a = float(input("Insert a number for side a: "))
    b = float(input("Insert a number for side b: "))
    hypotenuse = calculate_hypot(a, b)
    print("Hypotenuse =", hypotenuse)


# This block runs ONLY when the file is executed directly as a script.
# It does NOT run when the file is imported as a module.
if __name__ == "__main__":
    print("Running hypot_module.py as a stand-alone script.")
    print("Example: hypotenuse of sides 3 and 4 is", calculate_hypot(3, 4))
    # Uncomment the line below to interactively ask for user input when running as a script.
    # hypot_calculator_modular()
