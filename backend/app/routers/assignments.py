import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.assignment import Assignment
from app.models.ai_review import AIReview
from app.schemas.assignment import AssignmentResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


@router.get("", response_model=list[AssignmentResponse])
async def get_assignments(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment)
        .where(Assignment.student_id == current_user["student_id"])
        .options(selectinload(Assignment.reviews))
        .order_by(Assignment.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(
    assignment_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment)
        .where(
            Assignment.id == assignment_id,
            Assignment.student_id == current_user["student_id"],
        )
        .options(selectinload(Assignment.reviews))
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.post("/{assignment_id}/review")
async def trigger_review(
    assignment_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Assignment).where(
            Assignment.id == assignment_id,
            Assignment.student_id == current_user["student_id"],
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    from app.services.celery_app import celery_app
    celery_app.send_task("run_ai_review", args=[str(assignment_id)])

    return {"message": "Review triggered"}
