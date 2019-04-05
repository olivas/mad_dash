#!/usr/bin/env python3

from dash.dependencies import Input
from dash.dependencies import Output

from application import app
import tabs.histogram_tab as histogram_tab
import tabs.comparison_tab as comparison_tab
from serve_layout import serve_layout

from db import create_simprod_db_client

app.layout = serve_layout

@app.callback(Output('tab-content', 'children'),
              [Input('mad-dash-tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        layout = histogram_tab.layout()

    if tab == 'tab2':
        layout = comparison_tab.layout()
    return layout

if __name__ == '__main__':
    app.run_server(debug=True)

    
