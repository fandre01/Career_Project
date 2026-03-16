import json
import logging
from uuid import uuid4
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.schemas.chat import ChatRequest, ChatHistoryResponse, ChatMessageSchema
from backend.services.chat_service import FabriceAIService
from backend.models.chat_session import ChatSession, ChatMessage
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    service = FabriceAIService(db)

    # Try to create/find session in DB, but don't crash if DB fails
    session_id = request.session_id or str(uuid4())
    try:
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
            if session:
                session.last_active = datetime.now(timezone.utc)
                session_id = session.id
            else:
                session = ChatSession(id=session_id)
                db.add(session)
                db.commit()
        else:
            session = ChatSession(id=session_id)
            db.add(session)
            db.commit()

        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()
    except Exception as e:
        logger.error(f"Chat DB error (non-fatal): {e}")
        try:
            db.rollback()
        except Exception:
            pass

    async def generate():
        full_response = ""
        yield f"data: {json.dumps({'session_id': session_id})}\n\n"

        try:
            async for chunk in service.stream_response(session_id, request.message):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Chat streaming error: {e}", exc_info=True)
            error_msg = "Sorry, I encountered an error. Please try again!"
            yield f"data: {json.dumps({'content': error_msg})}\n\n"
            full_response = error_msg

        # Try to save assistant response, but don't crash if DB fails
        if full_response:
            try:
                assistant_msg = ChatMessage(
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                )
                db.add(assistant_msg)
                db.commit()
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
def chat_history(session_id: str, db: Session = Depends(get_db)):
    messages = []
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            messages = (
                db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )
    except Exception:
        pass

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageSchema.model_validate(m) for m in messages],
    )
