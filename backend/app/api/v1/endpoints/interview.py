from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.interview import Interview, InterviewStatus
from app.models.question import Question, QuestionType, DifficultyLevel
from app.models.resume import Resume
from app.schemas.interview import InterviewCreate, InterviewOut, InterviewStartResponse
from app.schemas.question import QuestionOut
from app.services.question_generator import generate_questions_from_skills
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def interview_status():
    return {"status": "interview endpoint ready"}


@router.post("/create", response_model=InterviewStartResponse)
async def create_interview(
    data: InterviewCreate,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(
        Resume.id == data.resume_id,
        Resume.user_id == user_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    if not resume.is_parsed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume must be parsed before creating an interview. Call /resume/parse first."
        )

    try:
        interview = Interview(
            user_id=user_id,
            resume_id=data.resume_id,
            title=data.title,
            job_role=data.job_role,
            status=InterviewStatus.PENDING,
            total_questions=data.num_questions,
            answered_questions=0
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        raw_questions = generate_questions_from_skills(
            skills=resume.extracted_skills or [],
            job_role=data.job_role,
            num_questions=data.num_questions
        )

        for q in raw_questions:
            question = Question(
                interview_id=interview.id,
                text=q["text"],
                question_type=QuestionType(q["question_type"]),
                difficulty=DifficultyLevel(q["difficulty"]),
                skill_tag=q.get("skill_tag"),
                order_index=q["order_index"]
            )
            db.add(question)

        db.commit()

        logger.info(f"Interview created: id={interview.id} questions={len(raw_questions)}")

        return InterviewStartResponse(
            interview_id=interview.id,
            title=interview.title,
            job_role=interview.job_role,
            total_questions=len(raw_questions),
            message=f"Interview created with {len(raw_questions)} questions. Call /start to begin."
        )

    except Exception as e:
        logger.error(f"Interview creation failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interview creation failed: {str(e)}"
        )


@router.post("/start/{interview_id}")
async def start_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.status = InterviewStatus.IN_PROGRESS
    db.commit()

    return {"message": "Interview started", "interview_id": interview_id, "status": "in_progress"}


@router.get("/{interview_id}/questions", response_model=List[QuestionOut])
async def get_interview_questions(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions = db.query(Question).filter(
        Question.interview_id == interview_id
    ).order_by(Question.order_index).all()

    return questions


@router.get("/{interview_id}/question/{question_index}", response_model=QuestionOut)
async def get_question_by_index(
    interview_id: int,
    question_index: int,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(
        Question.interview_id == interview_id,
        Question.order_index == question_index
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    return question


@router.get("/list", response_model=List[InterviewOut])
async def list_interviews(
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).filter(
        Interview.user_id == user_id
    ).order_by(Interview.created_at.desc()).all()
    return interviews


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview
