from math import sqrt

def trial_division(N, bound=0, start=2):
    if N <= 1:
        return N
    m = 7
    i = 1
    dif = [6, 4, 2, 4, 2, 4, 6, 2]

    if start > 7:
        # We need to find i.
        m = start % 30
        if m <= 1:
            i = 0
            m = start + (1 - m)
        elif m <= 7:
            i = 1
            m = start + (7 - m)
        elif m <= 11:
            i = 2
            m = start + (11 - m)
        elif m <= 13:
            i = 3
            m = start + (13 - m)
        elif m <= 17:
            i = 4
            m = start + (17 - m)
        elif m <= 19:
            i = 5
            m = start + (19 - m)
        elif m <= 23:
            i = 6
            m = start + (23 - m)
        elif m <= 29:
            i = 7
            m = start + (29 - m)

    if start <= 2 and N % 2 == 0:
        return 2
    if start <= 3 and N % 3 == 0:
        return 3
    if start <= 5 and N % 5 == 0:
        return 5

    limit = round(sqrt(N))
    if bound != 0 and bound < limit:
        limit = bound

    # Algorithm: only trial divide by numbers that
    # are congruent to 1,7,11,13,17,19,23,29 mod 30=2*3*5.
    while m <= limit:
        if N % m == 0:
            return m
        m += dif[i % 8]
        i += 1

    return N


def is_prime(N):
    return N > 1 and trial_division(N) == N

# Prime counting using trial division.
# This is a silly algorithm and obviously
# is mainly for testing!
def pi(x, isPrime=is_prime):
    s = 0
    for i in range(1, x+1):
        if isPrime(i):
            s += 1
    return s

def bench_pi(x, isPrime=is_prime):
    from time import time
    t = time()
    print(pi(x, isPrime),time()-t)

def wasm():
    return require('./wasm')

print(wasm())

try:
    exports.bench_pi = bench_pi
    exports.wasm = wasm
except:
    pass