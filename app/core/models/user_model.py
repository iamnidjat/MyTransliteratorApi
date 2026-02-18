from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    # Relationships
    transliterations = relationship("Transliteration", back_populates="user", cascade="all, delete-orphan") # one-to-many