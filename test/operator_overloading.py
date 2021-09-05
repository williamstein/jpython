def xgcd(a, b):
    prevx, x = 1, 0
    prevy, y = 0, 1
    while b:
        q, r = divmod(a, b)
        x, prevx = prevx - q * x, x
        y, prevy = prevy - q * y, y
        a, b = b, r
    return a, prevx, prevy

def inverse_mod(a, N):
    """
    Compute multiplicative inverse of a modulo N.
    """
    if a == 1 or N <= 1:  # common special cases
        return a % N
    [g, s, _] = xgcd(a, N)
    if g != 1:
        raise ZeroDivisionError
    b = s % N
    if b < 0:
        b += N
    return b

class Mod:
    def __init__(self, x, n):
        self.x = x % n
        self.n = n

    def __pow__(self, right, n): # not implemented yet
        """Dumb algorithm, of course."""
        if n == 0:
            return Mod(1, self.n)
        ans = Mod(self.x, self.n)
        for i in range(n-1):
            ans *= self
        return ans

    def __add__(self, right):
        return Mod(self.x + right.x, self.n)

    def __mul__(self, right):
        return Mod(self.x * right.x, self.n)

    def __sub__(self, right):
        return Mod(self.x - right.x, self.n)

    def __truediv__(self, right):
        return Mod(self.x * inverse_mod(right.x, self.n), self.n)

    def __floordiv__(self, right):
        """Silly arbitrary meaning of this for TESTING."""
        return Mod(self.x // right.x, self.n)

    def __repr__(self):
        print(f"Mod({self.x}, {self.n})")

    def __str__(self):
        print(f"Mod({self.x}, {self.n})")

def test1():
    a = Mod(3, 10)
    b = Mod(5, 10)
    c = a*b
    assert(c.x == 5)
    assert((a * (b / a)).x == b.x)
    assert((b//a).x == 1)


if __name__ == "__main__":
    test1()