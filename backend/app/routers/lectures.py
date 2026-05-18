from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.lecture import Lecture
from app.models.assignment import Assignment
from app.schemas.lecture import LectureResponse, LectureCreate, LectureUpdate
from app.services.auth import get_current_user, get_current_teacher

router = APIRouter(prefix="/api/lectures", tags=["lectures"])


@router.get("", response_model=list[LectureResponse])
async def get_lectures(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lecture).order_by(Lecture.number))
    return result.scalars().all()


@router.get("/blocks")
async def get_lectures_by_block(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lecture).order_by(Lecture.number))
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
async def get_lecture(lecture_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lecture).where(Lecture.id == lecture_id))
    lecture = result.scalar_one_or_none()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.get("/number/{number}", response_model=LectureResponse)
async def get_lecture_by_number(number: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lecture).where(Lecture.number == number))
    lecture = result.scalar_one_or_none()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lecture


@router.post("", response_model=LectureResponse)
async def create_lecture(
    lecture: LectureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_teacher),
):
    db_lecture = Lecture(**lecture.model_dump())
    db.add(db_lecture)
    await db.commit()
    await db.refresh(db_lecture)
    return db_lecture


@router.patch("/{lecture_id}", response_model=LectureResponse)
async def update_lecture(
    lecture_id: str,
    lecture: LectureUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_teacher),
):
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
