import uuid
from datetime import datetime
from pydantic import BaseModel


class AIReviewResponse(BaseModel):
    id: uuid.UUID
    triggered_at: datetime
    runs_without_errors: bool | None = None
    tests_passed: str | None = None
    style_comments: str | None = None
    logic_comments: str | None = None
    clarifying_question: str | None = None
    predicted_level: float | None = None
    error_occurred: bool

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    id: uuid.UUID
    lecture_id: uuid.UUID
    student_id: uuid.UUID
    github_pr_url: str | None = None
    branch_name: str | None = None
    status: str
    pr_description: str | None = None
    iteration_count: int
    ai_level: float | None = None
    teacher_level: float | None = None
    ai_comment: str | None = None
    teacher_comment: str | None = None
    needs_teacher: bool
    submitted_at: datetime | None = None
    merged_at: datetime | None = None
    created_at: datetime
    reviews: list[AIReviewResponse] = []

    class Config:
        from_attributes = True
