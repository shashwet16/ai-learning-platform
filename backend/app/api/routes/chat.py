import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.chat import Conversation, Message
from app.models.user import User
from app.schemas.chat import ConversationRead, MessageCreate, MessageRead
from app.services.llm.base import ChatMessage
from app.services.llm.factory import get_llm_provider

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}/messages", response_model=MessageRead, status_code=201)
def send_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    # Get-or-create: a conversation_id the caller hasn't used before starts
    # a new conversation; an existing one continues it. There's no
    # separate "create conversation" endpoint in the roadmap, so this
    # single endpoint has to serve both cases.
    conversation = db.get(Conversation, conversation_id)
    if conversation is None:
        conversation = Conversation(id=conversation_id, user_id=current_user.id)
        db.add(conversation)
        db.flush()
    elif conversation.user_id != current_user.id:
        # 404, not 403 — same reasoning as M2.5's login: don't confirm to
        # a caller that a conversation ID belonging to someone else exists
        # at all.
        raise AppError(
            "Conversation not found", status_code=404, code="conversation_not_found"
        )

    user_message = Message(
        conversation_id=conversation.id, role="user", content=body.content
    )
    db.add(user_message)
    db.commit()

    history = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
    ).all()
    chat_messages: list[ChatMessage] = [
        {"role": m.role, "content": m.content} for m in history
    ]

    provider = get_llm_provider()
    reply_text = provider.generate(chat_messages)

    assistant_message = Message(
        conversation_id=conversation.id, role="assistant", content=reply_text
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return assistant_message


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Conversation]:
    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.created_at.desc())
        ).all()
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
def get_conversation_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    conversation = db.get(Conversation, conversation_id)
    if conversation is None or conversation.user_id != current_user.id:
        raise AppError(
            "Conversation not found", status_code=404, code="conversation_not_found"
        )

    return list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        ).all()
    )
