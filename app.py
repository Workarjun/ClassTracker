from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_NAME = 'attendance.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                present INTEGER,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                present INTEGER,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    conn.close()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('INSERT INTO students (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    if request.method == 'POST':
        date = request.form['date']
        for student in students:
            present = 1 if request.form.get(f'present_{student[0]}') == 'on' else 0
            c.execute('INSERT INTO attendance (student_id, date, present) VALUES (?, ?, ?)',
                      (student[0], date, present))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return render_template('attendance.html', students=students)

@app.route('/records')
def records():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT students.name, attendance.date, attendance.present
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    ''')
    records = c.fetchall()
    conn.close()
    return render_template('records.html', records=records)

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        c.execute('UPDATE students SET name = ? WHERE id = ?', (name, student_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    c.execute('SELECT * FROM students WHERE id = ?', (student_id,))
    student = c.fetchone()
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    c.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)