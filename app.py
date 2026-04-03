import streamlit as st
import pandas as pd
import joblib
from sqlalchemy import create_engine, text
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import os

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="Student Performance System", page_icon="🎓", layout="wide")

# ==================================================
# THEME TOGGLE (SIDEBAR) – COMPACT & SAFE
# ==================================================
st.sidebar.subheader("🎨 Theme")

theme_choice = st.sidebar.radio(
    "UI Mode",
    ["Dark", "Light"],
    index=0,
    key="theme_selector_unique"   # 🔑 prevents duplicate ID error
)

st.session_state["theme"] = "dark" if theme_choice == "Dark" else "light"

# ==================================================
# STYLES (COMPACT • LIGHT + DARK • RESPONSIVE)
# ==================================================
theme = st.session_state.get("theme", "dark")

if theme == "dark":
    st.markdown("""
    <style>
    /* ========== DARK THEME ========== */
    .stApp {
        background: linear-gradient(135deg, #0f172a, #020617);
        color: #e5e7eb;
        font-family: "Segoe UI", sans-serif;
    }

    /* Titles */
    .main-title { font-size:32px; font-weight:700; color:#f8fafc; }
    .subtitle { font-size:14px; color:#cbd5f5; margin-bottom:16px; }

    /* Section Cards */
    .section-card {
        background: rgba(255,255,255,0.06);
        padding:16px;
        border-radius:12px;
        margin-bottom:14px;
        border:1px solid rgba(255,255,255,0.08);
    }

    .section-title {
        font-size:18px;
        font-weight:600;
        color:#e0e7ff;
        margin-bottom:8px;
    }

    /* Normal Cards */
    .card {
        background: rgba(255,255,255,0.07);
        padding:14px;
        border-radius:12px;
        margin-bottom:14px;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg,#1e293b,#020617);
        border-radius:12px;
        padding:12px;
        border:1px solid rgba(255,255,255,0.1);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg,#6366f1,#4f46e5);
        color:white;
        border-radius:8px;
        font-size:14px;
        padding:6px 14px;
        font-weight:600;
        border:none;
    }

    /* Risk Badges */
    .risk-high, .risk-medium, .risk-low {
        font-size:12px;
        padding:4px 10px;
        border-radius:8px;
        font-weight:700;
        display:inline-block;
    }

    .risk-high { background:#7f1d1d; color:#fee2e2; }
    .risk-medium { background:#78350f; color:#ffedd5; }
    .risk-low { background:#064e3b; color:#d1fae5; }

    /* Mobile */
    @media (max-width: 768px) {
        .main-title { font-size:24px; text-align:center; }
        .section-title { font-size:16px; text-align:center; }
        .subtitle { font-size:13px; text-align:center; }
        .section-card, .card { padding:12px; }
        .stButton>button { width:100%; }
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    /* ========== LIGHT THEME ========== */
    .stApp {
        background:#f8fafc;
        color:#0f172a;
        font-family: "Segoe UI", sans-serif;
    }

    .main-title { font-size:32px; font-weight:700; color:#0f172a; }
    .subtitle { font-size:14px; color:#475569; margin-bottom:16px; }

    .section-card {
        background:#ffffff;
        padding:16px;
        border-radius:12px;
        margin-bottom:14px;
        border:1px solid #e5e7eb;
    }

    .section-title {
        font-size:18px;
        font-weight:600;
        color:#1e293b;
        margin-bottom:8px;
    }

    .card {
        background:#ffffff;
        padding:14px;
        border-radius:12px;
        margin-bottom:14px;
        border:1px solid #e5e7eb;
    }

    [data-testid="metric-container"] {
        background:#ffffff;
        border-radius:12px;
        padding:12px;
        border:1px solid #e5e7eb;
    }

    .stButton>button {
        background: linear-gradient(135deg,#2563eb,#1d4ed8);
        color:white;
        border-radius:8px;
        font-size:14px;
        padding:6px 14px;
        font-weight:600;
        border:none;
    }

    .risk-high, .risk-medium, .risk-low {
        font-size:12px;
        padding:4px 10px;
        border-radius:8px;
        font-weight:700;
        display:inline-block;
    }

    .risk-high { background:#fecaca; color:#7f1d1d; }
    .risk-medium { background:#fed7aa; color:#78350f; }
    .risk-low { background:#bbf7d0; color:#064e3b; }

    @media (max-width: 768px) {
        .main-title { font-size:24px; text-align:center; }
        .section-title { font-size:16px; text-align:center; }
        .subtitle { font-size:13px; text-align:center; }
        .section-card, .card { padding:12px; }
        .stButton>button { width:100%; }
    }
    </style>
    """, unsafe_allow_html=True)


