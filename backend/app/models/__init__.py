# Import all models here so Alembic can detect them for migrations
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview
from app.models.question import Question
from app.models.response import Response
from app.models.evaluation import Evaluation

__all__ = [
    "User",
    "Resume",
    "Interview",
    "Question",
    "Response",
    "Evaluation",
]