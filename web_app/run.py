"""Root python script for Mad-Dash web application."""

from web_app.config import app

if __name__ == '__main__':
    app.run_server(debug=True)
