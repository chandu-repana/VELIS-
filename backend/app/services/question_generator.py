import logging
import random
from typing import List, Dict

logger = logging.getLogger(__name__)

QUESTION_TEMPLATES = {
    "technical": [
        "Explain how {skill} works internally and what makes it different from alternatives.",
        "What are the most important best practices when working with {skill} in production?",
        "Describe the most complex project you built using {skill} and the key challenges.",
        "How do you handle error handling and edge cases specifically in {skill}?",
        "What performance optimization techniques have you used with {skill}?",
        "How does {skill} handle concurrency or parallel processing?",
        "What are the security considerations when using {skill}?",
        "Walk me through how you would debug a critical issue in a {skill} application.",
        "How do you write tests for code that uses {skill}?",
        "What are the limitations of {skill} and when would you choose something else?"
    ],
    "behavioral": [
        "Tell me about a specific project where {skill} was critical to the outcome.",
        "Describe a time you had to learn {skill} quickly under pressure.",
        "Give an example of how you improved a system using {skill}.",
        "Tell me about a time your knowledge of {skill} helped resolve a team conflict.",
        "Describe a failure you had while working with {skill} and what you learned.",
        "How have you mentored others in {skill}?",
        "Tell me about a time you had to convince your team to adopt {skill}.",
        "Describe how you stay updated with new developments in {skill}."
    ],
    "situational": [
        "If a production system using {skill} went down at 2am, what would you do?",
        "How would you migrate a legacy system to use {skill} without downtime?",
        "If your team was divided on using {skill} for a new project, how would you decide?",
        "How would you optimize a slow {skill} application for 10x more users?",
        "If you discovered a security vulnerability in your {skill} implementation, what steps would you take?",
        "How would you onboard a new developer to a large {skill} codebase?",
        "If a client needed a feature that {skill} does not support natively, how would you handle it?"
    ],
    "general": [
        "Tell me about yourself and your experience with {skill}.",
        "Why did you choose to specialize in {skill} over other technologies?",
        "What resources do you use to stay current with {skill}?",
        "What is the hardest problem you solved using {skill}?",
        "How do you approach code reviews for {skill} related code?"
    ]
}

GENERAL_QUESTIONS = [
    "Tell me about yourself and your overall professional background.",
    "What are your greatest technical strengths as a developer?",
    "Describe your ideal development workflow and tools.",
    "How do you handle working under pressure and tight deadlines?",
    "Tell me about a time you disagreed with your manager and how you handled it.",
    "How do you prioritize tasks when working on multiple projects simultaneously?",
    "Describe your experience working in agile or scrum teams.",
    "Tell me about a time you failed at something and what you learned from it.",
    "How do you approach learning new technologies?",
    "What motivates you to do your best work every day?",
    "Describe a situation where you had to deliver bad news to a client or stakeholder.",
    "How do you ensure code quality in your projects?",
    "Tell me about a time you improved a slow or inefficient process.",
    "How do you handle technical debt in a codebase?",
    "Where do you see yourself in 3 to 5 years technically?",
    "What does a good code review look like to you?",
    "How do you approach system design for a new feature?",
    "Tell me about your experience with version control and team collaboration.",
    "How do you handle a situation where requirements keep changing?",
    "What is your approach to documentation?"
]


def generate_questions_from_skills(
    skills: List[str],
    job_role: str = "Software Developer",
    num_questions: int = 10
) -> List[Dict]:
    num_questions = min(max(num_questions, 1), 25)
    questions = []
    question_texts = set()

    skills_to_use = skills[:8] if len(skills) > 8 else skills

    if not skills_to_use:
        shuffled = GENERAL_QUESTIONS.copy()
        random.shuffle(shuffled)
        for i, q in enumerate(shuffled[:num_questions]):
            questions.append({
                "text": q,
                "question_type": "general",
                "difficulty": "medium",
                "skill_tag": None,
                "order_index": i
            })
        return questions

    skill_questions_target = min(int(num_questions * 0.65), len(skills_to_use) * 4)
    general_target = num_questions - skill_questions_target

    difficulties = ["easy", "medium", "medium", "hard"]
    q_types = ["technical", "behavioral", "situational", "technical", "general"]

    for skill_idx, skill in enumerate(skills_to_use):
        if len(questions) >= skill_questions_target:
            break
        questions_per_skill = max(1, skill_questions_target // len(skills_to_use))
        for q_count in range(questions_per_skill):
            if len(questions) >= skill_questions_target:
                break
            q_type = q_types[(skill_idx + q_count) % len(q_types)]
            templates = QUESTION_TEMPLATES[q_type]
            question_text = ""
            for _ in range(5):
                template = random.choice(templates)
                candidate = template.format(skill=skill.title())
                if candidate not in question_texts:
                    question_text = candidate
                    question_texts.add(question_text)
                    break
            if not question_text:
                continue
            difficulty = difficulties[q_count % len(difficulties)]
            questions.append({
                "text": question_text,
                "question_type": q_type,
                "difficulty": difficulty,
                "skill_tag": skill,
                "order_index": len(questions)
            })

    shuffled_general = GENERAL_QUESTIONS.copy()
    random.shuffle(shuffled_general)
    for q in shuffled_general:
        if len(questions) >= num_questions:
            break
        if q not in question_texts:
            question_texts.add(q)
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

    logger.info(f"Generated {len(questions)} questions for {len(skills_to_use)} skills")
    return questions[:num_questions]
