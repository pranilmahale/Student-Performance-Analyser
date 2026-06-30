import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from backend import (
    setup_database,
    insert_student,
    fetch_students,
    remove_student,
    generate_dummy_students,
    SUBJECTS,
    MONTHS
)

setup_database()

generate_dummy_students()

students = fetch_students()

st.set_page_config(
    page_title="StudentInsight Pro",
    layout="wide"
)

st.title("🎓 StudentInsight Pro Dashboard")

student_names = [s["name"] for s in students]

st.sidebar.title("➕ Add Student")

with st.sidebar.form("student_form"):

    name = st.text_input("Student Name")

    attendance = st.slider(
        "Attendance",
        0,
        100,
        75
    )

    assignments = st.slider(
        "Assignments",
        0,
        10,
        5
    )

    study_hours = st.slider(
        "Study Hours",
        0,
        15,
        4
    )

    st.subheader("📚 Subject Marks")

    subject_marks = {}

    for sub in SUBJECTS:

        subject_marks[sub] = st.slider(
            f"{sub} Marks",
            0,
            100,
            50
        )

    st.subheader("📈 Monthly Progress")

    monthly = []

    for month in MONTHS:

        score = st.slider(
            f"{month} Score",
            0,
            100,
            60
        )

        m_att = st.slider(
            f"{month} Attendance",
            0,
            100,
            attendance
        )

        monthly.append({
            "month": month,
            "score": score,
            "attendance": m_att
        })

    submit = st.form_submit_button("Save Student")

if submit:

    if name.strip() == "":

        st.error("Enter Student Name")

    else:

        marks_list = []

        for sub in SUBJECTS:

            marks_list.append({
                "subject": sub,
                "marks": subject_marks[sub]
            })

        avg_marks = np.mean(
            list(subject_marks.values())
        )

        predicted = int(
            avg_marks * 0.5 +
            attendance * 0.3 +
            assignments * 2 +
            study_hours * 3
        )

        if attendance < 65 or avg_marks < 40:
            risk = "High"

        elif attendance < 75 or avg_marks < 55:
            risk = "Medium"

        else:
            risk = "Safe"

        sorted_subjects = sorted(
            marks_list,
            key=lambda x: x["marks"]
        )

        student = {
            "name": name,
            "attendance": attendance,
            "assignments": assignments,
            "study_hours": study_hours,
            "predicted_score": predicted,
            "risk_level": risk,
            "weakest_subject": sorted_subjects[0]["subject"],
            "strongest_subject": sorted_subjects[-1]["subject"],
            "rank": np.random.randint(1, 61),
            "predicted_rank": np.random.randint(1, 61),
            "marks": marks_list,
            "monthly": monthly
        }

        insert_student(student)

        st.success("Student Added Successfully")

        st.rerun()

selected_name = st.sidebar.selectbox(
    "📌 Select Student",
    student_names
)

selected_subject = st.sidebar.selectbox(
    "📚 Filter Subject",
    ["All"] + SUBJECTS
)

student = next(
    s for s in students
    if s["name"] == selected_name
)

if st.sidebar.button("🗑 Delete Student"):

    remove_student(student["id"])

    st.success("Student Deleted")

    st.rerun()

avg_marks = np.mean([
    x["marks"]
    for x in student["marks"]
])

total_marks = sum([
    x["marks"]
    for x in student["marks"]
])

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric(
    "Attendance",
    f"{student['attendance']}%"
)

c2.metric(
    "Average",
    round(avg_marks, 2)
)

c3.metric(
    "Study Hours",
    student["study_hours"]
)

c4.metric(
    "Predicted Score",
    student["predicted_score"]
)

c5.metric(
    "Rank",
    student["rank"]
)

c6.metric(
    "Total Marks",
    total_marks
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Risk Analysis",
    "Comparison",
    "Radar Analysis"
])

