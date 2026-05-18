import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

security = HTTPBearer()


def create_access_token(student_id: uuid.UUID, github_username: str, role: str = "student") -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(student_id),
        "github_username": github_username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return {
            "student_id": uuid.UUID(payload["sub"]),
            "github_username": payload["github_username"],
            "role": payload.get("role", "student"),
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_teacher(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        role = payload.get("role", "student")
        if role not in ("teacher", "admin"):
            raise HTTPException(status_code=403, detail="Teacher access required")
        return {
            "student_id": uuid.UUID(payload["sub"]),
            "github_username": payload["github_username"],
            "role": role,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
