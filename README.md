# AI Resume Analyzer


A powerful Flask-based web application that leverages Google's Gemini AI to intelligently parse PDF resumes, extract key information, and match them against job descriptions. Designed for recruiters and HR professionals to streamline resume screening.

## Features

- **Batch Upload**: Upload multiple PDF resumes simultaneously for efficient analysis.
- **AI-Powered Extraction**: Automatically extract structured data including name, skills, experience, and education using advanced AI.
- **Intelligent Matching**: Compute a match score out of 100 based on job description alignment, with keyword overlap adjustments for accuracy.
- **Selection Status**: Determine candidate selection based on score thresholds (Selected if ≥50).
- **Results Storage**: Store analysis results in a local SQLite database for future reference.
- **Responsive UI**: Clean, Bootstrap-styled interface with real-time processing feedback.
- **Error Handling**: Robust handling for invalid files, API errors, and JSON parsing issues.

## How It Works

1. **Upload Resumes**: Users upload one or more PDF resumes and paste a job description.
2. **Text Extraction**: PyMuPDF extracts raw text from PDFs.
3. **AI Analysis**: Gemini AI processes the resume text against the job description using a structured prompt to extract data and compute scores.
4. **Scoring Adjustment**: The app applies keyword overlap logic to refine AI scores (e.g., boost for high overlap, penalize for low).
5. **Results Display**: Results are shown in a table and stored in the database for viewing later.

## Architecture

### Backend
- **Framework**: Flask (Python web framework for routing and request handling).
- **AI Integration**: Google Generative AI (Gemini 2.5-flash model) for natural language processing and analysis.
- **PDF Processing**: PyMuPDF (fitz) for reliable text extraction from PDFs.
- **Database**: SQLite for lightweight, file-based storage of analysis results.
- **Configuration**: Environment variables managed via python-dotenv.

### Frontend
- **Template Engine**: Jinja2 for dynamic HTML rendering.
- **CSS Framework**: Bootstrap 5 for responsive, modern styling.
- **JavaScript**: Marked.js for potential Markdown rendering (though not heavily used in current templates).

### File Structure
```
.
├── main.py                 # Main Flask application with routes, logic, and database setup
├── analyse_pdf.py          # AI analysis logic using Gemini API
├── list_models.py          # Utility script to list available Gemini models
├── templates/
│   ├── index.html          # Main upload and results page
│   └── results.html        # Page to view stored analysis results
├── uploads/                # Directory for temporarily storing uploaded PDFs
├── results.db              # SQLite database (auto-created on first run)
├── .env                    # Environment file for API keys (not in repo)
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules for sensitive/cache files
└── README.md               # This file
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- A Google Gemini API key (obtain from [Google AI Studio](https://aistudio.google.com/))

### Installation Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd Resume-Analyzer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

5. **Access the App**:
   - Open your browser and navigate to `http://localhost:5000`.
   - Upload PDFs, enter a job description, and analyze!

### Optional: List Available Models
Run `python list_models.py` to see available Gemini models.

## Usage Guide

1. **Upload Resumes**: On the main page, select multiple PDF files and paste the job description.
2. **Analyze**: Click "Analyze Resumes" to process. A spinner indicates progress.
3. **View Results**: Results appear in a table showing extracted data, match scores, and selection status.
4. **Stored Results**: Visit `/results` to view all past analyses from the database.

### Example Job Description
```
We are seeking a Python Developer with experience in Flask, AI/ML, and database management. Skills: Python, SQL, TensorFlow. Experience: 3+ years in web development.
```

## API Endpoints

- `GET /`: Renders the main upload form.
- `POST /`: Accepts form data (resumes and job description), processes uploads, performs analysis, and displays results.
- `GET /results`: Retrieves and displays all stored results from the database.

## LLM Prompts

The application uses a detailed prompt to guide Gemini AI for consistent, structured output.

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
- Keyword Overlap (0-40 points): Check for exact or closely related terms from the job description in the resume. Penalize heavily for missing key terms (e.g., if no overlap, score 0-5 in this category).
- Skills Alignment (0-30 points): Evaluate how well the resume's skills match the job's requirements.
- Experience and Education Fit (0-30 points): Assess relevance of experience and education to the job.
- Total match_score: Sum of the above, out of 100. Be strict: If key job description terms are absent, keep score low (e.g., <10 for no overlap).
- Example: For a job requiring "React.js Next.js" with no mention in resume, score should be 0-10.
- Determine selection status: If match score is 50 or above, Selected; otherwise, Not Selected.

Return only a JSON object with the following keys:
- name: string
- skills: array of strings
- experience: string
- education: string
- match_score: number
- selection_status: string ("Selected" or "Not Selected")
```

Note: The app further adjusts scores based on keyword overlap ratios for stricter evaluation.

## Dependencies

- `flask`: Web framework.
- `PyMuPDF`: PDF text extraction.
- `google-generativeai`: Gemini AI integration.
- `python-dotenv`: Environment variable management.

## Evaluation

- **Code Quality**: Modular design with clear separation of concerns (e.g., AI logic in separate file).
- **Data Extraction**: Accurate PDF parsing and reliable AI-driven information extraction.
- **LLM Prompt Quality**: Structured prompts ensure consistent JSON responses and fair scoring.
- **Output Clarity**: User-friendly tables and storage for easy review.
- **Performance**: Handles multiple resumes efficiently; includes error handling for robustness.


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss.


## Support

If you encounter issues, check the console for errors or ensure your API key is valid. For questions, open an issue on GitHub.
