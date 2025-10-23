from flask import Flask, request, render_template # type: ignore
import fitz  # type: ignore # PyMuPDF
from analyse_pdf import analyse_resume_gemini
import os
import time
import json
import sqlite3
import re

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
        justification TEXT,
        job_description TEXT,
        resume_content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    # Add missing columns if they don't exist (for backward compatibility)
    try:
        c.execute('ALTER TABLE results ADD COLUMN justification TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    try:
        c.execute('ALTER TABLE results ADD COLUMN resume_content TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

init_db()


def extract_text_from_resume(file_path):
    if file_path.endswith('.pdf'):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file type")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        resume_files = request.files.getlist('resumes')
        job_description = request.form["job_description"]

        results = []
        for resume_file in resume_files:
            if resume_file.filename and (resume_file.filename.endswith(".pdf") or resume_file.filename.endswith(".txt")):
                # Use timestamp to avoid filename conflicts
                timestamp = str(int(time.time() * 1000000))  # microsecond precision
                filename = f"{timestamp}_{resume_file.filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume_file.save(file_path)

                resume_content = extract_text_from_resume(file_path)
                result_str = analyse_resume_gemini(resume_content, job_description)
                try:
                    result = json.loads(result_str)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Raw response: {result_str}")
                    # Fallback to default values
                    result = {
                        'name': 'Error parsing name',
                        'skills': [],
                        'experience': 'Error parsing experience',
                        'education': 'Error parsing education',
                        'match_score': 0,
                        'selection_status': 'Not Selected',
                        'justification': 'Error in analysis'
                    }
                result['resume_id'] = len(results) + 1

                # Keyword overlap adjustment for stricter scoring
                jd_keywords = set(re.findall(r'\b\w+\b', job_description.lower()))
                resume_words = set(re.findall(r'\b\w+\b', resume_content.lower()))
                overlap_count = len(jd_keywords.intersection(resume_words))
                overlap_ratio = overlap_count / len(jd_keywords) if jd_keywords else 0
                print(f"JD keywords: {jd_keywords}, Overlap count: {overlap_count}, Ratio: {overlap_ratio}, AI score: {result['match_score']}")
                if overlap_ratio == 1.0:  # Full overlap
                    result['match_score'] = max(result['match_score'], 90)  # Boost to at least 90
                elif overlap_ratio >= 0.75:  # High overlap
                    result['match_score'] = max(result['match_score'], 70)  # Boost to at least 70
                elif overlap_ratio == 0:  # No overlap
                    result['match_score'] = 0  # Set to 0
                elif overlap_ratio < 0.1:  # Less than 10% overlap
                    result['match_score'] = min(result['match_score'], 5)  # Cap at 5
                elif overlap_ratio < 0.5:  # Less than 50% overlap
                    result['match_score'] = int(result['match_score'] * 0.5)  # Reduce by half
                print(f"Adjusted score: {result['match_score']}")
                # Update selection status based on adjusted score
                result['selection_status'] = "Selected" if result['match_score'] >= 50 else "Not Selected"

                results.append(result)

        # Save to database
        conn = sqlite3.connect('results.db')
        c = conn.cursor()
        for result in results:
            c.execute('''INSERT INTO results (resume_id, name, skills, experience, education, match_score, selection_status, justification, job_description, resume_content)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (result['resume_id'], result['name'], json.dumps(result['skills']), result['experience'], result['education'], result['match_score'], result['selection_status'], result.get('justification', ''), job_description, resume_content))
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
            'justification': row[8],
            'job_description': row[9],
            'resume_content': row[10],
            'timestamp': row[11]
        })
    return render_template('results.html', results=results_list)

if __name__ == "__main__":
    app.run(debug=True)
