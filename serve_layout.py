# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html

def serve_layout():
    
    return html.Div([
        html.H1("Mad Dash"),
        html.H4(id='callback-trigger-test'),
        html.Hr(),
        dcc.Tabs(id='mad-dash-tabs', value='tab1',
                 children = [
                     dcc.Tab(label='Histograms', value='tab1'),
                     dcc.Tab(label='Comparisons', value='tab2')
                 ]),
        html.Div(id='tab-content')
    ])

    