with tab1:

    st.subheader("📚 Subject Wise Performance")

    marks_df = pd.DataFrame(
        student["marks"]
    )

    if selected_subject != "All":

        marks_df = marks_df[
            marks_df["subject"] == selected_subject
        ]

    fig1 = px.bar(
        marks_df,
        x="subject",
        y="marks",
        text="marks",
        color="subject"
    )

    fig1.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.subheader("📈 Monthly Progress")

    monthly_df = pd.DataFrame(
        student["monthly"]
    )

    fig2 = px.line(
        monthly_df,
        x="month",
        y="score",
        markers=True
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

with tab2:

    st.subheader("⚠ Risk Analysis")

    if student["risk_level"] == "High":

        st.error("High Risk Student")

    elif student["risk_level"] == "Medium":

        st.warning("Medium Risk Student")

    else:

        st.success("Safe Student")

    risk_students = []

    for s in students:

        if s["risk_level"] != "Safe":

            total = sum([
                x["marks"]
                for x in s["marks"]
            ])

            risk_students.append({
                "Student": s["name"],
                "Total": total,
                "Risk": s["risk_level"]
            })

    risk_df = pd.DataFrame(
        risk_students
    )

    fig3 = px.bar(
        risk_df,
        x="Student",
        y="Total",
        color="Risk",
        text="Total"
    )

    fig3.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with tab3:

    st.subheader("📚 Subject Comparison")

    subject_selected = st.selectbox(
        "Select Subject",
        SUBJECTS
    )

    subject_data = []

    for s in students:

        for m in s["marks"]:

            if m["subject"] == subject_selected:

                subject_data.append({
                    "Student": s["name"],
                    "Marks": m["marks"]
                })

    subject_df = pd.DataFrame(
        subject_data
    )

    fig4 = px.bar(
        subject_df,
        x="Student",
        y="Marks",
        color="Student",
        text="Marks"
    )

    fig4.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.subheader("🏆 Total Marks Comparison")

    totals = []

    for s in students:

        total = sum([
            x["marks"]
            for x in s["marks"]
        ])

        totals.append({
            "Student": s["name"],
            "Total": total
        })

    total_df = pd.DataFrame(
        totals
    )

    fig5 = px.bar(
        total_df,
        x="Student",
        y="Total",
        color="Student",
        text="Total"
    )

    fig5.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.subheader("📊 Subject Average")

    avg_subject = []

    for sub in SUBJECTS:

        marks = []

        for s in students:

            for m in s["marks"]:

                if m["subject"] == sub:

                    marks.append(m["marks"])

        avg_subject.append({
            "Subject": sub,
            "Average": np.mean(marks)
        })

    avg_df = pd.DataFrame(
        avg_subject
    )

    fig6 = px.line(
        avg_df,
        x="Subject",
        y="Average",
        markers=True
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

with tab4:

    st.subheader("📡 Radar Analysis")

    radar_values = [
        x["marks"]
        for x in student["marks"]
    ]

    fig7 = go.Figure()

    fig7.add_trace(
        go.Scatterpolar(
            r=radar_values,
            theta=SUBJECTS,
            fill="toself",
            name=student["name"]
        )
    )

    fig7.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        )
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

def generate_report(student):

    avg_marks = np.mean([
        x["marks"]
        for x in student["marks"]
    ])

    total_marks = sum([
        x["marks"]
        for x in student["marks"]
    ])

    report = f"""
====================================================

STUDENT REPORT

====================================================

Name : {student['name']}

Attendance : {student['attendance']}%

Assignments : {student['assignments']}

Study Hours : {student['study_hours']}

Average Marks : {avg_marks:.2f}

Total Marks : {total_marks}

Predicted Score : {student['predicted_score']}

Risk Level : {student['risk_level']}

Weakest Subject : {student['weakest_subject']}

Strongest Subject : {student['strongest_subject']}

"""

    for mark in student["marks"]:

        report += f"{mark['subject']} : {mark['marks']}\n"

    return report

st.divider()

report = generate_report(student)

st.download_button(
    label="📄 Download Report",
    data=report,
    file_name=f"{student['name']}_report.txt",
    mime="text/plain"
)