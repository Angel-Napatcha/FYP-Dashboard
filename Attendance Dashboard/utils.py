import os
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
import io
import pandas as pd
import datetime
from data_processing import calculate_summary_statistics, calculate_student_enrolment, calculate_attendance_rate

def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join('uploaded_files', name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def create_summary_cards(df):
    # Call the processing function
    summary_data = calculate_summary_statistics(df)

    # Create a layout to display processed data using Bootstrap components
    summary_content = dbc.Row([
        dbc.Col(
            className='summary-card',
            children=[
                html.H3([
                    'Total', 
                    html.Br(), 
                    'Students'
                ], className='summary-title'),
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
                html.H3([
                    'Average', 
                    html.Br(), 
                    'Attendance Rate'
                ], className='summary-title'),
                html.H3(f"{summary_data['average_attendance']:.2f}%", className='summary-value')
            ],
            lg=4, md=6
        ),
        dbc.Col(
            className='summary-card',
            children=[
                html.H3([
                    'Course with ', 
                    html.Span('Highest', style={'color': 'green'}), 
                    html.Br(),
                    ' Attendance Rate'
                ], 
                className='summary-title'),
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
                html.H3([
                    'Course with ', 
                    html.Span('Lowest', style={'color': 'red'}), 
                    html.Br(),
                    ' Attendance Rate'
                ], 
                className='summary-title'),
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
                html.H3([
                    'Average', 
                    html.Br(), 
                    'Submission Rate'
                ], className='summary-title'),
                html.H3(f"{summary_data['average_submission_rate']:.2f}%", className='summary-value')
            ],
            lg=4, md=6
        )
    ], justify="center")

    return summary_content

def create_summary_section(df):
    summary_content = create_summary_cards(df)
    
    summary_section = dbc.Container([
        html.H6("Summary", style={
            'text-align': 'left',
            'margin-bottom': '0.5em',
            'margin-left': '0.5em',
            'margin-top': '0.75em'
        }),
        dbc.Row(
            summary_content,
            justify="center",
            )
        ], fluid=True, className="summary-container")       
    
    return summary_section

def create_enrolment_graph(df, level_of_study):
    if level_of_study == 'UG':
        colors = ['#7BBC9A', '#478DB8', '#E9BA5D', '#E46E53', '#9C71C6', '#AF7C4F']
        xaxis_range = [-8, 200]
        bar_height = 29
        enrolment_id = 'ug-enrolment-graph'
        year_level = 'Year'
        
    elif level_of_study == 'PGT':
        colors = ['#478DB8', '#E9BA5D']
        xaxis_range = [-2, 50]
        bar_height = 33
        enrolment_id = 'pgt-enrolment-graph'
        year_level = 'Year'

    enrolment_data = calculate_student_enrolment(df, level_of_study)
    num_courses = len(enrolment_data['total_students_per_course'])
    graph_height = num_courses * (bar_height)
    
    data = []
    cumulative_sums = {key: 0 for key in enrolment_data['total_students_per_course'].keys()}
    color_iterator = iter(colors)
    
    for year in enrolment_data['total_students_per_year_by_course']:
        year_data = enrolment_data['total_students_per_year_by_course'][year]
        for i, key in enumerate(enrolment_data['total_students_per_course'].keys()):
            cumulative_sums[key] += year_data[i]

        text_labels = [''] * len(year_data)
        if year == list(enrolment_data['total_students_per_year_by_course'].keys())[-1]:
            text_labels = [str(cumulative_sums[key]) for key in enrolment_data['total_students_per_course'].keys()]
        
        trace = go.Bar(
            name=year,
            x=year_data,
            y=list(enrolment_data['total_students_per_course'].keys()),
            orientation='h',
            text=text_labels,
            textposition='outside', 
            textfont=dict(family='sans-serif'),
            hoverinfo='none',
            hovertemplate=f'<b>{year_level}:</b> ' + year + '<br><b>Enrolment:</b> %{x}<extra></extra>',
            marker=dict(color=next(color_iterator, '#000000'))  # Default to black if colors run out
        )
        data.append(trace)

    layout = go.Layout(
        barmode='stack',
        yaxis={
            'automargin': True,
            'autorange': 'reversed',
        },
        xaxis={
            'range': xaxis_range,
        },
        bargap=0.30,
        bargroupgap=0.25,
        height=graph_height,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=30, t=15, b=15),
        font=dict(family='sans-serif', size=12)  # Default font for the whole layout
    )

    enrolment_figure = go.Figure(data=data, layout=layout)
    enrolment_graph = dcc.Graph(
        id=enrolment_id, 
        figure=enrolment_figure, 
        style={
            'maxHeight': '390px', 
            'border-radius': '15px', 
            'overflowY': 'scroll', 
            'width': '100%'
            }
        )

    # Legends
    year_levels = [f'Year {i}' for i in range(len(colors))]
    legend_entries = []
    for color, year in zip(colors, year_levels):
        legend_entry = html.Div([
            html.Span(className='legend-circle', style={'backgroundColor': color}),
            html.Span(year, className='legend-text')
        ], className='legend-entry')
        legend_entries.append(legend_entry)
    # Arrange entries into columns of two (can be adjusted based on the number of years)
    columns = [dbc.Col(legend_entries[i:i + 2], className='legend-column', width="auto") for i in range(0, len(legend_entries), 2)]
    enrolment_legend = html.Div(dbc.Row(columns, className='row'), style={'marginTop': '20px', 'marginLeft': '0'})
    
    return enrolment_graph, enrolment_legend

