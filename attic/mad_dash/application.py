#!/usr/bin/env python3

import dash
import flask

app = dash.Dash('Mad Dash', server = flask.Flask(__name__))
app.css.append_css({
    'external_url': 'https://codepen.io/aolivas/pen/bWLwgP.css'
})
server = app.server
app.config.suppress_callback_exceptions = True
