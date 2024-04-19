from dash import html
import dash_bootstrap_components as dbc
import base64
import io
import os
import pandas as pd
import datetime
from sections import create_summary_section, create_enrolment_section, create_attendance_section, create_submission_section, create_concerning_students_section

def parse_contents(contents, filename, date, decrypt=True):
    # Check if any of the parameters are None, return None if any are missing
    if contents is None or filename is None or date is None:
        return None

    # Split the content into type and data parts, then decode the base64 encoded data
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Check if the file extension is for Excel files, return an error message if not
    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        return html.Div(['This file type is not supported. Please upload an Excel file.'])

    try:
        if 'xls' in filename:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(io.BytesIO(decoded))
            
            # Create various sections of the dashboard
            summary_section = create_summary_section(df)
            enrolment_section = create_enrolment_section(df)
            attendance_section = create_attendance_section(df)
            submission_section = create_submission_section(df)
            concerning_students_section = create_concerning_students_section(df)
            
            # Organise the created sections into a responsive layout
            return html.Div([
            html.H5(filename), # Display the file name
            html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')), # Display the upload time formatted
            dbc.Row([
                dbc.Col([
                    summary_section, 
                    dbc.Row([
                        dbc.Col(enrolment_section, width=4),  
                        dbc.Col([
                            dbc.Row(attendance_section),
                            dbc.Row(submission_section), 
                        ], width=4),
                    ]), 
                ], width=8),
                dbc.Col(concerning_students_section, width=4),
            ]),
        ], style={'padding-left': '1em', 'padding-right': '1em', 'padding-top': '1.5em'})
    
    except Exception as e:
        # Return an error message if there was a problem processing the file
        return html.Div(['There was an error processing this file: {}'.format(e)])