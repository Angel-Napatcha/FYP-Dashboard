import os
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
import io
import pandas as pd
import datetime
from data_processing import calculate_summary_statistics, calculate_student_enrolment_ug, calculate_student_enrolment_pgt

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
            summary_content = dbc.Row([
                    dbc.Col(className='summary-card', children=[
                        html.H3(['Total', html.Br(), 'Students'], className='summary-title'),
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

            summary_section = dbc.Container([
                html.H6("Summary", style={
                    'text-align': 'left',
                    'margin-bottom': '0.25em',
                    'margin-left': '0.5em',
                    'margin-top': '0.5em'
                }),
                dbc.Row(
                    summary_content,
                    justify="center",
                )
            ], fluid=True, className="summary-section")
            
            ug_enrolment_data = calculate_student_enrolment_ug(df)
            
            ug_enrolment_graph_data = []
            cumulative_sums = {key: 0 for key in ug_enrolment_data['total_ug_students_per_course'].keys()}

            colors = ['#7BBC9A', '#478DB8', '#E9BA5D', '#E46E53', '#9C71C6']
            color_iterator = iter(colors)
            
            for year in ug_enrolment_data['total_ug_students_per_year_by_course']:
                year_data = ug_enrolment_data['total_ug_students_per_year_by_course'][year]
                for i, key in enumerate(ug_enrolment_data['total_ug_students_per_course'].keys()):
                    cumulative_sums[key] += year_data[i]

                text_labels = [''] * len(year_data)  # Empty labels for all bar segments

                # Only add the label for the last segment of the stack (assumes chronological order)
                if year == list(ug_enrolment_data['total_ug_students_per_year_by_course'].keys())[-1]:
                    text_labels = [str(cumulative_sums[key]) for key in ug_enrolment_data['total_ug_students_per_course'].keys()]
                
                trace = go.Bar(
                    name=year,
                    x=year_data,
                    y=list(ug_enrolment_data['total_ug_students_per_course'].keys()),
                    orientation='h',
                    text=text_labels,
                    textposition='outside', 
                    textfont=dict( 
                        family='sans-serif',
                    ),
                    marker=dict(
                    color=next(color_iterator, 'default_color')  # Cycles through the color list
                    )
                )
                
                ug_enrolment_graph_data.append(trace)

            layout = go.Layout(
                barmode='stack',
                yaxis={
                    'automargin': True,
                    'autorange': 'reversed',
                    'tickfont': {
                        'family': 'sans-serif',
                        'size': 12
                    },
                },
                xaxis={
                    'range': [0, 220]  
                    },
                # Adjust the space between bars
                bargap=0.30,  # Smaller values mean less space between individual bars
                bargroupgap=0.25,
                height=1250,
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(
                    l=50,  # Left margin
                    r=30,  # Right margin
                    t=15,  # Top margin
                    b=15,  # Bottom margin
                ), # Adjust bottom margin to accommodate the legend
                    showlegend=False
            )

            ug_enrolment_figure = go.Figure(data=ug_enrolment_graph_data, layout=layout)

            # The part of the layout to display the graph
            ug_enrolment_graph = dcc.Graph(
                id='ug-enrolment-graph',
                figure=ug_enrolment_figure, 
                style={
                'maxHeight': '350px',  # Adjust the max height as needed
                'border-radius': '15px',
                'overflowY': 'scroll',
                'width': '100%'
            })
            
            # Define the custom legend with corrected structure for 3 columns
            ug_enrolment_legend = html.Div(
                dbc.Row(
                    [
                        dbc.Col(  # Column for Year 0 and Year 1
                            [
                                html.Div(
                                    [
                                        html.Span(className='legend-circle', style={'backgroundColor': '#7BBC9A'}),
                                        html.Span('Year 0', className='legend-text'),
                                    ],
                                    className='legend-entry'
                                ),
                                html.Div(
                                    [
                                        html.Span(className='legend-circle', style={'backgroundColor': '#478DB8'}),
                                        html.Span('Year 1', className='legend-text'),
                                    ],
                                    className='legend-entry'
                                ),
                            ],
                            className='legend-column', width="auto"
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.Span(className='legend-circle', style={'backgroundColor': '#E9BA5D'}),
                                        html.Span('Year 2', className='legend-text'),
                                    ],
                                    className='legend-entry'
                                ),
                                html.Div(
                                    [
                                        html.Span(className='legend-circle', style={'backgroundColor': '#E46E53'}),
                                        html.Span('Year 3', className='legend-text'),
                                    ],
                                    className='legend-entry'
                                ),
                            ],
                            className='legend-column', width="auto"
                        ),
                        dbc.Col( 
                            [
                                html.Div(
                                    [
                                        html.Span(className='legend-circle', style={'backgroundColor': '#9C71C6'}),
                                        html.Span('Year 4', className='legend-text'),
                                    ],
                                    className='legend-entry'
                                ),
                            ],
                            className='legend-column', width="auto"
                        ),
                    ],
                    className='row'
                ),
                style={
                    'marginTop': '20px',
                    'marginLeft': '0'
                }
            )

            # Create a container for the graph with its custom legend, applying the CSS class
            ug_enrolment_content = html.Div(
                [
                    dbc.Row(html.H6("Student Enrolment", style={
                    'text-align': 'left',
                    'margin-bottom': '4em',
                    'margin-left': '0em',
                    'margin-top': '0.5em'
                })),
                    ug_enrolment_graph,  # The graph itself
                    ug_enrolment_legend,  # The custom legend directly below the graph
                ],
                className='enrolment-container'
            )
            
            # Call the student enrolment function
            pgt_enrolment_data = calculate_student_enrolment_pgt(df)
            
            
            
            total_pgt_students_per_course_str = "Total PGT Students per Course:\n" + "\n".join(f"{course}: {count}" for course, count in pgt_enrolment_data['total_pgt_students_per_course'].items())

            # Since total_pgt_students_per_year_by_course is a single integer, we handle it directly
            total_pgt_students_for_the_year_str = f"Total PGT Students for the Year: {pgt_enrolment_data['total_pgt_students_per_year_by_course']}"

            # Create the content to display
            pgt_enrolment_content = html.Div([
                html.P("PGT Enrolment Statistics", style={'fontWeight': 'bold'}),
                html.P(total_pgt_students_per_course_str.replace("\n", ", "), style={'whiteSpace': 'pre-line'}),
                html.P(total_pgt_students_for_the_year_str, style={'whiteSpace': 'pre-line'})
            ])
            
            return html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')),
                summary_section,
                ug_enrolment_content,
                pgt_enrolment_content
            ], style={'padding-left': '20px', 'padding-top': '20px'})
    
    except Exception as e:
        return html.Div(['There was an error processing this file: {}'.format(e)])