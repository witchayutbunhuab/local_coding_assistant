
"""Statistical analysis functions."""
from typing import List
import math

def mean(numbers: List[float]) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

def variance(numbers: List[float]) -> float:
    m = mean(numbers)
    return sum((x - m) ** 2 for x in numbers) / len(numbers)

def std_dev(numbers: List[float]) -> float:
    return math.sqrt(variance(numbers))
