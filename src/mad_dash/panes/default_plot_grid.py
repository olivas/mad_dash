# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html

row_one = html.Div([html.Div([dcc.Graph(id='one-one')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='one-two')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='one-three')],
                             className = 'three columns',
                             style = {"width": "30%"})],
                   className = 'row')

row_two = html.Div([html.Div([dcc.Graph(id='two-one')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='two-two')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='two-three')],
                             className = 'three columns',
                             style = {"width": "30%"})],
                   className = 'row')

row_three = html.Div([html.Div([dcc.Graph(id='three-one')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='three-two')],
                             className = 'three columns',
                             style = {"width": "30%"}),
                    html.Div([dcc.Graph(id='three-three')],
                             className = 'three columns',
                             style = {"width": "30%"})],
                   className = 'row')

default_plot_grid = html.Div([row_one, row_two, row_three])
