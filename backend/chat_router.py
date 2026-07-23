import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
from auth import get_current_user
import models
import schemas
from prompts import LEVEL_PROMPTS, recalibrate, LEVEL_ORDER
from llm_client import stream_reply

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/session", response_model=schemas.SessionOut)
def create_session(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    session = models.ChatSession(
        user_id=user.id,
        title="New chat",
        effective_level=user.base_level,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[schemas.SessionOut])
def list_sessions(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return (
        db.query(models.ChatSession)
        .filter(models.ChatSession.user_id == user.id)
        .order_by(models.ChatSession.created_at.desc())
        .all()
    )


@router.get("/session/{session_id}/messages", response_model=list[schemas.MessageOut])
def get_messages(session_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id, models.ChatSession.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages


@router.post("/message")
def send_message(req: schemas.SendMessageRequest, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == req.session_id, models.ChatSession.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # recalibrate effective level based on this message before generating a reply
    level_before = session.effective_level
    new_level, c_streak, m_streak, adjusted = recalibrate(
        session.effective_level, session.confusion_streak, session.mastery_streak, req.content
    )
    was_confusion_drop = adjusted and LEVEL_ORDER.index(new_level) < LEVEL_ORDER.index(level_before)
    was_mastery_rise = adjusted and LEVEL_ORDER.index(new_level) > LEVEL_ORDER.index(level_before)
    session.effective_level = new_level
    session.confusion_streak = c_streak
    session.mastery_streak = m_streak

    user_msg = models.Message(session_id=session.id, role="user", content=req.content)
    db.add(user_msg)

    if session.title == "New chat":
        session.title = (req.content[:40] + "...") if len(req.content) > 40 else req.content

    db.commit()

    # build conversation history for the model
    history = (
        db.query(models.Message)
        .filter(models.Message.session_id == session.id)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    conversation = [
        {"role": "user" if m.role == "user" else "assistant", "content": m.content}
        for m in history
    ]

    system_prompt = LEVEL_PROMPTS[session.effective_level]
    start = time.time()

    def event_stream():
        full_reply = []
        for chunk in stream_reply(system_prompt, conversation):
            full_reply.append(chunk)
            yield chunk

        latency_ms = (time.time() - start) * 1000
        guide_msg = models.Message(
            session_id=session.id,
            role="guide",
            content="".join(full_reply),
            level_at_response=session.effective_level,
            confusion_signal=was_confusion_drop,
            mastery_signal=was_mastery_rise,
            response_latency_ms=latency_ms,
        )
        db.add(guide_msg)
        db.commit()

    return StreamingResponse(event_stream(), media_type="text/plain")


@router.get("/session/{session_id}/level")
def get_level(session_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id, models.ChatSession.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"effective_level": session.effective_level, "base_level": user.base_level}