import asyncio
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, check_db_connection
from app.models.lecture import Lecture
from app.models.student import Student

SCR_DIR = os.environ.get("SCR_DIR", "/scr")
TEACHER_GITHUB_USERNAME = os.environ.get("TEACHER_GITHUB_USERNAME", "")
SEED_UPDATE_CONTENT = os.environ.get("SEED_UPDATE_CONTENT", "1").lower() in ("1", "true", "yes")

LECTURES = [
    {
        "number": 0,
        "title": "Объекты, типы, ссылки",
        "block": 1,
        "description": "Модель объектов Python, ссылки, сборка мусора. Исключения — синтаксис, traceback, иерархия.",
        "topics": "id, type, is, mutable/immutable, сборка мусора, исключения",
        "assignment_type": "B",
        "assignment_description": "Объясни фрагмент кода из реального проекта Django — как работают ссылки и mutability",
        "is_published": True,
    },
    {
        "number": 1,
        "title": "Циклы и управление потоком",
        "block": 1,
        "description": "Truth value testing, for/while, break/continue/else, enumerate, распаковка в циклах.",
        "topics": "truthiness, short-circuit, for, while, break, continue, else, enumerate",
        "assignment_type": "A",
        "assignment_description": "Напиши функцию с использованием enumerate и обработкой исключений",
        "is_published": True,
    },
    {
        "number": 2,
        "title": "Последовательности и протокол итерации",
        "block": 1,
        "description": "Sequence types, slicing, распаковка, протокол итерации __iter__/__next__, iterable vs iterator.",
        "topics": "list, tuple, range, slicing, iterable, iterator, __getitem__, zip, map, filter",
        "assignment_type": "A",
        "assignment_description": "Реализуй собственный итератор CountUp и используй его с for",
        "is_published": True,
    },
    {
        "number": 3,
        "title": "Функции, замыкания, области видимости",
        "block": 1,
        "description": "LEGB, nonlocal, closures, декораторы, functools.wraps",
        "topics": "LEGB, nonlocal, closures, декораторы, wraps, lru_cache",
        "assignment_type": "B",
        "assignment_description": "Объясни как работает замыкание в примере из Pydantic",
        "is_published": True,
    },
    {
        "number": 4,
        "title": "Множества и словари",
        "block": 2,
        "description": "Hashable, dict internals, set operations, collections.defaultdict, Counter",
        "topics": "hashable, dict, set, defaultdict, Counter, frozenset",
        "assignment_type": "A",
        "assignment_description": "Напиши функцию для подсчёта частот с использованием Counter",
        "is_published": True,
    },
    {
        "number": 5,
        "title": "Итераторы и генераторы",
        "block": 2,
        "description": "yield, generator expressions, generator functions, itertools, yield from, send, throw, close",
        "topics": "yield, generator expressions, itertools, send, throw, close, yield from",
        "assignment_type": "AB",
        "assignment_description": "Напиши генератор для бесконечной последовательности, используй itertools и объясни свой код",
        "is_published": True,
    },
    {
        "number": 6,
        "title": "ООП — часть 1: класс и экземпляр",
        "block": 3,
        "description": "Атрибуты, методы, __init__, __new__, self, cls, classmethod, staticmethod, property",
        "topics": "__init__, __new__, self, cls, classmethod, staticmethod, property, __dict__",
        "assignment_type": "B",
        "assignment_description": "Объясни зачем в Toga используется __new__ вместо __init__",
        "is_published": True,
    },
    {
        "number": 7,
        "title": "ООП — часть 2: наследование и исключения",
        "block": 3,
        "description": "MRO, super(), diamond problem, custom exceptions, __init_subclass__",
        "topics": "MRO, super, diamond inheritance, custom exceptions, __init_subclass__",
        "assignment_type": "A",
        "assignment_description": "Реализуй иерархию классов с MRO и super()",
        "is_published": True,
    },
    {
        "number": 8,
        "title": "Слоты, дескрипторы, декораторы",
        "block": 3,
        "description": "descriptor protocol, __slots__, декораторы классов, dataclasses",
        "topics": "__get__, __set__, __delete__, __slots__, dataclasses, decorators",
        "assignment_type": "B",
        "assignment_description": "Объясни как дескрипторы используются в Django ORM",
        "is_published": True,
    },
    {
        "number": 9,
        "title": "Метаклассы и сопоставление шаблону",
        "block": 3,
        "description": "type, metaclasses, __new__, __init_subclass__, structural pattern matching (match/case)",
        "topics": "metaclass, type, __new__, __init_subclass__, match/case, PEP 634",
        "assignment_type": "AB",
        "assignment_description": "Напиши простой метакласс, используй match/case для разбора структуры и объясни свой код",
        "is_published": True,
    },
    {
        "number": 10,
        "title": "Типизация в Python",
        "block": 4,
        "description": "Type hints, mypy, Protocols, TypedDict, generics, Pydantic для runtime-валидации",
        "topics": "typing, mypy, Protocol, TypedDict, generics, Pydantic",
        "assignment_type": "B",
        "assignment_description": "Объясни как Pydantic использует type hints для валидации данных",
        "is_published": True,
    },
    {
        "number": 11,
        "title": "Управление памятью и жизненный цикл объекта",
        "block": 4,
        "description": "Reference counting, GC, weakref, __del__, __weakref__, циклические ссылки",
        "topics": "refcount, gc, weakref, __del__, cyclic references, memory management",
        "assignment_type": "B",
        "assignment_description": "Объясни как работает garbage collector на примере фрагмента из CPython",
        "is_published": True,
    },
    {
        "number": 12,
        "title": "Асинхронность",
        "block": 4,
        "description": "asyncio, coroutines, tasks, event loop, async/await, aiohttp, асинхронные контекстные менеджеры",
        "topics": "async, await, coroutine, event loop, Task, asyncio, aiohttp",
        "assignment_type": "A",
        "assignment_description": "Напиши асинхронную функцию с использованием asyncio и aiohttp",
        "is_published": True,
    },
    {
        "number": 13,
        "title": "Куда идти дальше",
        "block": 4,
        "description": "Как читать open-source, как писать свою библиотеку, как стать частью сообщества",
        "topics": "open source, contribution, libraries, community, career",
        "assignment_type": "A",
        "assignment_description": "Финальное задание: выбери вариант A (разбор модуля), B (issue/PR), C (своя библиотека)",
        "is_published": True,
    },
]


