import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

EVALUATION_CRITERIA = {
    "technical": {
        "keywords_weight": 0.4,
        "length_weight": 0.2,
        "clarity_weight": 0.4
    },
    "behavioral": {
        "keywords_weight": 0.3,
        "length_weight": 0.3,
        "clarity_weight": 0.4
    },
    "situational": {
        "keywords_weight": 0.3,
        "length_weight": 0.3,
        "clarity_weight": 0.4
    },
    "general": {
        "keywords_weight": 0.2,
        "length_weight": 0.3,
        "clarity_weight": 0.5
    }
}

POSITIVE_INDICATORS = [
    "implemented", "developed", "built", "created", "designed",
    "optimized", "improved", "solved", "managed", "led",
    "collaborated", "delivered", "achieved", "increased", "reduced",
    "experience", "successfully", "team", "project", "result"
]

NEGATIVE_INDICATORS = [
    "i dont know", "i do not know", "not sure", "no idea",
    "never used", "not familiar", "i cant", "i cannot"
]

TECHNICAL_KEYWORDS = [
    "algorithm", "database", "api", "framework", "architecture",
    "performance", "scalability", "testing", "deployment", "security",
    "cache", "async", "concurrent", "microservice", "container",
    "pipeline", "integration", "optimization", "debug", "refactor"
]


def calculate_length_score(text: str) -> float:
    words = len(text.split())
    if words < 10:
        return 2.0
    elif words < 30:
        return 5.0
    elif words < 80:
        return 7.0
    elif words < 200:
        return 9.0
    else:
        return 8.0


def calculate_keyword_score(text: str, question_type: str, skill_tag: str = None) -> float:
    text_lower = text.lower()
    score = 5.0

    positive_count = sum(1 for word in POSITIVE_INDICATORS if word in text_lower)
    score += min(positive_count * 0.5, 2.5)

    negative_count = sum(1 for phrase in NEGATIVE_INDICATORS if phrase in text_lower)
    score -= min(negative_count * 2.0, 4.0)

    if question_type == "technical":
        tech_count = sum(1 for word in TECHNICAL_KEYWORDS if word in text_lower)
        score += min(tech_count * 0.3, 1.5)

    if skill_tag and skill_tag.lower() in text_lower:
        score += 1.0

    return max(0.0, min(10.0, score))


def calculate_clarity_score(text: str) -> float:
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) == 0:
        return 2.0

    score = 5.0

    if len(sentences) >= 2:
        score += 1.5

    words = text.split()
    if len(words) > 0:
        avg_sentence_length = len(words) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 25:
            score += 1.5
        elif avg_sentence_length > 40:
            score -= 1.0

    filler_words = ["um", "uh", "like", "basically", "literally", "you know"]
    filler_count = sum(text.lower().count(word) for word in filler_words)
    score -= min(filler_count * 0.3, 1.5)

    return max(0.0, min(10.0, score))


def extract_strengths(text: str, question_type: str) -> List[str]:
    strengths = []
    text_lower = text.lower()
    words = text.split()

    if len(words) >= 50:
        strengths.append("Provided a detailed and comprehensive answer")

    positive_found = [w for w in POSITIVE_INDICATORS if w in text_lower]
    if len(positive_found) >= 2:
        strengths.append("Used strong action words demonstrating experience")

    if question_type == "technical":
        tech_found = [w for w in TECHNICAL_KEYWORDS if w in text_lower]
        if tech_found:
            strengths.append(f"Demonstrated technical knowledge with relevant terminology")

    if any(word in text_lower for word in ["example", "instance", "project", "situation", "when i"]):
        strengths.append("Supported answer with concrete examples")

    if any(word in text_lower for word in ["result", "outcome", "achieved", "improved", "increased", "reduced"]):
        strengths.append("Highlighted measurable outcomes and results")

    if not strengths:
        strengths.append("Attempted to address the question")

    return strengths[:3]


def extract_improvements(text: str, question_type: str, score: float) -> List[str]:
    improvements = []
    text_lower = text.lower()
    words = text.split()

    if len(words) < 30:
        improvements.append("Provide more detailed explanation with examples")

    negative_found = [p for p in NEGATIVE_INDICATORS if p in text_lower]
    if negative_found:
        improvements.append("Avoid phrases indicating uncertainty — research gaps before the interview")

    if question_type == "technical":
        tech_found = [w for w in TECHNICAL_KEYWORDS if w in text_lower]
        if len(tech_found) < 2:
            improvements.append("Include more technical terminology and specific concepts")

    if not any(word in text_lower for word in ["example", "instance", "project", "when i", "once"]):
        improvements.append("Add specific examples from past experience to strengthen your answer")

    if score < 6.0:
        improvements.append("Structure your answer using the STAR method: Situation, Task, Action, Result")

    return improvements[:3]


def evaluate_response(
    question_text: str,
    answer_text: str,
    question_type: str = "general",
    skill_tag: str = None
) -> Dict:
    if not answer_text or len(answer_text.strip()) < 5:
        return {
            "score": 1.0,
            "strengths": ["Attempted to answer the question"],
            "improvements": [
                "Provide a substantive answer",
                "Speak clearly and at length about your experience",
                "Use the STAR method to structure behavioral answers"
            ],
            "feedback": "Answer was too short or empty. Please provide a detailed response."
        }

    criteria = EVALUATION_CRITERIA.get(question_type, EVALUATION_CRITERIA["general"])

    length_score = calculate_length_score(answer_text)
    keyword_score = calculate_keyword_score(answer_text, question_type, skill_tag)
    clarity_score = calculate_clarity_score(answer_text)

    final_score = (
        keyword_score * criteria["keywords_weight"] +
        length_score * criteria["length_weight"] +
        clarity_score * criteria["clarity_weight"]
    )
    final_score = round(max(1.0, min(10.0, final_score)), 1)

    strengths = extract_strengths(answer_text, question_type)
    improvements = extract_improvements(answer_text, question_type, final_score)

    if final_score >= 8.0:
        feedback = f"Excellent answer. Score: {final_score}/10. You demonstrated strong knowledge and communication skills."
    elif final_score >= 6.0:
        feedback = f"Good answer. Score: {final_score}/10. With a few improvements this could be an outstanding response."
    elif final_score >= 4.0:
        feedback = f"Average answer. Score: {final_score}/10. Focus on adding more detail and specific examples."
    else:
        feedback = f"Needs improvement. Score: {final_score}/10. Review the question and practice a more structured response."

    logger.info(f"Evaluation complete: score={final_score} type={question_type}")

    return {
        "score": final_score,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback
    }
