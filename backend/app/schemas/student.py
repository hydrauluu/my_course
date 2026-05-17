import uuid
from datetime import datetime
from pydantic import BaseModel


class StudentBase(BaseModel):
    github_username: str
    email: str | None = None
    full_name: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: uuid.UUID
    cohort_year: int
    entry_slice_score: float | None = None
    exit_slice_score: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    student: StudentResponse
    total_lectures: int
    completed_lectures: int
    assignments: list[dict]
    latest_review: dict | None = None
