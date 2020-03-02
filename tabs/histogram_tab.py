# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
import db
import plotly.graph_objs as go
from application import app
from dash.dependencies import Input, Output, State
from histogram_converter import n_histograms_to_plotly


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
    database_names = db.get_database_names(database_url)
    return [{'value': n, 'label': n} for n in database_names]


@app.callback(Output('collection-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_collection_options(database_name, database_url):
    collection_names = db.get_collection_names(database_name, database_url)
    return [{'label': name, 'value': name} for name in collection_names]


@app.callback(Output('filelist-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_histogram_filelist_message(database_name, collection_name, database_url):
    if not collection_name:
        return

    filelist = db.get_filelist(collection_name, database_name, database_url)

    i3_files_str = "I3File" if len(filelist) == 1 else "I3Files"
    filelist_message = f"Histograms from '{collection_name}' were generated from {len(filelist)} {i3_files_str}"

    return filelist_message


@app.callback(Output('n-histogram-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_n_histograms_message(database_name, collection_name, database_url):
    if not collection_name:
        return

    histogram_names = db.get_histogram_names(collection_name, database_name, database_url)
    return f"There are {len(histogram_names)} histograms in this collection"


@app.callback(Output('n-empty-histograms-message-tab1', 'children'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_n_empty_histograms_message(database_name, collection_name, database_url):
    if not collection_name:
        return

    histograms = db.get_histograms(collection_name, database_name, database_url)
    non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
    n_empty = len(histograms) - len(non_empty_histograms)

    return f'There are {n_empty} empty histograms'


@app.callback(Output('histogram-dropdown-tab1', 'options'),
              [Input('database-name-dropdown-tab1', 'value'),
               Input('collection-dropdown-tab1', 'value')],
              [State('database-url-input-tab1', 'value')])
def update_histogram_dropdown_options(database_name, collection_name, database_url):
    if not collection_name:
        return

    histogram_names = db.get_histogram_names(collection_name, database_name, database_url)
    return [{'label': name, 'value': name} for name in histogram_names]


@app.callback(
    Output('plot-linear-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_linear_histogram_dropdown(histogram_name, database_name, collection_name, database_url):
    histogram = db.get_histogram(histogram_name, collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('plot-log-histogram-tab1', 'figure'),
    [Input('histogram-dropdown-tab1', 'value'),
     Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_log_histogram_dropdown(histogram_name, database_name, collection_name, database_url):
    histogram = db.get_histogram(histogram_name, collection_name, database_name, database_url)
    layout = go.Layout(title=histogram['name'],
                       yaxis={'type': 'log',
                              'autorange': True})
    return n_histograms_to_plotly([histogram], layout=layout)


# NINE PLOTS #


@app.callback(
    Output('one-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_one_one(database_name, collection_name, database_url):
    histogram = db.get_histogram('PrimaryEnergy', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('one-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_one_two(database_name, collection_name, database_url):
    histogram = db.get_histogram('PrimaryZenith', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('one-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_one_three(database_name, collection_name, database_url):
    histogram = db.get_histogram('PrimaryCosZenith', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('two-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_two_one(database_name, collection_name, database_url):
    histogram = db.get_histogram('CascadeEnergy', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('two-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_two_two(database_name, collection_name, database_url):
    histogram = db.get_histogram('PulseTime', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('two-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_two_three(database_name, collection_name, database_url):
    histogram = db.get_histogram('SecondaryMultiplicity', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('three-one', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_three_one(database_name, collection_name, database_url):
    histogram = db.get_histogram('InIceDOMOccupancy', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('three-two', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_three_two(database_name, collection_name, database_url):
    histogram = db.get_histogram('InIceDOMLaunchTime', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])


@app.callback(
    Output('three-three', 'figure'),
    [Input('database-name-dropdown-tab1', 'value'),
     Input('collection-dropdown-tab1', 'value')],
    [State('database-url-input-tab1', 'value')])
def update_default_histograms_three_three(database_name, collection_name, database_url):
    histogram = db.get_histogram('LogQtot', collection_name, database_name, database_url)
    return n_histograms_to_plotly([histogram])
