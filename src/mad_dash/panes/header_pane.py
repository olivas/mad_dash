# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html

from pymongo import MongoClient

dbinfo_format = '''
Last Refresh: **%s  (US Mountain Time)**  
Last Run Time: **%s  (US Mountain Time)**  
'''
    
client = MongoClient()

url_input = dcc.Input(id = 'url_input',
                      value = 'mongodb-simprod.icecube.wisc.edu',
                      type = 'text')

dbuser_input = dcc.Input(id = 'dbuser_input',
                         placeholder = 'dbuser',
                         type = 'text')

dbpass_input = dcc.Input(id = 'dbpass_input',
                         placeholder = 'password',
                         type = 'password')

#client = MongoClient(url_input.value)
#dbs = [n for n in client.database_names() if n != 'admin' and n!= 'local']
dbs = ['test']
db_dropdown = dcc.Dropdown(id = 'db_dropdown',
                           options = [{'label': i, 'value': i} for i in dbs],
                           value = dbs[0])

db = client[db_dropdown.value]    
#collection_names = [n for n in db.collection_names()
#                    if n not in ['system.indexes']]
collection_names = ['collection']

#first_collection = db[collection_names[0]]    
#most_recent_document = first_collection.find({}).sort([('timestamp', -1)])[0]
#content = dbinfo_format % (most_recent_document['timestamp'].strftime('%c'),
#                           datetime.datetime.now().strftime('%c'))

#timestamps = html.Div(dcc.Markdown(content),
#                      style = {'textAlign': 'center'})

header_pane = html.Div([html.H1("Mad Dash"),
                           html.Hr(),
                           html.Div([html.Div([html.H3('Database URL'), url_input],
                                              className = 'six columns',
                                              style = {'width': '25%'}),
                                     html.Div([html.H3('Collection'), db_dropdown],
                                              className = 'six columns',
                                              style = {'width': '25%'})],
                                    className = 'row'),
                           #timestamps,
                           html.Hr()],
                          style = {'textAlign': 'center'})    


#header_pane = html.Div([
#    html.Div([
#        html.Div([
#            html.H3('Column 1'),
#            dcc.Graph(id='g1', figure={'data': [{'y': [1, 2, 3]}]})
#        ], className="six columns"),
#
#        html.Div([
#            html.H3('Column 2'),
#            dcc.Graph(id='g2', figure={'data': [{'y': [1, 2, 3]}]})
#        ], className="six columns"),
#    ], className="row")
#])
