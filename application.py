
import dash
import flask

app = dash.Dash('Mad Dash', server = flask.Flask(__name__))
server = app.server
app.config.suppress_callback_exceptions = True
