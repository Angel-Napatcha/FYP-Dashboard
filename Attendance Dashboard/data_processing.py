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
    total_students = df['User'].nunique()
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
