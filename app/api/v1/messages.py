from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.user import UserCreate
from app.services.dialogue import add_message, get_active_session, handle_user_text
from app.services.memory import store_memory_updates
from app.services.users import get_or_create_user

router = APIRouter()
DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=MessageResponse)
async def create_message(
    payload: MessageCreate,
    db: DbSession,
) -> MessageResponse:
    user = await get_or_create_user(
        db,
        UserCreate(
            telegram_id=payload.telegram_id,
            username=payload.username,
            first_name=payload.first_name,
            language_code=payload.language_code,
        ),
    )
    session = await get_active_session(db, user, source=payload.source)
    user_message = await add_message(
        db,
        user=user,
        session=session,
        role="user",
        content=payload.text,
    )

    reply, risk_level = await handle_user_text(db, user=user, session=session, text=payload.text)
    await add_message(db, user=user, session=session, role="assistant", content=reply)
    await store_memory_updates(
        db,
        user=user,
        session=session,
        source_message=user_message,
        user_text=payload.text,
        assistant_reply=reply,
    )
    await db.commit()

    return MessageResponse(
        user_id=user.id,
        session_id=session.id,
        reply=reply,
        risk_level=risk_level,
    )
