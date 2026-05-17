import uuid
from datetime import datetime
from pydantic import BaseModel


class LectureBase(BaseModel):
    number: int
    title: str
    block: int
    description: str | None = None
    topics: str | None = None
    real_code_link: str | None = None
    assignment_type: str
    assignment_description: str | None = None


class LectureCreate(LectureBase):
    content: str | None = None


class LectureUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignment_type: str | None = None
    assignment_description: str | None = None
    content: str | None = None
    is_published: bool | None = None
    lecture_date: datetime | None = None


class LectureResponse(LectureBase):
    id: uuid.UUID
    content: str | None = None
    is_published: bool
    lecture_date: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
