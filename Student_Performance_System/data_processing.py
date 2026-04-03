import pandas as pd
from sqlalchemy import create_engine

# 1. Setup the connection to your SQL database
# Replace 'root' and 'password' with your actual MySQL credentials
engine = create_engine('sqlite:///student_data.db')

def get_cleaned_data():
    """
    This function pulls data from SQL and prepares it for AI.
    """
    try:
        # Pull raw data from SQL
        query = "SELECT * FROM student_performance"
        df = pd.read_sql(query, engine)
        
        # Data Cleaning: Handle missing values (Basic)
        df = df.dropna()
        
        # Feature Engineering: Adding a new column if needed
        # Example: Total Score
        df['total_score_index'] = (df['attendance_rate'] * 0.4) + (df['previous_score'] * 0.6)
        
        return df
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

if __name__ == "_main_":
    # Test if the connection works when running this file directly
    data = get_cleaned_data()
    if data is not None:
        print("Data successfully loaded from SQL!")
        print(data.head())