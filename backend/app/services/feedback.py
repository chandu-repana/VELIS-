import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def generate_overall_feedback(
    scores: List[float],
    question_types: List[str],
    job_role: str = "Software Developer"
) -> Dict:
    if not scores:
        return {
            "overall_score": 0.0,
            "grade": "N/A",
            "summary": "No responses evaluated yet.",
            "top_strengths": [],
            "top_improvements": [],
            "recommendation": "Complete the interview to receive feedback."
        }

    overall_score = round(sum(scores) / len(scores), 1)

    if overall_score >= 8.5:
        grade = "A"
        recommendation = "Excellent performance. You are well prepared for this role."
    elif overall_score >= 7.0:
        grade = "B"
        recommendation = "Good performance. Minor improvements needed in specific areas."
    elif overall_score >= 5.5:
        grade = "C"
        recommendation = "Average performance. Focus on technical depth and structured answers."
    elif overall_score >= 4.0:
        grade = "D"
        recommendation = "Below average. Significant preparation needed before interviews."
    else:
        grade = "F"
        recommendation = "Needs substantial improvement. Consider mock interviews and targeted study."

    type_counts = {}
    for qt in question_types:
        type_counts[qt] = type_counts.get(qt, 0) + 1

    summary = (
        f"You completed {len(scores)} questions for the {job_role} role. "
        f"Overall score: {overall_score}/10 (Grade: {grade}). "
        f"{recommendation}"
    )

    top_strengths = []
    if overall_score >= 7.0:
        top_strengths.append("Strong communication and articulation skills")
    if "technical" in type_counts and overall_score >= 6.0:
        top_strengths.append("Solid technical knowledge demonstrated")
    if len(scores) == len(question_types):
        top_strengths.append("Completed all interview questions")

    top_improvements = []
    if overall_score < 7.0:
        top_improvements.append("Practice structured answers using STAR method")
    if overall_score < 6.0:
        top_improvements.append("Deepen technical knowledge in core skill areas")
    if overall_score < 5.0:
        top_improvements.append("Work on confidence and communication clarity")

    return {
        "overall_score": overall_score,
        "grade": grade,
        "summary": summary,
        "top_strengths": top_strengths,
        "top_improvements": top_improvements,
        "recommendation": recommendation
    }
