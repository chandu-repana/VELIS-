import logging
import random
from typing import List, Dict
from transformers import pipeline

logger = logging.getLogger(__name__)

QUESTION_TEMPLATES = {
    "technical": [
        "Explain how {skill} works and when you would use it.",
        "What are the key features of {skill} that make it useful?",
        "Describe a project where you used {skill} and the challenges you faced.",
        "What are the best practices when working with {skill}?",
        "How does {skill} compare to its alternatives?"
    ],
    "behavioral": [
        "Tell me about a time you solved a difficult problem using {skill}.",
        "Describe a situation where your knowledge of {skill} helped your team.",
        "Give an example of how you improved a process using {skill}.",
        "How have you kept your {skill} knowledge up to date?",
        "Describe a challenge you faced while learning {skill}."
    ],
    "situational": [
        "If a production system using {skill} went down, how would you debug it?",
        "How would you mentor a junior developer learning {skill}?",
        "If you had to migrate a legacy system to {skill}, what steps would you take?",
        "How would you optimize performance in a {skill} application?",
        "If your team disagreed on using {skill}, how would you handle it?"
    ],
    "general": [
        "Why did you choose to specialize in {skill}?",
        "What resources do you use to stay updated with {skill}?",
        "What is the most complex thing you have built using {skill}?",
        "How do you test and debug code written in {skill}?",
        "What do you enjoy most about working with {skill}?"
    ]
}

GENERAL_QUESTIONS = [
    "Tell me about yourself and your professional background.",
    "What are your greatest strengths as a software developer?",
    "Where do you see yourself in 5 years?",
    "Why are you looking for a new opportunity?",
    "How do you handle working under pressure and tight deadlines?",
    "Describe your ideal work environment.",
    "What motivates you to do your best work?",
    "How do you prioritize tasks when working on multiple projects?",
    "Tell me about a time you failed and what you learned from it.",
    "What makes you a good fit for this role?"
]

_generator = None


def get_generator():
    global _generator
    if _generator is None:
        try:
            logger.info("Loading text generation pipeline...")
            _generator = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                max_length=150,
                device=-1
            )
            logger.info("Text generation pipeline loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load AI model: {e}. Using template-based generation.")
            _generator = None
    return _generator


def generate_questions_from_skills(
    skills: List[str],
    job_role: str = "Software Developer",
    num_questions: int = 10
) -> List[Dict]:
    questions = []
    question_types = ["technical", "behavioral", "situational", "general"]

    skills_to_use = skills[:5] if len(skills) > 5 else skills

    if not skills_to_use:
        for i, q in enumerate(GENERAL_QUESTIONS[:num_questions]):
            questions.append({
                "text": q,
                "question_type": "general",
                "difficulty": "medium",
                "skill_tag": None,
                "order_index": i
            })
        return questions

    for i, skill in enumerate(skills_to_use):
        if len(questions) >= num_questions:
            break

        q_type = question_types[i % len(question_types)]
        templates = QUESTION_TEMPLATES[q_type]
        template = random.choice(templates)
        question_text = template.format(skill=skill.title())

        difficulty = "easy" if i < 2 else "hard" if i >= 4 else "medium"

        questions.append({
            "text": question_text,
            "question_type": q_type,
            "difficulty": difficulty,
            "skill_tag": skill,
            "order_index": i
        })

    general_needed = num_questions - len(questions)
    if general_needed > 0:
        shuffled = GENERAL_QUESTIONS.copy()
        random.shuffle(shuffled)
        for i, q in enumerate(shuffled[:general_needed]):
            questions.append({
                "text": q,
                "question_type": "general",
                "difficulty": "medium",
                "skill_tag": None,
                "order_index": len(questions)
            })

    random.shuffle(questions)
    for i, q in enumerate(questions):
        q["order_index"] = i

    logger.info(f"Generated {len(questions)} questions for skills: {skills_to_use}")
    return questions


def generate_ai_question(skill: str, context: str = "") -> str:
    gen = get_generator()
    if gen is None:
        templates = QUESTION_TEMPLATES["technical"]
        return random.choice(templates).format(skill=skill.title())

    try:
        prompt = f"Generate an interview question about {skill} for a {context} role."
        result = gen(prompt, max_length=100, num_return_sequences=1)
        return result[0]["generated_text"].strip()
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return random.choice(QUESTION_TEMPLATES["technical"]).format(skill=skill.title())
