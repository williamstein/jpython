###########################################################
# RapydScript Standard Library
# Author: Alexander Tsepkov
# Copyright 2013 Pyjeon Software LLC
# License: Apache License    2.0
# This library is covered under Apache license, so that
# you can distribute it with your RapydScript applications.
###########################################################

# basic implementation of Python's 'math' library

# NOTE: this is only meant to aid those porting lots of Python code into RapydScript,
# if you're writing a new RapydScript application, in most cases you probably want to
# use JavaScript's Math module directly instead

pi = Math.PI
e = Math.E


########################################
# Number-theoretic and representation functions
########################################
def ceil(x):
    return Math.ceil(x)


def copysign(x, y):
    x = Math.abs(x)
    if y < 0:
        return -x
    else:
        return x


def fabs(x):
    return Math.abs(x)


def factorial(x):
    if Math.abs(int(x)) is not x:
        raise ValueError("factorial() only accepts integral values")
    factorial.cache = []

    def r(n):
        if n is 0 or n is 1:
            return 1
        if not factorial.cache[n]:
            factorial.cache[n] = r(n - 1) * n
        return factorial.cache[n]

    return r(x)


def floor(x):
    return Math.floor(x)


def fmod(x, y):
    # javascript's % operator isn't consistent with C fmod implementation, this function is
    while y <= x:
        x -= y
    return x


def fsum(iterable):
    # like Python's fsum, this method is much more resilient to rounding errors than regular sum
    partials = []  # sorted, non-overlapping partial sums
    for x in iterable:
        i = 0
        for y in partials:
            if Math.abs(x) < Math.abs(y):
                x, y = y, x
            hi = x + y
            lo = y - (hi - x)
            if lo:
                partials[i] = lo
                i += 1
            x = hi
        #partials[i:] = [x]
        partials.splice(i, partials.length - i, x)
    return sum(partials)


def isinf(x):
    return not isFinite(x)


def isnan(x):
    return isNaN(x)


def modf(x):
    m = fmod(x, 1)
    return m, x - m


def trunc(x):
    return x | 0


########################################
# Power and logarithmic functions
########################################
def exp(x):
    return Math.exp(x)


def expm1(x):
    # NOTE: Math.expm1() is currently only implemented in Firefox, this provides alternative implementation
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/expm1
    #return Math.expm1(x)
    if Math.abs(x) < 1e-5:
        return x + 0.5 * x * x
    else:
        return Math.exp(x) - 1


def log(x, base=e):
    return Math.log(x) / Math.log(base)


def log1p(x):
    # NOTE: Math.log1p() is currently only implemented in Firefox, this provides alternative implementation
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log1p
    # this version has been taken from http://phpjs.org/functions/log1p/
    # admittedly it's not as accurate as MDN version, as you can see from math.log1p(1) result
    ret = 0
    n = 50
    if x <= -1:
        return Number.NEGATIVE_INFINITY
    if x < 0 or x > 1:
        return Math.log(1 + x)
    for i in range(1, n):
        if i % 2 is 0:
            ret -= Math.pow(x, i) / i
        else:
            ret += Math.pow(x, i) / i
    return ret


def log10(x):
    # NOTE: Math.log10() is currently only implemented in Firefox, this provides alternative implementation
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log10
    # I didn't find a more accurate algorithm so I'm using the basic implementation
    return Math.log(x) / Math.LN10


def pow(x, y):
    if x < 0 and int(y) is not y:
        raise ValueError('math domain error')
    if isnan(y) and x is 1:
        return 1
    return Math.pow(x, y)


def sqrt(x):
    return Math.sqrt(x)


########################################
# Trigonometric functions
########################################
def acos(x):
    return Math.acos(x)


def asin(x):
    return Math.asin(x)


def atan(x):
    return Math.atan(x)


def atan2(y, x):
    return Math.atan2(y, x)


def cos(x):
    return Math.cos(x)


def sin(x):
    return Math.sin(x)


def hypot(x, y):
    return Math.sqrt(x * x + y * y)


def tan(x):
    return Math.tan(x)


########################################
# Angular conversion
########################################
def degrees(x):
    return x * 180 / pi


def radians(x):
    return x * pi / 180


########################################
# Hyperbolic functions
########################################
def acosh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/acosh
    return Math.log(x + Math.sqrt(x * x - 1))


def asinh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/asinh
    return Math.log(x + Math.sqrt(x * x + 1))


def atanh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/atanh
    return 0.5 * Math.log((1 + x) / (1 - x))


def cosh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/cosh
    return (Math.exp(x) + Math.exp(-x)) / 2


def sinh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sinh
    return (Math.exp(x) - Math.exp(-x)) / 2


def tanh(x):
    # NOTE: will be replaced with official, when it becomes mainstream
    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/tanh
    return (Math.exp(x) - Math.exp(-x)) / (Math.exp(x) + Math.exp(-x))


#import stdlib
#print(math.ceil(4.2))
#print(math.floor(4.2))
#print(math.fabs(-6))
#print(math.copysign(-5, 7))
#print(math.factorial(4))
#print(math.fmod(-1e100, 1e100))
#
#d = [0.9999999, 1, 2, 3]
#print(sum(d), math.fsum(d))
#print(math.isinf(5), math.isinf(Infinity))
#print(math.modf(5.5))
#print(math.trunc(2.6), math.trunc(-2.6))
#print(math.exp(1e-5), math.expm1(1e-5))
#print(math.log(10), math.log(10, 1000))
#print(math.log1p(1e-15), math.log1p(1))
#print(math.log10(1000), math.log(1000, 10))
#print(math.pow(1, 0), math.pow(1, NaN), math.pow(0, 0), math.pow(NaN, 0), math.pow(4,3), math.pow(100, -2))
#print(math.hypot(3,4))
#print(math.acosh(2), math.asinh(1), math.atanh(0.5), math.cosh(1), math.cosh(-1), math.sinh(1), math.tanh(1))
