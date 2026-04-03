import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Use local SQLite database for consistency with the rest of the project
engine = create_engine('sqlite:///student_data.db')

def generate_bulk_data(n=100):
    np.random.seed(42)

    data = {
        'attendance': np.random.uniform(0.5, 1.0, n),
        'study_hours': np.random.randint(2, 25, n),
        'marks': np.random.randint(30, 100, n)
    }

    df = pd.DataFrame(data)

    # Simple rule: pass if marks > 50
    df['passed'] = (df['marks'] > 50).astype(int)

    # Generate a synthetic SGPA (scale 0.0 - 10.0) correlated with marks and attendance
    noise = np.random.normal(0, 0.5, n)
    sgpa = (df['marks'] / 100.0) * 8.5 + (df['attendance'] - 0.5) * 1.0 + noise
    sgpa = sgpa.clip(0.0, 10.0)
    df['sgpa'] = sgpa.round(2)

    # Upload to local SQLite `performance` table (replace existing data)
    df.to_sql('performance', con=engine, if_exists='replace', index=False)
    print(f"Successfully uploaded {n} student records to local SQLite (performance table).")

if __name__ == "__main__":
    generate_bulk_data(100)