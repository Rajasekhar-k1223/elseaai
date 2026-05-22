from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # e.g., "UPLOAD_DOCUMENT", "LOGIN", "CHAT_QUERY"
    module = Column(String(50)) # e.g., "Healthcare", "Cybersecurity"
    details = Column(Text) # JSON string with additional metadata
    ip_address = Column(String(45))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
