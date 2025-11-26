from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def init_db():
    conn = sqlite3.connect('results.db')
    return conn

# Function for teacher login
def login_teacher(conn, email, password):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM teachers WHERE email = ? AND password = ?', (email, password))
    return cursor.fetchone()

# Fetch classes and subjects for a teacher
def fetch_classes_subjects(conn, teacher_id):
    cursor = conn.cursor()
    cursor.execute('SELECT class_name, subject_name FROM classes_subjects WHERE teacher_id = ?', (teacher_id,))
    return cursor.fetchall()

# Fetch results for a specific class and subject
def fetch_results_for_class_subject(conn, teacher_id, class_name, subject_name):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT student_name, total_marks, max_marks
        FROM results
        WHERE teacher_id = (SELECT id FROM teachers WHERE id = ?)
        AND class_name = ? AND subject_name = ?
    ''', (teacher_id, class_name, subject_name))
    return cursor.fetchall()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = init_db()
        teacher = login_teacher(conn, email, password)
        conn.close()

        if teacher:
            session['teacher_id'] = teacher[0]
            session['teacher_name'] = teacher[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Invalid login credentials.")

    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('index'))

    teacher_id = session['teacher_id']
    teacher_name = session['teacher_name']
    conn = init_db()
    classes_subjects = fetch_classes_subjects(conn, teacher_id)
    conn.close()

    if request.method == 'POST':
        selected_option = request.form.get('class_subject')
        if selected_option:
            class_name, subject_name = selected_option.split(" - ")
            conn = init_db()
            results = fetch_results_for_class_subject(conn, teacher_id, class_name, subject_name)
            conn.close()
            return render_template(
                'dashboard.html',
                teacher_name=teacher_name,
                classes_subjects=classes_subjects,
                selected_class=class_name,
                selected_subject=subject_name,
                results=results
            )

    return render_template('dashboard.html', teacher_name=teacher_name, classes_subjects=classes_subjects)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
