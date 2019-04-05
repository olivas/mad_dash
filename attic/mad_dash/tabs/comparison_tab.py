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

def extract_histograms(database_url, database_name, collection_name):

    client = create_simprod_db_client(database_url)
    db = client[database_name]
    collection = db[collection_name]

    histogram_names = [doc['name'] for doc in
                       db[collection_dropdown.value].find({'name' : {'$ne':'filelist'}})]

    return [collection.find_one({'name': name})
            for name in histogram_names
            if name != 'filelist']

def layout():
    return html.Div([html.H3('Collection Comparisons'),
                     dcc.Dropdown(id='collection-dropdown-lhs-tab2',                                       
                                  value='icecube:test-data:trunk:production-histograms'),
                     dcc.Dropdown(id='collection-dropdown-rhs-tab2',                                    
                                  value='icecube:test-data:trunk:production-histograms'),
                     dcc.Dropdown(
                         id='my-dropdown',
                         options=[
                             {'label': 'New York City', 'value': 'NYC'},
                             {'label': 'Montreal', 'value': 'MTL'},
                             {'label': 'San Francisco', 'value': 'SF'}
                         ],
                         value='NYC'
                         ),
                     html.Button('go', id='comparison-go-button-tab2'),
                     html.H3(id='collection-comparison-result-tab2'),
                     html.Hr()
    ])



@app.callback(Output('collection-dropdown-lhs-tab2', 'value'),
              [Input('url-input', 'value'),
               Input('db-dropdown', 'value')])
def set_lhs_collection_options(database_url, database_name):
    client = create_simprod_db_client(database_url)
    db = client[database_name]    
    return [{'label': name, 'value': name} 
            for name in db.collection_names()
            if name != 'system.indexes'] 

@app.callback(Output('collection-dropdown-rhs-tab2', 'value'),
              [Input('url-input', 'value'),
               Input('db-dropdown', 'value')])
def set_rhs_collection_options(database_url, database_name):
    client = create_simprod_db_client(database_url)
    db = client[database_name]    
    return [{'label': name, 'value': name} 
            for name in db.collection_names()
            if name != 'system.indexes'] 

@app.callback(Output('collection-comparison-result-tab2', 'children'),
              [Input('url-input', 'value'),
               Input('db-dropdown', 'value'),
               Input('collection-dropdown-lhs-tab2', 'value'),
               Input('collection-dropdown-rhs-tab2', 'value')])
def compare_collections(database_url, database_name, lhs_collection, rhs_collection):
    client = create_simprod_db_client(database_url)
    db = client[database_name]

    lhs_histograms = extract_histograms(database_url, database_name, lhs_collection)
    rhs_histograms = extract_histograms(database_url, database_name, rhs_collection)

    return 'PASS'
                           
