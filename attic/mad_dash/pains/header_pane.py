# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html
import random

from mad_dash.simprod_db import spdb

db = spdb[db_dropdown.value]
collection_names = [n for n in db.collection_names()
                    if n not in ['system.indexes']]

coll_dropdown = dcc.Dropdown(id = 'coll_dropdown',
                             options = [{'label': i, 'value': i} for i in collection_names],
                             value = 'icecube:test-data:trunk:production-histograms')

coll = db[coll_dropdown.value]
histogram_names = [doc['name'] for doc in
                   db[coll_dropdown.value].find({'name' : {'$ne':'filelist'}})]

filelist = [doc['name'] for doc in
            db[coll_dropdown.value].find({'name' : 'filelist'})]

if 'filelist' in histogram_names:
    histogram_names.remove('filelist')

histograms = [coll.find_one({'name': name}) for name in histogram_names]
non_empty_histograms = [h for h in histograms if any(h['bin_values'])]
n_empty = len(histogram_names) - len(non_empty_histograms)
options = [{'label': i, 'value': i} for i in histogram_names]
default_histogram = random.choice(non_empty_histograms)
hist_dropdown = dcc.Dropdown(id = 'hist_dropdown',
                             options = options,
                             value = default_histogram['name'])

filelist_message = "These histograms were generated from %d %s" %\
                   (len(filelist), "I3File" if len(filelist) == 1 else "I3Files")

header_pane = html.Div([html.H1("Mad Dash"),
                        html.Hr(),
                        html.Div([html.Div([html.H3('Database URL'), url_input],
                                           className = 'two columns',
                                           style = {'width': '45%'}),
                                  html.Div([html.H3('Database Names'), db_dropdown],
                                           className = 'two columns',
                                           style = {'width': '45%'})],
                                 className = 'row'), 
                        html.Div([html.H3('Collections'), coll_dropdown]),
                        html.Div([html.H3('Histogram'), 
                                  html.H4(filelist_message, id = 'histogram-filelist'),
                                  html.H4('There are %d histograms in this collection' % len(histogram_names),
                                          id = 'histogram-text'),
                                  html.H4('There are %d empty histograms' % n_empty,
                                          id = 'n-empty-histograms'),
                                  hist_dropdown,
                                  html.Div([html.Div(dcc.Graph(id='plot_linear_histogram'),
                                                     className = 'two columns',
                                                     style = {'width': '45%'}),
                                            html.Div(dcc.Graph(id='plot_log_histogram'),
                                                     className = 'two columns',
                                                     style = {'width': '45%'})],
                                           className = 'row')
                                  ]),
                        html.Hr()],
                       style = {'textAlign': 'center'})    

