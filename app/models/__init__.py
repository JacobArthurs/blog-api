from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .posts import Post

__all__ = ["Base", "Post"]