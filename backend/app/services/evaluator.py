import logging
import re
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import concurrent.futures

logger = logging.getLogger(__name__)

_qa_pipeline = None
_executor = ThreadPoolExecutor(max_workers=1)


def get_qa_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        try:
            from transformers import pipeline
            logger.info("Loading AI evaluation model...")
            _qa_pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                device=-1,
                max_length=200
            )
            logger.info("AI evaluation model loaded")
        except Exception as e:
            logger.warning(f"Could not load AI model: {e}")
            _qa_pipeline = None
    return _qa_pipeline


TECHNICAL_KEYWORDS = [
    "algorithm", "database", "api", "framework", "architecture", "performance",
    "scalability", "testing", "deployment", "security", "cache", "async",
    "concurrent", "microservice", "container", "pipeline", "integration",
    "optimization", "debug", "refactor", "complexity", "latency", "throughput",
    "encryption", "authentication", "authorization", "rest", "queue",
    "design pattern", "load balancing", "fault tolerance", "version control",
    "ci/cd", "agile", "scrum", "unit test", "integration test", "mock",
    "dependency", "interface", "abstraction", "polymorphism", "inheritance"
]

POSITIVE_INDICATORS = [
    "implemented", "developed", "built", "created", "designed", "optimized",
    "improved", "solved", "managed", "led", "collaborated", "delivered",
    "achieved", "increased", "reduced", "automated", "migrated", "deployed",
    "architected", "refactored", "mentored", "launched", "shipped", "scaled",
    "fixed", "resolved", "analyzed", "debugged", "tested", "reviewed"
]

WEAK_INDICATORS = [
    "i think", "maybe", "i guess", "not sure", "i believe", "probably",
    "i dont know", "i do not know", "no idea", "never used", "not familiar",
    "i cant", "i cannot", "i havent", "i have not", "searching in google",
    "will search", "will google", "look it up", "find online", "i will google"
]

IRRELEVANT_PHRASES = [
    "i don't know what", "i have no idea", "i never heard",
    "unrelated", "off topic", "what does that mean",
    "can you repeat", "i didn't understand"
]

STAR_INDICATORS = {
    "situation": ["when", "at my previous", "in my last", "during", "while working", "in the project", "once"],
    "task": ["i had to", "my responsibility", "i was tasked", "i needed to", "my role was", "i was asked"],
    "action": ["i implemented", "i created", "i built", "i developed", "i used", "i applied", "i wrote", "i designed"],
    "result": ["result", "outcome", "achieved", "improved", "reduced", "increased", "saved", "percent", "%", "faster", "better"]
}


def has_star_structure(text: str) -> float:
    text_lower = text.lower()
    score = 0.0
    for component, keywords in STAR_INDICATORS.items():
        if any(kw in text_lower for kw in keywords):
            score += 0.25
    return score


def check_relevance_to_question(answer: str, question: str, skill_tag: str = None) -> float:
    answer_lower = answer.lower()
    question_lower = question.lower()

    for phrase in IRRELEVANT_PHRASES:
        if phrase in answer_lower:
            return 0.5

    question_words = set(re.findall(r'\b\w{4,}\b', question_lower))
    answer_words = set(re.findall(r'\b\w{4,}\b', answer_lower))

    stop_words = {"that", "this", "with", "from", "have", "will", "would", "could", "should", "about", "what", "when", "where", "which"}
    question_words -= stop_words
    answer_words -= stop_words

    if not question_words:
        return 5.0

    overlap = question_words & answer_words
    relevance_ratio = len(overlap) / len(question_words)

    if skill_tag and skill_tag.lower() in answer_lower:
        relevance_ratio += 0.3

    return min(10.0, relevance_ratio * 10.0)


def _run_ai_inference(prompt: str) -> str:
    pipe = get_qa_pipeline()
    if pipe is None:
        return ""
    result = pipe(prompt, max_length=200, num_return_sequences=1)
    return result[0]["generated_text"].strip()


def get_ai_feedback(question_text: str, answer_text: str, question_type: str) -> Dict:
    try:
        prompt = f"""You are an expert interview coach. Evaluate this candidate answer.

Question: {question_text[:200]}
Answer: {answer_text[:300]}
Type: {question_type}

Is the answer relevant to the question? Score it 1-10.
Give one specific strength and one specific improvement.

SCORE: [1-10]
RELEVANT: [yes/no]
STRENGTH: [specific strength from this answer]
IMPROVEMENT: [specific improvement for this answer]"""

        future = _executor.submit(_run_ai_inference, prompt)
        output = future.result(timeout=25)

        score = None
        relevant = True
        strength = None
        improvement = None

        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("SCORE:"):
                try:
                    num = re.search(r'[\d.]+', line.replace("SCORE:", ""))
                    if num:
                        score = float(num.group())
                        score = max(0.5, min(10.0, score))
                except:
                    pass
            elif line.startswith("RELEVANT:"):
                relevant = "no" not in line.lower()
            elif line.startswith("STRENGTH:"):
                strength = line.replace("STRENGTH:", "").strip()
            elif line.startswith("IMPROVEMENT:"):
                improvement = line.replace("IMPROVEMENT:", "").strip()

        if score is not None:
            if not relevant:
                score = min(score, 3.0)
            return {
                "ai_score": score,
                "ai_strength": strength,
                "ai_improvement": improvement,
                "is_relevant": relevant
            }

    except FutureTimeoutError:
        logger.warning("AI evaluation timed out — using rule-based scoring only")
    except Exception as e:
        logger.error(f"AI evaluation error: {e}")

    return None


