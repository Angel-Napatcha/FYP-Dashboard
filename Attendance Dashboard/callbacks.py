from dash.dependencies import Input, Output, State
from dash import html, no_update, dcc
import dash_bootstrap_components as dbc
from sections import save_file
from parse_contents import parse_contents
import pandas as pd

def register_callbacks(app):
    @app.callback(
        Output('output-data-upload', 'children'),
        Output('loading-state', 'style'),
        Output('upload-data', 'style'),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'), State('upload-data', 'last_modified')]
    )
    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            # Normalize input data to lists to handle single or multiple files
            list_of_contents = list_of_contents if isinstance(list_of_contents, list) else [list_of_contents]
            list_of_names = list_of_names if isinstance(list_of_names, list) else [list_of_names]
            list_of_dates = list_of_dates if isinstance(list_of_dates, list) else [list_of_dates]

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
            return children, {'display': 'none'}, {'display': 'none'}

        # If no files are uploaded, don't update the upload interface or the loading state
        return [], {'display': 'none'}, no_update
    
    @app.callback(
        [Output('ug-enrolment-content', 'style'),
         Output('pgt-enrolment-content', 'style')],
        [Input('student-enrolment-dropdown', 'value')]
    )
    def dropdown_student_enrolment(level_of_study):
        if level_of_study == 'ug':
            return {'display': 'block'}, {'display': 'none'}
        elif level_of_study == 'pgt':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return no_update, no_update
        
    @app.callback(
    Output('year-of-course-dropdown', 'options'),
    Input('level-of-study-dropdown', 'value')
    )
    def set_year_options(level_of_study):
        if level_of_study == 'ug':
            return [{'label': f'Year {i}', 'value': str(i)} for i in range(0, 6)]
        elif level_of_study == 'pgt':
            return [{'label': f'Year {i}', 'value': str(i)} for i in range(1, 3)]
    
    years_of_course = {
        'UG': range(0, 6),  # Year 0 to Year 5 for Undergraduates
        'PGT': range(1, 3)  # Year 1 to Year 2 for Postgraduates
    }
    
    @app.callback(
    [Output(f'{level.lower()}-year-{year}', 'style') for level in ['UG', 'PGT'] for year in years_of_course[level]],
    Input('level-of-study-dropdown', 'value'),
    Input('year-of-course-dropdown', 'value')
    )
    def show_graph(level_of_study, year_of_course):
        
        visibility = {}
        for level in ['UG', 'PGT']:
            for year in years_of_course[level]:
                element_id = f'{level.lower()}-year-{year}'
                if level.lower() == level_of_study and str(year) == str(year_of_course):
                    visibility[element_id] = {'display': 'block'}
                else:
                    visibility[element_id] = {'display': 'none'}

        # Generate the output list with the correct length
        output = [visibility.get(f'{level.lower()}-year-{year}', {'display': 'none'}) for level in ['UG', 'PGT'] for year in years_of_course[level]]
        return output
    