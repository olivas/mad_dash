from math import fabs
    
# The following tests are from F.Porter
# "Testing Consistency of Two Histograms" arXiv : 0804.0380
def test_kolmogorov_smirnof(h1, h2):
    r"""Perform the Kolmogorov-Smirnof test for the histograms h1, h2
    which are assumed to have the same binning. The binning needs to be small
    compared to important features of the histograms.
    Output:
        T : float
            Maximum distance between the cumulative distributions.            
    """
    assert(len(h1['bin_values']) == len(h2['bin_values']))
    nbins = len(h1['bin_values'])
    s1 = sum(h1['bin_values'])
    s2 = sum(h2['bin_values'])
    if s1 == 0 and s2 == 0:
        return 0.

    cdf_diffs = [fabs(sum(h1['bin_values'][:i])/s1 - sum(h2['bin_values'][:i])/s2)
                 for i in range(nbins)]
    T = max(cdf_diffs)    
    return T
        
    
