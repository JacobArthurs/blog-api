from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, func, select, table, column
from sqlalchemy.orm import relationship, column_property
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

    tags = relationship("Tag", secondary="post_tags", back_populates="posts", order_by="Tag.created_at.desc()")
    comments = relationship("Comment", back_populates="post", cascade="all, delete", order_by="Comment.like_count.desc(), Comment.created_at.desc()")

    comment_count = column_property(
        select(func.count(column("id")))
        .select_from(table("comments"))
        .where(column("post_id") == id)
        .correlate_except(table("comments"))
        .scalar_subquery()
    )