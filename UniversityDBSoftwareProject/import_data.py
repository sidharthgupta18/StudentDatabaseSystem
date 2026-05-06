import pandas as pd
import mysql.connector
from mysql.connector import Error
import os

def import_excel_data():
    connection = None
    try:
        # Path to the minor folder with the 6 Excel files
        minor_folder = os.path.join(os.path.dirname(__file__), 'minor')

        if not os.path.exists(minor_folder):
            print(" 'minor' folder not found! Make sure it's in the same directory as this script.")
            return

        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='PASSWORD',  # YOUR PASSWORD HERE
            database='university_db'
        )

        if not connection.is_connected():
            print(" Could not connect to database.")
            return

        cursor = connection.cursor()
        total_records = 0

        # 1. Import Branches
        branches_file = os.path.join(minor_folder, 'branches.xlsx')
        if os.path.exists(branches_file):
            df = pd.read_excel(branches_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO branches (branch_id, branch_name, duration_years) VALUES (%s, %s, %s)",
                        (row['branch_id'], row['branch_name'], row['duration_years'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting branch {row['branch_id']}: {e}")
            print(f" Branches    - {count} records imported")
            total_records += count
        else:
            print(" branches.xlsx not found, skipping.")

        # 2. Import Subjects
        subjects_file = os.path.join(minor_folder, 'subjects.xlsx')
        if os.path.exists(subjects_file):
            df = pd.read_excel(subjects_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO subjects (subject_id, subject_name, branch_id, semester, credits, is_lab) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['subject_id'], row['subject_name'], row['branch_id'], row['semester'], row['credits'], row['is_lab'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting subject {row['subject_id']}: {e}")
            print(f" Subjects    - {count} records imported")
            total_records += count
        else:
            print(" subjects.xlsx not found, skipping.")

        # 3. Import Faculty
        faculty_file = os.path.join(minor_folder, 'faculty.xlsx')
        if os.path.exists(faculty_file):
            df = pd.read_excel(faculty_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO faculty (faculty_id, name, email, phone, branch_id, designation) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['faculty_id'], row['name'], row['email'], row['phone'], row['branch_id'], row['designation'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting faculty {row['faculty_id']}: {e}")
            print(f" Faculty     - {count} records imported")
            total_records += count
        else:
            print(" faculty.xlsx not found, skipping.")

        # 4. Import Students
        students_file = os.path.join(minor_folder, 'students.xlsx')
        if os.path.exists(students_file):
            df = pd.read_excel(students_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO students (student_id, name, batch, section, semester, branch_id, email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['name'], row['batch'], row['section'], row['semester'], row['branch_id'], row['email'], row['phone'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting student {row['student_id']}: {e}")
            print(f" Students    - {count} records imported")
            total_records += count
        else:
            print(" students.xlsx not found, skipping.")

        # 5. Import Attendance
        attendance_file = os.path.join(minor_folder, 'attendance.xlsx')
        if os.path.exists(attendance_file):
            df = pd.read_excel(attendance_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO attendance (student_id, subject_id, attended, total, percentage, faculty_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'], row['attended'], row['total'], row['percentage'], row['faculty_id'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting attendance record: {e}")
            print(f" Attendance  - {count} records imported")
            total_records += count
        else:
            print(" attendance.xlsx not found, skipping.")

        # 6. Import Marks
        marks_file = os.path.join(minor_folder, 'marks.xlsx')
        if os.path.exists(marks_file):
            df = pd.read_excel(marks_file)
            count = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT IGNORE INTO marks (student_id, subject_id, t1_marks, t2_marks, t3_marks, ta_marks, total_marks, percentage, grade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'], row['t1_marks'], row['t2_marks'], row['t3_marks'], row['ta_marks'], row['total_marks'], row['percentage'], row['grade'])
                    )
                    count += 1
                except Error as e:
                    print(f"  Error inserting marks record: {e}")
            print(f" Marks       - {count} records imported")
            total_records += count
        else:
            print(" marks.xlsx not found, skipping.")

        connection.commit()
        print(f"\n Successfully imported {total_records} total records from minor/ folder!")

    except Error as e:
        print(f" Database error: {e}")
    except Exception as e:
        print(f" Error: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    import_excel_data()