from math import log

from scipy.special import binom

# Test from F.Porter "Testing Consistency of Two Histograms" arXiv : 0804.0380# 

def test_cramer_von_mises(h1, h2):
    r"""
    Compare histograms h1, h2 with the Cramer-von-Mises test.
    """
    result = 0.
    Nu = float(sum(h1['bin_values']))
    Nv = float(sum(h2['bin_values']))
    if Nu == 0 and Nv == 0:
        return 0.

    for i,uv in enumerate(zip(h1['bin_values'], h2['bin_values'])):
        u = float(uv[0])
        v = float(uv[1])        
        t = u + v
        u_ecdf = sum([bn for bn in h1['bin_values'][:i]])/sum(h1['bin_values'])
        v_ecdf = sum([bn for bn in h2['bin_values'][:i]])/sum(h2['bin_values'])        
        result += t*(u_ecdf - v_ecdf)**2
    factor = Nu*Nv/(Nu+Nv)**2
    T = factor * result
    return T
