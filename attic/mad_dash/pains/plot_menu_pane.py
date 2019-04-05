# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
def create_plot_menu_pane():
    class_name = 'two columns'    
    divs = \
    [
        html.Div([dcc.Dropdown(id = 'generator-dropdown',
                               placeholder = 'Generator')],
                 className = class_name,
                 style = {"width": "20%"}),
        html.Div([dcc.Dropdown(id = 'histogram-name-dropdown',
                               placeholder = 'Histogram Name')],
                 className = class_name,
                 style = {"width": "40%"})
    ]
    
    return html.Div(divs, className = 'row')                         


