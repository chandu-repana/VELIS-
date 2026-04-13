from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel
import logging
import httpx

logger = logging.getLogger(__name__)

router = APIRouter()

GITHUB_CLIENT_ID = "Ov23li24tF4OzEewUsvS"
GITHUB_CLIENT_SECRET = "ab7c03519e42aace3ee30565d838ab40f0f274a8"


class GoogleTokenRequest(BaseModel):
    token: str


class GitHubCodeRequest(BaseModel):
    code: str


@router.get("/status")
async def auth_status():
    return {"status": "auth endpoint ready"}


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token(subject=str(user.id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "full_name": user.full_name, "email": user.email}
    }


@router.post("/google")
async def google_login(data: GoogleTokenRequest, db: Session = Depends(get_db)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"id_token": data.token}
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        info = resp.json()
        email = info.get("email")
        name = info.get("name", email)
        if not email:
            raise HTTPException(status_code=400, detail="Could not get email from Google")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                full_name=name,
                email=email,
                hashed_password=hash_password("google_oauth_" + email),
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        token = create_access_token(subject=str(user.id))
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user.id, "full_name": user.full_name, "email": user.email}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google login error: {e}")
        raise HTTPException(status_code=500, detail="Google login failed")


@router.post("/github")
async def github_login(data: GitHubCodeRequest, db: Session = Depends(get_db)):
    logger.info(f"GitHub login attempt with code: {data.code[:10]}...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": data.code
                },
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )

        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            error_desc = token_data.get("error_description", "No access token received")
            raise HTTPException(status_code=401, detail=f"GitHub auth failed: {error_desc}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            user_resp = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}", "Accept": "application/vnd.github.v3+json"}
            )
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"token {access_token}", "Accept": "application/vnd.github.v3+json"}
            )

        github_user = user_resp.json()
        emails = email_resp.json()

        email = None
        if isinstance(emails, list):
            primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
            if primary:
                email = primary["email"]

        if not email:
            email = github_user.get("email")
        if not email:
            email = f"github_{github_user['id']}@velis.local"

        name = github_user.get("name") or github_user.get("login") or "GitHub User"

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                full_name=name,
                email=email,
                hashed_password=hash_password("github_oauth_" + str(github_user["id"])),
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        velis_token = create_access_token(subject=str(user.id))
        return {
            "access_token": velis_token,
            "token_type": "bearer",
            "user": {"id": user.id, "full_name": user.full_name, "email": user.email}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"GitHub login failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_me(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
