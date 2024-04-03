from dash import dcc, html

def upload_layout():
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
        html.Div(id='output-data-upload'),
        html.Div(id='loading-state', children=[html.Div("Loading...")], style={'display': 'none'})
    ])