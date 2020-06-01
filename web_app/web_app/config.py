"""Config file."""

import dash  # type: ignore
import flask

app = dash.Dash(__name__, server=flask.Flask(__name__))
server = app.server
app.config.suppress_callback_exceptions = True

dbms_server_url = 'http://localhost:8080'
token_server_url = 'http://localhost:8888'