def read_lecture_content(number: int) -> str | None:
    md_path = Path(SCR_DIR) / f"lecture_{number:02d}" / f"lecture_{number:02d}.md"
    if md_path.exists():
        return md_path.read_text(encoding="utf-8")
    return None


async def seed_teacher():
    if not TEACHER_GITHUB_USERNAME:
        return

    await check_db_connection()
    async with async_session() as db:
        result = await db.execute(
            select(Student).where(Student.github_username == TEACHER_GITHUB_USERNAME)
        )
        existing = result.scalar_one_or_none()
        if not existing:
            teacher = Student(
                github_username=TEACHER_GITHUB_USERNAME,
                role="teacher",
            )
            db.add(teacher)
            await db.commit()
            print(f"  Created teacher account: {TEACHER_GITHUB_USERNAME}")
        elif existing.role != "teacher":
            existing.role = "teacher"
            await db.commit()
            print(f"  Updated {TEACHER_GITHUB_USERNAME} role to teacher")
        else:
            print(f"  Teacher account already exists: {TEACHER_GITHUB_USERNAME}")


async def seed_lectures():
    await check_db_connection()
    async with async_session() as db:
        for lecture_data in LECTURES:
            result = await db.execute(
                select(Lecture).where(Lecture.number == lecture_data["number"])
            )
            existing = result.scalar_one_or_none()
            if not existing:
                content = read_lecture_content(lecture_data["number"])
                lecture_data["content"] = content
                if content:
                    print(f"  Loaded content for lecture {lecture_data['number']} ({len(content)} chars)")
                db.add(Lecture(**lecture_data))
                print(f"  Added lecture {lecture_data['number']}: {lecture_data['title']}")
            else:
                if SEED_UPDATE_CONTENT:
                    content = read_lecture_content(lecture_data["number"])
                    if content and content != existing.content:
                        existing.content = content
                        print(f"  Updated content for lecture {lecture_data['number']}")
                    if lecture_data.get("assignment_type") and lecture_data["assignment_type"] != existing.assignment_type:
                        existing.assignment_type = lecture_data["assignment_type"]
                        print(f"  Updated assignment_type for lecture {lecture_data['number']}: {lecture_data['assignment_type']}")
                print(f"  Lecture {lecture_data['number']} already exists")

        await db.commit()
        print("Seed complete!")


async def seed_all():
    await seed_teacher()
    await seed_lectures()


if __name__ == "__main__":
    asyncio.run(seed_all())
