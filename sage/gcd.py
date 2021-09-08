def gcd(a, b):
    """
    >>> gcd(3,6)
    3
    >>> gcd(10,15)
    5
    """
    if a == 0: return abs(b)
    if b == 0: return abs(a)
    if a < 0: a = -a
    if b < 0: b = -b
    while b:
        c = a % b
        a = b
        b = c
    return a

if __name__ == "__main__":
    print("gcd(18,15) = ", gcd(18,15))