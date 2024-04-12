import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor  # You can change this to any estimator

def preprocess_data(df):
    # Ensure all required columns are present
    required_columns = ['User', '% Attendance', 'Submitted', 'Assessments', 'Quarter', 'Year of Course', 'Course Code']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    # Convert % Attendance from a fraction to a percentage
    df['% Attendance'] *= 100

    # Impute missing values for necessary columns
    imputer = IterativeImputer(estimator=RandomForestRegressor(), random_state=42, max_iter=3, initial_strategy='median')
    columns_to_impute = ['Submitted', 'Assessments', '% Attendance']
    df[columns_to_impute] = imputer.fit_transform(df[columns_to_impute])

    # Calculate Submission Rate
    df['Submission Rate'] = (df['Submitted'] / df['Assessments']) * 100

    # Scale the relevant columns
    scaler = StandardScaler()
    df['% Attendance Scaled'] = scaler.fit_transform(df[['% Attendance']])
    df['Submission Rate Scaled'] = scaler.fit_transform(df[['Submission Rate']])

    # Aggregate data across all quarters
    df_aggregated = df.groupby('User').agg({
        '% Attendance': lambda x: x.mean().round(2),
        'Submission Rate': lambda x: x.mean().round(2),
        '% Attendance Scaled': 'mean',
        'Submission Rate Scaled': 'mean',
        'Level of Study': lambda x: x.iloc[0],  # Using first valid entry per user
        'Year of Course': 'first',
        'Course Code': 'first'
    }).reset_index()

    return df_aggregated


def perform_model(df):
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    df = df[df['% Attendance Scaled'] != "Data not provided"]  # Exclude records without valid scaled data
    model.fit(df[['% Attendance Scaled', 'Submission Rate Scaled']])

    df['Anomaly'] = model.predict(df[['% Attendance Scaled', 'Submission Rate Scaled']])
    thresholds = df[['% Attendance', 'Submission Rate']].mean()

    df_filtered = df[(df['Anomaly'] == -1) &
                     (df['% Attendance'] < thresholds['% Attendance']) &
                     (df['Submission Rate'] < thresholds['Submission Rate'])]

    return df_filtered

def detect_students_at_risk(df, level_of_study, year_of_course, course_code):
    preprocessed_data = preprocess_data(df)
    anomalised_data = perform_model(preprocessed_data)
    students_at_risk = anomalised_data[
        (anomalised_data['Level of Study'] == level_of_study) &
        (anomalised_data['Year of Course'] == year_of_course) &
        (anomalised_data['Course Code'] == course_code)
    ]

    return students_at_risk