import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.lecture import Lecture
from app.models.assignment import Assignment
from app.schemas.lecture import LectureResponse, LectureCreate, LectureUpdate
from app.rate_limiter import limiter
from app.services.auth import get_current_user, get_current_teacher, verify_csrf

router = APIRouter(prefix="/api/lectures", tags=["lectures"])


@router.get("", response_model=list[LectureResponse])
@limiter.limit("60/minute")
async def get_lectures(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lecture).where(Lecture.is_published == True).order_by(Lecture.number)
    )
    return result.scalars().all()


@router.get("/blocks")
@limiter.limit("60/minute")
async def get_lectures_by_block(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lecture).where(Lecture.is_published == True).order_by(Lecture.number)
    )
    lectures = result.scalars().all()

    blocks = {}
    for lecture in lectures:
        block_key = f"block_{lecture.block}"
        if block_key not in blocks:
            blocks[block_key] = {
                "block": lecture.block,
                "title": _block_title(lecture.block),
                "lectures": [],
            }
        blocks[block_key]["lectures"].append(LectureResponse.model_validate(lecture))

    return list(blocks.values())


@router.get("/{lecture_id}", response_model=LectureResponse)
@limiter.limit("60/minute")
async def get_lecture(request: Request, lecture_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lecture).where(Lecture.id == lecture_id, Lecture.is_published == True)
    )
    lecture = result.scalar_one_or_none()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.get("/number/{number}", response_model=LectureResponse)
@limiter.limit("60/minute")
async def get_lecture_by_number(request: Request, number: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lecture).where(Lecture.number == number, Lecture.is_published == True)
    )
    lecture = result.scalar_one_or_none()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.post("", response_model=LectureResponse)
@limiter.limit("30/minute")
async def create_lecture(
    request: Request,
    lecture: LectureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_teacher),
):
    await verify_csrf(request)
    db_lecture = Lecture(**lecture.model_dump())
    db.add(db_lecture)
    await db.commit()
    await db.refresh(db_lecture)
    return db_lecture


@router.patch("/{lecture_id}", response_model=LectureResponse)
@limiter.limit("30/minute")
async def update_lecture(
    request: Request,
    lecture_id: uuid.UUID,
    lecture: LectureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_teacher),
):
    await verify_csrf(request)
    result = await db.execute(select(Lecture).where(Lecture.id == lecture_id))
    db_lecture = result.scalar_one_or_none()
    if not db_lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    for key, value in lecture.model_dump(exclude_unset=True).items():
        setattr(db_lecture, key, value)

    await db.commit()
    await db.refresh(db_lecture)
    return db_lecture


def _block_title(block: int) -> str:
    titles = {
        1: "Фундамент мышления",
        2: "Структуры данных",
        3: "Объектная модель",
        4: "Инженерия",
    }
    return titles.get(block, "Unknown")
