import pandas as pd


def calculate_summary_statistics(df):
    # Check if necessary columns exist
    required_columns = ['User', '% Attendance', 'Submitted', 'Assessments', 'Course Code', 'Quarter']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError("Missing required column: {}".format(column))
            
    # Ensure that the columns are in the correct format
    df['% Attendance'] = pd.to_numeric(df['% Attendance'], errors='coerce')
    df['Submitted'] = pd.to_numeric(df['Submitted'], errors='coerce')
    df['Assessments'] = pd.to_numeric(df['Assessments'], errors='coerce')
    df['Quarter'] = pd.to_numeric(df['Quarter'], errors='coerce')
    
    # Drop rows with NaN values that were created due to coercion errors
    df = df.dropna(subset=['% Attendance', 'Submitted', 'Assessments', 'Quarter'])

    # Total Students
    current_students = df[df['Quarter'] == 4]
    total_students = current_students['User'].nunique()

    # Average Attendance
    average_attendance = df['% Attendance'].mean() * 100  # Convert to percentage
    
    # Dropout Rate
    total_enrolled = len(df['User'].unique())
    total_active = len(df.loc[df['% Attendance'] > 0, 'User'].unique())
    dropout_rate = 100 * (1 - (total_active / total_enrolled))
    
    # Average Submission Rate
    total_submissions = df['Submitted'].sum()
    total_assessments = df['Assessments'].sum()
    average_submission_rate = (total_submissions / total_assessments) * 100 if total_assessments > 0 else 0
    
    # Course Attendance
    course_attendance = df.groupby('Course Code')['% Attendance'].mean() * 100
    course_with_highest_attendance = course_attendance.idxmax(), course_attendance.max()
    course_with_lowest_attendance = course_attendance.idxmin(), course_attendance.min()

    # Prepare the result dictionary
    summary_result = {
        'total_students': total_students,
        'dropout_rate': dropout_rate,
        'average_attendance': average_attendance,
        'average_submission_rate': average_submission_rate,
        'course_with_highest_attendance': course_with_highest_attendance,
        'course_with_lowest_attendance': course_with_lowest_attendance,
    }

    return summary_result

def calculate_student_enrolment(df, level_of_study):
    # Check if necessary columns exist
    required_columns = ['User', 'Level of Study', 'Year of Course', 'Course Code', 'Quarter']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    # Ensure that the columns are in the correct format
    df['Year of Course'] = pd.to_numeric(df['Year of Course'], errors='coerce')
    df['Quarter'] = pd.to_numeric(df['Quarter'], errors='coerce')
    
    # Drop rows with NaN values that were created due to coercion errors
    df = df.dropna(subset=['Year of Course', 'Quarter'])
    
    # Filter for students in the 4th Quarter based on the student type
    students_q4 = df[(df['Level of Study'] == level_of_study) & (df['Quarter'] == 4)]

    # Total students per course
    total_students_per_course = students_q4.groupby('Course Code')['User'].nunique().to_dict()
    
    # Initialise variable to hold yearly data
    total_students_per_year_by_course = None

    if level_of_study == 'UG':
        # Group by course and year, then count unique users
        grouped_data = students_q4.groupby(['Course Code', 'Year of Course'])['User'].nunique().unstack(fill_value=0)

        # Preparing dictionary to hold total students per year by course
        total_students_per_year_by_course = {'Year ' + str(year): [] for year in range(6)}

        # Iterate over the grouped data to populate the dictionary
        for course, year_data in grouped_data.iterrows():
            for year in range(6):
                total_students_per_year_by_course[f'Year {year}'].append(year_data.get(year, 0))
    else:
        # Group by course and year, then count unique users
        grouped_data = students_q4.groupby(['Course Code', 'Year of Course'])['User'].nunique().unstack(fill_value=0)

        # Preparing dictionary to hold total students per year by course
        total_students_per_year_by_course = {'Year ' + str(year): [] for year in range(1, 3)}

        # Iterate over the grouped data to populate the dictionary
        for course, year_data in grouped_data.iterrows():
            for year in range(1, 3):
                total_students_per_year_by_course[f'Year {year}'].append(year_data.get(year, 0))

    enrolment_result = {
        'total_students_per_course': total_students_per_course,
        'total_students_per_year_by_course': total_students_per_year_by_course
    }
    return enrolment_result

def calculate_attendance_rate(df, level_of_study, year_of_course):
    # Check if necessary columns exist
    required_columns = ['% Attendance', 'Level of Study', 'Year of Course', 'Course Code', 'Quarter']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError("Missing required column: {}".format(column))

    # Ensure that the columns are in the correct format
    df['% Attendance'] = pd.to_numeric(df['% Attendance'], errors='coerce')
    df['Year of Course'] = pd.to_numeric(df['Year of Course'], errors='coerce')
    df['Quarter'] = pd.to_numeric(df['Quarter'], errors='coerce')

    # Drop rows with NaN values that were created due to coercion errors
    df = df.dropna(subset=['% Attendance', 'Year of Course', 'Quarter'])

    # Filter the data frame based on the provided level_of_study and year_of_course
    filtered_df = df[(df['Level of Study'] == level_of_study) & (df['Year of Course'] == year_of_course)]

    attendance_result = {}
    for course_code, group in filtered_df.groupby(['Course Code', 'Year of Course']):
        course_attendance = group.pivot_table(
            index='Quarter',
            values='% Attendance',
            aggfunc='mean'
        )['% Attendance'].to_dict()

        # Multiply each quarter's attendance by 100 to convert to percentage
        course_attendance = {quarter: attendance * 100 for quarter, attendance in course_attendance.items()}

        # Calculate the average attendance
        if course_attendance:
            # Ensure the dictionary is not empty
            average_attendance = sum(course_attendance.values()) / len(course_attendance)
            attendance_result[course_code] = {
                'attendance_by_quarter': course_attendance,
                'average_attendance': average_attendance
            }

    return attendance_result

def calculate_submission_rate(df, level_of_study, year_of_course):
    # Check if necessary columns exist
    required_columns = ['Submitted', 'Assessments', 'Level of Study', 'Year of Course', 'Course Code', 'Quarter']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError("Missing required column: {}".format(column))

    # Ensure that the columns are in the correct format
    df['Submitted'] = pd.to_numeric(df['Submitted'], errors='coerce')
    df['Assessments'] = pd.to_numeric(df['Assessments'], errors='coerce')
    df['Year of Course'] = pd.to_numeric(df['Year of Course'], errors='coerce')
    df['Quarter'] = pd.to_numeric(df['Quarter'], errors='coerce')

    # Drop rows with NaN values that were created due to coercion errors
    df = df.dropna(subset=['Submitted', 'Assessments', 'Year of Course', 'Quarter'])

    # Filter the data frame based on the provided level_of_study and year_of_course
    filtered_df = df[(df['Level of Study'] == level_of_study) & (df['Year of Course'] == year_of_course)]
    
    submission_result = {}
    for course_code, group in filtered_df.groupby('Course Code'):
        total_submissions = group['Submitted'].sum()
        total_assessments = group['Assessments'].sum()
        average_submission_rate = (total_submissions / total_assessments * 100) if total_assessments > 0 else 0
        submission_result[course_code] = {
            'Course Code': course_code,
            'Year of Course': year_of_course,
            'Average Submission Rate': round(average_submission_rate, 2)  # rounding to 2 decimal places for neatness
        }
    
    return submission_result