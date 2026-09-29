
"""Math utility functions."""
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    result = add(a, 0)
    return result + a * (b - 1)

def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
