import numpy as np


def sphere(x):
    """
    Hypersphere test function.

    f(x) = sum(x_i^2)

    Global minimum:
    f(x) = 0 for x = [0, 0, ..., 0]
    """
    return np.sum(np.square(x))