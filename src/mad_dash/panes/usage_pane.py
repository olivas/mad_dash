# -*- coding: utf-8 -*-

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from pymongo import MongoClient

# this should get collection names from
def create_usage_pane(start_time,                      
                      end_time,
                      collection_names):
    url = 'mongodb://localhost:27017/'
    dbname = 'HoboCI_test_test'
    client = MongoClient(url)
    db = client[dbname]

    print('url: %s' % url)
    print('db: %s' % dbname)
    print('create_usage_pane: collection_names = %s' % str(collection_names))

    cpu_scatter = list()
    mem_scatter = list()
    gpu_scatter = list()
    for collection_name in collection_names:
        collection = db[collection_name]

        query_command = {'timestamp': {'$gt': start_time, '$lt': end_time}}
        documents = collection.find(query_command)

        print(type(start_time))
        print("found %d documents for (%s, %s)" % (documents.count(), start_time, end_time))

        cpu_stats = list()
        mem_stats = list()
        gpu_stats = list()
        timestamps = list()
        for d in documents:
            # either loop like list or reset the cursors
            cpu_stats.append(d['usage']['utime'])
            mem_stats.append(d['usage']['maxrss'] / 1e6) # want units of GB
            gpu_stats.append(d['usage']['stime'])
            timestamps.append(d['timestamp'])
            
        cpu_scatter.append(go.Scatter(x = timestamps, y = cpu_stats, name = collection_name))
        mem_scatter.append(go.Scatter(x = timestamps, y = mem_stats, name = collection_name))
        gpu_scatter.append(go.Scatter(x = timestamps, y = [0 for t in timestamps], name = collection_name))

    margin = go.Margin(l = 50, r = 10, t = 30, b = 70)
    cpu_stats_graph = dcc.Graph(figure = go.Figure(data = cpu_scatter,
                                                   layout = {'title':  'CPU Time',
                                                             'margin': margin,
                                                             'legend' : {'x': 0, 'y': 1}}),
                                id = 'cpu_stats_%s' % collection_name)

    mem_stats_graph = dcc.Graph(figure = go.Figure(data = mem_scatter, 
                                                   layout = {'title':  'Peak Memory Usage',
                                                             'margin': margin,
                                                             'legend' : {'x': 0, 'y': 1}}),
                                id = 'mem_sstats_%s' % collection_name)

    gpu_stats_graph = dcc.Graph(figure = go.Figure(data = gpu_scatter, 
                                                   layout = {'title':  'GPU Usage',
                                                             'margin': margin,
                                                             'legend' : {'x': 0, 'y': 1}}),
                                id = 'gpu_stats_%s' % collection_name)        
        
    return html.Div([cpu_stats_graph, mem_stats_graph, gpu_stats_graph],
                    id = 'usage-pane')
                    
                    

