import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Integer, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AIReview(Base):
    __tablename__ = "ai_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    runs_without_errors: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    tests_passed: Mapped[str | None] = mapped_column(String(50), nullable=True)
    style_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    logic_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    clarifying_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    predicted_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_occurred: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assignment = relationship("Assignment", back_populates="reviews")
