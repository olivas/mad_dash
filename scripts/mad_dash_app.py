#!/usr/bin/env python3

import sys, os
from os.path import join
sys.path.insert(0,join(os.environ['HOME'], 'mad_dash/src'))

import dash
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from mad_dash.serve_layout import serve_layout
from mad_dash.simprod_db import spdb
from mad_dash.histogram_converter import to_plotly

app = dash.Dash('Mad Dash')
app.layout = serve_layout()
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('coll_dropdown', 'options'),
    [Input('db_dropdown', 'value')])
def update_collection_dropdown(value):
    db = spdb[value]    
    collection_names = [n for n in db.collection_names()
                        if n not in ['system.indexes']]
    return [{'label': i, 'value': i} for i in collection_names]

@app.callback(
    Output('hist_dropdown', 'options'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])
def update_histogram_dropdown(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram_names = [doc['name'] for doc in coll.find()]
    print(histogram_names)
    return [{'label': i, 'value': i} for i in histogram_names]

@app.callback(
    Output('histogram-text', 'children'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_histogram_dropdown(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram_names = [doc['name'] for doc in coll.find()]
    return 'There are %d histograms in this collection' % len(histogram_names)

@app.callback(
    Output('plot_linear_histogram', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value'),
     Input('hist_dropdown', 'value')])
def update_histogram_dropdown(db_name, collection_name, histogram_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': histogram_name})
    return to_plotly(histogram)

@app.callback(
    Output('plot_log_histogram', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value'),
     Input('hist_dropdown', 'value')])
def update_histogram_dropdown(db_name, collection_name, histogram_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': histogram_name})
    layout = go.Layout(title = histogram['name'],
                       yaxis = {'type': 'log',
                                'autorange': True})
    print(histogram['name'])
    return to_plotly(histogram, layout = layout)

@app.callback(
    Output('one-one', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'PrimaryEnergy'})
    return to_plotly(histogram)

@app.callback(
    Output('one-two', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'PrimaryZenith'})
    return to_plotly(histogram)

@app.callback(
    Output('one-three', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'PrimaryCosZenith'})
    return to_plotly(histogram)

@app.callback(
    Output('two-one', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'CascadeEnergy'})
    return to_plotly(histogram)

@app.callback(
    Output('two-two', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'PulseTime'})
    return to_plotly(histogram)

@app.callback(
    Output('two-three', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'SecondaryMultiplicity'})
    return to_plotly(histogram)

@app.callback(
    Output('three-one', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'InIceDOMOccupancy'})
    return to_plotly(histogram)

@app.callback(
    Output('three-two', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'InIceDOMLaunchTime'})
    return to_plotly(histogram)

@app.callback(
    Output('three-three', 'figure'),
    [Input('db_dropdown', 'value'),
     Input('coll_dropdown', 'value')])    
def update_default_histograms(db_name, collection_name):
    coll = spdb[db_name][collection_name]
    histogram = coll.find_one({'name': 'LogQtot'})
    return to_plotly(histogram)

if __name__ == '__main__':
    app.run_server(debug=True)
