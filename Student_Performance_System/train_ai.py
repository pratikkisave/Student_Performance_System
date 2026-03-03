import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def retrain_model():
    engine = create_engine("sqlite:///student_data.db")

    # Load ONLY user data
    df = pd.read_sql("user_inputs", engine)

    if df.empty or len(df) < 5:
        return False, "Not enough data to retrain model"

    X = df[['attendance', 'study_hours', 'marks']]
    y = df['passed']

    results = {}

    # Retrain classifier for Pass/Fail
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        joblib.dump(clf, "student_model.pkl")
        acc = clf.score(X_test, y_test)
        results['pass_accuracy'] = round(acc * 100, 2)
    except Exception as e:
        results['pass_error'] = str(e)

    # Retrain SGPA regressor if sgpa column present
    if 'sgpa' in df.columns and df['sgpa'].notna().sum() >= 5:
        try:
            y_sgpa = df['sgpa']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_sgpa, test_size=0.2, random_state=42
            )

            reg = RandomForestRegressor(n_estimators=100, random_state=42)
            reg.fit(X_train, y_train)
            joblib.dump(reg, "sgpa_model.pkl")
            r2 = reg.score(X_test, y_test)
            results['sgpa_r2'] = round(r2, 4)
        except Exception as e:
            results['sgpa_error'] = str(e)
    else:
        results['sgpa_error'] = 'Not enough sgpa data to retrain'

    return True, results
