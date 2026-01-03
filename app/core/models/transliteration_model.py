from sqlalchemy import Column, Integer, String, Text, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transliteration(Base):
    __tablename__ = 'transliterations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_language = Column(String(10), nullable=False) # String(10) to save space, langs will be as 'az', 'ru' etc.
    target_language = Column(String(10), nullable=False)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DATETIME, nullable=False)

    # Relationships
    user = relationship("User", back_populates="transliterations")