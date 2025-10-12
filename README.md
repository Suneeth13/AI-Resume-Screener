# AI Resume Analyzer

A Flask-based web application that intelligently parses resumes, extracts key information, and matches them against job descriptions using Google's Gemini AI.

## Features

- Upload multiple PDF resumes
- Extract structured data: name, skills, experience, education
- Compute match score against job description
- Display results with selection status

## Architecture

### Backend
- **Framework**: Flask (Python)
- **AI Integration**: Google Generative AI (Gemini 2.5-flash)
- **PDF Processing**: PyMuPDF (fitz)
- **Database**: SQLite (for storing analysis results)

### Frontend
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Marked.js for Markdown rendering

### File Structure
```
.
├── main.py                 # Main Flask application
├── analyse_pdf.py          # AI analysis logic
├── list_models.py          # Gemini models lister
├── templates/
│   └── index.html          # Web UI
├── uploads/                # Uploaded PDF files
├── results.db              # SQLite database (created on first run)
├── .env                    # Environment variables (GEMINI_API_KEY)
└── requirements.txt        # Python dependencies
```

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variable: Create `.env` file with `GEMINI_API_KEY=your_api_key`
4. Run the app: `python main.py`
5. Open http://localhost:5000

## LLM Prompts

### Resume Analysis Prompt
```
You are a professional resume analyzer.

Resume:
{resume_content}

Job Description:
{job_description}

Task:
- Extract from the resume: Name of Person, Skills (as a list), Experience (summary), Education (summary).
- Analyze the resume against the job description.
- Give a match score out of 100.
- Determine selection status: If match score is 70 or above, Selected; otherwise, Not Selected.

Return only a JSON object with the following keys:
- name: string
- skills: array of strings
- experience: string
- education: string
- match_score: number
- selection_status: string ("Selected" or "Not Selected")
```

## API Endpoints

- `GET /`: Main page with upload form
- `POST /`: Process uploaded resumes and job description, store results in database
- `GET /results`: View all stored analysis results

## Dependencies

- flask
- PyMuPDF
- google-generativeai
- python-dotenv

## Evaluation

- Code Quality: Modular structure with separation of concerns
- Data Extraction: Accurate PDF text extraction and AI parsing
- LLM Prompt Quality: Structured prompt yielding consistent JSON output
- Output Clarity: Clean tabular display of analysis results
