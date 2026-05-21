from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.memory import UserMemory
from app.models.user import User
from app.schemas.user import MemoryRead, UserRead

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
