# -*- coding: utf-8 -*-
"""Tools for converting I3 histograms to plotly Bar graphs."""

from typing import List

import plotly.graph_objs as go  # type: ignore


def n_histograms_to_plotly(histograms: List[dict], title: str = None, y_log: bool = False, alert_no_data: bool = False, no_title: bool = False) -> go.Figure:
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
    if not isinstance(histograms, list):
        raise TypeError("`histogram` argument needs to be a list of n histograms.")

    # Layout
    margin = None
    if not title:
        if no_title:
            title = None
            margin = {'t': 50}
        elif any(histograms):
            title = histograms[0]['name']

    yaxis = None
    if y_log:
        yaxis = {'type': 'log', 'autorange': True}
        if title:
            title = f"{title} (Log)"

    xaxis = None
    if not any(histograms) and alert_no_data:
        xaxis = {'title': '(no data)'}

    layout = go.Layout(title=title, yaxis=yaxis, xaxis=xaxis, margin=margin)

    # Data
    data = None
    if any(histograms):
        # Use the name of the collection if all the histograms have the same name
        use_collection_names = len(set(h['name'] for h in histograms)) == 1

        first = histograms[0]  # Use first histogram for common attributes

        # Data
        bin_width = (first['xmax'] - first['xmin']) / float(len(first['bin_values']))
        x_values = [first['xmin'] + i * bin_width for i in range(len(first['bin_values']))]
        text = f"nan({first['nan_count']}) under({first['underflow']}) over({first['overflow']})"

        data = []
        for histo in histograms:
            data.append(go.Bar(x=x_values,
                               y=histo['bin_values'],
                               text=text,
                               name=histo['name'] if not use_collection_names else histo['collection']))

    return go.Figure(data=data, layout=layout)


def histogram_to_plotly(histogram: dict, title: str = None, y_log: bool = False, alert_no_data: bool = False, no_title: bool = False) -> go.Figure:
    """Return a plotly Bar graph object with one histogram."""
    return n_histograms_to_plotly([histogram], title, y_log, alert_no_data, no_title)
