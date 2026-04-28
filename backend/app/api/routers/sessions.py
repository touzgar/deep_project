from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.SessionResponse])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sessions(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    return crud.create_session(db=db, session_data=session_data)

@router.put("/{session_id}", response_model=schemas.SessionResponse)
def update_session(session_id: int, session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = crud.update_session(db, session_id, session_data)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.delete_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
