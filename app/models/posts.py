from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from . import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, nullable=False, default=0)
    read_time_minutes = Column(Integer, nullable=False, default=0)
    featured = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    tags = relationship("Tag", secondary="post_tags", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")