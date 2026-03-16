from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from backend.db.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    ip_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    visitor_hash = Column(String(64), nullable=True, index=True)
    page = Column(String(200), default="/")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
