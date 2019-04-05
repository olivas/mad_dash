# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
def create_histogram_slider_pane():

    # this really looks like shit and it doesn't work to boot.
    back_button = html.Button('Back', id='back-button')    
    next_button = html.Button('Next', id='next-button')
    slider = dcc.Slider(min=0, max=10, step=1, value = 0, id = 'histogram-slider')
            
    return html.Div([back_button, slider, next_button])

    
