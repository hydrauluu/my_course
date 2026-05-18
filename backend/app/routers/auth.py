import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.student import Student
from app.rate_limiter import limiter
from app.schemas.auth import GitHubLoginRequest, TokenResponse, UserInfo
from app.services.auth import create_access_token, get_current_user
from app.services.github import exchange_code_for_token, get_github_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


async def _authenticate_student(code: str, db: AsyncSession) -> Student:
    token_data = await exchange_code_for_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    github_user = await get_github_user(access_token)
    github_username = github_user["login"]

    result = await db.execute(select(Student).where(Student.github_username == github_username))
    student = result.scalar_one_or_none()

    if not student:
        student = Student(
            github_username=github_username,
            email=github_user.get("email"),
            full_name=github_user.get("name"),
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        logger.info("Created new student account: %s", github_username)

    return student


@router.get("/github/callback")
@limiter.limit("10/minute")
async def github_callback(request: Request, code: str, db: AsyncSession = Depends(get_db)):
    student = await _authenticate_student(code, db)
    jwt_token = create_access_token(student.id, student.github_username, student.role)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login?token={jwt_token}")


@router.post("/github/login")
@limiter.limit("10/minute")
async def github_login(request: Request, payload: GitHubLoginRequest, db: AsyncSession = Depends(get_db)):
    student = await _authenticate_student(payload.code, db)
    jwt_token = create_access_token(student.id, student.github_username, student.role)
    return TokenResponse(access_token=jwt_token)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == current_user["student_id"]))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(
        id=student.id,
        github_username=student.github_username,
        email=student.email,
        full_name=student.full_name,
    )


@router.get("/github/login")
async def github_login_url():
    return {
        "url": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=user:email,repo"
    }
