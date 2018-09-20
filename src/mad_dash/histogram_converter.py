# -*- coding: utf-8 -*-

import plotly.graph_objs as go

def to_plotly(histogram, layout = None):
    '''
    This function converts a histogram assuming the following
    dictionary structure
    "name" : String that's the name of the histograms
    "xmin" : Minimum x-value.
    "xmax" : Maxium x-value.
    "overflow" : Number of counts >= xmax
    "underflow" : Number of counters < xmin
    "nan_count" : Number of NaN entries
    "bin_values" : List of bin values (i.e. histogram contents)

    This function returns a plotly Bar graph object.
    '''
    bin_width = (histogram['xmax'] - histogram['xmin'])/float(len(histogram['bin_values']))
    x_values = [histogram['xmin'] + i*bin_width for i in range(len(histogram['bin_values']))]
    text = "nan(%d) under(%d) over(%d)" % \
           (histogram['nan_count'],histogram['underflow'],histogram['overflow'])

    if not layout:
        layout = go.Layout(title = histogram['name'])
    
    return go.Figure(data = [go.Bar( x = x_values,
                                     y = histogram['bin_values'],
                                     text = text,
                                     name = histogram['name'])],
                     layout = layout
    )

