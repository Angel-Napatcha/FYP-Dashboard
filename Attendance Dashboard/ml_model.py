import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
# from sklearn.ensemble import RandomForestRegressor  # You can change this to any estimator
from sklearn.linear_model import LinearRegression
import numpy as np

def preprocess_data(df):
    # Ensure all required columns are present
    required_columns = [
        'User', '% Attendance', 'Submitted', 'Assessments',
        'Quarter', 'Year of Course', 'Course Code'
    ]
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")
    
    # Convert % Attendance from a fraction to a percentage if it's not already
    if df['% Attendance'].max() <= 1:
        df['% Attendance'] *= 100
    
    # Check for full year presence by counting unique quarters
    full_year_presence = df.groupby('User')['Quarter'].nunique() == 4
    users_full_year = full_year_presence[full_year_presence].index
    df = df[df['User'].isin(users_full_year)]
    
    # Impute missing values for necessary columns
    imputer = IterativeImputer(
        estimator=LinearRegression(),
        missing_values=np.nan,  # Ensure this matches how missing values are represented in your data
        max_iter=50,  # Increased from the default to allow more iterations
        tol=0.001,  # Adjust tolerance based on your data scale
        n_nearest_features=None,  # Use all features available for imputing each feature
        initial_strategy='median',
        random_state=42
    )
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
        '% Attendance': 'mean',
        'Submission Rate': 'mean',
        '% Attendance Scaled': 'mean',
        'Submission Rate Scaled': 'mean',
        'Level of Study': 'first',
        'Year of Course': 'first',
        'Course Code': 'first'
    }).reset_index()
    
    # Round the aggregated values after grouping to avoid any possible bias
    df_aggregated['% Attendance'] = df_aggregated['% Attendance'].round(2)
    df_aggregated['Submission Rate'] = df_aggregated['Submission Rate'].round(2)
    
    # Sort by Course Code
    df_aggregated.sort_values(by='Course Code', inplace=True)
    
    return df_aggregated

def perform_model(df):
    model = IsolationForest(n_estimators=100, contamination=0.25, random_state=42)
    df = df[df['% Attendance Scaled'] != "Data not provided"]  # Exclude records without valid scaled data
    model.fit(df[['% Attendance Scaled', 'Submission Rate Scaled']])

    df['Anomaly'] = model.predict(df[['% Attendance Scaled', 'Submission Rate Scaled']])
    thresholds = df[['% Attendance', 'Submission Rate']].mean()

    df_filtered = df[(df['Anomaly'] == -1) &
                     (df['% Attendance'] < thresholds['% Attendance']) &
                     (df['Submission Rate'] < thresholds['Submission Rate'])]

    return df_filtered

def detect_concerning_students(df, level_of_study, year_of_course):
    preprocessed_data = preprocess_data(df)
    anomalised_data = perform_model(preprocessed_data)
    at_risk_students = anomalised_data[
        (anomalised_data['Level of Study'] == level_of_study) &
        (anomalised_data['Year of Course'] == year_of_course)
    ]

    return at_risk_students