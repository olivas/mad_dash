
# Test are from F.Porter "Testing Consistency of Two Histograms" arXiv : 0804.0380
def test_norm_chisq(h1, h2):
    r"""Compare histograms h1, h2 with a Chi^2 test.
    Assumes they have the same binning.
    Output:
        chisq : float
            A Chi^2 sum over all bins.
        p : float
            The p-value according to the Chi^2 distribution, nDOF = n(bins).
            
    """
    # calculate the \chi^2 test statistic
    terms = [(u - v)**2/(u + v) \
             for u,v in zip(h1['bin_values'], h2['bin_values'])\
             if u > 0 and v > 0]
    T = sum(terms)
    return T
