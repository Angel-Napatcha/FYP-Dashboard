from dash import dcc, html

def upload_layout():
    # Define a layout for the file upload interface
    return html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ', 
                html.A('Select Files')
            ], className='upload-text'),
            className='custom-upload',
            style={'display': 'block'}
        ),
        # Div for displaying outputs after file upload, initially empty
        html.Div(id='output-data-upload'),
        # Div for showing a loading state, hidden by default
        html.Div(id='loading-state', children=[html.Div("Loading...")], style={'display': 'none'})
    ])