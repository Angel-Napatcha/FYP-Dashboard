import dash
import dash_bootstrap_components as dbc
from upload import upload_layout
from callbacks import register_callbacks

# Initialize the Dash app (assuming you're doing this inside app.py)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = upload_layout()

register_callbacks(app)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)