def create_enrolment_section(df):
    ug_enrolment_graph, ug_enrolment_legend = create_enrolment_graph(df, 'UG')
    pgt_enrolment_graph, pgt_enrolment_legend = create_enrolment_graph(df, 'PGT')
    
    enrolment_section = html.Div(
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
                    searchable=False,
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
                    ug_enrolment_graph,
                    ug_enrolment_legend, 
                ],
                id='ug-enrolment-content', 
                style={'display': 'block'} 
            ),
            html.Div(
                [
                    pgt_enrolment_graph,
                    pgt_enrolment_legend
                ],
                id='pgt-enrolment-content', 
                style={'display': 'none'} 
            )
        ]
    )
    return enrolment_section

def create_attendance_graph(df, level_of_study, year_of_course):
    # Data preparation
    attendance = calculate_attendance_rate(df, level_of_study, year_of_course)
    courses = [course_code[0] for course_code in attendance.keys()]
    quarters = ['Week 1-3', 'Week 4-6', 'Week 6-9', 'Week 9-12']
    num_quarters = len(quarters)
    y_data = [list(course_data['attendance_by_quarter'].values()) for course_data in attendance.values()]
    average_attendance = [course_data['average_attendance'] for course_data in attendance.values()]
    colors = ['#7252A7', '#9099FF', '#6EB1FF', '#9CDBFF']

    # Constants for bar dimensions and spacing
    bar_width = 0.1   # Fixed width for each bar
    space_between_bars = 0.03
    space_between_groups = 0.15

    # Calculate x positions for each bar and adjust the graph width
    x_positions = []
    current_x = 0
    for i in range(len(courses)):
        group_positions = []
        for j in range(num_quarters):
            group_positions.append(current_x + j * (bar_width + space_between_bars))
        x_positions.append(group_positions)
        current_x += (num_quarters * (bar_width + space_between_bars) - space_between_bars) + space_between_groups

    # Calculate dynamic width of the graph
    graph_width = max(275, len(courses) * 80)

    # Plotting
    traces = []
    for i, course in enumerate(courses):
        for j, quarter in enumerate(quarters):
            traces.append(go.Bar(
                x=[x_positions[i][j]],
                y=[y_data[i][j]],
                name=quarter,
                marker_color=colors[j],
                width=bar_width,
                hovertemplate=f'<b>Week:</b> {quarter}<br><b>Attendance Rate:</b> {y_data[i][j]:.2f}%<extra></extra>', 
            ))

    # Line chart for average attendance
    traces.append(go.Scatter(
        x=[sum(pos)/len(pos) for pos in x_positions],
        y=average_attendance,
        mode='lines+markers',
        name='Average Attendance',
        marker=dict(color='#FFA41B', size=8),
        line=dict(color='#FFA41B'),
        hovertemplate='<b>Average Attendance:</b> %{y:.2f}%<extra></extra>',
    ))
    
    # Calculate dynamic range for x-axis
    x_axis_range = [min(x_positions[0]) - bar_width - 0.1, max(x_positions[-1]) + bar_width]

    # Layout configuration
    layout = go.Layout(
        yaxis=dict(
            title='Attendance (%)',
            titlefont=dict(
                family='sans-serif',
            ),
            tickfont=dict(
                family='sans-serif',             
            ),
            range=[0, 100],
            dtick=25,
            automargin=True 
        ),
        xaxis=dict(
            tickfont=dict(
                family='sans-serif',
                size=12,             
            ),
            tickvals=[sum(pos) / len(pos) for pos in x_positions],
            ticktext=courses,
            range=x_axis_range,
        ),
        barmode='group',
        height=210,
        showlegend=False,
        plot_bgcolor='#F7F7F7',
        margin=dict(l=75, r=20, t=35, b=35),
        autosize=False,
        width=graph_width  # Dynamically adjusted width
    )

    attendance_figure = go.Figure(data=traces, layout=layout)

    # Create the dcc.Graph object to render in Dash
    attendance_graph = dcc.Graph(
        id='attendance-graph',
        figure=attendance_figure,
        style={
            'border-radius': '15px',
            'overflowX': 'auto',  # Allows horizontal scrolling if needed
            'overflowY': 'hidden',  # Prevents vertical scrolling
            'width': '100%',
            'maxWidth': '25.5em',  # Ensures the graph width is dynamically set
        }
    )
    
    attendance_legend = html.Div(
        [html.Div(
            [
                html.Div(style={'background-color': colors[i], 'width': '10px', 'height': '10px', 'border-radius': '50%'}, className='legend-circle'),
                html.Div(f'Week {i*3+1}-{i*3+3}', className='legend-text')
            ],
            className='legend-entry'
        ) for i in range(num_quarters)],
        className='legend-column'
    )

    return attendance_graph, attendance_legend

