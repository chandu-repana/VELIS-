from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.question import Question
from app.models.response import Response
from app.models.interview import Interview, InterviewStatus
from app.schemas.response import ResponseOut, TranscriptionResult
from app.services.tts_service import generate_question_audio
from app.services.stt_service import transcribe_audio_safe
from app.utils.audio_handler import save_audio_file
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def voice_status():
    return {"status": "voice endpoint ready"}


@router.post("/tts/{question_id}")
async def question_to_speech(
    question_id: int,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        if question.audio_path and os.path.exists(question.audio_path):
            return FileResponse(
                question.audio_path,
                media_type="audio/mpeg",
                filename=f"question_{question_id}.mp3"
            )

        audio_path = generate_question_audio(question.text, question_id)
        question.audio_path = audio_path
        db.commit()

        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename=f"question_{question_id}.mp3"
        )

    except Exception as e:
        logger.error(f"TTS failed for question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS generation failed: {str(e)}"
        )


@router.post("/stt/{question_id}/{interview_id}", response_model=TranscriptionResult)
async def speech_to_text(
    question_id: int,
    interview_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    try:
        audio_path = await save_audio_file(file, subfolder="responses")
        result = transcribe_audio_safe(audio_path)

        existing = db.query(Response).filter(
            Response.question_id == question_id,
            Response.interview_id == interview_id
        ).first()

        if existing:
            existing.audio_path = audio_path
            existing.transcribed_text = result["text"]
            db.commit()
            db.refresh(existing)
            response_id = existing.id
        else:
            response = Response(
                question_id=question_id,
                interview_id=interview_id,
                audio_path=audio_path,
                transcribed_text=result["text"],
                is_evaluated=False,
                strengths=[],
                improvements=[]
            )
            db.add(response)

            interview.answered_questions = (interview.answered_questions or 0) + 1
            if interview.answered_questions >= interview.total_questions:
                interview.status = InterviewStatus.COMPLETED

            db.commit()
            db.refresh(response)
            response_id = response.id

        return TranscriptionResult(
            question_id=question_id,
            interview_id=interview_id,
            transcribed_text=result["text"],
            language=result.get("language", "en"),
            response_id=response_id,
            message="Audio transcribed successfully"
        )

    except Exception as e:
        logger.error(f"STT failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech transcription failed: {str(e)}"
        )


@router.get("/response/{response_id}", response_model=ResponseOut)
async def get_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    return response


@router.get("/interview/{interview_id}/responses")
async def get_interview_responses(
    interview_id: int,
    db: Session = Depends(get_db)
):
    responses = db.query(Response).filter(
        Response.interview_id == interview_id
    ).all()
    return responses
