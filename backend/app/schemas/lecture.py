import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class LectureBase(BaseModel):
    number: int
    title: str = Field(max_length=255)
    block: int
    description: str | None = Field(default=None, max_length=10000)
    topics: str | None = Field(default=None, max_length=5000)
    real_code_link: str | None = Field(default=None, max_length=500)
    assignment_type: str = Field(max_length=2, pattern=r"^(A|B|C|AB)$")
    assignment_description: str | None = Field(default=None, max_length=5000)


class LectureCreate(LectureBase):
    content: str | None = None


class LectureUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    assignment_type: str | None = Field(default=None, max_length=2, pattern=r"^(A|B|C|AB)$")
    assignment_description: str | None = Field(default=None, max_length=5000)
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