def calculate_length_score(text: str) -> float:
    words = len(text.split())
    if words < 5:
        return 0.0
    elif words < 15:
        return 2.5
    elif words < 30:
        return 5.0
    elif words < 60:
        return 7.0
    elif words < 120:
        return 8.5
    elif words < 200:
        return 9.0
    elif words < 300:
        return 8.5
    else:
        return 7.5


def calculate_technical_score(answer: str, question_type: str) -> float:
    answer_lower = answer.lower()
    score = 5.0

    if question_type == "technical":
        tech_count = sum(1 for w in TECHNICAL_KEYWORDS if w in answer_lower)
        score += min(tech_count * 0.5, 3.0)

    star_bonus = has_star_structure(answer)
    score += star_bonus * 2.5

    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
    if len(sentences) >= 3:
        score += 1.5
    elif len(sentences) >= 2:
        score += 0.8

    filler_count = sum(answer.lower().count(w) for w in ["um", "uh", "you know", "kind of"])
    score -= min(filler_count * 0.4, 2.0)

    return max(0.0, min(10.0, score))


def generate_specific_strengths(answer: str, question: str, question_type: str, score: float, is_relevant: bool = True) -> List[str]:
    strengths = []
    answer_lower = answer.lower()
    words = answer.split()

    if not is_relevant:
        return ["Made an attempt to respond"]

    positive_found = [w for w in POSITIVE_INDICATORS if w in answer_lower]
    if len(positive_found) >= 2:
        strengths.append(f"Strong action verbs used: {', '.join(positive_found[:3])}")
    elif len(positive_found) == 1:
        strengths.append("Used action-oriented language showing ownership")

    if len(words) >= 80:
        strengths.append("Detailed and comprehensive response")
    elif len(words) >= 40:
        strengths.append("Complete answer that addresses the question")

    if question_type == "technical":
        tech_found = [w for w in TECHNICAL_KEYWORDS if w in answer_lower]
        if len(tech_found) >= 2:
            strengths.append(f"Technical depth shown: {', '.join(tech_found[:3])}")
        elif len(tech_found) == 1:
            strengths.append(f"Mentioned relevant technical concept: {tech_found[0]}")

    numbers = re.findall(r'\b\d+\s*(?:%|percent|x|times)\b', answer_lower)
    if numbers:
        strengths.append(f"Quantified impact with metrics ({numbers[0]})")

    star_score = has_star_structure(answer)
    if star_score >= 0.75:
        strengths.append("Excellent STAR structure: clear situation, action and result")
    elif star_score >= 0.5:
        strengths.append("Good narrative structure with clear context")

    if any(w in answer_lower for w in ["example", "instance", "specifically", "for instance", "such as"]):
        strengths.append("Supported answer with a concrete example")

    if not strengths:
        if len(words) >= 10:
            strengths.append("Addressed the question with relevant content")
        else:
            strengths.append("Attempted to respond to the question")

    return strengths[:3]


def generate_specific_improvements(answer: str, question: str, question_type: str, score: float, is_relevant: bool = True) -> List[str]:
    improvements = []
    answer_lower = answer.lower()
    words = answer.split()

    if not is_relevant:
        improvements.append(f"Your answer did not directly address the question — re-read it and focus on what is being asked")
        improvements.append("Identify the key topic of the question before answering")
        improvements.append("Even if unsure, explain your thought process related to the topic")
        return improvements

    if len(words) < 20:
        improvements.append(f"Too brief ({len(words)} words) — aim for at least 60-80 words with a structured explanation")
    elif len(words) < 40:
        improvements.append("Expand with more context, specific details, or a real example")

    weak_found = [p for p in WEAK_INDICATORS if p in answer_lower]
    if weak_found:
        improvements.append(f"Remove uncertainty phrases like '{weak_found[0]}' — speak from experience and knowledge")

    if question_type == "technical":
        tech_found = [w for w in TECHNICAL_KEYWORDS if w in answer_lower]
        if len(tech_found) == 0:
            improvements.append("Add specific technical terms and concepts — show depth of knowledge not just awareness")
        elif len(tech_found) == 1:
            improvements.append(f"Expand on {tech_found[0]} — explain how you used it, challenges faced, and outcomes")

    if not any(w in answer_lower for w in ["example", "instance", "project", "when i", "at my", "specifically", "once", "worked on"]):
        improvements.append("Add a real example: describe a specific project or situation where you applied this")

    numbers = re.findall(r'\b\d+\s*(?:%|percent|x|times)\b', answer_lower)
    if not numbers and score < 7.0:
        improvements.append("Quantify your results — 'reduced load time by 40%' is far more impactful than 'made it faster'")

    star_score = has_star_structure(answer)
    if star_score < 0.5 and question_type in ["behavioral", "situational"]:
        improvements.append("Structure as STAR: Situation → Task → Action → Result for behavioral questions")

    if "searching in google" in answer_lower or "will google" in answer_lower or "look it up" in answer_lower:
        improvements.append("Never mention Googling in an interview — instead explain how you would logically approach the problem")

    seen = set()
    unique = []
    for imp in improvements:
        key = imp[:25]
        if key not in seen:
            seen.add(key)
            unique.append(imp)

    return unique[:4]


