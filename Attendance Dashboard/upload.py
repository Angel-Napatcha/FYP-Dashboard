from dash import dcc, html


def upload_layout():
    # Layout for the file upload interface
    return html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ', 
                html.A('Select Files')
            ], className='upload-text'),
            className='custom-upload',
            style={'width': '100%', 'padding': '20px', 'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center'}
        ),
        dcc.Loading(
            id='loading-upload',
            children=html.Div(id='output-data-upload'),
            type='circle'
        ),
        html.Div(id='loading-state', style={'display': 'none'}, children="Loading..."),
        dcc.Store(id='stored-data')
    ])