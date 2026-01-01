from unittest.mock import MagicMock

def create_mock_refresh(**fields):
    def mock_refresh(obj):
        for field, value in fields.items():
            setattr(obj, field, value)

    return mock_refresh

def create_mock_post(id, title, slug, content, tags=None):
    mock_post = MagicMock()
    mock_post.id = id
    mock_post.title = title
    mock_post.slug = slug
    mock_post.content = content
    mock_post.tags = tags or []
    return mock_post

def create_mock_tag(id, name, slug):
    mock_tag = MagicMock()
    mock_tag.id = id
    mock_tag.name = name
    mock_tag.slug = slug
    return mock_tag

def create_mock_comment(id, post_id, author_name, author_email, content, parent_id=None, replies=None):
    mock_comment = MagicMock()
    mock_comment.id = id
    mock_comment.post_id = post_id
    mock_comment.parent_id = parent_id
    mock_comment.author_name = author_name
    mock_comment.author_email = author_email
    mock_comment.content = content
    mock_comment.replies = replies or []
    return mock_comment