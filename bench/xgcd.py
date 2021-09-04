# A standard xgcd implementation for Python copied from a random webpage.
# This of course quickly overflows with Javascript "integers" = doubles'
def xgcd(a, b):
    prevx, x = 1, 0
    prevy, y = 0, 1
    while b:
        q, r = divmod(a, b)
        x, prevx = prevx - q * x, x
        y, prevy = prevy - q * y, y
        a, b = b, r
    return a, prevx, prevy

def bench_xgcd():
    from time import time
    t = time()
    s = 0
    for i in range(10**6):
        s += xgcd(92250, 922350+i)[0]
    print(s, time()-t)

bench_xgcd()