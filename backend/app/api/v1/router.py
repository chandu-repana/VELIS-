"""
Central API router for v1.
All endpoint modules are registered here.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, resume, interview, voice, analytics

api_router = APIRouter()

api_router.include_router(auth.router,      prefix="/auth",      tags=["Authentication"])
api_router.include_router(resume.router,    prefix="/resume",    tags=["Resume"])
api_router.include_router(interview.router, prefix="/interview", tags=["Interview"])
api_router.include_router(voice.router,     prefix="/voice",     tags=["Voice"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
