from flask import Flask, request, render_template
import fitz  # PyMuPDF
from analyse_pdf import analyse_resume_gemini
import os
import time
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


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

        return render_template("index.html", results=results)

    return render_template("index.html", results=None)


if __name__ == "__main__":
    app.run(debug=True)