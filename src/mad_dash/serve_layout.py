# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from pymongo import MongoClient

import mad_dash
from mad_dash.histogram_converter import to_plotly

def serve_layout():
    return html.Div([dcc.Tabs(id='mad-dash-tabs', value='tab1',
                              children = [
                                  dcc.Tab(label='Histograms', value='tab1'),
                                  dcc.Tab(label='Comparisons', value='tab2')
                              ]),
                    html.Div(id='tab-content')])
