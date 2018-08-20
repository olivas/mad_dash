# -*- coding: utf-8 -*-

import dash, json, datetime
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['HoboCI_test']

# Run over each collection and get the meta data
# for each run for a given time range.
collection_names = ['tev_starting_muon']

# need a time range 
start_time = datetime.datetime(2017, 10, 26, 0)
end_time = datetime.datetime(2017, 10, 26, 23)

graphs = list()
z = list()
y = list()
for collection_name in collection_names:
    collection = db[collection_name]

    query_command = {'metadata.timestamp': {'$gt': start_time, '$lt': end_time}}
    runs = collection.find(query_command)

    res_stats = list()
    timestamps = list()
    for document in runs:
        res_stats.append(int(document['metadata']['success']))
        timestamps.append(document['metadata']['timestamp'])

    z.append(res_stats)
    y.append(collection_name)
        
res_heatmap = go.Heatmap( z = z,
                          x = timestamps,
                          y = y,
                          zmin = 0,
                          zmax = 1,
                          reversescale = True,
                          showscale = False)

_res_stats_graph = dcc.Graph(figure = go.Figure(data = [res_heatmap],
                                                layout = {'title': 'Run Results'}),
                             
                             id = 'res_heatmap')

pass_fail_stats = html.Div([_res_stats_graph])

