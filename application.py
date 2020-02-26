
import dash
import flask

app = dash.Dash(__name__, server = flask.Flask(__name__))
server = app.server
app.config.suppress_callback_exceptions = True
