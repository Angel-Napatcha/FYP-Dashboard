import os
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import base64
from data_processing import calculate_summary_statistics, calculate_student_enrolment, calculate_attendance_rate, calculate_submission_rate
from ml_model import detect_concerning_students


def save_file(name, content):
    # Decode and store a file uploaded with Plotly Dash
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join('uploaded_files', name), "wb") as fp:
        fp.write(base64.decodebytes(data))

def create_summary_cards(df):
    # Call the summary data processing function
    summary_data = calculate_summary_statistics(df)

    # Create a layout to display summary data
    summary_content = dbc.Row([
        # Total students card
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
        # Average attendance rate card
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
        # Course with highest attendance rate card
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
        # Course with lowest attendance rate card
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
        # Average submission rate card
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
        # Summary title
        html.H6("Summary", style={
            'text-align': 'left',
            'margin-bottom': '0.5em',
            'margin-left': '0.5em',
            'margin-top': '0.75em'
        }),
        # Summary content
        dbc.Row(
            summary_content,
            justify="center",
            )
        ], fluid=True, className="summary-container")       
    
    return summary_section

def create_enrolment_graph(df, level_of_study):
    # Determine parameters based on the level of study
    if level_of_study == 'UG':
        colors = ['#FF899E', '#FFBD55', '#E9E16A', '#4ECFA5', '#59BAEF', '#857BB8']
        xaxis_range = [-8, 200]
        bar_height = 29
        enrolment_id = 'ug-enrolment-graph'
        year_level = 'Year'
        year_levels = [f'Year {i}' for i in range(len(colors))]
        
    elif level_of_study == 'PGT':
        colors = ['#FFBD55', '#E9E16A']
        xaxis_range = [-2, 50]
        bar_height = 33
        enrolment_id = 'pgt-enrolment-graph'
        year_level = 'Year'
        year_levels = [f'Year {i+1}' for i in range(len(colors))]

    # Call the student enrolemnt data processing function
    enrolment_data = calculate_student_enrolment(df, level_of_study)
    
    # Determine graph height
    num_courses = len(enrolment_data['total_students_per_course'])
    graph_height = num_courses * (bar_height)
    
    # Prepare data for plotting
    data = []
    cumulative_sums = {key: 0 for key in enrolment_data['total_students_per_course'].keys()}
    color_iterator = iter(colors)
    
    # Iterate over years and courses to create traces for the graph
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

    # Layout configuration
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
        font=dict(family='sans-serif', size=12)
    )

    # Figure configuration
    enrolment_figure = go.Figure(data=data, layout=layout)
    
    # Graph configuration
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

    # Create legends for the graph
    legend_entries = []
    for color, year in zip(colors, year_levels):
        legend_entry = html.Div([
            html.Span(className='legend-circle', style={'backgroundColor': color}),
            html.Span(year, className='legend-text')
        ], className='legend-entry')
        legend_entries.append(legend_entry)
    # Arrange entries into columns of two
    columns = [dbc.Col(legend_entries[i:i + 2], className='legend-column', width="auto") for i in range(0, len(legend_entries), 2)]
    enrolment_legend = html.Div(dbc.Row(columns, className='row'), style={'marginTop': '20px', 'marginLeft': '0'})
    
    return enrolment_graph, enrolment_legend

