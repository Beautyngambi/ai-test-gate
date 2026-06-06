"""The SAME calculator API, but with one deliberate, subtle bug.

This is the "bad" sample file. Running the gate against it should produce at
least one FAILING test, so the gate recommends REJECT. That is the headline
demo: the tool catches a real defect in AI-style code before a human approves it.
"""


def add(a, b):
    """Return the sum of two numbers."""
    return a + b


def divide(a, b):
    """Divide a by b. Raise ValueError if b is zero (can't divide by zero)."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def is_prime(n):
    """Return True if n is a prime number, otherwise False."""
    # BUG: the correct check is `n < 2`. Using `n < 1` here wrongly reports
    # that 1 is prime (is_prime(1) returns True), which is mathematically wrong.
    if n < 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def factorial(n):
    """Return n! (n factorial). Raise ValueError for negative input."""
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
