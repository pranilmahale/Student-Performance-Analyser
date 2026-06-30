import sqlite3
import random
import numpy as np

DB_NAME = "student_insight.db"

SUBJECTS = ["Python", "Maths", "AE", "DBMS", "OS"]

MONTHS = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]

def get_connection():

    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

def setup_database():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        attendance INTEGER,
        assignments INTEGER,
        study_hours INTEGER,
        predicted_score INTEGER,
        risk_level TEXT,
        weakest_subject TEXT,
        strongest_subject TEXT,
        rank INTEGER,
        predicted_rank INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        marks INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS monthly_report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        month TEXT,
        score INTEGER,
        attendance INTEGER
    )
    """)

    conn.commit()

    conn.close()

def insert_student(student):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("""
    INSERT INTO students (
        name,
        attendance,
        assignments,
        study_hours,
        predicted_score,
        risk_level,
        weakest_subject,
        strongest_subject,
        rank,
        predicted_rank
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student["name"],
        student["attendance"],
        student["assignments"],
        student["study_hours"],
        student["predicted_score"],
        student["risk_level"],
        student["weakest_subject"],
        student["strongest_subject"],
        student["rank"],
        student["predicted_rank"]
    ))

    student_id = cur.lastrowid

    for mark in student["marks"]:

        cur.execute("""
        INSERT INTO marks (
            student_id,
            subject,
            marks
        )
        VALUES (?, ?, ?)
        """, (
            student_id,
            mark["subject"],
            mark["marks"]
        ))

    for month in student["monthly"]:

        cur.execute("""
        INSERT INTO monthly_report (
            student_id,
            month,
            score,
            attendance
        )
        VALUES (?, ?, ?, ?)
        """, (
            student_id,
            month["month"],
            month["score"],
            month["attendance"]
        ))

    conn.commit()

    conn.close()

def fetch_students():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("SELECT * FROM students")

    rows = cur.fetchall()

    students = []

    for row in rows:

        student_id = row[0]

        cur.execute("""
        SELECT subject, marks
        FROM marks
        WHERE student_id=?
        """, (student_id,))

        marks = [
            {
                "subject": x[0],
                "marks": x[1]
            }
            for x in cur.fetchall()
        ]

        cur.execute("""
        SELECT month, score, attendance
        FROM monthly_report
        WHERE student_id=?
        """, (student_id,))

        monthly = [
            {
                "month": x[0],
                "score": x[1],
                "attendance": x[2]
            }
            for x in cur.fetchall()
        ]

        students.append({
            "id": row[0],
            "name": row[1],
            "attendance": row[2],
            "assignments": row[3],
            "study_hours": row[4],
            "predicted_score": row[5],
            "risk_level": row[6],
            "weakest_subject": row[7],
            "strongest_subject": row[8],
            "rank": row[9],
            "predicted_rank": row[10],
            "marks": marks,
            "monthly": monthly
        })

    conn.close()

    return students

def remove_student(student_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM marks WHERE student_id=?",
        (student_id,)
    )

    cur.execute(
        "DELETE FROM monthly_report WHERE student_id=?",
        (student_id,)
    )

    cur.execute(
        "DELETE FROM students WHERE id=?",
        (student_id,)
    )

    conn.commit()

    conn.close()

def generate_dummy_students():

    students = fetch_students()

    if len(students) > 0:
        return

    for i in range(1, 61):

        marks = []

        for sub in SUBJECTS:

            marks.append({
                "subject": sub,
                "marks": random.randint(35, 100)
            })

        monthly = []

        for month in MONTHS:

            monthly.append({
                "month": month,
                "score": random.randint(40, 100),
                "attendance": random.randint(60, 100)
            })

        avg_marks = np.mean([
            x["marks"]
            for x in marks
        ])

        attendance = random.randint(60, 100)

        if attendance < 65 or avg_marks < 40:
            risk = "High"

        elif attendance < 75 or avg_marks < 55:
            risk = "Medium"

        else:
            risk = "Safe"

        sorted_subjects = sorted(
            marks,
            key=lambda x: x["marks"]
        )

        student = {
            "name": f"Student_{i}",
            "attendance": attendance,
            "assignments": random.randint(4, 10),
            "study_hours": random.randint(1, 8),
            "predicted_score": int(avg_marks),
            "risk_level": risk,
            "weakest_subject": sorted_subjects[0]["subject"],
            "strongest_subject": sorted_subjects[-1]["subject"],
            "rank": random.randint(1, 60),
            "predicted_rank": random.randint(1, 60),
            "marks": marks,
            "monthly": monthly
        }

        insert_student(student)