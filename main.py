from datetime import datetime, timezone
from sqlalchemy import or_
from typing import Annotated
from datetime import timedelta
from fastapi import FastAPI, Depends, Response, status, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy import text
from database import Base, SessionLocal, engine
from schemas import ReviewCreate, UserCreate, UserOut, EntryCreate, EntryOut, EntryUpdate, TagCreate, TagOut
from models import User, Entry, Tag
from utils import hash_password, next_review_interval, verify_password
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
    
    # Handle tags
    if entry.tags:
        for tag_name in entry.tags:
            # Find existing tag or create new one
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            new_entry.tags.append(tag)
    
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.get("/entries/due_for_review", response_model=list[EntryOut])
def get_entries_due_for_review(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_time = datetime.now(timezone.utc)
    entries = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.next_review_date.isnot(None),
        Entry.next_review_date <= current_time
    ).all()
    return entries

@app.get("/entries", response_model=list[EntryOut])
def get_entries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), tag: str | None = Query(None), search: str | None = Query(None), skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    query = db.query(Entry).filter(Entry.user_id == current_user.id)
    
    # Filter by tag if provided
    if tag:
        query = query.join(Entry.tags).filter(Tag.name == tag)
    
    # Filter by search term if provided
    if search:
        query = query.filter(Entry.title.ilike(f"%{search}%") | Entry.content.ilike(f"%{search}%"))
    
    query = query.offset(skip).limit(limit)
    entries = query.all()
    return entries

@app.get("/entries/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/entries/{entry_id}/review", response_model=EntryOut)
def review_entry(entry_id: int, review: ReviewCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Update review data
    entry.understanding_rating = review.rating
    entry.last_reviewed_at = datetime.now(timezone.utc)
    entry.review_count += 1
    entry.next_review_date = next_review_interval(review.rating, entry.review_count)
    
    db.commit()
    db.refresh(entry)
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

    if hasattr(entry_update, 'tags') and entry_update.tags is not None:
        # Clear existing tags
        entry.tags.clear()
        # Add new tags
        for tag_name in entry_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            entry.tags.append(tag)
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

@app.post("/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")
    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@app.get("/tags", response_model=list[TagOut])
def list_tags(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    return tags 




