import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import no_update
import dash_bootstrap_components as dbc
import base64
import io
import pandas as pd
import datetime
import openpyxl
from data_processing import calculate_summary_statistics

# Initialize the Dash app (assuming you're doing this inside app.py)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ], className='upload-text'),
        className='custom-upload',
        style={'display': 'block'}
    ),
    # This will toggle based on upload status
    html.Div(id='output-data-upload'),
    # Initially hidden loading indicator
    html.Div(id='loading-state', children=[html.Div("Loading...")], style={'display': 'none'})
])

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join('uploaded_files', name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        return html.Div(['This file type is not supported. Please upload an Excel file.'])

    try:
        if 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            # Call the processing function
            summary_data = calculate_summary_statistics(df)

            # Create a layout to display processed data using Bootstrap components
            card_content = dbc.Row([
                    dbc.Col(className='summary-card', children=[
                        html.H3('Total Students', className='summary-title'),
                        html.H3(f"{summary_data['total_students']}", className='summary-value'),
                        html.P([html.Span(f"{summary_data['dropout_rate']:.2f}%", style={'color': 'red'}), " dropout rate"], className='summary-small')
                    ], lg=4, md=6),
                    dbc.Col(className='summary-card', children=[
                        html.H3('Average Attendance Rate', className='summary-title'),
                        html.H3(f"{summary_data['average_attendance']:.2f}%", className='summary-value')
                    ], lg=4, md=6),
                    dbc.Col(className='summary-card', children=[
                        html.H3(['Course with ', html.Span('Highest', style={'color': 'green'}), ' Attendance Rate'], className='summary-title'),
                        html.H3(summary_data['course_with_highest_attendance'][0], className='summary-value'),
                        html.P([
                            html.Span(f"{summary_data['course_with_highest_attendance'][1]:.2f}%", style={'color': 'green'}),
                            " average"
                        ], className='summary-small')
                    ], lg=4, md=6),
                    dbc.Col(className='summary-card', children=[
                        html.H3(['Course with ', html.Span('Lowest', style={'color': 'red'}), ' Attendance Rate'], className='summary-title'),
                        html.H3(summary_data['course_with_lowest_attendance'][0], className='summary-value'),
                        html.P([
                            html.Span(f"{summary_data['course_with_lowest_attendance'][1]:.2f}%", style={'color': 'red'}), 
                            " average"
                        ], className='summary-small')
                    ], lg=4, md=6),
                    dbc.Col(className='summary-card', children=[
                        html.H3('Average Submission Rate', className='summary-title'),
                        html.H3(f"{summary_data['average_submission_rate']:.2f}%", className='summary-value')
                    ], lg=4, md=6)
                ], justify="start")

            cards_layout = dbc.Container([
                html.H5("Summary", style={'text-align': 'left', 'margin-bottom': '0.4rem', 'margin-left': '0.5em', 'margin-top': '0.4rem'}),
                dbc.Row(
                    card_content,
                    justify="around",
                )
            ], fluid=False, className="summary-section")

            return html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')),
                cards_layout
            ], style={'padding-left': '20px', 'padding-top': '20px'})
    except Exception as e:
        return html.Div(['There was an error processing this file: {}'.format(e)])

@app.callback(
    Output('output-data-upload', 'children'),
    Output('loading-state', 'style'),
    Output('upload-data', 'style'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        if not isinstance(list_of_contents, list):
            list_of_contents = [list_of_contents]
        if not isinstance(list_of_names, list):
            list_of_names = [list_of_names]
        if not isinstance(list_of_dates, list):
            list_of_dates = [list_of_dates]

        children = []
        for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
            if not (name.endswith('.xls') or name.endswith('.xlsx')):
                children.append(html.Div([
                    f'File "{name}" is not an Excel file and was not uploaded.'
                ]))
            else:
                child = parse_contents(content, name, date)
                children.append(child)
                save_file(name, content)

        # Hide the loading state and the upload interface, then show the processed data
        loading_style = {'display': 'none'}
        upload_style = {'display': 'none'}  # Hide upload interface
        return children, loading_style, upload_style

    # If no files are uploaded, don't update the upload interface or the loading state
    return [], {'display': 'none'}, no_update

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)