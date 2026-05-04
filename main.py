from typing import Annotated
from datetime import timedelta
from fastapi import FastAPI, Depends, Response, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import Base, SessionLocal, engine
from schemas import UserCreate, UserOut, EntryCreate, EntryOut, EntryUpdate
from models import User, Entry
from utils import hash_password, verify_password
from auth import Token, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def test():
    return {"message": "API is working!"}

@app.get("/health")
def health():
    try:
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    finally:
        db.close()
    

    
@app.post("/users/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
        hashed_password = hash_password(user.password)
        # Create new user
        new_user = User(email=user.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise e

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user_id=user.id,
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/entries", response_model=EntryOut)
def create_entry(entry: EntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_entry = Entry(user_id=current_user.id, title=entry.title, content=entry.content)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.get("/entries", response_model=list[EntryOut])
def get_entries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.query(Entry).filter(Entry.user_id == current_user.id).all()
    return entries

@app.get("/entries/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.put("/entries/{entry_id}", response_model=EntryOut)
def update_entry(entry_id: int, entry_update: EntryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if entry_update.title is not None:
        entry.title = entry_update.title
    if entry_update.content is not None:
        entry.content = entry_update.content
    db.commit()
    db.refresh(entry)
    return entry

@app.delete("/entries/{entry_id}")
def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted"} 

