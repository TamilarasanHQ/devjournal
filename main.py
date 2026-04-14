from fastapi import FastAPI, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from schemas import UserCreate, UserOut
from models import User
from utils import hash_password, verify_password
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
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    

    
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

