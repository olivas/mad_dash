"""Config file."""

import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import flask

app = dash.Dash(
    __name__, server=flask.Flask(__name__), external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = app.server
app.config.suppress_callback_exceptions = True

dbms_server_url = "http://localhost:8080"
token_server_url = "http://localhost:8888"
