import google.generativeai as genai 
from dotenv import load_dotenv
import os 

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

configuration = {
    "temperature":1,
    "top_p":0.95,
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
    - Give a match score out of 100.
    - Determine selection status: If match score is 70 or above, Selected; otherwise, Not Selected.

    Return only a JSON object with the following keys:
    - name: string
    - skills: array of strings
    - experience: string
    - education: string
    - match_score: number
    - selection_status: string ("Selected" or "Not Selected")
    """

    response = model.generate_content(prompt)

    return response.text
