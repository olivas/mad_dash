#!/usr/bin/env python3

from dash.dependencies import Input
from dash.dependencies import Output

from application import app
import mad_dash.tabs.histogram_tab as histogram_tab
import mad_dash.tabs.comparison_tab as comparison_tab
from mad_dash.serve_layout import serve_layout

app.layout = serve_layout

@app.callback(Output('tab-content', 'children'),
              [Input('mad-dash-tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        print('tab1')
        layout = histogram_tab.layout()

    if tab == 'tab2':
        print('tab2')
        layout = comparison_tab.layout()

    return layout
        
if __name__ == '__main__':
    app.run_server(debug=True)
