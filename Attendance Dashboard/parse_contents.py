import os
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
import io
import pandas as pd
import datetime
from sections import create_summary_section, create_enrolment_section, create_attendance_section, create_submission_graph

def parse_contents(contents, filename, date):
    if contents is None or filename is None or date is None:
        return None
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        return html.Div(['This file type is not supported. Please upload an Excel file.'])

    try:
        if 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            
            summary_section = create_summary_section(df)
            enrolment_section = create_enrolment_section(df)
            attendance_section = create_attendance_section(df)
            submission_section = create_submission_graph(df)
            
            return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')),
            dbc.Row([
                dbc.Col(summary_section, md=8),  # Use 8 out of 12 columns for the summary
                dbc.Col(html.Div(), md=4),  # This column acts as a space filler
            ]),
            dbc.Row([
                dbc.Col(html.Div(enrolment_section, className="enrolment-container"), md=3),
                dbc.Col(
                    html.Div([
                        dbc.Row([
                            html.Div(attendance_section, className="attendance-submission-container", style={'width': '35.30em'})
                        ]),
                        dbc.Row([
                            html.Div(submission_section, className="attendance-submission-container", style={'width': '35.30em'})
                        ])
                    ]),  # Specify width here in your CSS style
                    md=5
                ),
                dbc.Col(html.Div(), md=4)  # Adjust or remove as needed.
            ])
        ], style={'padding-left': '1em', 'padding-right': '1em', 'padding-top': '1.5em'})
    except Exception as e:
        return html.Div(['There was an error processing this file: {}'.format(e)])