def create_enrolment_section(df):
    # Create graphs and legends for UG and PGT levels
    ug_enrolment_graph, ug_enrolment_legend = create_enrolment_graph(df, 'UG')
    pgt_enrolment_graph, pgt_enrolment_legend = create_enrolment_graph(df, 'PGT')
    
    # Create the enrolment section layout
    enrolment_section = html.Div(
        [
            dbc.Row(
                # Students enrolment title
                html.H6("Students Enrolment", style={
                    'text-align': 'left',
                    'margin-bottom': '1em',
                    'margin-top': '0.5em'
                }),
                justify="start",
                align="center"
            ),
            dbc.Row(
                # Dropdown menu to switch between UG and PGT
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
            # UG Enrolment Graph and Legend
            html.Div(
                [
                    ug_enrolment_graph,
                    ug_enrolment_legend, 
                ],
                id='ug-enrolment-content', 
                style={'display': 'block'} 
            ),
            # PGT Enrolment Graph and Legend
            html.Div(
                [
                    pgt_enrolment_graph,
                    pgt_enrolment_legend
                ],
                id='pgt-enrolment-content', 
                style={'display': 'none'} 
            )
        ],
        className='enrolment-container'
    )
    return enrolment_section

def create_attendance_graph(df, level_of_study, year_of_course):
    # Call the attendance rate data processing function
    attendance_rates = calculate_attendance_rate(df, level_of_study, year_of_course)
    
    # Determine parameters
    courses = [course_code[0] for course_code in attendance_rates.keys()]
    quarters = ['Week 1-3', 'Week 4-6', 'Week 6-9', 'Week 9-12']
    num_quarters = len(quarters)
    y_data = [list(course_data['attendance_by_quarter'].values()) for course_data in attendance_rates.values()]
    average_attendance = [course_data['average_attendance'] for course_data in attendance_rates.values()]
    colors = ['#7252A7', '#9099FF', '#6EB1FF', '#9CDBFF']

    # Constants for bar dimensions and spacing
    bar_width = 0.1 
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

    # Add markers for average attendance (the lollipop heads)
    traces.append(go.Scatter(
        x=[sum(pos) / len(pos) for pos in x_positions],
        y=average_attendance,
        name= '',
        mode='markers',
        marker=dict(color='#FFA41B', size=10, symbol='circle'),
        hovertemplate='<b>Average Attendance Rate:</b> %{y:.2f}%',
        showlegend=False
    ))

    # Add sticks for the lollipop chart (vertical lines)
    for i, avg in enumerate(average_attendance):
        # Calculate the start and end x-positions for the stick
        x_pos = sum(x_positions[i]) / len(x_positions[i])
        traces.append(go.Scatter(
            x=[x_pos, x_pos],
            y=[0, avg],
            mode='lines',
            marker=dict(color='#FFA41B'),
            showlegend=False,
            hoverinfo='skip',
            hovertemplate=None
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
        width=graph_width 
    )

    # Figure configuration
    attendance_figure = go.Figure(data=traces, layout=layout)

    # Graph configuration
    attendance_graph = dcc.Graph(
        id='attendance-graph',
        figure=attendance_figure,
        style={
            'border-radius': '15px',
            'overflowX': 'auto', 
            'width': '100%',
            'maxWidth': '28.05em', 
        }
    )

    return attendance_graph

def create_attendance_section(df):
    # Define levels of study and corresponding years of courses
    levels_of_study = ['UG', 'PGT']
    years_of_course = {
        'UG': range(0, 6),
        'PGT': range(1, 3) 
    }

    # Prepare graph containers by level and year
    graph_containers = {}
    for level in levels_of_study:
        for year in years_of_course[level]:
            graph_id = f'{level.lower()}-year-{year}-attendance'
            attendance_graph = create_attendance_graph(df, level, year)
            graph_containers[graph_id] = html.Div(attendance_graph, id=graph_id, style={'display': 'none'})
    
    # Dropdowns for selecting level of study
    level_of_study_dropdown = dcc.Dropdown(
        id='attendance-level-of-study-dropdown',
        options=[{'label': level, 'value': level.lower()} for level in levels_of_study],
        value='ug',
        clearable=False,
        searchable=False,
        className='custom-dropdown',
    )
    
    # Dropdowns for selecting year of course
    year_of_course_dropdown = dcc.Dropdown(
        id='attendance-year-of-course-dropdown',
        options=[],
        clearable=False,
        searchable=False,
        className='year-dropdown'
    )
   
    # Define parameters
    colors = ['#7252A7', '#9099FF', '#6EB1FF', '#9CDBFF']
    num_quarters = 4
    
    # Create legends for the graph
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
    
    # Create the attendance section layout
    attendance_section = html.Div([
        html.Div([
            # Students attendance title
            dbc.Row(html.H6("Attendance Rates", style={
                'text-align': 'left', 'margin-bottom': '1em', 'margin-top': '0.5em'
            }), justify="start", align="center"),
            attendance_content
        ], className='attendance-submission-container')
    ])

    return attendance_section

def create_submission_graph(df, level_of_study, year_of_course):
    # Call the submission rate data processing function
    submission_rates = calculate_submission_rate(df, level_of_study, year_of_course)
    
    # Determine parameters
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

    # Figure configuration
    submission_figure = go.Figure(data=traces, layout=layout)

    # Graph configuration
    submission_graph = dcc.Graph(
        id='submission-graph',
        figure=submission_figure,
        style={
            'border-radius': '15px',
            'overflowX': 'auto',  
            'width': '100%',
            'maxWidth': '28.05em',
        }
    )

    return submission_graph

def create_submission_section(df):
     # Define levels of study and corresponding years of courses
    levels_of_study = ['UG', 'PGT']
    years_of_course = {
        'UG': range(0, 6),  
        'PGT': range(1, 3) 
    }

    # Prepare graph containers by level and year
    graph_containers = {}
    for level in levels_of_study:
        for year in years_of_course[level]:
            graph_id = f'{level.lower()}-year-{year}-submission'
            submission_graph = create_submission_graph(df, level, year)
            # Each graph is placed in separate columns
            graph_containers[graph_id] = html.Div(submission_graph, id=graph_id, style={'display': 'none'})
    
    # Dropdowns for selecting level of study
    level_of_study_dropdown = dcc.Dropdown(
        id='submission-level-of-study-dropdown',
        options=[{'label': level, 'value': level.lower()} for level in levels_of_study],
        value='ug',
        clearable=False,
        searchable=False,
        className='custom-dropdown'
    )

    # Dropdowns for selecting year of course
    year_of_course_dropdown = dcc.Dropdown(
        id='submission-year-of-course-dropdown',
        options=[],  # Options will be set by callback based on selected level of study
        value='1',
        clearable=False,
        searchable=False,
        className='year-dropdown'
    )
    
    # Combining all components into the content section
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
    
     # Create the submission section layout
    submission_section = html.Div([
        html.Div([
            # Students submission title
            dbc.Row(html.H6("Submission Rates", style={
                'text-align': 'left', 'margin-bottom': '1em', 'margin-top': '0.5em'
            }), justify="start", align="center"),
            submission_content
        ], className='attendance-submission-container')  # Add the same class as attendance-section
    ])
        
    return submission_section

def create_ug_table(df, year_of_course):
    level_of_study = 'UG'
    ug_students_list = detect_concerning_students(df, level_of_study, year_of_course)
    
    if not ug_students_list.empty:
        return html.Div(
            dash_table.DataTable(
                id='ug-students-table',
                data=ug_students_list.to_dict('records'),
                columns=[
                    {'name': 'Student', 'id': 'User'},
                    {'name': 'Course Code', 'id': 'Course Code'},
                    {'name': 'Attendance Rate (%)', 'id': '% Attendance'},
                    {'name': 'Submission Rate (%)', 'id': 'Submission Rate'},
                ],
                # Inline styles for the table cells
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'backgroundColor': '#FFF',
                    'border': 'none',
                    'font-family': 'sans-serif',
                    'font-size': '12.5px'
                },
                # Inline styles for the table header
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': '#f4f4f4',
                    'fontFamily': 'sans-serif',
                    'fontSize': '12.5px'
                },
                # Conditional styling for odd rows
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}
                ],
                style_as_list_view=True,
            ),
            className='at-risk-table'
        )
    else:
        return html.Div("No at-risk students found for the given criteria.", style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'fontSize': '14px', 'marginTop': '20px'})

