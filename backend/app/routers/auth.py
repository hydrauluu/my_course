import logging
import secrets
from datetime import datetime, timezone

from jose import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.student import Student
from app.rate_limiter import limiter
from app.schemas.auth import GitHubLoginRequest, UserInfo
from app.services.auth import (
    COOKIE_NAME,
    create_access_token,
    get_current_user,
    set_auth_cookie,
    set_csrf_cookie,
    clear_auth_cookie,
    verify_csrf,
    _blacklist_token,
)
from app.services.github import exchange_code_for_token, get_github_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

OAUTH_STATE_COOKIE = "github_oauth_state"


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
async def github_callback(request: Request, code: str, state: str, db: AsyncSession = Depends(get_db)):
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not cookie_state or not secrets.compare_digest(cookie_state, state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    student = await _authenticate_student(code, db)
    jwt_token = create_access_token(student.id, student.github_username, student.role)
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard", status_code=302)
    set_auth_cookie(response, jwt_token)
    set_csrf_cookie(response)
    response.delete_cookie(key=OAUTH_STATE_COOKIE, path="/")
    return response


@router.post("/github/login")
@limiter.limit("10/minute")
async def github_login(request: Request, payload: GitHubLoginRequest, db: AsyncSession = Depends(get_db)):
    await verify_csrf(request)
    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not cookie_state or not secrets.compare_digest(cookie_state, payload.state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    student = await _authenticate_student(payload.code, db)
    jwt_token = create_access_token(student.id, student.github_username, student.role)
    response = Response(status_code=200)
    set_auth_cookie(response, jwt_token)
    set_csrf_cookie(response)
    return response


@router.get("/me", response_model=UserInfo)
@limiter.limit("60/minute")
async def get_me(request: Request, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.id == current_user["student_id"]))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo(
        id=student.id,
        github_username=student.github_username,
        email=student.email,
        full_name=student.full_name,
        role=student.role,
    )


@router.post("/logout")
@limiter.limit("30/minute")
async def logout(request: Request, response: Response):
    await verify_csrf(request)
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                remaining = int(exp - datetime.now(timezone.utc).timestamp())
                if remaining > 0:
                    _blacklist_token(jti, remaining)
        except Exception:
            logger.warning("Failed to blacklist token during logout")
    clear_auth_cookie(response)
    return {"status": "ok"}


@router.get("/github/login")
@limiter.limit("60/minute")
async def github_login_url(request: Request, response: Response):
    state = secrets.token_urlsafe(32)
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=600,
        path="/",
    )
    return {
        "url": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=user:email,repo&state={state}"
    }
