# -*- coding: utf-8 -*-
import datetime
import random

import numpy
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from copy import copy

from db import create_simprod_db_client
from application import app
from compare import compare
from histogram_converter import two_plotly
from histogram_converter import to_plotly
import plotly.graph_objs as go


def cdf(histogram):
    cdf_histogram = copy(histogram)
    v = 0
    for idx, bv in enumerate(histogram['bin_values']):
        v += bv
        histogram['bin_values'][idx] = v
    return histogram

def extract_histograms(database_url, database_name, collection_name):
    '''
    Returns a dictionary of histograms where the key is the histogram name
    and the value is the histogram document.
    '''
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]
    histograms = collection.find({})

    return {h['name']:h for h in histograms
            if h['name'] != 'filelist'}


def scale_to_match(h1, h2):

    n1 = sum(h1['bin_values'])
    n2 = sum(h2['bin_values'])

    if n1 == 0 or n2 == 0:
        return

    print('before sum1 = %d' % sum(h1['bin_values']))
    print('before sum2 = %d'% sum(h2['bin_values']))

    if n1 > n2:
        N = n1/n2
        print('N = %d' % N)
        for idx in range(len(h1['bin_values'])):
            h1['bin_values'][idx] /= N
    else:
        N = n2/n1
        print('N = %d' % N)
        for idx in range(len(h2['bin_values'])):
            h2['bin_values'][idx] /= N

    print('after sum1 = %d' % sum(h1['bin_values']))
    print('after sum2 = %d'% sum(h2['bin_values']))

def layout():
    return html.Div([
        dcc.Input(id='database-url-input-tab2',
                  value='mongodb-simprod.icecube.wisc.edu',
                  readOnly=True,
                  size='33',
                  type='text',
                  style={'text-align': 'center'}),
        dcc.Dropdown(id='database-name-dropdown-tab2',
                     value='simprod_histograms'),
        html.Hr(),
        html.H3('Collection Comparisons'),
        dcc.Dropdown(id='collection-dropdown-lhs-tab2',
                     value='icecube:test-data:trunk:production-histograms'),
        dcc.Dropdown(id='collection-dropdown-rhs-tab2',
                     value='icecube:test-data:trunk:production-histograms'),
        html.Button('go', id='comparison-go-button-tab2'),
        html.Hr(),
        dcc.Dropdown(id='histogram-dropdown-tab2'),
        html.Div([html.Div(dcc.Graph(id='plot-linear-histogram-tab2'),
                           className = 'two columns',
                           style = {'width': '45%'}),
                  html.Div(dcc.Graph(id='plot-log-histogram-tab2'),
                           className = 'two columns',
                           style = {'width': '45%'})],
                 className = 'row'),
        html.Div([html.Div(dcc.Graph(id='plot-histogram-ratio-tab2'),
                           className = 'two columns',
                           style = {'width': '45%'}),
                  html.Div(dcc.Graph(id='plot-histogram-cdf-tab2'),
                           className = 'two columns',
                           style = {'width': '45%'})],
                 className = 'row'),
        html.Hr(),
        html.Table(id='collection-comparison-result-tab2'),
    ])


@app.callback(Output('database-name-dropdown-tab2', 'options'),
              [Input('database-url-input-tab2', 'value')])
def get_database_name_options(database_url):
    client = create_simprod_db_client(database_url)
    db_names = [n for n in client.database_names()
                if n != 'system.indexes']
    db_names.remove('admin')
    db_names.remove('local')
    if 'simprod_filecatalog' in db_names:
        db_names.remove('simprod_filecatalog')

    return [{'value': n, 'label': n} for n in db_names]

@app.callback(Output('collection-dropdown-lhs-tab2', 'options'),
              [Input('database-url-input-tab2', 'value'),
               Input('database-name-dropdown-tab2', 'value')])
def set_lhs_collection_options(database_url, database_name):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    options = [{'label': name, 'value': name}
            for name in db.collection_names()
            if name != 'system.indexes']
    print(options)
    return options

@app.callback(Output('collection-dropdown-rhs-tab2', 'options'),
              [Input('database-url-input-tab2', 'value'),
               Input('database-name-dropdown-tab2', 'value')])
def set_rhs_collection_options(database_url, database_name):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    return [{'label': name, 'value': name}
            for name in db.collection_names()
            if name != 'system.indexes']

@app.callback(Output('collection-comparison-result-tab2', 'children'),
              [Input('comparison-go-button-tab2', 'n_clicks')],
              [State('database-url-input-tab2', 'value'),
               State('database-name-dropdown-tab2', 'value'),
               State('collection-dropdown-lhs-tab2', 'value'),
               State('collection-dropdown-rhs-tab2', 'value')])
def compare_collections(n_clicks,
                        database_url,
                        database_name,
                        lhs_collection,
                        rhs_collection):
    if not n_clicks:
        return

    print("compare_collections: Comparing...")
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_histograms = extract_histograms(database_url,
                                        database_name,
                                        lhs_collection)
    rhs_histograms = extract_histograms(database_url,
                                        database_name,
                                        rhs_collection)

    results = dict()
    for lhs_name, lhs_histogram in lhs_histograms.items():
        if lhs_name not in rhs_histograms:
            print("Histogram %s in LHS, but not RHS." % lhs_name)
            continue
        rhs_histogram = rhs_histograms[lhs_name]
        results[lhs_name] = compare(lhs_histogram, rhs_histogram)

    headers = ['Histogram', 'Chi2', 'KS', 'AD', 'Result', 'Notes']
    table_elements = [html.Tr([html.Th(h) for h in headers])]
    for name, result in results.items():
        chi2_result = result['chisq']['pvalue'] if 'chisq' in result else '---'
        KS_result = result['KS']['pvalue'] if 'KS' in result else '---'
        AD_result = result['AD']['pvalue'] if 'AD' in result else '---'
        pass_fail = 'PASS'
        notes = 'N/A'

        if 'chisq' not in result and 'KS' not in result and 'AD' not in result:
            if len(result) == 1:
                notes = list(result.keys())[0]

        row_data = [name, str(chi2_result), KS_result, AD_result, pass_fail, notes]
        row = html.Tr([html.Td(d) for d in row_data])
        table_elements.append(row)

    print("compare_collections: Done.")
    return table_elements

