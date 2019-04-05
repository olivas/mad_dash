# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
def create_plot_pane():

    return html.Div([html.Div([dcc.Graph(id='benchmark_pane')],
                              className = 'two columns',
                              style = {"width": "45%"}),
                     html.Div([dcc.Graph(id='test_pane')],
                              className = 'two columns',
                              style = {"width": "45%"})],
                    className = 'row')

