# From F.Porter "Testing Consistency of Two Histograms" arXiv : 0804.0380
def test_shape_chisq(h1, h2):
    r"""Compare histograms h1, h2 with a Chi^2 test after normalizing them.
    Assumes they have the same binning.
    Output:
        chisq : float
            A Chi^2 sum over all bins.
        p : float
            The p-value according to the Chi^2 distribution, nDOF = n(bins)-1.
            
    """
    # calculate the \chi^2 test statistic
    n1 = sum(h1['bin_values'])
    n2 = sum(h2['bin_values'])
    try:
        n1sq = n1**2
        n2sq = n2**2
        terms = [(u/n1 - v/n2)**2/(u/n1sq + v/n2sq) \
                 for u,v in zip(h1['bin_values'], h2['bin_values']) \
                 if u > 0 and v > 0 ]             
    except ZeroDivisionError:
        s = float(n1)/n2
        ssq = s**2
        terms = [(u/s - v)**2/(u/ssq + v) \
                 for u,v in zip(h1['bin_values'], h2['bin_values']) \
                 if u > 0 and v > 0 ]
    T = sum(terms)
    return T
    
    
