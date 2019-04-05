# -*- coding: utf-8 -*-
import datetime
import random

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State

from db import create_simprod_db_client
from application import app

def extract_histograms(database_url, database_name, collection_name):

    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]

    histogram_names = [doc['name'] for doc in
                       collection.find({'name' : {'$ne':'filelist'}})]

    return [collection.find_one({'name': name})
            for name in histogram_names
            if name != 'filelist']

def layout():
    return html.Div([
        dcc.Input(id='database-url-input-tab2',
                  value='mongodb-simprod.icecube.wisc.edu',
                  readOnly=True,
                  size=33,
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
        html.H3(id='collection-comparison-result-tab2'),
        html.Button('go', id='comparison-go-button-tab2'),
        html.Hr()
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
              [Input('database-url-input-tab2', 'value'),
               Input('database-name-dropdown-tab2', 'value'),
               Input('collection-dropdown-lhs-tab2', 'value'),
               Input('collection-dropdown-rhs-tab2', 'value')])
def compare_collections(database_url, database_name, lhs_collection, rhs_collection):
    print('WTF')
    client = create_simprod_db_client(database_url)
    db = client[database_name]

    print('extracting lhs histograms...')
    lhs_histograms = extract_histograms(database_url, database_name, lhs_collection)
    print('done.')
    print('extracting rhs histograms')
    rhs_histograms = extract_histograms(database_url, database_name, rhs_collection)
    print('done.')

    print('ugh.')
    return 'PASS'
                           
