import dash
from dash import dcc
import dash_bootstrap_components as dbc
from upload import upload_layout
from callbacks import register_callbacks

# Initialise the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    upload_layout(),
    dcc.Store(id='stored-data')
], fluid=True)

register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)