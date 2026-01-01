from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.tests.utils import create_mock_refresh, create_mock_comment, create_mock_post

client = TestClient(app)

def test_get_comment(mock_db):
    # Arrange
    mock_comment = create_mock_comment(1, 1, "John Doe", "john@example.com", "Great post!")
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_comment

    # Act
    response = client.get("/comments/1")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["post_id"] == 1
    assert data["author_name"] == "John Doe"
    assert data["author_email"] == "john@example.com"
    assert data["content"] == "Great post!"
    assert data["parent_id"] is None
    assert data["replies"] == []

def test_get_comment_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.get("/comments/99999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"

def test_get_comments_by_post(mock_db):
    # Arrange
    mock_comment1 = create_mock_comment(1, 1, "John Doe", "john@example.com", "Great post!")
    mock_comment2 = create_mock_comment(2, 1, "Jane Smith", "jane@example.com", "I agree!")
    mock_db.query.return_value.options.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
        mock_comment1,
        mock_comment2
    ]

    # Act
    response = client.get("/comments/post/1")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["author_name"] == "John Doe"
    assert data[1]["id"] == 2
    assert data[1]["author_name"] == "Jane Smith"


def test_get_comments_by_post_with_pagination(mock_db):
    # Arrange
    mock_db.query.return_value.options.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []

    # Act
    response = client.get("/comments/post/1?skip=10&limit=5")

    # Assert
    assert response.status_code == 200
    mock_db.query.return_value.options.return_value.filter.return_value.offset.assert_called_with(10)
    mock_db.query.return_value.options.return_value.filter.return_value.offset.return_value.limit.assert_called_with(5)

def test_create_comment(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test Post", "test-post", "Content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_post
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        created_at=datetime(2026, 1, 1),
        replies=[]
    )

    # Act
    response = client.post(
        "/comments/",
        json={
            "post_id": 1,
            "author_name": "John Doe",
            "author_email": "john@example.com",
            "content": "Great post!"
        }
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["id"] == 1
    assert data["post_id"] == 1
    assert data["author_name"] == "John Doe"
    assert data["author_email"] == "john@example.com"
    assert data["content"] == "Great post!"
    assert data["parent_id"] is None
    assert data["created_at"] == "2026-01-01T00:00:00"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_comment_post_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.post(
        "/comments/",
        json={
            "post_id": 999,
            "author_name": "John Doe",
            "author_email": "john@example.com",
            "content": "Great post!"
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_create_comment_with_parent(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test Post", "test-post", "Content")
    mock_parent_comment = create_mock_comment(1, 1, "Jane", "jane@example.com", "First comment")
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_post, mock_parent_comment]

    mock_db.refresh.side_effect = create_mock_refresh(
        id=2,
        created_at=datetime(2026, 1, 1),
        replies=[]
    )

    # Act
    response = client.post(
        "/comments/",
        json={
            "post_id": 1,
            "parent_id": 1,
            "author_name": "John Doe",
            "author_email": "john@example.com",
            "content": "Reply to first comment"
        }
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["parent_id"] == 1
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_create_comment_parent_not_found(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test Post", "test-post", "Content")
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_post, None]

    # Act
    response = client.post(
        "/comments/",
        json={
            "post_id": 1,
            "parent_id": 999,
            "author_name": "John Doe",
            "author_email": "john@example.com",
            "content": "Reply"
        }
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Parent comment not found"

def test_create_comment_parent_wrong_post(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test Post", "test-post", "Content")
    mock_parent_comment = create_mock_comment(1, 2, "Jane", "jane@example.com", "Comment on different post")
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_post, mock_parent_comment]

    # Act
    response = client.post(
        "/comments/",
        json={
            "post_id": 1,
            "parent_id": 1,
            "author_name": "John Doe",
            "author_email": "john@example.com",
            "content": "Reply"
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Parent comment does not belong to the specified post"

def test_delete_comment(mock_db, mock_auth):
    # Arrange
    mock_comment = create_mock_comment(1, 1, "John Doe", "john@example.com", "Great post!")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_comment

    # Act
    response = client.delete("/comments/1")

    # Assert
    assert response.status_code == 204
    mock_db.delete.assert_called_once_with(mock_comment)
    mock_db.commit.assert_called_once()

def test_delete_comment_not_found(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.delete("/comments/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"

def test_delete_comment_unauthorized(mock_db):
    # Act
    response = client.delete("/comments/1")

    # Assert
    assert response.status_code == 401
