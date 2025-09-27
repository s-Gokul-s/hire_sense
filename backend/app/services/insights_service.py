# app/services/insights_service_spacy.py
import os
import re
from huggingface_hub import snapshot_download
import spacy

# ----------------- Env Fix for Windows -----------------
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

# ----------------- Load Model -----------------
# Download and load the spaCy NER model
model_path = snapshot_download("amjad-awad/skill-extractor", repo_type="model")
nlp = spacy.load(model_path)

# ----------------- Generic → Specific Skill Mapping -----------------
GENERIC_SKILL_MAP = {
    "databases": ["mysql", "postgresql", "mongodb", "sqlite", "oracle"],
    "sql": ["mysql", "postgresql", "sqlite", "oracle"],
    "version control": ["git", "github", "gitlab", "bitbucket"],
    "machine learning": ["scikit-learn", "tensorflow", "pytorch", "keras"],
    "nlp": ["spacy", "nltk", "bert", "transformers"],
}

# ----------------- Noise Terms (skip these if extracted) -----------------
NOISE_TERMS = {"code", "management", "computer skills", "software development"}

# ----------------- Text Cleaning -----------------
def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ----------------- Extract Skills -----------------
def extract_skills(text: str) -> list:
    """
    Extract skills from text using spaCy NER model.
    """
    text = clean_text(text)
    doc = nlp(text)
    skills = [
        ent.text.strip().lower()
        for ent in doc.ents
        if "SKILLS" in ent.label_
    ]
    # Deduplicate + remove noise
    return list(set(skill for skill in skills if skill not in NOISE_TERMS))

# ----------------- Expand Generic Skills -----------------
def expand_with_generic_matches(jd_skills, resume_skills):
    """
    Consider a generic skill matched if any mapped specific skill 
    is found in the resume skills.
    """
    matched = set(jd_skills).intersection(resume_skills)
    missing = set(jd_skills)

    for generic, specifics in GENERIC_SKILL_MAP.items():
        if generic in jd_skills:
            if any(specific in resume_skills for specific in specifics):
                matched.add(generic)

    # Remove matched ones from missing
    missing = missing - matched
    return matched, missing

# ----------------- Match Skills -----------------
def get_skill_matches(jd_text: str, resume_text: str):
    """
    Compare skills between JD and Resume.
    Returns matched and missing skills.
    """
    jd_skills = set(extract_skills(jd_text))
    resume_skills = set(extract_skills(resume_text))

    matched_skills, missing_skills = expand_with_generic_matches(jd_skills, resume_skills)

    return {
        "jd_skills": sorted(jd_skills),
        "resume_skills": sorted(resume_skills),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
    }
