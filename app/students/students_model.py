import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from app.shared.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    
    createdAt = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updatedAt = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)