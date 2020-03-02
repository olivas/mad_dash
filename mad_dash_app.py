#!/usr/bin/env python3

import tabs.comparison_tab as comparison_tab
import tabs.histogram_tab as histogram_tab
from application import app
from dash.dependencies import Input, Output
from serve_layout import serve_layout

app.layout = serve_layout
server = app.server


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