def evaluate_response(
    question_text: str,
    answer_text: str,
    question_type: str = "general",
    skill_tag: str = None
) -> Dict:
    if not answer_text or len(answer_text.strip()) < 8:
        return {
            "score": 0.5,
            "strengths": ["Attempted to respond"],
            "improvements": [
                "Provide a complete answer of at least 3-4 sentences",
                "Speak clearly and at normal pace for accurate transcription",
                "Use STAR method for behavioral questions"
            ],
            "feedback": "Answer was too short or empty. Please provide a detailed response."
        }

    relevance_score = check_relevance_to_question(answer_text, question_text, skill_tag)
    is_relevant = relevance_score >= 2.5

    weights = {
        "technical":   {"relevance": 0.40, "length": 0.20, "technical": 0.40},
        "behavioral":  {"relevance": 0.35, "length": 0.25, "technical": 0.40},
        "situational": {"relevance": 0.35, "length": 0.25, "technical": 0.40},
        "general":     {"relevance": 0.40, "length": 0.30, "technical": 0.30}
    }

    w = weights.get(question_type, weights["general"])
    length_score = calculate_length_score(answer_text)
    technical_score = calculate_technical_score(answer_text, question_type)

    rule_score = (
        relevance_score * w["relevance"] +
        length_score * w["length"] +
        technical_score * w["technical"]
    )

    if not is_relevant:
        rule_score = min(rule_score, 3.5)

    final_score = rule_score
    ai_strength = None
    ai_improvement = None

    ai_result = get_ai_feedback(question_text, answer_text, question_type)
    if ai_result:
        ai_weight = 0.45
        final_score = (rule_score * (1 - ai_weight)) + (ai_result["ai_score"] * ai_weight)
        ai_strength = ai_result.get("ai_strength")
        ai_improvement = ai_result.get("ai_improvement")
        if not ai_result.get("is_relevant", True):
            final_score = min(final_score, 3.5)
            is_relevant = False

    final_score = round(max(0.5, min(10.0, final_score)), 1)

    strengths = generate_specific_strengths(answer_text, question_text, question_type, final_score, is_relevant)
    improvements = generate_specific_improvements(answer_text, question_text, question_type, final_score, is_relevant)

    if ai_strength and len(ai_strength) > 10 and ai_strength not in str(strengths):
        strengths = [ai_strength] + strengths[:2]
    if ai_improvement and len(ai_improvement) > 10 and ai_improvement not in str(improvements):
        improvements = [ai_improvement] + improvements[:3]

    if not is_relevant:
        feedback = f"Score: {final_score}/10 — Your answer did not directly address the question. Focus on what is being asked."
    elif final_score >= 9.0:
        feedback = f"Outstanding. Score: {final_score}/10. Exactly the kind of answer that impresses interviewers."
    elif final_score >= 7.5:
        feedback = f"Strong answer. Score: {final_score}/10. Clear experience and solid communication."
    elif final_score >= 6.0:
        feedback = f"Good answer. Score: {final_score}/10. Specific examples and metrics would make this excellent."
    elif final_score >= 4.5:
        feedback = f"Average. Score: {final_score}/10. Lacks depth and real examples — expand your answer significantly."
    elif final_score >= 3.0:
        feedback = f"Below average. Score: {final_score}/10. Study this topic and prepare structured real examples."
    else:
        feedback = f"Needs major improvement. Score: {final_score}/10. The answer does not demonstrate the required knowledge."

    logger.info(f"Evaluated: score={final_score} relevant={is_relevant} type={question_type} words={len(answer_text.split())} ai={'yes' if ai_result else 'no (timeout/error)'}")

    return {
        "score": final_score,
        "strengths": strengths[:3],
        "improvements": improvements[:4],
        "feedback": feedback
    }
