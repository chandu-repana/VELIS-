import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

TECH_SKILLS = {
    "programming": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "kotlin", "swift", "php", "ruby", "scala", "r", "matlab", "bash", "shell"
    ],
    "web": [
        "react", "angular", "vue", "nextjs", "nodejs", "express", "django",
        "fastapi", "flask", "spring", "html", "css", "tailwind", "bootstrap"
    ],
    "database": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
        "cassandra", "elasticsearch", "dynamodb", "firebase"
    ],
    "cloud": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "jenkins", "github actions", "ci/cd", "linux"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "nlp", "computer vision", "pandas", "numpy",
        "huggingface", "openai", "langchain"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "agile", "scrum", "time management"
    ]
}


def extract_skills(text: str) -> List[str]:
    """
    Extract skills from resume text by matching against known skill keywords.
    Returns a deduplicated list of found skills.
    """
    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    for category, skills in TECH_SKILLS.items():
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)

    logger.info(f"Extracted {len(found_skills)} skills from resume")
    return sorted(list(found_skills))


def extract_experience_years(text: str) -> int:
    """
    Estimate years of experience from resume text.
    Looks for patterns like '5 years', '3+ years experience'.
    """
    if not text:
        return 0

    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+experience',
    ]

    text_lower = text.lower()
    max_years = 0

    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            years = int(match)
            if years > max_years and years < 50:
                max_years = years

    return max_years


def extract_education(text: str) -> List[Dict[str, str]]:
    """
    Extract education information from resume text.
    Looks for degree keywords and university mentions.
    """
    if not text:
        return []

    education = []
    degree_patterns = [
        r'(b\.?tech|bachelor|b\.?e\.?|b\.?sc|b\.?s\.?)\s+in\s+([a-zA-Z\s]+)',
        r'(m\.?tech|master|m\.?e\.?|m\.?sc|m\.?s\.?)\s+in\s+([a-zA-Z\s]+)',
        r'(ph\.?d|doctorate)\s+in\s+([a-zA-Z\s]+)',
        r'(mba|pgdm)\s+in\s+([a-zA-Z\s]+)',
    ]

    text_lower = text.lower()

    for pattern in degree_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            education.append({
                "degree": match[0].upper(),
                "field": match[1].strip().title()
            })

    return education[:5]


def extract_all(text: str) -> Dict[str, Any]:
    """
    Run the full extraction pipeline on resume text.
    Returns skills, experience years, and education.
    """
    return {
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": extract_education(text)
    }