@app.callback(Output('histogram-dropdown-tab2', 'options'),
              [Input('comparison-go-button-tab2', 'n_clicks')],
              [State('database-name-dropdown-tab2', 'value'),
               State('collection-dropdown-lhs-tab2', 'value'),
               State('collection-dropdown-rhs-tab2', 'value'),
               State('database-url-input-tab2', 'value')])
def update_histogram_dropdown_options(n_clicks,
                                      database_name,
                                      lhs_collection_name,
                                      rhs_collection_name,
                                      database_url):
    if not n_clicks:
        return

    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_collection = db[lhs_collection_name]
    rhs_collection = db[rhs_collection_name]
    rhs_cursor = rhs_collection.find()
    lhs_cursor = lhs_collection.find()
    rhs_histogram_names = [d['name'] for d in rhs_cursor]
    lhs_histogram_names = [d['name'] for d in lhs_cursor]
    histogram_names = [n for n in lhs_histogram_names
                       if n in rhs_histogram_names]
    return [{'label': name, 'value': name} for name in histogram_names]


@app.callback(
    Output('plot-linear-histogram-tab2', 'figure'),
    [Input('histogram-dropdown-tab2', 'value')],
    [State('database-name-dropdown-tab2', 'value'),
     State('collection-dropdown-lhs-tab2', 'value'),
     State('collection-dropdown-rhs-tab2', 'value'),
     State('database-url-input-tab2', 'value')])
def update_linear_histogram_dropdown(histogram_name,
                                     database_name,
                                     lhs_collection_name,
                                     rhs_collection_name,
                                     database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_collection = db[lhs_collection_name]
    rhs_collection = db[rhs_collection_name]
    lhs_histogram = lhs_collection.find_one({'name': histogram_name})
    rhs_histogram = rhs_collection.find_one({'name': histogram_name})
    return two_plotly(lhs_histogram, rhs_histogram)

@app.callback(
    Output('plot-log-histogram-tab2', 'figure'),
    [Input('histogram-dropdown-tab2', 'value')],
    [State('database-name-dropdown-tab2', 'value'),
     State('collection-dropdown-lhs-tab2', 'value'),
     State('collection-dropdown-rhs-tab2', 'value'),
     State('database-url-input-tab2', 'value')])
def update_log_histogram_dropdown(histogram_name,
                                  database_name,
                                  lhs_collection_name,
                                  rhs_collection_name,
                                  database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_collection = db[lhs_collection_name]
    rhs_collection = db[rhs_collection_name]
    lhs_histogram = lhs_collection.find_one({'name': histogram_name})
    rhs_histogram = rhs_collection.find_one({'name': histogram_name})

    layout = go.Layout(title = lhs_histogram['name'],
                       yaxis = {'type': 'log',
                                'autorange': True})

    return two_plotly(lhs_histogram, rhs_histogram, layout = layout)

@app.callback(
    Output('plot-histogram-ratio-tab2', 'figure'),
    [Input('histogram-dropdown-tab2', 'value')],
    [State('database-name-dropdown-tab2', 'value'),
     State('collection-dropdown-lhs-tab2', 'value'),
     State('collection-dropdown-rhs-tab2', 'value'),
     State('database-url-input-tab2', 'value')])
def update_ratio_histogram(histogram_name,
                         database_name,
                         lhs_collection_name,
                         rhs_collection_name,
                         database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_collection = db[lhs_collection_name]
    rhs_collection = db[rhs_collection_name]
    lhs_histogram = lhs_collection.find_one({'name': histogram_name})
    rhs_histogram = rhs_collection.find_one({'name': histogram_name})

    scale_to_match(lhs_histogram, rhs_histogram)

    ratio_histogram = copy(lhs_histogram)
    for idx, bv in enumerate(rhs_histogram['bin_values']):
        ratio_histogram['bin_values'][idx] /= bv if bv > 0 else 1.

    layout = go.Layout(title = "Scaled to Match Ratio")
    return to_plotly(ratio_histogram, layout=layout)

@app.callback(
    Output('plot-histogram-cdf-tab2', 'figure'),
    [Input('histogram-dropdown-tab2', 'value')],
    [State('database-name-dropdown-tab2', 'value'),
     State('collection-dropdown-lhs-tab2', 'value'),
     State('collection-dropdown-rhs-tab2', 'value'),
     State('database-url-input-tab2', 'value')])
def update_cdf_histogram(histogram_name,
                         database_name,
                         lhs_collection_name,
                         rhs_collection_name,
                         database_url):
    client = create_simprod_db_client(database_url)
    db = client[database_name]
    lhs_collection = db[lhs_collection_name]
    rhs_collection = db[rhs_collection_name]
    lhs_histogram = lhs_collection.find_one({'name': histogram_name})
    rhs_histogram = rhs_collection.find_one({'name': histogram_name})

    scale_to_match(lhs_histogram, rhs_histogram)

    ratio_histogram = cdf(lhs_histogram)
    for idx, bv in enumerate(cdf(rhs_histogram)['bin_values']):
        ratio_histogram['bin_values'][idx] /= bv if bv > 0 else 1.

    layout = go.Layout(title = "Scaled to Match CDF Ratio")
    return to_plotly(ratio_histogram, layout = layout)
