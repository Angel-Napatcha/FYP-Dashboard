from dash.dependencies import Input, Output, State
from dash import html, no_update
from sections import save_file
from parse_contents import parse_contents

def register_callbacks(app):
    # Callback for processing and displaying uploaded Excel file
    @app.callback(
        Output('output-data-upload', 'children'),
        Output('loading-state', 'style'), 
        Output('upload-data', 'style'),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'), State('upload-data', 'last_modified')]
    )
    def update_output(list_of_contents, list_of_names, list_of_dates):
        # Check if there are any files uploaded
        if list_of_contents is not None:
            # Ensure all inputs are treated as lists for consistency, even if a single file is uploaded
            list_of_contents = list_of_contents if isinstance(list_of_contents, list) else [list_of_contents]
            list_of_names = list_of_names if isinstance(list_of_names, list) else [list_of_names]
            list_of_dates = list_of_dates if isinstance(list_of_dates, list) else [list_of_dates]

            children = []
            # Process file uploaded
            for content, name, date in zip(list_of_contents, list_of_names, list_of_dates):
                # Validate file type
                if not (name.endswith('.xls') or name.endswith('.xlsx')):
                    children.append(html.Div([
                        f'File "{name}" is not an Excel file and was not uploaded.'
                    ]))
                else:
                    # Process valid Excel file and add to the display
                    child = parse_contents(content, name, date)
                    children.append(child)
                    save_file(name, content)
                    
            return children, {'display': 'none'}, {'display': 'none'}

        return [], {'display': 'none'}, no_update
    
    # Callback for updating content based on selected student enrolment level
    @app.callback(
        [Output('ug-enrolment-content', 'style'),
         Output('pgt-enrolment-content', 'style')],
        [Input('student-enrolment-dropdown', 'value')]
    )
    def dropdown_student_enrolment(level_of_study):
        # Show or hide content based on user selection in the dropdown
        if level_of_study == 'ug':
            return {'display': 'block'}, {'display': 'none'}
        elif level_of_study == 'pgt':
            return {'display': 'none'}, {'display': 'block'}
        else:
            return no_update, no_update # No change if the selection is unchanged
    
    years_of_course = {
            'UG': range(0, 6),
            'PGT': range(1, 3)
        }
    
    # Callback for setting options in a dropdown based on level of study
    @app.callback(
    Output('attendance-year-of-course-dropdown', 'options'),
    Output('attendance-year-of-course-dropdown', 'value'),  
    Input('attendance-level-of-study-dropdown', 'value')
    )
    def set_year_options(level_of_study):
        # Define dropdown options and default value based on level of study
        if level_of_study == 'ug':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['UG']]
            default_year = '1'
        elif level_of_study == 'pgt':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['PGT']]
            default_year = '1'

        return year_options, default_year
    
    # Generates attendance graph based on available study levels and years
    @app.callback(
    [Output(f'{level.lower()}-year-{year}-attendance', 'style') for level in ['UG', 'PGT'] for year in years_of_course[level]],
    Input('attendance-level-of-study-dropdown', 'value'),
    Input('attendance-year-of-course-dropdown', 'value')
    )
    def show_attendance_graph(level_of_study, year_of_course):
        visibility = {}
        # Update visibility for each graph element based on the selected study level and year
        for level in ['UG', 'PGT']:
            for year in years_of_course[level]:
                element_id = f'{level.lower()}-year-{year}-attendance'
                if level.lower() == level_of_study and str(year) == str(year_of_course):
                    visibility[element_id] = {'display': 'block'}
                else:
                    visibility[element_id] = {'display': 'none'}

        return [visibility.get(f'{level.lower()}-year-{year}-attendance', {'display': 'none'}) for level in ['UG', 'PGT'] for year in years_of_course[level]]
        
    # Callback for setting options in a dropdown based on level of study
    @app.callback(
    Output('submission-year-of-course-dropdown', 'options'),
    Output('submission-year-of-course-dropdown', 'value'),  
    Input('submission-level-of-study-dropdown', 'value')
    )
    # Define dropdown options and default value based on level of study
    def set_year_options(level_of_study):
        if level_of_study == 'ug':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['UG']]
            default_year = '1'
        elif level_of_study == 'pgt':
            year_options = [{'label': f'Year {i}', 'value': str(i)} for i in years_of_course['PGT']]
            default_year = '1' 

        return year_options, default_year
    
    # Generates attendance graph based on available study levels and years
    @app.callback(
    [Output(f'{level.lower()}-year-{year}-submission', 'style') for level in ['UG', 'PGT'] for year in years_of_course[level]],
    Input('submission-level-of-study-dropdown', 'value'),
    Input('submission-year-of-course-dropdown', 'value')
    )
    def show_submission_graph(level_of_study, year_of_course):
        visibility = {}
        # Update visibility for each graph element based on the selected study level and year
        for level in ['UG', 'PGT']:
            for year in years_of_course[level]:
                element_id = f'{level.lower()}-year-{year}-submission'
                if level.lower() == level_of_study and str(year) == str(year_of_course):
                    visibility[element_id] = {'display': 'block'}
                else:
                    visibility[element_id] = {'display': 'none'}

        return [visibility.get(f'{level.lower()}-year-{year}-submission', {'display': 'none'}) for level in ['UG', 'PGT'] for year in years_of_course[level]]
    
    # Generates UG concerning students table based on available years
    @app.callback(
    [Output(f'ug-year-{year}-table', 'style') for year in range(6)],
    [Input('ug-year-of-course-dropdown', 'value')]
    )
    def show_ug_tables(selected_year):
        # Generate a dictionary to control the visibility of each UG table
        visibility = {f'ug-year-{year}-table': {'display': 'block' if year == selected_year else 'none'} for year in range(6)}
        return [visibility[f'ug-year-{year}-table'] for year in range(6)]

    # Generates PGT concerning students table based on available years
    @app.callback(
        [Output(f'pgt-year-{year}-table', 'style') for year in range(1, 3)],
        [Input('pgt-year-of-course-dropdown', 'value')]
    )
    def show_pgt_tables(selected_year):
        # Generate a dictionary to control the visibility of each PGT table
        visibility = {f'pgt-year-{year}-table': {'display': 'block' if year == selected_year else 'none'} for year in range(1, 3)}
        return [visibility[f'pgt-year-{year}-table'] for year in range(1, 3)]
