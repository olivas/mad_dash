from math import log
# Test from F.Porter "Testing Consistency of Two Histograms" arXiv : 0804.0380# 

def test_anderson_darling(h1, h2):
    r"""
    Compare histograms h1, h2 with the Anderson-Darling test.
    """
    result = 0.
    Nu = float(sum(h1['bin_values']))
    Nv = float(sum(h2['bin_values']))

    if Nu == 0 or Nv == 0:
        return 0.
    
    factor = 1./(Nu+Nv)
    sigma_j = 0.
    sigma_uj = 0.
    sigma_vj = 0.
    for i,uv in enumerate(zip(h1['bin_values'], h2['bin_values'])):
        u = float(uv[0])
        v = float(uv[1])
        if u == 0 and v == 0:
            continue
        t = u + v

        sigma_uj += u
        sigma_vj += v
        sigma_j += t

        term1 = (1./Nu)*((Nu+Nv)*sigma_uj - Nu*sigma_j)**2
        term2 = (1./Nv)*((Nu+Nv)*sigma_vj - Nv*sigma_j)**2

        denom = sigma_j *(Nu + Nv - sigma_j)
        if denom == 0 :
            continue
        result += t*(term1 + term2)/denom

    T = factor * result
    return T