# ===============================
# THEME TOGGLE (LIGHT / DARK)
# ===============================
st.sidebar.subheader("🎨 Theme Settings")

theme = st.sidebar.radio(
    "Select Theme",
    ["Dark Mode", "Light Mode"],
    index=0
)

if theme == "Dark Mode":
    st.session_state["theme"] = "dark"
else:
    st.session_state["theme"] = "light"

# ==================================================
# HEADER
# ==================================================
st.markdown("""
<div class="main-title">🎓 Student Performance Analysis System</div>
<div class="subtitle">AI-Powered Academic Analytics Dashboard</div>
""", unsafe_allow_html=True)

# ==================================================
# DATABASE & MODEL
# ==================================================
engine = create_engine("sqlite:///student_data.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "student_model.pkl")

if not os.path.exists(MODEL_PATH):
    st.error(f"ML model file not found at {MODEL_PATH}")
    st.stop()

model = joblib.load(MODEL_PATH)

# ==================================================
# DATABASE MIGRATION
# ==================================================
def migrate_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS user_inputs (
            student_name TEXT,
            roll_no TEXT PRIMARY KEY,
            attendance REAL,
            study_hours INTEGER,
            marks INTEGER,
            total_marks INTEGER,
            percentage REAL,
            passed INTEGER,
            grade TEXT,
            risk TEXT
        )
        """))

        cols = conn.execute(text("PRAGMA table_info(user_inputs)")).fetchall()
        existing_cols = [c[1] for c in cols]

        extra_cols = {
            "gender": "TEXT",
            "year": "TEXT",
            "branch": "TEXT",
            "teacher_remark": "TEXT"
        }

        for col, dtype in extra_cols.items():
            if col not in existing_cols:
                conn.execute(text(f"ALTER TABLE user_inputs ADD COLUMN {col} {dtype}"))

migrate_db()

# ==================================================
# SUBJECT MANAGER
# ==================================================
if "subjects" not in st.session_state:
    st.session_state.subjects = [
        {"name": "Cloud Computing", "marks": 0, "total": 100},
        {"name": "Artificial Intelligence", "marks": 0, "total": 100},
        {"name": "Web Analytics", "marks": 0, "total": 100},
        {"name": "DSBDA", "marks": 0, "total": 100},
    ]

# ==================================================
# HELPERS
# ==================================================
def grade_calc(p):
    if p >= 85: return "A"
    if p >= 70: return "B"
    if p >= 55: return "C"
    if p >= 40: return "D"
    return "F"

def consistency_check(hours, percent):
    if hours >= 15 and percent < 50:
        return "High study hours but low performance"
    if hours < 6 and percent >= 60:
        return "Low study hours but good performance"
    return "Consistent"

def risk_calc(att, percent, hours):
    if att < 60 or percent < 40 or hours < 6:
        return "High Risk"
    elif att < 75 or percent < 55 or hours < 10:
        return "Medium Risk"
    return "Low Risk"

def delete_student(roll_no):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM user_inputs WHERE roll_no = :roll"),
            {"roll": roll_no}
        )

# ==================================================
# EXPLAINABLE AI (PHASE 5) – FIXED
# ==================================================
def explain_prediction(attendance, study_hours, percentage):
    reasons = []

    if attendance < 60:
        reasons.append("Low attendance (< 60%)")

    if study_hours < 6:
        reasons.append("Insufficient study hours per week")

    if percentage < 40:
        reasons.append("Low overall academic performance")

    if not reasons:
        return "Performance indicators are strong. No major risk factors detected."

    return " | ".join(reasons)


def ai_recommendation(attendance, study_hours, percentage, risk):
    recommendations = []

    if attendance < 75:
        recommendations.append(
            "Improve attendance by attending lectures regularly."
        )

    if study_hours < 10:
        recommendations.append(
            "Increase study time to at least 10–15 hours per week."
        )

    if percentage < 50:
        recommendations.append(
            "Revise basic concepts and take weekly practice tests."
        )

    if risk == "High Risk":
        recommendations.append(
            "Immediately consult the teacher or academic mentor."
        )

    elif risk == "Medium Risk":
        recommendations.append(
            "Maintain consistency and increase practice."
        )

    if not recommendations:
        recommendations.append(
            "Performance is good. Maintain the current study pattern."
        )

    return recommendations

# ==================================================
# TABS
# ==================================================
tab1, tab2, tab3 = st.tabs(
    ["➕ Add / Edit Student", "📚 Manage Subjects", "📊 Dashboard"]
)

# ==================================================
# TAB 1 – ADD / EDIT STUDENT (FINAL UPDATED UI)
# ==================================================
with tab1:
    st.markdown(
        "<div class='card'><h2>➕ Add / Edit Student</h2>"
        "<p style='color:#cbd5e1;'>Enter student details and subject-wise marks</p></div>",
        unsafe_allow_html=True
    )

    # -------------------------------
    # Load existing data
    # -------------------------------
    df = pd.read_sql("user_inputs", engine)
    edit = st.checkbox("✏️ Edit Existing Student")

    student = None
    if edit and not df.empty:
        sel = st.selectbox("Select Roll Number", df["roll_no"])
        student = df[df["roll_no"] == sel].iloc[0]

    # ==================================================
    # BASIC DETAILS
    # ==================================================
    st.markdown("<div class='card'><h3>👤 Student Basic Details</h3></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Student Name", student.student_name if student is not None else "")
        roll = st.text_input(
    "Roll Number",
    student.roll_no if student is not None else "",
    disabled=edit   # 🔐 LOCK PRIMARY KEY
    
)

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=["Male","Female","Other"].index(student.gender)
            if student is not None and student.gender in ["Male","Female","Other"] else 0
        )

    with col2:
        year = st.selectbox(
            "Year",
            ["FY", "SY","TY","BE" ],
            index=["FY","SY","TY","Final Year"].index(student.year)
            if student is not None and student.year in ["FY","SY","TY","Final Year"] else 0
        )
        branch = st.selectbox(
            "Cource Name",
            ["AIML","CS","IT", "ENTC","MECH","CIVIL"],
            index=[
                "CSE","IT","Computer Science & Engg (Data Science)",
                "ENTC","MECH","CIVIL"
            ].index(student.branch)
            if student is not None else 0
        )

    # ==================================================
    # ACADEMIC INPUTS
    # ==================================================
    st.markdown("<div class='card'><h3>📚 Academic Inputs</h3></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        attendance = st.slider(
            "Attendance (%)",
            0, 100,
            int(student.attendance) if student is not None else 75
        )

    with col4:
        study_hours = st.number_input(
            "Study Hours / Week",
            0, 60,
            int(student.study_hours) if student is not None else 10
        )

    # ==================================================
    # SUBJECTS & MARKS
    # ==================================================
    st.markdown(
        "<div class='card'><h3>📘 Subjects & Marks</h3>"
        "<p style='color:#cbd5e1;'>Enter obtained and total marks</p></div>",
        unsafe_allow_html=True
    )

    total_obt, total_max = 0, 0

    for i, sub in enumerate(st.session_state.subjects):
        st.markdown(
            f"<div class='card'><b>{i+1}. {sub['name']}</b></div>",
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            sub["marks"] = st.number_input(
                "Obtained Marks",
                0, 100,
                value=sub["marks"],
                key=f"marks_{i}"
            )

        with c2:
            sub["total"] = st.number_input(
                "Total Marks",
                1, 100,
                value=sub["total"],
                key=f"total_{i}"
            )

        total_obt += sub["marks"]
        total_max += sub["total"]

    # ==================================================
    # LIVE PERFORMANCE (NEW FEATURE)
    # ==================================================
    if total_max > 0:
        live_percentage = round((total_obt / total_max) * 100, 2)
    else:
        live_percentage = 0

    st.markdown("<div class='card'><h3>📈 Live Performance</h3></div>", unsafe_allow_html=True)

    st.metric("Current Percentage", f"{live_percentage}%")
    st.progress(min(live_percentage / 100, 1.0))

    live_grade = grade_calc(live_percentage)
    live_risk = risk_calc(attendance, live_percentage, study_hours)

    cg1, cg2 = st.columns(2)

    with cg1:
        st.success(f"🎓 Grade: {live_grade}")

    with cg2:
        if live_risk == "High Risk":
            st.error("⚠️ Risk Level: High Risk")
        elif live_risk == "Medium Risk":
            st.warning("⚠️ Risk Level: Medium Risk")
        else:
            st.success("✅ Risk Level: Low Risk")

    # ==================================================
    # TEACHER REMARK
    # ==================================================
    teacher_remark = st.text_area(
        "📝 Teacher Remark",
        student.teacher_remark if student is not None else ""
    )

    # ==================================================
    # SAVE STUDENT
    # ==================================================
    if st.button("💾 Save Student"):
        X = pd.DataFrame(
            [[attendance / 100, study_hours, total_obt]],
            columns=["attendance", "study_hours", "marks"]
        )

        pred = int(model.predict(X)[0])

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT OR REPLACE INTO user_inputs
                (student_name, roll_no, gender, year, branch,
                 attendance, study_hours, marks, total_marks,
                 percentage, passed, grade, risk, teacher_remark)
                VALUES (:name, :roll, :gender, :year, :branch,
                        :att, :study, :marks, :total,
                        :perc, :passed, :grade, :risk, :remark)
            """), {
                "name": name,
                "roll": roll,
                "gender": gender,
                "year": year,
                "branch": branch,
                "att": attendance,
                "study": study_hours,
                "marks": total_obt,
                "total": total_max,
                "perc": live_percentage,
                "passed": pred,
                "grade": live_grade,
                "risk": live_risk,
                "remark": teacher_remark
            })

        st.success("✅ Student record saved successfully")

