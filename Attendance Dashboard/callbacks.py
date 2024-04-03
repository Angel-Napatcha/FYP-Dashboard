from dash.dependencies import Input, Output, State
from dash import html, no_update
from utils import save_file, parse_contents

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