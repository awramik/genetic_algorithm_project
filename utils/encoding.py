import numpy as np


"""
x = L + [ decimal / [2^n−1] ] * [U - L]
"""

def binary_to_decimal(binary):
    """
    Convert binary list to decimal number.
    """
    return int("".join(map(str, binary)), 2)


def decimal_to_real(decimal, lower_bound, upper_bound, bits):
    """
    Convert decimal value to real number in given range.
    """
    max_decimal = 2 ** bits - 1

    real = lower_bound + (decimal / max_decimal) * (upper_bound - lower_bound)

    return real


def binary_to_real(binary, lower_bound, upper_bound):
    """
    Convert binary chromosome to real value.
    """
    bits = len(binary)

    decimal = binary_to_decimal(binary)

    return decimal_to_real(decimal, lower_bound, upper_bound, bits)