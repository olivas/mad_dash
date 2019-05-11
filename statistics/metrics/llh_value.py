from math import log
from numpy import isinf
from scipy.special import binom
# Test from F.Porter "Testing Consistency of Two Histograms" arXiv : 0804.0380# 

def test_llh_value(h1, h2):
    r"""
    Compare histograms h1, h2 with the log likelihood value test.
    FIXME: This is currently returning inf on occasion.  It should
           never do that. Taking it out of the rotation.
    """
    result = 0.
    Nu = float(sum(h1['bin_values']))
    Nv = float(sum(h2['bin_values']))
    if Nu == 0 and Nv == 0:
        return 0.
    
    for u,v in zip(h1['bin_values'], h2['bin_values']):
        u = float(u)
        v = float(v)        
        t = u + v
        bn = binom(t,v)
        if isinf(bn):
            print("binom(%f, %f) = %f" % (t,v,bn))
        term1 = log(bn)
        if isinf(term1):
            print("log(%f) = %f" % (term1, log(bn)))
        term2 = t*log(Nu/(Nu + Nv))
        if isinf(term2):
            print("term2 = %f" % term2)
        term3 = v*log(Nv/Nu)
        if isinf(term3):
            print("term3 = %f" % term3)
        result += term1 + term2 + term3
    T = -result
    return T