# ==================================================
# TAB 2 – MANAGE SUBJECTS (AI REMOVED)
# ==================================================
with tab2:
    st.markdown(
        "<div class='card'><h2>📚 Manage Subjects</h2>"
        "<p style='color:#cbd5e1;'>Add or remove subjects (No AI here)</p></div>",
        unsafe_allow_html=True
    )

    # -------------------------------
    # ADD NEW SUBJECT
    # -------------------------------
    new_sub = st.text_input(
        "New Subject Name",
        key="tab2_new_subject"
    )

    if st.button("➕ Add Subject", key="tab2_add_subject") and new_sub:
        st.session_state.subjects.append(
            {"name": new_sub, "marks": 0, "total": 100}
        )
        st.success("Subject added successfully")
        st.rerun()

    st.divider()

    # -------------------------------
    # EXISTING SUBJECTS LIST
    # -------------------------------
    st.subheader("📘 Existing Subjects")

    if len(st.session_state.subjects) == 0:
        st.info("No subjects available")
    else:
        for i, sub in enumerate(st.session_state.subjects):
            col1, col2 = st.columns([5, 1])

            with col1:
                st.write(f"*{i+1}. {sub['name']}*")

            with col2:
                if st.button("❌ Remove", key=f"tab2_remove_{i}"):
                    st.session_state.subjects.pop(i)
                    st.rerun()

