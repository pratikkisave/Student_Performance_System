import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# ==================================================
# 1. CONNECT TO DATABASE
# ==================================================
engine = create_engine('sqlite:///student_data.db')

# Make sure table name is correct
df = pd.read_sql('user_inputs', engine)

if df.empty:
    raise ValueError("Database is empty. Add student records first.")

# ==================================================
# 2. FEATURES (X) AND TARGET (y)
# ==================================================
X = df[['attendance', 'study_hours', 'marks']].copy()

# ✅ FIX: Normalize attendance (0–100 → 0–1)
X['attendance'] = X['attendance'] / 100

y = df['passed']

# ==================================================
# 3. MODEL INITIALIZATION
# ==================================================
model = LogisticRegression(max_iter=1000)

# ==================================================
# 4. TRAIN MODEL
# ==================================================
model.fit(X, y)

# ==================================================
# 5. QUICK EVALUATION (OPTIONAL BUT GOOD)
# ==================================================
pred = model.predict(X)
acc = accuracy_score(y, pred)
print("Training Accuracy:", round(acc * 100, 2), "%")

# ==================================================
# 6. SAVE MODEL
# ==================================================
joblib.dump(model, 'student_model.pkl')

print("✅ student_model.pkl created successfully!")