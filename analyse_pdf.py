import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv # type: ignore
import os 

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

configuration = {
    "temperature":0.3,
    "top_p":0.8,
    "top_k":40,
    "max_output_tokens":8192,
    "response_mime_type":"application/json"
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=configuration
)

def analyse_resume_gemini(resume_content,job_description):
    prompt = f"""
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
    """

    response = model.generate_content(prompt)

    # Check if response is blocked or invalid
    if response.candidates and response.candidates[0].finish_reason == 2:  # SAFETY
        # Return a default JSON string for blocked responses
        return '{"name": "Blocked by AI Safety", "skills": [], "experience": "Blocked", "education": "Blocked", "match_score": 0, "selection_status": "Not Selected"}'
    
    if response.parts:
        return response.text
    else:
        # Fallback if no parts
        return '{"name": "Error", "skills": [], "experience": "Error", "education": "Error", "match_score": 0, "selection_status": "Not Selected"}'
