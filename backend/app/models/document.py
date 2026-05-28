from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class DocumentMetadata(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(36), unique=True, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_file_path = Column(String(500), nullable=True)
    document_type = Column(String(50), default="general")
    handwriting_detected = Column(Boolean, default=False)
    status = Column(String(50), default="pending_review")
    review_notes = Column(Text, nullable=True)
    fine_tune_dataset_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="documents")
