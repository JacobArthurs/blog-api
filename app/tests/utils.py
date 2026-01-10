from unittest.mock import MagicMock
from datetime import datetime

def create_mock_refresh(**fields):
    def mock_refresh(obj):
        for field, value in fields.items():
            setattr(obj, field, value)

    return mock_refresh

def create_mock_post(id, title, slug, content, tags=None, summary="Test summary", read_time_minutes=5, featured=False, view_count=0, created_at=None, updated_at=None):
    mock_post = MagicMock()
    mock_post.id = id
    mock_post.title = title
    mock_post.slug = slug
    mock_post.summary = summary
    mock_post.content = content
    mock_post.read_time_minutes = read_time_minutes
    mock_post.featured = featured
    mock_post.view_count = view_count
    mock_post.created_at = created_at or datetime(2026, 1, 1)
    mock_post.updated_at = updated_at or datetime(2026, 1, 1)
    mock_post.tags = tags or []
    return mock_post

def create_mock_tag(id, name, slug, created_at=None, updated_at=None):
    mock_tag = MagicMock()
    mock_tag.id = id
    mock_tag.name = name
    mock_tag.slug = slug
    mock_tag.created_at = created_at or datetime(2026, 1, 1)
    mock_tag.updated_at = updated_at or datetime(2026, 1, 1)
    return mock_tag

def create_mock_comment(id, post_id, author_name, author_email, content, parent_id=None, replies=None, like_count=0, created_at=None):
    mock_comment = MagicMock()
    mock_comment.id = id
    mock_comment.post_id = post_id
    mock_comment.parent_id = parent_id
    mock_comment.author_name = author_name
    mock_comment.author_email = author_email
    mock_comment.content = content
    mock_comment.like_count = like_count
    mock_comment.created_at = created_at or datetime(2026, 1, 1)
    mock_comment.replies = replies or []
    return mock_comment