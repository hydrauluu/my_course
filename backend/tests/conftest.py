import os
import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.student import Student
from app.models.lecture import Lecture
from app.models.assignment import Assignment
from app.models.ai_review import AIReview
from app.services.auth import create_access_token

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/python_course_test",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def mock_claude():
    with patch("app.services.ai_review.run_ai_review", new_callable=AsyncMock) as mock:
        mock.return_value = (
            "✅ Код запускается без ошибок\n"
            "✅ Тесты пройдены (3/3)\n"
            "📝 Стиль: хороший код\n"
            "❓ Вопрос: Почему выбран этот подход?"
        )
        yield mock


@pytest.fixture(autouse=True)
def mock_github_exchange():
    with patch("app.services.github.exchange_code_for_token", new_callable=AsyncMock) as mock:
        mock.return_value = {"access_token": "test-gh-token"}
        yield mock


@pytest.fixture(autouse=True)
def mock_github_user():
    with patch("app.services.github.get_github_user", new_callable=AsyncMock) as mock:
        mock.return_value = {"login": "testuser", "email": "test@example.com", "name": "Test User"}
        yield mock


@pytest.fixture
def mock_celery():
    with patch("app.services.celery_app.celery_app.send_task") as mock:
        yield mock


@pytest.fixture
def mock_webhook_verify():
    with patch("app.routers.webhooks.verify_webhook", new_callable=AsyncMock) as mock:
        yield mock


@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def student_id():
    return uuid.uuid4()


@pytest.fixture
def teacher_id():
    return uuid.uuid4()


@pytest.fixture
def student_token(student_id):
    return create_access_token(student_id, "testuser", "student")


@pytest.fixture
def teacher_token(teacher_id):
    return create_access_token(teacher_id, "teacher_user", "teacher")


@pytest.fixture
def auth_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def teacher_headers(teacher_token):
    return {"Authorization": f"Bearer {teacher_token}"}


@pytest_asyncio.fixture
async def seeded_lecture(db_session: AsyncSession):
    lecture = Lecture(
        number=1,
        title="Test Lecture",
        block=1,
        description="Test description",
        topics="test",
        assignment_type="A",
        is_published=True,
    )
    db_session.add(lecture)
    await db_session.commit()
    await db_session.refresh(lecture)
    return lecture


@pytest_asyncio.fixture
async def seeded_assignment(db_session: AsyncSession, student_id, seeded_lecture):
    student = Student(id=student_id, github_username="testuser")
    db_session.add(student)

    assignment = Assignment(
        lecture_id=seeded_lecture.id,
        student_id=student_id,
        github_pr_url="https://github.com/test/repo/pull/1",
        branch_name="hw01/testuser",
        status="open",
        iteration_count=1,
    )
    db_session.add(assignment)
    await db_session.commit()
    await db_session.refresh(assignment)
    return assignment
