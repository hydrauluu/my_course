import uuid
from datetime import datetime
from pydantic import BaseModel


class StudentResponse(BaseModel):
    github_username: str
    email: str | None = None
    full_name: str | None = None
    id: uuid.UUID
    cohort_year: int
    entry_slice_score: float | None = None
    exit_slice_score: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True
