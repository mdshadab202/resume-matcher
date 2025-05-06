import re
import spacy
from rapidfuzz import process

nlp = spacy.load("en_core_web_sm")

def load_skills():
    with open("backend/skill_master_list.txt", "r", encoding="utf-8") as file:
        return [line.strip().lower() for line in file.readlines()]

SKILL_LIST = load_skills()
EDUCATION_KEYWORDS = ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'mba', 'bsc', 'msc']
EXPERIENCE_KEYWORDS = ['experience', 'internship', 'years', 'year', 'worked', 'job', 'role']

def extract_skills(text, threshold=85):
    text = text.lower()
    doc = nlp(text)
    possible_skills = set()
    for chunk in doc.noun_chunks:
        phrase = chunk.text.strip().lower()
        match = process.extractOne(phrase, SKILL_LIST)
        if match and match[1] >= threshold:
            possible_skills.add(match[0])
    return list(possible_skills)

def extract_education(text):
    text = text.lower()
    return list(set([edu for edu in EDUCATION_KEYWORDS if edu in text]))

def extract_experience(text):
    text = text.lower()
    return list(set([exp for exp in EXPERIENCE_KEYWORDS if exp in text]))
