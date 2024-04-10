import os
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
import pandas as pd
from data_processing import calculate_summary_statistics, calculate_student_enrolment, calculate_attendance_rate, calculate_submission_rate

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
                html.H6("Students Enrolment", style={
                    'text-align': 'left',
                    'margin-bottom': '1em',
                    'margin-top': '0.5em'
                }),
                justify="start",
                align="center"
            ),
            dbc.Row(
                dcc.Dropdown(
                    id='student-enrolment-dropdown',
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
    attendance_rates = calculate_attendance_rate(df, level_of_study, year_of_course)
    courses = [course_code[0] for course_code in attendance_rates.keys()]
    quarters = ['Week 1-3', 'Week 4-6', 'Week 6-9', 'Week 9-12']
    num_quarters = len(quarters)
    y_data = [list(course_data['attendance_by_quarter'].values()) for course_data in attendance_rates.values()]
    average_attendance = [course_data['average_attendance'] for course_data in attendance_rates.values()]
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
    graph_width = max(325, len(courses) * 85)

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
            'width': '100%',
            'maxWidth': '26.15em',  # Ensures the graph width is dynamically set
        }
    )

    return attendance_graph

def create_attendance_section(df):
    levels_of_study = ['UG', 'PGT']
    years_of_course = {
        'UG': range(0, 6),  # Year 0 to Year 5 for Undergraduates
        'PGT': range(1, 3)  # Year 1 to Year 2 for Postgraduates
    }

    # Prepare graph containers by level and year
    graph_containers = {}
    for level in levels_of_study:
        for year in years_of_course[level]:
            graph_id = f'{level.lower()}-year-{year}-attendance'
            attendance_graph = create_attendance_graph(df, level, year)
            # Each graph is placed in separate columns
            graph_containers[graph_id] = html.Div(attendance_graph, id=graph_id, style={'display': 'none'})
    
    # Dropdowns for selecting level of study and year of course
    level_of_study_dropdown = dcc.Dropdown(
        id='attendance-level-of-study-dropdown',
        options=[{'label': level, 'value': level.lower()} for level in levels_of_study],
        value='ug',
        clearable=False,
        searchable=False,
        className='custom-dropdown',
    )

    year_of_course_dropdown = dcc.Dropdown(
        id='attendance-year-of-course-dropdown',
        options=[],  # Options will be set by callback based on selected level of study
        clearable=False,
        searchable=False,
        className='year-dropdown'
    )
   
    colors = ['#7252A7', '#9099FF', '#6EB1FF', '#9CDBFF']
    num_quarters = 4
    
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
    
    # Combining all components into the content section
    attendance_content = html.Div([
        html.Div([
            level_of_study_dropdown,
            year_of_course_dropdown
        ], className='dropdown-row'),
        html.Div(
            attendance_legend,
            className='attendance-legend'
        ),
        dbc.Col(
            html.Div(
                list(graph_containers.values()),
                className='attendance-submission-graph-wrapper'
            ),
            width=12
        )
    ], className='attendance-submission-content')
    
    # Overall section including the header
    attendance_section = html.Div([
        dbc.Row(html.H6("Attendance Rates", style={
            'text-align': 'left', 'margin-bottom': '1em', 'margin-top': '0.5em'
        }), justify="start", align="center"),
        attendance_content
    ])

    return attendance_section

def create_submission_graph(df, level_of_study, year_of_course):
    # Data preparation
    submission_rates = calculate_submission_rate(df, level_of_study, year_of_course)
    courses = [course_code for course_code in submission_rates.keys()]
    average_submissions = [course_data['Average Submission Rate'] for course_data in submission_rates.values()]
    bar_color = '#2F4CFF'  # Uniform color for all bars

    # Constants for bar dimensions
    bar_width = 0.25   # Wider bar for better visibility since there's only one bar per course

    # Calculate x positions for each bar
    x_positions = [i for i, _ in enumerate(courses)]

    # Plotting
    traces = []
    for i, course in enumerate(courses):
        traces.append(go.Bar(
            x=[x_positions[i]],
            y=[average_submissions[i]],
            name=course,
            marker_color=bar_color,
            width=bar_width,
            hovertemplate=f'<b>Submission Rate:</b> {average_submissions[i]:.2f}%<extra></extra>', 
        ))

    # Calculate dynamic width of the graph
    graph_width = max(300, len(courses) * (bar_width + 65))

    # Layout configuration
    layout = go.Layout(
        yaxis=dict(
            title='Submission (%)',
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
            tickvals=x_positions,
            ticktext=courses,
        ),
        barmode='group',
        height=210,
        showlegend=False,
        plot_bgcolor='#F7F7F7',
        margin=dict(l=75, r=20, t=35, b=35),
        autosize=False,
        width=graph_width  # Dynamically adjusted width
    )

    submission_figure = go.Figure(data=traces, layout=layout)

    # Create the dcc.Graph object to render in Dash
    submission_graph = dcc.Graph(
        id='submission-graph',
        figure=submission_figure,
        style={
            'border-radius': '15px',
            'overflowX': 'auto',  # Allows horizontal scrolling if needed
            'width': '100%',
            'maxWidth': '26.15em',  # Ensures the graph width is dynamically set
        }
    )

    return submission_graph

def create_submission_section(df):
    levels_of_study = ['UG', 'PGT']
    years_of_course = {
        'UG': range(0, 6),  # Year 0 to Year 5 for Undergraduates
        'PGT': range(1, 3)  # Year 1 to Year 2 for Postgraduates
    }

    # Prepare graph containers by level and year
    graph_containers = {}
    for level in levels_of_study:
        for year in years_of_course[level]:
            graph_id = f'{level.lower()}-year-{year}-submission'
            submission_graph = create_submission_graph(df, level, year)
            # Each graph is placed in separate columns
            graph_containers[graph_id] = html.Div(submission_graph, id=graph_id, style={'display': 'none'})
    
    # Dropdowns for selecting level of study and year of course
    level_of_study_dropdown = dcc.Dropdown(
        id='submission-level-of-study-dropdown',
        options=[{'label': level, 'value': level.lower()} for level in levels_of_study],
        value='ug',
        clearable=False,
        searchable=False,
        className='custom-dropdown'
    )

    year_of_course_dropdown = dcc.Dropdown(
        id='submission-year-of-course-dropdown',
        options=[],  # Options will be set by callback based on selected level of study
        value='1',
        clearable=False,
        searchable=False,
        className='year-dropdown'
    )
    
    submission_content = html.Div([
        html.Div([
            level_of_study_dropdown,
            year_of_course_dropdown
        ], className='dropdown-row'),
        dbc.Col(
            html.Div(
                list(graph_containers.values()),
                className='attendance-submission-graph-wrapper'
            ),
            width=12
        )
    ], className='attendance-submission-content')
    
    # Overall section including the header
    submission_section = html.Div([
        dbc.Row(html.H6("Submission Rates", style={
            'text-align': 'left', 'margin-bottom': '1em', 'margin-top': '0.5em'
        }), justify="start", align="center"),
        submission_content
    ])
    
    return submission_section