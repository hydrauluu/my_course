import uuid
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer

from app.config import settings

security = HTTPBearer(auto_error=False)

COOKIE_NAME = "auth_token"
CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"


def create_access_token(student_id: uuid.UUID, github_username: str, role: str = "student") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(student_id),
        "github_username": github_username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_HOURS * 3600,
        path="/",
    )


def set_csrf_cookie(response: Response):
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=settings.JWT_EXPIRATION_HOURS * 3600,
        path="/",
    )
    return token


def clear_auth_cookie(response: Response):
    response.delete_cookie(key=COOKIE_NAME, path="/")
    response.delete_cookie(key=CSRF_COOKIE_NAME, path="/")


async def verify_csrf(request: Request):
    if not settings.CSRF_ENABLED:
        return
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)
    if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=403, detail="CSRF token mismatch")


def _decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return {
            "student_id": uuid.UUID(payload["sub"]),
            "github_username": payload["github_username"],
            "role": payload.get("role", "student"),
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        return _decode_token(token)

    auth = await security(request)
    if auth and auth.credentials:
        return _decode_token(auth.credentials)

    raise HTTPException(status_code=401, detail="Not authenticated")


async def get_current_teacher(request: Request) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        user = _decode_token(token)
    else:
        auth = await security(request)
        if not auth or not auth.credentials:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user = _decode_token(auth.credentials)

    if user["role"] not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user
