"""A few small, clearly-correct functions for the test gate to verify.

This is the "good" sample file. The generated tests should all PASS and
coverage should be high, so the gate recommends APPROVE.
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
    """Return True if n is a prime number, otherwise False.

    A prime is a whole number greater than 1 with no divisors other than
    1 and itself. So 0, 1, and all negatives are NOT prime.
    """
    if n < 2:              # 0, 1 and negatives are not prime
        return False
    # Check every possible divisor from 2 up to the square root of n.
    # If any divides n evenly, n is not prime.
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def factorial(n):
    """Return n! (n factorial). Raise ValueError for negative input."""
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    result = 1
    # Multiply 1 * 2 * 3 * ... * n. (factorial of 0 is 1, so the loop is skipped.)
    for i in range(2, n + 1):
        result *= i
    return result
