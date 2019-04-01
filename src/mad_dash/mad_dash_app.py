#!/usr/bin/env python3

import sys, os
from os.path import join

import dash
import flask
from dash.dependencies import Input
from dash.dependencies import Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from mad_dash.serve_layout import serve_layout
from mad_dash.simprod_db import spdb
from mad_dash.histogram_converter import to_plotly
from mad_dash.panes.header_pane import header_pane
from mad_dash.panes.default_plot_grid import default_plot_grid

app = dash.Dash('Mad Dash', server = flask.Flask(__name__))
app.layout = serve_layout()
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
server = app.server
app.config.suppress_callback_exceptions = True

@app.callback(Output('tab-content', 'children'),
              [Input('mad-dash-tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        return html.Div([header_pane,
                         html.Hr(),
                         default_plot_grid])

    if tab == 'tab2':
        return html.Div([header_pane,
                         html.Hr(),
                         default_plot_grid])


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
    app.run_server(debug=True, port=4000)
