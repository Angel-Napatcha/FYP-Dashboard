from dash.dependencies import Input, Output, State
from dash import html, no_update, dcc
import dash_bootstrap_components as dbc
from utils import save_file, create_attendance_graph
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
    
    # @app.callback(
    #     Output('stored-data', 'data'),
    #     [Input('upload-data', 'contents')],
    #     [State('upload-data', 'filename')]
    # )
    # def handle_upload(contents, filename):
    #     if contents is not None:
    #         # Assuming you're saving the file and want to pass its filename to the store
    #         path = save_file(filename, contents)  # You'll define how to save the file
    #         return path  # Return the path or filename for the dcc.Store

    #     return no_update 
    
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
    
    # @app.callback(
    # [Output('attendance-graph', 'figure'),
    #  Output('attendance-legend-placeholder', 'children')],
    # [Input('level-of-study-dropdown', 'value'),
    #  Input('year-of-course-dropdown', 'value'),
    #  Input('stored-data', 'data')]  # This is assuming you store the uploaded data in 'stored-data'
    # )
    # def update_attendance_graph(level_of_study, year_of_course, stored_data):
    #     # Here you will need to retrieve your DataFrame using the stored data
    #     # For example, if stored_data is the filename:
    #     df = pd.read_excel(stored_data)

    #     # Convert the year of course to integer
    #     year_of_course = int(year_of_course)

    #     # Now call your function to create the graph and legend
    #     attendance_graph, attendance_legend = create_attendance_graph(df, level_of_study, year_of_course)
        
    #     # Return the updated figure and legend
    #     return attendance_graph, attendance_legend
    