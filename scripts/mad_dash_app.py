#!/usr/bin/env python3

import mad_dash
#from mad_dash import serve_layout
from mad_dash.serve_layout import serve_layout

import dash

app = dash.Dash('Mad Dash')
app.layout = serve_layout()
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
app.run_server(debug=True)
