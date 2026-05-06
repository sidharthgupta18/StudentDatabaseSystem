import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='DATABASE PASSOWORD'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            cursor.execute("DROP DATABASE IF EXISTS university_db")
            cursor.execute("CREATE DATABASE university_db")
            print("Database created successfully!")
            
            cursor.execute("USE university_db")
            
            tables_sql = [
                # Branches table
                """
                CREATE TABLE branches (
                    branch_id VARCHAR(10) PRIMARY KEY,
                    branch_name VARCHAR(100) NOT NULL,
                    duration_years INT DEFAULT 4
                )
                """,
                # Students table
                """
                CREATE TABLE students (
                    student_id VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    batch VARCHAR(10),
                    section VARCHAR(5),
                    semester INT,
                    branch_id VARCHAR(10),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Subjects table
                """
                CREATE TABLE subjects (
                    subject_id VARCHAR(10) PRIMARY KEY,
                    subject_name VARCHAR(100) NOT NULL,
                    branch_id VARCHAR(10),
                    semester INT,
                    credits INT,
                    is_lab BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Faculty table
                """
                CREATE TABLE faculty (
                    faculty_id VARCHAR(10) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(15),
                    branch_id VARCHAR(10),
                    designation VARCHAR(50),
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Attendance table
                """
                CREATE TABLE attendance (
                    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    subject_id VARCHAR(10),
                    attended INT,
                    total INT,
                    percentage DECIMAL(5,2),
                    faculty_id VARCHAR(10),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
                    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
                )
                """,
                # Marks table
                """
                CREATE TABLE marks (
                    marks_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    subject_id VARCHAR(10),
                    t1_marks INT,
                    t2_marks INT,
                    t3_marks INT,
                    ta_marks INT,
                    total_marks INT,
                    percentage DECIMAL(5,2),
                    grade VARCHAR(2),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
                )
                """
            ]
            
            for table_sql in tables_sql:
                cursor.execute(table_sql)
            
            connection.commit()
            print("All tables created successfully!")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_database()