from flask import Flask, request, render_template
import fitz  # PyMuPDF
from analyse_pdf import analyse_resume_gemini
import os
import time
import json
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        name TEXT,
        skills TEXT,
        experience TEXT,
        education TEXT,
        match_score INTEGER,
        selection_status TEXT,
        job_description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()


def extract_text_from_resume(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume_files = request.files.getlist('resumes')
        job_description = request.form["job_description"]

        results = []
        for resume_file in resume_files:
            if resume_file.filename and resume_file.filename.endswith(".pdf"):
                # Use timestamp to avoid filename conflicts
                timestamp = str(int(time.time() * 1000000))  # microsecond precision
                filename = f"{timestamp}_{resume_file.filename}"
                pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume_file.save(pdf_path)

                resume_content = extract_text_from_resume(pdf_path)
                result_str = analyse_resume_gemini(resume_content, job_description)
                result = json.loads(result_str)
                result['resume_id'] = len(results) + 1

                results.append(result)

        # Save to database
        conn = sqlite3.connect('results.db')
        c = conn.cursor()
        for result in results:
            c.execute('''INSERT INTO results (resume_id, name, skills, experience, education, match_score, selection_status, job_description)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (result['resume_id'], result['name'], json.dumps(result['skills']), result['experience'], result['education'], result['match_score'], result['selection_status'], job_description))
        conn.commit()
        conn.close()

        return render_template("index.html", results=results)

    return render_template("index.html", results=None)


@app.route('/results')
def view_results():
    conn = sqlite3.connect('results.db')
    c = conn.cursor()
    c.execute('SELECT * FROM results ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    # Convert to dict list
    results_list = []
    for row in rows:
        results_list.append({
            'id': row[0],
            'resume_id': row[1],
            'name': row[2],
            'skills': json.loads(row[3]),
            'experience': row[4],
            'education': row[5],
            'match_score': row[6],
            'selection_status': row[7],
            'job_description': row[8],
            'timestamp': row[9]
        })
    return render_template('results.html', results=results_list)

if __name__ == "__main__":
    app.run(debug=True)
