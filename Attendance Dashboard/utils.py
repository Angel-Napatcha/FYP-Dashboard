import os
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
import io
import pandas as pd
import datetime
from data_processing import calculate_summary_statistics, calculate_ug_student_enrolment, calculate_pgt_student_enrolment

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join('uploaded_files', name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def create_summary_section(df):
    # Call the processing function
    summary_data = calculate_summary_statistics(df)

    # Create a layout to display processed data using Bootstrap components
    summary_content = dbc.Row([
        dbc.Col(
            className='summary-card',
            children=[
                html.H3(['Total', html.Br(), 'Students'], className='summary-title'),
                html.H3(f"{summary_data['total_students']}", className='summary-value'),
                html.P(
                    [
                        html.Span(f"{summary_data['dropout_rate']:.2f}%", style={'color': 'red'}), 
                        " dropout rate"
                    ],
                    className='summary-small'
                )
            ],
            lg=4, md=6
        ),
        dbc.Col(
            className='summary-card',
            children=[
                html.H3('Average Attendance Rate', className='summary-title'),
                html.H3(f"{summary_data['average_attendance']:.2f}%", className='summary-value')
            ],
            lg=4, md=6
        ),
        dbc.Col(
            className='summary-card',
            children=[
                html.H3(
                    [
                        'Course with ', 
                        html.Span('Highest', style={'color': 'green'}), 
                        ' Attendance Rate'
                    ], 
                    className='summary-title'
                ),
                html.H3(summary_data['course_with_highest_attendance'][0], className='summary-value'),
                html.P(
                    [
                        html.Span(f"{summary_data['course_with_highest_attendance'][1]:.2f}%", style={'color': 'green'}), 
                        " average"
                    ],
                    className='summary-small'
                )
            ],
            lg=4, md=6
        ),
        dbc.Col(
            className='summary-card',
            children=[
                html.H3(
                    [
                        'Course with ', 
                        html.Span('Lowest', style={'color': 'red'}), 
                        ' Attendance Rate'
                    ], 
                    className='summary-title'
                ),
                html.H3(summary_data['course_with_lowest_attendance'][0], className='summary-value'),
                html.P(
                    [
                        html.Span(f"{summary_data['course_with_lowest_attendance'][1]:.2f}%", style={'color': 'red'}), 
                        " average"
                    ],
                    className='summary-small'
                )
            ],
            lg=4, md=6
        ),
        dbc.Col(
            className='summary-card',
            children=[
                html.H3('Average Submission Rate', className='summary-title'),
                html.H3(f"{summary_data['average_submission_rate']:.2f}%", className='summary-value')
            ],
            lg=4, md=6
        )
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
    
    return summary_section

def create_ug_enrolment_graph(df):
    ug_enrolment_data = calculate_ug_student_enrolment(df)
            
    data = []
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
            hoverinfo='none',
            hovertemplate='<b>Year:</b> ' + year + '<br><b>Enrolment:</b> %{x}<extra></extra>',
            marker=dict(
                color=next(color_iterator, 'default_color')  # Cycles through the color list
            )
        )
        
        data.append(trace)

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
            'range': [0, 225]  
            },
        # Adjust the space between bars
        bargap=0.30,  # Smaller values mean less space between individual bars
        bargroupgap=0.25,
        height=1300,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=50,  # Left margin
            r=30,  # Right margin
            t=15,  # Top margin
            b=15,  # Bottom margin
        ),
            showlegend=False
    )

    ug_enrolment_figure = go.Figure(data=data, layout=layout)

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
    
    return ug_enrolment_graph, ug_enrolment_legend

def create_pgt_enrolment_graph(df):
    
    pgt_enrolment_data = calculate_pgt_student_enrolment(df)
            
    data = []

    color = '#478DB8'
    
    # 'total_pgt_students_per_course' would be a dictionary with course codes as keys and student counts as values
    courses = list(pgt_enrolment_data['total_pgt_students_per_course'].keys())
    student_counts = list(pgt_enrolment_data['total_pgt_students_per_course'].values())
    
    trace = go.Bar(
        name='Year 1',
        x=student_counts,
        y=courses,
        orientation='h',
        text=student_counts,
        textposition='outside', 
        textfont=dict( 
            family='sans-serif',
        ),
        hoverinfo='none',
        hovertemplate='<b>Year:</b> Year 1<br><b>Enrolment:</b> %{x}<extra></extra>',
        marker=dict(
            color=color
        )
    )
        
    data.append(trace)

    layout = go.Layout(
        barmode='group',
        yaxis={
            'automargin': True,
            'autorange': 'reversed',
            'tickfont': {
                'family': 'sans-serif',
                'size': 12
            },
        },
        xaxis={
            'range': [0, 50]  
            },
        bargap=0.30, 
        bargroupgap=0.25,
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=50,  # Left margin
            r=30,  # Right margin
            t=15,  # Top margin
            b=15,  # Bottom margin
        ), # Adjust bottom margin to accommodate the legend
            showlegend=False
    )

    pgt_enrolment_figure = go.Figure(data=data, layout=layout)

    # The part of the layout to display the graph
    pgt_enrolment_graph = dcc.Graph(
        id='pgt-enrolment-graph',
        figure=pgt_enrolment_figure, 
        style={
        'maxHeight': '350px',  # Adjust the max height as needed
        'border-radius': '15px',
        'overflowY': 'scroll',
        'width': '100%'
    })

    # Define the custom legend
    pgt_enrolment_legend = html.Div(
        dbc.Row(
            [
                dbc.Col(
                    [
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
            ],
            className='row'
        ),
        style={
            'marginTop': '20px',
            'marginLeft': '0'
        }
    )
    
    return pgt_enrolment_graph, pgt_enrolment_legend

def create_enrolment_section(df):
    ug_enrolment_graph, ug_enrolment_legend = create_ug_enrolment_graph(df)
    pgt_enrolment_graph, pgt_enrolment_legend = create_pgt_enrolment_graph(df)
    
    enrolment_content = html.Div(
        [
            dbc.Row(
                html.H6("Student Enrolment", style={
                    'text-align': 'left',
                    'margin-bottom': '1em',
                    'margin-top': '0.5em'
                }),
                justify="start",
                align="center"
            ),
            dbc.Row(
                dcc.Dropdown(
                    id='student-enrolment-toggle',
                    options=[
                        {'label': 'UG', 'value': 'ug'},
                        {'label': 'PGT', 'value': 'pgt'}
                    ],
                    value='ug',
                    clearable=False, 
                    className='custom-dropdown', 
                ),
                justify="start",
                align="center",
                style={
                    'margin-bottom': '1em'
                }
            ),
            html.Div(
                [
                    ug_enrolment_graph,  # The graph itself
                    ug_enrolment_legend,  # The custom legend directly below the graph
                ],
                id='ug-enrolment-content',  # Add an ID for UG content
                style={'display': 'block'}  # Set initial display to 'block'
            ),
            html.Div(
                [
                    pgt_enrolment_graph,
                    pgt_enrolment_legend
                ],
                id='pgt-enrolment-content',  # Add an ID for PGT content
                style={'display': 'none'}  # Set initial display to 'none'
            )
        ],
        className='enrolment-container'
    )
    return enrolment_content

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
        return html.Div(['This file type is not supported. Please upload an Excel file.'])

    try:
        if 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            
            summary_section = create_summary_section(df)
            enrolment_section = create_enrolment_section(df)
            
            return html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')),
                summary_section,
                enrolment_section,
            ], style={'padding-left': '20px', 'padding-top': '20px'})
    
    except Exception as e:
        return html.Div(['There was an error processing this file: {}'.format(e)])