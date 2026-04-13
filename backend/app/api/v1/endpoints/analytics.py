from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.interview import Interview
from app.models.question import Question
from app.models.response import Response
from app.services.evaluator import evaluate_response
from app.services.feedback import generate_overall_feedback
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status")
async def analytics_status():
    return {"status": "analytics endpoint ready"}


@router.post("/evaluate/{response_id}")
async def evaluate_single_response(response_id: int, db: Session = Depends(get_db)):
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    if not response.transcribed_text:
        raise HTTPException(status_code=400, detail="Response has no transcribed text")

    question = db.query(Question).filter(Question.id == response.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        result = evaluate_response(
            question_text=question.text,
            answer_text=response.transcribed_text,
            question_type=question.question_type.value,
            skill_tag=question.skill_tag
        )
        response.score = result["score"]
        response.feedback = result["feedback"]
        response.strengths = result["strengths"]
        response.improvements = result["improvements"]
        response.is_evaluated = True
        db.commit()
        db.refresh(response)
        return {
            "response_id": response_id,
            "score": result["score"],
            "feedback": result["feedback"],
            "strengths": result["strengths"],
            "improvements": result["improvements"]
        }
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/evaluate-interview/{interview_id}")
async def evaluate_all_responses(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    responses = db.query(Response).filter(Response.interview_id == interview_id).all()
    if not responses:
        raise HTTPException(status_code=404, detail="No responses found")

    evaluated = []
    scores = []
    question_types = []

    for response in responses:
        if not response.transcribed_text or len(response.transcribed_text.strip()) < 5:
            continue
        question = db.query(Question).filter(Question.id == response.question_id).first()
        if not question:
            continue
        result = evaluate_response(
            question_text=question.text,
            answer_text=response.transcribed_text,
            question_type=question.question_type.value,
            skill_tag=question.skill_tag
        )
        response.score = result["score"]
        response.feedback = result["feedback"]
        response.strengths = result["strengths"]
        response.improvements = result["improvements"]
        response.is_evaluated = True
        scores.append(result["score"])
        question_types.append(question.question_type.value)
        evaluated.append({
            "response_id": response.id,
            "question_id": response.question_id,
            "score": result["score"],
            "feedback": result["feedback"]
        })

    if scores:
        interview.overall_score = round(sum(scores) / len(scores), 1)

    db.commit()

    overall_feedback = generate_overall_feedback(
        scores=scores,
        question_types=question_types,
        job_role=interview.job_role or "Software Developer",
        individual_results=evaluated
    )

    return {
        "interview_id": interview_id,
        "total_evaluated": len(evaluated),
        "individual_results": evaluated,
        "overall_feedback": overall_feedback
    }


@router.get("/interview/{interview_id}/report")
async def get_interview_report(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    responses = db.query(Response).filter(
        Response.interview_id == interview_id,
        Response.is_evaluated == True
    ).all()

    questions = db.query(Question).filter(Question.interview_id == interview_id).all()
    question_map = {q.id: q for q in questions}

    report_items = []
    for r in responses:
        q = question_map.get(r.question_id)
        report_items.append({
            "question": q.text if q else "Unknown",
            "question_type": q.question_type.value if q else "general",
            "skill_tag": q.skill_tag if q else None,
            "answer": r.transcribed_text,
            "score": r.score,
            "feedback": r.feedback,
            "strengths": r.strengths or [],
            "improvements": r.improvements or []
        })

    scores = [r.score for r in responses if r.score is not None]
    question_types = [item["question_type"] for item in report_items]

    overall_feedback = generate_overall_feedback(
        scores=scores,
        question_types=question_types,
        job_role=interview.job_role or "Software Developer",
        individual_results=report_items
    )

    return {
        "interview_id": interview_id,
        "job_role": interview.job_role,
        "status": interview.status.value,
        "overall_score": interview.overall_score,
        "total_questions": interview.total_questions,
        "answered_questions": interview.answered_questions,
        "overall_feedback": overall_feedback,
        "detailed_results": report_items
    }


@router.get("/dashboard/{user_id}")
async def get_user_dashboard(user_id: int, db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(
        Interview.user_id == user_id
    ).order_by(Interview.created_at.desc()).all()

    if not interviews:
        return {
            "total_interviews": 0,
            "average_score": 0,
            "best_score": 0,
            "completed_interviews": 0,
            "interviews": []
        }

    scores = [i.overall_score for i in interviews if i.overall_score is not None]
    interview_list = []
    for interview in interviews:
        interview_list.append({
            "id": interview.id,
            "title": interview.title,
            "job_role": interview.job_role,
            "status": interview.status.value,
            "overall_score": interview.overall_score,
            "total_questions": interview.total_questions,
            "answered_questions": interview.answered_questions,
            "created_at": interview.created_at.isoformat()
        })

    return {
        "total_interviews": len(interviews),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "completed_interviews": len([i for i in interviews if i.status.value == "completed"]),
        "interviews": interview_list
    }
