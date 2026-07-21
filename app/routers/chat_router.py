from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent import run_agent
from app.db import get_db
from app.models import ChatMessage
from app.schemas import ChatIn, ChatOut

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history")
def history(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).limit(limit).all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in rows]


@router.post("", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    try:
        reply = run_agent(db, payload.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ChatOut(reply=reply)
