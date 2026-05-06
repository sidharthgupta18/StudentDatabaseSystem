# 🎓 Student Management System

A complete **Student Management System** built using **Python (Tkinter GUI)** and **MySQL**, with support for Excel-based data import, attendance tracking, and marks analysis.

---

## 🚀 Features

* 📊 Dashboard with real-time statistics
* 👥 Student management (add, view, filter)
* 📚 Academic records (attendance & marks)
* 📈 Reports & analytics
* 📤 Import data from Excel files
* 🛠️ Built-in tools (grade calculator, validation)
* 🗄️ MySQL database integration

---

## 🏗️ Tech Stack

* **Frontend (GUI):** Tkinter (Python)
* **Backend:** Python
* **Database:** MySQL
* **Data Handling:** Pandas
* **File Input:** Excel (.xlsx)

---

## 📂 Project Structure

```
project/
│
├── database_setup.py      # Creates database & tables
├── import_data.py         # Imports Excel data into MySQL
├── gui.py                 # Main GUI application
├── minor/                 # Excel files folder
│   ├── branches.xlsx
│   ├── students.xlsx
│   ├── subjects.xlsx
│   ├── faculty.xlsx
│   ├── attendance.xlsx
│   └── marks.xlsx
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies

```
pip install pandas mysql-connector-python openpyxl
```

### 3. Configure MySQL

Update your MySQL password in:

* database_setup.py
* import_data.py
* gui.py

```
password = 'YOUR_PASSWORD'
```

---

### 4. Run Database Setup

```
python database_setup.py
```

---

### 5. Import Excel Data

Make sure the `minor/` folder contains all Excel files, then run:

```
python import_data.py
```

---

### 6. Run the GUI

```
python gui.py
```

---

## 📊 Database Schema

The system includes:

* Branches
* Students
* Subjects
* Faculty
* Attendance
* Marks

All connected using **foreign key relationships**.

---

## ⚠️ Important Notes

* Ensure MySQL server is running
* Excel files must follow correct format
* Use valid branch IDs (CSE, ECE, etc.)

---

## 👨‍💻 Author

Sidharth Gupta

---

## 📌 Future Improvements

* Web version (Flask/Django)
* Authentication system
* Graphs & charts
* Deployment

---

## ⭐ If you found this useful, consider giving it a star!
