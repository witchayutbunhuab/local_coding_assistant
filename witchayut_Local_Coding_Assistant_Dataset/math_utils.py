"""Mathematical utility functions for statistical calculations."""
from typing import List

def mean(numbers: List[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers."""
    if not numbers:
        return 0.0
    total_sum = sum(numbers)
    average = total_sum / len(numbers)
    return average

def factorial(n: int) -> int:
    """Calculate the factorial of a non-negative integer recursively."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

def median(numbers: List[float]) -> float:
    """Calculate the median value of a list of numbers."""
    if not numbers:
        return 0.0
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2.0
    return sorted_nums[mid]

def variance(numbers: List[float]) -> float:
    """Calculate variance using mean."""
    if len(numbers) <= 1:
        return 0.0
    avg = mean(numbers)
    return sum((x - avg) ** 2 for x in numbers) / (len(numbers) - 1)