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
    students_q4 = df[df['Quarter'] == 4]
    total_students = students_q4['User'].nunique()

    #Average Attendance
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

def calculate_ug_student_enrolment(df):
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
    
    # Filter for UG students in the 4th Quarter
    ug_students_q4 = df[(df['Level of Study'] == 'UG') & (df['Quarter'] == 4)]

    # Total students per course
    total_ug_students_per_course = ug_students_q4.groupby('Course Code')['User'].nunique().to_dict()

    # Total students per year by course
    total_ug_students_per_year_by_course = {'Year 0': [], 'Year 1': [], 'Year 2': [], 'Year 3': [], 'Year 4': [], 'Year 5': []}

    # Iterate through the courses to get counts per year
    for course in ug_students_q4['Course Code'].unique():
        course_data = ug_students_q4[ug_students_q4['Course Code'] == course]
        for year in range(6):  # Adjusted to include Year 0 to Year 5
            count = course_data[course_data['Year of Course'] == year]['User'].nunique()
            total_ug_students_per_year_by_course[f'Year {year}'].append(count)

    ug_enrolment_result = {
        'total_ug_students_per_course': total_ug_students_per_course,
        'total_ug_students_per_year_by_course': total_ug_students_per_year_by_course
    }
    return ug_enrolment_result

def calculate_pgt_student_enrolment(df):
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
    
    # Filter for PGT students in the 4th Quarter
    pgt_students_q4 = df[(df['Level of Study'] == 'PGT') & (df['Quarter'] == 4)]

    # Total PGT students per course
    total_pgt_students_per_course = pgt_students_q4.groupby('Course Code')['User'].nunique().to_dict()

    # Total PGT students for the year is simply the count of unique students in the PGT filter
    total_pgt_students_per_year_by_course = pgt_students_q4['User'].nunique()

    # Building the result dictionary
    pgt_enrolment_result = {
        'total_pgt_students_per_course': total_pgt_students_per_course,
        'total_pgt_students_per_year_by_course': total_pgt_students_per_year_by_course
    }
    return pgt_enrolment_result

def calculate_ug_attendance_rate(df):
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

    ug_students = df[(df['Level of Study'] == 'UG')]

    ug_attendance = {}

    for course_code, group in ug_students.groupby(['Course Code', 'Year of Course']):
        course_attendance = group.pivot_table(
            index='Quarter',
            values='% Attendance',
            aggfunc='mean'
        ).to_dict()

        for course_code, group in ug_students.groupby(['Course Code', 'Year of Course']):
            course_attendance = group.pivot_table(
                index='Quarter',
                values='% Attendance',
                aggfunc='mean'
            )['% Attendance'].to_dict() # Directly access the '% Attendance' to get a dictionary of quarters to attendance values.

            # Multiply each quarter's attendance by 100 to convert to percentage
            course_attendance = {quarter: attendance * 100 for quarter, attendance in course_attendance.items()}
            
            # Calculate the average attendance
            if course_attendance:  # Ensure the dictionary is not empty
                average_attendance = sum(course_attendance.values()) / len(course_attendance)
                ug_attendance[course_code] = {
                    'attendance_by_quarter': course_attendance,
                    'average_attendance': average_attendance
                }

    return ug_attendance

def calculate_pgt_attendance_rate(df):
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

    pgt_students = df[(df['Level of Study'] == 'PGT')]

    pgt_attendance = {}

    for course_code, group in pgt_students.groupby(['Course Code', 'Year of Course']):
        course_attendance = group.pivot_table(
            index='Quarter',
            values='% Attendance',
            aggfunc='mean'
        ).to_dict()

        for course_code, group in pgt_students.groupby(['Course Code', 'Year of Course']):
            course_attendance = group.pivot_table(
                index='Quarter',
                values='% Attendance',
                aggfunc='mean'
            )['% Attendance'].to_dict() # Directly access the '% Attendance' to get a dictionary of quarters to attendance values.

            # Multiply each quarter's attendance by 100 to convert to percentage
            course_attendance = {quarter: attendance * 100 for quarter, attendance in course_attendance.items()}
            
            # Calculate the average attendance
            if course_attendance:  # Ensure the dictionary is not empty
                average_attendance = sum(course_attendance.values()) / len(course_attendance)
                pgt_attendance[course_code] = {
                    'attendance_by_quarter': course_attendance,
                    'average_attendance': average_attendance
                }

    return pgt_attendance