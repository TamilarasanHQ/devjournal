from sqlalchemy import Column, Integer, String, TypeDecorator, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    entries = relationship("Entry", back_populates="user")
class Entry(Base):
    __tablename__ = "entry"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="entries")
    tags = relationship("Tag", secondary="entry_tag", back_populates="entries")
    understanding_rating = Column(Integer, nullable=True)
    last_reviewed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    review_count = Column(Integer, default=0, nullable=False)
    next_review_date = Column(TIMESTAMP(timezone=True), nullable=True)

class Tag(Base):
    __tablename__ = "tag"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    entries = relationship("Entry", secondary="entry_tag", back_populates="tags")

class EntryTag(Base):
    __tablename__ = "entry_tag"
    entry_id = Column(Integer, ForeignKey("entry.id"), primary_key=True) 
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)
