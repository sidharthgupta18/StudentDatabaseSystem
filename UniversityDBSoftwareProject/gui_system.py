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
                password='DATABASE PASSWORD',
                database='university_db',
                autocommit=True
            )
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None):
        """Execute SQL query and return results"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            return results, columns
        except Error as e:
            messagebox.showerror("Database Error", f"Query error: {e}")
            return None, None

    def setup_gui(self):
        """Setup the main GUI"""
      
        header_frame = tk.Frame(self.root, bg='#34495e', height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎓 Student Management System", 
                              font=('Arial', 20, 'bold'), fg='white', bg='#34495e')
        title_label.pack(pady=20)
        
       
        main_container = tk.Frame(self.root, bg='#2c3e50')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
      
        self.setup_sidebar(main_container)
        
    
        self.setup_content_area(main_container)
        
    def setup_sidebar(self, parent):
        """Setup navigation sidebar"""
        sidebar_frame = tk.Frame(parent, bg='#34495e', width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)
  
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Students", self.show_students),
            ("📚 Academics", self.show_academics),
            ("📈 Reports", self.show_reports),
            ("🛠️ Tools", self.show_tools),
            ("📤 Import Data", self.show_import),
            ("❌ Exit", self.exit_app)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(sidebar_frame, text=text, font=('Arial', 12),
                           bg='#3498db', fg='white', relief='flat', height=2,
                           command=command, anchor='w', padx=20)
            btn.pack(fill=tk.X, padx=10, pady=5)
        
    def setup_content_area(self, parent):
        """Setup main content area"""
        self.content_frame = tk.Frame(parent, bg='#ecf0f1')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
       
        self.show_dashboard()
    
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard"""
        self.clear_content()
        
    
        header = tk.Label(self.content_frame, text="📊 Dashboard", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)
      
        stats_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_data = self.get_statistics()
        
        stats_cards = [
            ("👥 Students", stats_data['students'], '#e74c3c'),
            ("👨‍🏫 Faculty", stats_data['faculty'], '#3498db'),
            ("🏛️ Branches", stats_data['branches'], '#2ecc71'),
            ("📚 Subjects", stats_data['subjects'], '#f39c12')
        ]
        
        for i, (title, count, color) in enumerate(stats_cards):
            card = tk.Frame(stats_frame, bg=color, relief='raised', bd=1)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            count_label = tk.Label(card, text=str(count), font=('Arial', 24, 'bold'), 
                                  bg=color, fg='white')
            count_label.pack(pady=10)
            
            title_label = tk.Label(card, text=title, font=('Arial', 12), 
                                  bg=color, fg='white')
            title_label.pack(pady=5)
            
            stats_frame.columnconfigure(i, weight=1)
        
        
        actions_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        actions_label = tk.Label(actions_frame, text="Quick Actions", 
                               font=('Arial', 14, 'bold'), bg='#ecf0f1')
        actions_label.pack(anchor='w')
        
        action_buttons = [
            ("View Students", self.show_students),
            ("Check Attendance", lambda: self.show_academics('attendance')),
            ("View Marks", lambda: self.show_academics('marks')),
            ("Generate Report", self.show_reports)
        ]
        
        for text, command in action_buttons:
            btn = tk.Button(actions_frame, text=text, font=('Arial', 10),
                           bg='#95a5a6', fg='white', command=command)
            btn.pack(side=tk.LEFT, padx=5, pady=10)
    
    def get_statistics(self):
        """Get database statistics"""
        stats = {
            'students': 0,
            'faculty': 0,
            'branches': 0,
            'subjects': 0
        }
        
        queries = {
            'students': "SELECT COUNT(*) FROM students",
            'faculty': "SELECT COUNT(*) FROM faculty",
            'branches': "SELECT COUNT(*) FROM branches",
            'subjects': "SELECT COUNT(*) FROM subjects"
        }
        
        for key, query in queries.items():
            result, _ = self.execute_query(query)
            if result:
                stats[key] = result[0][0]
        
        return stats
    
    def show_students(self):
        """Show students management"""
        self.clear_content()
        
        header = tk.Label(self.content_frame, text="👥 Student Management", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)
        
        
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
        """Load students data"""
        branch = self.branch_var.get()
        
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)

        query = "SELECT student_id, name, batch, section, semester, branch_id, email FROM students WHERE branch_id = %s"
        results, _ = self.execute_query(query, (branch,))
        
        if results:
            for row in results:
                self.students_tree.insert('', tk.END, values=row)
    
    def add_student_dialog(self):
        """Dialog to add new student"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("400x300")
        dialog.configure(bg='#ecf0f1')
        
        tk.Label(dialog, text="Add New Student", font=('Arial', 16, 'bold'), 
                bg='#ecf0f1').pack(pady=10)
        
        fields = [
            ("Student ID", "student_id"),
            ("Name", "name"),
            ("Batch", "batch"),
            ("Section", "section"),
            ("Semester", "semester"),
            ("Branch", "branch"),
            ("Email", "email"),
            ("Phone", "phone")
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            frame = tk.Frame(dialog, bg='#ecf0f1')
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=label, width=10, anchor='w', bg='#ecf0f1').pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[key] = entry
        
      
        button_frame = tk.Frame(dialog, bg='#ecf0f1')
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(button_frame, text="Save", bg='#2ecc71', fg='white',
                 command=lambda: self.save_student(entries, dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", bg='#e74c3c', fg='white',
                 command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_student(self, entries, dialog):
        """Save new student to database"""
        try:
            query = """INSERT INTO students (student_id, name, batch, section, semester, branch_id, email, phone) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                entries['student_id'].get(),
                entries['name'].get(),
                entries['batch'].get(),
                entries['section'].get(),
                entries['semester'].get(),
                entries['branch'].get(),
                entries['email'].get(),
                entries['phone'].get()
            )
            
            self.execute_query(query, values)
            messagebox.showinfo("Success", "Student added successfully!")
            dialog.destroy()
            self.load_students()  
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {e}")
    
    def show_academics(self, tab='attendance'):
        """Show academics section"""
        self.clear_content()
        
        header = tk.Label(self.content_frame, text="📚 Academic Records", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)
        
       
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        

        attendance_frame = ttk.Frame(notebook)
        notebook.add(attendance_frame, text='📅 Attendance')
        
        
        marks_frame = ttk.Frame(notebook)
        notebook.add(marks_frame, text='📊 Marks')
        
      
        self.setup_attendance_tab(attendance_frame)
        
        
        self.setup_marks_tab(marks_frame)
        
        
        if tab == 'marks':
            notebook.select(1)
    
    def setup_attendance_tab(self, parent):
        """Setup attendance tab"""
        
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(controls_frame, text="Student ID:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.attendance_id_var = tk.StringVar()
        entry = tk.Entry(controls_frame, textvariable=self.attendance_id_var, width=20)
        entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="View Attendance", bg='#3498db', fg='white',
                 command=self.view_attendance).pack(side=tk.LEFT, padx=5)
        
        
        self.attendance_text = scrolledtext.ScrolledText(parent, width=80, height=20)
        self.attendance_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_marks_tab(self, parent):
        """Setup marks tab"""
        
        controls_frame = tk.Frame(parent, bg='#ecf0f1')
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(controls_frame, text="Student ID:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.marks_id_var = tk.StringVar()
        entry = tk.Entry(controls_frame, textvariable=self.marks_id_var, width=20)
        entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(controls_frame, text="View Marks", bg='#3498db', fg='white',
                 command=self.view_marks).pack(side=tk.LEFT, padx=5)
        
        
        self.marks_text = scrolledtext.ScrolledText(parent, width=80, height=20)
        self.marks_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def view_attendance(self):
        """View student attendance"""
        student_id = self.attendance_id_var.get()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter Student ID")
            return
        
        query = """
        SELECT s.name, s.branch_id, 
               SUM(a.attended) as total_attended,
               SUM(a.total) as total_classes,
               ROUND((SUM(a.attended) / SUM(a.total)) * 100, 2) as overall_percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.student_id = %s
        GROUP BY s.student_id, s.name, s.branch_id
        """
        
        results, _ = self.execute_query(query, (student_id,))
        
        self.attendance_text.delete(1.0, tk.END)
        
        if results:
            data = results[0]
            text = f"""ATTENDANCE SUMMARY FOR {data[0]}

Branch: {data[1]}
Classes Attended: {data[2]}/{data[3]}
Overall Percentage: {data[4]}%

Attendance Status: {'✅ Good' if data[4] >= 75 else '⚠️ Average' if data[4] >= 60 else '❌ Low'}
"""
            self.attendance_text.insert(tk.END, text)
        else:
            self.attendance_text.insert(tk.END, "No attendance data found for this student.")
    
    def view_marks(self):
        """View student marks"""
        student_id = self.marks_id_var.get()
        if not student_id:
            messagebox.showwarning("Warning", "Please enter Student ID")
            return
        
        query = """
        SELECT s.name, sub.subject_name, m.t1_marks, m.t2_marks, m.t3_marks, 
               m.total_marks, m.percentage, m.grade
        FROM marks m
        JOIN students s ON m.student_id = s.student_id
        JOIN subjects sub ON m.subject_id = sub.subject_id
        WHERE m.student_id = %s
        """
        
        results, _ = self.execute_query(query, (student_id,))
        
        self.marks_text.delete(1.0, tk.END)
        
        if results:
            text = f"MARKS ANALYSIS FOR {results[0][0]}\n\n"
            text += "="*60 + "\n"
            
            total_percentage = 0
            for row in results:
                text += f"\nSubject: {row[1]}\n"
                text += f"Tests: T1={row[2]}, T2={row[3]}, T3={row[4]}\n"
                text += f"Total: {row[5]}, Percentage: {row[6]}%, Grade: {row[7]}\n"
                text += "-"*40 + "\n"
                total_percentage += row[6]
            
            avg_percentage = total_percentage / len(results)
            text += f"\nOverall Average: {avg_percentage:.2f}%\n"
            
            self.marks_text.insert(tk.END, text)
        else:
            self.marks_text.insert(tk.END, "No marks data found for this student.")
    
    def show_reports(self):
        """Show reports section"""
        self.clear_content()
        
        header = tk.Label(self.content_frame, text="📈 Reports & Analytics", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)
        
        
        reports_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        report_buttons = [
            ("Branch Report", self.generate_branch_report),
            ("Database Statistics", self.show_db_stats),
            ("Student Summary", self.show_student_summary),
            ("Faculty Summary", self.show_faculty_summary)
        ]
        
        for i, (text, command) in enumerate(report_buttons):
            btn = tk.Button(reports_frame, text=text, font=('Arial', 12),
                           bg='#3498db', fg='white', height=3, width=20,
                           command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            
            reports_frame.columnconfigure(i%2, weight=1)
            reports_frame.rowconfigure(i//2, weight=1)
        
        
        self.reports_text = scrolledtext.ScrolledText(self.content_frame, width=80, height=15)
        self.reports_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def generate_branch_report(self):
        """Generate branch report"""
        query = """
        SELECT b.branch_id, b.branch_name, COUNT(s.student_id),
               CASE 
                   WHEN COUNT(s.student_id) > 30 THEN 'High'
                   WHEN COUNT(s.student_id) > 15 THEN 'Medium' 
                   ELSE 'Low'
               END as status
        FROM branches b
        LEFT JOIN students s ON b.branch_id = s.branch_id
        GROUP BY b.branch_id, b.branch_name
        """
        
        results, _ = self.execute_query(query)
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "BRANCH REPORT\n")
        self.reports_text.insert(tk.END, "="*50 + "\n\n")
        
        if results:
            for row in results:
                self.reports_text.insert(tk.END, f"Branch: {row[1]} ({row[0]})\n")
                self.reports_text.insert(tk.END, f"Students: {row[2]}\n")
                self.reports_text.insert(tk.END, f"Status: {row[3]}\n")
                self.reports_text.insert(tk.END, "-"*30 + "\n")
        else:
            self.reports_text.insert(tk.END, "No data found for report.")
    
    def show_db_stats(self):
        """Show database statistics"""
        stats_queries = [
            ("Branches", "SELECT COUNT(*) FROM branches"),
            ("Subjects", "SELECT COUNT(*) FROM subjects"),
            ("Faculty", "SELECT COUNT(*) FROM faculty"),
            ("Students", "SELECT COUNT(*) FROM students"),
            ("Attendance Records", "SELECT COUNT(*) FROM attendance"),
            ("Marks Records", "SELECT COUNT(*) FROM marks")
        ]
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "DATABASE STATISTICS\n")
        self.reports_text.insert(tk.END, "="*30 + "\n\n")
        
        total_records = 0
        for label, query in stats_queries:
            result, _ = self.execute_query(query)
            if result:
                count = result[0][0]
                self.reports_text.insert(tk.END, f"{label:20}: {count} records\n")
                total_records += count
        
        self.reports_text.insert(tk.END, f"\n{'Total Records':20}: {total_records} records\n")
    
    def show_student_summary(self):
        """Show student summary"""
        query = """
        SELECT s.student_id, s.name, s.branch_id, b.branch_name, s.semester, s.batch
        FROM students s
        JOIN branches b ON s.branch_id = b.branch_id
        LIMIT 20
        """
        
        results, _ = self.execute_query(query)
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "STUDENT SUMMARY (First 20)\n")
        self.reports_text.insert(tk.END, "="*60 + "\n\n")
        
        if results:
            for row in results:
                self.reports_text.insert(tk.END, f"ID: {row[0]}, Name: {row[1]}\n")
                self.reports_text.insert(tk.END, f"Branch: {row[2]} ({row[3]}), Sem: {row[4]}, Batch: {row[5]}\n")
                self.reports_text.insert(tk.END, "-"*40 + "\n")
        else:
            self.reports_text.insert(tk.END, "No student data found.")
    
    def show_faculty_summary(self):
        """Show faculty summary"""
        query = """
        SELECT f.faculty_id, f.name, f.designation, b.branch_name
        FROM faculty f
        JOIN branches b ON f.branch_id = b.branch_id
        """
        
        results, _ = self.execute_query(query)
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, "FACULTY SUMMARY\n")
        self.reports_text.insert(tk.END, "="*50 + "\n\n")
        
        if results:
            for row in results:
                self.reports_text.insert(tk.END, f"ID: {row[0]}, Name: {row[1]}\n")
                self.reports_text.insert(tk.END, f"Designation: {row[2]}, Branch: {row[3]}\n")
                self.reports_text.insert(tk.END, "-"*30 + "\n")
        else:
            self.reports_text.insert(tk.END, "No faculty data found.")
    
    def show_tools(self):
        """Show system tools"""
        self.clear_content()
        
        header = tk.Label(self.content_frame, text="🛠️ System Tools", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)

        tools_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tool_buttons = [
            ("Test Grade Calculator", self.test_grade_calculator),
            ("Check Branch Strength", self.check_branch_strength),
            ("Test Triggers", self.test_triggers),
            ("Data Validation", self.data_validation)
        ]
        
        for i, (text, command) in enumerate(tool_buttons):
            btn = tk.Button(tools_frame, text=text, font=('Arial', 12),
                           bg='#95a5a6', fg='white', height=2, width=25,
                           command=command)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            
            tools_frame.columnconfigure(i%2, weight=1)
            tools_frame.rowconfigure(i//2, weight=1)
    
    def test_grade_calculator(self):
        """Test grade calculator function using MySQL"""
        percentage = simpledialog.askfloat("Grade Calculator", "Enter percentage (0-100):")
        if percentage is not None:
            try:
                
                query = "SELECT CalculateGrade(%s) as grade"
                result, _ = self.execute_query(query, (percentage,))
                if result:
                    messagebox.showinfo("Grade Result", f"Grade for {percentage}%: {result[0][0]}")
                else:
                    messagebox.showerror("Error", "Could not calculate grade")
            except Exception as e:
                messagebox.showerror("Error", f"MySQL function error: {e}")
    
    def check_branch_strength(self):
        """Check branch strength using MySQL function"""
        branch = simpledialog.askstring("Branch Strength", "Enter branch code (CSE, ECE, MECH, etc.):")
        if branch:
            try:
                
                query = "SELECT GetBranchStrength(%s) as strength"
                result, _ = self.execute_query(query, (branch,))
                if result:
                    messagebox.showinfo("Branch Strength", f"Total students in {branch}: {result[0][0]}")
                else:
                    messagebox.showerror("Error", "Could not get branch strength")
            except Exception as e:
                messagebox.showerror("Error", f"MySQL function error: {e}")
    
    def test_triggers(self):
        """Test triggers"""
        query = "SELECT student_id, subject_id, total_marks, percentage, grade FROM marks LIMIT 3"
        results, _ = self.execute_query(query)
        
        if results:
            text = "TRIGGER TEST - Marks Data (First 3 records):\n\n"
            for row in results:
                text += f"Student: {row[0]}, Subject: {row[1]}\n"
                text += f"Total: {row[2]}, Percentage: {row[3]}%, Grade: {row[4]}\n"
                text += "-"*40 + "\n"
            
            messagebox.showinfo("Trigger Test", text)
    
    def data_validation(self):
        """Data validation check"""
        tables = ['students', 'branches', 'subjects', 'faculty', 'attendance', 'marks']
        text = "DATA VALIDATION CHECK\n\n"
        
        for table in tables:
            result, _ = self.execute_query(f"SELECT COUNT(*) FROM {table}")
            if result:
                count = result[0][0]
                status = "✅ OK" if count > 0 else "❌ EMPTY"
                text += f"{table:15}: {count:4} records - {status}\n"
        
        messagebox.showinfo("Data Validation", text)
    
    def show_import(self):
        """Show import data section"""
        self.clear_content()
        
        header = tk.Label(self.content_frame, text="📤 Import Data from Excel", 
                         font=('Arial', 18, 'bold'), bg='#ecf0f1')
        header.pack(pady=20)
        
        
        import_frame = tk.Frame(self.content_frame, bg='#ecf0f1')
        import_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(import_frame, text="Import data from Excel files in 'minor' folder", 
                font=('Arial', 12), bg='#ecf0f1').pack(pady=10)

        tk.Button(import_frame, text="🚀 Import All Data", font=('Arial', 14, 'bold'),
                 bg='#2ecc71', fg='white', height=3, command=self.import_all_data).pack(pady=20)

        self.import_text = scrolledtext.ScrolledText(import_frame, width=80, height=15)
        self.import_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.check_file_status()
    
    def check_file_status(self):
        """Check Excel file status"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_dir, 'minor')
        
        files = [
            ('branches.xlsx', 'Branches'),
            ('subjects.xlsx', 'Subjects'), 
            ('faculty.xlsx', 'Faculty'),
            ('students.xlsx', 'Students'),
            ('attendance.xlsx', 'Attendance'),
            ('marks.xlsx', 'Marks')
        ]
        
        self.import_text.delete(1.0, tk.END)
        self.import_text.insert(tk.END, "FILE STATUS CHECK\n")
        self.import_text.insert(tk.END, "="*40 + "\n\n")
        
        for filename, description in files:
            filepath = os.path.join(folder_path, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_excel(filepath)
                    self.import_text.insert(tk.END, f"✅ {description:12} - {len(df):3} records found\n")
                except:
                    self.import_text.insert(tk.END, f"❌ {description:12} - Error reading file\n")
            else:
                self.import_text.insert(tk.END, f"❌ {description:12} - File not found\n")
    
    def import_all_data(self):
        """Import all data from Excel files"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, 'minor')
            
            if not os.path.exists(folder_path):
                messagebox.showerror("Error", "'minor' folder not found!")
                return
            
            files_imported = 0
            total_records = 0
            
            self.import_text.delete(1.0, tk.END)
            self.import_text.insert(tk.END, "IMPORTING DATA...\n")
            self.import_text.insert(tk.END, "="*40 + "\n\n")

            branches_file = os.path.join(folder_path, 'branches.xlsx')
            if os.path.exists(branches_file):
                branches_df = pd.read_excel(branches_file)
                for _, row in branches_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO branches (branch_id, branch_name, duration_years) VALUES (%s, %s, %s)",
                        (row['branch_id'], row['branch_name'], row['duration_years'])
                    )
                self.import_text.insert(tk.END, f"✅ Branches     - {len(branches_df):3} records imported\n")
                files_imported += 1
                total_records += len(branches_df)

            subjects_file = os.path.join(folder_path, 'subjects.xlsx')
            if os.path.exists(subjects_file):
                subjects_df = pd.read_excel(subjects_file)
                for _, row in subjects_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO subjects (subject_id, subject_name, branch_id, semester, credits, is_lab) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['subject_id'], row['subject_name'], row['branch_id'], row['semester'], row['credits'], row['is_lab'])
                    )
                self.import_text.insert(tk.END, f"✅ Subjects     - {len(subjects_df):3} records imported\n")
                files_imported += 1
                total_records += len(subjects_df)

            faculty_file = os.path.join(folder_path, 'faculty.xlsx')
            if os.path.exists(faculty_file):
                faculty_df = pd.read_excel(faculty_file)
                for _, row in faculty_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO faculty (faculty_id, name, email, phone, branch_id, designation) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['faculty_id'], row['name'], row['email'], row['phone'], row['branch_id'], row['designation'])
                    )
                self.import_text.insert(tk.END, f"✅ Faculty      - {len(faculty_df):3} records imported\n")
                files_imported += 1
                total_records += len(faculty_df)
  
            students_file = os.path.join(folder_path, 'students.xlsx')
            if os.path.exists(students_file):
                students_df = pd.read_excel(students_file)
                for _, row in students_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO students (student_id, name, batch, section, semester, branch_id, email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['name'], row['batch'], row['section'], row['semester'], row['branch_id'], row['email'], row['phone'])
                    )
                self.import_text.insert(tk.END, f"✅ Students     - {len(students_df):3} records imported\n")
                files_imported += 1
                total_records += len(students_df)

            attendance_file = os.path.join(folder_path, 'attendance.xlsx')
            if os.path.exists(attendance_file):
                attendance_df = pd.read_excel(attendance_file)
                for _, row in attendance_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO attendance (student_id, subject_id, attended, total, percentage, faculty_id) VALUES (%s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'], row['attended'], row['total'], row['percentage'], row['faculty_id'])
                    )
                self.import_text.insert(tk.END, f"✅ Attendance   - {len(attendance_df):3} records imported\n")
                files_imported += 1
                total_records += len(attendance_df)

            marks_file = os.path.join(folder_path, 'marks.xlsx')
            if os.path.exists(marks_file):
                marks_df = pd.read_excel(marks_file)
                for _, row in marks_df.iterrows():
                    self.execute_query(
                        "INSERT IGNORE INTO marks (student_id, subject_id, t1_marks, t2_marks, t3_marks, ta_marks, total_marks, percentage, grade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (row['student_id'], row['subject_id'], row['t1_marks'], row['t2_marks'], row['t3_marks'], row['ta_marks'], row['total_marks'], row['percentage'], row['grade'])
                    )
                self.import_text.insert(tk.END, f"✅ Marks        - {len(marks_df):3} records imported\n")
                files_imported += 1
                total_records += len(marks_df)
            
            self.import_text.insert(tk.END, "="*40 + "\n")
            self.import_text.insert(tk.END, f"✅ Import completed: {files_imported}/6 files, {total_records} total records\n")
            messagebox.showinfo("Success", "Data imported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.disconnect()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementGUI(root)
    root.mainloop()