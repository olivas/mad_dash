# -*- coding: utf-8 -*-
import datetime
import random

import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from db import create_simprod_db_client
from application import app
from histogram_converter import to_plotly

def layout():

    return html.Div([
        dcc.Input(id='database-url-input-tab1',
                  value='mongodb-simprod.icecube.wisc.edu',
                  readOnly=True,
                  size=33,
                  type='text',
                  style={'text-align': 'center'}),
        dcc.Dropdown(id='database-name-dropdown-tab1',
                     value='simprod_histograms'),
        html.Hr(),
        html.Div([html.H3('Collections'),
                  dcc.Dropdown(id='collection-dropdown-tab1',
                               value='icecube:test-data:trunk:production-histograms')
        ]),
        html.Div([html.H3('Histogram'), 
                  html.H6(id='filelist-message-tab1'),                                            
                  html.H6(id='n-histogram-message-tab1'),                                            
                  html.H6(id='n-empty-histograms-message-tab1'),                                            
                  dcc.Dropdown(id='histogram-dropdown-tab1',
                               value='PrimaryEnergy'),
                  html.Div([html.Div(dcc.Graph(id='plot-linear-histogram-tab1'),
                                     className = 'two columns',
                                     style = {'width': '45%'}),
                            html.Div(dcc.Graph(id='plot-log-histogram-tab1'),
                                     className = 'two columns',
                                     style = {'width': '45%'})],
                           className = 'row')
        ]),
        html.Hr()],
                    style = {'textAlign': 'center'})

@app.callback(Output('callback-trigger-test', 'children'),
              [Input('database-url-input-tab1', 'value')])
def callback_trigger_test(value):
    return value

@app.callback(Output('database-name-dropdown-tab1', 'options'),
              [Input('database-url-input-tab1', 'value')])
def get_database_name_options(database_url):
    client = create_simprod_db_client(database_url)
    db_names = [n for n in client.database_names()
                if n != 'system.indexes']
    db_names.remove('admin')
    db_names.remove('local')
    if 'simprod_filecatalog' in db_names:
        db_names.remove('simprod_filecatalog')

    return [{'value': n, 'label': n} for n in db_names]

@app.callback(Output('collection-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_collection_options(database_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]    
    return [{'label': name, 'value': name} 
            for name in db.collection_names()
            if name != 'system.indexes'] 

@app.callback(Output('filelist-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def update_histogram_filelist_message(database_name, collection_name, database_url):
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]

    filelist = [doc['name'] for doc in
                db[collection_name].find({'name' : 'filelist'})]
    
    filelist_message = "Histograms from '%s' were generated from %d %s" %\
                       (collection_name,
                        len(filelist),
                        "I3File" if len(filelist) == 1 else "I3Files")

    return filelist_message

@app.callback(Output('n-histogram-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def update_n_histograms_message(database_name, collection_name, database_url):
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram_names = [d['name'] for d in collection.find()]    
    return 'There are %d histograms in this collection' % len(histogram_names)

@app.callback(Output('n-empty-histograms-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def update_n_empty_histograms_message(database_name, collection_name, database_url):
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram_names = [d['name'] for d in collection.find()]
    # this is crazy
    # make this a server-side call
    histograms = [collection.find_one({'name': name})
                  for name in histogram_names
                  if name != 'filelist']
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histogram_names) - len(non_empty_histograms)    
    return 'There are %d empty histograms' % n_empty

@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def update_histogram_dropdown_options(database_name, collection_name, database_url):
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram_names = [d['name'] for d in collection.find()]    
    return [{'label': name, 'value': name} for name in histogram_names]

@app.callback(
    Output('plot-linear-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_linear_histogram_dropdown(histogram_name, database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': histogram_name})
    return to_plotly(histogram)

@app.callback(
    Output('plot-log-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_log_histogram_dropdown(histogram_name, database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': histogram_name})
    layout = go.Layout(title = histogram['name'],
                       yaxis = {'type': 'log',
                                'autorange': True})
    return to_plotly(histogram, layout = layout)

