# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html

from pymongo import MongoClient

def create_database_selection_pane():
    
    url_input = dcc.Input(id = 'url_input',
                          value = 'mongodb://localhost:27017/',
                          type = 'text')

    client = MongoClient(url_input.value)
    dbs = [n for n in client.database_names() if n.startswith("HoboCI")]

    db_dropdown = dcc.Dropdown(id = 'db_dropdown',
                               options = [{'label': i, 'value': i} for i in dbs],
                               value = dbs[0])

    db = client[db_dropdown.value]    
    collection_names = [n for n in db.collection_names()
                        if n not in ['system.indexes']]
    
    return html.Header([html.Div([html.Div([url_input],                        
                                           className = 'two columns',
                                           style = {'width': '45%'}),
                                  html.Div([db_dropdown],
                                           className = 'two columns',
                                           style = {'width': '45%'})],
                                 className = 'row')],
                       style = {'textAlign': 'center'})    