# ==================================================
# TAB 3 – DASHBOARD (FINAL WITH RISK COLORS)
# ==================================================
# ==================================================
# TAB 3 – DASHBOARD (FINAL FIXED VERSION)
# ==================================================
with tab3:
    st.markdown(
        "<div class='section-card'><div class='section-title'>📊 Dashboard Overview</div></div>",
        unsafe_allow_html=True
    )

    # -------------------------------
    # LOAD DATA
    # -------------------------------
    df = pd.read_sql("user_inputs", engine)

    if df.empty:
        st.info("No student records found")
        st.stop()

    # -------------------------------
    # TOP SUMMARY METRICS
    # -------------------------------
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("📈 Avg Percentage", f"{round(df['percentage'].mean(), 2)}%")

    with m2:
        st.metric("🎓 Total Students", len(df))

    with m3:
        st.metric("⚠️ High Risk Students", (df["risk"] == "High Risk").sum())

    st.divider()

    # -------------------------------
    # RISK SUMMARY
    # -------------------------------
    st.markdown("<div class='section-title'>🚦 Risk Summary</div>", unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric("🟥 High Risk", (df["risk"] == "High Risk").sum())

    with r2:
        st.metric("🟧 Medium Risk", (df["risk"] == "Medium Risk").sum())

    with r3:
        st.metric("🟩 Low Risk", (df["risk"] == "Low Risk").sum())

    st.divider()

    # -------------------------------
    # FILTERS
    # -------------------------------
    st.markdown("<div class='section-title'>🔍 Filters</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)

    with f1:
        filter_branch = st.selectbox(
            "Select Branch",
            ["All"] + sorted(df["branch"].dropna().unique().tolist())
        )

    with f2:
        filter_year = st.selectbox(
            "Select Year",
            ["All"] + sorted(df["year"].dropna().unique().tolist())
        )

    filtered_df = df.copy()

    if filter_branch != "All":
        filtered_df = filtered_df[filtered_df["branch"] == filter_branch]

    if filter_year != "All":
        filtered_df = filtered_df[filtered_df["year"] == filter_year]

    st.divider()

    # -------------------------------
    # DISTRIBUTION CHARTS
    # -------------------------------
    st.markdown("<div class='section-title'>📊 Student Distribution</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.write("🏫 Branch-wise Students")
        st.bar_chart(filtered_df.groupby("branch").size())

    with c2:
        st.write("🎓 Year-wise Students")
        st.bar_chart(filtered_df.groupby("year").size())

    st.divider()

    # -------------------------------
    # PERFORMANCE SUMMARY TABLE
    # -------------------------------
    st.markdown("<div class='section-title'>📈 Performance Summary</div>", unsafe_allow_html=True)

    perf_summary = (
        filtered_df.groupby("branch")
        .agg(
            Avg_Attendance=("attendance", "mean"),
            Avg_Percentage=("percentage", "mean"),
            High_Risk_Students=("risk", lambda x: (x == "High Risk").sum())
        )
        .reset_index()
    )

    st.dataframe(perf_summary, use_container_width=True)

    st.divider()

    # -------------------------------
    # RISK DISTRIBUTION PIE CHART
    # -------------------------------
    st.markdown("<div class='section-title'>🥧 Risk Distribution</div>", unsafe_allow_html=True)

    risk_counts = filtered_df["risk"].value_counts()

    fig, ax = plt.subplots()
    ax.pie(
        risk_counts.values,
        labels=risk_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")

    st.pyplot(fig)

    st.divider()

    # -------------------------------
    # INDIVIDUAL STUDENT ANALYSIS
    # -------------------------------
    # -------------------------------
# INDIVIDUAL STUDENT ANALYSIS
# -------------------------------
st.markdown("<div class='section-title'>👤 Individual Student Analysis</div>", unsafe_allow_html=True)

selected_roll = st.selectbox(
    "Select Roll Number",
    filtered_df["roll_no"].unique()
)

student_df = filtered_df[filtered_df["roll_no"] == selected_roll]
st.dataframe(student_df, use_container_width=True)

row = student_df.iloc[0]

# -------------------------------
# DELETE BUTTON ✅
# -------------------------------
col_del1, col_del2 = st.columns([3, 1])

with col_del2:
    if st.button("🗑️ Delete Student"):
        delete_student(selected_roll)
        
        st.success("✅ Student deleted successfully")
        st.rerun()

# -------------------------------
# EARLY WARNING
# -------------------------------
if row.risk == "High Risk":
    st.error("🚨 Early Warning: Immediate academic intervention required")
elif row.risk == "Medium Risk":
    st.warning("⚠️ Warning: Student needs monitoring and guidance")
else:
    st.success("✅ Student performance is on track")

st.divider()

# -------------------------------
# EXPLAINABLE AI
# -------------------------------
st.subheader("🧠 Explainable AI Insight")
explanation = explain_prediction(
    row.attendance,
    row.study_hours,
    row.percentage
)
st.info(explanation)

# -------------------------------
# AI RECOMMENDATIONS
# -------------------------------
st.subheader("🎯 AI Recommendations")
recommendations = ai_recommendation(
    row.attendance,
    row.study_hours,
    row.percentage,
    row.risk
)

for i, rec in enumerate(recommendations, 1):
    st.write(f"{i}. {rec}")
    st.divider()

    # MODEL ACCURACY
    X = filtered_df[["attendance", "study_hours", "marks"]].copy()
    X["attendance"] = X["attendance"] / 100

    accuracy = accuracy_score(
        filtered_df["passed"],
        model.predict(X)
    )

    st.success(f"✅ Model Accuracy: {round(accuracy * 100, 2)}%")

    # ==========================================
# 🎓 CGPA CALCULATION SECTION
# ==========================================

# Ensure percentage exists
if 'percentage' not in df.columns:
    if 'marks' in df.columns and 'total_marks' in df.columns:
        df['percentage'] = (df['marks'] / df['total_marks']) * 100
    else:
        st.warning("Marks data not available to calculate percentage")

# Convert Percentage → CGPA
# Formula: CGPA = Percentage / 9.5
if 'percentage' in df.columns:
    df['cgpa'] = df['percentage'] / 9.5

    avg_cgpa = round(df['cgpa'].mean(), 2)

    st.metric("🎓 Average CGPA", avg_cgpa)

else:
    st.warning("Cannot calculate CGPA (percentage missing)")
