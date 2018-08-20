# -*- coding: utf-8 -*-
import datetime
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from pymongo import MongoClient

import mad_dash
from mad_dash.histogram_converter import to_plotly

from mad_dash.panes.header_pane import header_pane
#from mad_dash.panes.plot_pane import plot_pane
#from mad_dash.panes.plot_menu_pane import plot_menu_pane

def serve_layout():
    return header_pane

    #return html.Div([header_pane,
                     #plot_menu_pane, html.Hr(),                     
                     #plot_pane, html.Hr()
    #])
