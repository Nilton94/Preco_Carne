import math
import re
from decimal import Decimal

__author__ = "Alexander Zaitsev (azaitsev@gmail.com)"

def remove_exponent(d):

    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


def millify(n, precision=0, drop_nulls=True, prefixes=[]):
    
    try:
        millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
        if prefixes:
            millnames = ['']
            millnames.extend(prefixes)
        n = float(n)
        millidx = max(
            0, 
            min(
                len(millnames) - 1,
                int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
            )
        )
        result = '{:.{precision}f}'.format(n / 10**(3 * millidx), precision=precision)
        if drop_nulls:
            result = remove_exponent(Decimal(result))
        return '{0}{dx}'.format(result, dx=millnames[millidx])
    except:
        return '0'