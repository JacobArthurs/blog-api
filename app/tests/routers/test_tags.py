from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.tests.utils import create_mock_refresh, create_mock_tag

client = TestClient(app)

def test_get_tags(mock_db):
    # Arrange
    mock_tag = create_mock_tag(1, "Python", "python")
    mock_db.query.return_value.order_by.return_value.count.return_value = 1
    mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_tag]

    # Act
    response = client.get("/tags/")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["total"] == 1
    assert data["offset"] == 0
    assert data["limit"] == 10
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == 1
    assert data["items"][0]["name"] == "Python"
    assert data["items"][0]["slug"] == "python"

def test_get_tags_with_pagination(mock_db):
    # Arrange
    mock_db.query.return_value.order_by.return_value.count.return_value = 0
    mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

    # Act
    response = client.get("/tags/?offset=10&limit=5")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["total"] == 0
    assert data["offset"] == 10
    assert data["limit"] == 5
    assert data["items"] == []
    # Get the query object and verify offset and limit were called correctly
    query = mock_db.query.return_value
    query.order_by.return_value.offset.assert_called_with(10)
    query.order_by.return_value.offset.return_value.limit.assert_called_with(5)

def test_get_tag_by_id(mock_db):
    # Arrange
    mock_tag = create_mock_tag(1, "Python", "python")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

    # Act
    response = client.get("/tags/1")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Python"
    assert data["slug"] == "python"

def test_get_tag_by_id_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.get("/tags/99999")

    # Assert
    assert response.status_code == 404

def test_get_tag_by_slug(mock_db):
    # Arrange
    mock_tag = create_mock_tag(1, "Python", "python")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

    # Act
    response = client.get("/tags/slug/python")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["id"] == 1
    assert data["name"] == "Python"
    assert data["slug"] == "python"

def test_get_tag_by_slug_not_found(mock_db):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.get("/tags/slug/no-slug")

    # Assert
    assert response.status_code == 404

def test_create_tag(mock_db, mock_auth):
    # Arrange
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1)
    )

    # Act
    response = client.post(
        "/tags/",
        json={"name": "Python"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["id"] == 1
    assert data["name"] == "Python"
    assert data["slug"] == "auto-slug"
    assert data["created_at"] == "2026-01-01T00:00:00"
    assert data["updated_at"] == "2026-01-01T00:00:00"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_create_tag_with_custom_slug(mock_db, mock_auth, mocker):
    # Arrange
    mocker.patch("app.routers.tags.slugify", return_value="should-not-be-used")
    mock_db.refresh.side_effect = create_mock_refresh(
        id=1,
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1)
    )

    # Act
    response = client.post(
        "/tags/",
        json={"name": "Python", "slug": "custom-python"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["slug"] == "custom-python"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_update_tag(mock_db, mock_auth):
    # Arrange
    mock_tag = create_mock_tag(1, "Old Name", "old-slug")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tag
    mock_db.refresh.side_effect = create_mock_refresh(
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 2)
    )

    # Act
    response = client.patch(
        "/tags/1",
        json={"name": "Updated Name"}
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert mock_tag.name == "Updated Name"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_tag)

def test_update_tag_not_found(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.patch(
        "/tags/999",
        json={"name": "Updated Name"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Tag not found"

def test_update_tag_with_custom_slug(mock_db, mock_auth, mocker):
    # Arrange
    mock_tag = create_mock_tag(1, "Name", "old-slug")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tag
    mocker.patch("app.routers.tags.validate_unique_slug", return_value=None)
    mock_db.refresh.side_effect = create_mock_refresh(
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 2)
    )

    # Act
    response = client.patch(
        "/tags/1",
        json={"slug": "new-custom-slug"}
    )

    # Assert
    assert response.status_code == 200
    assert mock_tag.slug == "new-custom-slug"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_tag)

def test_delete_tag(mock_db, mock_auth):
    # Arrange
    mock_tag = create_mock_tag(1, "Python", "python")
    mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

    # Act
    response = client.delete("/tags/1")

    # Assert
    assert response.status_code == 204
    mock_db.delete.assert_called_once_with(mock_tag)
    mock_db.commit.assert_called_once()

def test_delete_tag_not_found(mock_db, mock_auth):
    # Arrange
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Act
    response = client.delete("/tags/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Tag not found"

def test_create_tag_unauthorized(mock_db):
    # Act
    response = client.post(
        "/tags/",
        json={"name": "Python"}
    )

    # Assert
    assert response.status_code == 401

def test_update_tag_unauthorized(mock_db):
    # Act
    response = client.patch(
        "/tags/1",
        json={"name": "Updated Name"}
    )

    # Assert
    assert response.status_code == 401

def test_delete_tag_unauthorized(mock_db):
    # Act
    response = client.delete("/tags/1")

    # Assert
    assert response.status_code == 401
