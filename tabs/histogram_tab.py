# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from application import app
from dash.dependencies import Input, Output, State
from db import create_simprod_db_client
from histogram_converter import to_plotly


def layout():

    return html.Div([
        dcc.Input(id='database-url-input-tab1',
                  value='mongodb-simprod.icecube.wisc.edu',
                  readOnly=True,
                  size='33',
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
                                     className='two columns',
                                     style={'width': '45%'}),
                            html.Div(dcc.Graph(id='plot-log-histogram-tab1'),
                                     className='two columns',
                                     style={'width': '45%'})],
                           className='row')
                  ]),
        html.Hr(),
        html.Div([html.Div([dcc.Graph(id='one-one')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='one-two')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='one-three')],
                           className='three columns',
                           style={"width": "30%"})],
                 className='row'),
        html.Div([html.Div([dcc.Graph(id='two-one')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='two-two')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='two-three')],
                           className='three columns',
                           style={"width": "30%"})],
                 className='row'),
        html.Div([html.Div([dcc.Graph(id='three-one')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='three-two')],
                           className='three columns',
                           style={"width": "30%"}),
                  html.Div([dcc.Graph(id='three-three')],
                           className='three columns',
                           style={"width": "30%"})],
                 className='row')],
                    style={'textAlign': 'center'})


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
    filelist = collection.find_one({'name' : 'filelist'})['files']
    
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
    cursor = collection.find()
    histogram_names = [d['name'] for d in cursor]
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
    cursor = collection.find()
    histograms = [h for h in cursor if h['name'] != 'filelist']                  
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histograms) - len(non_empty_histograms)    
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
    cursor = collection.find()
    histogram_names = [d['name'] for d in cursor] 
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

# NINE PLOTS #

@app.callback(
    Output('one-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'PrimaryEnergy'})
    return to_plotly(histogram)

@app.callback(
    Output('one-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'PrimaryZenith'})
    return to_plotly(histogram)

@app.callback(
    Output('one-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'PrimaryCosZenith'})
    return to_plotly(histogram)

@app.callback(
    Output('two-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'CascadeEnergy'})
    return to_plotly(histogram)

@app.callback(
    Output('two-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'PulseTime'})
    return to_plotly(histogram)

@app.callback(
    Output('two-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'SecondaryMultiplicity'})
    return to_plotly(histogram)

@app.callback(
    Output('three-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'InIceDOMOccupancy'})
    return to_plotly(histogram)

@app.callback(
    Output('three-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'InIceDOMLaunchTime'})
    return to_plotly(histogram)

@app.callback(
    Output('three-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])    
def update_default_histograms(database_name, collection_name, database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histogram = collection.find_one({'name': 'LogQtot'})
    return to_plotly(histogram)
