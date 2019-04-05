# -*- coding: utf-8 -*-
import datetime
import random

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from mad_dash.db import create_simprod_db_client
from mad_dash.application import app

def get_database_name_options(database_url):
    client = create_simprod_db_client(database_url)
    db_names = [n for n in client.database_names()
                if n != 'system.indexes']
    db_names.remove('admin')
    db_names.remove('local')
    if 'simprod_filecatalog' in db_names:
        db_names.remove('simprod_filecatalog')

    return [{'value': n, 'label': n} for n in db_names]

def get_collection_options(database_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]    
    return [{'label': name, 'value': name} 
            for name in db.collection_names()
            if name != 'system.indexes'] 

def get_histogram_options(database_name, collection_name, database_url):
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram_names = [d['name'] for d in collection.find()]    
    return [{'label': name, 'value': name} for name in histogram_names]

def layout():

    database_url_input = dcc.Input(id='database-url-input-tab1',
                                   value='mongodb-simprod.icecube.wisc.edu',
                                   readOnly=True,
                                   size=33,
                                   type='text',
                                   style={'text-align': 'center'})

    database_name_dropdown = dcc.Dropdown(id='database-name-dropdown-tab1',
                                          options=get_database_name_options(database_url_input.value), 
                                          value='simprod_histograms')

    collection_dropdown = dcc.Dropdown(id='collection-dropdown-tab1',
                                       options=get_collection_options(database_name_dropdown.value,
                                                                      database_url_input.value),
                                       value='icecube:test-data:trunk:production-histograms')
    
    return html.Div([
        html.Div([html.Div([
            html.H3('Database URL'),
            database_url_input
        ],
                           className = 'two columns',
                           style = {'width': '45%'}),
                  html.Div([
                      html.H3('Database Names'),
                      database_name_dropdown
                 ],
                           className = 'two columns',
                           style = {'width': '45%'})],
                 className = 'row'),         
        html.Div([html.H3('Collections'), collection_dropdown]),
        html.Div([html.H3('Histogram'), 
                  html.H4(id='n-histogram-message-tab1'),                                            
                  html.H4(id='n-empty-histograms-tab1'),                                            
                  dcc.Dropdown(id='histogram-dropdown-tab1',
                               options=get_histogram_options(database_name_dropdown.value,
                                                             collection_dropdown.value,
                                                              database_url_input.value),
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

@app.callback(Output('database-name-dropdown-tab1', 'options'),
              [Input('database-url-input-tab1', 'value')])
def set_database_name_options(database_url):
    '''
    Current this does nothing unless you change database-url-input-tab1
    readOnly flag to True.
    '''
    return get_database_name_options(database_url)

@app.callback(Output('collection-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def set_collection_options(database_name, database_url):
    print('huh')
    return get_collection_options(database_name, database_url)
    
@app.callback(Output('filelist-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value'),
               Input('histogram-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def set_histogram_filelist_message(database_name, collection_name, _, database_url):
    print('huh')
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
def set_n_histograms_message(database_name, collection_name, database_url):
    print('huh')
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
def set_n_empty_histograms_message(database_name, collection_name, database_url):
    print('huh')
    if not collection_name:
        return
    
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram_names = [d['name'] for d in collection.find()]
    histograms = [collection.find_one({'name': name}) for name in histogram_names]
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histogram_names) - len(non_empty_histograms)    
    return 'There are %d empty histograms' % n_empty

@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
               [State('database-url-input-tab1', 'value')])
def set_histogram_dropdown_options(database_name, collection_name, database_url):
    print('huh')
    return get_histograms_dropdown_options(database_name, collection_name, database_url)

@app.callback(
    Output('plot-linear-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_linear_histogram_dropdown(histogram_name, database_name, collection_name, database_url):
    print('huh')
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
    print('huh')
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': histogram_name})
    layout = go.Layout(title = histogram['name'],
                       yaxis = {'type': 'log',
                                'autorange': True})
    return to_plotly(histogram, layout = layout)

