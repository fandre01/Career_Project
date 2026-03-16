from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.schemas.chat import ChatRequest, ChatHistoryResponse, ChatMessageSchema
from backend.services.chat_service import FabriceAIService
from backend.models.chat_session import ChatSession, ChatMessage
from datetime import datetime, timezone

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    service = FabriceAIService(db)

    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        session.last_active = datetime.now(timezone.utc)
    else:
        session = ChatSession()
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.commit()

    async def generate():
        full_response = ""
        yield f"data: {{\"session_id\": \"{session.id}\"}}\n\n"

        async for chunk in service.stream_response(session.id, request.message):
            full_response += chunk
            import json
            yield f"data: {json.dumps({'content': chunk})}\n\n"

        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=full_response,
        )
        db.add(assistant_msg)
        db.commit()

        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
def chat_history(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageSchema.model_validate(m) for m in messages],
    )
