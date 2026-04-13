import re
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from app.data.skills_dataset import COMPREHENSIVE_SKILLS, ROLE_SKILL_MAPPING, INTERVIEW_QA_PAIRS
    TECH_SKILLS = COMPREHENSIVE_SKILLS
    logger.info("Loaded comprehensive skills dataset")
except ImportError:
    logger.warning("Using fallback skills dataset")
    TECH_SKILLS = {
        "languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift", "php", "ruby"],
        "frontend": ["react", "angular", "vue", "nextjs", "html", "css", "tailwind", "bootstrap", "redux", "graphql"],
        "backend": ["nodejs", "express", "fastapi", "django", "flask", "spring", "rest api", "microservices"],
        "database": ["postgresql", "mysql", "mongodb", "redis", "sqlite", "elasticsearch", "dynamodb", "firebase"],
        "cloud_devops": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "linux", "ci/cd"],
        "ai_ml": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "nlp", "pandas", "numpy"],
        "mobile": ["android", "ios", "react native", "flutter"],
        "testing": ["jest", "pytest", "junit", "selenium", "cypress", "tdd", "bdd"],
        "tools": ["git", "github", "jira", "figma", "docker", "postman"],
        "soft_skills": ["leadership", "communication", "teamwork", "problem solving", "agile", "scrum"]
    }
    ROLE_SKILL_MAPPING = {
        "Frontend Developer": ["react", "javascript", "html", "css"],
        "Backend Developer": ["python", "nodejs", "postgresql"],
        "Full Stack Developer": ["react", "nodejs", "python"],
        "DevOps Engineer": ["docker", "kubernetes", "aws"],
        "Data Scientist": ["python", "machine learning", "pandas"],
        "Software Developer": ["python", "java", "javascript"]
    }


def extract_skills(text: str) -> List[str]:
    if not text:
        return []
    text_lower = text.lower()
    found_skills = set()

    for category, skills in TECH_SKILLS.items():
        for skill in skills:
            if len(skill) <= 2:
                pattern = r'\b' + re.escape(skill.upper()) + r'\b'
                if re.search(pattern, text):
                    found_skills.add(skill)
            else:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(skill)

    logger.info(f"Extracted {len(found_skills)} skills from resume")
    return sorted(list(found_skills))


def detect_job_role(skills: List[str], raw_text: str = "") -> str:
    if not skills:
        return "Software Developer"

    skills_lower = [s.lower() for s in skills]
    text_lower = raw_text.lower() if raw_text else ""
    role_scores = {}

    try:
        role_map = ROLE_SKILL_MAPPING
    except:
        role_map = {"Software Developer": ["python", "java", "javascript"]}

    for role, role_skills in role_map.items():
        score = 0
        matched = 0
        for keyword in role_skills:
            if keyword in skills_lower:
                score += 2
                matched += 1
            elif keyword in text_lower:
                score += 1
                matched += 1
        min_match = max(2, len(role_skills) // 3)
        if matched >= min_match:
            role_scores[role] = score

    if not role_scores:
        return "Software Developer"
    return max(role_scores, key=role_scores.get)


def extract_experience_years(text: str) -> int:
    if not text:
        return 0
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+(?:professional\s+)?experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience',
        r'worked\s+for\s+(\d+)\+?\s*years?',
    ]
    text_lower = text.lower()
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            years = int(match)
            if 0 < years < 50 and years > max_years:
                max_years = years

    if max_years == 0:
        year_pattern = r'\b(20\d{2})\b'
        years_found = re.findall(year_pattern, text)
        if len(years_found) >= 2:
            years_int = [int(y) for y in years_found]
            span = max(years_int) - min(years_int)
            if 0 < span < 40:
                max_years = span
    return max_years


def extract_education(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    degree_patterns = [
        r'(b\.?tech|bachelor of technology)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|university|college|$)',
        r'(b\.?e\.?|bachelor of engineering)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
        r'(b\.?sc\.?|bachelor of science)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
        r'(m\.?tech|master of technology)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
        r'(m\.?sc\.?|master of science)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
        r'(mba|master of business)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
        r'(ph\.?d|doctorate)\s*(?:in\s+)?([a-zA-Z\s]+?)(?:\n|,|from|at|$)',
    ]
    text_lower = text.lower()
    education = []
    seen = []
    for pattern in degree_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            key = match[0][:5]
            if key not in seen:
                seen.append(key)
                field = match[1].strip()[:50] if match[1].strip() else "Not specified"
                education.append({"degree": match[0].upper().strip(), "field": field.title()})
    return education[:3]


def extract_all(text: str) -> Dict[str, Any]:
    skills = extract_skills(text)
    experience_years = extract_experience_years(text)
    education = extract_education(text)
    suggested_role = detect_job_role(skills, text)
    return {
        "skills": skills,
        "experience_years": experience_years,
        "education": education,
        "suggested_role": suggested_role
    }
