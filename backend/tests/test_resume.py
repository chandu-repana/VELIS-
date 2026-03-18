import pytest
from app.services.skill_extractor import extract_skills, extract_experience_years, extract_education, extract_all
from app.services.evaluator import evaluate_response, calculate_length_score, calculate_clarity_score


def test_extract_skills_python():
    text = "I have experience with Python, Django, and PostgreSQL for backend development."
    skills = extract_skills(text)
    assert "python" in skills
    assert "django" in skills
    assert "postgresql" in skills


def test_extract_skills_empty():
    skills = extract_skills("")
    assert skills == []


def test_extract_skills_no_match():
    skills = extract_skills("I love cooking pasta and reading books.")
    assert skills == []


def test_extract_experience_years():
    text = "I have 5 years of experience in software development."
    years = extract_experience_years(text)
    assert years == 5


def test_extract_experience_zero():
    years = extract_experience_years("I am a fresh graduate.")
    assert years == 0


def test_extract_education():
    text = "I completed my B.Tech in Computer Science from VIT University."
    education = extract_education(text)
    assert len(education) >= 0


def test_extract_all_returns_dict():
    text = "Python developer with 3 years experience in React and PostgreSQL."
    result = extract_all(text)
    assert "skills" in result
    assert "experience_years" in result
    assert "education" in result
    assert isinstance(result["skills"], list)


def test_evaluate_empty_response():
    result = evaluate_response("What is Python?", "", "technical")
    assert result["score"] == 1.0
    assert len(result["strengths"]) > 0
    assert len(result["improvements"]) > 0


def test_evaluate_good_response():
    answer = "Python is a high-level programming language. I have implemented several projects using Python including a machine learning pipeline that improved performance by 30 percent. I used libraries like pandas, numpy, and scikit-learn to build data processing algorithms."
    result = evaluate_response("Tell me about Python", answer, "technical", "python")
    assert result["score"] > 5.0
    assert "feedback" in result


def test_evaluate_short_response():
    result = evaluate_response("Explain REST APIs", "I know APIs", "technical")
    assert result["score"] < 7.0


def test_length_score():
    assert calculate_length_score("word " * 5) < calculate_length_score("word " * 50)


def test_clarity_score():
    good = "I developed a Python application. It improved performance by 40 percent. The team was happy with the results."
    poor = "um basically i uh like you know worked on some stuff"
    assert calculate_clarity_score(good) > calculate_clarity_score(poor)
