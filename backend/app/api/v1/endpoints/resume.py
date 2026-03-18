from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeParseResponse, ResumeOut
from app.utils.file_handler import save_upload_file
from app.services.resume_parser import parse_resume
from app.services.skill_extractor import extract_all
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def resume_status():
    return {"status": "resume endpoint ready"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Upload a resume file (PDF or DOCX).
    Saves the file and creates a database record.
    """
    try:
        file_path = await save_upload_file(file, subfolder="resumes")

        resume = Resume(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path,
            file_type=file.content_type,
            is_parsed=False
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        logger.info(f"Resume uploaded: id={resume.id} user={user_id}")

        return ResumeUploadResponse(
            id=resume.id,
            filename=resume.filename,
            file_type=resume.file_type,
            is_parsed=resume.is_parsed,
            message="Resume uploaded successfully. Call /parse to extract skills."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume upload failed"
        )


@router.post("/parse/{resume_id}", response_model=ResumeParseResponse)
async def parse_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """
    Parse an uploaded resume to extract skills, experience, and education.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    try:
        raw_text = parse_resume(resume.file_path, resume.file_type)
        extracted = extract_all(raw_text)

        resume.raw_text = raw_text
        resume.extracted_skills = extracted["skills"]
        resume.experience_years = extracted["experience_years"]
        resume.education = extracted["education"]
        resume.is_parsed = True

        db.commit()
        db.refresh(resume)

        logger.info(f"Resume parsed: id={resume_id} skills={len(extracted['skills'])}")

        return ResumeParseResponse(
            id=resume.id,
            filename=resume.filename,
            extracted_skills=resume.extracted_skills,
            experience_years=resume.experience_years,
            education=resume.education,
            is_parsed=resume.is_parsed
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on disk"
        )
    except Exception as e:
        logger.error(f"Resume parse failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume parsing failed: {str(e)}"
        )


@router.get("/list", response_model=List[ResumeOut])
async def list_resumes(
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """Get all resumes for a user."""
    resumes = db.query(Resume).filter(Resume.user_id == user_id).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    return resume
