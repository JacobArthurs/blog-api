from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .posts import Post
from .tags import Tag
from .post_tags import PostTag
from .comments import Comment

__all__ = ["Base", "Post", "Tag", "PostTag", "Comment"]