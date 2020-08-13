#!/usr/bin/env python
import logging
from multiprocessing import Pool, TimeoutError

import numpy
from scipy.stats import anderson_ksamp, chisquare
from scipy.stats.mstats import ks_twosamp


def both_empty(h1, h2):
    """Returns True if neither histogram has content."""
    def empty(h): return not any([True for v in h['bin_values'] if v > 0])
    return (empty(h1) and empty(h2))

def comparable(h1, h2):
    """Returns True if two histograms are comparable, meaning they have the
    same name and binning and more than 1 non-zero bin."""
    return ((h1['xmin'] == h2['xmin']) and
            (h1['xmax'] == h2['xmax']) and
            (h1['name'] == h2['name']) and
            (len(h1['bin_values']) == len(h2['bin_values'])))

def identical(h1, h2):
    print(h1['bin_values'])
    print(h2['bin_values'])
    return h1['bin_values'] == h2['bin_values']

def different_statistics(h1, h2):
    return

def statistical_preconditions(h1, h2):
    n_common_nonzero_bins = len([True for u, v in zip(h1['bin_values'], h2['bin_values'])
                                 if u > 0 and v > 0])
    return n_common_nonzero_bins > 10

def compare(h1, h2):
    """Compares two histograms applying statistical tests.  Both histograms
    need to be comparable, meaning they have to have the same number of bins,
    the same x-axis ranges, and the same name.  In production they will always
    have the same name, since it's also the dictionary key.

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
    """
    result = {}
    if both_empty(h1, h2):
        pvalue = 0. if not comparable(h1, h2) else 1.
        return {'both_empty': {'pvalue': pvalue}}

    if not comparable(h1, h2):
        return {'comparable': {'pvalue': 0.}}

    if identical(h1, h2):
        return {'identity': {'pvalue': 1.}}

    # we'll likely want to make a stricter requirement of having
    # at least N non-zero bins in common. N = 1 might be a bit too low.
    def n_nonzero_bins(h): return len([v for v in h['bin_values'] if v != 0])
    if n_nonzero_bins(h1) == 1 and \
       n_nonzero_bins(h2) == 1:
        # at this point if they're single bin then it's a fail because
        # we already know they're not identical
        return {'single_bin': {'pvalue': 0.}}

    if not statistical_preconditions(h1, h2):
        return {'insufficient_statistics': {'pvalue': 0.}}

    # Consider making these multi-threaded.
    # Not necessarily for performance reasons, but under certain
    # currently unknown conditions the KS test can lock up and
    # I'd like to be able to gracefully recover from that.

    pool = Pool(processes=3)

    n1 = sum(h1['bin_values'])
    n2 = sum(h2['bin_values'])
    bv1 = numpy.array(h1['bin_values'])
    bv2 = numpy.array(h2['bin_values'])
    if n1 != n2:
        # scale the larger histogram down
        N = min(n1, n2)
        if N > 0:
            bv1 = numpy.array(h1['bin_values'])/N
            bv2 = numpy.array(h2['bin_values'])/N
    try:
        res = pool.apply_async(chisquare, (bv1, bv2))
        chi2_result = res.get(timeout=1)
        print(chi2_result)
        result['chisq'] = {'T': chi2_result[0], 'pvalue': chi2_result[1]}
    except Exception as e:
        result['chisq'] = {'pvalue': 0, "Exception": str(e)}

    try:
        res = pool.apply_async(ks_twosamp, (bv1, bv2))
        ks_result = res.get(timeout=10)
        result['KS'] = {'T': ks_result[0], 'pvalue': ks_result[1]}
    except Exception as e:
        result['KS'] = {'pvalue': 0, "Exception": str(e)}

    try:
        res = pool.apply_async(anderson_ksamp, ([bv1, bv2]))
        ad_result = res.get(timeout=10)
        print("AD Critical Values = %s" % str(ad_result[1]))
        result['AD'] = {'T': ad_result[0], 'pvalue': ad_result[2]}
        sys.exit()
    except Exception as e:
        result['AD'] = {'pvalue': 0, "Exception": str(e)}

    pool.close()
    pool.join()

    return result
