import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'PASSWORD'   # <-- replace with your actual password
}

# ─────────────────────────────────────────────
#  SECTION 1 — CREATE DATABASE AND TABLES
# ─────────────────────────────────────────────

def create_database():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)

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
                    branch_id   VARCHAR(10)  PRIMARY KEY,
                    branch_name VARCHAR(100) NOT NULL,
                    duration_years INT DEFAULT 4
                )
                """,
                # Students table
                """
                CREATE TABLE students (
                    student_id VARCHAR(20)  PRIMARY KEY,
                    name       VARCHAR(100) NOT NULL,
                    batch      VARCHAR(10),
                    section    VARCHAR(5),
                    semester   INT,
                    branch_id  VARCHAR(10),
                    email      VARCHAR(100),
                    phone      VARCHAR(20),
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Subjects table
                """
                CREATE TABLE subjects (
                    subject_id   VARCHAR(10)  PRIMARY KEY,
                    subject_name VARCHAR(100) NOT NULL,
                    branch_id    VARCHAR(10),
                    semester     INT,
                    credits      INT,
                    is_lab       BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Faculty table
                """
                CREATE TABLE faculty (
                    faculty_id  VARCHAR(10)  PRIMARY KEY,
                    name        VARCHAR(100) NOT NULL,
                    email       VARCHAR(100),
                    phone       VARCHAR(15),
                    branch_id   VARCHAR(10),
                    designation VARCHAR(50),
                    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
                )
                """,
                # Attendance table
                """
                CREATE TABLE attendance (
                    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id    VARCHAR(20),
                    subject_id    VARCHAR(10),
                    attended      INT,
                    total         INT,
                    percentage    DECIMAL(5,2),
                    faculty_id    VARCHAR(10),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
                    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
                )
                """,
                # Marks table
                """
                CREATE TABLE marks (
                    marks_id    INT AUTO_INCREMENT PRIMARY KEY,
                    student_id  VARCHAR(20),
                    subject_id  VARCHAR(10),
                    t1_marks    INT,
                    t2_marks    INT,
                    t3_marks    INT,
                    ta_marks    INT,
                    total_marks INT,
                    percentage  DECIMAL(5,2),
                    grade       VARCHAR(2),
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
                )
                """,
                # Low attendance log table (used by the cursor procedure)
                """
                CREATE TABLE low_attendance_log (
                    log_id     INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20),
                    avg_pct    DECIMAL(5,2),
                    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
                """
            ]

            for table_sql in tables_sql:
                cursor.execute(table_sql)

            connection.commit()
            print("All tables created successfully!")

    except Error as e:
        print(f"Error in create_database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ─────────────────────────────────────────────
#  SECTION 2 — SQL FUNCTIONS
#  These are reusable MySQL functions that
#  can be called inside queries anywhere.
# ─────────────────────────────────────────────

def create_functions():
    """
    Creates 3 SQL FUNCTIONS inside university_db:

    1. assign_grade(pct)
       - Input : a decimal percentage (e.g. 85.5)
       - Output: grade string  A+ / A / B / C / F
       - Used  : FR-19 — auto grade calculation

    2. calculate_attendance_pct(sid, subid)
       - Input : student_id and subject_id
       - Output: attendance percentage as DECIMAL
       - Used  : FR-11 — attendance percentage

    3. get_total_marks(t1, t2, t3, ta)
       - Input : four individual test scores
       - Output: their sum as INT
       - Used  : FR-18 — total marks computation
    """
    functions_sql = {

        # ── FUNCTION 1 ──────────────────────────────
        "assign_grade": """
            CREATE FUNCTION assign_grade(pct DECIMAL(5,2))
            RETURNS VARCHAR(2)
            DETERMINISTIC
            BEGIN
                DECLARE grade VARCHAR(2);
                IF     pct >= 90 THEN SET grade = 'A+';
                ELSEIF pct >= 80 THEN SET grade = 'A';
                ELSEIF pct >= 70 THEN SET grade = 'B';
                ELSEIF pct >= 60 THEN SET grade = 'C';
                ELSE                   SET grade = 'F';
                END IF;
                RETURN grade;
            END
        """,

        # ── FUNCTION 2 ──────────────────────────────
        "calculate_attendance_pct": """
            CREATE FUNCTION calculate_attendance_pct(
                sid   VARCHAR(20),
                subid VARCHAR(10)
            )
            RETURNS DECIMAL(5,2)
            DETERMINISTIC
            BEGIN
                DECLARE pct DECIMAL(5,2);
                SELECT (attended / total) * 100
                INTO   pct
                FROM   attendance
                WHERE  student_id = sid
                  AND  subject_id = subid
                LIMIT 1;
                RETURN IFNULL(pct, 0);
            END
        """,

        # ── FUNCTION 3 ──────────────────────────────
        "get_total_marks": """
            CREATE FUNCTION get_total_marks(
                t1 INT, t2 INT, t3 INT, ta INT
            )
            RETURNS INT
            DETERMINISTIC
            BEGIN
                RETURN IFNULL(t1,0) + IFNULL(t2,0)
                     + IFNULL(t3,0) + IFNULL(ta,0);
            END
        """
    }

    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()

        # Allow multi-statement stored routines
        cursor.execute("SET GLOBAL log_bin_trust_function_creators = 1")

        for name, sql in functions_sql.items():
            try:
                cursor.execute(f"DROP FUNCTION IF EXISTS {name}")
                cursor.execute(sql)
                print(f"  Function '{name}' created.")
            except Error as e:
                print(f"  Error creating function '{name}': {e}")

        connection.commit()
        print("All SQL functions created!")

    except Error as e:
        print(f"Error in create_functions: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ─────────────────────────────────────────────
#  SECTION 3 — SQL TRIGGERS
#  Triggers fire AUTOMATICALLY when rows are
#  inserted or deleted — no manual call needed.
# ─────────────────────────────────────────────

def create_triggers():
    """
    Creates 3 SQL TRIGGERS inside university_db:

    1. after_attendance_insert
       - Fires : AFTER INSERT on attendance
       - Action: auto-calculates and stores percentage
       - Used  : FR-11

    2. after_marks_insert
       - Fires : AFTER INSERT on marks
       - Action: auto-assigns grade using assign_grade()
       - Used  : FR-19

    3. before_student_delete
       - Fires : BEFORE DELETE on students
       - Action: removes related attendance & marks first
                 so foreign key constraint is not violated
       - Used  : FR-03
    """
    triggers_sql = {

        # ── TRIGGER 1 ─── FIXED ─────────────────────────
        "after_attendance_insert": """
            CREATE TRIGGER after_attendance_insert
            BEFORE INSERT ON attendance
            FOR EACH ROW
            BEGIN
                SET NEW.percentage = (NEW.attended / NEW.total) * 100;
            END
        """,

        # ── TRIGGER 2 ─── FIXED ─────────────────────────
        "after_marks_insert": """
            CREATE TRIGGER after_marks_insert
            BEFORE INSERT ON marks
            FOR EACH ROW
            BEGIN
                SET NEW.total_marks = get_total_marks(
                                    NEW.t1_marks,
                                    NEW.t2_marks,
                                    NEW.t3_marks,
                                    NEW.ta_marks);
                SET NEW.percentage  = NEW.total_marks / 4.0;
                SET NEW.grade       = assign_grade(NEW.percentage);
            END
        """,

        # ── TRIGGER 3 ───────────────────────────────
        "before_student_delete": """
            CREATE TRIGGER before_student_delete
            BEFORE DELETE ON students
            FOR EACH ROW
            BEGIN
                DELETE FROM low_attendance_log
                WHERE  student_id = OLD.student_id;

                DELETE FROM attendance
                WHERE  student_id = OLD.student_id;

                DELETE FROM marks
                WHERE  student_id = OLD.student_id;
            END
        """
    }

    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()

        for name, sql in triggers_sql.items():
            try:
                cursor.execute(f"DROP TRIGGER IF EXISTS {name}")
                cursor.execute(sql)
                print(f"  Trigger '{name}' created.")
            except Error as e:
                print(f"  Error creating trigger '{name}': {e}")

        connection.commit()
        print("All SQL triggers created!")

    except Error as e:
        print(f"Error in create_triggers: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ─────────────────────────────────────────────
#  SECTION 4 — STORED PROCEDURE WITH SQL CURSOR
#  A SQL CURSOR lets you loop row-by-row
#  through a query result inside MySQL itself.
# ─────────────────────────────────────────────

def create_cursor_procedure():
    """
    Creates 1 STORED PROCEDURE that uses a SQL CURSOR:

    Procedure : flag_low_attendance()
    Cursor    : student_attendance_cursor
    - Loops through every student's average attendance
    - If average < 75%, writes a row to low_attendance_log
    - Used: FR-13 — attendance alert system
    """
    procedure_sql = """
        CREATE PROCEDURE flag_low_attendance()
        BEGIN
            -- Variables to hold each row fetched by the cursor
            DECLARE done    INT         DEFAULT 0;
            DECLARE sid     VARCHAR(20);
            DECLARE avg_pct DECIMAL(5,2);

            -- ── CURSOR DECLARATION ──────────────────
            -- student_attendance_cursor fetches each
            -- student's average attendance percentage
            DECLARE student_attendance_cursor CURSOR FOR
                SELECT   student_id,
                         AVG(percentage) AS avg_pct
                FROM     attendance
                GROUP BY student_id;
            -- ────────────────────────────────────────

            -- Handler: when no more rows, set done = 1
            DECLARE CONTINUE HANDLER
                FOR NOT FOUND SET done = 1;

            -- Clear old log before re-running
            DELETE FROM low_attendance_log;

            -- Open the cursor (executes the SELECT)
            OPEN student_attendance_cursor;

            check_loop: LOOP
                -- Fetch one row into variables
                FETCH student_attendance_cursor INTO sid, avg_pct;

                -- Exit loop when no rows left
                IF done = 1 THEN
                    LEAVE check_loop;
                END IF;

                -- If below threshold, log the student
                IF avg_pct < 75 THEN
                    INSERT INTO low_attendance_log
                        (student_id, avg_pct)
                    VALUES
                        (sid, avg_pct);
                END IF;

            END LOOP;

            -- Always close the cursor when done
            CLOSE student_attendance_cursor;

        END
    """

    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()

        cursor.execute("DROP PROCEDURE IF EXISTS flag_low_attendance")
        cursor.execute(procedure_sql)
        connection.commit()
        print("Stored procedure 'flag_low_attendance' with cursor created!")

    except Error as e:
        print(f"Error in create_cursor_procedure: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ─────────────────────────────────────────────
#  SECTION 5 — PYTHON HELPER FUNCTIONS
#  These call the SQL objects from Python code
#  (used inside gui_system.py)
# ─────────────────────────────────────────────

def get_student_grade(student_id, subject_id):
    """
    Calls the SQL function assign_grade() via Python.
    Returns the grade string for a student in a subject.
    Usage in gui_system.py:
        grade = get_student_grade('CSE001', 'CS401')
    """
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()
        cursor.execute("""
            SELECT assign_grade(percentage)
            FROM   marks
            WHERE  student_id = %s
              AND  subject_id = %s
        """, (student_id, subject_id))
        result = cursor.fetchone()
        return result[0] if result else 'N/A'

    except Error as e:
        print(f"Error in get_student_grade: {e}")
        return 'N/A'
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def get_attendance_percentage(student_id, subject_id):
    """
    Calls the SQL function calculate_attendance_pct() via Python.
    Returns attendance percentage as a float.
    Usage in gui_system.py:
        pct = get_attendance_percentage('CSE001', 'CS401')
    """
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()
        cursor.execute("""
            SELECT calculate_attendance_pct(%s, %s)
        """, (student_id, subject_id))
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0

    except Error as e:
        print(f"Error in get_attendance_percentage: {e}")
        return 0.0
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def run_low_attendance_check():
    """
    Calls the stored procedure flag_low_attendance() via Python.
    This triggers the SQL CURSOR internally inside MySQL.
    Returns list of (student_id, avg_pct) tuples for at-risk students.
    Usage in gui_system.py:
        at_risk = run_low_attendance_check()
    """
    try:
        connection = mysql.connector.connect(
            **DB_CONFIG, database='university_db'
        )
        cursor = connection.cursor()

        # Call the stored procedure (runs the SQL CURSOR inside MySQL)
        cursor.callproc('flag_low_attendance')

        # Fetch the logged results
        cursor.execute("""
            SELECT student_id, avg_pct
            FROM   low_attendance_log
            ORDER BY avg_pct ASC
        """)
        results = cursor.fetchall()
        return results

    except Error as e:
        print(f"Error in run_low_attendance_check: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# ─────────────────────────────────────────────
#  MAIN — run everything in correct order
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n-- Step 1: Creating database and tables --")
    create_database()

    print("\n-- Step 2: Creating SQL functions --")
    create_functions()

    print("\n-- Step 3: Creating SQL triggers --")
    create_triggers()

    print("\n-- Step 4: Creating stored procedure with cursor --")
    create_cursor_procedure()

    print("\n-- All done! university_db is ready. --\n")