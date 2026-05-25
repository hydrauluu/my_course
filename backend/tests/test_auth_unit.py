import uuid
import pytest
from jose import jwt
from fastapi import HTTPException

from app.config import settings
from app.services.auth import (
    create_access_token,
    get_current_user,
    get_current_teacher,
    _decode_token,
    COOKIE_NAME,
)


@pytest.fixture
def student_id():
    return uuid.uuid4()


@pytest.fixture
def teacher_id():
    return uuid.uuid4()


class TestTokenCreation:
    def test_create_access_token_returns_string(self, student_id):
        token = create_access_token(student_id, "testuser", "student")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_claims(self, student_id):
        token = create_access_token(student_id, "testuser", "student")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["sub"] == str(student_id)
        assert payload["github_username"] == "testuser"
        assert payload["role"] == "student"
        assert "jti" in payload
        assert "iat" in payload
        assert "exp" in payload

    def test_create_token_with_teacher_role(self, teacher_id):
        token = create_access_token(teacher_id, "teacher_user", "teacher")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["role"] == "teacher"

    def test_create_token_with_admin_role(self, teacher_id):
        token = create_access_token(teacher_id, "admin_user", "admin")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload["role"] == "admin"

    def test_create_token_different_jti(self, student_id):
        token1 = create_access_token(student_id, "testuser", "student")
        token2 = create_access_token(student_id, "testuser", "student")
        payload1 = jwt.decode(token1, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        payload2 = jwt.decode(token2, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        assert payload1["jti"] != payload2["jti"]


class TestDecodeToken:
    def test_decode_valid_token(self, student_id):
        token = create_access_token(student_id, "testuser", "student")
        user = _decode_token(token)
        assert user["student_id"] == student_id
        assert user["github_username"] == "testuser"
        assert user["role"] == "student"

    def test_decode_invalid_token(self):
        with pytest.raises(HTTPException) as exc:
            _decode_token("invalid-token")
        assert exc.value.status_code == 401

    def test_decode_expired_token(self, student_id):
        from datetime import datetime, timedelta, timezone
        payload = {
            "sub": str(student_id),
            "github_username": "testuser",
            "role": "student",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "jti": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(HTTPException) as exc:
            _decode_token(token)
        assert exc.value.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_no_token(self):
        class MockRequest:
            cookies = {}
            headers = {}

        with pytest.raises(HTTPException) as exc:
            await get_current_user(MockRequest())
        assert exc.value.status_code == 401

    async def test_cookie_token(self, student_id):
        token = create_access_token(student_id, "testuser", "student")

        class MockRequest:
            cookies = {COOKIE_NAME: token}
            headers = {}

        user = await get_current_user(MockRequest())
        assert user["github_username"] == "testuser"
        assert user["role"] == "student"

    async def test_bearer_token(self, student_id):
        token = create_access_token(student_id, "testuser", "student")

        from starlette.requests import Request
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
            "cookies": {},
            "query_string": b"",
        }
        request = Request(scope)
        user = await get_current_user(request)
        assert user["github_username"] == "testuser"


class TestGetCurrentTeacher:
    @pytest.mark.asyncio
    async def test_rejects_student(self, student_id):
        token = create_access_token(student_id, "testuser", "student")

        class MockRequest:
            cookies = {COOKIE_NAME: token}
            headers = {}

        with pytest.raises(HTTPException) as exc:
            await get_current_teacher(MockRequest())
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_accepts_teacher(self, teacher_id):
        token = create_access_token(teacher_id, "teacher_user", "teacher")

        class MockRequest:
            cookies = {COOKIE_NAME: token}
            headers = {}

        user = await get_current_teacher(MockRequest())
        assert user["role"] == "teacher"

    @pytest.mark.asyncio
    async def test_accepts_admin(self, teacher_id):
        token = create_access_token(teacher_id, "admin_user", "admin")

        class MockRequest:
            cookies = {COOKIE_NAME: token}
            headers = {}

        user = await get_current_teacher(MockRequest())
        assert user["role"] == "admin"
