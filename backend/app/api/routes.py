from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as SessionDB

from app.api.schemas import MessageCreate, MessageRead, SessionCreate, SessionRead
from app.db.database import get_db
from app.db.models import Message, Session, User

router = APIRouter(prefix="/api", tags=["persistence"])


@router.post("/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(session: SessionCreate, db: SessionDB = Depends(get_db)) -> Session:
    user = db.query(User).first()
    if user is None:
        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

    db_session = Session(user_id=str(user.id), title=session.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions/{session_id}", response_model=SessionRead)
def get_session(session_id: str, db: SessionDB = Depends(get_db)) -> Session:
    db_session = db.get(Session, session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session


@router.get("/sessions/{session_id}/messages", response_model=list[MessageRead])
def get_messages(session_id: str, db: SessionDB = Depends(get_db)) -> list[Message]:
    session = db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc())
    messages = db.execute(stmt).scalars().all()
    return messages


@router.post("/sessions/{session_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
def create_message(
    session_id: str,
    message: MessageCreate,
    db: SessionDB = Depends(get_db),
) -> Message:
    session = db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    db_message = Message(session_id=session_id, role=message.role, content=message.content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
