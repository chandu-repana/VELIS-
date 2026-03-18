import pytest
from app.services.question_generator import generate_questions_from_skills, QUESTION_TEMPLATES, GENERAL_QUESTIONS
from app.services.feedback import generate_overall_feedback


def test_generate_questions_with_skills():
    skills = ["python", "react", "postgresql"]
    questions = generate_questions_from_skills(skills, "Software Developer", 10)
    assert len(questions) == 10
    for q in questions:
        assert "text" in q
        assert "question_type" in q
        assert "difficulty" in q
        assert "order_index" in q


def test_generate_questions_no_skills():
    questions = generate_questions_from_skills([], "Developer", 5)
    assert len(questions) == 5
    for q in questions:
        assert q["question_type"] == "general"


def test_generate_questions_fewer_than_requested():
    skills = ["python"]
    questions = generate_questions_from_skills(skills, "Developer", 8)
    assert len(questions) == 8


def test_question_types_valid():
    valid_types = {"technical", "behavioral", "situational", "general"}
    skills = ["python", "java", "react", "docker"]
    questions = generate_questions_from_skills(skills, "Developer", 10)
    for q in questions:
        assert q["question_type"] in valid_types


def test_question_difficulties_valid():
    valid_difficulties = {"easy", "medium", "hard"}
    skills = ["python", "react"]
    questions = generate_questions_from_skills(skills, "Developer", 5)
    for q in questions:
        assert q["difficulty"] in valid_difficulties


def test_order_index_sequential():
    skills = ["python", "react"]
    questions = generate_questions_from_skills(skills, "Developer", 5)
    indices = [q["order_index"] for q in questions]
    assert sorted(indices) == list(range(len(questions)))


def test_generate_overall_feedback_excellent():
    feedback = generate_overall_feedback([9.0, 8.5, 9.5], ["technical", "behavioral", "general"], "Developer")
    assert feedback["grade"] == "A"
    assert feedback["overall_score"] >= 8.5


def test_generate_overall_feedback_poor():
    feedback = generate_overall_feedback([2.0, 3.0, 1.5], ["technical", "behavioral", "general"], "Developer")
    assert feedback["grade"] in ["D", "F"]
    assert feedback["overall_score"] < 5.0


def test_generate_overall_feedback_empty():
    feedback = generate_overall_feedback([], [], "Developer")
    assert feedback["overall_score"] == 0.0
    assert feedback["grade"] == "N/A"


def test_question_templates_exist():
    assert "technical" in QUESTION_TEMPLATES
    assert "behavioral" in QUESTION_TEMPLATES
    assert "situational" in QUESTION_TEMPLATES
    assert "general" in QUESTION_TEMPLATES


def test_general_questions_not_empty():
    assert len(GENERAL_QUESTIONS) > 0
