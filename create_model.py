import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# This creates a local database file named 'student_data.db'
engine = create_engine('sqlite:///student_data.db')

# Generate 100 fake students
np.random.seed(42)
df = pd.DataFrame({
    'attendance': np.random.uniform(0.5, 1.0, 100),
    'study_hours': np.random.randint(1, 20, 100),
    'marks': np.random.randint(30, 100, 100)
})
# Logic: If marks > 50, they pass (1), else fail (0)
df['passed'] = (df['marks'] > 50).astype(int)

# Save to SQL
df.to_sql('performance', engine, if_exists='replace', index=False)
print("Step 2 Complete: SQL Database Created!")