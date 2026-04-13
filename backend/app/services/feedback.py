import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def generate_overall_feedback(
    scores: List[float],
    question_types: List[str],
    job_role: str = "Software Developer",
    individual_results: List[Dict] = None
) -> Dict:
    if not scores:
        return {
            "overall_score": 0.0,
            "grade": "N/A",
            "summary": "No responses evaluated yet.",
            "top_strengths": [],
            "top_improvements": [],
            "recommendation": "Complete the interview to receive feedback.",
            "category_scores": {}
        }

    overall_score = round(sum(scores) / len(scores), 1)

    if overall_score >= 8.5:
        grade = "A+"
        recommendation = "Exceptional performance. You are very well prepared for this role."
    elif overall_score >= 8.0:
        grade = "A"
        recommendation = "Excellent performance. Strong candidate for this position."
    elif overall_score >= 7.0:
        grade = "B"
        recommendation = "Good performance. Minor improvements in depth and examples needed."
    elif overall_score >= 6.0:
        grade = "C+"
        recommendation = "Above average. Work on structuring answers with the STAR method."
    elif overall_score >= 5.0:
        grade = "C"
        recommendation = "Average performance. Significant preparation needed in key areas."
    elif overall_score >= 4.0:
        grade = "D"
        recommendation = "Below average. Deep study and mock interview practice required."
    else:
        grade = "F"
        recommendation = "Needs substantial improvement. Focus on fundamentals and real examples."

    category_scores = {}
    if question_types:
        for qt in set(question_types):
            qt_scores = [scores[i] for i, t in enumerate(question_types) if t == qt]
            if qt_scores:
                category_scores[qt] = round(sum(qt_scores) / len(qt_scores), 1)

    weakest_category = min(category_scores, key=category_scores.get) if category_scores else None
    strongest_category = max(category_scores, key=category_scores.get) if category_scores else None

    top_strengths = []
    if overall_score >= 7.0:
        top_strengths.append("Strong overall communication and articulation")
    if strongest_category and category_scores.get(strongest_category, 0) >= 7.0:
        top_strengths.append(f"Best performance in {strongest_category} questions (avg {category_scores[strongest_category]}/10)")
    if len([s for s in scores if s >= 7.0]) >= len(scores) * 0.5:
        top_strengths.append("Consistently strong answers across multiple questions")
    if individual_results:
        high_scores = [r for r in individual_results if r.get("score", 0) >= 8.0]
        if high_scores:
            top_strengths.append(f"Excellent answers on {len(high_scores)} question(s)")

    top_improvements = []
    if weakest_category and category_scores.get(weakest_category, 10) < 6.0:
        top_improvements.append(f"Focus on improving {weakest_category} answers (avg {category_scores[weakest_category]}/10)")
    low_scores = [s for s in scores if s < 5.0]
    if low_scores:
        top_improvements.append(f"{len(low_scores)} answer(s) scored below 5 — review those topics")
    if overall_score < 7.0:
        top_improvements.append("Practice STAR method for behavioral and situational questions")
    if overall_score < 6.0:
        top_improvements.append("Prepare 2-3 real project examples for each skill on your resume")
    if overall_score < 5.0:
        top_improvements.append("Schedule daily mock interviews to build confidence and fluency")

    answered = len(scores)
    summary = (
        f"You answered {answered} questions for the {job_role} role. "
        f"Overall score: {overall_score}/10 (Grade: {grade}). "
    )
    if strongest_category and weakest_category and strongest_category != weakest_category:
        summary += f"Strongest in {strongest_category} questions, weakest in {weakest_category} questions. "
    summary += recommendation

    return {
        "overall_score": overall_score,
        "grade": grade,
        "summary": summary,
        "top_strengths": top_strengths[:3],
        "top_improvements": top_improvements[:4],
        "recommendation": recommendation,
        "category_scores": category_scores
    }
