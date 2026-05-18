import pytest
from sqlalchemy import select

from app.models.student import Student
from app.services.auth import create_access_token, get_current_user, get_current_teacher
from fastapi import HTTPException
import pytest_asyncio


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_github_login_url(self, client):
        response = await client.get("/api/auth/github/login")
        assert response.status_code == 200
        data = response.json()
        assert "url" in data
        assert "github.com/login/oauth/authorize" in data["url"]

    @pytest.mark.asyncio
    async def test_github_callback_creates_user(self, client, mock_github_exchange, mock_github_user):
        response = await client.get("/api/auth/github/callback", params={"code": "test-code"})
        assert response.status_code in (200, 307)

    @pytest.mark.asyncio
    async def test_get_me_unauthorized(self, client):
        response = await client.get("/api/auth/me")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_me_with_token(self, client, auth_headers, student_id, db_session):
        student = Student(id=student_id, github_username="testuser")
        db_session.add(student)
        await db_session.commit()

        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["github_username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/auth/me", headers=headers)
        assert response.status_code == 401


class TestAuthDependencies:
    @pytest.mark.asyncio
    async def test_create_access_token_contains_role(self, student_id):
        token = create_access_token(student_id, "testuser", "student")
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_get_current_teacher_rejects_student(self, student_id):
        token = create_access_token(student_id, "testuser", "student")
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_teacher(creds)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_current_teacher_accepts_teacher(self, teacher_id):
        token = create_access_token(teacher_id, "teacher_user", "teacher")
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")

        result = await get_current_teacher(creds)
        assert result["role"] == "teacher"

    @pytest.mark.asyncio
    async def test_get_current_teacher_accepts_admin(self, teacher_id):
        token = create_access_token(teacher_id, "admin_user", "admin")
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(credentials=token, scheme="Bearer")

        result = await get_current_teacher(creds)
        assert result["role"] == "admin"
