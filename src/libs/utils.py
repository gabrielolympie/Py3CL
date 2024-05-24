import numpy as np


def safe_divide(a, b):
    return a / b if b != 0 else 0


@np.vectorize
def vectorized_safe_divide(a, b):
    return safe_divide(a, b)
