import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from datetime import datetime


class StudentManagementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')

        self.connection = None
        self.connect()
        self.setup_gui()


    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='PASSWORD',   # <-- your password
                database='university_db',
                autocommit=True
            )
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Connection failed: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            return results, columns
        except Error as e:
            messagebox.showerror("Database Error", f"Query error: {e}")
            return None, None

    # ── GUI SETUP ─────────────────────────────────────────────────

    def setup_gui(self):
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="Student Management System",
                 font=('Arial', 20, 'bold'), fg='white', bg='#34495e').pack(pady=20)

        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.setup_sidebar(main_container)
        self.setup_content_area(main_container)

    def setup_sidebar(self, parent):
        sidebar_frame = tk.Frame(parent, bg='#34495e', width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)

        nav_buttons = [
            ("Dashboard",    self.show_dashboard),
            ("Students",     self.show_students),
            ("Academics",    self.show_academics),
            ("Reports",      self.show_reports),
            ("Tools",        self.show_tools),
            ("Import Data",  self.show_import),
            ("Exit",         self.exit_app)
        ]
        for text, command in nav_buttons:
            tk.Button(sidebar_frame, text=text, font=('Arial', 12),
                      bg='#3498db', fg='white', relief='flat', height=2,
                      command=command, anchor='w', padx=20).pack(fill=tk.X, padx=10, pady=5)

    def setup_content_area(self, parent):
        self.content_frame = tk.Frame(parent, bg='#ecf0f1')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.show_dashboard()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ── DASHBOARD ─────────────────────────────────────────────────

    def show_dashboard(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Dashboard",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        stats_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        stats_data = self.get_statistics()
        cards = [
            ("Students",  stats_data['students'],  '#e74c3c'),
            ("Faculty",   stats_data['faculty'],   '#3498db'),
            ("Branches",  stats_data['branches'],  '#2ecc71'),
            ("Subjects",  stats_data['subjects'],  '#f39c12')
        ]
        for i, (title, count, color) in enumerate(cards):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            tk.Label(card, text=str(count), font=('Arial', 24, 'bold'),
                     bg=color, fg='white').pack(pady=10)
            tk.Label(card, text=title, font=('Arial', 12),
                     bg=color, fg='white').pack(pady=5)
            stats_frame.columnconfigure(i, weight=1)

        actions_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        tk.Label(actions_frame, text="Quick Actions",
                 font=('Arial', 14, 'bold'), bg='#ecf0f1').pack(anchor='w')

        for text, command in [
            ("View Students",    self.show_students),
            ("Check Attendance", lambda: self.show_academics('attendance')),
            ("View Marks",       lambda: self.show_academics('marks')),
            ("Generate Report",  self.show_reports)
        ]:
            tk.Button(actions_frame, text=text, font=('Arial', 10),
                      bg='#95a5a6', fg='white', command=command).pack(side=tk.LEFT, padx=5, pady=10)

    def get_statistics(self):
        stats = {'students': 0, 'faculty': 0, 'branches': 0, 'subjects': 0}
        for key in stats:
            result, _ = self.execute_query(f"SELECT COUNT(*) FROM {key}")
            if result:
                stats[key] = result[0][0]
        return stats

    # ── STUDENTS ──────────────────────────────────────────────────

    def show_students(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Student Management",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        controls_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        controls_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(controls_frame, text="Select Branch:", font=('Arial', 12),
                 bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.branch_var = tk.StringVar()
        branch_combo = ttk.Combobox(controls_frame, textvariable=self.branch_var,
                                    values=['CSE', 'ECE', 'MECH', 'AIML', 'RAI', 'MNC'])
        branch_combo.pack(side=tk.LEFT, padx=5)
        branch_combo.set('CSE')

        tk.Button(controls_frame, text="View Students", font=('Arial', 10),
                  bg='#3498db', fg='white', command=self.load_students).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="Add Student", font=('Arial', 10),
                  bg='#2ecc71', fg='white', command=self.add_student_dialog).pack(side=tk.LEFT, padx=5)

        table_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('ID', 'Name', 'Batch', 'Section', 'Semester', 'Branch', 'Email')
        self.students_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        self.students_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_students()

    def load_students(self):
        branch = self.branch_var.get()
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        results, _ = self.execute_query(
            "SELECT student_id, name, batch, section, semester, branch_id, email "
            "FROM students WHERE branch_id = %s", (branch,))
        if results:
            for row in results:
                self.students_tree.insert('', tk.END, values=row)

    def add_student_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("400x380")
        dialog.configure(bg='#ecf0f1')
        tk.Label(dialog, text="Add New Student",
                 font=('Arial', 16, 'bold'), bg='#ecf0f1').pack(pady=10)

        fields = [
            ("Student ID", "student_id"),
            ("Name",       "name"),
            ("Batch",      "batch"),
            ("Section",    "section"),
            ("Semester",   "semester"),
            ("Branch",     "branch"),
            ("Email",      "email"),
            ("Phone",      "phone")
        ]
        entries = {}
        for label, key in fields:
            frame = tk.Frame(dialog, bg='#ecf0f1')
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label, width=10, anchor='w', bg='#ecf0f1').pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[key] = entry

        btn_frame = tk.Frame(dialog, bg='#ecf0f1')
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        tk.Button(btn_frame, text="Save", bg='#2ecc71', fg='white',
                  command=lambda: self.save_student(entries, dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", bg='#e74c3c', fg='white',
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_student(self, entries, dialog):
        """
        FR-07: Validate inputs
        FR-08: Prevent duplicate entries
        Then INSERT — trigger does NOT fire here (no attendance/marks).
        """
        # ── FR-07: Validate ──────────────────────────────────────
        required = ['student_id', 'name', 'branch', 'semester', 'email']
        for field in required:
            if not entries[field].get().strip():
                messagebox.showerror("Validation Error",
                                     f"'{field}' is required.")
                return

        email = entries['email'].get().strip()
        if '@' not in email or '.' not in email:
            messagebox.showerror("Validation Error",
                                 "Enter a valid email address (must contain @ and .)")
            return

        try:
            sem = int(entries['semester'].get().strip())
            if not (1 <= sem <= 8):
                raise ValueError
        except ValueError:
            messagebox.showerror("Validation Error",
                                 "Semester must be a number between 1 and 8.")
            return

        student_id = entries['student_id'].get().strip()

        # ── FR-08: Duplicate check ────────────────────────────────
        result, _ = self.execute_query(
            "SELECT student_id FROM students WHERE student_id = %s", (student_id,))
        if result:
            messagebox.showerror("Duplicate Entry",
                                 f"Student ID '{student_id}' already exists.")
            return

        # ── INSERT ───────────────────────────────────────────────
        try:
            self.execute_query(
                """INSERT INTO students
                   (student_id, name, batch, section, semester,
                    branch_id, email, phone)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (student_id,
                 entries['name'].get().strip(),
                 entries['batch'].get().strip(),
                 entries['section'].get().strip(),
                 sem,
                 entries['branch'].get().strip(),
                 email,
                 entries['phone'].get().strip())
            )
            messagebox.showinfo("Success", "Student added successfully!")
            dialog.destroy()
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")

    # ── ACADEMICS ─────────────────────────────────────────────────

    def show_academics(self, tab='attendance'):
        self.clear_content()
        tk.Label(self.content_frame, text="Academic Records",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        attendance_frame = ttk.Frame(notebook)
        notebook.add(attendance_frame, text='Attendance')
        marks_frame = ttk.Frame(notebook)
        notebook.add(marks_frame, text='Marks')

        self.setup_attendance_tab(attendance_frame)
        self.setup_marks_tab(marks_frame)

        if tab == 'marks':
            notebook.select(1)

    def setup_attendance_tab(self, parent):
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(controls_frame, text="Student ID:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.attendance_id_var = tk.StringVar()
        tk.Entry(controls_frame, textvariable=self.attendance_id_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="View Attendance", bg='#3498db', fg='white',
                  command=self.view_attendance).pack(side=tk.LEFT, padx=5)

        self.attendance_text = scrolledtext.ScrolledText(parent, width=80, height=20)
        self.attendance_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_marks_tab(self, parent):
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(controls_frame, text="Student ID:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.marks_id_var = tk.StringVar()
        tk.Entry(controls_frame, textvariable=self.marks_id_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(controls_frame, text="View Marks", bg='#3498db', fg='white',
                  command=self.view_marks).pack(side=tk.LEFT, padx=5)

        self.marks_text = scrolledtext.ScrolledText(parent, width=80, height=20)
        self.marks_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def view_attendance(self):
        """
        CHANGED: now calls SQL function calculate_attendance_pct()
        per subject row so the DB function is actually exercised.
        Also highlights status based on 75% threshold (FR-13).
        """
        student_id = self.attendance_id_var.get().strip()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID")
            return

        # Per-subject rows using the SQL function
        query = """
            SELECT sub.subject_name,
                   a.attended,
                   a.total,
                   calculate_attendance_pct(a.student_id, a.subject_id) AS pct
            FROM   attendance a
            JOIN   subjects   sub ON a.subject_id = sub.subject_id
            WHERE  a.student_id = %s
        """
        results, _ = self.execute_query(query, (student_id,))

        # Overall summary
        summary_query = """
            SELECT s.name, s.branch_id,
                   SUM(a.attended) AS total_attended,
                   SUM(a.total)    AS total_classes,
                   ROUND(SUM(a.attended) / SUM(a.total) * 100, 2) AS overall_pct
            FROM   attendance a
            JOIN   students   s ON a.student_id = s.student_id
            WHERE  a.student_id = %s
            GROUP  BY s.student_id, s.name, s.branch_id
        """
        summary, _ = self.execute_query(summary_query, (student_id,))

        self.attendance_text.delete(1.0, tk.END)

        if summary:
            data = summary[0]
            overall = float(data[4]) if data[4] else 0
            status = "Good (above 75%)" if overall >= 75 else \
                     "Average (60-74%)" if overall >= 60 else \
                     "LOW - Below 75% Threshold"
            self.attendance_text.insert(tk.END,
                f"ATTENDANCE SUMMARY FOR {data[0]}\n"
                f"Branch: {data[1]}\n"
                f"Classes Attended: {data[2]}/{data[3]}\n"
                f"Overall Percentage: {overall}%\n"
                f"Status: {status}\n"
                f"{'='*50}\n\n"
                f"SUBJECT-WISE BREAKDOWN (via calculate_attendance_pct())\n\n"
            )

        if results:
            for row in results:
                subj, attended, total, pct = row
                pct = float(pct) if pct else 0
                flag = " [ALERT - Below 75%]" if pct < 75 else ""
                self.attendance_text.insert(tk.END,
                    f"Subject : {subj}\n"
                    f"Attended: {attended}/{total} | Percentage: {pct:.2f}%{flag}\n"
                    f"{'-'*40}\n"
                )
        else:
            self.attendance_text.insert(tk.END, "No attendance data found for this student.")

    def view_marks(self):
        """
        Displays marks — total_marks, percentage, grade are already
        filled by after_marks_insert TRIGGER so we just display them.
        """
        student_id = self.marks_id_var.get().strip()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter a Student ID")
            return

        query = """
            SELECT s.name, sub.subject_name,
                   m.t1_marks, m.t2_marks, m.t3_marks, m.ta_marks,
                   m.total_marks, m.percentage, m.grade
            FROM   marks    m
            JOIN   students s   ON m.student_id = s.student_id
            JOIN   subjects sub ON m.subject_id = sub.subject_id
            WHERE  m.student_id = %s
        """
        results, _ = self.execute_query(query, (student_id,))

        self.marks_text.delete(1.0, tk.END)

        if results:
            self.marks_text.insert(tk.END,
                f"MARKS ANALYSIS FOR {results[0][0]}\n"
                f"(total_marks, percentage & grade auto-filled by after_marks_insert trigger)\n"
                f"{'='*60}\n\n"
            )
            total_pct = 0
            for row in results:
                _, subj, t1, t2, t3, ta, total, pct, grade = row
                self.marks_text.insert(tk.END,
                    f"Subject    : {subj}\n"
                    f"Tests      : T1={t1}  T2={t2}  T3={t3}  TA={ta}\n"
                    f"Total      : {total}  |  Percentage: {pct}%  |  Grade: {grade}\n"
                    f"{'-'*40}\n"
                )
                total_pct += float(pct) if pct else 0
            avg = total_pct / len(results)
            self.marks_text.insert(tk.END, f"\nOverall Average: {avg:.2f}%\n")
        else:
            self.marks_text.insert(tk.END, "No marks data found for this student.")

    # ── REPORTS ───────────────────────────────────────────────────

    def show_reports(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Reports & Analytics",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        reports_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        report_buttons = [
            ("Branch Report",       self.generate_branch_report),
            ("Database Statistics", self.show_db_stats),
            ("Student Summary",     self.show_student_summary),
            ("Faculty Summary",     self.show_faculty_summary)
        ]
        for i, (text, command) in enumerate(report_buttons):
            tk.Button(reports_frame, text=text, font=('Arial', 12),
                      bg='#3498db', fg='white', height=3, width=20,
                      command=command).grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            reports_frame.columnconfigure(i % 2, weight=1)
            reports_frame.rowconfigure(i // 2, weight=1)

        self.reports_text = scrolledtext.ScrolledText(self.content_frame, width=80, height=15)
        self.reports_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def generate_branch_report(self):
        results, _ = self.execute_query("""
            SELECT b.branch_id, b.branch_name, COUNT(s.student_id),
                   CASE
                       WHEN COUNT(s.student_id) > 30 THEN 'High'
                       WHEN COUNT(s.student_id) > 15 THEN 'Medium'
                       ELSE 'Low'
                   END AS status
            FROM   branches b
            LEFT JOIN students s ON b.branch_id = s.branch_id
            GROUP  BY b.branch_id, b.branch_name
        """)
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "BRANCH REPORT\n" + "="*50 + "\n\n")
        if results:
            for row in results:
                self.reports_text.insert(tk.END,
                    f"Branch  : {row[1]} ({row[0]})\n"
                    f"Students: {row[2]}\nStatus  : {row[3]}\n"
                    + "-"*30 + "\n")
        else:
            self.reports_text.insert(tk.END, "No data found.")

    def show_db_stats(self):
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "DATABASE STATISTICS\n" + "="*30 + "\n\n")
        total = 0
        for label, table in [
            ("Branches", "branches"), ("Subjects", "subjects"),
            ("Faculty", "faculty"),   ("Students", "students"),
            ("Attendance Records", "attendance"), ("Marks Records", "marks")
        ]:
            result, _ = self.execute_query(f"SELECT COUNT(*) FROM {table}")
            if result:
                count = result[0][0]
                self.reports_text.insert(tk.END, f"{label:22}: {count} records\n")
                total += count
        self.reports_text.insert(tk.END, f"\n{'Total':22}: {total} records\n")

    def show_student_summary(self):
        results, _ = self.execute_query("""
            SELECT s.student_id, s.name, s.branch_id,
                   b.branch_name, s.semester, s.batch
            FROM   students s
            JOIN   branches b ON s.branch_id = b.branch_id
            LIMIT  20
        """)
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "STUDENT SUMMARY (First 20)\n" + "="*60 + "\n\n")
        if results:
            for row in results:
                self.reports_text.insert(tk.END,
                    f"ID: {row[0]}, Name: {row[1]}\n"
                    f"Branch: {row[2]} ({row[3]}), Sem: {row[4]}, Batch: {row[5]}\n"
                    + "-"*40 + "\n")
        else:
            self.reports_text.insert(tk.END, "No student data found.")

    def show_faculty_summary(self):
        results, _ = self.execute_query("""
            SELECT f.faculty_id, f.name, f.designation, b.branch_name
            FROM   faculty  f
            JOIN   branches b ON f.branch_id = b.branch_id
        """)
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "FACULTY SUMMARY\n" + "="*50 + "\n\n")
        if results:
            for row in results:
                self.reports_text.insert(tk.END,
                    f"ID: {row[0]}, Name: {row[1]}\n"
                    f"Designation: {row[2]}, Branch: {row[3]}\n"
                    + "-"*30 + "\n")
        else:
            self.reports_text.insert(tk.END, "No faculty data found.")

    # ── TOOLS ─────────────────────────────────────────────────────

    def show_tools(self):
        self.clear_content()
        tk.Label(self.content_frame, text="System Tools",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        tools_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tool_buttons = [
            ("Test Grade Calculator",   self.test_grade_calculator),
            ("Check Branch Strength",   self.check_branch_strength),
            ("Test Triggers",           self.test_triggers),
            ("Data Validation",         self.data_validation),
            # NEW button — calls the stored procedure with SQL CURSOR
            ("Low Attendance Alert",    self.show_low_attendance),
        ]
        for i, (text, command) in enumerate(tool_buttons):
            tk.Button(tools_frame, text=text, font=('Arial', 12),
                      bg='#95a5a6', fg='white', height=2, width=25,
                      command=command).grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            tools_frame.columnconfigure(i % 2, weight=1)
            tools_frame.rowconfigure(i // 2, weight=1)

    def test_grade_calculator(self):
        """
        FIXED: was calling "CalculateGrade(%s)" which does not exist.
        Now calls "assign_grade(%s)" — the correct function name from database_setup.py.
        """
        percentage = simpledialog.askfloat("Grade Calculator", "Enter percentage (0-100):")
        if percentage is not None:
            try:
                result, _ = self.execute_query(
                    "SELECT assign_grade(%s) AS grade", (percentage,))
                if result:
                    messagebox.showinfo("Grade Result",
                                        f"assign_grade({percentage}%) = {result[0][0]}")
                else:
                    messagebox.showerror("Error", "Could not calculate grade")
            except Exception as e:
                messagebox.showerror("Error", f"MySQL function error: {e}")

    def check_branch_strength(self):
        """
        FIXED: was calling "GetBranchStrength(%s)" which does not exist.
        Now uses a plain COUNT query — clean and reliable.
        """
        branch = simpledialog.askstring("Branch Strength",
                                        "Enter branch code (CSE / ECE / MECH / AIML / RAI / MNC):")
        if branch:
            try:
                result, _ = self.execute_query(
                    "SELECT COUNT(*) FROM students WHERE branch_id = %s", (branch.strip().upper(),))
                if result:
                    messagebox.showinfo("Branch Strength",
                                        f"Total students in {branch.upper()}: {result[0][0]}")
                else:
                    messagebox.showerror("Error", "Branch not found or no students.")
            except Exception as e:
                messagebox.showerror("Error", f"Query error: {e}")

    def test_triggers(self):
        """
        Shows marks rows — total_marks, percentage, grade are auto-filled
        by the after_marks_insert trigger, so they should always be populated.
        """
        results, _ = self.execute_query(
            "SELECT student_id, subject_id, total_marks, percentage, grade "
            "FROM marks LIMIT 3")
        if results:
            text = "TRIGGER TEST — Marks (auto-filled by after_marks_insert trigger)\n\n"
            for row in results:
                text += (f"Student: {row[0]}, Subject: {row[1]}\n"
                         f"Total  : {row[2]}, Percentage: {row[3]}%, Grade: {row[4]}\n"
                         + "-"*40 + "\n")
            messagebox.showinfo("Trigger Test", text)
        else:
            messagebox.showinfo("Trigger Test", "No marks records found.")

    def data_validation(self):
        tables = ['students', 'branches', 'subjects', 'faculty', 'attendance', 'marks']
        text = "DATA VALIDATION CHECK\n\n"
        for table in tables:
            result, _ = self.execute_query(f"SELECT COUNT(*) FROM {table}")
            if result:
                count = result[0][0]
                status = "OK" if count > 0 else "EMPTY"
                text += f"{table:15}: {count:4} records — {status}\n"
        messagebox.showinfo("Data Validation", text)

    def show_low_attendance(self):
        """
        NEW — calls the stored procedure flag_low_attendance() via callproc().
        The procedure uses the SQL CURSOR (student_attendance_cursor) internally
        to loop through all students and log those below 75%.
        Results are then read from low_attendance_log and displayed here.
        Used for FR-13: Attendance Alerts.
        """
        try:
            cursor = self.connection.cursor()

            # This call runs the STORED PROCEDURE which runs the SQL CURSOR inside MySQL
            cursor.callproc('flag_low_attendance')

            # Consume any result sets the procedure may have left
            for _ in cursor.stored_results():
                pass

            cursor.close()

            # Read the results the cursor procedure wrote to low_attendance_log
            results, _ = self.execute_query("""
                SELECT l.student_id, s.name, l.avg_pct
                FROM   low_attendance_log l
                JOIN   students           s ON l.student_id = s.student_id
                ORDER  BY l.avg_pct ASC
            """)

            if results:
                text = ("LOW ATTENDANCE ALERT\n"
                        "(Generated by flag_low_attendance() stored procedure\n"
                        " using student_attendance_cursor SQL CURSOR)\n\n"
                        + "="*50 + "\n\n")
                for row in results:
                    text += (f"Student ID : {row[0]}\n"
                             f"Name       : {row[1]}\n"
                             f"Avg Att.   : {float(row[2]):.2f}% — BELOW 75%\n"
                             + "-"*40 + "\n")
                messagebox.showwarning("Low Attendance Alert", text)
            else:
                messagebox.showinfo("Low Attendance Alert",
                                    "All students are above 75% attendance.")

        except Error as e:
            messagebox.showerror("Error", f"Could not run attendance check: {e}")

    # ── IMPORT DATA ───────────────────────────────────────────────

    def show_import(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Import Data from Excel",
                 font=('Arial', 18, 'bold'), bg='#ecf0f1').pack(pady=20)

        import_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        import_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(import_frame, text="Import data from Excel files in 'minor' folder",
                 font=('Arial', 12), bg='#ecf0f1').pack(pady=10)
        tk.Button(import_frame, text="Import All Data", font=('Arial', 14, 'bold'),
                  bg='#2ecc71', fg='white', height=3,
                  command=self.import_all_data).pack(pady=20)

        self.import_text = scrolledtext.ScrolledText(import_frame, width=80, height=15)
        self.import_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.check_file_status()

    def check_file_status(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'minor')
        files = [
            ('branches.xlsx',   'Branches'),
            ('subjects.xlsx',   'Subjects'),
            ('faculty.xlsx',    'Faculty'),
            ('students.xlsx',   'Students'),
            ('attendance.xlsx', 'Attendance'),
            ('marks.xlsx',      'Marks')
        ]
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, "FILE STATUS CHECK\n" + "="*40 + "\n\n")
        for filename, description in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_excel(filepath)
                    self.import_text.insert(tk.END,
                        f"OK  {description:12} — {len(df):3} records found\n")
                except Exception:
                    self.import_text.insert(tk.END,
                        f"ERR {description:12} — Error reading file\n")
            else:
                self.import_text.insert(tk.END,
                    f"--- {description:12} — File not found\n")

    def import_all_data(self):
        """
        CHANGED for attendance and marks rows:

        Attendance: we NO LONGER pass 'percentage' column.
            The after_attendance_insert TRIGGER calculates and stores it automatically.

        Marks: we NO LONGER pass 'total_marks', 'percentage', 'grade'.
            The after_marks_insert TRIGGER calls get_total_marks() and assign_grade()
            and fills those columns automatically after each INSERT.
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, 'minor')

            if not os.path.exists(folder_path):
                messagebox.showerror("Error", "'minor' folder not found!")
                return

            files_imported = 0
            total_records  = 0

            self.import_text.delete(1.0, tk.END)
            self.import_text.insert(tk.END, "IMPORTING DATA...\n" + "="*40 + "\n\n")

            # 1. Branches
            branches_file = os.path.join(folder_path, 'branches.xlsx')
            if os.path.exists(branches_file):
                df = pd.read_excel(branches_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO branches "
                        "(branch_id, branch_name, duration_years) VALUES (%s, %s, %s)",
                        (row['branch_id'], row['branch_name'], row['duration_years'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Branches   — {len(df):3} records imported\n")
                files_imported += 1
                total_records  += len(df)

            # 2. Subjects
            subjects_file = os.path.join(folder_path, 'subjects.xlsx')
            if os.path.exists(subjects_file):
                df = pd.read_excel(subjects_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO subjects "
                        "(subject_id, subject_name, branch_id, semester, credits, is_lab) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['subject_id'], row['subject_name'], row['branch_id'],
                         row['semester'], row['credits'], row['is_lab'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Subjects   — {len(df):3} records imported\n")
                files_imported += 1
                total_records  += len(df)

            # 3. Faculty
            faculty_file = os.path.join(folder_path, 'faculty.xlsx')
            if os.path.exists(faculty_file):
                df = pd.read_excel(faculty_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO faculty "
                        "(faculty_id, name, email, phone, branch_id, designation) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['faculty_id'], row['name'], row['email'],
                         row['phone'], row['branch_id'], row['designation'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Faculty    — {len(df):3} records imported\n")
                files_imported += 1
                total_records  += len(df)

            # 4. Students
            students_file = os.path.join(folder_path, 'students.xlsx')
            if os.path.exists(students_file):
                df = pd.read_excel(students_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO students "
                        "(student_id, name, batch, section, semester, "
                        " branch_id, email, phone) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['name'], row['batch'],
                         row['section'], row['semester'], row['branch_id'],
                         row['email'], row['phone'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Students   — {len(df):3} records imported\n")
                files_imported += 1
                total_records  += len(df)

            # 5. Attendance — CHANGED: omit 'percentage' column
            #    after_attendance_insert TRIGGER fills it automatically
            attendance_file = os.path.join(folder_path, 'attendance.xlsx')
            if os.path.exists(attendance_file):
                df = pd.read_excel(attendance_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO attendance "
                        "(student_id, subject_id, attended, total, faculty_id) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'],
                         row['attended'], row['total'], row['faculty_id'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Attendance — {len(df):3} records imported "
                    f"(percentage auto-set by trigger)\n")
                files_imported += 1
                total_records  += len(df)

            # 6. Marks — CHANGED: omit 'total_marks', 'percentage', 'grade'
            #    after_marks_insert TRIGGER fills them automatically
            marks_file = os.path.join(folder_path, 'marks.xlsx')
            if os.path.exists(marks_file):
                df = pd.read_excel(marks_file)
                for _, row in df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO marks "
                        "(student_id, subject_id, t1_marks, t2_marks, t3_marks, ta_marks) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'],
                         row['t1_marks'], row['t2_marks'],
                         row['t3_marks'], row['ta_marks'])
                    )
                self.import_text.insert(tk.END,
                    f"OK  Marks      — {len(df):3} records imported "
                    f"(total/pct/grade auto-set by trigger)\n")
                files_imported += 1
                total_records  += len(df)

            self.import_text.insert(tk.END,
                "="*40 + "\n"
                f"Import completed: {files_imported}/6 files, "
                f"{total_records} total records\n"
            )
            messagebox.showinfo("Success", "Data imported successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")

    # ── EXIT ──────────────────────────────────────────────────────

    def exit_app(self):
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.disconnect()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementGUI(root)
    root.mainloop()