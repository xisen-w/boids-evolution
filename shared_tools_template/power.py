"""Drastically simplified power tool."""

from typing import Union
import importlib


def execute(base: Union[int, float], exponent: int) -> float:
    """Compute ``base`` raised to ``exponent`` using the simple multiply tool."""

    if not isinstance(exponent, int):
        raise TypeError("exponent must be an integer")
    if exponent < 0:
        raise ValueError("negative exponents are not supported")

    if exponent == 0:
        return 1.0

    multiply = importlib.import_module('multiply')

    result = float(base)
    for _ in range(exponent - 1):
        result = multiply.execute(result, base)
    return result
