from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.tests.utils import create_mock_refresh, create_mock_post, create_mock_tag

client = TestClient(app)

def test_get_posts(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test", "test-slug", "Content")
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.count.return_value = 1
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_post]

    # Act
    response = client.get("/posts/")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == 1
    assert data["items"][0]["title"] == "Test"
    assert data["items"][0]["slug"] == "test-slug"
    assert data["items"][0]["content"] == "Content"
    assert data["items"][0]["tags"] == []

def test_get_posts_with_pagination(mock_db):
    # Arrange
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.count.return_value = 0
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    # Act
    response = client.get("/posts/?offset=10&limit=5")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["total"] == 0
    assert data["offset"] == 10
    assert data["limit"] == 5
    assert data["items"] == []
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(10)
    mock_db.query.return_value.options.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(5)

def test_get_post_by_id(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test", "test-slug", "Content")
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_post

    # Act
    response = client.get("/posts/1")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "Test"
    assert data["slug"] == "test-slug"
    assert data["content"] == "Content"
    assert data["tags"] == []

def test_get_post_by_id_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
    
    # Act
    response = client.get("/posts/99999")

    # Assert
    assert response.status_code == 404

def test_get_post_by_slug(mock_db):
    # Arrange
    mock_post = create_mock_post(1, "Test", "test-slug", "Content")
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = mock_post

    # Act
    response = client.get("/posts/slug/test-slug")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "Test"
    assert data["slug"] == "test-slug"
    assert data["content"] == "Content"
    assert data["tags"] == []

def test_get_post_by_slug_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.options.return_value.filter.return_value.first.return_value = None
    
    # Act
    response = client.get("/posts/slug/no-slug")

    # Assert
    assert response.status_code == 404

def test_create_post(mock_db, mock_auth):
    # Arrange
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        view_count=0,
        comment_count=0,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1)
    )

    # Act
    response = client.post(
        "/posts/",
        json={"title": "New Post", "summary": "Post summary", "content": "Post content"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["id"] == 1
    assert data["title"] == "New Post"
    assert data["slug"] == "auto-slug"
    assert data["content"] == "Post content"
    assert data["view_count"] == 0
    assert data["created_at"] == "2026-01-01T00:00:00"
    assert data["updated_at"] == "2026-01-01T00:00:00"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_post_with_custom_slug(mock_db, mock_auth, mocker):
    # Arrange
    mocker.patch("app.routers.posts.slugify", return_value="should-not-be-used")
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        view_count=0,
        comment_count=0,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1)
    )

    # Act
    response = client.post(
        "/posts/",
        json={"title": "New Post", "summary": "Post summary", "content": "Post content", "slug": "custom-slug"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["slug"] == "custom-slug"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_post_with_tags(mock_db, mock_auth):
    # Arrange
    mock_tag1 = create_mock_tag(1, "Tag1", "tag1")
    mock_tag2 = create_mock_tag(2, "Tag2", "tag2")

    mock_db.query.return_value.filter.return_value.all.return_value = [mock_tag1, mock_tag2]
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        view_count=0,
        comment_count=0,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1)
    )

    # Act
    response = client.post(
        "/posts/",
        json={"title": "New Post", "summary": "Post summary", "content": "Post content", "tag_ids": [1, 2]}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert len(data["tags"]) == 2
    assert data["tags"][0]["name"] == "Tag1"
    assert data["tags"][1]["name"] == "Tag2"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_post_with_invalid_tag_ids(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.all.return_value = []

    # Act
    response = client.post(
        "/posts/",
        json={"title": "New Post", "summary": "Post summary", "content": "Post content", "tag_ids": [999]}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "One or more tags not found"

def test_update_post(mock_db, mock_auth):
    # Arrange
    mock_post = create_mock_post(1, "Old Title", "old-slug", "Old content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_post
    mock_db.refresh.side_effect = create_mock_refresh(
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 2)
    )

    # Act
    response = client.patch(
        "/posts/1",
        json={"title": "Updated Title", "content": "Updated content"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert mock_post.title == "Updated Title"
    assert mock_post.content == "Updated content"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_post)

def test_update_post_not_found(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.patch(
        "/posts/999",
        json={"title": "Updated Title"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_update_post_with_custom_slug(mock_db, mock_auth, mocker):
    # Arrange
    mock_post = create_mock_post(1, "Title", "old-slug", "Content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_post
    mocker.patch("app.routers.posts.validate_unique_slug", return_value=None)
    mock_db.refresh.side_effect = create_mock_refresh(
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 2)
    )

    # Act
    response = client.patch(
        "/posts/1",
        json={"slug": "new-custom-slug"}
    )

    # Assert
    assert response.status_code == 200
    assert mock_post.slug == "new-custom-slug"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_post)

def test_update_post_clear_tags(mock_db, mock_auth):
    # Arrange
    mock_tag = create_mock_tag(1, "Tag", "tag")
    mock_post = create_mock_post(1, "Title", "slug", "Content", tags=[mock_tag])
    mock_db.query.return_value.filter.return_value.first.return_value = mock_post
    mock_db.refresh.side_effect = create_mock_refresh(
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 2)
    )

    # Act
    response = client.patch(
        "/posts/1",
        json={"tag_ids": []}
    )

    # Assert
    assert response.status_code == 200
    assert mock_post.tags == []
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_post)

def test_delete_post(mock_db, mock_auth):
    # Arrange
    mock_post = create_mock_post(1, "Title", "slug", "Content")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_post

    # Act
    response = client.delete("/posts/1")

    # Assert
    assert response.status_code == 204
    mock_db.delete.assert_called_once_with(mock_post)
    mock_db.commit.assert_called_once()

def test_delete_post_not_found(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.delete("/posts/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

def test_create_post_unauthorized(mock_db):
    # Act
    response = client.post(
        "/posts/",
        json={"title": "New Post", "content": "Post content"}
    )

    # Assert
    assert response.status_code == 401

def test_update_post_unauthorized(mock_db):
    # Act
    response = client.patch(
        "/posts/1",
        json={"title": "Updated Title"}
    )

    # Assert
    assert response.status_code == 401

def test_delete_post_unauthorized(mock_db):
    # Act
    response = client.delete("/posts/1")

    # Assert
    assert response.status_code == 401