def create_attendance_section(df):
    
    attendance_graph, attendance_legend = create_attendance_graph(df, 'UG', 1)
    
    attendance_content = html.Div(
        [
            html.Div(
                attendance_legend,
                className='attendance-legend'
            ),
            dbc.Col(
                html.Div(
                    attendance_graph,
                    className='attendance-graph-wrapper'
                )
            ),
        ],
        className='attendance-content'
    )
    
    attendance_section = html.Div(
        [
            dbc.Row(
                html.H6("Student Attendance", style={
                    'text-align': 'left',
                    'margin-bottom': '1em',
                    'margin-top': '0.5em'
                }),
                justify="start",
                align="center"
            ),
            html.Div(
                [
                   attendance_content
                ],
                id='attendance-content', 
                style={'display': 'block'} 
            )
        ],
        className='attedance-container '
    )
            

    return attendance_section

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
            attendance_section = create_attendance_section(df)
            
            return html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')),
                dbc.Row([
                    dbc.Col(summary_section, md=8),  # Use 8 out of 12 columns for the summary
                    dbc.Col(html.Div(), md=4),  # This is to fill the space if you want to maintain the grid layout. Adjust or remove as needed.
                ]),
                dbc.Row([
                    dbc.Col(html.Div(enrolment_section, className="enrolment-container"), md=3),
                    dbc.Col(html.Div(attendance_section, className="attendance-container"), md=5)
                ]),
            ], style={'padding-left': '1.5em', 'padding-right': '1.5em', 'padding-top': '1.5em'})

    except Exception as e:
        return html.Div(['There was an error processing this file: {}'.format(e)])