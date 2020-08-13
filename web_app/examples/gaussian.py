#!/usr/bin/env python

import random
import sys
from statistics.compare import compare

import numpy

sys.path.insert(0, '/home/olivas/mad_dash')



mu = 0.
sigma = 1.
N = 100000

h_range = (-5, 5)
nbins = 20

poisson_benchmark = {
    'bin_values' : list(numpy.histogram([random.gauss(mu, sigma) for _ in range(N)], range=h_range, bins=nbins)[0]),
    'xmin' : h_range[0],
    'xmax' : h_range[1],
    'name' : 'poisson'
}

poisson_test = {
    'bin_values' : list(numpy.histogram([random.gauss(mu, sigma) for _ in range(int(N))], range=h_range, bins=nbins)[0]),
    'xmin' : h_range[0],
    'xmax' : h_range[1],
    'name' : 'poisson'
}

print(compare(poisson_benchmark, poisson_test))

# Thanks for nothin' scipy
# SciPy is going to be useless for this.  We'll have to roll our own.
#  /home/olivas/mad_dash/mdenv/lib/python3.6/site-packages/scipy/stats/stats.py:4653: RuntimeWarning: divide by zero encountered in true_divide
#    terms = (f_obs - f_exp)**2 / f_exp
#  /home/olivas/mad_dash/mdenv/lib/python3.6/site-packages/scipy/stats/stats.py:4653: RuntimeWarning: invalid value encountered in true_divide
#    terms = (f_obs - f_exp)**2 / f_exp
#  Power_divergenceResult(statistic=nan, pvalue=nan)
#  {'chisq': {'T': nan, 'pvalue': nan}, 'KS': {'T': 0.1, 'pvalue': 0.9999652306540077}, 'AD': {'pvalue': 0, 'Exception': 'The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()'}}
