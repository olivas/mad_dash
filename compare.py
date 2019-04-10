#!/usr/bin/env python
import logging

from scipy.stats import chisquare
from scipy.stats import anderson_ksamp
from scipy.stats.mstats import ks_twosamp

from multiprocessing import Pool, TimeoutError

def both_empty(h1, h2):
    '''
    Returns True if neither histogram has content.
    '''
    empty = lambda h : not any([True for v in h['bin_values'] if v > 0])
    return (empty(h1) and empty(h2))

def comparable(h1, h2):
    '''
    Returns True if two histograms are comparable,
    meaning they have the same name and binning and more
    than 1 non-zero bin.
    '''
    return ((h1['xmin'] == h2['xmin']) and\
            (h1['xmax'] == h2['xmax']) and\
            (h1['name'] == h2['name']) and\
            (len(h1['bin_values']) == len(h2['bin_values'])))

def identical(h1, h2):
    return h1['bin_values'] == h2['bin_values']

def different_statistics(h1, h2):
    return 
    
def statistical_preconditions(h1, h2):
    n_common_nonzero_bins = len([True for u,v in zip(h1['bin_values'], h2['bin_values'])
                                 if u > 0 and v > 0])
    return n_common_nonzero_bins > 10

def compare(h1, h2):
    '''
    Compares two histograms applying statistical tests.  Both histograms
    need to be comparable, meaning they have to have the same number of
    bins, the same x-axis ranges, and the same name.  In production they
    will always have the same name, since it's also the dictionary key.

    If either histogram one has only 0 or 1 non-empty bins
    then they're also not comparable.  This causes scipy statistical
    tests to lockup and this is not the tool you want to use in those cases.

    If the histograms are not comparable an empty dictionary is returned.

    If both histograms are comparable a dictionary is returned with the
    results of the statistical comparisons.

    {
      'both_empty': {'pvalue': pvalue},
      'comparable': {'pvalue': pvalue},
      'identity': {'pvalue': pvalue},
      'single_bin': {'pvalue': pvalue},
      'insufficient_statistics': {'pvalue': pvalue},
      'chisq': {'T': T, 'pvalue': pvalue},
      'KS': {'T': T, 'pvalue': pvalue}
    }
    '''
    result = {}
    if both_empty(h1, h2):
        pvalue = 0. if not comparable(h1, h2) else 1.
        return {'both_empty': {'pvalue': pvalue} }

    if not comparable(h1, h2):
        return {'comparable': {'pvalue': 0.} }

    if identical(h1, h2):
        return {'identity': {'pvalue': 1.} }

    # we'll likely want to make a stricter requirement of having
    # at least N non-zero bins in common. N = 1 might be a bit too low.
    n_nonzero_bins = lambda h : len([v for v in h['bin_values'] if v != 0])
    if n_nonzero_bins(h1) == 1 and \
       n_nonzero_bins(h2) == 1:
        # at this point if they're single bin then it's a fail because
        # we already know they're not identical
        return {'single_bin': {'pvalue': 0.} }

    if not statistical_preconditions(h1, h2):
        return {'insufficient_statistics': {'pvalue': 0.} }

    # Consider making these multi-threaded.
    # Not necessarily for performance reasons, but under certain
    # currently unknown conditions the KS test can lock up and
    # I'd like to be able to gracefully recover from that.

    pool = Pool(processes=3)
    
    try:
        res = pool.apply_async(chisquare, (h1['bin_values'], h2['bin_values']))
        chi2_result = res.get(timeout=1)
        result['chisq'] = {'T': chi2_result[0], 'pvalue': chi2_result[1]}
    except Exception as e:
        result['chisq'] = {'pvalue': 0, "Exception": str(e)}

    try:
        res = pool.apply_async(ks_twosamp, (h1['bin_values'], h2['bin_values']))
        ks_result = res.get(timeout=10)
        result['KS'] = {'T': ks_result[0], 'pvalue': ks_result[1]}
    except Exception as e:
        result['KS'] = {'pvalue': 0, "Exception": str(e)}

    try:
        res = pool.apply_async(anderson_ksamp, (h1['bin_values'], h2['bin_values']))
        ad_result = res.get(timeout=10)
        result['AD'] = {'T': ad_result[0], 'pvalue': ad_result[2]}
    except Exception as e:
        result['AD'] = {'pvalue': 0, "Exception": str(e)}

    pool.close()
    pool.join()
        
    return result
