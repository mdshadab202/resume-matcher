# import os
# import re
# import spacy
# from rapidfuzz import process

# # Load SpaCy model
# nlp = spacy.load("en_core_web_sm")

# # Dynamically resolve the base directory (where this file is)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Load skills list
# def load_skills():
#     skill_file_path = os.path.join(BASE_DIR, "skill_master_list.txt")
#     with open(skill_file_path, "r", encoding="utf-8") as file:
#         return [line.strip().lower() for line in file.readlines()]

# # Global constants
# SKILL_LIST = load_skills()
# EDUCATION_KEYWORDS = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'bsc', 'msc']
# EXPERIENCE_KEYWORDS = ['experience', 'internship', 'years', 'year', 'worked', 'job', 'role']

# # Extract Skills
# def extract_skills(text, threshold=85):
#     text = text.lower()
#     doc = nlp(text)
#     possible_skills = set()
#     for chunk in doc.noun_chunks:
#         phrase = chunk.text.strip().lower()
#         match = process.extractOne(phrase, SKILL_LIST)
#         if match and match[1] >= threshold:
#             possible_skills.add(match[0])
#     return list(possible_skills)

# # Extract Education
# def extract_education(text):
#     text = text.lower()
#     return list(set([edu for edu in EDUCATION_KEYWORDS if edu in text]))

# # Extract Experience
# def extract_experience(text):
#     text = text.lower()
#     return list(set([exp for exp in EXPERIENCE_KEYWORDS if exp in text]))

import re

def extract_skills(text):
    skills_list = [
        "python", "java", "c++", "sql", "excel", "machine learning", "deep learning",
        "data analysis", "nlp", "tensorflow", "keras", "pytorch", "react", "django",
        "flask", "fastapi", "aws", "azure", "git", "docker"
    ]
    text_lower = text.lower()
    found = [skill for skill in skills_list if skill in text_lower]
    return found

def extract_education(text):
    edu_keywords = [
        "bsc", "msc", "b.tech", "m.tech", "b.e", "m.e", "mba", "bba",
        "phd", "high school", "intermediate", "diploma", "bachelor", "master", "doctorate"
    ]
    text_lower = text.lower()
    found = [edu for edu in edu_keywords if edu in text_lower]
    return found

def extract_experience(text):
    """
    Extract years/months of experience → return total months of experience.
    E.g.:
    "5 years", "2.5 years", "6 months" → converts to months (int)
    """
    text_lower = text.lower()
    total_months = 0

    year_matches = re.findall(r'(\d+(\.\d+)?)\s*(year|years|yr|yrs)', text_lower)
    month_matches = re.findall(r'(\d+(\.\d+)?)\s*(month|months|mo)', text_lower)

    for match in year_matches:
        years = float(match[0])
        total_months += int(years * 12)

    for match in month_matches:
        months = float(match[0])
        total_months += int(months)

    return total_months
