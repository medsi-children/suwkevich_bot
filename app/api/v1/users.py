from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.memory import ImportantFact, KnownPerson, OpenTopic, UserMemory
from app.models.user import User
from app.schemas.user import (
    ImportantFactRead,
    KnownPersonRead,
    MemoryRead,
    OpenTopicRead,
    UserRead,
)

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{telegram_id}", response_model=UserRead)
async def read_user(telegram_id: int, db: DbSession) -> User:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{telegram_id}/memories", response_model=list[MemoryRead])
async def read_user_memories(
    telegram_id: int,
    db: DbSession,
) -> list[UserMemory]:
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(UserMemory)
        .where(UserMemory.user_id == user.id)
        .order_by(UserMemory.importance.desc(), UserMemory.updated_at.desc())
        .limit(50)
    )
    return list(result.scalars().all())


@router.get("/{telegram_id}/facts", response_model=list[ImportantFactRead])
async def read_user_facts(
    telegram_id: int,
    db: DbSession,
) -> list[ImportantFact]:
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(ImportantFact)
        .where(ImportantFact.user_id == user.id, ImportantFact.is_active.is_(True))
        .order_by(ImportantFact.importance.desc(), ImportantFact.last_mentioned_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.get("/{telegram_id}/people", response_model=list[KnownPersonRead])
async def read_user_people(
    telegram_id: int,
    db: DbSession,
) -> list[KnownPerson]:
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(KnownPerson)
        .where(KnownPerson.user_id == user.id, KnownPerson.is_active.is_(True))
        .order_by(KnownPerson.importance.desc(), KnownPerson.last_mentioned_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.get("/{telegram_id}/topics", response_model=list[OpenTopicRead])
async def read_user_topics(
    telegram_id: int,
    db: DbSession,
) -> list[OpenTopic]:
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.execute(
        select(OpenTopic)
        .where(OpenTopic.user_id == user.id)
        .order_by(OpenTopic.priority.desc(), OpenTopic.last_mentioned_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())
