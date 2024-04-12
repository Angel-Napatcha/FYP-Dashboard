from dash.dependencies import Input, Output, State
from dash import html, no_update
from sections import save_file
from parse_contents import parse_contents

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
    
    years_of_course = {
            'UG': range(0, 6),  # Year 0 to Year 5 for Undergraduates
            'PGT': range(1, 3)  # Year 1 to Year 2 for Postgraduates
        }
    
    @app.callback(
    Output('attendance-year-of-course-dropdown', 'options'),  # for the dropdown options
    Output('attendance-year-of-course-dropdown', 'value'),  
    Input('attendance-level-of-study-dropdown', 'value')
    )
    def set_year_options(level_of_study):
        if level_of_study == 'ug':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['UG']]
            default_year = '1'  # Set the default year to '0' for UG
        elif level_of_study == 'pgt':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['PGT']]
            default_year = '1'  # Set the default year to '1' for PGT

        return year_options, default_year
    
    @app.callback(
    [Output(f'{level.lower()}-year-{year}-attendance', 'style') for level in ['UG', 'PGT'] for year in years_of_course[level]],
    Input('attendance-level-of-study-dropdown', 'value'),
    Input('attendance-year-of-course-dropdown', 'value')
    )
    def show_attendance_graph(level_of_study, year_of_course):
        visibility = {}
        for level in ['UG', 'PGT']:
            for year in years_of_course[level]:
                element_id = f'{level.lower()}-year-{year}-attendance'
                if level.lower() == level_of_study and str(year) == str(year_of_course):
                    visibility[element_id] = {'display': 'block'}
                else:
                    visibility[element_id] = {'display': 'none'}

        # Generate the output list with the correct length
        output = [visibility.get(f'{level.lower()}-year-{year}-attendance', {'display': 'none'}) for level in ['UG', 'PGT'] for year in years_of_course[level]]
        return output
    
    @app.callback(
    Output('submission-year-of-course-dropdown', 'options'),  # for the dropdown options
    Output('submission-year-of-course-dropdown', 'value'),  
    Input('submission-level-of-study-dropdown', 'value')
    )
    def set_year_options(level_of_study):
        if level_of_study == 'ug':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['UG']]
            default_year = '1'  # Set the default year to '1' for UG
        elif level_of_study == 'pgt':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['PGT']]
            default_year = '1'  # Set the default year to '1' for PGT

        return year_options, default_year
    
    @app.callback(
    [Output(f'{level.lower()}-year-{year}-submission', 'style') for level in ['UG', 'PGT'] for year in years_of_course[level]],
    Input('submission-level-of-study-dropdown', 'value'),
    Input('submission-year-of-course-dropdown', 'value')
    )
    def show_submission_graph(level_of_study, year_of_course):
        visibility = {}
        for level in ['UG', 'PGT']:
            for year in years_of_course[level]:
                element_id = f'{level.lower()}-year-{year}-submission'
                if level.lower() == level_of_study and str(year) == str(year_of_course):
                    visibility[element_id] = {'display': 'block'}
                else:
                    visibility[element_id] = {'display': 'none'}

        # Generate the output list with the correct length
        output = [visibility.get(f'{level.lower()}-year-{year}-submission', {'display': 'none'}) for level in ['UG', 'PGT'] for year in years_of_course[level]]
        return output