# -*- coding: utf-8 -*-
"""Tools for converting I3 histograms to plotly Bar graphs."""

from typing import List

import plotly.graph_objs as go  # type: ignore


def n_histograms_to_plotly(histograms: List[dict], title: str = None, log: bool = False) -> go.Figure:
    """Return a plotly Bar graph object with a n overlapped histograms.

    This function converts a histogram assuming the following
    dictionary structure
    "name" : String that's the name of the histograms
    "xmin" : Minimum x-value.
    "xmax" : Maximum x-value.
    "overflow" : Number of counts >= xmax
    "underflow" : Number of counters < xmin
    "nan_count" : Number of NaN entries
    "bin_values" : List of bin values (i.e. histogram contents)
    """
    if not histograms or not isinstance(histograms, list):
        raise TypeError("`histogram` argument needs to be a list of n histograms.")

    if not any(histograms):
        return go.Figure()

    first = histograms[0]
    if not title:
        title = first['name']

    if log:
        layout = go.Layout(title=f"{title} (Log)", yaxis={'type': 'log', 'autorange': True})
    else:
        layout = go.Layout(title=title)

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


def histogram_to_plotly(histogram: dict, title: str = None, log: bool = False) -> go.Figure:
    """Return a plotly Bar graph object with one histogram."""
    return n_histograms_to_plotly([histogram], title, log)