def create_pgt_table(df, year_of_course):
    level_of_study = 'PGT'
    pgt_students_list = detect_concerning_students(df, level_of_study, year_of_course)
    
    if not pgt_students_list.empty:
        return html.Div(
            dash_table.DataTable(
                id='pgt-students-table',
                data=pgt_students_list.to_dict('records'),
                columns=[
                    {'name': 'Student', 'id': 'User'},
                    {'name': 'Course Code', 'id': 'Course Code'},
                    {'name': 'Attendance Rate (%)', 'id': '% Attendance'},
                    {'name': 'Submission Rate (%)', 'id': 'Submission Rate'},
                ],
                # Inline styles for the table cells
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'backgroundColor': '#FFF',
                    'border': 'none',
                    'font-family': 'sans-serif',
                    'font-size': '12.5px'
                },
                # Inline styles for the table header
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': '#f4f4f4',
                    'fontFamily': 'sans-serif',
                    'fontSize': '12.5px'
                },
                # Conditional styling for odd rows
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}
                ],
                style_as_list_view=True,
            ),
            className='at-risk-table'  # Assign the CSS class to the Div
        )
    else:
        return html.Div("No at-risk students found for the given criteria.", style={'textAlign': 'center', 'fontFamily': 'sans-serif', 'fontSize': '14px', 'marginTop': '20px'})

def create_concerning_students_section(df):
    years_of_course = {
        'UG': range(0, 6), 
        'PGT': range(1, 3) 
    }
    
    # Prepare containers for UG tables
    ug_table_containers = {}
    for year in years_of_course['UG']:
        graph_id = f'ug-year-{year}-table'
        ug_table = create_ug_table(df, year) 
        ug_table_containers[graph_id] = html.Div(ug_table, id=graph_id, style={'display': 'none'})
    
    ug_year_of_course_dropdown = dcc.Dropdown(
        id='ug-year-of-course-dropdown',
        options=[{'label': 'Year ' + str(year), 'value': year} for year in range(6)],  # Dropdown options corrected
        value=1,
        clearable=False,
        searchable=False,
        className='grey-dropdown'
    )
    
    # Prepare containers for PGT tables
    pgt_table_containers = {}
    for year in years_of_course['PGT']: 
        graph_id = f'pgt-year-{year}-table'
        pgt_table = create_pgt_table(df, year) 
        pgt_table_containers[graph_id] = html.Div(pgt_table, id=graph_id, style={'display': 'none'})
    
    pgt_year_of_course_dropdown = dcc.Dropdown(
        id='pgt-year-of-course-dropdown',
        options=[{'label': f'Year {year}', 'value': year} for year in range(1, 3)], 
        value=1,
        clearable=False,
        searchable=False,
        className='grey-dropdown'
    )
    
    at_risk_students_section = html.Div([
    html.Div([
        dbc.Row(
            html.H6([
                # Title for the section
                html.Span("Concerning Students", style={'color': 'red'}), 
                " Filtered By", 
                html.Br(),  
                "Machine Learning"
            ], style={
                'text-align': 'left',
                'margin-bottom': '1em',
                'margin-top': '0.5em'
            }), justify="start", align="center"
        ),
        # UG section
        html.Div('Undergraduate', className='ug-label'),
        ug_year_of_course_dropdown,
        html.Div(list(ug_table_containers.values()), className='ug-table-container'),
        # PGT section
        html.Div('Postgraduate', className='pgt-label'),
        pgt_year_of_course_dropdown,
        html.Div(list(pgt_table_containers.values()), className='pgt-table-container'),
    ], className='risk-container')
])
    
    return at_risk_students_section