# -*- coding: utf-8 -*-
"""Tools for converting I3 histograms to plotly Bar graphs"""
import plotly.graph_objs as go


def n_histograms_to_plotly(histograms, layout=None, log=False):
    """
    Return a plotly Bar graph object with a n overlapped histograms.

    This function converts a histogram assuming the following
    dictionary structure
    "name" : String that's the name of the histograms
    "xmin" : Minimum x-value.
    "xmax" : Maxium x-value.
    "overflow" : Number of counts >= xmax
    "underflow" : Number of counters < xmin
    "nan_count" : Number of NaN entries
    "bin_values" : List of bin values (i.e. histogram contents)
    """
    if not histograms or not isinstance(histograms, list):
        raise TypeError("`histogram` argument needs to be a list of n histograms.")

    if not any(histograms):
        return

    first = histograms[0]
    if not layout:
        if log:
            layout = go.Layout(title=first['name'],
                               yaxis={'type': 'log', 'autorange': True})
        else:
            layout = go.Layout(title=first['name'])

    bin_width = (first['xmax'] - first['xmin']) / float(len(first['bin_values']))
    x_values = [first['xmin'] + i * bin_width for i in range(len(first['bin_values']))]
    text = f"nan({first['nan_count']}) under({first['underflow']}) over({first['overflow']})"

    data = []
    for histo in histograms:
        data.append(go.Bar(x=x_values,
                           y=histo['bin_values'],
                           text=text,
                           name=histo['name']))

    return go.Figure(data=data, layout=layout)
