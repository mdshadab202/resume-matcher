
import os
import shutil
import fitz  # PyMuPDF
import pandas as pd
import re
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from backend.keyword_extractor import extract_skills, extract_education, extract_experience
from fastapi import Request
from fastapi.templating import Jinja2Templates

# === SETUP ===

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULT_PATH = os.path.join(BASE_DIR, "matching_results.xlsx")
LOG_FILE = os.path.join(BASE_DIR, "app.log")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# === LOGGING ===
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# === FASTAPI SETUP ===

app = FastAPI()
templates = Jinja2Templates(directory="frontend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/matching_results", StaticFiles(directory=BASE_DIR), name="matching_results")

# === UTILITIES ===

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def extract_contact_info(text):
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-()]{7,}\d", text)
    return (email.group(0) if email else None), (phone.group(0) if phone else None)

# === ROUTES ===

@app.post("/match/")
async def match_resumes(jd_text: str = Form(...), resumes: List[UploadFile] = File(...)):
    try:
        if os.path.exists(UPLOAD_DIR):
            shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save job description
        with open(os.path.join(BASE_DIR, "temp_jd.txt"), "w", encoding="utf-8") as f:
            f.write(jd_text)

        # Extract JD features
        jd_skills = extract_skills(jd_text)
        jd_edu = extract_education(jd_text)
        jd_exp = extract_experience(jd_text)
        jd_features = {"skills": jd_skills, "education": jd_edu, "experience": jd_exp}

        all_results = []

        for resume_file in resumes:
            file_path = os.path.join(UPLOAD_DIR, resume_file.filename)
            with open(file_path, "wb") as f:
                f.write(await resume_file.read())

            resume_text = extract_text_from_pdf(file_path)
            resume_skills = extract_skills(resume_text)
            resume_edu = extract_education(resume_text)
            resume_exp = extract_experience(resume_text)
            email, phone = extract_contact_info(resume_text)

            def match_score(jd_list, resume_list):
                if not jd_list:
                    return 0
                matched = [s for s in jd_list if s in resume_list]
                return int(len(matched) / len(jd_list) * 100)

            skill_score = match_score(jd_skills, resume_skills)
            edu_score = match_score(jd_edu, resume_edu)
            exp_score = match_score(jd_exp, resume_exp)

            scores = {
                "Skills Score": skill_score,
                "Education Score": edu_score,
                "Experience Score": exp_score,
            }

            present_keys = [k for k, v in jd_features.items() if v]
           
            if len(present_keys) == 1:
                final_score = scores[f"{present_keys[0].capitalize()} Score"]
            elif len(present_keys) == 2:
                final_score = int(sum([scores[f"{k.capitalize()} Score"] for k in present_keys]) / len(present_keys))
            else:
                final_score = int((skill_score * 0.7 + edu_score * 0.15 + exp_score * 0.15))
            if final_score >= 90:
                priority = "High"
            elif final_score >= 75:
                priority = "Medium"
            else:
                priority = "Low"

            # Determine which scores to include based on JD
            result = {
                "Resume": resume_file.filename,
                "Email": email,
                "Phone": phone,
            }

            if "skills" in present_keys:
                result["Skill Score"] = skill_score
                
            
            if "education" in present_keys:
                result["Education Score"] = edu_score
            if "experience" in present_keys:
                result["Experience Score"] = exp_score

            result["Final Score"] = final_score
            result["Priority"] = priority
            all_results.append(result)



        df = pd.DataFrame(all_results)
        df.to_excel(RESULT_PATH, index=False)

        logging.info("Matching completed successfully for %d resumes.", len(resumes))
        return JSONResponse(content={"message": "Matching done", "results": all_results})

    except Exception as e:
        logging.error("Error in matching: %s", str(e), exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Matching failed."})


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=open("frontend/index.html", encoding="utf-8").read())


@app.get("/match_results", response_class=HTMLResponse)
def show_results(request: Request):
    if not os.path.exists(RESULT_PATH):
        return HTMLResponse("<h3>No match results found. Did you run matching?</h3>")

    df = pd.read_excel(RESULT_PATH)

    # Add Priority column
    def get_priority(score):
        if score >= 90:
            return "High"
        elif score >= 75:
            return "Medium"
        else:
            return "Low"

    df["Priority"] = df["Final Score"].apply(get_priority)

    high = df[df["Priority"] == "High"]
    medium = df[df["Priority"] == "Medium"]
    low = df[df["Priority"] == "Low"]

    return templates.TemplateResponse("results.html", {
        "request": request,
        "high": high,
        "medium": medium,
        "low": low
    })

