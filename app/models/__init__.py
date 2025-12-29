from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .posts import Post
from .tags import Tag

__all__ = ["Base", "Post", "Tag"]