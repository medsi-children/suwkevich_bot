import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.user import UserCreate
from app.services.dialogue import add_message, get_active_session, handle_user_text
from app.services.memory import apply_memory_control, store_memory_updates_deferred
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
    control_reply = await apply_memory_control(
        db,
        user=user,
        session=session,
        source_message=user_message,
        text=payload.text,
    )
    if control_reply:
        await add_message(db, user=user, session=session, role="assistant", content=control_reply)
        await db.commit()
        return MessageResponse(
            user_id=user.id,
            session_id=session.id,
            reply=control_reply,
            mode="memory_control",
        )

    reply, risk_level = await handle_user_text(db, user=user, session=session, text=payload.text)
    await add_message(db, user=user, session=session, role="assistant", content=reply)
    user_id = user.id
    session_id = session.id
    source_message_id = user_message.id
    await db.commit()
    asyncio.create_task(
        store_memory_updates_deferred(
            user_id=user_id,
            session_id=session_id,
            source_message_id=source_message_id,
            user_text=payload.text,
            assistant_reply=reply,
        )
    )

    return MessageResponse(
        user_id=user.id,
        session_id=session.id,
        reply=reply,
        risk_level=risk_level,
    )
